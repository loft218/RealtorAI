# app/services/circle_recommender.py

from typing import Dict, List, Optional
from app.db import Database
from app.utils.sql_utils import format_sql
from app.models.requirement import ParsedRequirement
from app.core.config import settings


class CircleRecommenderService:
    def __init__(self):
        self.db = Database

    async def recommend_circles(
        self,
        requirement: ParsedRequirement,
        weights: Optional[Dict[str, float]] = None,
        limit: int = 10,
        random_factor: float = 1.0,
    ) -> List[Dict]:
        if not requirement:
            raise ValueError("Requirement must be provided")
        score_weights = weights or settings.DEFAULT_WEIGHTS

        district_codes = requirement.district_codes or []
        circle_codes = requirement.circle_codes or []
        budget_range = requirement.budget or [None, None]

        min_price = (budget_range[0] or 0) * 10000
        max_price = (budget_range[1] or 99999999) * 10000

        # 动态拼接 WHERE 条件
        where_clauses = []
        params = []
        param_idx = 1

        if district_codes:
            where_clauses.append(f"v.district_code = ANY(${param_idx})")
            params.append(district_codes)
            param_idx += 1
        if circle_codes:
            where_clauses.append(f"v.circle_code = ANY(${param_idx})")
            params.append(circle_codes)
            param_idx += 1

        if not where_clauses:
            where_sql = "TRUE"
        else:
            where_sql = " OR ".join(where_clauses)

        # 记录 limit 参数的位置
        limit_idx = param_idx
        params.append(limit)
        param_idx += 1

        # 加入权重参数
        params += [
            score_weights["base_score"],
            score_weights["living_score"],
            score_weights["traffic_score"],
            score_weights["school_score"],
            score_weights["hospital_score"],
            score_weights["park_score"],
            score_weights["restaurant_score"],
        ]

        # 加入预算参数
        params += [min_price, max_price]

        query = f"""
        SELECT v.circle_code, v.circle_name, v.district_name,
               t.avg_list_price, t.avg_sign_price, t.transaction_count,
               v.community_count,
               v.avg_base_score, v.avg_living_score, v.avg_traffic_score,
               v.avg_school_score, v.avg_hospital_score, v.avg_park_score,
               v.avg_restaurant_score,
               (
                   ROUND(
                       v.avg_base_score * CAST(${param_idx} AS NUMERIC) +
                       v.avg_living_score * CAST(${param_idx+1} AS NUMERIC) +
                       v.avg_traffic_score * CAST(${param_idx+2} AS NUMERIC) +
                       v.avg_school_score * CAST(${param_idx+3} AS NUMERIC) +
                       v.avg_hospital_score * CAST(${param_idx+4} AS NUMERIC) +
                       v.avg_park_score * CAST(${param_idx+5} AS NUMERIC) +
                       v.avg_restaurant_score * CAST(${param_idx+6} AS NUMERIC)
                   , 2)
                   + (RANDOM() * {random_factor})
               ) AS final_score
        FROM public.v_circle_scores v
        JOIN public.latest_circle_transactions t ON v.circle_code = t.circle_code
        WHERE {where_sql}
          AND t.avg_list_price BETWEEN ${param_idx+7} AND ${param_idx+8}
        ORDER BY final_score DESC
        LIMIT ${limit_idx}
        """

        print("🌐", "-" * 80)
        print(format_sql(query, params))
        print("🌐", "-" * 80)

        rows = await self.db.fetch_all(query, params)
        return [dict(row) for row in rows]


# 实例化
circle_recommender_service = CircleRecommenderService()

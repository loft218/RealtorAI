# app/services/recommender.py

from typing import Dict, List, Optional
from app.db import Database
from app.utils.sql_utils import format_sql
from app.models.requirement import ParsedRequirement
from app.core.config import settings


class RecommenderService:
    def __init__(self):
        self.db = Database

    async def recommend_communities(
        self,
        requirement: ParsedRequirement,
        weights: Optional[Dict[str, float]] = None,
        limit: int = 10,
    ) -> List[Dict]:
        if not requirement:
            raise ValueError("Requirement must be provided")
        score_weights = weights or settings.DEFAULT_WEIGHTS

        district_codes = requirement.district_codes or []
        circle_codes = requirement.circle_codes or []
        budget_range = requirement.budget or [None, None]
        bedroom_count = requirement.bedroom_count

        min_price = (budget_range[0] or 0) * 10000
        max_price = (budget_range[1] or 99999999) * 10000

        # 动态拼接 WHERE 条件
        where_clauses = []
        params = []
        param_idx = 1

        if district_codes and len(district_codes) > 0:
            where_clauses.append(f"v.district_code = ANY(${param_idx})")
            params.append(district_codes)
            param_idx += 1
        if circle_codes and len(circle_codes) > 0:
            where_clauses.append(f"v.circle_code = ANY(${param_idx})")
            params.append(circle_codes)
            param_idx += 1

        if not where_clauses:
            where_sql = "TRUE"
        else:
            where_sql = " OR ".join(where_clauses)

        # 记录 limit 参数在 params 中的位置
        limit_idx = param_idx
        params.append(limit)
        param_idx += 1

        # 其余参数
        params += [
            score_weights["base_score"],
            score_weights["living_score"],
            score_weights["traffic_score"],
            score_weights["school_score"],
            score_weights["hospital_score"],
            score_weights["park_score"],
            score_weights["restaurant_score"],
        ]
        if bedroom_count is not None:
            params += [bedroom_count, min_price, max_price]
            query = f"""
            SELECT v.id, v.name, v.district_name, v.circle_name, v.avg_listing_price,
                   v.base_score, v.living_score, v.traffic_score, v.school_score,
                   v.hospital_score, v.park_score, v.restaurant_score,
                   (
                       ROUND(
                           v.base_score * CAST(${param_idx} AS NUMERIC) +
                           v.living_score * CAST(${param_idx+1} AS NUMERIC) +
                           v.traffic_score * CAST(${param_idx+2} AS NUMERIC) +
                           v.school_score * CAST(${param_idx+3} AS NUMERIC) +
                           v.hospital_score * CAST(${param_idx+4} AS NUMERIC) +
                           v.park_score * CAST(${param_idx+5} AS NUMERIC) +
                           v.restaurant_score * CAST(${param_idx+6} AS NUMERIC)
                       , 2)
                   ) AS final_score
            FROM public.v_community_scores v
            JOIN public.mv_community_roomtype_avg_price p ON v.id = p.community_id
            WHERE {where_sql}
              AND p.room_type = ${param_idx+7}
              AND p.avg_price BETWEEN ${param_idx+8} AND ${param_idx+9}
            ORDER BY final_score DESC
            LIMIT ${limit_idx}
            """
        else:
            params += [min_price, max_price]
            query = f"""
            SELECT v.id, v.name, v.district_name, v.circle_name, v.avg_listing_price,
                   v.base_score, v.living_score, v.traffic_score, v.school_score,
                   v.hospital_score, v.park_score, v.restaurant_score,
                   (
                       ROUND(
                           v.base_score * CAST(${param_idx} AS NUMERIC) +
                           v.living_score * CAST(${param_idx+1} AS NUMERIC) +
                           v.traffic_score * CAST(${param_idx+2} AS NUMERIC) +
                           v.school_score * CAST(${param_idx+3} AS NUMERIC) +
                           v.hospital_score * CAST(${param_idx+4} AS NUMERIC) +
                           v.park_score * CAST(${param_idx+5} AS NUMERIC) +
                           v.restaurant_score * CAST(${param_idx+6} AS NUMERIC)
                       , 2)
                   ) AS final_score
            FROM public.v_community_scores v
            JOIN public.v_community_price_range r ON v.id = r.community_id
            WHERE {where_sql}
              AND NOT (r.max_avg_price < ${param_idx+7} OR r.min_avg_price > ${param_idx+8})
            ORDER BY final_score DESC
            LIMIT ${limit_idx}
            """
        print("💡", "-" * 80)
        print(format_sql(query, params))
        print("💡", "-" * 80)

        rows = await self.db.fetch_all(query, params)
        return [dict(row) for row in rows]

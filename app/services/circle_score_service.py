from typing import List, Dict
from app.db import Database


class CircleScoreService:
    def __init__(self):
        self.db = Database

    async def get_circles_scores(self, circle_codes: List[str]) -> List[Dict]:
        if not circle_codes:
            return []

        # 查询评分及排名
        sql_score = """
        SELECT district_code, district_name, circle_code, circle_name, community_count,
               avg_base_score, avg_base_score_rank, avg_base_score_percentile,
               avg_living_score, avg_living_score_rank, avg_living_score_percentile,
               avg_traffic_score, avg_traffic_score_rank, avg_traffic_score_percentile,
               avg_school_score, avg_school_score_rank, avg_school_score_percentile,
               avg_hospital_score, avg_hospital_score_rank, avg_hospital_score_percentile,
               avg_park_score, avg_park_score_rank, avg_park_score_percentile,
               avg_restaurant_score, avg_restaurant_score_rank, avg_restaurant_score_percentile
        FROM public.circle_score_rankings
        WHERE circle_code = ANY($1)
        """
        score_rows = await self.db.fetch_all(sql_score, [circle_codes])
        score_map = {row["circle_code"]: dict(row) for row in score_rows}

        # 查询最新均价及环比
        sql_price = """
        SELECT circle_code, latest_month, latest_avg_price, prev_avg_price, mom_ratio
        FROM public.v_circle_avg_price_monthly_ratio
        WHERE circle_code = ANY($1)
        """
        price_rows = await self.db.fetch_all(sql_price, [circle_codes])
        price_map = {row["circle_code"]: dict(row) for row in price_rows}

        # 合并数据
        result = []
        for code in circle_codes:
            score = score_map.get(code, {})
            price = price_map.get(code, {})
            merged = {**score, **price}
            result.append(merged)
        return result

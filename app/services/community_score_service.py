from typing import List, Dict
from app.db import Database


class CommunityScoreService:
    def __init__(self):
        self.db = Database

    async def get_communities_scores(self, community_ids: List[str]) -> List[Dict]:
        if not community_ids:
            return []
        # 查询评分信息
        sql_score = """
        SELECT 
            c.id, 
            c.name, 
            c.alias, 
            c.city_code, 
            c.district_code, 
            c.district_name, 
            c.circle_code, 
            c.circle_name, 
            c.circle_line, 
            c.completion_years, 
            c.building_types, 
            c.transaction_rights, 
            c.floor_totals, 
            c.house_types, 
            c.developer, 
            c.building_count, 
            c.household_count, 
            c.head_image, 
            c.bk_id, 
            c.grade, 
            c.created_at, 
            c.updated_at,
            r.ring, 
            r.year_range, 
            r.base_score, 
            r.living_score, 
            r.traffic_score, 
            r.school_score, 
            r.hospital_score, 
            r.park_score, 
            r.restaurant_score, 
            r.avg_listing_price, 
            r.base_rank, 
            r.base_exceed_pct, 
            r.living_rank, 
            r.living_exceed_pct, 
            r.traffic_rank, 
            r.traffic_exceed_pct, 
            r.school_rank, 
            r.school_exceed_pct, 
            r.hospital_rank, 
            r.hospital_exceed_pct, 
            r.park_rank, 
            r.park_exceed_pct, 
            r.restaurant_rank, 
            r.restaurant_exceed_pct
        FROM 
            public.v_community c
        JOIN 
            public.community_scores_ranking r
        ON 
            c.id = r.id
        WHERE c.id = ANY($1)
        """
        score_rows = await self.db.fetch_all(sql_score, [community_ids])
        score_map = {row["id"]: dict(row) for row in score_rows}

        # 查询价格信息
        sql_price = """
        SELECT community_id, latest_month, latest_avg_price, prev_avg_price, mom_ratio
        FROM public.v_community_listing_price_mom
        WHERE community_id = ANY($1)
        """
        price_rows = await self.db.fetch_all(sql_price, [community_ids])
        price_map = {row["community_id"]: dict(row) for row in price_rows}

        # 合并
        result = []
        for cid in community_ids:
            score = score_map.get(cid, {})
            price = price_map.get(cid, {})
            merged = {**score, **price}
            result.append(merged)
        return result

# app/services/recommender.py

from typing import Dict, List, Optional
from app.db import Database
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
        # 使用传入权重或默认权重
        score_weights = weights or settings.DEFAULT_WEIGHTS

        district_codes = requirement.district_codes or []
        circle_codes = requirement.circle_codes or []
        budget_range = requirement.budget or [None, None]

        query = """
        SELECT id, name, district_name, circle_name, avg_listing_price,
               base_score, living_score, traffic_score, school_score,
               hospital_score, park_score, restaurant_score,
               (
                   base_score * $4 +
                   living_score * $5 +
                   traffic_score * $6 +
                   school_score * $7 +
                   hospital_score * $8 +
                   park_score * $9 +
                   restaurant_score * $10
               ) AS final_score
        FROM public.v_community_scores
        WHERE (district_code = ANY($1)
          OR circle_code = ANY($2))
          AND avg_listing_price BETWEEN $11 AND $12
        ORDER BY final_score DESC
        LIMIT $3
        """

        min_price = budget_range[0] * 10000 if budget_range[0] else 0
        max_price = budget_range[1] * 10000 if budget_range[1] else 99999999

        params = [
            district_codes,  # $1
            circle_codes,  # $2
            limit,  # $3
            score_weights["base_score"],  # $4
            score_weights["living_score"],  # $5
            score_weights["traffic_score"],  # $6
            score_weights["school_score"],  # $7
            score_weights["hospital_score"],  # $8
            score_weights["park_score"],  # $9
            score_weights["restaurant_score"],  # $10
            min_price,  # $11
            max_price,  # $12
        ]

        print("Executing query with params:", params)

        rows = await self.db.fetch_all(query, params)
        return [dict(row) for row in rows]

from typing import List, Optional
from pydantic import BaseModel


class CommunityInfo(BaseModel):
    id: str
    name: str
    district_code: str
    district_name: str
    circle_code: str
    circle_name: str
    ring: Optional[str]
    year_range: Optional[str]
    base_score: float
    living_score: float
    traffic_score: float
    school_score: float
    hospital_score: float
    park_score: float
    restaurant_score: float
    avg_listing_price: float
    total_score: float


class CommunityRecommendationResponse(BaseModel):
    communities: List[CommunityInfo]

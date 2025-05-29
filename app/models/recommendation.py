from typing import List, Optional
from pydantic import BaseModel


class CommunityInfo(BaseModel):
    id: str
    name: str
    district_code: Optional[str]
    district_name: Optional[str]
    circle_code: Optional[str]
    circle_name: Optional[str]
    ring: Optional[str]
    year_range: Optional[str]
    base_score: Optional[float]
    living_score: Optional[float]
    traffic_score: Optional[float]
    school_score: Optional[float]
    hospital_score: Optional[float]
    park_score: Optional[float]
    restaurant_score: Optional[float]
    avg_listing_price: Optional[float]
    total_score: float


class CommunityRecommendationResponse(BaseModel):
    communities: List[CommunityInfo]

# app/api/recommendation.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.services.recommender import RecommenderService
from app.models.requirement import ParsedRequirement  # 导入 ParsedRequirement 模型

router = APIRouter()


# 请求模型：接受格式化结果和可选自定义权重
class RecommendRequest(BaseModel):
    parsed_requirement: Dict[str, Any]  # 直接传入 NLP 已解析结果
    custom_weights: Optional[Dict[str, float]] = Field(default=None)
    random_factor: Optional[float] = Field(
        default=1.0, description="推荐结果的随机扰动因子，100分制建议0.1~1.0"
    )


# 推荐结果结构
class CommunityScore(BaseModel):
    id: str
    name: str
    district_name: str
    circle_name: str
    base_score: float
    living_score: float
    traffic_score: float
    school_score: float
    hospital_score: float
    park_score: float
    restaurant_score: float
    avg_listing_price: float
    final_score: float


class RecommendResponse(BaseModel):
    top_communities: List[CommunityScore]


@router.post("/recommend-communities", response_model=RecommendResponse)
async def recommend_communities(req: RecommendRequest):
    parsed = req.parsed_requirement
    if not parsed:
        raise HTTPException(status_code=400, detail="缺少有效的结构化购房需求")

    weights = req.custom_weights
    random_factor = req.random_factor if req.random_factor is not None else 1.0

    # 调用推荐服务
    recommender = RecommenderService()
    parsed = ParsedRequirement(**parsed)  # Convert dict to ParsedRequirement
    top_communities = await recommender.recommend_communities(
        parsed, weights=weights, random_factor=random_factor
    )

    return {"top_communities": top_communities}

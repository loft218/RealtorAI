# app/api/recommendation.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.services.recommender import RecommenderService
from app.services.circle_recommender import CircleRecommenderService
from app.models.requirement import ParsedRequirement  # 导入 ParsedRequirement 模型

router = APIRouter()


# 请求模型：接受格式化结果和可选自定义权重
class RecommendRequest(BaseModel):
    parsed_requirement: Dict[str, Any]  # 直接传入 NLP 已解析结果
    custom_weights: Optional[Dict[str, float]] = Field(default=None)
    random_factor: Optional[float] = Field(
        default=1.0, description="推荐结果的随机扰动因子，100分制建议0.1~1.0"
    )
    limit: Optional[int] = Field(default=10, description="返回推荐结果的数量")


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


# 板块推荐结果结构
class CircleScore(BaseModel):
    circle_code: str
    circle_name: str
    district_name: str
    avg_list_price: float
    avg_sign_price: float
    transaction_count: int
    community_count: int
    avg_base_score: float
    avg_living_score: float
    avg_traffic_score: float
    avg_school_score: float
    avg_hospital_score: float
    avg_park_score: float
    avg_restaurant_score: float
    final_score: float


class RecommendResponse(BaseModel):
    top_communities: List[CommunityScore]


class RecommendCircleResponse(BaseModel):
    top_circles: List[CircleScore]


@router.post("/recommend-communities", response_model=RecommendResponse)
async def recommend_communities(req: RecommendRequest):
    parsed = req.parsed_requirement
    if not parsed:
        raise HTTPException(status_code=400, detail="缺少有效的结构化购房需求")

    weights = req.custom_weights
    random_factor = req.random_factor if req.random_factor is not None else 1.0
    limit = req.limit if req.limit is not None else 10

    # 调用推荐服务
    recommender = RecommenderService()
    parsed = ParsedRequirement(**parsed)  # Convert dict to ParsedRequirement
    top_communities = await recommender.recommend_communities(
        parsed, weights=weights, random_factor=random_factor, limit=limit
    )

    return {"top_communities": top_communities}


@router.post("/recommend-circles", response_model=RecommendCircleResponse)
async def recommend_circles(req: RecommendRequest):
    parsed = req.parsed_requirement
    if not parsed:
        raise HTTPException(status_code=400, detail="缺少有效的结构化购房需求")

    weights = req.custom_weights
    random_factor = req.random_factor if req.random_factor is not None else 1.0
    limit = req.limit if req.limit is not None else 10

    recommender = CircleRecommenderService()
    parsed = ParsedRequirement(**parsed)
    top_circles = await recommender.recommend_circles(
        requirement=parsed,
        weights=weights,
        random_factor=random_factor,
        limit=limit,
    )

    return {"top_circles": top_circles}

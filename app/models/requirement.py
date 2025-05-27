# app/models/requirement.py

from pydantic import BaseModel
from typing import List, Optional


class RawTextRequest(BaseModel):
    text: str


class ParsedRequirement(BaseModel):
    # 目标区域
    region: Optional[str] = None

    # NLP 阶段抽取出的可多个区名与商圈名
    district_names: Optional[List[str]] = None
    circle_names: Optional[List[str]] = None

    # 对应的编码列表
    district_codes: Optional[List[str]] = None
    circle_codes: Optional[List[str]] = None

    # 预算范围
    budget: Optional[List[int]] = None

    # 购房目的
    purpose: Optional[List[str]] = None

    # 家庭状况
    family_status: Optional[List[str]] = None  # 家庭状况（如“单身”、“已婚有子女”）

    # 其他偏好（文本形式）
    preferences: Optional[List[str]] = None

    class Config:
        schema_extra = {
            "example": {
                "region": "浦东张江",
                "district_names": ["浦东", "闵行"],
                "circle_names": ["张江", "古美"],
                "district_codes": ["310115", "310112"],
                "circle_codes": ["613000136", "611900068"],
                "budget": [750, 850],
                "purpose": ["自住优先"],
                "family_status": ["已婚", "有子女"],
                "preferences": ["靠近地铁", "靠小学"],
            }
        }

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
    budget: Optional[List[Optional[int]]] = [None, None]

    # 房型（卧室数量，整数）
    bedroom_count: Optional[int] = None

    # 购房目的
    purpose: Optional[List[str]] = None

    # 家庭状况
    family_status: Optional[List[str]] = None

    # 其他偏好（文本形式）
    preferences: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "region": "浦东张江",
                "district_names": ["浦东"],
                "circle_names": ["张江"],
                "district_codes": ["310115"],
                "circle_codes": ["613000136"],
                "budget": [750, 850],
                "bedroom_count": 3,
                "purpose": ["自住优先"],
                "family_status": ["已婚", "有子女"],
                "preferences": ["靠近地铁", "靠小学"],
            }
        }

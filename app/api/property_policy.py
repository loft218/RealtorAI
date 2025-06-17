from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import Any, Dict
from app.services.property_policy_service import PropertyPolicyService
from datetime import datetime, date

router = APIRouter()


class PropertyPolicyResponse(BaseModel):
    id: int
    policy_date: datetime
    policy_data: Dict[str, Any]
    data_source: str
    created_at: datetime
    updated_at: datetime


@router.get("/property-policy", response_model=PropertyPolicyResponse)
async def get_property_policy():
    row = await PropertyPolicyService.get_latest_policy()
    if not row:
        raise HTTPException(status_code=404, detail="未找到政策数据")
    return PropertyPolicyResponse(**row)

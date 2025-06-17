from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from app.services.market_stats_service import MarketStatsService

router = APIRouter()


class MarketStatsResponse(BaseModel):
    data: Dict[str, Any]


@router.get("/market-stats", response_model=MarketStatsResponse)
async def get_market_stats():
    data = MarketStatsService.get_latest_stats()
    if not data:
        raise HTTPException(status_code=404, detail="数据文件不存在或读取失败")
    return {"data": data}

from datetime import datetime, date
from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel, validator
from typing import Any, Dict
from app.services.market_overview_service import MarketOverviewService

app = FastAPI()
router = APIRouter()


class MarketOverviewResponse(BaseModel):
    id: int
    snapshot_date: datetime
    overview_data: Dict[str, Any]
    data_source: str
    created_at: datetime
    updated_at: datetime


@router.get("/market-overview", response_model=MarketOverviewResponse)
async def get_market_overview():
    row = await MarketOverviewService.get_latest_overview()
    if not row:
        raise HTTPException(status_code=404, detail="未找到市场概览数据")
    return row


app.include_router(router, prefix="/api")

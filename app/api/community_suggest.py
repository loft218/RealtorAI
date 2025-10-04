from fastapi import APIRouter, Query, HTTPException
from typing import List
from pydantic import BaseModel

from app.services.community_suggest_service import CommunitySuggestService

router = APIRouter()


class CommunitySuggestItem(BaseModel):
    id: str
    name: str
    display_name: str
    alias: str | None = None
    circle_code: str | None = None
    circle_name: str | None = None
    district_code: str | None = None
    district_name: str | None = None


class CommunitySuggestResponse(BaseModel):
    suggestions: List[CommunitySuggestItem]


@router.get("/community-suggest", response_model=CommunitySuggestResponse)
async def community_suggest(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50)):
    if not q:
        raise HTTPException(status_code=400, detail="query parameter 'q' is required")

    service = CommunitySuggestService()
    results = await service.suggest(q, limit=limit)
    return {"suggestions": results}

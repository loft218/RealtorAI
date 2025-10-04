from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from app.services.community_suggest_service import CommunitySuggestService

router = APIRouter()


class CommunitySuggestItem(BaseModel):
    id: str
    name: str
    display_name: str
    alias: Optional[str] = None
    circle_code: Optional[str] = None
    circle_name: Optional[str] = None
    district_code: Optional[str] = None
    district_name: Optional[str] = None


class CommunitySuggestResponse(BaseModel):
    suggestions: List[CommunitySuggestItem]


@router.get("/community-suggest", response_model=CommunitySuggestResponse)
async def community_suggest(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50)):
    if not q:
        raise HTTPException(status_code=400, detail="query parameter 'q' is required")

    service = CommunitySuggestService()
    results = await service.suggest(q, limit=limit)
    return {"suggestions": results}

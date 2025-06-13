from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from app.services.community_score_service import CommunityScoreService

app = FastAPI()
router = APIRouter()
community_score_service = CommunityScoreService()


class CommunityScoreRequest(BaseModel):
    community_ids: List[str]


class CommunityScoreResponse(BaseModel):
    communities: List[Dict]


@router.post("/community-scores", response_model=CommunityScoreResponse)
async def get_community_scores(req: CommunityScoreRequest):
    if not req.community_ids:
        raise HTTPException(status_code=400, detail="community_ids不能为空")
    communities = await community_score_service.get_communities_scores(
        req.community_ids
    )
    return {"communities": communities}


app.include_router(router, prefix="/api")

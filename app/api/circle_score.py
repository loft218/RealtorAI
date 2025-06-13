from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from app.services.circle_score_service import CircleScoreService

app = FastAPI()
router = APIRouter()
circle_score_service = CircleScoreService()


class CircleScoreRequest(BaseModel):
    circle_codes: List[str]


class CircleScoreResponse(BaseModel):
    circles: List[Dict]


@router.post("/circle-scores", response_model=CircleScoreResponse)
async def get_circle_scores(req: CircleScoreRequest):
    if not req.circle_codes:
        raise HTTPException(status_code=400, detail="circle_codes不能为空")
    circles = await circle_score_service.get_circles_scores(req.circle_codes)
    return {"circles": circles}


app.include_router(router, prefix="/api")

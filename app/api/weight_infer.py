# app/api/weight_infer.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.weight_inferencer import weight_inferencer

router = APIRouter()


class WeightInferRequest(BaseModel):
    requirement: Dict[str, Any]


class WeightInferResponse(BaseModel):
    weights: Dict[str, float]


@router.post("/infer-weights", response_model=WeightInferResponse)
async def infer_weights(req: WeightInferRequest):
    weights = await weight_inferencer.infer_weights(req.requirement)
    if not weights:
        raise HTTPException(status_code=500, detail="权重推理失败")
    return {"weights": weights}

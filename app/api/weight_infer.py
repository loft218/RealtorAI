# app/api/weight_infer.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.services.weight_infer_local import infer_weights_locally

router = APIRouter()


class WeightInferRequest(BaseModel):
    requirement: str  # 修改为文本类型
    alpha: float = 2.0


class WeightInferResponse(BaseModel):
    weights: Dict[str, float]


@router.post("/infer-weights", response_model=WeightInferResponse)
async def infer_weights(req: WeightInferRequest):
    weights = await infer_weights_locally(
        req.requirement, alpha=req.alpha
    )  # 直接传文本
    if not weights:
        raise HTTPException(status_code=500, detail="权重推理失败")
    return {"weights": weights}

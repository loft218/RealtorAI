from fastapi import APIRouter, HTTPException
from app.models.requirement import RawTextRequest, ParsedRequirement
# from app.services.nlp_parser import parse_text
from app.services.nlp_parser_local import parse_text

router = APIRouter()


@router.post("/parse-requirement", response_model=ParsedRequirement)
async def parse_requirement(req: RawTextRequest):
    try:
        result = await parse_text(req.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

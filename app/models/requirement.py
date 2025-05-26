# app/models/requirement.py

from pydantic import BaseModel
from typing import List, Optional


class RawTextRequest(BaseModel):
    text: str


class ParsedRequirement(BaseModel):
    region: Optional[str]
    budget_min: Optional[int]
    budget_max: Optional[int]
    purpose: Optional[str]
    other_preferences: Optional[List[str]] = []

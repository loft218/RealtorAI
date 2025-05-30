from typing import List
from app.services.location_mapper import mapper
from app.services.deepseek_client import deepseek_client

# Prompt: LLM 只解析预算、购房目的和其他偏好
PROMPT_TEMPLATE = """
请将以下购房需求文本提取成结构化 JSON,仅需包含以下字段:
- region: 目标区域（如“浦东”、“张江”）,返回字符串
- budget_min: 预算下限（万元）,无法确定时返回 None
- budget_max: 预算上限（万元),无法确定时返回 None
- bedroom_count: 房型（卧室数量，整数），无法确定时返回 None
- purpose: 购房目的（如“首套自住”、“投资升值”,"改善"），返回字符串数组
- family_status: 家庭状况（如“单身”、“已婚有子女”、”带老人“），返回字符串数组
- preferences: 偏好（如“靠近地铁”、“学区”），返回字符串数组

输出格式示例：
```json
{
  "region": "浦东张江",
  "budget_min": 750,
  "budget_max": 850,
  "bedroom_count": 3,
  "purpose": ["自住","改善"],
  "family_status": ["已婚","有子女","带老人"],
  "preferences": ["靠近地铁","靠小学"]
}
```
购房需求文本：
{text}
"""


async def parse_text(text: str) -> dict:
    # 1. 提取地名
    district_names, circle_names = mapper.extract(text)

    # 2. 构造 prompt 并调用 LLM
    prompt = PROMPT_TEMPLATE.replace("{text}", text.strip())
    parsed_llm = await deepseek_client.call(prompt)
    if not parsed_llm:
        return {}

    # 3. 地图反查代码
    district_codes: List[str] = [
        mapper.get_district_code(name)
        for name in district_names
        if mapper.get_district_code(name)
    ]

    circle_codes: List[str] = [
        mapper.get_circle_code(name)
        for name in circle_names
        if mapper.get_circle_code(name)
    ]

    # 4. 预算修正
    budget_min = parsed_llm.get("budget_min")
    budget_max = parsed_llm.get("budget_max")
    if budget_min is not None and budget_max is not None and budget_min == budget_max:
        base = budget_min
        ratio = 0.1
        delta = max(int(base * ratio), 50)
        budget_min = base - delta
        budget_max = base + delta

    # 5. 返回结构化结果
    return {
        "region": parsed_llm.get("region"),
        "district_names": district_names or None,
        "district_codes": district_codes or None,
        "circle_names": circle_names or None,
        "circle_codes": circle_codes or None,
        "budget": [budget_min, budget_max],
        "bedroom_count": parsed_llm.get("bedroom_count"),
        "purpose": parsed_llm.get("purpose"),
        "family_status": parsed_llm.get("family_status"),
        "preferences": parsed_llm.get("preferences", []),
    }

import re
import json
import httpx
from typing import List, Optional
from app.core.config import settings
from app.services.location_mapper import mapper

# Prompt: LLM 只解析预算、购房目的和其他偏好
PROMPT_TEMPLATE = """
请将以下购房需求文本提取成结构化 JSON,仅需包含以下字段:
- region: 目标区域（如“浦东”、“张江”）,返回字符串
- budget_min: 预算下限（万元）,无法确定时返回 None
- budget_max: 预算上限（万元),无法确定时返回 None
- purpose: 购房目的（如“首套自住”、“投资升值”,"改善"），返回字符串数组
- family_status: 家庭状况（如“单身”、“已婚有子女”、”带老人“），返回字符串数组
- preferences: 偏好（如“靠近地铁”、“学区”），返回字符串数组

输出格式示例：
```json
{
  "region": "浦东张江",
  "budget_min": 750,
  "budget_max": 850,
  "purpose": ["自住","改善"],
  "family_status": ["已婚","有子女","带老人"],
  "preferences": ["靠近地铁","靠小学"]
}
```
购房需求文本：
{text}
"""


async def parse_text(text: str) -> dict:
    # 1. 用 FlashText 预提取 district_names 和 circle_names
    district_names, circle_names = mapper.extract(text)
    # 2. 调用 DeepSeek / LLM 解析其余字段
    prompt = PROMPT_TEMPLATE.replace("{text}", text.strip())
    headers = {
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",  # 根据实际情况替换模型名称
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.DEEPSEEK_API_URL, json=payload, headers=headers, timeout=30
        )
        response.raise_for_status()
        result = response.json()

        # 从 DeepSeek 返回内容中提取 JSON 部分
        content = result["choices"][0]["message"]["content"]
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            # 若未匹配到 JSON，则返回空 dict 或抛异常
            return {}

        parsed_llm = json.loads(match.group())

        # 3. 映射 district_names -> district_codes
        district_codes: List[str] = []
        for name in district_names:
            code = mapper.get_district_code(name)
            if code:
                district_codes.append(code)

        # 4. 映射 circle_names -> circle_codes
        circle_codes: List[str] = []
        for cname in circle_names:
            # 可能同一商圈名出现于多个区，依次尝试
            for dcode in district_codes:
                ccode = mapper.get_circle_code(dcode, cname)
                if ccode and ccode not in circle_codes:
                    circle_codes.append(ccode)

        # 原始值
        budget_min = parsed_llm.get("budget_min", None)
        budget_max = parsed_llm.get("budget_max", None)

        # —— 新增：如果 LLM 给出定值，则强制生成一个浮动区间 ——
        if (
            budget_min is not None
            and budget_max is not None
            and budget_min == budget_max
        ):
            base = budget_min
            # 这里用 10% 的浮动，也可改成从 settings 里读
            ratio = 0.10
            delta = max(int(base * ratio), 50)  # 最少浮动 50 万
            budget_min = base - delta
            budget_max = base + delta

        # 5. 返回最终结构
        return {
            "region": parsed_llm.get("region", None),
            "district_names": district_names or None,
            "district_codes": district_codes or None,
            "circle_names": circle_names or None,
            "circle_codes": circle_codes or None,
            "budget": [budget_min, budget_max],
            "purpose": parsed_llm.get("purpose"),
            "family_status": parsed_llm.get("family_status"),
            "preferences": parsed_llm.get("preferences", []),
        }

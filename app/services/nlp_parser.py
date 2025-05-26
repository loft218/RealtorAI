# app/services/nlp_parser.py

import re
import json
import httpx
from app.core.config import settings

PROMPT_TEMPLATE = """
请将以下购房需求文本提取成结构化 JSON，字段包括：
- region：目标区域（如“朝阳区”）
- budget_min：预算下限（万元）
- budget_max：预算上限（万元）
- purpose：购房目的（如“首套自住”、“投资升值”）
- other_preferences：其他偏好，如“近地铁”、“靠学校”

输出格式:
```json
{
  "region": "...",
  "budget_min": ...,
  "budget_max": ...,
  "purpose": "...",
  "other_preferences": ["..."]
}```
购房需求文本：
{text}
"""


async def parse_text(text: str) -> dict:
    """
    将用户的购房需求文本发送给 DeepSeek NLP 服务，
    并返回解析后的结构化 JSON。
    """
    # 填充 prompt
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

        parsed = json.loads(match.group())
        return {
            "region": parsed.get("region"),
            "budget_min": parsed.get("budget_min"),
            "budget_max": parsed.get("budget_max"),
            "purpose": parsed.get("purpose"),
            "other_preferences": parsed.get("other_preferences", []),
        }

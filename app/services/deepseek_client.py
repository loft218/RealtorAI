import re
import json
import httpx
from typing import Optional
from app.core.config import settings


class DeepSeekClient:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = settings.DEEPSEEK_API_URL

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def call(
        self,
        prompt: str,
        model: str = "deepseek-chat",
        temperature: float = 0.2,
        web_search: bool = False,  # 新增参数控制是否联网
    ) -> Optional[dict]:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "web_search": web_search,  # 关键参数，启用联网搜索
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url, json=payload, headers=self.headers, timeout=30
            )
            response.raise_for_status()
            result = response.json()

        content = result["choices"][0]["message"]["content"]
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            return None

        return json.loads(match.group())


# 单例导出
deepseek_client = DeepSeekClient()

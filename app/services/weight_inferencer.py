from typing import List, Dict, Any
from app.services.deepseek_client import deepseek_client

# 权重推理的Prompt模板
WEIGHT_INFER_PROMPT = """
你是一个房产推荐系统的智能权重推理助手。
根据用户的购房需求，动态生成各评分项的权重（权重总和为1，保留三位小数）。

评分项包括：
- base_score（小区基础品质）
- living_score（居住舒适度）
- traffic_score（交通便利度）
- school_score（学校资源）
- hospital_score（医院资源）
- park_score（公园绿地）
- restaurant_score（餐饮设施）

用户需求：
{requirement}

请输出 JSON 格式，例如：
{{
  "base_score": 0.15,
  "living_score": 0.20,
  "traffic_score": 0.25,
  "school_score": 0.20,
  "hospital_score": 0.05,
  "park_score": 0.10,
  "restaurant_score": 0.05
}}
"""


class WeightInferencer:
    async def infer_weights(self, requirement: Dict[str, Any]) -> Dict[str, float]:
        prompt = WEIGHT_INFER_PROMPT.format(requirement=requirement)
        result = await deepseek_client.call(prompt)
        if not result:
            # 返回默认权重或空权重
            return {
                "base_score": 0.15,
                "living_score": 0.20,
                "traffic_score": 0.20,
                "school_score": 0.15,
                "hospital_score": 0.10,
                "park_score": 0.10,
                "restaurant_score": 0.10,
            }
        return {
            k: float(v)
            for k, v in result.items()
            if k
            in [
                "base_score",
                "living_score",
                "traffic_score",
                "school_score",
                "hospital_score",
                "park_score",
                "restaurant_score",
            ]
        }


weight_inferencer = WeightInferencer()

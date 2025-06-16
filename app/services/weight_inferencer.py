import numpy as np

from typing import Dict
from app.core.config import settings
from app.services.deepseek_client import deepseek_client

# 优化后的 Prompt
WEIGHT_INFER_PROMPT = """
你是一个房产推荐系统的智能权重推理助手。
请根据用户的购房需求，为以下评分项分配重要性权重，权重总和为1，保留三位小数。

评分项包括：
- base_score（小区基础品质）
- living_score（居住舒适度）
- traffic_score（交通便利度）
- school_score（学校资源）
- hospital_score（医院资源）
- park_score（公园绿地）
- restaurant_score（餐饮设施）

要求：
1. 权重不能平均分配，请结合需求内容突出主要诉求。
2. 如果用户表达了明显的偏好，请将相关项的权重适当拉高。
3. 请避免每项权重接近，请在主项与次项之间拉开差距。
4. 请只返回 JSON 格式，如下示例：

示例：
{{
  "base_score": 0.15,
  "living_score": 0.25,
  "traffic_score": 0.30,
  "school_score": 0.20,
  "hospital_score": 0.02,
  "park_score": 0.05,
  "restaurant_score": 0.03
}}

用户需求：
{requirement}
"""


def stretch_weights(weights: Dict[str, float], alpha: float = 2.0) -> Dict[str, float]:
    """
    对权重进行指数拉伸，增强主次差异。
    alpha 越大，主项越突出，次项越弱。默认 2.0。
    """
    keys = list(weights.keys())
    values = np.array([weights[k] for k in keys])
    stretched = np.power(values, alpha)
    normalized = stretched / stretched.sum()
    return {k: round(float(v), 3) for k, v in zip(keys, normalized)}


class WeightInferencer:
    async def infer_weights(
        self, requirement_text: str, alpha: float = 2.0
    ) -> Dict[str, float]:
        prompt = WEIGHT_INFER_PROMPT.format(requirement=requirement_text)
        result = await deepseek_client.call(prompt)

        # 默认权重作为 fallback
        default_weights = settings.DEFAULT_WEIGHTS

        if not result or not isinstance(result, dict):
            return stretch_weights(default_weights, alpha=alpha)

        # 提取有效权重
        parsed_weights = {
            k: float(result[k])
            for k in default_weights
            if k in result and isinstance(result[k], (float, int))
        }

        # 用默认值补全缺失项
        for k in default_weights:
            parsed_weights.setdefault(k, default_weights[k])

        return stretch_weights(parsed_weights)


# 实例化供外部调用
weight_inferencer = WeightInferencer()

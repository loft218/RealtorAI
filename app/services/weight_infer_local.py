import jieba
import numpy as np
from typing import Dict
from app.config.keyword_config import WEIGHT_KEYWORDS

DEFAULT_BASE_SCORE = 0.2  # 没匹配到关键词时的默认基础得分

def stretch_weights(weights: Dict[str, float], alpha: float = 1.5) -> Dict[str, float]:
    """
    对权重进行拉伸处理，使主项更突出，次项更低调
    :param weights: 原始归一化权重
    :param alpha: 拉伸系数（默认2）
    :return: 拉伸后的归一化权重（保留3位小数）
    """
    keys = list(weights.keys())
    values = np.array([weights[k] for k in keys])
    stretched = np.power(values, alpha)
    normalized = stretched / stretched.sum()
    return {k: round(float(v), 3) for k, v in zip(keys, normalized)}


async def infer_weights_locally(requirement_text: str) -> Dict[str, float]:
    """
    根据用户需求文本，使用分词和关键词匹配进行评分项权重推理（本地）
    :param requirement_text: 用户购房需求文本
    :return: 各项评分权重（总和为1）
    """
    words = list(jieba.cut(requirement_text))  # 精确模式分词
    raw_scores = {}

    for score_key, keywords in WEIGHT_KEYWORDS.items():
        matched = sum(1 for word in words if word in keywords)
        raw_scores[score_key] = matched if matched > 0 else DEFAULT_BASE_SCORE

    total_score = sum(raw_scores.values())
    normalized_scores = {k: v / total_score for k, v in raw_scores.items()}

    # return normalized_scores
    return stretch_weights(normalized_scores)


# ✅ 示例调用
if __name__ == "__main__":
    user_requirement = (
        "房龄新，交通方便，附近有地铁站，学校资源丰富，公园绿地多，居住舒适度高。"
    )
    print("用户需求：", user_requirement)
    weights = infer_weights_locally(user_requirement)
    print("推理得到的评分项权重：")
    print(weights)

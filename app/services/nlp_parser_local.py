import re
import jieba
from typing import List, Dict, Any
from app.services.location_mapper import mapper
from app.config.keyword_config import (
    PURPOSE_KEYWORDS,
    FAMILY_STATUS_KEYWORDS,
    PREFERENCE_KEYWORDS,
    BEDROOM_MAP,
)


BEDROOM_PATTERNS = [
    r"([一二两三四五六七八九])房",
    r"([一二两三四五六七八九])室",
    r"([一二两三四五六七八九])居",
    r"(\d)房",
    r"(\d)室",
    r"(\d)居",
]

BUDGET_PATTERNS = [
    # 1. 数字 + 单位 + 区间（带"万"或"w"）+ 连接词：到、-、~、至
    r"(?P<min>\d{2,4})\s*[万wW]?\s*(?:到|[-~—～至])\s*(?P<max>\d{2,4})\s*[万wW]?(?:之间|以内|左右)?",
    # 2. 纯数字区间（如：5000000到8000000）
    r"(?P<min>\d{5,8})\s*(?:到|[-~—～至])\s*(?P<max>\d{5,8})",
    # 3. 单个预算值 + 后缀词（模糊）：预算在500万左右
    r"(?:预算[是为在]?)?\s*(?P<value>\d{2,4})\s*[万wW]?\s*(?:左右|以内)?",
    # 4. 单个大数字预算值（单位为元）
    r"(?P<value>\d{6,8})(?![万wW])",
]


def extract_budget(text: str) -> (int, int):
    import re

    for pattern in BUDGET_PATTERNS:
        match = re.search(pattern, text)
        if not match:
            continue

        group = match.groupdict()
        if "min" in group and "max" in group:
            min_val = int(group["min"])
            max_val = int(group["max"])
            # 单位判断：若为元则转换为万元
            if min_val > 10000 and max_val > 10000:
                min_val //= 10000
                max_val //= 10000
            return min_val, max_val

        if "value" in group:
            value = int(group["value"])
            if value > 10000:
                value //= 10000
            delta = max(50, int(value * 0.1))  # 默认10%的浮动
            return value - delta, value + delta

    return None, None


def extract_bedroom_count(text: str) -> int:
    for pattern in BEDROOM_PATTERNS:
        assert isinstance(pattern, str), f"Pattern {pattern} is not a string"
        match = re.search(pattern, text)
        if match:
            val = match.group(1)
            if val in BEDROOM_MAP:
                return BEDROOM_MAP[val]
            elif val.isdigit():
                return int(val)
    return None


# -------------------- 主函数 --------------------
async def parse_text(text: str) -> Dict[str, Any]:
    text = text.strip()
    words = list(jieba.cut(text))

    # 1. 地名提取（区、板块名）
    district_names, circle_names = mapper.extract(text)
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
    region = (
        "".join(district_names + circle_names)
        if district_names or circle_names
        else None
    )

    # 2. 预算提取
    budget_min, budget_max = extract_budget(text)

    # 3. 卧室数量提取（支持中文/数字/居/房/室）
    bedroom_count = extract_bedroom_count(text)

    # 4. 购房目的提取
    purpose = [k for k, v in PURPOSE_KEYWORDS.items() if any(word in text for word in v)] or None

    # 5. 家庭状况提取
    family_status = [k for k, v in FAMILY_STATUS_KEYWORDS.items() if any(word in text for word in v)] or None

    # 6. 偏好提取
    preferences = [k for k, v in PREFERENCE_KEYWORDS.items() if any(word in text for word in v)] or None

    # 7. 构造返回结构
    return {
        "region": region,
        "district_names": district_names or None,
        "district_codes": district_codes or None,
        "circle_names": circle_names or None,
        "circle_codes": circle_codes or None,
        "budget": [budget_min, budget_max] if budget_min or budget_max else None,
        "bedroom_count": bedroom_count,
        "purpose": purpose or None,
        "family_status": family_status or None,
        "preferences": preferences,
    }

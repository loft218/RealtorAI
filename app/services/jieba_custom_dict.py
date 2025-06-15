import jieba
from app.config.keyword_config import (
    WEIGHT_KEYWORDS,
    PURPOSE_KEYWORDS,
    FAMILY_STATUS_KEYWORDS,
    PREFERENCE_KEYWORDS,
)


def add_all_custom_words():
    keyword_dicts = [
        WEIGHT_KEYWORDS,
        PURPOSE_KEYWORDS,
        FAMILY_STATUS_KEYWORDS,
        PREFERENCE_KEYWORDS,
    ]
    words = set()
    for d in keyword_dicts:
        for v in d.values():
            if isinstance(v, list):
                words.update(v)
            else:
                words.add(v)
    for word in words:
        jieba.add_word(word)

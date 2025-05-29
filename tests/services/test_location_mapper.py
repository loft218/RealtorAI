import pytest
from unittest.mock import mock_open, patch
from app.services.location_mapper import LocationMapper


@pytest.fixture
def location_mapper(mocker):
    return LocationMapper()


@pytest.mark.parametrize(
    "text,expected_districts,expected_circles",
    [
        # 基础匹配测试
        ("浦东新区的陆家嘴板块", ["浦东"], ["陆家嘴"]),
        ("黄浦区的外滩很漂亮", ["黄浦"], []),
        ("徐汇区的徐家汇商圈", ["徐汇"], ["徐家汇"]),
        # 带不同后缀的测试
        ("浦东新区区的陆家嘴片区", ["浦东"], ["陆家嘴"]),
        ("静安新区的南京西路商圈", ["静安"], ["南京西路"]),
        ("黄浦区的南京西路板块", ["黄浦"], ["南京西路"]),  # 注意：这里测试跨区同名商圈
        # 多个匹配测试
        ("浦东新区和黄浦区都有好房子", ["浦东", "黄浦"], []),
        ("陆家嘴板块和外滩片区都很繁华", [], ["陆家嘴"]),
        ("徐汇区和静安区的徐家汇和南京西路", ["徐汇", "静安"], ["徐家汇", "南京西路"]),
        # 无匹配测试
        ("北京和上海都是大城市", [], []),
        ("这个区域没有定义", [], []),
        ("随便写点什么", [], []),
        # 大小写不敏感测试
        ("pUdOnG新区的陆家嘴", [], ["陆家嘴"]),
        ("黄浦区的XU家汇", ["黄浦"], []),  # 注意：这里测试大小写不敏感
        # 混合内容测试
        (
            "在浦东新区和静安区之间，陆家嘴和南京西路都是热门区域",
            ["浦东", "静安"],
            ["陆家嘴", "南京西路"],
        ),
        ("黄浦区的外滩与徐汇区的徐家汇哪个更好?", ["黄浦", "徐汇"], ["徐家汇"]),
        # 边界情况测试
        ("浦东新区", ["浦东"], []),  # 只有区
        ("陆家嘴", [], ["陆家嘴"]),  # 只有商圈
        ("", [], []),  # 空字符串
        ("   ", [], []),  # 只有空格
    ],
)
def test_extract(location_mapper, text, expected_districts, expected_circles):
    """测试extract方法从文本中提取区和商圈名称"""
    districts, circles = location_mapper.extract(text)

    # 使用集合比较忽略顺序，但不考虑重复(根据实现需求)
    assert set(districts) == set(expected_districts)
    assert set(circles) == set(expected_circles)

    # 如果需要保持顺序和唯一性(根据实现中的append逻辑)
    assert len(districts) == len(expected_districts)
    assert len(circles) == len(expected_circles)


def test_extract_with_duplicates(location_mapper):
    """测试文本中重复出现的区和商圈名称"""
    text = "浦东新区的陆家嘴很棒，浦东新区的发展很快，陆家嘴的房价很高"
    districts, circles = location_mapper.extract(text)

    # 根据实现，应该去重
    assert districts == ["浦东"]
    assert circles == ["陆家嘴"]


def test_extract_with_special_characters(location_mapper):
    """测试包含特殊字符的文本"""
    text = "浦东新区!@#的$%^陆家嘴&*()板块"
    districts, circles = location_mapper.extract(text)

    assert districts == ["浦东"]
    assert circles == ["陆家嘴"]


def test_extract_partial_matches(location_mapper):
    """测试部分匹配不应被提取"""
    text = "浦东的陆家"  # 部分名称不应匹配
    districts, circles = location_mapper.extract(text)

    assert districts == ["浦东"]
    assert circles == []


def test_extract_partial_matches2(location_mapper):
    text = "我想在张江地铁站附近购买一套房子"  # 部分名称不应匹配
    districts, circles = location_mapper.extract(text)

    assert districts == []
    assert circles == ["张江"]

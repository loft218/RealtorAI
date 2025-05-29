import csv
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from flashtext import KeywordProcessor

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"


class LocationMapper:
    def __init__(self):
        # 原始映射表
        self.district_map: Dict[str, str] = {}
        self.circle_map: Dict[Tuple[str, str], str] = {}
        # FlashText 关键词处理器
        self.district_proc = KeywordProcessor(case_sensitive=False)
        self.circle_proc = KeywordProcessor(case_sensitive=False)

        self._load_districts()
        self._load_circles()
        self._build_processors()

    def _load_districts(self):
        path = DATA_DIR / "district.csv"
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["name"].strip()
                code = row["code"].strip()
                # 存映射
                self.district_map[name] = code

    def _load_circles(self):
        path = DATA_DIR / "circle.csv"
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["name"].strip()
                code = row["code"].strip()
                district_code = row["district_code"].strip()
                self.circle_map[name] = code

    def _build_processors(self):
        # 区名处理器，加入“区”“新区”后缀
        for name in self.district_map.keys():
            self.district_proc.add_keyword(name)
            self.district_proc.add_keyword(f"{name}区")
            self.district_proc.add_keyword(f"{name}新区")
        # 商圈处理器
        for name in self.circle_map.keys():
            self.circle_proc.add_keyword(name)
            # 如有“板块”或“片区”后缀可按需加入
            self.circle_proc.add_keyword(f"{name}板块")
            self.circle_proc.add_keyword(f"{name}片区")

    def get_district_code(self, district_name: str) -> Optional[str]:
        return self.district_map.get(district_name.strip())

    def get_circle_code(self, circle_name: str) -> Optional[str]:
        return self.circle_map.get((circle_name.strip()))

    def extract(self, text: str) -> Tuple[List[str], List[str]]:
        """
        用 FlashText 从文本里抽取 district_names 和 circle_names（原始名称，不含“区”“板块”等后缀）。
        返回 ([district_name,...], [circle_name,...])。
        """
        # 抽取原始关键词
        raw_districts = self.district_proc.extract_keywords(text)
        raw_circles = self.circle_proc.extract_keywords(text)

        # 清洗后缀，统一成原始名称
        district_names = []
        for d in raw_districts:
            name = d.rstrip("区新区")
            if name not in district_names:
                district_names.append(name)

        circle_names = []
        for c in raw_circles:
            name = c.rstrip("板块片区商圈")
            if name not in circle_names:
                circle_names.append(name)

        return district_names, circle_names


# 单例
mapper = LocationMapper()

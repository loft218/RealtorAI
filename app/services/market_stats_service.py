import os
import json
from typing import Dict, Any, Optional


class MarketStatsService:
    @staticmethod
    def get_latest_stats() -> Optional[Dict[str, Any]]:
        file_path = os.path.join(
            os.path.dirname(__file__), "../../data/sh_realestate_market_stats.json"
        )
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return data[0]  # 返回最新一条
            elif isinstance(data, dict):
                return data
            else:
                return None
        except Exception:
            return None

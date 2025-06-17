from typing import Optional, Dict, Any
from app.db import Database
import json


class MarketOverviewService:
    @staticmethod
    async def get_latest_overview() -> Optional[Dict[str, Any]]:
        sql = """
        SELECT id, snapshot_date, overview_data, data_source, created_at, updated_at
        FROM public.sh_secondhand_market_overview
        ORDER BY id DESC LIMIT 1;
        """
        rows = await Database.fetch_all(sql)
        if not rows:
            return None
        row = dict(rows[0])
        # 类型兼容处理
        if isinstance(row.get("overview_data"), str):
            row["overview_data"] = json.loads(row["overview_data"])
        return row

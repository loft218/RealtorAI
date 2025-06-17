import json
from app.db import Database


class PropertyPolicyService:
    @staticmethod
    async def get_latest_policy():
        sql = """
        SELECT id, policy_date, policy_data, data_source, created_at, updated_at
        FROM public.sh_property_policies
        ORDER BY id DESC LIMIT 1;
        """
        rows = await Database.fetch_all(sql)
        if not rows:
            return None
        row = dict(rows[0])
        # 兼容 policy_data 为字符串的情况
        if isinstance(row.get("policy_data"), str):
            row["policy_data"] = json.loads(row["policy_data"])
        return row

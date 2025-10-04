from typing import List, Dict, Any
from app.db import Database


class CommunitySuggestService:
    def __init__(self):
        self.db = Database

    async def suggest(self, q: str, limit: int = 10) -> List[Dict[str, Any]]:
        """在 public.v_community 上进行前缀/模糊查询，返回前 limit 条结果。

        搜索顺序：name 前缀匹配 > alias 前缀匹配 > name 模糊匹配。
        返回字段：id,name,alias,circle_code,circle_name,district_code,district_name
        """
        if not q:
            return []

        # 使用 ILIKE 和 % 匹配来做前缀和模糊，优先 name 前缀
        sql = """
        SELECT id, name, alias, circle_code, circle_name, district_code, district_name,
          (CASE WHEN name ILIKE $1 || '%' THEN 0
                WHEN alias ILIKE $1 || '%' THEN 1
                ELSE 2 END) AS match_type
        FROM public.v_community
        WHERE name ILIKE $1 || '%' OR alias ILIKE $1 || '%' OR name ILIKE '%' || $1 || '%'
        ORDER BY
          match_type, name
        LIMIT $2
        """

        rows = await self.db.fetch_all(sql, [q, limit])
        results = []
        for r in rows:
            rec = dict(r)
            # match_type: 0=name prefix, 1=alias prefix, 2=fuzzy
            mt = rec.pop('match_type', None)
            if mt == 1:
                # alias 命中：显示 alias
                rec['display_name'] = rec.get('alias') or rec.get('name')
            else:
                # name 命中或模糊：显示 name
                rec['display_name'] = rec.get('name')
            results.append(rec)
        return results

# app/utils/sql_formatter.py

import re

def format_sql(query: str, params: list) -> str:
    """
    简单格式化带参数的PostgreSQL SQL语句，把$1,$2...替换成对应的参数值，
    用于调试打印，注意不要用于直接执行防止SQL注入。
    """
    formatted_sql = query
    for i, param in enumerate(params, 1):
        # 检查 $i 是否出现在 ANY($i) 这种上下文
        any_pattern = f"ANY(${i})"
        if isinstance(param, list):
            if any_pattern in formatted_sql:

                def escape_elem(e):
                    if isinstance(e, str):
                        safe_e = e.replace("'", "''")
                        return f"'{safe_e}'"
                    elif e is None:
                        return "NULL"
                    else:
                        return str(e)

                elems = ",".join(escape_elem(e) for e in param)
                replacement = f"ARRAY[{elems}]"
            else:
                # 只取第一个元素或 NULL
                if len(param) == 0:
                    replacement = "NULL"
                else:
                    e = param[0]
                    if isinstance(e, str):
                        safe_e = e.replace("'", "''")
                        replacement = f"'{safe_e}'"
                    elif e is None:
                        replacement = "NULL"
                    else:
                        replacement = str(e)
        elif isinstance(param, str):
            safe_param = param.replace("'", "''")
            replacement = f"'{safe_param}'"
        elif param is None:
            replacement = "NULL"
        else:
            replacement = str(param)

        # 只替换完整的 $i（防止 $1 替换到 $10、$11）
        formatted_sql = re.sub(rf"\${i}(?!\d)", replacement, formatted_sql)

    return formatted_sql

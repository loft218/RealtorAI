from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from app.services.deepseek_client import deepseek_client  # 假设你有此服务

router = APIRouter()


class MarketTrendResponse(BaseModel):
    data: Dict[str, Any]


@router.get("/market-trend", response_model=MarketTrendResponse)
async def get_market_trend():
    prompt = """
请以严格的 JSON 格式返回“截至目前最新的上海二手房市场成交情况”，并包含以下字段：

{
  "截至日期": "YYYY-MM-DD",
  "近期成交": [
    {
      "日期": "YYYY-MM-DD",
      "成交套数": 数字,
      "环比变化": {
        "套数变化": 数字,
        "百分比变化": "±XX.X%"
      },
      "周均套数": 数字,
      "超周均百分比": "±XX.X%"
    }
  ],
  "月度成交": [
    {
      "月份": "YYYY-MM",
      "累计成交套数": 数字,
      "日均套数": 数字,
      "同比变化": "±XX.X%"
    }
  ],
  "市场趋势": {
        "成交量趋势": "字符串",
        "价格走势": "字符串"
      }
    }
    """
    result = await deepseek_client.call(prompt, web_search=True)
    if not result:
        raise HTTPException(status_code=500, detail="查询失败")
    return {"data": result}

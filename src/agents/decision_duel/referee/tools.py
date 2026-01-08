from langchain_core.tools import tool
import requests
import json
import yfinance as yf
from datetime import datetime


@tool(
    "search",
    description="Use it to search for data, statistics, news, or actual historical evidence on the internet to strengthen your decision in the debate.",
)
def search(query: str) -> str:
    """Search on the web for get information that helps you"""

    url = "https://google.serper.dev/search"
    payload = json.dumps(
        {"q": query, "location": "Bogota, Colombia", "gl": "co", "hl": "en"}
    )
    headers = {
        "X-API-KEY": "eb119bd476012142212b51233047635acfa1749d",
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text


@tool(
    "search_yahoo_finance",
    description="Use it to retrieve neutral market data from Yahoo Finance including prices, trends, volume, and company fundamentals without bullish or bearish bias.",
)
def search_yahoo_finance(ticker: str) -> dict:
    """
    Neutral Yahoo Finance search tool.
    Provides descriptive market data with no directional bias.
    """

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")

        if hist.empty:
            return {"error": "No data available", "ticker": ticker}

        current_price = hist["Close"].iloc[-1]
        prev_price = hist["Close"].iloc[-2]
        change_pct = ((current_price - prev_price) / prev_price) * 100

        ma20 = hist["Close"].rolling(20).mean().iloc[-1]
        ma50 = hist["Close"].rolling(50).mean().iloc[-1]
        ma200 = hist["Close"].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None

        volume = hist["Volume"].iloc[-1]
        avg_volume = hist["Volume"].rolling(20).mean().iloc[-1]

        info = stock.info
        market_cap = info.get("marketCap")
        sector = info.get("sector")
        industry = info.get("industry")

        return {
            "ticker": ticker,
            "timestamp": datetime.utcnow().isoformat(),
            "price": round(current_price, 2),
            "daily_change_pct": round(change_pct, 2),
            "moving_averages": {
                "ma20": round(ma20, 2),
                "ma50": round(ma50, 2),
                "ma200": round(ma200, 2) if ma200 else None,
            },
            "volume": {
                "current": int(volume),
                "avg_20d": int(avg_volume),
            },
            "fundamentals": {
                "market_cap": market_cap,
                "sector": sector,
                "industry": industry,
            },
            "note": "Neutral market snapshot. No bullish or bearish interpretation applied.",
        }

    except Exception as e:
        return {"error": str(e), "ticker": ticker}


tools = [search, search_yahoo_finance]

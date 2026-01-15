from langchain_core.tools import tool
import requests
import json
import yfinance as yf
from datetime import datetime
import os


@tool(
    "search",
    description="Use it to search for data, statistics, news, or actual historical evidence on the internet to strengthen your argument in the debate.",
)
def search(query: str) -> str:
    """Search on the web for get information that helps you"""

    url = "https://google.serper.dev/search"
    payload = json.dumps(
        {"q": query, "location": "Bogota, Colombia", "gl": "co", "hl": "en"}
    )
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.text


@tool(
    "get_yahoo_finance_bull_data",
    description="Use it to get data to market prices, historical time series, company fundamentals, financial statements, and trading data for stocks, ETFs, indices, currencies, commodities, and cryptocurrencies.",
)
def get_yahoo_finance_bull_data(ticker: str) -> dict:
    """
    Use it to get data to market prices, historical time series, company fundamentals, financial statements, and trading data for stocks, ETFs, indices, currencies, commodities, and cryptocurrencies.
    """

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")

        if hist.empty:
            return {"error": "No data available", "ticker": ticker}

        current_price = hist["Close"].iloc[-1]
        prev_price = hist["Close"].iloc[-2]
        change_pct = ((current_price - prev_price) / prev_price) * 100

        ma50 = hist["Close"].rolling(50).mean().iloc[-1]
        ma200 = hist["Close"].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None

        volume = hist["Volume"].iloc[-1]
        avg_volume = hist["Volume"].rolling(20).mean().iloc[-1]

        info = stock.info
        market_cap = info.get("marketCap")
        sector = info.get("sector")

        bullish_trend = ma200 is not None and ma50 > ma200
        bullish_momentum = current_price > ma50
        volume_confirmation = volume > avg_volume

        bull_signal = bullish_trend and bullish_momentum and volume_confirmation

        return {
            "ticker": ticker,
            "timestamp": datetime.utcnow().isoformat(),
            "price": round(current_price, 2),
            "change_pct": round(change_pct, 2),
            "ma50": round(ma50, 2),
            "ma200": round(ma200, 2) if ma200 else None,
            "volume": int(volume),
            "avg_volume_20d": int(avg_volume),
            "market_cap": market_cap,
            "sector": sector,
            "signals": {
                "bullish_trend": bullish_trend,
                "bullish_momentum": bullish_momentum,
                "volume_confirmation": volume_confirmation,
                "bull_signal": bull_signal,
            },
        }

    except Exception as e:
        return {"error": str(e), "ticker": ticker}


tools = [search, get_yahoo_finance_bull_data]

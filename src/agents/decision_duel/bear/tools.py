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
    "get_yahoo_finance_bear_data",
    description="Use it to detect bearish signals using market prices, historical time series, company fundamentals, and trading data from Yahoo Finance.",
)
def get_yahoo_finance_bear_data(ticker: str) -> dict:
    """
    Tool for a Bear agent.
    Detects bearish market conditions using Yahoo Finance data.
    """

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")

        if hist.empty:
            return {"error": "No data available", "ticker": ticker}

        # Prices
        current_price = hist["Close"].iloc[-1]
        prev_price = hist["Close"].iloc[-2]
        change_pct = ((current_price - prev_price) / prev_price) * 100

        # Moving averages
        ma50 = hist["Close"].rolling(50).mean().iloc[-1]
        ma200 = hist["Close"].rolling(200).mean().iloc[-1] if len(hist) >= 200 else None

        # Volume
        volume = hist["Volume"].iloc[-1]
        avg_volume = hist["Volume"].rolling(20).mean().iloc[-1]

        # Fundamentals
        info = stock.info
        market_cap = info.get("marketCap")
        sector = info.get("sector")

        # Bear signals
        bearish_trend = ma200 is not None and ma50 < ma200
        bearish_momentum = current_price < ma50
        volume_confirmation = volume > avg_volume

        bear_signal = bearish_trend and bearish_momentum and volume_confirmation

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
                "bearish_trend": bearish_trend,
                "bearish_momentum": bearish_momentum,
                "volume_confirmation": volume_confirmation,
                "bear_signal": bear_signal,
            },
        }

    except Exception as e:
        return {"error": str(e), "ticker": ticker}


tools = [search, get_yahoo_finance_bear_data]

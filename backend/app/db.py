import sqlite3
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import yfinance as yf

DB_PATH = "database.db"


def get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = get_conn()
    _ = conn.execute("""
    CREATE TABLE IF NOT EXISTS stock_metadata (
        ticker TEXT PRIMARY KEY,
        last_modified TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()


def get_stock(ticker: str):
    if ticker not in get_tickers():
        raise ValueError("invalid ticker")
    conn = get_conn()
    # Check last modified time
    cur = conn.execute(
        "SELECT last_modified FROM stock_metadata WHERE ticker = ?", (ticker,)
    )
    row = cur.fetchone()

    if row:
        last_modified = datetime.fromisoformat(row[0])
        if datetime.now() - last_modified < timedelta(days=1):
            # Data is fresh → fetch from DB
            stock_df = pd.read_sql(f"SELECT * FROM '{ticker}'", conn)
            stock_df["Date"] = pd.to_datetime(stock_df["Date"]).dt.strftime("%Y-%m-%d")
            high_52w = stock_df["High"].max()
            low_52w = stock_df["Low"].min()
            conn.close()
            return {
                "data": stock_df.to_dict(orient="records"),
                "52_week_high": high_52w,
                "52_week_low": low_52w,
            }

    # Data stale or missing → download fresh
    stock = yf.download(ticker, period="1y", progress=False)

    if isinstance(stock.columns, pd.MultiIndex):
        stock.columns = [col[0] if col[0] else col[1] for col in stock.columns]

    stock.reset_index(inplace=True)
    high_52w = stock["High"].max()
    low_52w = stock["Low"].min()

    # Store stock data in its own table
    stock.to_sql(ticker, conn, if_exists="replace", index=False)

    # Update metadata
    _ = conn.execute(
        """
        INSERT INTO stock_metadata (ticker, last_modified)
        VALUES (?, ?)
        ON CONFLICT(ticker) DO UPDATE SET last_modified=excluded.last_modified
    """,
        (ticker, datetime.now().isoformat()),
    )

    conn.commit()
    conn.close()

    return get_stock(ticker)


def get_tickers() -> dict[str, dict[str, str]]:
    return {
        "AAPL": {"company": "Apple Inc.", "sector": "Technology"},
        "MSFT": {"company": "Microsoft Corp.", "sector": "Technology"},
        "GOOGL": {
            "company": "Alphabet Inc. (Class A)",
            "sector": "Communication Services",
        },
        "AMZN": {
            "company": "Amazon.com Inc.",
            "sector": "Consumer Discretionary",
        },
        "TSLA": {"company": "Tesla Inc.", "sector": "Consumer Discretionary"},
        "JPM": {"company": "JPMorgan Chase & Co.", "sector": "Financials"},
        "NVDA": {"company": "NVIDIA Corp.", "sector": "Technology"},
        "PEP": {"company": "PepsiCo Inc.", "sector": "Consumer Staples"},
        "XOM": {"company": "Exxon Mobil Corp.", "sector": "Energy"},
        "JNJ": {"company": "Johnson & Johnson", "sector": "Healthcare"},
    }

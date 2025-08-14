from functools import lru_cache
import sqlite3
from datetime import datetime, timedelta

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


@lru_cache(maxsize=128)
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
                "max52": high_52w,
                "min52": low_52w,
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
        # Technology
        "AAPL": {"company": "Apple Inc.", "sector": "Technology"},
        "MSFT": {"company": "Microsoft Corp.", "sector": "Technology"},
        "GOOGL": {
            "company": "Alphabet Inc. (Class A)",
            "sector": "Communication Services",
        },
        "NVDA": {"company": "NVIDIA Corp.", "sector": "Technology"},
        "META": {"company": "Meta Platforms Inc.", "sector": "Communication Services"},
        "CRM": {"company": "Salesforce Inc.", "sector": "Technology"},
        "ORCL": {"company": "Oracle Corp.", "sector": "Technology"},
        "INTC": {"company": "Intel Corp.", "sector": "Technology"},
        "IBM": {
            "company": "International Business Machines Corp.",
            "sector": "Technology",
        },
        "ADBE": {"company": "Adobe Inc.", "sector": "Technology"},
        "NOW": {"company": "ServiceNow Inc.", "sector": "Technology"},
        "SHOP": {"company": "Shopify Inc.", "sector": "Technology"},
        # Consumer Discretionary
        "AMZN": {"company": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
        "TSLA": {"company": "Tesla Inc.", "sector": "Consumer Discretionary"},
        "HD": {"company": "Home Depot Inc.", "sector": "Consumer Discretionary"},
        "NKE": {"company": "Nike Inc.", "sector": "Consumer Discretionary"},
        "SBUX": {"company": "Starbucks Corp.", "sector": "Consumer Discretionary"},
        "DIS": {"company": "Walt Disney Co.", "sector": "Communication Services"},
        "NFLX": {"company": "Netflix Inc.", "sector": "Communication Services"},
        "MCD": {"company": "McDonald's Corp.", "sector": "Consumer Discretionary"},
        "LOW": {"company": "Lowe's Companies Inc.", "sector": "Consumer Discretionary"},
        # Healthcare
        "JNJ": {"company": "Johnson & Johnson", "sector": "Healthcare"},
        "PFE": {"company": "Pfizer Inc.", "sector": "Healthcare"},
        "UNH": {"company": "UnitedHealth Group Inc.", "sector": "Healthcare"},
        "ABT": {"company": "Abbott Laboratories", "sector": "Healthcare"},
        "MRK": {"company": "Merck & Co. Inc.", "sector": "Healthcare"},
        "TMO": {"company": "Thermo Fisher Scientific Inc.", "sector": "Healthcare"},
        "MDT": {"company": "Medtronic PLC", "sector": "Healthcare"},
        "ABBV": {"company": "AbbVie Inc.", "sector": "Healthcare"},
        # Financials
        "JPM": {"company": "JPMorgan Chase & Co.", "sector": "Financials"},
        "BAC": {"company": "Bank of America Corp.", "sector": "Financials"},
        "WFC": {"company": "Wells Fargo & Co.", "sector": "Financials"},
        "GS": {"company": "Goldman Sachs Group Inc.", "sector": "Financials"},
        "MS": {"company": "Morgan Stanley", "sector": "Financials"},
        "C": {"company": "Citigroup Inc.", "sector": "Financials"},
        "AXP": {"company": "American Express Co.", "sector": "Financials"},
        "V": {"company": "Visa Inc.", "sector": "Financials"},
        "MA": {"company": "Mastercard Inc.", "sector": "Financials"},
        "BRK.B": {
            "company": "Berkshire Hathaway Inc. (Class B)",
            "sector": "Financials",
        },
        # Consumer Staples
        "PEP": {"company": "PepsiCo Inc.", "sector": "Consumer Staples"},
        "KO": {"company": "Coca-Cola Co.", "sector": "Consumer Staples"},
        "WMT": {"company": "Walmart Inc.", "sector": "Consumer Staples"},
        "PG": {"company": "Procter & Gamble Co.", "sector": "Consumer Staples"},
        "COST": {"company": "Costco Wholesale Corp.", "sector": "Consumer Staples"},
        "TGT": {"company": "Target Corp.", "sector": "Consumer Discretionary"},
        # Energy
        "XOM": {"company": "Exxon Mobil Corp.", "sector": "Energy"},
        "CVX": {"company": "Chevron Corp.", "sector": "Energy"},
        "COP": {"company": "ConocoPhillips", "sector": "Energy"},
        "EOG": {"company": "EOG Resources Inc.", "sector": "Energy"},
        "SLB": {"company": "Schlumberger NV", "sector": "Energy"},
        # Industrial
        "BA": {"company": "Boeing Co.", "sector": "Industrials"},
        "CAT": {"company": "Caterpillar Inc.", "sector": "Industrials"},
        "GE": {"company": "General Electric Co.", "sector": "Industrials"},
        "MMM": {"company": "3M Co.", "sector": "Industrials"},
        "HON": {"company": "Honeywell International Inc.", "sector": "Industrials"},
        "UPS": {"company": "United Parcel Service Inc.", "sector": "Industrials"},
        "RTX": {"company": "Raytheon Technologies Corp.", "sector": "Industrials"},
        # Real Estate
        "AMT": {"company": "American Tower Corp.", "sector": "Real Estate"},
        "PLD": {"company": "Prologis Inc.", "sector": "Real Estate"},
        "CCI": {"company": "Crown Castle Inc.", "sector": "Real Estate"},
        # Materials
        "LIN": {"company": "Linde PLC", "sector": "Materials"},
        "APD": {"company": "Air Products and Chemicals Inc.", "sector": "Materials"},
        "SHW": {"company": "Sherwin-Williams Co.", "sector": "Materials"},
        # Utilities
        "NEE": {"company": "NextEra Energy Inc.", "sector": "Utilities"},
        "DUK": {"company": "Duke Energy Corp.", "sector": "Utilities"},
        "SO": {"company": "Southern Co.", "sector": "Utilities"},
        # Communication Services
        "T": {"company": "AT&T Inc.", "sector": "Communication Services"},
        "VZ": {
            "company": "Verizon Communications Inc.",
            "sector": "Communication Services",
        },
        "CMCSA": {"company": "Comcast Corp.", "sector": "Communication Services"},
    }

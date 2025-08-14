from functools import lru_cache
from sklearn.linear_model import LinearRegression
import numpy as np
from app import db
import pandas as pd


@lru_cache(maxsize=128)
def predict(ticker: str):
    conn = db.get_conn()
    stock = pd.read_sql_query(f"SELECT Date, Close FROM '{ticker}'", conn)
    conn.close()
    X = np.array(range(len(stock))).reshape(-1, 1)
    y = stock["Close"].values  # All closing prices

    model = LinearRegression()
    model.fit(X, y)

    future_days = np.array([[len(stock) + i] for i in range(7)])  # Next 7 days
    predictions = model.predict(future_days)

    # Return predictions with dates (approximate future dates)
    last_date = pd.to_datetime(stock["Date"].iloc[-1])
    future_dates = [
        (last_date + pd.Timedelta(days=i + 1)).strftime("%Y-%m-%d") for i in range(7)
    ]
    result = [
        {"date": date, "predicted_price": float(price)}
        for date, price in zip(future_dates, predictions)
    ]

    return result

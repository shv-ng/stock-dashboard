from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()


@app.get("/api/list")
def get_companies():
    return db.get_tickers()


@app.get("/api/history/{ticker}")
def get_stock(ticker: str):
    if ticker not in db.get_tickers():
        raise HTTPException(status_code=400, detail="invalid ticker")
    return db.get_stock(ticker)

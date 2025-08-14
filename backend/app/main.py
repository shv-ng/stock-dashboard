from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app import db
from app import predict

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()


# list out all the tickers company name and sector
@app.get("/api/list")
@limiter.limit("60/minute")
def get_companies(request: Request, response: Response):
    return db.get_tickers()


# get stock of last 1y of given ticker
@app.get("/api/history/{ticker}")
@limiter.limit("250/minute")
def get_stock(request: Request, response: Response, ticker: str):
    if ticker not in db.get_tickers():
        raise HTTPException(status_code=400, detail="invalid ticker")
    return db.get_stock(ticker)


@app.get("/api/predict/{ticker}")
@limiter.limit("250/minute")
def predict_stocks(request: Request, response: Response, ticker: str):
    try:
        result = predict.predict(ticker)
        return {"ticker": ticker, "predictions": result}
    except Exception:
        raise HTTPException(status_code=404, detail=f"No data for {ticker} in database")

"""yfinance를 이용한 가격 데이터 수집 및 캐싱."""
import os

import pandas as pd
import yfinance as yf

from src.config import BENCHMARK, DATA_DIR_PROCESSED, DATA_DIR_RAW, END_DATE, START_DATE, TICKERS


def download_prices(tickers=None, start=START_DATE, end=END_DATE, use_cache=True):
    """종가(Adj Close) 데이터를 내려받는다. 캐시가 있으면 재사용한다."""
    tickers = tickers or TICKERS
    cache_path = os.path.join(DATA_DIR_RAW, "prices.csv")

    if use_cache and os.path.exists(cache_path):
        prices = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        if set(tickers).issubset(prices.columns):
            return prices[tickers]

    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    prices = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]].rename(
        columns={"Close": tickers[0]}
    )
    prices = prices.dropna(how="all")

    os.makedirs(DATA_DIR_RAW, exist_ok=True)
    prices.to_csv(cache_path)
    return prices


def download_benchmark(benchmark=BENCHMARK, start=START_DATE, end=END_DATE, use_cache=True):
    """벤치마크(기본 SPY) 가격 데이터를 내려받는다."""
    cache_path = os.path.join(DATA_DIR_RAW, f"benchmark_{benchmark}.csv")

    if use_cache and os.path.exists(cache_path):
        return pd.read_csv(cache_path, index_col=0, parse_dates=True)[benchmark]

    raw = yf.download(benchmark, start=start, end=end, auto_adjust=True, progress=False)
    close = raw["Close"]
    series = close[benchmark] if isinstance(close, pd.DataFrame) else close.rename(benchmark)
    series = series.rename(benchmark)

    os.makedirs(DATA_DIR_RAW, exist_ok=True)
    series.to_csv(cache_path)
    return series


def compute_daily_returns(prices, save=True):
    """일별 수익률을 계산하고 processed 폴더에 저장한다."""
    returns = prices.pct_change().dropna(how="all")
    if save:
        os.makedirs(DATA_DIR_PROCESSED, exist_ok=True)
        returns.to_csv(os.path.join(DATA_DIR_PROCESSED, "daily_returns.csv"))
    return returns

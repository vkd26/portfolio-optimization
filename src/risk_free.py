"""시장별 무위험수익률(risk-free rate) 결정.

미국 종목이면 yfinance의 13주 미국채(^IRX) 수익률을 자동으로 가져온다.
한국(.KS/.KQ 등) 등 그 외 시장은 yfinance에 신뢰할 만한 국채수익률 데이터가 없어
자동 조회를 지원하지 않고, config.py에 지정된 수동값(RISK_FREE_RATE)을 그대로 사용한다.
"""
import pandas as pd
import yfinance as yf

from src.config import RISK_FREE_RATE, RISK_FREE_RATE_MODE

US_TBILL_TICKER = "^IRX"  # 13-week Treasury Bill yield (%, 연율)


def _is_korean_ticker(ticker):
    return ticker.upper().endswith((".KS", ".KQ"))


def detect_market(tickers):
    """티커 형식으로 시장을 추정한다 (완벽하지 않은 휴리스틱)."""
    if all(_is_korean_ticker(t) for t in tickers):
        return "KR"
    if any(_is_korean_ticker(t) for t in tickers):
        return "MIXED"
    return "US"


def fetch_us_risk_free_rate(start, end, ticker=US_TBILL_TICKER):
    """13주 미국채 수익률(%)의 기간 평균을 소수(예: 0.045)로 반환."""
    data = yf.download(ticker, start=start, end=end, progress=False)
    close = data["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.mean() / 100


def get_risk_free_rate(tickers, start, end, mode=RISK_FREE_RATE_MODE, manual_rate=RISK_FREE_RATE):
    """시장에 맞는 무위험수익률을 결정한다.

    - mode="manual": 시장과 무관하게 manual_rate를 그대로 사용
    - mode="auto" + 미국 종목: ^IRX 13주 국채수익률 기간평균을 자동 조회
    - mode="auto" + 그 외 시장: 자동 조회를 지원하지 않으므로 manual_rate로 대체하고 안내 출력
    """
    if mode == "manual":
        return manual_rate

    market = detect_market(tickers)

    if market == "US":
        try:
            return fetch_us_risk_free_rate(start, end)
        except Exception as e:
            print(f"[경고] 미국채(^IRX) 수익률 자동 조회 실패({e}). manual_rate={manual_rate:.2%} 사용.")
            return manual_rate

    print(
        f"[안내] '{market}' 시장은 yfinance로 국채수익률을 자동 조회할 수 없어 "
        f"config.py의 RISK_FREE_RATE(={manual_rate:.2%})를 사용합니다. "
        "한국 국채수익률은 한국은행 ECOS(https://ecos.bok.or.kr) 등에서 확인 후 "
        "config.py의 RISK_FREE_RATE 값을 직접 갱신하세요."
    )
    return manual_rate

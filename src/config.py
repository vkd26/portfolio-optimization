"""프로젝트 전역 설정. 종목/기간을 바꾸고 싶으면 이 파일만 수정하면 된다."""
import os
from datetime import date, timedelta

# notebooks/에서 실행하든 프로젝트 루트에서 실행하든 항상 같은 data/ 폴더를 가리키도록 절대경로로 고정
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 섹터별로 분산된 미국 대형주 10종목 (자유롭게 교체 가능)
TICKERS = ["GOOGL",  # Technology (AAPL → Alphabet)
"ORCL",   # Technology (MSFT → Oracle)
"AMD",    # Semiconductors (NVDA → AMD)
"BAC",    # Financials (JPM → Bank of America)
"MA",     # Financials / Payments (V → Mastercard)
"PFE",    # Healthcare (JNJ → Pfizer)
"ABBV",   # Healthcare (UNH → AbbVie)
"CVX",    # Energy (XOM → Chevron)
"KO",     # Consumer Staples (PG → Coca-Cola)
"LOW",    # Consumer Discretionary (HD → Lowe's)
]

# 성과 비교용 벤치마크
BENCHMARK = "SPY"

# 무위험수익률(risk-free rate) 결정 방식
#   "auto"   -> src.risk_free.get_risk_free_rate()가 시장을 자동판별해서 결정
#               (미국 종목: yfinance ^IRX 13주 국채수익률 자동 조회 / 그 외 시장: 아래 수동값 사용)
#   "manual" -> 시장과 상관없이 항상 아래 RISK_FREE_RATE 값을 그대로 사용
RISK_FREE_RATE_MODE = "auto"

# manual 모드일 때, 혹은 auto 모드인데 자동 조회가 불가능한 시장(예: 한국 등)일 때 사용하는 값.
# 한국 국채수익률은 한국은행 ECOS(https://ecos.bok.or.kr)에서 확인 후 직접 갱신하면 된다.
RISK_FREE_RATE = 0.04  # 연 4% 가정 (미국 단기 국채 수준)

END_DATE = date.today()
START_DATE = END_DATE - timedelta(days=365 * 5)

TRADING_DAYS_PER_YEAR = 252

DATA_DIR_RAW = os.path.join(PROJECT_ROOT, "data", "raw")
DATA_DIR_PROCESSED = os.path.join(PROJECT_ROOT, "data", "processed")

# Portfolio Optimization

미국 주식 10종목을 대상으로 현대 포트폴리오 이론(MPT) 기반 자산배분을 수행하는 프로젝트다.

## 주요 내용

- **데이터 수집**: `yfinance`로 10개 종목 + 벤치마크(SPY)의 최근 5년 일별 종가 수집
- **포트폴리오 최적화**: 효율적 프론티어(Efficient Frontier) 계산, 샤프비율 최대화(Max Sharpe) / 최소분산(Min Volatility) 포트폴리오 도출 (`scipy.optimize`)
- **성과 비교**: 최적 포트폴리오 vs S&P 500 벤치마크의 CAGR, 변동성, 샤프비율, 최대낙폭(MDD) 비교
- **무위험수익률 자동 설정**: 미국 종목은 yfinance `^IRX`(13주 국채) 수익률을 자동 조회하고, 그 외 시장(예: 한국)은 `src/config.py`의 수동값을 사용

## 대상 종목

섹터 분산을 위해 아래 10개 대형주로 구성했다 (`src/config.py`에서 자유롭게 변경 가능):

| 종목 | 섹터 |
|---|---|
| AAPL, MSFT, NVDA | Technology |
| JPM, V | Financials |
| JNJ, UNH | Healthcare |
| XOM | Energy |
| PG | Consumer Staples |
| HD | Consumer Discretionary |

벤치마크: **SPY** (S&P 500 ETF) · 분석 기간: 최근 5년

## 무위험수익률(risk-free rate) 설정

`src/config.py`의 `RISK_FREE_RATE_MODE`로 결정 방식을 바꿀 수 있다.

- `"auto"` (기본값): 종목 티커로 시장을 판별해 미국 종목이면 `^IRX` 13주 국채수익률을 자동 조회, 그 외 시장(`.KS`/`.KQ` 등)은 자동 조회를 지원하지 않아 아래 수동값으로 대체
- `"manual"`: 시장과 무관하게 `RISK_FREE_RATE` 값을 그대로 사용

한국 국채수익률처럼 yfinance로 못 가져오는 값은 한국은행 ECOS(https://ecos.bok.or.kr) 등에서 직접 확인해 `RISK_FREE_RATE`를 갱신하면 된다.

## 폴더 구조

```
portfolio-optimization/
├── data/
│   ├── raw/                # yfinance 원본 캐시 (git 미포함, 최초 실행 시 자동 생성)
│   └── processed/          # 가공된 수익률 데이터
├── notebooks/
│   └── 01_portfolio_optimization.ipynb   # 메인 분석 노트북
├── src/
│   ├── config.py           # 종목/기간/벤치마크/무위험수익률 설정
│   ├── data_loader.py      # yfinance 데이터 수집 및 캐싱
│   ├── portfolio.py         # 효율적 프론티어, 샤프비율/최소분산 최적화
│   ├── risk_free.py        # 시장별 무위험수익률 자동 판별/조회
│   └── metrics.py          # CAGR, 변동성, 샤프비율, MDD 등 성과 지표
├── tests/
│   └── test_portfolio.py   # 합성 데이터 기반 단위 테스트 (네트워크 미사용)
├── requirements.txt
└── pytest.ini
```

## 실행 방법

```bash
pip install -r requirements.txt
jupyter notebook notebooks/01_portfolio_optimization.ipynb
```

단위 테스트 실행:

```bash
pytest
```

## 한계 및 향후 개선 방향

- 최적화가 과거 데이터 기반 in-sample 결과라 실전에서는 walk-forward 방식의 리밸런싱 검증이 필요하다.
- 거래비용, 슬리피지, 세금이 반영되지 않았다.
- 공매도 없이 개별 비중 0~100% 제약을 두어 롱온리 펀드 운용에 가까운 가정을 사용했다.
- 시장 판별은 티커 형식(`.KS`/`.KQ` 접미사 유무) 기반의 단순 휴리스틱이라 완벽하지 않다.

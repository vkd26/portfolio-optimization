"""수익률 시계열에서 성과 지표를 계산하는 함수들."""
import numpy as np

from src.config import RISK_FREE_RATE, TRADING_DAYS_PER_YEAR


def cagr(returns, periods_per_year=TRADING_DAYS_PER_YEAR):
    """연평균 복리 성장률."""
    cumulative = (1 + returns).prod()
    n_years = len(returns) / periods_per_year
    return cumulative ** (1 / n_years) - 1


def annual_volatility(returns, periods_per_year=TRADING_DAYS_PER_YEAR):
    return returns.std() * np.sqrt(periods_per_year)


def sharpe_ratio(returns, risk_free_rate=RISK_FREE_RATE, periods_per_year=TRADING_DAYS_PER_YEAR):
    excess_return = cagr(returns, periods_per_year) - risk_free_rate
    vol = annual_volatility(returns, periods_per_year)
    return excess_return / vol if vol != 0 else np.nan


def max_drawdown(returns):
    """누적 수익률 곡선 기준 최대 낙폭 (음수로 반환)."""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = cumulative / running_max - 1
    return drawdown.min()


def performance_summary(returns, risk_free_rate=RISK_FREE_RATE):
    """리포트용 성과 지표 dict."""
    return {
        "CAGR": cagr(returns),
        "Volatility": annual_volatility(returns),
        "Sharpe": sharpe_ratio(returns, risk_free_rate),
        "MaxDrawdown": max_drawdown(returns),
    }

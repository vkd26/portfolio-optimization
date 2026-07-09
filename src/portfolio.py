"""현대 포트폴리오 이론(MPT) 기반 효율적 프론티어 및 샤프비율 최적화."""
import numpy as np
import pandas as pd
from scipy.optimize import minimize

from src.config import RISK_FREE_RATE, TRADING_DAYS_PER_YEAR


def annualize_returns(daily_returns, periods_per_year=TRADING_DAYS_PER_YEAR):
    return daily_returns.mean() * periods_per_year


def annualize_cov(daily_returns, periods_per_year=TRADING_DAYS_PER_YEAR):
    return daily_returns.cov() * periods_per_year


def portfolio_performance(weights, mean_returns, cov_matrix, risk_free_rate=RISK_FREE_RATE):
    """주어진 비중의 연 기대수익률, 변동성, 샤프비율을 계산."""
    weights = np.array(weights)
    ret = np.dot(weights, mean_returns)
    vol = np.sqrt(weights @ cov_matrix @ weights)
    sharpe = (ret - risk_free_rate) / vol if vol != 0 else np.nan
    return ret, vol, sharpe


def _negative_sharpe(weights, mean_returns, cov_matrix, risk_free_rate):
    _, _, sharpe = portfolio_performance(weights, mean_returns, cov_matrix, risk_free_rate)
    return -sharpe


def _portfolio_volatility(weights, mean_returns, cov_matrix):
    _, vol, _ = portfolio_performance(weights, mean_returns, cov_matrix)
    return vol


def _default_bounds_constraints(n_assets):
    bounds = tuple((0.0, 1.0) for _ in range(n_assets))  # 공매도 없음, 개별 비중 0~100%
    constraints = ({"type": "eq", "fun": lambda w: np.sum(w) - 1},)
    init_guess = np.repeat(1 / n_assets, n_assets)
    return bounds, constraints, init_guess


def max_sharpe_portfolio(mean_returns, cov_matrix, risk_free_rate=RISK_FREE_RATE):
    """샤프비율을 최대화하는 비중을 탐색."""
    n_assets = len(mean_returns)
    bounds, constraints, init_guess = _default_bounds_constraints(n_assets)

    result = minimize(
        _negative_sharpe,
        init_guess,
        args=(mean_returns, cov_matrix, risk_free_rate),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )
    return result.x


def min_volatility_portfolio(mean_returns, cov_matrix):
    """변동성을 최소화하는 비중을 탐색."""
    n_assets = len(mean_returns)
    bounds, constraints, init_guess = _default_bounds_constraints(n_assets)

    result = minimize(
        _portfolio_volatility,
        init_guess,
        args=(mean_returns, cov_matrix),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )
    return result.x


def efficient_frontier(mean_returns, cov_matrix, n_points=50):
    """목표 수익률 구간을 스캔하며 각 수익률에서 변동성을 최소화한 프론티어를 계산."""
    n_assets = len(mean_returns)
    bounds = tuple((0.0, 1.0) for _ in range(n_assets))

    target_returns = np.linspace(mean_returns.min(), mean_returns.max(), n_points)
    frontier_vol = []

    for target in target_returns:
        constraints = (
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
            {"type": "eq", "fun": lambda w, target=target: portfolio_performance(w, mean_returns, cov_matrix)[0] - target},
        )
        init_guess = np.repeat(1 / n_assets, n_assets)
        result = minimize(
            _portfolio_volatility,
            init_guess,
            args=(mean_returns, cov_matrix),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )
        frontier_vol.append(result.fun if result.success else np.nan)

    return pd.DataFrame({"Return": target_returns, "Volatility": frontier_vol})


def random_portfolios(mean_returns, cov_matrix, n_portfolios=5000, risk_free_rate=RISK_FREE_RATE, seed=42):
    """효율적 프론티어 배경에 뿌릴 무작위 포트폴리오 샘플 (시각화용)."""
    rng = np.random.default_rng(seed)
    n_assets = len(mean_returns)

    records = []
    for _ in range(n_portfolios):
        weights = rng.random(n_assets)
        weights /= weights.sum()
        ret, vol, sharpe = portfolio_performance(weights, mean_returns, cov_matrix, risk_free_rate)
        records.append({"Return": ret, "Volatility": vol, "Sharpe": sharpe})

    return pd.DataFrame(records)

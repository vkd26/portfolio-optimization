"""합성(synthetic) 데이터로 핵심 로직을 검증하는 간단한 sanity test. 네트워크 접근 없음."""
import numpy as np
import pandas as pd
import pytest

from src.metrics import cagr, max_drawdown, performance_summary, sharpe_ratio
from src.portfolio import (
    efficient_frontier,
    max_sharpe_portfolio,
    min_volatility_portfolio,
    portfolio_performance,
)


@pytest.fixture
def synthetic_returns():
    rng = np.random.default_rng(0)
    dates = pd.bdate_range("2021-01-01", periods=500)
    n_assets = 4
    data = rng.normal(loc=0.0006, scale=0.012, size=(len(dates), n_assets))
    return pd.DataFrame(data, index=dates, columns=[f"A{i}" for i in range(n_assets)])


def test_max_sharpe_weights_sum_to_one(synthetic_returns):
    mean_returns = synthetic_returns.mean() * 252
    cov_matrix = synthetic_returns.cov() * 252

    weights = max_sharpe_portfolio(mean_returns, cov_matrix)

    assert weights.shape == (4,)
    assert np.isclose(weights.sum(), 1, atol=1e-4)
    assert (weights >= -1e-6).all()


def test_min_vol_has_lower_or_equal_volatility_than_max_sharpe(synthetic_returns):
    mean_returns = synthetic_returns.mean() * 252
    cov_matrix = synthetic_returns.cov() * 252

    sharpe_weights = max_sharpe_portfolio(mean_returns, cov_matrix)
    min_vol_weights = min_volatility_portfolio(mean_returns, cov_matrix)

    _, sharpe_vol, _ = portfolio_performance(sharpe_weights, mean_returns, cov_matrix)
    _, min_vol, _ = portfolio_performance(min_vol_weights, mean_returns, cov_matrix)

    assert min_vol <= sharpe_vol + 1e-6


def test_efficient_frontier_shape(synthetic_returns):
    mean_returns = synthetic_returns.mean() * 252
    cov_matrix = synthetic_returns.cov() * 252

    frontier = efficient_frontier(mean_returns, cov_matrix, n_points=10)

    assert len(frontier) == 10
    assert set(frontier.columns) == {"Return", "Volatility"}


def test_metrics_on_known_series():
    # 매일 정확히 0.1%씩 상승하는 시계열 -> 변동성 0, 낙폭 없음
    returns = pd.Series([0.001] * 252)

    assert cagr(returns) == pytest.approx((1.001**252) - 1)
    assert max_drawdown(returns) == pytest.approx(0, abs=1e-9)
    assert np.isnan(sharpe_ratio(returns * 0))  # 변동성이 0이면 정의되지 않음

    summary = performance_summary(returns)
    assert set(summary.keys()) == {"CAGR", "Volatility", "Sharpe", "MaxDrawdown"}

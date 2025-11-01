"""
Tests para el módulo de simulación.
"""

import pytest
import numpy as np
import pandas as pd
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import generate_monthly_returns, simulate_portfolio_path
from src.rebalance_strategies import TimeBasedRebalance, ThresholdBasedRebalance


def test_generate_monthly_returns():
    """Test de generación de retornos mensuales."""
    asset_stats = {
        'stocks': {'mean_return': 0.10, 'std_dev': 0.15},
        'bonds': {'mean_return': 0.05, 'std_dev': 0.08}
    }
    
    returns = generate_monthly_returns(asset_stats, n_months=12, random_seed=42)
    
    assert isinstance(returns, pd.DataFrame)
    assert len(returns) == 12
    assert 'stocks' in returns.columns
    assert 'bonds' in returns.columns


def test_time_based_rebalance():
    """Test de estrategia de rebalanceo basada en tiempo."""
    target_allocation = {'stocks': 0.6, 'bonds': 0.4}
    strategy = TimeBasedRebalance(target_allocation, frequency='annual')
    
    from datetime import datetime
    current_date = datetime(2025, 1, 1)
    
    # Primera vez debe rebalancear
    should_rebal = strategy.should_rebalance(
        {'stocks': 0.6, 'bonds': 0.4},
        current_date,
        100000
    )
    assert should_rebal == True


def test_threshold_based_rebalance():
    """Test de estrategia de rebalanceo basada en umbral."""
    target_allocation = {'stocks': 0.6, 'bonds': 0.4}
    strategy = ThresholdBasedRebalance(target_allocation, threshold=0.05)
    
    from datetime import datetime
    current_date = datetime(2025, 1, 1)
    
    # Desviación mayor al umbral debe rebalancear
    should_rebal = strategy.should_rebalance(
        {'stocks': 0.72, 'bonds': 0.28},  # 12% de desviación
        current_date,
        100000
    )
    assert should_rebal == True
    
    # Desviación menor al umbral no debe rebalancear
    should_rebal = strategy.should_rebalance(
        {'stocks': 0.62, 'bonds': 0.38},  # 2% de desviación
        current_date,
        100000
    )
    assert should_rebal == False


def test_rebalance_cost():
    """Test de cálculo de costo de rebalanceo."""
    target_allocation = {'stocks': 0.6, 'bonds': 0.4}
    strategy = TimeBasedRebalance(target_allocation, transaction_cost=0.002)
    
    current_values = {'stocks': 70000, 'bonds': 30000}
    portfolio_value = 100000
    
    new_values, cost = strategy.rebalance(current_values, portfolio_value)
    
    assert cost > 0
    assert sum(new_values.values()) <= portfolio_value
    assert abs(new_values['stocks'] / portfolio_value - 0.6) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



"""
Tests específicos para estrategias de rebalanceo.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.rebalance_strategies import (
    TimeBasedRebalance,
    ThresholdBasedRebalance,
    create_rebalance_strategy
)


def test_time_rebalance_frequency():
    """Test de diferentes frecuencias de rebalanceo."""
    target_allocation = {'stocks': 0.6, 'bonds': 0.4}
    
    # Test mensual
    strategy_monthly = TimeBasedRebalance(target_allocation, frequency='monthly')
    date1 = datetime(2025, 1, 1)
    date2 = datetime(2025, 2, 1)
    
    strategy_monthly.should_rebalance({'stocks': 0.6, 'bonds': 0.4}, date1, 100000)
    should_rebal = strategy_monthly.should_rebalance({'stocks': 0.6, 'bonds': 0.4}, date2, 100000)
    
    # Después de 30 días, debería rebalancear si es mensual
    assert should_rebal == True


def test_threshold_calculation():
    """Test de cálculo correcto de umbral."""
    target_allocation = {'stocks': 0.6, 'bonds': 0.4}
    strategy = ThresholdBasedRebalance(target_allocation, threshold=0.05)
    
    # Caso límite: exactamente en el umbral
    current_allocation = {'stocks': 0.65, 'bonds': 0.35}  # 5% de desviación
    should_rebal = strategy.should_rebalance(
        current_allocation,
        datetime(2025, 1, 1),
        100000
    )
    assert should_rebal == True


def test_create_rebalance_strategy():
    """Test de factory function."""
    portfolio_config = {
        'allocation': {'stocks': 0.6, 'bonds': 0.4},
        'rebalance': {'type': 'time', 'frequency': 'annual'}
    }
    
    strategy = create_rebalance_strategy(portfolio_config)
    assert isinstance(strategy, TimeBasedRebalance)
    
    # Test threshold
    portfolio_config_threshold = {
        'allocation': {'stocks': 0.6, 'bonds': 0.4},
        'rebalance': {'type': 'threshold', 'threshold': 0.05}
    }
    
    strategy_threshold = create_rebalance_strategy(portfolio_config_threshold)
    assert isinstance(strategy_threshold, ThresholdBasedRebalance)


def test_rebalance_values_sum():
    """Test de que los valores rebalanceados sumen correctamente."""
    target_allocation = {'stocks': 0.6, 'bonds': 0.4}
    strategy = TimeBasedRebalance(target_allocation, transaction_cost=0.002)
    
    current_values = {'stocks': 70000, 'bonds': 30000}
    portfolio_value = 100000
    
    new_values, cost = strategy.rebalance(current_values, portfolio_value)
    
    # La suma de nuevos valores más el costo debe ser aproximadamente igual al valor original
    total_after_rebalance = sum(new_values.values()) + cost
    assert abs(total_after_rebalance - portfolio_value) < 1  # Permitir pequeñas diferencias por redondeo


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



"""
Tests de integridad de datos.
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_preprocessing import calculate_returns, calculate_statistics


def test_calculate_returns():
    """Test de cálculo de retornos."""
    prices_dict = {
        'stocks': pd.Series([100, 105, 110, 108, 115]),
        'bonds': pd.Series([50, 51, 52, 51.5, 53])
    }
    
    returns = calculate_returns(prices_dict)
    
    assert 'stocks' in returns
    assert 'bonds' in returns
    assert len(returns['stocks']) == len(prices_dict['stocks']) - 1
    assert not returns['stocks'].isna().any()


def test_calculate_statistics():
    """Test de cálculo de estadísticas."""
    # Crear retornos simulados
    np.random.seed(42)
    returns_dict = {
        'stocks': pd.Series(np.random.normal(0.0005, 0.02, 252)),
        'bonds': pd.Series(np.random.normal(0.0002, 0.01, 252))
    }
    
    stats = calculate_statistics(returns_dict)
    
    assert isinstance(stats, pd.DataFrame)
    assert 'asset' in stats.columns
    assert 'mean_return_annual' in stats.columns
    assert 'std_dev_annual' in stats.columns
    assert len(stats) == 2


def test_statistics_values():
    """Test de valores razonables en estadísticas."""
    np.random.seed(42)
    returns_dict = {
        'stocks': pd.Series(np.random.normal(0.0005, 0.02, 252))
    }
    
    stats = calculate_statistics(returns_dict)
    
    # El Sharpe ratio debería ser razonable (no infinito ni NaN)
    sharpe = stats.loc[0, 'sharpe_ratio']
    assert not np.isnan(sharpe)
    assert not np.isinf(sharpe)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



"""
Módulo para simulación Monte Carlo de carteras de inversión.
"""

import numpy as np
import pandas as pd
import yaml
import os
from datetime import datetime, timedelta
from pathlib import Path
try:
    from .rebalance_strategies import create_rebalance_strategy
except ImportError:
    from rebalance_strategies import create_rebalance_strategy


def load_config(config_path="config/settings.yaml"):
    """Carga la configuración desde el archivo YAML."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def load_asset_statistics(processed_path="data/processed/"):
    """
    Carga las estadísticas de activos desde el archivo CSV.
    
    Returns:
        dict: Diccionario con media y std dev por activo
    """
    stats_path = os.path.join(processed_path, "asset_statistics.csv")
    
    if not os.path.exists(stats_path):
        raise FileNotFoundError(
            f"Archivo de estadísticas no encontrado: {stats_path}\n"
            "Ejecuta primero: python src/data_preprocessing.py"
        )
    
    stats_df = pd.read_csv(stats_path)
    
    # Convertir a diccionario
    stats = {}
    for _, row in stats_df.iterrows():
        stats[row['asset']] = {
            'mean_return': row['mean_return_annual'],
            'std_dev': row['std_dev_annual']
        }
    
    return stats


def generate_monthly_returns(asset_stats, n_months, random_seed=None):
    """
    Genera retornos mensuales simulados usando distribución normal.
    
    Args:
        asset_stats: dict con estadísticas anualizadas por activo
        n_months: número de meses a simular
        random_seed: semilla para reproducibilidad
        
    Returns:
        dict: retornos mensuales por activo (DataFrame con n_months filas)
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    # Convertir estadísticas anuales a mensuales
    monthly_returns = {}
    
    for asset in asset_stats.keys():
        # Para cash, usar tasa libre de riesgo baja (ej: 2% anual)
        if asset == 'cash':
            # Tasa libre de riesgo conservadora: 2% anual
            mean_annual = 0.02
            std_annual = 0.001  # Muy baja volatilidad
        else:
            stats = asset_stats[asset]
            mean_annual = stats['mean_return']
            std_annual = stats['std_dev']
        
        # Anualizar: dividir media por 12, std por sqrt(12)
        mean_monthly = mean_annual / 12
        std_monthly = std_annual / np.sqrt(12)
        
        # Generar retornos logarítmicos mensuales
        log_returns = np.random.normal(mean_monthly, std_monthly, n_months)
        monthly_returns[asset] = log_returns
    
    return pd.DataFrame(monthly_returns)


def simulate_portfolio_path(
    initial_capital,
    asset_stats,
    portfolio_config,
    rebalance_strategy,
    monthly_returns,
    withdrawal_amount,
    inflation_rate=0.02,
    apply_inflation=True,
    periodic_contribution=0,
    contribution_enabled=False,
    thirteenth_payment_months=None,
    thirteenth_payment_amount=0,
    thirteenth_payment_enabled=False
):
    """
    Simula un único camino de evolución de la cartera.
    
    Args:
        initial_capital: capital inicial
        asset_stats: estadísticas de activos
        portfolio_config: configuración de la cartera
        rebalance_strategy: estrategia de rebalanceo
        monthly_returns: DataFrame con retornos mensuales simulados
        withdrawal_amount: monto de retiro mensual
        inflation_rate: tasa de inflación anual
        apply_inflation: si ajustar retiros por inflación
        periodic_contribution: monto de contribución periódica (positivo para aportes, negativo para impuestos)
        contribution_enabled: si las contribuciones están habilitadas
        thirteenth_payment_months: lista de meses (1-indexed) donde se aplican décimos sueldos
        thirteenth_payment_amount: monto del décimo sueldo
        thirteenth_payment_enabled: si los décimos sueldos están habilitados
        
    Returns:
        pd.DataFrame: evolución del portafolio por mes
        dict: métricas finales
    """
    n_months = len(monthly_returns)
    allocation = portfolio_config['allocation']
    
    # Inicializar cartera
    portfolio_value = initial_capital
    asset_values = {
        asset: portfolio_value * weight
        for asset, weight in allocation.items()
    }
    
    # Preparar historial
    history = []
    withdrawal = withdrawal_amount
    total_withdrawals = 0
    total_contributions = 0
    total_rebalance_costs = 0
    months_survived = n_months
    
    # Normalizar thirteenth_payment_months (convertir a 0-indexed)
    if thirteenth_payment_months is None:
        thirteenth_payment_months = []
    thirteenth_payment_months_0indexed = [m - 1 for m in thirteenth_payment_months]
    
    # Fecha inicial (para el rebalanceo basado en tiempo)
    current_date = datetime(2025, 1, 1)
    
    for month in range(n_months):
        # Ajustar retiro por inflación si aplica
        if apply_inflation and month > 0:
            monthly_inflation = (1 + inflation_rate) ** (1/12) - 1
            withdrawal = withdrawal * (1 + monthly_inflation)
        
        # Calcular retornos del mes
        month_returns = monthly_returns.iloc[month]
        
        # Actualizar valores de activos con retornos
        new_asset_values = {}
        for asset in asset_values:
            if asset in month_returns.index:
                monthly_return = month_returns[asset]
                new_asset_values[asset] = asset_values[asset] * np.exp(monthly_return)
            else:
                # Si no hay retorno, mantener valor (no debería pasar)
                new_asset_values[asset] = asset_values[asset]
        
        # Calcular nuevo valor total
        portfolio_value = sum(new_asset_values.values())
        
        # Aplicar contribución periódica (después de retornos, antes de retiros)
        contribution_this_month = 0
        if contribution_enabled:
            contribution_this_month = periodic_contribution
            if contribution_this_month != 0:
                portfolio_value += contribution_this_month
                total_contributions += contribution_this_month
                # Distribuir la contribución según la asignación actual
                if portfolio_value > 0:
                    for asset in new_asset_values:
                        new_asset_values[asset] = (new_asset_values[asset] / 
                                                  (portfolio_value - contribution_this_month) * 
                                                  portfolio_value)
        
        # Determinar retiro total del mes
        monthly_withdrawal = withdrawal
        
        # Agregar décimo sueldo si aplica en este mes
        if thirteenth_payment_enabled and month in thirteenth_payment_months_0indexed:
            thirteenth_amount = thirteenth_payment_amount
            # Ajustar décimo sueldo por inflación si aplica
            if apply_inflation and month > 0:
                monthly_inflation = (1 + inflation_rate) ** (1/12) - 1
                thirteenth_amount = thirteenth_payment_amount * ((1 + inflation_rate) ** ((month + 1) / 12))
            monthly_withdrawal += thirteenth_amount
        
        # Realizar retiro
        if portfolio_value >= monthly_withdrawal:
            portfolio_value -= monthly_withdrawal
            total_withdrawals += monthly_withdrawal
            # Reducir proporcionalmente cada activo
            for asset in new_asset_values:
                new_asset_values[asset] *= (1 - monthly_withdrawal / (portfolio_value + monthly_withdrawal))
        else:
            # Capital agotado
            months_survived = month
            portfolio_value = 0
            new_asset_values = {asset: 0 for asset in new_asset_values}
            break
        
        # Verificar si se debe rebalancear
        current_allocation = {
            asset: value / portfolio_value if portfolio_value > 0 else 0
            for asset, value in new_asset_values.items()
        }
        
        if rebalance_strategy.should_rebalance(current_allocation, current_date, portfolio_value):
            new_asset_values, rebalance_cost = rebalance_strategy.rebalance(
                new_asset_values, 
                portfolio_value
            )
            portfolio_value -= rebalance_cost
            total_rebalance_costs += rebalance_cost
        
        # Actualizar para siguiente mes
        asset_values = new_asset_values
        
        # Guardar estado
        history.append({
            'month': month + 1,
            'portfolio_value': portfolio_value,
            'withdrawal': monthly_withdrawal,
            'base_withdrawal': withdrawal,
            'contribution': contribution_this_month,
            'total_withdrawals': total_withdrawals,
            'total_contributions': total_contributions,
            'total_rebalance_costs': total_rebalance_costs,
            **{f'{asset}_value': new_asset_values.get(asset, 0) for asset in allocation.keys()}
        })
        
        # Avanzar fecha
        current_date += timedelta(days=30)
    
    # Calcular métricas finales
    net_flow = total_contributions - total_withdrawals
    metrics = {
        'final_value': portfolio_value,
        'total_withdrawals': total_withdrawals,
        'total_contributions': total_contributions,
        'net_flow': net_flow,
        'total_rebalance_costs': total_rebalance_costs,
        'months_survived': months_survived,
        'survived_full_period': months_survived == n_months,
        'total_return': (portfolio_value - initial_capital) / initial_capital if initial_capital > 0 else 0
    }
    
    return pd.DataFrame(history), metrics


def monte_carlo_simulation(
    initial_capital,
    asset_stats,
    portfolio_config,
    rebalance_strategy,
    n_months,
    n_iterations,
    withdrawal_amount,
    inflation_rate=0.02,
    apply_inflation=True,
    periodic_contribution=0,
    contribution_enabled=False,
    thirteenth_payment_months=None,
    thirteenth_payment_amount=0,
    thirteenth_payment_enabled=False,
    random_seed=42
):
    """
    Ejecuta simulación Monte Carlo completa.
    
    Returns:
        list: lista de DataFrames con historial de cada simulación
        pd.DataFrame: DataFrame con métricas de todas las simulaciones
    """
    all_histories = []
    all_metrics = []
    
    # Verificar si la cartera usa cash y agregarlo a asset_stats si es necesario
    allocation = portfolio_config['allocation']
    if 'cash' in allocation and allocation['cash'] > 0 and 'cash' not in asset_stats:
        asset_stats = asset_stats.copy()
        asset_stats['cash'] = {'mean_return': 0.02, 'std_dev': 0.001}
    
    print(f"Ejecutando {n_iterations} simulaciones Monte Carlo...")
    
    for i in range(n_iterations):
        if (i + 1) % 1000 == 0:
            print(f"  Progreso: {i + 1}/{n_iterations}")
        
        # Generar retornos para esta iteración
        monthly_returns = generate_monthly_returns(
            asset_stats, 
            n_months, 
            random_seed=random_seed + i if random_seed else None
        )
        
        # Simular camino
        history, metrics = simulate_portfolio_path(
            initial_capital,
            asset_stats,
            portfolio_config,
            rebalance_strategy,
            monthly_returns,
            withdrawal_amount,
            inflation_rate,
            apply_inflation,
            periodic_contribution,
            contribution_enabled,
            thirteenth_payment_months,
            thirteenth_payment_amount,
            thirteenth_payment_enabled
        )
        
        history['simulation'] = i + 1
        all_histories.append(history)
        all_metrics.append(metrics)
    
    metrics_df = pd.DataFrame(all_metrics)
    
    return all_histories, metrics_df


def run_simulation(config_path="config/settings.yaml"):
    """
    Función principal que ejecuta todas las simulaciones.
    """
    # Cargar configuración
    config = load_config(config_path)
    
    print("=" * 60)
    print("🎲 SIMULACIÓN MONTE CARLO DE CARTERAS")
    print("=" * 60)
    
    # Cargar estadísticas de activos
    print("\n1. Cargando estadísticas de activos...")
    asset_stats = load_asset_statistics(config['data_source']['processed_path'])
    
    # Parámetros de simulación
    initial_capital = config['project']['initial_capital']
    n_years = config['project']['simulation_horizon_years']
    n_months = n_years * 12
    withdrawal_amount = config['project']['withdrawals']['amount']
    n_iterations = config['simulation']['montecarlo_iterations']
    random_seed = config['project']['random_seed']
    apply_inflation = config['simulation']['inflation_adjustment']
    
    # Parámetros de contribuciones y cambios en retiros
    contributions_config = config.get('contributions', {})
    periodic_contribution = contributions_config.get('periodic_contribution', 0)
    contribution_enabled = contributions_config.get('enabled', False)
    
    withdrawal_changes_config = config.get('withdrawal_changes', {})
    thirteenth_payment_months = withdrawal_changes_config.get('thirteenth_payment_months', [])
    thirteenth_payment_amount = withdrawal_changes_config.get('thirteenth_payment_amount', withdrawal_amount)
    thirteenth_payment_enabled = withdrawal_changes_config.get('enabled', False)
    
    # Mostrar información sobre contribuciones y cambios en retiros
    if contribution_enabled:
        print(f"\n  💰 Contribuciones periódicas: ${periodic_contribution:,.2f}/mes {'(impuestos)' if periodic_contribution < 0 else '(aportes)'}")
    if thirteenth_payment_enabled:
        print(f"  📅 Décimos sueldos: ${thirteenth_payment_amount:,.2f} en meses {thirteenth_payment_months}")
    
    # Crear directorio de resultados
    os.makedirs(config['project']['output_dir'], exist_ok=True)
    
    # Ejecutar para cada cartera y escenario
    all_results = {}
    
    portfolios = config['portfolios']
    scenarios = config['economic_scenarios']
    
    for portfolio_name, portfolio_config in portfolios.items():
        print(f"\n2. Simulando cartera: {portfolio_config['name']}")
        
        portfolio_results = {}
        
        for scenario_name, scenario_params in scenarios.items():
            print(f"   Escenario: {scenario_name}")
            
            # Crear estrategia de rebalanceo
            rebalance_strategy = create_rebalance_strategy(
                portfolio_config,
                transaction_cost=scenario_params['transaction_cost']
            )
            
            # Ejecutar simulación
            histories, metrics_df = monte_carlo_simulation(
                initial_capital=initial_capital,
                asset_stats=asset_stats,
                portfolio_config=portfolio_config,
                rebalance_strategy=rebalance_strategy,
                n_months=n_months,
                n_iterations=n_iterations,
                withdrawal_amount=withdrawal_amount,
                inflation_rate=scenario_params['inflation_rate'],
                apply_inflation=apply_inflation,
                periodic_contribution=periodic_contribution,
                contribution_enabled=contribution_enabled,
                thirteenth_payment_months=thirteenth_payment_months,
                thirteenth_payment_amount=thirteenth_payment_amount,
                thirteenth_payment_enabled=thirteenth_payment_enabled,
                random_seed=random_seed
            )
            
            # Guardar resultados
            result_key = f"{portfolio_name}_{scenario_name}"
            
            # Guardar métricas
            metrics_path = os.path.join(
                config['project']['output_dir'],
                f"metrics_{result_key}.csv"
            )
            metrics_df.to_csv(metrics_path, index=False)
            
            # Guardar historiales (solo algunos para no ocupar mucho espacio)
            sample_indices = np.random.choice(len(histories), min(100, len(histories)), replace=False)
            sample_histories = [histories[i] for i in sample_indices]
            histories_df = pd.concat(sample_histories, ignore_index=True)
            histories_path = os.path.join(
                config['project']['output_dir'],
                f"histories_{result_key}.csv"
            )
            histories_df.to_csv(histories_path, index=False)
            
            portfolio_results[scenario_name] = {
                'histories': histories,
                'metrics': metrics_df
            }
            
            # Mostrar resumen
            survival_rate = metrics_df['survived_full_period'].mean() * 100
            avg_final_value = metrics_df['final_value'].mean()
            print(f"      ✅ Tasa de supervivencia: {survival_rate:.2f}%")
            print(f"      ✅ Valor final promedio: ${avg_final_value:,.2f}")
        
        all_results[portfolio_name] = portfolio_results
    
    print("\n" + "=" * 60)
    print("✅ SIMULACIONES COMPLETADAS")
    print("=" * 60)
    print(f"Resultados guardados en: {config['project']['output_dir']}")
    
    return all_results


if __name__ == "__main__":
    run_simulation()


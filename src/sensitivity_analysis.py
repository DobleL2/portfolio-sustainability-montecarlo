"""
Módulo para análisis de sensibilidad y comparación de escenarios.
"""

import pandas as pd
import numpy as np
import os
import yaml
from pathlib import Path


def load_config(config_path="config/settings.yaml"):
    """Carga la configuración desde el archivo YAML."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def load_simulation_results(output_dir="results/simulations/", config_path=None):
    """
    Carga todos los resultados de las simulaciones.
    
    Args:
        output_dir: Directorio donde están los resultados
        config_path: Ruta al archivo de configuración (opcional)
    
    Returns:
        dict: Diccionario con métricas por cartera y escenario
    """
    if config_path is None:
        # Intentar encontrar el archivo de configuración
        possible_paths = [
            "config/settings.yaml",
            "../config/settings.yaml",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "config/settings.yaml")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break
        
        if config_path is None:
            config_path = "config/settings.yaml"  # Default
    
    config = load_config(config_path)
    portfolios = config['portfolios']
    scenarios = config['economic_scenarios']
    
    # Normalizar la ruta del directorio de resultados
    # Si es relativa, intentar encontrar desde diferentes ubicaciones
    if not os.path.isabs(output_dir):
        possible_output_dirs = [
            output_dir,  # Ruta relativa directa
            os.path.join("..", output_dir),  # Desde notebooks/
            os.path.join(os.path.dirname(os.path.dirname(__file__)), output_dir)  # Desde raíz del proyecto
        ]
        for possible_dir in possible_output_dirs:
            if os.path.exists(possible_dir):
                output_dir = possible_dir
                break
    
    results = {}
    
    for portfolio_name in portfolios.keys():
        portfolio_results = {}
        
        for scenario_name in scenarios.keys():
            result_key = f"{portfolio_name}_{scenario_name}"
            metrics_path = os.path.join(output_dir, f"metrics_{result_key}.csv")
            
            if os.path.exists(metrics_path):
                metrics_df = pd.read_csv(metrics_path)
                portfolio_results[scenario_name] = metrics_df
            else:
                print(f"⚠️  Archivo no encontrado: {metrics_path}")
        
        if portfolio_results:
            results[portfolio_name] = portfolio_results
    
    return results


def calculate_summary_statistics(metrics_df):
    """
    Calcula estadísticas resumen de las métricas de simulación.
    
    Args:
        metrics_df: DataFrame con métricas de todas las iteraciones
        
    Returns:
        dict: Estadísticas resumen
    """
    stats = {
        'survival_rate': metrics_df['survived_full_period'].mean() * 100,
        'mean_final_value': metrics_df['final_value'].mean(),
        'median_final_value': metrics_df['final_value'].median(),
        'std_final_value': metrics_df['final_value'].std(),
        'min_final_value': metrics_df['final_value'].min(),
        'max_final_value': metrics_df['final_value'].max(),
        'percentile_5': metrics_df['final_value'].quantile(0.05),
        'percentile_25': metrics_df['final_value'].quantile(0.25),
        'percentile_75': metrics_df['final_value'].quantile(0.75),
        'percentile_95': metrics_df['final_value'].quantile(0.95),
        'mean_months_survived': metrics_df['months_survived'].mean(),
        'mean_total_withdrawals': metrics_df['total_withdrawals'].mean(),
        'mean_total_rebalance_costs': metrics_df['total_rebalance_costs'].mean(),
        'mean_total_return': metrics_df['total_return'].mean() * 100
    }
    
    # Agregar métricas de contribuciones si están disponibles
    if 'total_contributions' in metrics_df.columns:
        stats['mean_total_contributions'] = metrics_df['total_contributions'].mean()
        stats['mean_net_flow'] = metrics_df['net_flow'].mean()
    
    return stats


def compare_scenarios(results_dict):
    """
    Compara escenarios económicos para cada cartera.
    
    Args:
        results_dict: Diccionario con resultados por cartera y escenario
        
    Returns:
        pd.DataFrame: Tabla comparativa
    """
    comparison_data = []
    
    for portfolio_name, portfolio_results in results_dict.items():
        for scenario_name, metrics_df in portfolio_results.items():
            stats = calculate_summary_statistics(metrics_df)
            
            comparison_data.append({
                'portfolio': portfolio_name,
                'scenario': scenario_name,
                **stats
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    return comparison_df


def compare_portfolios(results_dict, scenario='base'):
    """
    Compara diferentes carteras bajo un mismo escenario.
    
    Args:
        results_dict: Diccionario con resultados
        scenario: nombre del escenario a comparar
        
    Returns:
        pd.DataFrame: Tabla comparativa
    """
    comparison_data = []
    
    for portfolio_name, portfolio_results in results_dict.items():
        if scenario in portfolio_results:
            metrics_df = portfolio_results[scenario]
            stats = calculate_summary_statistics(metrics_df)
            
            comparison_data.append({
                'portfolio': portfolio_name,
                **stats
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    return comparison_df


def analyze_sensitivity(config_path="config/settings.yaml"):
    """
    Función principal que ejecuta análisis de sensibilidad completo.
    
    Returns:
        dict: Resultados del análisis
    """
    config = load_config(config_path)
    
    print("=" * 60)
    print("📊 ANÁLISIS DE SENSIBILIDAD Y ESCENARIOS")
    print("=" * 60)
    
    # Cargar resultados
    print("\n1. Cargando resultados de simulaciones...")
    results = load_simulation_results(config['project']['output_dir'], config_path=config_path)
    
    if not results:
        print("❌ No se encontraron resultados. Ejecuta primero: python src/simulation.py")
        return None
    
    # Crear directorio de tablas
    tables_dir = "results/tables"
    os.makedirs(tables_dir, exist_ok=True)
    
    # Comparar escenarios
    print("\n2. Comparando escenarios económicos...")
    scenario_comparison = compare_scenarios(results)
    scenario_path = os.path.join(tables_dir, "scenario_comparison.csv")
    scenario_comparison.to_csv(scenario_path, index=False)
    print(f"  ✅ Guardado en: {scenario_path}")
    
    # Comparar carteras por escenario
    print("\n3. Comparando carteras por escenario...")
    portfolio_comparisons = {}
    
    for scenario_name in config['economic_scenarios'].keys():
        portfolio_comp = compare_portfolios(results, scenario=scenario_name)
        portfolio_comparisons[scenario_name] = portfolio_comp
        
        portfolio_path = os.path.join(
            tables_dir, 
            f"portfolio_comparison_{scenario_name}.csv"
        )
        portfolio_comp.to_csv(portfolio_path, index=False)
        print(f"  ✅ {scenario_name}: {portfolio_path}")
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📈 RESUMEN DE COMPARACIÓN DE ESCENARIOS")
    print("=" * 60)
    
    summary_cols = ['portfolio', 'scenario', 'survival_rate', 'mean_final_value', 
                    'percentile_5', 'percentile_95']
    print(scenario_comparison[summary_cols].to_string(index=False))
    
    print("\n" + "=" * 60)
    print("📈 COMPARACIÓN DE CARTERAS (Escenario Base)")
    print("=" * 60)
    
    if 'base' in portfolio_comparisons:
        base_cols = ['portfolio', 'survival_rate', 'mean_final_value', 
                     'percentile_5', 'percentile_95']
        print(portfolio_comparisons['base'][base_cols].to_string(index=False))
    
    print("=" * 60)
    
    return {
        'scenario_comparison': scenario_comparison,
        'portfolio_comparisons': portfolio_comparisons,
        'raw_results': results
    }


if __name__ == "__main__":
    analyze_sensitivity()



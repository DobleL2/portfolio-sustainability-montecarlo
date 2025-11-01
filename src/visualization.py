"""
Módulo para visualización de resultados de simulaciones.
"""

import matplotlib.pyplot as plt
import seaborn as sns
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
    Carga resultados de simulaciones.
    
    Args:
        output_dir: Directorio donde están los resultados
        config_path: Ruta al archivo de configuración (opcional)
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
        
        if portfolio_results:
            results[portfolio_name] = portfolio_results
    
    return results


def load_simulation_histories(output_dir="results/simulations/", config_path=None):
    """
    Carga los historiales de simulación guardados.
    
    Args:
        output_dir: Directorio donde están los resultados
        config_path: Ruta al archivo de configuración (opcional)
    
    Returns:
        dict: Diccionario con historiales por cartera y escenario
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
    
    histories = {}
    
    for portfolio_name in portfolios.keys():
        portfolio_histories = {}
        
        for scenario_name in scenarios.keys():
            result_key = f"{portfolio_name}_{scenario_name}"
            histories_path = os.path.join(output_dir, f"histories_{result_key}.csv")
            
            if os.path.exists(histories_path):
                histories_df = pd.read_csv(histories_path)
                portfolio_histories[scenario_name] = histories_df
        
        if portfolio_histories:
            histories[portfolio_name] = portfolio_histories
    
    return histories


def plot_portfolio_evolution(histories, title="Evolución de la Cartera", 
                             save_path=None, n_paths=50):
    """
    Grafica la evolución del valor de la cartera para múltiples simulaciones.
    
    Args:
        histories: lista de DataFrames con historial de cada simulación
        title: título del gráfico
        save_path: ruta para guardar el gráfico
        n_paths: número máximo de caminos a mostrar
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Mostrar algunos caminos individuales (transparentes)
    for i, history in enumerate(histories[:n_paths]):
        ax.plot(history['month'], history['portfolio_value'], 
                alpha=0.1, color='blue', linewidth=0.5)
    
    # Calcular y mostrar percentiles
    all_months = set()
    for history in histories:
        all_months.update(history['month'].values)
    
    months_sorted = sorted(all_months)
    percentiles = {p: [] for p in [5, 25, 50, 75, 95]}
    
    for month in months_sorted:
        values_at_month = []
        for history in histories:
            month_data = history[history['month'] == month]
            if not month_data.empty:
                values_at_month.append(month_data['portfolio_value'].iloc[0])
        
        if values_at_month:
            for p in percentiles.keys():
                percentiles[p].append(np.percentile(values_at_month, p))
    
    # Plotear percentiles
    ax.plot(months_sorted, percentiles[50], 'b-', linewidth=2, label='Mediana (50%)')
    ax.fill_between(months_sorted, percentiles[25], percentiles[75], 
                     alpha=0.3, color='blue', label='IQR (25-75%)')
    ax.fill_between(months_sorted, percentiles[5], percentiles[95], 
                     alpha=0.2, color='blue', label='Rango (5-95%)')
    
    # Línea de capital inicial
    if histories:
        initial_value = histories[0]['portfolio_value'].iloc[0] if not histories[0].empty else 0
        ax.axhline(y=initial_value, color='green', linestyle='--', 
                   linewidth=1, label='Capital inicial')
    
    # Línea en cero (quiebra)
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1, label='Quiebra')
    
    ax.set_xlabel('Mes', fontsize=12)
    ax.set_ylabel('Valor de la Cartera (USD)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  ✅ Gráfico guardado: {save_path}")
    
    return fig


def plot_final_value_distribution(metrics_df, title="Distribución de Valores Finales",
                                  save_path=None):
    """
    Grafica la distribución de valores finales de la cartera.
    
    Args:
        metrics_df: DataFrame con métricas de simulaciones
        title: título del gráfico
        save_path: ruta para guardar el gráfico
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histograma
    ax1.hist(metrics_df['final_value'], bins=50, edgecolor='black', alpha=0.7, color='steelblue')
    ax1.axvline(metrics_df['final_value'].mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Media: ${metrics_df["final_value"].mean():,.0f}')
    ax1.axvline(metrics_df['final_value'].median(), color='green', linestyle='--', 
                linewidth=2, label=f'Mediana: ${metrics_df["final_value"].median():,.0f}')
    ax1.set_xlabel('Valor Final (USD)', fontsize=11)
    ax1.set_ylabel('Frecuencia', fontsize=11)
    ax1.set_title('Histograma de Valores Finales', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Box plot
    box_data = [metrics_df['final_value']]
    ax2.boxplot(box_data, vert=True, patch_artist=True,
                boxprops=dict(facecolor='steelblue', alpha=0.7))
    ax2.set_ylabel('Valor Final (USD)', fontsize=11)
    ax2.set_title('Box Plot de Valores Finales', fontsize=12, fontweight='bold')
    ax2.set_xticklabels(['Cartera'])
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  ✅ Gráfico guardado: {save_path}")
    
    return fig


def plot_survival_probability(metrics_df, n_months, title="Probabilidad de Supervivencia",
                              save_path=None):
    """
    Grafica la probabilidad de supervivencia a lo largo del tiempo.
    
    Args:
        metrics_df: DataFrame con métricas
        n_months: número total de meses en la simulación
        title: título del gráfico
        save_path: ruta para guardar
    """
    # Esta función necesitaría historiales completos para calcular mes a mes
    # Por ahora, mostramos la tasa de supervivencia final
    fig, ax = plt.subplots(figsize=(10, 6))
    
    survival_rate = metrics_df['survived_full_period'].mean() * 100
    months_survived = metrics_df['months_survived']
    
    # Histograma de meses sobrevividos
    ax.hist(months_survived, bins=min(50, months_survived.nunique()), 
            edgecolor='black', alpha=0.7, color='coral')
    ax.axvline(n_months, color='green', linestyle='--', linewidth=2, 
               label=f'Periodo completo ({n_months} meses)')
    ax.axvline(months_survived.mean(), color='red', linestyle='--', linewidth=2,
               label=f'Media: {months_survived.mean():.1f} meses')
    ax.set_xlabel('Meses Sobrevividos', fontsize=11)
    ax.set_ylabel('Frecuencia', fontsize=11)
    ax.set_title(f'{title}\nTasa de Supervivencia: {survival_rate:.2f}%', 
                 fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  ✅ Gráfico guardado: {save_path}")
    
    return fig


def plot_capital_evolution(histories_df, portfolio_name, scenario_name, 
                           initial_capital=None, title=None, save_path=None):
    """
    Grafica la evolución del capital a lo largo del tiempo para una cartera.
    
    Args:
        histories_df: DataFrame con historiales de simulación
        portfolio_name: nombre de la cartera
        scenario_name: nombre del escenario
        initial_capital: capital inicial (opcional)
        title: título del gráfico (opcional)
        save_path: ruta para guardar el gráfico
    """
    if histories_df.empty:
        print(f"  ⚠️  No hay datos de historial para {portfolio_name} - {scenario_name}")
        return None
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Obtener todas las simulaciones únicas
    simulation_ids = histories_df['simulation'].unique()
    months = sorted(histories_df['month'].unique())
    
    # Calcular percentiles a lo largo del tiempo
    percentiles_data = {p: [] for p in [5, 25, 50, 75, 95]}
    mean_values = []
    
    for month in months:
        month_data = histories_df[histories_df['month'] == month]['portfolio_value']
        if not month_data.empty:
            values = month_data.values
            for p in percentiles_data.keys():
                percentiles_data[p].append(np.percentile(values, p))
            mean_values.append(values.mean())
        else:
            for p in percentiles_data.keys():
                percentiles_data[p].append(0)
            mean_values.append(0)
    
    # Plotear algunos caminos individuales (transparentes)
    for sim_id in simulation_ids[:30]:  # Mostrar solo algunas para no saturar
        sim_data = histories_df[histories_df['simulation'] == sim_id]
        sim_data_sorted = sim_data.sort_values('month')
        ax.plot(sim_data_sorted['month'], sim_data_sorted['portfolio_value'], 
                alpha=0.15, color='gray', linewidth=0.5)
    
    # Plotear percentiles
    ax.plot(months, percentiles_data[50], 'b-', linewidth=2.5, label='Mediana (50%)')
    ax.fill_between(months, percentiles_data[25], percentiles_data[75], 
                     alpha=0.3, color='blue', label='IQR (25-75%)')
    ax.fill_between(months, percentiles_data[5], percentiles_data[95], 
                     alpha=0.2, color='blue', label='Rango (5-95%)')
    ax.plot(months, mean_values, 'r--', linewidth=2, label='Media', alpha=0.7)
    
    # Línea de capital inicial
    if initial_capital:
        ax.axhline(y=initial_capital, color='green', linestyle='--', 
                   linewidth=2, label=f'Capital inicial (${initial_capital:,.0f})', alpha=0.7)
    else:
        # Intentar obtener del primer mes
        first_month_data = histories_df[histories_df['month'] == histories_df['month'].min()]
        if not first_month_data.empty:
            avg_initial = first_month_data['portfolio_value'].mean()
            ax.axhline(y=avg_initial, color='green', linestyle='--', 
                       linewidth=2, label=f'Capital inicial (${avg_initial:,.0f})', alpha=0.7)
    
    # Línea en cero (quiebra)
    ax.axhline(y=0, color='red', linestyle='-', linewidth=1.5, label='Quiebra', alpha=0.5)
    
    ax.set_xlabel('Mes', fontsize=13, fontweight='bold')
    ax.set_ylabel('Valor de la Cartera (USD)', fontsize=13, fontweight='bold')
    
    if title:
        ax.set_title(title, fontsize=15, fontweight='bold', pad=15)
    else:
        # Intentar encontrar el archivo de configuración
        possible_paths = [
            "config/settings.yaml",
            "../config/settings.yaml",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "config/settings.yaml")
        ]
        config_path = None
        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break
        if config_path is None:
            config_path = "config/settings.yaml"
        
        config = load_config(config_path)
        portfolio_label = config['portfolios'][portfolio_name]['name']
        ax.set_title(f'Evolución del Capital - {portfolio_label} ({scenario_name})', 
                     fontsize=15, fontweight='bold', pad=15)
    
    ax.legend(loc='best', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Formatear eje Y con comas
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  ✅ Gráfico guardado: {save_path}")
    
    return fig


def plot_capital_evolution_comparison(histories_dict, scenario_name='base',
                                      initial_capital=None, title=None, save_path=None, config_path=None):
    """
    Compara la evolución del capital entre diferentes carteras.
    
    Args:
        histories_dict: Diccionario con historiales por cartera
        scenario_name: nombre del escenario a comparar
        initial_capital: capital inicial (opcional)
        title: título del gráfico (opcional)
        save_path: ruta para guardar el gráfico
        config_path: ruta al archivo de configuración (opcional)
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
            config_path = "config/settings.yaml"
    
    config = load_config(config_path)
    portfolios = config['portfolios']
    
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # Colores para cada cartera
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    portfolio_names_list = []
    medians_list = []
    
    for idx, (portfolio_name, portfolio_histories) in enumerate(histories_dict.items()):
        if scenario_name not in portfolio_histories:
            continue
        
        histories_df = portfolio_histories[scenario_name]
        
        if histories_df.empty:
            continue
        
        portfolio_label = portfolios[portfolio_name]['name']
        portfolio_names_list.append(portfolio_label)
        
        # Calcular mediana a lo largo del tiempo
        months = sorted(histories_df['month'].unique())
        median_values = []
        
        for month in months:
            month_data = histories_df[histories_df['month'] == month]['portfolio_value']
            if not month_data.empty:
                median_values.append(np.percentile(month_data.values, 50))
            else:
                median_values.append(0)
        
        medians_list.append(median_values)
        
        # Plotear mediana
        color = colors[idx % len(colors)]
        ax.plot(months, median_values, linewidth=3, label=portfolio_label, 
                color=color, alpha=0.8)
        
        # Calcular y plotear banda de confianza (5-95%)
        percentile_5 = []
        percentile_95 = []
        for month in months:
            month_data = histories_df[histories_df['month'] == month]['portfolio_value']
            if not month_data.empty:
                percentile_5.append(np.percentile(month_data.values, 5))
                percentile_95.append(np.percentile(month_data.values, 95))
            else:
                percentile_5.append(0)
                percentile_95.append(0)
        
        ax.fill_between(months, percentile_5, percentile_95, 
                         alpha=0.15, color=color)
    
    # Línea de capital inicial
    if initial_capital:
        ax.axhline(y=initial_capital, color='green', linestyle='--', 
                   linewidth=2, label=f'Capital inicial (${initial_capital:,.0f})', 
                   alpha=0.7, zorder=0)
    
    # Línea en cero (quiebra)
    ax.axhline(y=0, color='red', linestyle='-', linewidth=1.5, 
               label='Quiebra', alpha=0.5, zorder=0)
    
    ax.set_xlabel('Mes', fontsize=14, fontweight='bold')
    ax.set_ylabel('Valor de la Cartera (USD)', fontsize=14, fontweight='bold')
    
    if title:
        ax.set_title(title, fontsize=16, fontweight='bold', pad=15)
    else:
        ax.set_title(f'Comparación de Evolución del Capital - Escenario: {scenario_name.capitalize()}', 
                     fontsize=16, fontweight='bold', pad=15)
    
    ax.legend(loc='best', fontsize=11, framealpha=0.9, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Formatear eje Y con comas
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  ✅ Gráfico guardado: {save_path}")
    
    return fig


def plot_portfolio_comparison(results_dict, metric='survival_rate', 
                              title="Comparación de Carteras", save_path=None, config_path=None):
    """
    Compara diferentes carteras usando una métrica específica.
    
    Args:
        results_dict: Diccionario con resultados por cartera y escenario
        metric: métrica a comparar ('survival_rate', 'mean_final_value', etc.)
        title: título del gráfico
        save_path: ruta para guardar
        config_path: ruta al archivo de configuración (opcional)
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
            config_path = "config/settings.yaml"
    
    config = load_config(config_path)
    portfolios = config['portfolios']
    
    comparison_data = []
    
    for portfolio_name, portfolio_results in results_dict.items():
        portfolio_label = portfolios[portfolio_name]['name']
        
        for scenario_name, metrics_df in portfolio_results.items():
            if metric == 'survival_rate':
                value = metrics_df['survived_full_period'].mean() * 100
            elif metric == 'mean_final_value':
                value = metrics_df['final_value'].mean()
            else:
                value = metrics_df[metric].mean()
            
            comparison_data.append({
                'portfolio': portfolio_label,
                'scenario': scenario_name,
                'value': value
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Crear gráfico de barras agrupadas
    scenarios = comparison_df['scenario'].unique()
    portfolios_list = comparison_df['portfolio'].unique()
    x = np.arange(len(portfolios_list))
    width = 0.25
    
    for i, scenario in enumerate(scenarios):
        scenario_data = comparison_df[comparison_df['scenario'] == scenario]
        values = [scenario_data[scenario_data['portfolio'] == p]['value'].iloc[0] 
                  for p in portfolios_list]
        ax.bar(x + i * width, values, width, label=scenario.capitalize(), alpha=0.8)
    
    ax.set_xlabel('Cartera', fontsize=11)
    
    if metric == 'survival_rate':
        ax.set_ylabel('Tasa de Supervivencia (%)', fontsize=11)
    elif metric == 'mean_final_value':
        ax.set_ylabel('Valor Final Promedio (USD)', fontsize=11)
    else:
        ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=11)
    
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xticks(x + width)
    ax.set_xticklabels(portfolios_list, rotation=15, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  ✅ Gráfico guardado: {save_path}")
    
    return fig


def generate_all_visualizations(config_path="config/settings.yaml"):
    """
    Genera todas las visualizaciones del proyecto.
    """
    config = load_config(config_path)
    
    print("=" * 60)
    print("📊 GENERACIÓN DE VISUALIZACIONES")
    print("=" * 60)
    
    # Normalizar rutas para que funcionen desde cualquier directorio
    base_dir = os.path.dirname(os.path.dirname(__file__)) if hasattr(__file__, '__file__') else os.getcwd()
    
    # Crear directorio de figuras (intentar varias ubicaciones)
    possible_figures_dirs = [
        "results/figures",
        "../results/figures",
        os.path.join(base_dir, "results/figures")
    ]
    figures_dir = None
    for possible_dir in possible_figures_dirs:
        if os.path.exists(os.path.dirname(possible_dir)) or possible_dir == "results/figures":
            figures_dir = possible_dir
            os.makedirs(figures_dir, exist_ok=True)
            break
    
    if figures_dir is None:
        figures_dir = "results/figures"
        os.makedirs(figures_dir, exist_ok=True)
    
    # Cargar resultados
    print("\n1. Cargando resultados...")
    results = load_simulation_results(config['project']['output_dir'], config_path=config_path)
    
    if not results:
        print("❌ No se encontraron resultados. Ejecuta primero: python src/simulation.py")
        return
    
    portfolios = config['portfolios']
    scenarios = config['economic_scenarios']
    n_months = config['project']['simulation_horizon_years'] * 12
    
    print("\n2. Cargando historiales de simulación...")
    histories = load_simulation_histories(config['project']['output_dir'], config_path=config_path)
    
    initial_capital = config['project']['initial_capital']
    
    print("\n3. Generando gráficos de evolución del capital por cartera...")
    
    # Gráficos de evolución individual por cartera y escenario
    for portfolio_name, portfolio_histories in histories.items():
        portfolio_label = portfolios[portfolio_name]['name']
        
        for scenario_name, histories_df in portfolio_histories.items():
            plot_capital_evolution(
                histories_df,
                portfolio_name,
                scenario_name,
                initial_capital=initial_capital,
                save_path=os.path.join(
                    figures_dir,
                    f"evolution_{portfolio_name}_{scenario_name}.png"
                )
            )
    
    print("\n4. Generando gráficos de comparación de evolución entre carteras...")
    
    # Comparación de evolución para cada escenario
    for scenario_name in scenarios.keys():
        plot_capital_evolution_comparison(
            histories,
            scenario_name=scenario_name,
            initial_capital=initial_capital,
            save_path=os.path.join(
                figures_dir,
                f"evolution_comparison_{scenario_name}.png"
            ),
            config_path=config_path
        )
    
    print("\n5. Generando gráficos de comparación de carteras (métricas)...")
    
    # Comparación de tasas de supervivencia
    plot_portfolio_comparison(
        results, 
        metric='survival_rate',
        title="Comparación de Tasas de Supervivencia",
        save_path=os.path.join(figures_dir, "comparison_survival_rate.png"),
        config_path=config_path
    )
    
    # Comparación de valores finales
    plot_portfolio_comparison(
        results,
        metric='mean_final_value',
        title="Comparación de Valores Finales Promedio",
        save_path=os.path.join(figures_dir, "comparison_final_values.png"),
        config_path=config_path
    )
    
    print("\n6. Generando gráficos de distribución...")
    
    # Distribuciones de valores finales por cartera y escenario
    for portfolio_name, portfolio_results in results.items():
        portfolio_label = portfolios[portfolio_name]['name']
        
        for scenario_name, metrics_df in portfolio_results.items():
            plot_final_value_distribution(
                metrics_df,
                title=f"Distribución - {portfolio_label} ({scenario_name})",
                save_path=os.path.join(
                    figures_dir, 
                    f"distribution_{portfolio_name}_{scenario_name}.png"
                )
            )
            
            plot_survival_probability(
                metrics_df,
                n_months,
                title=f"Supervivencia - {portfolio_label} ({scenario_name})",
                save_path=os.path.join(
                    figures_dir,
                    f"survival_{portfolio_name}_{scenario_name}.png"
                )
            )
    
    print("\n" + "=" * 60)
    print("✅ VISUALIZACIONES COMPLETADAS")
    print("=" * 60)
    print(f"Gráficos guardados en: {figures_dir}")


if __name__ == "__main__":
    generate_all_visualizations()


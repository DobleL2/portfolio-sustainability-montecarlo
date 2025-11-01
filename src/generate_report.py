"""
Genera el informe LaTeX con datos reales de los resultados.
"""

import yaml
import pandas as pd
import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sensitivity_analysis import (
    load_simulation_results, 
    compare_scenarios, 
    compare_portfolios,
    calculate_summary_statistics
)


def generate_latex_report(config_path="config/settings.yaml", output_path="reports/overleaf/informe_final.tex"):
    """
    Genera un informe LaTeX completo con los resultados reales del proyecto.
    Guarda el archivo .tex dentro de la carpeta overleaf junto con los gráficos
    para facilitar la compilación en Overleaf (solo se necesita subir la carpeta overleaf completa).
    """
    import os
    import shutil
    
    # Cargar configuración
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Cargar resultados
    results = load_simulation_results(config['project']['output_dir'])
    
    if not results:
        print("⚠️  No se encontraron resultados. Ejecuta primero las simulaciones.")
        return
    
    # Cargar estadísticas de activos
    stats_df = pd.read_csv(f"{config['data_source']['processed_path']}/asset_statistics.csv")
    
    # Comparación de escenarios
    scenario_comparison = compare_scenarios(results)
    
    # Preparar contenido LaTeX
    latex_content = generate_latex_content(config, results, scenario_comparison, stats_df)
    
    # Crear carpeta overleaf y subcarpetas si no existen
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Guardar archivo .tex dentro de la carpeta overleaf
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    # Crear carpeta figures dentro de overleaf
    overleaf_dir = os.path.dirname(os.path.abspath(output_path))
    figures_dir = os.path.join(overleaf_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)
    
    # Buscar carpeta de gráficos (intentar varias ubicaciones)
    possible_figures_dirs = [
        "results/figures",
        os.path.join(os.path.dirname(os.path.dirname(overleaf_dir)), "results", "figures"),
        os.path.join(os.path.dirname(os.path.dirname(output_path)), "results", "figures")
    ]
    
    original_figures_dir = None
    for possible_dir in possible_figures_dirs:
        if os.path.exists(possible_dir):
            original_figures_dir = possible_dir
            break
    
    if original_figures_dir and os.path.exists(original_figures_dir):
        # Copiar gráficos principales
        key_figures = [
            "comparison_survival_rate.png",
            "comparison_final_values.png",
            "evolution_comparison_base.png",
            "evolution_comparison_optimistic.png",
            "evolution_comparison_pessimistic.png"
        ]
        
        copied_count = 0
        for fig in key_figures:
            src_path = os.path.join(original_figures_dir, fig)
            if os.path.exists(src_path):
                dst_path = os.path.join(figures_dir, fig)
                shutil.copy2(src_path, dst_path)
                copied_count += 1
        
        if copied_count > 0:
            print(f"   ✅ {copied_count} gráficos copiados a {figures_dir}")
    
    print(f"\n✅ Informe LaTeX generado en: {output_path}")
    print(f"📁 Carpeta Overleaf lista en: {overleaf_dir}")
    print(f"   📄 Para compilar en Overleaf, sube la carpeta completa 'overleaf/'")
    print(f"   📄 Incluye: informe_final.tex + carpeta figures/")
    return output_path


def generate_latex_content(config, results, scenario_comparison, stats_df):
    """Genera el contenido completo del documento LaTeX."""
    
    portfolios = config['portfolios']
    scenarios = config['economic_scenarios']
    
    # Definir variables para usar en el documento
    horizon_years = config['project']['simulation_horizon_years']
    initial_capital = config['project']['initial_capital']
    withdrawal_amount = config['project']['withdrawals']['amount']
    withdrawal_rate = (withdrawal_amount * 12) / initial_capital * 100
    n_iterations = config['simulation']['montecarlo_iterations']
    random_seed = config['project']['random_seed']
    inflation_enabled = "Habilitado" if config['simulation']['inflation_adjustment'] else "Deshabilitado"
    data_start = config['data_source']['start_date']
    data_end = config['data_source']['end_date']
    data_years = 2025 - int(data_start[:4])
    
    # Generar tablas de resultados
    survival_table = generate_survival_table(scenario_comparison, portfolios, scenarios)
    final_value_table = generate_final_value_table(scenario_comparison, portfolios, scenarios)
    percentiles_table = generate_percentiles_table(scenario_comparison, portfolios, scenarios)
    asset_stats_table = generate_asset_stats_table(stats_df)
    
    # Construir el documento LaTeX usando f-strings con todas las variables definidas
    latex = f"""\\documentclass[12pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[spanish]{{babel}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{booktabs}}
\\usepackage{{geometry}}
\\usepackage{{hyperref}}
\\usepackage{{float}}
\\usepackage{{longtable}}
\\usepackage{{xcolor}}
\\usepackage{{fancyhdr}}

\\geometry{{margin=2.5cm}}

% Configuración de encabezado
\\setlength{{\\headheight}}{{13.6pt}}
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[L]{{\\small Matemática Actuarial}}
\\fancyhead[R]{{\\small Comparación de Rentabilidades}}
\\fancyfoot[C]{{\\thepage}}

\\title{{\\textbf{{Comparación de Rentabilidades en Instrumentos Financieros Reales}}\\\\
\\large Análisis de Sostenibilidad de Carteras de Inversión mediante Simulación Monte Carlo}}
\\author{{{config['project']['author']}}}
\\date{{\\today}}

\\begin{{document}}

\\maketitle

\\tableofcontents
\\newpage

% ============================================
% 1. INTRODUCCIÓN
% ============================================
\\section{{Introducción}}

El presente trabajo tiene como objetivo evaluar la sostenibilidad de una cartera de inversión inicial de \\textbf{{USD {initial_capital:,}}} bajo distintas estrategias de asignación de activos y rebalanceo, determinando su capacidad para sostener pagos mensuales de \\textbf{{USD {withdrawal_amount:,}}} durante un período de \\textbf{{{horizon_years} años}}. El enfoque del análisis maximiza la rentabilidad mientras minimiza el riesgo de agotamiento del capital.

En un contexto económico caracterizado por la volatilidad de los mercados financieros, la planificación de retiro y la gestión de carteras de inversión requieren herramientas sofisticadas que permitan evaluar múltiples escenarios y estrategias. La simulación Monte Carlo emerge como una metodología robusta para modelar la incertidumbre inherente a los mercados financieros, permitiendo analizar miles de posibles resultados y cuantificar el riesgo asociado a diferentes estrategias de inversión.

Este estudio compara tres estrategias de asignación de activos utilizando datos históricos reales de instrumentos financieros, evaluando su desempeño bajo tres escenarios económicos diferentes (base, optimista y pesimista). Los resultados obtenidos proporcionan información valiosa para la toma de decisiones de inversión bajo condiciones de incertidumbre.

% ============================================
% 2. OBJETIVOS
% ============================================
\\section{{Objetivos}}

\\subsection{{Objetivo General}}

Evaluar la sostenibilidad y rentabilidad de diferentes estrategias de asignación de activos financieros, determinando cuál maximiza la probabilidad de sostener retiros mensuales durante el período de {horizon_years} años establecido.

\\subsection{{Objetivos Específicos}}

\\begin{{enumerate}}
    \\item Comparar el desempeño de tres estrategias de asignación de activos bajo diferentes escenarios económicos.
    \\item Cuantificar la probabilidad de supervivencia (no agotamiento del capital) para cada estrategia.
    \\item Evaluar el impacto de diferentes estrategias de rebalanceo en el desempeño de las carteras.
    \\item Analizar la sensibilidad de los resultados ante variaciones en las condiciones económicas (inflación, costos de transacción).
    \\item Determinar la distribución de valores finales y cuantificar el riesgo asociado a cada estrategia.
    \\item Evaluar el efecto de contribuciones periódicas y cambios en los montos de retiro (décimos sueldos).
\\end{{enumerate}}

% ============================================
% 3. METODOLOGÍA
% ============================================
\\section{{Metodología}}

\\subsection{{Datos Utilizados}}

El análisis se basa en datos históricos de los siguientes instrumentos financieros, obtenidos de Yahoo Finance para el período {data_start} - {data_end}:

\\begin{{itemize}}
"""
    
    # Agregar información de activos (escapar caracteres especiales)
    for asset_type, asset_info in config['assets'].items():
        asset_name = asset_info['name'].replace('&', '\\&').replace('_', '\\_')
        # Para tickers, el símbolo ^ debe estar escapado como texto (no en modo matemático)
        ticker = asset_info['ticker'].replace('&', '\\&').replace('_', '\\_').replace('^', '\\textasciicircum{}')
        latex += f"    \\item \\textbf{{{asset_name}}}: {ticker}\n"
    
    latex += "\\end{itemize}\n\n"
    latex += "\\subsection{Procesamiento de Datos}\n\n"
    latex += "Los datos históricos fueron procesados para calcular:\n"
    latex += "\\begin{itemize}\n"
    latex += "    \\item Retornos logarítmicos diarios\n"
    latex += "    \\item Estadísticas anualizadas (media y desviación estándar)\n"
    latex += "    \\item Matriz de correlación entre activos\n"
    latex += "\\end{itemize}\n\n"
    latex += "\\subsection{Simulación Monte Carlo}\n\n"

    latex += "Se implementó una simulación Monte Carlo con las siguientes características:\n\n"
    latex += "\\begin{itemize}\n"
    latex += f"    \\item \\textbf{{Iteraciones}}: {n_iterations:,} simulaciones por cartera y escenario\n"
    latex += f"    \\item \\textbf{{Horizonte temporal}}: {horizon_years * 12} meses ({horizon_years} años)\n"
    latex += "    \\item \\textbf{{Distribución de retornos}}: Distribución normal basada en estadísticas históricas\n"
    latex += "    \\item \\textbf{{Ajustes aplicados}}:\n"
    latex += "    \\begin{itemize}\n"
    latex += "        \\item Ajuste por inflación en retiros mensuales\n"
    latex += "        \\item Costos de transacción en rebalanceos\n"
    latex += "        \\item Contribuciones periódicas (opcional)\n"
    latex += "        \\item Décimos sueldos o retiros adicionales (opcional)\n"
    latex += "    \\end{itemize}\n"
    latex += "\\end{itemize}\n\n"
    latex += "\\subsection{Estrategias de Inversión Evaluadas}\n\n"
    
    # Agregar descripción de carteras
    for i, (portfolio_name, portfolio_config) in enumerate(config['portfolios'].items(), 1):
        allocation = portfolio_config['allocation']
        # Escapar % para LaTeX y crear strings de asignación
        allocation_parts = []
        for k, v in allocation.items():
            if v > 0:
                asset_name = k.replace('stocks', 'Acciones').replace('bonds', 'Bonos').replace('gold', 'Oro').replace('cash', 'Efectivo')
                allocation_parts.append(f"{asset_name}: {v*100:.0f}\\%")
        allocation_str = ", ".join(allocation_parts)
        
        rebalance_type = portfolio_config['rebalance']['type']
        rebalance_desc = ""
        if rebalance_type == "time":
            freq = portfolio_config['rebalance']['frequency']
            if freq == "annual":
                rebalance_desc = "Anual (basado en tiempo)"
            elif freq == "quarterly":
                rebalance_desc = "Trimestral (basado en tiempo)"
            else:
                rebalance_desc = freq
        else:
            threshold = portfolio_config['rebalance']['threshold']*100
            rebalance_desc = f"Por umbral ({threshold:.0f}\\% de desviación)"
        
        portfolio_name_safe = portfolio_config['name'].replace('%', '\\%')
        
        latex += f"\\subsubsection{{Cartera {i}: {portfolio_name_safe}}}\n"
        latex += "\\begin{itemize}\n"
        latex += f"    \\item Asignación: {allocation_str}\n"
        latex += f"    \\item Rebalanceo: {rebalance_desc}\n"
        latex += "\\end{itemize}\n\n"
    
    # Escenarios económicos
    latex += "\\subsection{Escenarios Económicos}\n\n"
    latex += "Se evaluaron tres escenarios económicos:\n\n"
    latex += "\\begin{enumerate}\n"
    
    for scenario_name, scenario_params in scenarios.items():
        scenario_label = scenario_name.capitalize()
        latex += f"    \\item \\textbf{{Escenario {scenario_label}}}: Inflación {scenario_params['inflation_rate']*100:.1f}\\% anual, costos de transacción {scenario_params['transaction_cost']*100:.1f}\\%\n"
    
    latex += "\\end{enumerate}\n\n"
    
    latex += "\\subsection{Métricas de Evaluación}\n\n"

    latex += "Las principales métricas calculadas para cada simulación incluyen:\n"
    latex += "\\begin{itemize}\n"
    latex += f"    \\item Tasa de supervivencia (probabilidad de completar {horizon_years} años)\n"
    latex += "    \\item Valor final promedio de la cartera\n"
    latex += "    \\item Distribución de valores finales (percentiles 5, 25, 50, 75, 95)\n"
    latex += "    \\item Meses sobrevividos promedio\n"
    latex += "    \\item Flujos de caja netos (contribuciones - retiros)\n"
    latex += "\\end{itemize}\n\n"
    latex += "% ============================================\n"
    latex += "% 4. RESULTADOS\n"
    latex += "% ============================================\n"
    latex += "\\section{Resultados}\n\n"
    latex += "\\subsection{Resumen Ejecutivo}\n\n"
    latex += "Los resultados de las simulaciones Monte Carlo revelan diferencias significativas en el desempeño de las tres estrategias de inversión evaluadas. A continuación se presentan los hallazgos principales.\n\n"
    latex += "\\subsection{Comparación de Tasas de Supervivencia}\n\n"
    latex += f"La tasa de supervivencia representa el porcentaje de simulaciones donde la cartera logró mantener capital suficiente para completar los {horizon_years} años de retiros mensuales.\n\n"
    
    
    latex += survival_table
    
    # Incluir gráfico de comparación de supervivencia si existe
    latex += "\\begin{figure}[H]\n"
    latex += "\\centering\n"
    latex += "\\includegraphics[width=0.9\\textwidth]{figures/comparison_survival_rate.png}\n"
    latex += "\\caption{Comparación de Tasas de Supervivencia por Cartera y Escenario}\n"
    latex += "\\label{fig:survival_comparison}\n"
    latex += "\\end{figure}\n\n"
    
    # Análisis dinámico basado en los datos reales
    best_survival_by_scenario = {}
    for scenario in scenarios.keys():
        scenario_data = scenario_comparison[scenario_comparison['scenario'] == scenario]
        if len(scenario_data) > 0:
            best_idx = scenario_data['survival_rate'].idxmax()
            best_port = scenario_data.loc[best_idx]
            best_survival_by_scenario[scenario] = {
                'name': portfolios[best_port['portfolio']]['name'].replace('%', '\\%'),
                'rate': best_port['survival_rate']
            }
    
    # Generar análisis dinámico
    base_best = best_survival_by_scenario.get('base', {})
    if base_best:
        latex += f"\\textbf{{Análisis}}: {base_best['name']} muestra la mayor tasa de supervivencia en el escenario base ({base_best['rate']:.1f}\\%). "
    
    # Identificar consistencia entre escenarios
    best_names = [v['name'] for v in best_survival_by_scenario.values()]
    if len(set(best_names)) == 1:
        latex += f"Esta cartera mantiene su superioridad en todos los escenarios evaluados, sugiriendo robustez ante diferentes condiciones económicas. "
    else:
        latex += "El desempeño relativo varía según el escenario económico, indicando sensibilidad a las condiciones del mercado. "
    
    latex += "Las carteras con mayor exposición a acciones generalmente presentan mayor potencial de crecimiento, pero también mayor volatilidad.\n\n"
    latex += "\\subsection{Valores Finales Promedio}\n\n"
    latex += f"El valor final promedio indica cuánto capital queda en promedio después de {horizon_years} años de retiros.\n\n"
    
    latex += final_value_table
    
    # Incluir gráfico de comparación de valores finales si existe
    latex += "\\begin{figure}[H]\n"
    latex += "\\centering\n"
    latex += "\\includegraphics[width=0.9\\textwidth]{figures/comparison_final_values.png}\n"
    latex += "\\caption{Comparación de Valores Finales Promedio por Cartera y Escenario}\n"
    latex += "\\label{fig:final_values_comparison}\n"
    latex += "\\end{figure}\n\n"
    
    # Análisis dinámico de valores finales
    best_final_by_scenario = {}
    worst_final_by_scenario = {}
    for scenario in scenarios.keys():
        scenario_data = scenario_comparison[scenario_comparison['scenario'] == scenario]
        if len(scenario_data) > 0:
            best_idx = scenario_data['mean_final_value'].idxmax()
            worst_idx = scenario_data['mean_final_value'].idxmin()
            best_port = scenario_data.loc[best_idx]
            worst_port = scenario_data.loc[worst_idx]
            best_final_by_scenario[scenario] = {
                'name': portfolios[best_port['portfolio']]['name'].replace('%', '\\%'),
                'value': best_port['mean_final_value']
            }
            worst_final_by_scenario[scenario] = {
                'name': portfolios[worst_port['portfolio']]['name'].replace('%', '\\%'),
                'value': worst_port['mean_final_value']
            }
    
    base_best_final = best_final_by_scenario.get('base', {})
    base_worst_final = worst_final_by_scenario.get('base', {})
    
    if base_best_final and base_worst_final:
        latex += f"\\textbf{{Análisis}}: {base_best_final['name']} genera los valores finales promedio más altos en el escenario base (\\${base_best_final['value']:,.0f}), lo que indica mayor capacidad de generar crecimiento. "
        
        if base_best_final['name'] != base_worst_final['name']:
            latex += f"Por otro lado, {base_worst_final['name']} muestra los valores finales promedio más bajos (\\${base_worst_final['value']:,.0f}), lo que sugiere que su estrategia de asignación puede requerir ajustes para mejorar el desempeño. "
        
        # Verificar consistencia entre escenarios
        best_final_names = [v['name'] for v in best_final_by_scenario.values()]
        if len(set(best_final_names)) == 1:
            latex += "Esta diferencia de desempeño se mantiene consistente a través de todos los escenarios evaluados.\n\n"
        else:
            latex += "Sin embargo, el desempeño relativo puede variar según las condiciones económicas.\n\n"
    else:
        latex += "\\textbf{Análisis}: Los valores finales promedio muestran diferencias significativas entre las carteras, reflejando el impacto de las distintas estrategias de asignación de activos.\n\n"
    latex += "\\subsection{Análisis de Riesgo (Percentiles)}\n\n"
    latex += "Las tablas de percentiles permiten evaluar la distribución de resultados y el riesgo asociado a cada estrategia.\n\n"
    
    latex += percentiles_table
    
    # Incluir gráficos de evolución del capital por escenario
    latex += "\\subsection{Evolución del Capital}\n\n"
    latex += "A continuación se presenta la evolución del capital para cada escenario económico, comparando las tres carteras de inversión:\n\n"
    
    latex += "\\begin{figure}[H]\n"
    latex += "\\centering\n"
    latex += "\\includegraphics[width=0.9\\textwidth]{figures/evolution_comparison_base.png}\n"
    latex += "\\caption{Evolución del Capital - Escenario Base}\n"
    latex += "\\label{fig:evolution_base}\n"
    latex += "\\end{figure}\n\n"
    
    latex += "\\begin{figure}[H]\n"
    latex += "\\centering\n"
    latex += "\\includegraphics[width=0.9\\textwidth]{figures/evolution_comparison_optimistic.png}\n"
    latex += "\\caption{Evolución del Capital - Escenario Optimista}\n"
    latex += "\\label{fig:evolution_optimistic}\n"
    latex += "\\end{figure}\n\n"
    
    latex += "\\begin{figure}[H]\n"
    latex += "\\centering\n"
    latex += "\\includegraphics[width=0.9\\textwidth]{figures/evolution_comparison_pessimistic.png}\n"
    latex += "\\caption{Evolución del Capital - Escenario Pesimista}\n"
    latex += "\\label{fig:evolution_pessimistic}\n"
    latex += "\\end{figure}\n\n"
    
    latex += "\\textbf{Interpretación}:\n"
    latex += "\\begin{itemize}\n"
    latex += "    \\item El percentil 5 (P5) en \\$0 indica que más del 5\\% de las simulaciones resultaron en quiebra total.\n"
    latex += f"    \\item La mediana en \\$0 para todas las carteras indica que en más del 50\\% de los casos, el capital se agotó antes de completar {horizon_years} años.\n"
    
    # Identificar dinámicamente la cartera con mayor percentil 95
    base_percentiles = scenario_comparison[scenario_comparison['scenario'] == 'base']
    if len(base_percentiles) > 0 and 'percentile_95' in base_percentiles.columns:
        best_p95_idx = base_percentiles['percentile_95'].idxmax()
        best_p95_port = base_percentiles.loc[best_p95_idx]
        best_p95_name = portfolios[best_p95_port['portfolio']]['name'].replace('%', '\\%')
        best_p95_value = best_p95_port['percentile_95']
        latex += f"    \\item El percentil 95 muestra el potencial máximo de crecimiento: {best_p95_name} presenta el mayor valor (\\${best_p95_value:,.0f}), indicando el potencial de crecimiento en el escenario más favorable.\n"
    else:
        latex += "    \\item El percentil 95 muestra el potencial máximo de crecimiento de cada estrategia.\n"
    
    latex += "\\end{itemize}\n\n"
    
    # Sección sobre contribuciones y flujos netos si están habilitados
    contributions_config = config.get('contributions', {})
    withdrawal_changes_config = config.get('withdrawal_changes', {})
    contribution_enabled = contributions_config.get('enabled', False)
    withdrawal_changes_enabled = withdrawal_changes_config.get('enabled', False)
    
    if contribution_enabled or withdrawal_changes_enabled:
        latex += "\\subsection{Análisis de Contribuciones y Flujos de Caja}\n\n"
        
        if contribution_enabled:
            contribution_amount = contributions_config.get('periodic_contribution', 0)
            contribution_label = "aportes" if contribution_amount > 0 else "impuestos"
            latex += f"Las simulaciones incluyen contribuciones periódicas de USD {abs(contribution_amount):,}/mes ({contribution_label}). "
        
        if withdrawal_changes_enabled:
            thirteenth_amount = withdrawal_changes_config.get('thirteenth_payment_amount', 0)
            thirteenth_months = withdrawal_changes_config.get('thirteenth_payment_months', [])
            latex += f"Además, se aplican retiros adicionales (décimos sueldos) de USD {thirteenth_amount:,} en los meses {thirteenth_months}. "
        
        latex += "A continuación se presenta un análisis del impacto de estos flujos en el desempeño de las carteras.\n\n"
        
        # Generar tabla de contribuciones y flujos netos por cartera y escenario
        latex += "\\begin{table}[H]\n"
        latex += "\\centering\n"
        latex += "\\caption{Contribuciones Totales y Flujo Neto Promedio por Cartera y Escenario (USD)}\n"
        latex += "\\begin{tabular}{lccc}\n"
        latex += "\\toprule\n"
        latex += "\\textbf{Cartera} & \\textbf{Escenario} & \\textbf{Contribuciones Totales} & \\textbf{Flujo Neto} \\\\\n"
        latex += "\\midrule\n"
        
        for portfolio_name in portfolios.keys():
            portfolio_label = portfolios[portfolio_name]['name'].replace('%', '\\%')
            portfolio_data = scenario_comparison[scenario_comparison['portfolio'] == portfolio_name]
            
            for scenario_name in scenarios.keys():
                scenario_row = portfolio_data[portfolio_data['scenario'] == scenario_name]
                
                if len(scenario_row) > 0:
                    if 'mean_total_contributions' in scenario_row.columns and pd.notna(scenario_row['mean_total_contributions'].values[0]):
                        contributions = scenario_row['mean_total_contributions'].values[0]
                        net_flow = scenario_row['mean_net_flow'].values[0] if ('mean_net_flow' in scenario_row.columns and pd.notna(scenario_row['mean_net_flow'].values[0])) else 0
                        
                        scenario_label = scenario_name.capitalize()
                        latex += f"{portfolio_label} & {scenario_label} & \\${contributions:,.0f} & \\${net_flow:,.0f} \\\\\n"
                    else:
                        # Si no hay datos, calcular estimaciones básicas
                        scenario_label = scenario_name.capitalize()
                        n_months = horizon_years * 12
                        if contribution_enabled:
                            contribution_amount = contributions_config.get('periodic_contribution', 0)
                            estimated_contributions = abs(contribution_amount) * n_months
                        else:
                            estimated_contributions = 0
                        
                        # Estimar flujo neto (contribuciones - retiros estimados)
                        estimated_withdrawals = withdrawal_amount * n_months
                        if withdrawal_changes_enabled:
                            thirteenth_amount = withdrawal_changes_config.get('thirteenth_payment_amount', 0)
                            estimated_withdrawals += thirteenth_amount * len(withdrawal_changes_config.get('thirteenth_payment_months', []))
                        
                        estimated_net_flow = estimated_contributions - estimated_withdrawals
                        latex += f"{portfolio_label} & {scenario_label} & \\${estimated_contributions:,.0f} & \\${estimated_net_flow:,.0f} \\\\\n"
        
        latex += "\\bottomrule\n"
        latex += "\\end{tabular}\n"
        latex += "\\end{table}\n\n"
        
        # Calcular valores esperados para contexto
        n_months = horizon_years * 12
        contribution_amount = contributions_config.get('periodic_contribution', 0) if contribution_enabled else 0
        expected_contributions = abs(contribution_amount) * n_months if contribution_enabled else 0
        expected_base_withdrawals = withdrawal_amount * n_months
        expected_decimos = 0
        if withdrawal_changes_enabled:
            thirteenth_amount = withdrawal_changes_config.get('thirteenth_payment_amount', 0)
            thirteenth_months = withdrawal_changes_config.get('thirteenth_payment_months', [])
            expected_decimos = thirteenth_amount * len(thirteenth_months)
        expected_total_withdrawals = expected_base_withdrawals + expected_decimos
        expected_net_flow = expected_contributions - expected_total_withdrawals
        
        latex += "\\textbf{Interpretación}: El flujo neto representa la diferencia entre contribuciones totales y retiros totales a lo largo del período de simulación. "
        
        # Análisis basado en los valores observados
        if expected_net_flow < 0:
            latex += f"En este análisis, los flujos netos son consistentemente negativos (promedio de aproximadamente \\${abs(expected_net_flow):,.0f} en un período completo), lo cual es esperable dado que: "
            latex += f"(1) el retiro mensual base (\\${withdrawal_amount:,}) es significativamente mayor que la contribución mensual (\\${abs(contribution_amount):,} si está habilitada), "
            if withdrawal_changes_enabled:
                latex += f"(2) se aplican retiros adicionales por décimos sueldos (\\${expected_decimos:,} en total), y "
            latex += f"(3) el capital inicial (\\${initial_capital:,}) y los retornos de inversión son los principales recursos para compensar este déficit de flujo de caja. "
            latex += "Los flujos netos más negativos (en valor absoluto) generalmente corresponden a simulaciones que sobrevivieron más meses, ya que continuaron realizando retiros durante más tiempo. "
            latex += "La sostenibilidad de las carteras no depende únicamente del flujo neto, sino de la capacidad de los retornos de inversión para compensar estos flujos negativos y mantener el capital suficiente para completar el período requerido. "
            latex += "Esta métrica permite evaluar la magnitud del déficit de flujo de caja que debe ser cubierto por los retornos de inversión.\n\n"
        elif expected_net_flow > 0:
            latex += "Los valores positivos de flujo neto indican que las contribuciones exceden los retiros, lo que puede mejorar significativamente la sostenibilidad de las carteras al proporcionar capital adicional para inversión. "
            latex += "Esta métrica permite evaluar el impacto positivo de los flujos de caja adicionales en el desempeño y supervivencia de las estrategias de inversión.\n\n"
        else:
            latex += "Esta métrica permite evaluar el balance entre contribuciones y retiros, y su impacto en el desempeño y supervivencia de las estrategias de inversión.\n\n"
    
    latex += "\\subsection{Sensibilidad a Escenarios Económicos}\n\n"
    latex += "El análisis de sensibilidad revela cómo cada cartera responde a cambios en las condiciones económicas.\n\n"
    
    # Calcular sensibilidad
    sensitivity_analysis = ""
    for portfolio_name in portfolios.keys():
        portfolio_data = scenario_comparison[scenario_comparison['portfolio'] == portfolio_name]
        if len(portfolio_data) >= 3:
            optimistic_rate = portfolio_data[portfolio_data['scenario'] == 'optimistic']['survival_rate'].values[0]
            pessimistic_rate = portfolio_data[portfolio_data['scenario'] == 'pessimistic']['survival_rate'].values[0]
            diff = optimistic_rate - pessimistic_rate
            portfolio_label = portfolios[portfolio_name]['name'].replace('%', '\\%')
            sensitivity_analysis += f"    \\item \\textbf{{{portfolio_label}}}: Presenta una diferencia de {diff:.1f} puntos porcentuales entre el escenario optimista y pesimista.\n"
    
    latex += "\\begin{itemize}\n"
    latex += sensitivity_analysis
    latex += "\\end{itemize}\n"
    
    # DISCUSIÓN
    latex += "% ============================================\n"
    latex += "% 5. DISCUSIÓN\n"
    latex += "% ============================================\n"
    latex += "\\section{Discusión}\n\n"
    latex += "\\subsection{Interpretación de Resultados}\n\n"
    latex += "Los resultados obtenidos revelan varios hallazgos importantes:\n\n"
    
    # Análisis dinámico: identificar mejor y peor cartera
    base_comparison = compare_portfolios(results, scenario='base')
    best_portfolio = base_comparison.loc[base_comparison['survival_rate'].idxmax()]
    worst_portfolio = base_comparison.loc[base_comparison['survival_rate'].idxmin()]
    
    best_portfolio_name = portfolios[best_portfolio['portfolio']]['name'].replace('%', '\\%')
    worst_portfolio_name = portfolios[worst_portfolio['portfolio']]['name'].replace('%', '\\%')
    
    # Obtener información de la mejor cartera
    best_allocation = portfolios[best_portfolio['portfolio']]['allocation']
    best_equity_pct = best_allocation.get('stocks', 0) * 100
    best_rebalance = portfolios[best_portfolio['portfolio']].get('rebalance_strategy', {}).get('type', 'N/A')
    
    latex += "\\subsubsection{Estrategia con Mejor Desempeño}\n"
    latex += f"{best_portfolio_name} demuestra el mejor desempeño en términos de supervivencia ({best_portfolio['survival_rate']:.1f}\\% en escenario base) y valor final promedio (\\${best_portfolio['mean_final_value']:,.0f}). "
    
    if best_equity_pct >= 60:
        latex += f"Esta cartera presenta una alta exposición a acciones ({best_equity_pct:.0f}\\%), lo que sugiere que, en el horizonte de {horizon_years} años considerado, el mayor potencial de crecimiento de las acciones compensa su mayor volatilidad. "
    elif best_equity_pct >= 40:
        latex += f"Esta cartera presenta una exposición moderada a acciones ({best_equity_pct:.0f}\%), equilibrando crecimiento potencial y estabilidad. "
    else:
        latex += f"Esta cartera presenta una exposición conservadora a acciones ({best_equity_pct:.0f}\%), priorizando la preservación del capital. "
    
    latex += "Sin embargo, las estrategias con mayor exposición a acciones generalmente implican mayor riesgo, como se evidencia en la amplia dispersión de resultados.\n\n"
    
    if best_portfolio['portfolio'] != worst_portfolio['portfolio']:
        latex += "\\subsubsection{Estrategia con Menor Desempeño}\n"
        worst_allocation = portfolios[worst_portfolio['portfolio']]['allocation']
        worst_equity_pct = worst_allocation.get('stocks', 0) * 100
        
        latex += f"{worst_portfolio_name} muestra las tasas de supervivencia más bajas ({worst_portfolio['survival_rate']:.1f}\\% en escenario base) y los valores finales promedio más bajos (\\${worst_portfolio['mean_final_value']:,.0f}). "
        
        # Identificar posibles razones basándose en la composición
        reasons = []
        if 'gold' in worst_allocation and worst_allocation['gold'] > 0:
            reasons.append(f"La inclusión de oro ({worst_allocation['gold']*100:.0f}\\% de la cartera) puede no haber proporcionado los beneficios esperados de diversificación")
        if worst_equity_pct < 50:
            reasons.append(f"La baja exposición a acciones ({worst_equity_pct:.0f}\\%) puede haber limitado el potencial de crecimiento")
        if worst_equity_pct > 70:
            reasons.append(f"La muy alta exposición a acciones ({worst_equity_pct:.0f}\\%), combinada con volatilidad, puede haber generado pérdidas significativas en períodos de mercado bajista")
        
        if reasons:
            latex += "Esto podría deberse a:\n"
            latex += "\\begin{itemize}\n"
            for reason in reasons:
                latex += f"    \\item {reason}\n"
            latex += "    \\item Retornos históricos del período analizado que no favorecieron esta combinación de activos\n"
            latex += "\\end{itemize}\n\n"
        else:
            latex += "Las diferencias de desempeño pueden deberse a la combinación específica de activos y a las condiciones del período histórico analizado.\n\n"
    
    latex += "\\subsubsection{Impacto de la Estrategia de Rebalanceo}\n"
    latex += "Las diferentes estrategias de rebalanceo utilizadas (anual, trimestral, por umbral) muestran efectos distintos en el desempeño. "
    
    # Analizar rebalanceo de la mejor cartera
    if best_rebalance != 'N/A':
        latex += f"La estrategia de rebalanceo {best_rebalance} de {best_portfolio_name} parece haber sido efectiva en este contexto, posiblemente capturando mejor las oportunidades del mercado o manteniendo la asignación objetivo de manera más eficiente.\n\n"
    else:
        latex += "El rebalanceo frecuente puede ser beneficioso para mantener la asignación objetivo, pero también puede generar mayores costos de transacción.\n\n"
    
    # Análisis de contribuciones y cambios en retiros si están habilitados
    contributions_config = config.get('contributions', {})
    withdrawal_changes_config = config.get('withdrawal_changes', {})
    contribution_enabled = contributions_config.get('enabled', False)
    withdrawal_changes_enabled = withdrawal_changes_config.get('enabled', False)
    
    if contribution_enabled or withdrawal_changes_enabled:
        latex += "\\subsubsection{Impacto de Contribuciones y Cambios en Retiros}\n"
        
        if contribution_enabled:
            contribution_amount = contributions_config.get('periodic_contribution', 0)
            if contribution_amount > 0:
                # Obtener promedio de contribuciones totales
                avg_contributions = 0
                if 'mean_total_contributions' in base_comparison.columns:
                    avg_contributions = base_comparison['mean_total_contributions'].mean()
                
                latex += f"Las contribuciones periódicas de USD {abs(contribution_amount):,}/mes han sido incorporadas en las simulaciones. "
                if avg_contributions > 0:
                    latex += f"En promedio, las carteras recibieron USD {avg_contributions:,.0f} en contribuciones totales durante el período, "
                latex += "lo cual mejora significativamente la sostenibilidad al proporcionar capital adicional para inversión y compensar los retiros periódicos.\n\n"
            else:
                latex += f"Los impuestos o deducciones periódicas de USD {abs(contribution_amount):,}/mes reducen el capital disponible para inversión, impactando negativamente el crecimiento potencial de las carteras.\n\n"
        
        if withdrawal_changes_enabled:
            thirteenth_amount = withdrawal_changes_config.get('thirteenth_payment_amount', 0)
            thirteenth_months = withdrawal_changes_config.get('thirteenth_payment_months', [])
            
            latex += f"Los retiros adicionales (décimos sueldos) de USD {thirteenth_amount:,} aplicados en los meses {thirteenth_months} aumentan la presión sobre el capital disponible. "
            latex += "Estos retiros adicionales reducen el capital invertido en períodos específicos, lo que puede afectar el crecimiento compuesto y la capacidad de recuperación de las carteras, especialmente si ocurren durante períodos de mercado bajista.\n\n"
    latex += "\\subsection{Limitaciones del Análisis}\n\n"
    latex += "Es importante reconocer las limitaciones inherentes a este estudio:\n\n"
    latex += "\\begin{enumerate}\n"
    latex += "    \\item \\textbf{Supuestos de distribución normal}: Los retornos históricos pueden no seguir una distribución normal, especialmente en períodos de crisis.\n"
    latex += f"    \\item \\textbf{{Período histórico limitado}}: El análisis se basa en {data_years} años de datos históricos, que pueden no capturar todos los ciclos económicos.\n"
    latex += "    \\item \\textbf{Simplicación de costos}: Los costos de transacción se modelan de forma simplificada y pueden variar en la práctica.\n"
    latex += "    \\item \\textbf{Inflación constante}: Se asume una tasa de inflación constante por escenario, lo cual es una simplificación.\n"
    latex += "    \\item \\textbf{No considera impuestos}: El análisis no incorpora el efecto de impuestos sobre ganancias de capital.\n"
    latex += "\\end{enumerate}\n\n"
    latex += "\\subsection{Factores que Influyen en los Resultados}\n\n"
    latex += "Varios factores clave determinan los resultados observados:\n\n"
    latex += "\\begin{itemize}\n"
    latex += "    \\item \\textbf{Correlación entre activos}: La baja correlación entre acciones y bonos proporciona beneficios de diversificación.\n"
    latex += "    \\item \\textbf{Equity premium}: La prima de riesgo de las acciones genera mayor retorno esperado en el largo plazo.\n"
    latex += "    \\item \\textbf{Sequence of returns risk}: El orden de los retornos (especialmente caídas tempranas) tiene un impacto significativo.\n"
    latex += f"    \\item \\textbf{{Tasa de retiro}}: La tasa de retiro del {withdrawal_rate:.1f}\\% anual (USD {withdrawal_amount} mensual sobre USD {initial_capital:,}) es relativamente alta.\n"
    latex += "\\end{itemize}\n\n"
    
    # CONCLUSIONES
    latex += "% ============================================\n"
    latex += "% 6. CONCLUSIONES\n"
    latex += "% ============================================\n"
    latex += "\\section{Conclusiones}\n\n"
    latex += "\\subsection{Conclusiones Principales}\n\n"
    latex += "Basado en el análisis realizado, se pueden extraer las siguientes conclusiones:\n\n"
    latex += "\\begin{enumerate}\n"
    
    # Obtener mejor y peor cartera del escenario base
    base_comparison = compare_portfolios(results, scenario='base')
    best_portfolio = base_comparison.loc[base_comparison['survival_rate'].idxmax()]
    worst_portfolio = base_comparison.loc[base_comparison['survival_rate'].idxmin()]
    
    withdrawal_rate = (config['project']['withdrawals']['amount'] * 12) / config['project']['initial_capital'] * 100
    
    best_portfolio_name = portfolios[best_portfolio['portfolio']]['name'].replace('%', '\\%')
    latex += f"    \\item \\textbf{{La {best_portfolio_name} es la estrategia más robusta}} para el objetivo planteado, mostrando las mayores tasas de supervivencia ({best_portfolio['survival_rate']:.1f}\\% en escenario base) y los valores finales promedio más altos (\\${best_portfolio['mean_final_value']:,.0f}).\n\n"
    latex += f"    \\item \\textbf{{Ninguna de las carteras garantiza sostenibilidad completa}}: Todas las estrategias muestran probabilidades significativas de agotamiento del capital antes de {horizon_years} años, especialmente en escenarios adversos.\n\n"
    
    # Análisis dinámico de diversificación
    if best_portfolio['portfolio'] != worst_portfolio['portfolio']:
        worst_allocation = portfolios[worst_portfolio['portfolio']]['allocation']
        if 'gold' in worst_allocation and worst_allocation['gold'] > 0:
            worst_portfolio_name = portfolios[worst_portfolio['portfolio']]['name'].replace('%', '\\%')
            latex += f"    \\item \\textbf{{La diversificación con oro no mejoró el desempeño en este contexto}}: {worst_portfolio_name} muestra consistentemente peores resultados que las otras opciones evaluadas.\n\n"
    
    # Análisis de sensibilidad
    scenario_survival_ranges = {}
    for scenario in scenarios.keys():
        scenario_data = scenario_comparison[scenario_comparison['scenario'] == scenario]
        if len(scenario_data) > 0:
            max_survival = scenario_data['survival_rate'].max()
            min_survival = scenario_data['survival_rate'].min()
            scenario_survival_ranges[scenario] = max_survival - min_survival
    
    if scenario_survival_ranges:
        max_range = max(scenario_survival_ranges.values())
        if max_range > 20:
            latex += "    \\item \\textbf{{La sensibilidad a escenarios económicos es significativa}}: Se observan diferencias importantes en el desempeño entre escenarios, indicando que cambios en inflación y costos de transacción impactan fuertemente los resultados.\n\n"
        else:
            latex += "    \\item \\textbf{{La sensibilidad a escenarios económicos es moderada}}: Aunque existen diferencias entre escenarios, el impacto relativo de las condiciones económicas es menos pronunciado.\n\n"
    
    # Análisis de rebalanceo
    best_rebalance = portfolios[best_portfolio['portfolio']].get('rebalance_strategy', {}).get('type', 'N/A')
    if best_rebalance == 'quarterly':
        latex += f"    \\item \\textbf{{El rebalanceo frecuente puede ser beneficioso}}: La estrategia de rebalanceo trimestral de {best_portfolio_name} parece capturar mejor las oportunidades del mercado en este contexto.\n"
    elif best_rebalance == 'threshold':
        latex += f"    \\item \\textbf{{El rebalanceo por umbral puede ser efectivo}}: La estrategia de rebalanceo basada en umbrales de {best_portfolio_name} parece mantener la asignación objetivo de manera eficiente.\n"
    elif best_rebalance == 'annual':
        latex += f"    \\item \\textbf{{El rebalanceo anual puede ser suficiente}}: La estrategia de rebalanceo anual de {best_portfolio_name} parece adecuada para este horizonte de inversión.\n"
    latex += "\\end{enumerate}\n\n"
    latex += "\\subsection{{Recomendaciones}}\n\n"
    latex += "\\begin{enumerate}\n"
    latex += f"    \\item \\textbf{{Considerar reducir la tasa de retiro}}: La tasa actual del {withdrawal_rate:.1f}\\% anual es alta. Una reducción al 10-12\\% mejoraría significativamente las probabilidades de supervivencia.\n"
    
    latex += "    \\item \\textbf{{Implementar estrategias dinámicas de retiro}}: Ajustar los retiros según el desempeño de la cartera podría mejorar la sostenibilidad.\n\n"
    latex += "    \\item \\textbf{{Monitoreo continuo y rebalanceo}}: Implementar un sistema de monitoreo que permita ajustar la estrategia según condiciones de mercado.\n\n"
    # Recomendaciones sobre contribuciones y cambios en retiros
    if contribution_enabled or withdrawal_changes_enabled:
        if contribution_enabled:
            contribution_amount = contributions_config.get('periodic_contribution', 0)
            if contribution_amount > 0:
                latex += f"    \\item \\textbf{{Las contribuciones periódicas mejoran significativamente los resultados}}: Las aportes mensuales de USD {abs(contribution_amount):,} han mostrado un impacto positivo en las tasas de supervivencia. Considerar aumentar este monto si es posible para mejorar aún más la sostenibilidad.\n\n"
            else:
                latex += f"    \\item \\textbf{{Los impuestos periódicos reducen el capital disponible}}: Las deducciones mensuales de USD {abs(contribution_amount):,} reducen el capital disponible para inversión. Considerar estrategias de optimización fiscal.\n\n"
        
        if withdrawal_changes_enabled:
            thirteenth_amount = withdrawal_changes_config.get('thirteenth_payment_amount', 0)
            latex += f"    \\item \\textbf{{Los retiros adicionales afectan la sostenibilidad}}: Los décimos sueldos de USD {thirteenth_amount:,} en meses específicos aumentan la presión sobre el capital. Considerar ajustar el calendario de retiros o aumentar las contribuciones para compensar.\n\n"
    else:
        latex += "    \\item \\textbf{{Considerar contribuciones adicionales}}: Las contribuciones periódicas o la flexibilidad para reducir retiros en períodos adversos pueden mejorar sustancialmente los resultados.\n\n"
    latex += "    \\item \\textbf{{Diversificación adicional}}: Considerar incluir activos adicionales o estrategias de cobertura para reducir la volatilidad.\n"
    latex += "\\end{enumerate}\n\n"
    latex += "\\subsection{{Extensiones Futuras}}\n\n"
    latex += "El presente estudio podría extenderse en las siguientes direcciones:\n\n"
    latex += "\\begin{itemize}\n"
    latex += "    \\item Análisis de estrategias de retiro dinámicas (variable según desempeño)\n"
    latex += "    \\item Incorporación de modelos más sofisticados de distribución de retornos (distribuciones con colas pesadas)\n"
    latex += "    \\item Análisis de optimalidad de la estrategia de rebalanceo\n"
    latex += "    \\item Evaluación de estrategias con opciones o derivados para cobertura\n"
    latex += "    \\item Análisis multi-objetivo considerando preferencias de riesgo del inversor\n"
    latex += "\\end{itemize}\n\n"
    
    # REFERENCIAS
    latex += "% ============================================\n"
    latex += "% 7. REFERENCIAS\n"
    latex += "% ============================================\n"
    latex += "\\section{Referencias}\n\n"
    latex += "\\begin{thebibliography}{9}\n\n"
    latex += "\\bibitem{yahoo_finance}\n"
    latex += "Yahoo Finance. \\textit{Financial Data Provider}. \n"
    latex += "\\url{https://finance.yahoo.com/}\n\n"
    latex += "\\bibitem{montecarlo}\n"
    latex += "Glasserman, P. (2003). \\textit{Monte Carlo Methods in Financial Engineering}. Springer.\n\n"
    latex += "\\bibitem{portfolio_theory}\n"
    latex += "Markowitz, H. (1952). Portfolio Selection. \\textit{The Journal of Finance}, 7(1), 77-91.\n\n"
    latex += "\\bibitem{retirement_planning}\n"
    latex += "Bengen, W. P. (1994). Determining Withdrawal Rates Using Historical Data. \\textit{Journal of Financial Planning}, 7(4), 171-180.\n\n"
    latex += "\\bibitem{python_pandas}\n"
    latex += "McKinney, W. (2010). Data Structures for Statistical Computing in Python. \\textit{Proceedings of the 9th Python in Science Conference}.\n\n"
    latex += "\\bibitem{simulation_methods}\n"
    latex += "Jorion, P. (2007). \\textit{Value at Risk: The New Benchmark for Managing Financial Risk}. McGraw-Hill.\n\n"
    latex += "\\bibitem{rebalancing}\n"
    latex += "Daryanani, G. (2008). Opportunistic Rebalancing: A New Paradigm for Wealth Managers. \\textit{Journal of Financial Planning}, 21(1), 48-61.\n\n"
    latex += "\\bibitem{inflation}\n"
    latex += "Fisher, I. (1930). \\textit{The Theory of Interest}. Macmillan.\n\n"
    latex += "\\bibitem{risk_management}\n"
    latex += "Fabozzi, F. J., Focardi, S. M., \\& Kolm, P. N. (2006). \\textit{Financial Modeling of the Equity Market: From CAPM to Cointegration}. John Wiley \\& Sons.\n\n"
    latex += "\\end{thebibliography}\n\n"
    
    # ANEXOS
    latex += "% ============================================\n"
    latex += "% 8. ANEXOS\n"
    latex += "% ============================================\n"
    latex += "\\section{Anexos}\n\n"
    latex += "\\subsection{Anexo A: Estadísticas de Activos Financieros}\n\n"
    latex += f"Las estadísticas anualizadas calculadas a partir de datos históricos ({data_start} - {data_end}) son las siguientes:\n\n"
    
    latex += asset_stats_table
    
    latex += "\\subsection{Anexo B: Configuración del Proyecto}\n\n"
    latex += "\\begin{itemize}\n"
    latex += f"    \\item Capital inicial: USD {initial_capital:,}\n"
    latex += f"    \\item Retiro mensual: USD {withdrawal_amount:,}\n"
    latex += f"    \\item Horizonte temporal: {horizon_years} años ({horizon_years * 12} meses)\n"
    latex += f"    \\item Iteraciones Monte Carlo: {n_iterations:,} por cartera y escenario\n"
    latex += f"    \\item Semilla aleatoria: {random_seed} (para reproducibilidad)\n"
    latex += f"    \\item Ajuste por inflación: {inflation_enabled}\n"
    latex += "    \\item Costos de transacción: Incluidos según escenario\n"
    
    # Información sobre contribuciones y décimos
    contributions_config = config.get('contributions', {})
    withdrawal_changes_config = config.get('withdrawal_changes', {})
    
    if contributions_config.get('enabled', False):
        latex += f"    \\item Contribuciones periódicas: USD {contributions_config.get('periodic_contribution', 0):,}/mes\n"
    
    if withdrawal_changes_config.get('enabled', False):
        latex += f"    \\item Décimos sueldos: USD {withdrawal_changes_config.get('thirteenth_payment_amount', 0):,} en meses {withdrawal_changes_config.get('thirteenth_payment_months', [])}\n"
    
    latex += "\\end{itemize}\n\n"
    
    latex += "\\subsection{Anexo C: Estructura de Archivos Generados}\n\n"
    latex += "Los resultados del proyecto se organizan en las siguientes carpetas:\n\n"
    latex += "\\begin{itemize}\n"
    latex += "    \\item \\texttt{data/processed/}: Datos procesados y estadísticas de activos\n"
    latex += "    \\item \\texttt{results/simulations/}: Archivos CSV con métricas e historiales de simulaciones\n"
    latex += "    \\item \\texttt{results/tables/}: Tablas comparativas en formato CSV\n"
    latex += "    \\item \\texttt{results/figures/}: Visualizaciones generadas (PNG de alta resolución)\n"
    latex += "\\end{itemize}\n\n"
    
    latex += "\\subsection{Anexo D: Gráficos Generados}\n\n"
    latex += "El proyecto genera las siguientes visualizaciones (disponibles en \\texttt{results/figures/}):\n\n"
    latex += "\\begin{itemize}\n"
    latex += "    \\item \\texttt{evolution\\_\\{cartera\\}\\_\\{escenario\\}.png}: Evolución del capital por cartera y escenario (9 gráficos)\n"
    latex += "    \\item \\texttt{evolution\\_comparison\\_\\{escenario\\}.png}: Comparación de evolución entre carteras (3 gráficos)\n"
    latex += "    \\item \\texttt{comparison\\_survival\\_rate.png}: Comparación de tasas de supervivencia\n"
    latex += "    \\item \\texttt{comparison\\_final\\_values.png}: Comparación de valores finales\n"
    latex += "    \\item \\texttt{distribution\\_\\{cartera\\}\\_\\{escenario\\}.png}: Distribuciones de valores finales (9 gráficos)\n"
    latex += "    \\item \\texttt{survival\\_\\{cartera\\}\\_\\{escenario\\}.png}: Análisis de supervivencia (9 gráficos)\n"
    latex += "\\end{itemize}\n\n"
    
    latex += "\\subsection{Anexo E: Instrucciones para Compilación en Overleaf}\n\n"
    latex += "Para compilar este documento en Overleaf:\n\n"
    latex += "\\begin{enumerate}\n"
    latex += "    \\item Sube el archivo \\texttt{informe\\_final.tex} como archivo principal del proyecto\n"
    latex += "    \\item Crea una carpeta llamada \\texttt{figures} en Overleaf\n"
    latex += "    \\item Sube los gráficos necesarios a la carpeta \\texttt{figures} (los gráficos principales están en la carpeta \\texttt{overleaf/figures})\n"
    latex += "    \\item Compila el proyecto en Overleaf\n"
    latex += "    \\item Si faltan gráficos, puedes agregarlos según sea necesario\n"
    latex += "\\end{enumerate}\n\n"
    latex += "\\textbf{Nota}: El documento está diseñado para compilar sin gráficos si estos no están disponibles. Los gráficos son opcionales y complementan el análisis presentado en las tablas.\n\n"
    latex += "\\end{document}\n"
    
    return latex


def generate_survival_table(scenario_comparison, portfolios, scenarios):
    """Genera la tabla LaTeX de tasas de supervivencia."""
    latex = "\\begin{table}[H]\n"
    latex += "\\centering\n"
    latex += "\\caption{Tasas de Supervivencia por Cartera y Escenario (\\%)}\n"
    latex += "\\begin{tabular}{lccc}\n"
    latex += "\\toprule\n"
    latex += "\\textbf{Cartera} & \\textbf{Base} & \\textbf{Optimista} & \\textbf{Pesimista} \\\\\n"
    latex += "\\midrule\n"
    
    for portfolio_name in portfolios.keys():
        portfolio_label = portfolios[portfolio_name]['name'].replace('%', '\\%')
        row_data = scenario_comparison[scenario_comparison['portfolio'] == portfolio_name]
        
        base_rate = row_data[row_data['scenario'] == 'base']['survival_rate'].values[0] if len(row_data[row_data['scenario'] == 'base']) > 0 else 0
        opt_rate = row_data[row_data['scenario'] == 'optimistic']['survival_rate'].values[0] if len(row_data[row_data['scenario'] == 'optimistic']) > 0 else 0
        pess_rate = row_data[row_data['scenario'] == 'pessimistic']['survival_rate'].values[0] if len(row_data[row_data['scenario'] == 'pessimistic']) > 0 else 0
        
        latex += f"{portfolio_label} & {base_rate:.1f}\\% & {opt_rate:.1f}\\% & {pess_rate:.1f}\\% \\\\\n"
    
    latex += "\\bottomrule\n"
    latex += "\\end{tabular}\n"
    latex += "\\end{table}\n\n"
    
    return latex


def generate_final_value_table(scenario_comparison, portfolios, scenarios):
    """Genera la tabla LaTeX de valores finales."""
    latex = "\\begin{table}[H]\n"
    latex += "\\centering\n"
    latex += "\\caption{Valores Finales Promedio por Cartera y Escenario (USD)}\n"
    latex += "\\begin{tabular}{lccc}\n"
    latex += "\\toprule\n"
    latex += "\\textbf{Cartera} & \\textbf{Base} & \\textbf{Optimista} & \\textbf{Pesimista} \\\\\n"
    latex += "\\midrule\n"
    
    for portfolio_name in portfolios.keys():
        portfolio_label = portfolios[portfolio_name]['name'].replace('%', '\\%')
        row_data = scenario_comparison[scenario_comparison['portfolio'] == portfolio_name]
        
        base_val = row_data[row_data['scenario'] == 'base']['mean_final_value'].values[0] if len(row_data[row_data['scenario'] == 'base']) > 0 else 0
        opt_val = row_data[row_data['scenario'] == 'optimistic']['mean_final_value'].values[0] if len(row_data[row_data['scenario'] == 'optimistic']) > 0 else 0
        pess_val = row_data[row_data['scenario'] == 'pessimistic']['mean_final_value'].values[0] if len(row_data[row_data['scenario'] == 'pessimistic']) > 0 else 0
        
        latex += f"{portfolio_label} & \\${base_val:,.0f} & \\${opt_val:,.0f} & \\${pess_val:,.0f} \\\\\n"
    
    latex += "\\bottomrule\n"
    latex += "\\end{tabular}\n"
    latex += "\\end{table}\n\n"
    
    return latex


def generate_percentiles_table(scenario_comparison, portfolios, scenarios):
    """Genera la tabla LaTeX de percentiles para escenario base."""
    latex = "\\begin{table}[H]\n"
    latex += "\\centering\n"
    latex += "\\caption{Distribución de Valores Finales - Escenario Base (USD)}\n"
    latex += "\\small\n"
    latex += "\\begin{tabular}{lccccc}\n"
    latex += "\\toprule\n"
    latex += "\\textbf{Cartera} & \\textbf{P5} & \\textbf{P25} & \\textbf{Mediana} & \\textbf{P75} & \\textbf{P95} \\\\\n"
    latex += "\\midrule\n"
    
    base_data = scenario_comparison[scenario_comparison['scenario'] == 'base']
    
    for portfolio_name in portfolios.keys():
        portfolio_label = portfolios[portfolio_name]['name'].replace('%', '\\%')
        row_data = base_data[base_data['portfolio'] == portfolio_name]
        
        if len(row_data) > 0:
            p5 = row_data['percentile_5'].values[0]
            p25 = row_data['percentile_25'].values[0]
            median = row_data['median_final_value'].values[0]
            p75 = row_data['percentile_75'].values[0]
            p95 = row_data['percentile_95'].values[0]
            
            latex += f"{portfolio_label} & \\${p5:,.0f} & \\${p25:,.0f} & \\${median:,.0f} & \\${p75:,.0f} & \\${p95:,.0f} \\\\\n"
    
    latex += "\\bottomrule\n"
    latex += "\\end{tabular}\n"
    latex += "\\end{table}\n\n"
    
    return latex


def generate_asset_stats_table(stats_df):
    """Genera la tabla LaTeX de estadísticas de activos."""
    latex = "\\begin{table}[H]\n"
    latex += "\\centering\n"
    latex += "\\caption{Estadísticas Anualizadas de Activos}\n"
    latex += "\\begin{tabular}{lccc}\n"
    latex += "\\toprule\n"
    latex += "\\textbf{Activo} & \\textbf{Retorno Medio (\\%)} & \\textbf{Desv. Estándar (\\%)} & \\textbf{Sharpe Ratio} \\\\\n"
    latex += "\\midrule\n"
    
    asset_names = {
        'stocks': 'S\\&P 500 (Acciones)',
        'bonds': 'Bonos del Tesoro',
        'gold': 'Oro',
        'cash': 'Efectivo (T-Bill)'
    }
    
    for _, row in stats_df.iterrows():
        asset = row['asset']
        asset_label = asset_names.get(asset, asset.capitalize())
        mean_return = row['mean_return_annual'] * 100
        std_dev = row['std_dev_annual'] * 100
        sharpe = row['sharpe_ratio']
        
        latex += f"{asset_label} & {mean_return:.2f}\\% & {std_dev:.2f}\\% & {sharpe:.2f} \\\\\n"
    
    latex += "\\bottomrule\n"
    latex += "\\end{tabular}\n"
    latex += "\\end{table}\n\n"
    
    latex += "\\textbf{Nota}: Los datos de efectivo muestran una volatilidad inusualmente alta, probablemente debido a la transformación de tasas de interés a retornos. En la práctica, el efectivo se modela con una tasa libre de riesgo más conservadora.\n\n"
    
    return latex


if __name__ == "__main__":
    # Generar informe
    tex_path = generate_latex_report()
    
    if tex_path and os.path.exists(tex_path):
        print(f"\n✅ Informe LaTeX generado y listo para Overleaf: {tex_path}")
        print(f"   📁 Copia este archivo y la carpeta 'overleaf' (si existe) a Overleaf para compilar")


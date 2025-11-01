"""
Módulo para descarga y procesamiento de datos financieros.
"""

import os
import yfinance as yf
import pandas as pd
import numpy as np
import yaml
from pathlib import Path


def load_config(config_path="config/settings.yaml"):
    """Carga la configuración desde el archivo YAML."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def download_data(config):
    """
    Descarga datos históricos de Yahoo Finance.
    
    Args:
        config: Diccionario con la configuración del proyecto
        
    Returns:
        dict: Diccionario con DataFrames de precios por activo
    """
    assets = config['assets']
    data_source = config['data_source']
    
    # Crear directorio si no existe
    os.makedirs(data_source['download_path'], exist_ok=True)
    
    prices = {}
    
    for asset_type, asset_info in assets.items():
        ticker = asset_info['ticker']
        name = asset_info['name']
        
        print(f"Descargando {name} ({ticker})...")
        
        try:
            # Descargar datos
            ticker_obj = yf.Ticker(ticker)
            df = ticker_obj.history(
                start=data_source['start_date'],
                end=data_source['end_date'],
                interval=data_source['interval']
            )
            
            if df.empty:
                print(f"  ⚠️  No se obtuvieron datos para {ticker}")
                continue
            
            # Guardar datos crudos
            filename = f"{asset_type}_{ticker.replace('^', '').replace('=', '_')}.csv"
            filepath = os.path.join(data_source['download_path'], filename)
            df.to_csv(filepath)
            
            prices[asset_type] = df['Close']
            print(f"  ✅ Datos descargados: {len(df)} registros")
            
        except Exception as e:
            print(f"  ❌ Error descargando {ticker}: {str(e)}")
            continue
    
    return prices


def calculate_returns(prices_dict):
    """
    Calcula retornos logarítmicos desde precios.
    
    Args:
        prices_dict: Diccionario con Series de precios por activo
        
    Returns:
        dict: Diccionario con Series de retornos por activo
    """
    returns = {}
    
    for asset_type, prices in prices_dict.items():
        # Calcular retornos logarítmicos
        log_returns = np.log(prices / prices.shift(1)).dropna()
        returns[asset_type] = log_returns
    
    return returns


def consolidate_returns(returns_df):
    """
    Consolida retornos que pueden tener múltiples entradas por fecha.
    Combina filas con misma fecha tomando el primer valor no-NaN para cada columna.
    
    Args:
        returns_df: DataFrame con retornos que puede tener duplicados por fecha
        
    Returns:
        pd.DataFrame: DataFrame consolidado con una fila por fecha
    """
    # Asegurar que el índice es DatetimeIndex
    if not isinstance(returns_df.index, pd.DatetimeIndex):
        returns_df.index = pd.to_datetime(returns_df.index)
    
    # Agrupar por fecha (solo la fecha, sin hora)
    # Para cada columna, tomar el primer valor no-NaN
    consolidated = returns_df.groupby(returns_df.index.date).agg({
        col: lambda x: x.dropna().iloc[0] if len(x.dropna()) > 0 else np.nan
        for col in returns_df.columns
    })
    
    # Convertir el índice de vuelta a DatetimeIndex
    consolidated.index = pd.to_datetime(consolidated.index)
    
    return consolidated


def calculate_statistics(returns_dict):
    """
    Calcula estadísticas anualizadas (media y desviación estándar).
    
    Args:
        returns_dict: Diccionario con Series de retornos por activo
        
    Returns:
        pd.DataFrame: DataFrame con estadísticas anualizadas
    """
    stats_list = []
    
    for asset_type, returns in returns_dict.items():
        # Calcular estadísticas diarias
        mean_daily = returns.mean()
        std_daily = returns.std()
        
        # Anualizar (252 días de trading)
        trading_days = 252
        mean_annual = mean_daily * trading_days
        std_annual = std_daily * np.sqrt(trading_days)
        
        stats_list.append({
            'asset': asset_type,
            'mean_return_annual': mean_annual,
            'std_dev_annual': std_annual,
            'sharpe_ratio': mean_annual / std_annual if std_annual > 0 else 0,
            'observations': len(returns)
        })
    
    stats_df = pd.DataFrame(stats_list)
    return stats_df


def process_data(config_path="config/settings.yaml"):
    """
    Función principal que ejecuta todo el pipeline de procesamiento.
    
    Args:
        config_path: Ruta al archivo de configuración
    """
    # Cargar configuración
    config = load_config(config_path)
    
    print("=" * 60)
    print("📊 PROCESAMIENTO DE DATOS FINANCIEROS")
    print("=" * 60)
    
    # Descargar datos
    print("\n1. Descargando datos históricos...")
    prices = download_data(config)
    
    if not prices:
        print("❌ No se pudieron descargar datos. Abortando.")
        return
    
    # Calcular retornos
    print("\n2. Calculando retornos...")
    returns = calculate_returns(prices)
    
    # Guardar retornos procesados
    os.makedirs(config['data_source']['processed_path'], exist_ok=True)
    returns_df = pd.DataFrame(returns)
    
    # Consolidar retornos por fecha (eliminar duplicados y NaN innecesarios)
    print("  Consolidando retornos por fecha...")
    returns_df_consolidated = consolidate_returns(returns_df)
    
    returns_path = os.path.join(
        config['data_source']['processed_path'], 
        'returns.csv'
    )
    returns_df_consolidated.to_csv(returns_path)
    
    # Verificar calidad de datos
    total_nan = returns_df_consolidated.isna().sum().sum()
    total_values = returns_df_consolidated.size
    nan_percentage = (total_nan / total_values * 100) if total_values > 0 else 0
    
    print(f"  ✅ Retornos guardados en {returns_path}")
    print(f"  📊 Datos consolidados: {len(returns_df_consolidated)} días únicos")
    print(f"  📊 Valores faltantes: {total_nan} ({nan_percentage:.2f}%)")
    
    if nan_percentage > 5:
        print(f"  ⚠️  Advertencia: Alto porcentaje de valores faltantes. Revisar datos.")
    
    # Calcular estadísticas
    print("\n3. Calculando estadísticas anualizadas...")
    stats = calculate_statistics(returns)
    
    # Guardar estadísticas
    stats_path = os.path.join(
        config['data_source']['processed_path'],
        'asset_statistics.csv'
    )
    stats.to_csv(stats_path, index=False)
    print(f"  ✅ Estadísticas guardadas en {stats_path}")
    print("\n" + "=" * 60)
    print("📈 ESTADÍSTICAS ANUALIZADAS")
    print("=" * 60)
    print(stats.to_string(index=False))
    print("=" * 60)
    
    return prices, returns, stats


if __name__ == "__main__":
    process_data()



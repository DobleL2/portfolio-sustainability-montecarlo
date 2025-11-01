"""
Módulo para implementar estrategias de rebalanceo de cartera.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class RebalanceStrategy:
    """Clase base para estrategias de rebalanceo."""
    
    def __init__(self, target_allocation, transaction_cost=0.002):
        """
        Args:
            target_allocation: dict con las asignaciones objetivo (stocks, bonds, gold, cash)
            transaction_cost: costo de transacción como proporción del valor rebalanceado
        """
        self.target_allocation = target_allocation
        self.transaction_cost = transaction_cost
        self.last_rebalance_date = None
    
    def should_rebalance(self, current_allocation, date, portfolio_value):
        """
        Determina si se debe rebalancear.
        
        Args:
            current_allocation: dict con asignaciones actuales
            date: fecha actual (datetime)
            portfolio_value: valor total de la cartera
            
        Returns:
            bool: True si se debe rebalancear
        """
        raise NotImplementedError
    
    def calculate_rebalance_cost(self, target_allocation, current_allocation, portfolio_value):
        """
        Calcula el costo de transacción del rebalanceo.
        
        Args:
            target_allocation: asignaciones objetivo
            current_allocation: asignaciones actuales
            portfolio_value: valor total de la cartera
            
        Returns:
            float: costo de transacción
        """
        # Calcular el cambio en cada activo
        total_change = 0
        for asset in target_allocation:
            change = abs(target_allocation[asset] - current_allocation.get(asset, 0))
            total_change += change
        
        # Costo es proporcional al cambio total
        cost = portfolio_value * (total_change / 2) * self.transaction_cost
        return cost
    
    def rebalance(self, current_values, portfolio_value):
        """
        Rebalancea la cartera según las asignaciones objetivo.
        
        Args:
            current_values: dict con valores actuales por activo
            portfolio_value: valor total de la cartera
            
        Returns:
            dict: nuevos valores después del rebalanceo
            float: costo de transacción
        """
        # Calcular asignaciones actuales
        current_allocation = {
            asset: value / portfolio_value if portfolio_value > 0 else 0
            for asset, value in current_values.items()
        }
        
        # Calcular nuevos valores objetivo
        new_values = {
            asset: portfolio_value * target
            for asset, target in self.target_allocation.items()
        }
        
        # Calcular costo
        cost = self.calculate_rebalance_cost(
            self.target_allocation, 
            current_allocation, 
            portfolio_value
        )
        
        # Aplicar costo
        remaining_value = portfolio_value - cost
        new_values = {
            asset: remaining_value * target
            for asset, target in self.target_allocation.items()
        }
        
        return new_values, cost


class TimeBasedRebalance(RebalanceStrategy):
    """Estrategia de rebalanceo basada en tiempo (mensual, trimestral, anual)."""
    
    def __init__(self, target_allocation, frequency="annual", transaction_cost=0.002):
        """
        Args:
            target_allocation: dict con asignaciones objetivo
            frequency: frecuencia de rebalanceo ("monthly", "quarterly", "annual")
            transaction_cost: costo de transacción
        """
        super().__init__(target_allocation, transaction_cost)
        self.frequency = frequency
        
        # Mapeo de frecuencia a días
        self.frequency_days = {
            "monthly": 30,
            "quarterly": 90,
            "annual": 365
        }
    
    def should_rebalance(self, current_allocation, date, portfolio_value):
        """Determina si es momento de rebalancear según la frecuencia."""
        if self.last_rebalance_date is None:
            self.last_rebalance_date = date
            return True
        
        days_since_rebalance = (date - self.last_rebalance_date).days
        
        if days_since_rebalance >= self.frequency_days.get(self.frequency, 365):
            self.last_rebalance_date = date
            return True
        
        return False


class ThresholdBasedRebalance(RebalanceStrategy):
    """Estrategia de rebalanceo basada en umbral de desviación."""
    
    def __init__(self, target_allocation, threshold=0.05, transaction_cost=0.002):
        """
        Args:
            target_allocation: dict con asignaciones objetivo
            threshold: umbral de desviación (ej: 0.05 = 5%)
            transaction_cost: costo de transacción
        """
        super().__init__(target_allocation, transaction_cost)
        self.threshold = threshold
    
    def should_rebalance(self, current_allocation, date, portfolio_value):
        """Determina si alguna asignación se desvió más del umbral."""
        for asset, target in self.target_allocation.items():
            current = current_allocation.get(asset, 0)
            deviation = abs(current - target)
            
            if deviation > self.threshold:
                return True
        
        return False


def create_rebalance_strategy(portfolio_config, transaction_cost=0.002):
    """
    Factory function para crear estrategia de rebalanceo según configuración.
    
    Args:
        portfolio_config: dict con configuración de la cartera del YAML
        transaction_cost: costo de transacción
        
    Returns:
        RebalanceStrategy: instancia de estrategia de rebalanceo
    """
    target_allocation = portfolio_config['allocation']
    rebalance_config = portfolio_config['rebalance']
    
    if rebalance_config['type'] == 'time':
        frequency = rebalance_config.get('frequency', 'annual')
        return TimeBasedRebalance(
            target_allocation, 
            frequency=frequency,
            transaction_cost=transaction_cost
        )
    elif rebalance_config['type'] == 'threshold':
        threshold = rebalance_config.get('threshold', 0.05)
        return ThresholdBasedRebalance(
            target_allocation,
            threshold=threshold,
            transaction_cost=transaction_cost
        )
    else:
        raise ValueError(f"Tipo de rebalanceo desconocido: {rebalance_config['type']}")



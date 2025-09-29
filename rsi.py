import numpy as np
from typing import List, Tuple, Optional
from datetime import datetime, timedelta

def get_rsi(prices: List[Tuple[int, float]], period: int = 14) -> Optional[float]:
    """
    this code made by ai
    """
    if len(prices) < period + 1:
        return None
    
    # Извлекаем цены
    price_values = np.array([p[1] for p in prices])
    
    # Рассчитываем изменения цен
    deltas = np.diff(price_values)
    
    # Используем np.maximum вместо np.where чтобы избежать проблем с условиями
    gains = np.maximum(deltas, 0)
    losses = np.maximum(-deltas, 0)
    
    # Рассчитываем средние для последнего периода
    last_gains = gains[-period:]
    last_losses = losses[-period:]
    
    avg_gain = np.mean(last_gains)
    avg_loss = np.mean(last_losses)
    
    # Проверяем avg_loss на 0
    if np.isclose(avg_loss, 0):
        return 100.0
    
    # Рассчитываем RS и RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)

def get_last_rsi_smoothed(prices: List[Tuple[int, float]], period: int = 14) -> Optional[float]:
    """
    Рассчитывает последнее значение RSI со сглаживанием.
    """
    if len(prices) < period + 1:
        return None
    
    # Извлекаем цены
    price_values = [p[1] for p in prices]
    
    # Рассчитываем изменения цен
    deltas = []
    for i in range(1, len(price_values)):
        deltas.append(price_values[i] - price_values[i-1])
    
    # Разделяем на положительные и отрицательные изменения
    gains = [max(d, 0) for d in deltas]
    losses = [max(-d, 0) for d in deltas]
    
    # Рассчитываем сглаженные средние
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    # Обновляем средние для оставшихся периодов
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    # Если средние убытки равны 0, RSI = 100
    if avg_loss == 0:
        return 100.0
    
    # Рассчитываем RS и RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)
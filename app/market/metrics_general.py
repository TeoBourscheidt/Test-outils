import numpy as np
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
# ==================== METRIQUES ====================

def get_returns(data: pd.DataFrame) -> pd.Series:
    """Calcule les rendements journaliers"""
    prices = data['Close']
    return prices.pct_change().dropna()


def max_drawdown(data :pd.DataFrame) -> dict:
    """
    Calcule le Maximum Drawdown (MDD)
    
    Returns:
        dict avec 'mdd' (%), 'peak', 'trough', 'recovery', 'duration_days'
    """
    prices=data['Close']
    
    cummax = prices.cummax()
    drawdown = (prices - cummax) / cummax
    
    mdd = drawdown.min()
    trough_idx = drawdown.idxmin()
    peak_idx = prices[:trough_idx].idxmax()
    
    # Trouver la date de récupération
    recovery_idx = None
    peak_value = prices[peak_idx]
    for date in prices[trough_idx:].index:
        if prices[date] >= peak_value:
            recovery_idx = date
            break
    
    duration = (trough_idx - peak_idx).days if hasattr(trough_idx - peak_idx, 'days') else None
    
    return {
        'mdd': mdd * 100,
        'peak': peak_idx,
        'trough': trough_idx,
        'recovery': recovery_idx,
        'duration_days': duration
    }


def sharpe_ratio(data:pd.DataFrame, 
                 risk_free_rate: float = 0.02, 
                 periods_per_year: int = 252) -> float:
    """Calcule le ratio de Sharpe annualisé"""
    returns = get_returns(data)
    excess_returns = returns - risk_free_rate / periods_per_year
    return np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std()


def sortino_ratio(data:  pd.DataFrame,
                  risk_free_rate: float = 0.02,
                  periods_per_year: int = 252) -> float:
    """Calcule le ratio de Sortino (uniquement volatilité à la baisse)"""
    returns = get_returns(data)
    excess_returns = returns - risk_free_rate / periods_per_year
    downside_returns = excess_returns[excess_returns < 0]
    downside_std = downside_returns.std()
    
    return np.sqrt(periods_per_year) * excess_returns.mean() / downside_std


def calmar_ratio(data: pd.DataFrame,
                 periods_per_year: int = 252) -> float:
    """Calcule le ratio de Calmar (rendement annualisé / MDD)"""
    annual_ret = annual_return(data, periods_per_year)
    mdd = abs(max_drawdown(data)['mdd'])
    
    return annual_ret / mdd if mdd != 0 else np.inf


def annual_return(data: pd.DataFrame,
                  periods_per_year: int = 252) -> float:
    """Calcule le rendement annualisé en %"""
    prices = data['Close']
    
    total_return = (prices.iloc[-1] / prices.iloc[0]) - 1
    n_periods = len(prices)
    n_years = n_periods / periods_per_year
    
    return ((1 + total_return) ** (1 / n_years) - 1) * 100


def volatility(data:  pd.DataFrame,
               periods_per_year: int = 252) -> float:
    """Calcule la volatilité annualisée en %"""
    returns = get_returns(data)
    return returns.std() * np.sqrt(periods_per_year) * 100

def rolling_volatility(data:  pd.DataFrame, 
                       window: int = 10,
                       periods_per_year: int = 252) -> pd.Series:
    """
    Calcule la volatilité glissante annualisée
    
    Args:
        window: Fenêtre en jours (défaut 10)
    
    Returns:
        Series de volatilités glissantes en %
    """
    returns = get_returns(data)
    return returns.rolling(window).std() * np.sqrt(periods_per_year) * 100

def cor(data1:pd.DataFrame,data2:pd.DataFrame)->float:
    return1=get_returns(data1)
    return2=get_returns(data2)
    return return1.corr(return2) 

def rolling_corr(data1:pd.DataFrame,data2:pd.DataFrame,
                window:int=10)->pd.Series:
    return1=get_returns(data1)
    return2=get_returns(data2)
    return return1.rolling(window).corr(return2)

def var(data:pd.DataFrame,
        confidence_level: float = 0.95) -> float:
    """Calcule la Value at Risk (VaR) en %"""
    returns = get_returns(data)
    return np.percentile(returns, (1 - confidence_level) * 100) * 100


def cvar(data: pd.DataFrame,
         confidence_level: float = 0.95) -> float:
    """Calcule la Conditional Value at Risk (CVaR) en %"""
    returns = get_returns(data)
    var_value = var(data, confidence_level) / 100
    return returns[returns <= var_value].mean() * 100

def win_rate(data:  pd.DataFrame) -> float:
    """Calcule le taux de jours positifs en %"""
    returns = get_returns(data)
    return (returns > 0).sum() / len(returns) * 100


def best_worst_days(data: pd.DataFrame, n: int = 5) -> dict:
    """
    Identifie les meilleurs et pires jours
    
    Returns:
        dict avec 'best_days' et 'worst_days'
    """
    returns = get_returns(data)
    
    best = returns.nlargest(n)
    worst = returns.nsmallest(n)
    
    return {
        'best_days': [(date.strftime('%d/%m/%Y'), ret * 100) for date, ret in best.items()],
        'worst_days': [(date.strftime('%d/%m/%Y'), ret * 100) for date, ret in worst.items()]
    }

# ==================== FORME RENDEMENTS ====================
def skewness(data:  pd.DataFrame) -> float:
    """Calcule l'asymétrie (skewness) des rendements"""
    returns = get_returns(data)
    return returns.skew()


def kurtosis(data: pd.DataFrame) -> float:
    """Calcule le kurtosis (excès) des rendements"""
    returns = get_returns(data)
    return returns.kurtosis()

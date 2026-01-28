#%%
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# ==================== UTILITAIRES ====================
# nom colonne : Open, High, Low, Close,Volume, Dividends, Stock Spits
def get_last_data(tickers:list,start:str,end:str)->dict:
    """Retourne les info des tickers de la période choisi dans un dict."""
    data_tickers=dict()
    for ticker in tickers:
        data=yf.Ticker(ticker).history(start=start,end=end)
        data_tickers[ticker]=data

    return data_tickers

def validate_ticker(ticker:str)->bool:
    """Vérifie si un ticker existe"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return 'symbol' in info or 'shortName' in info
    except:
        return False

# ==================== CALCULS DE PERFORMANCE ====================

def calculate_performance(data:pd.DataFrame):
    """Calcule les métriques de performance sur la période"""
    if data is None or data.empty:
        return None
    
    first_close = data['Close'].iloc[0]
    last_close = data['Close'].iloc[-1]
    variation_pct = ((last_close - first_close) / first_close) * 100
    variation_abs = last_close - first_close
    
    return {
        'prix_debut': float(round(first_close, 2)),
        'prix_fin': float(round(last_close, 2)),
        'variation_pct': float(round(variation_pct, 2)),
        'variation_abs': float(round(variation_abs, 2)),
        'plus_haut': float(round(data['High'].max(), 2)),
        'plus_bas': float(round(data['Low'].min(), 2)),
        'volume_moyen': int(data['Volume'].mean()),
        'volume_total': int(data['Volume'].sum())
    }




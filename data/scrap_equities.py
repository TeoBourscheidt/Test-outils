import yfinance as yf
import pandas as pd
import requests
from io import StringIO
import streamlit as st

@st.cache_data(ttl=86400)
def get_sp500_tickers():
    """Récupère les tickers du S&P 500"""
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text))
        df = tables[0]
        tickers = df['Symbol'].str.replace('.', '-', regex=False).tolist()
        return tickers
    except Exception as e:
        st.error(f"Erreur S&P 500 : {e}")
        return []

@st.cache_data(ttl=86400)
def get_dow30_tickers():
    """Récupère les tickers du Dow Jones Industrial Average"""
    url = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text))
        
        # Chercher le tableau avec la colonne 'Symbol'
        df = None
        for t in tables:
            if 'Symbol' in t.columns:
                df = t
                break
        
        if df is not None:
            tickers = df['Symbol'].str.strip().str.replace('.', '-', regex=False).tolist()
            return tickers
        else:
            st.error("Tableau des composants Dow Jones non trouvé.")
            return []
            
    except Exception as e:
        st.error(f"Erreur Dow Jones : {e}")
        return []

@st.cache_data(ttl=86400)
def get_nasdaq100_tickers():
    """Récupère les tickers du NASDAQ 100"""
    url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text))
        
        # Chercher le tableau avec 'Ticker'
        df = None
        for t in tables:
            if 'Ticker' in t.columns:
                df = t
                break
        
        if df is not None:
            tickers = df['Ticker'].tolist()
            return tickers
        else:
            st.error("Tableau NASDAQ 100 non trouvé.")
            return []
            
    except Exception as e:
        st.error(f"Erreur NASDAQ 100 : {e}")
        return []

@st.cache_data(ttl=86400)
def get_cac40_tickers():
    """Récupère les tickers du CAC 40"""
    url = "https://en.wikipedia.org/wiki/CAC_40"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text))
        
        # Chercher le tableau avec 'Ticker'
        df = None
        for t in tables:
            if 'Ticker' in t.columns:
                df = t
                break
        
        if df is not None:
            tickers = df['Ticker'].tolist()
            return tickers
        else:
            st.error("Tableau CAC 40 non trouvé.")
            return []
            
    except Exception as e:
        st.error(f"Erreur CAC 40 : {e}")
        return []

@st.cache_data(ttl=86400)
def get_dax40_tickers():
    """Récupère les tickers du DAX 40"""
    url = "https://en.wikipedia.org/wiki/DAX"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text))
        
        # Chercher le tableau avec une colonne contenant 'Ticker'
        df = None
        ticker_col = None
        
        for t in tables:
            for col in t.columns:
                if 'Ticker' in str(col) or 'Symbol' in str(col):
                    df = t
                    ticker_col = col
                    break
            if df is not None:
                break
        
        if df is not None and ticker_col is not None:
            tickers = df[ticker_col].str.strip().tolist()
            # Ajouter .DE si pas déjà présent
            tickers = [t if '.DE' in t else f"{t}.DE" for t in tickers]
            return tickers
        else:
            st.error("Tableau DAX non trouvé.")
            return []
            
    except Exception as e:
        st.error(f"Erreur DAX : {e}")
        return []

@st.cache_data(ttl=86400)
def get_ftse100_tickers():
    """Récupère les tickers du FTSE 100"""
    url = "https://en.wikipedia.org/wiki/FTSE_100_Index"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text))
        
        # Chercher le tableau avec environ 100 lignes
        df = None
        for t in tables:
            if 95 <= len(t) <= 105:
                df = t
                break
        
        if df is not None:
            # Chercher la colonne avec les tickers (EPIC)
            ticker_col = None
            for col in ['EPIC', 'Ticker', 'Symbol']:
                if col in df.columns:
                    ticker_col = col
                    break
            
            if ticker_col is None:
                # Prendre la 2ème colonne par défaut
                ticker_col = df.columns[1]
            
            tickers = [f"{str(t).strip()}.L" for t in df[ticker_col].tolist()]
            return tickers
        else:
            st.error("Tableau FTSE 100 non trouvé.")
            return []
            
    except Exception as e:
        st.error(f"Erreur FTSE 100 : {e}")
        return []

@st.cache_data(ttl=86400)
def get_eurostoxx50_tickers():
    """Récupère les tickers de l'Euro Stoxx 50"""
    url = "https://en.wikipedia.org/wiki/Euro_Stoxx_50"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tables = pd.read_html(StringIO(response.text))
        
        # Chercher le tableau avec 'Ticker'
        df = None
        for t in tables:
            if 'Ticker' in t.columns:
                df = t
                break
        
        if df is not None:
            tickers = df['Ticker'].str.strip().tolist()
            return tickers
        else:
            st.error("Tableau Euro Stoxx 50 non trouvé.")
            return []
            
    except Exception as e:
        st.error(f"Erreur Euro Stoxx 50 : {e}")
        return []

def get_index(index: str) -> list:
    """
    Fonction principale pour récupérer les tickers d'un indice donné
    
    Args:
        index: Nom de l'indice (S&P 500, Dow Jones Industrial, NASDAQ 100, 
               CAC 40, DAX 40, FTSE 100, Euro Stoxx 50)
    
    Returns:
        Liste des tickers de l'indice
    """
    index_map = {
        "S&P 500": get_sp500_tickers,
        "Dow Jones Industrial": get_dow30_tickers,
        "NASDAQ Composite": get_nasdaq100_tickers,
        "CAC 40": get_cac40_tickers,
        "DAX 40": get_dax40_tickers,
        "FTSE 100": get_ftse100_tickers,
        "Euro Stoxx 50": get_eurostoxx50_tickers
    }
    
    if index in index_map:
        return index_map[index]()
    else:
        st.warning(f"Indice '{index}' non reconnu.")
        return []
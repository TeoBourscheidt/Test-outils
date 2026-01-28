import yfinance as yf
import pandas as pd
import requests
from io import StringIO
import streamlit as st

@st.cache_data(ttl=84600)
def get_sp500_tickers():
    """Récupère les tickers du S&P 500"""
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Récupérer le HTML avec headers
    response = requests.get(url, headers=headers)
    tables = pd.read_html(StringIO(response.text))
    tickers = tables[0]['Symbol'].tolist()
    return tickers

@st.cache_data(ttl=84600)
def get_dow30_tickers():
    url = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        # Utiliser StringIO pour éviter les warnings de pandas
        tables = pd.read_html(StringIO(response.text))
        
        # On cherche le tableau qui contient une colonne 'Symbol' ou 'Ticker'
        # Souvent c'est l'index 1, mais on va boucler pour être sûr
        df = None
        for t in tables:
            if 'Symbol' in t.columns:
                df = t
                break
        
        if df is not None:
            # Nettoyage des tickers
            tickers = df['Symbol'].str.strip().str.replace('.', '-', regex=False).tolist()
            return tickers
        else:
            st.error("Tableau des composants non trouvé sur Wikipédia.")
            return []
            
    except Exception as e:
        st.error(f"Erreur Dow Jones : {e}")
        return []

@st.cache_data(ttl=84600)
def get_nasdaq100_tickers():
    """Récupère les tickers du NASDAQ 100"""
    url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    tables = pd.read_html(StringIO(response.text))
    tickers = tables[4]['Ticker'].tolist()
    return tickers

@st.cache_data(ttl=84600)
def get_cac40_tickers():
    """Récupère les tickers du CAC 40 (Euronext Paris)"""
    url = "https://en.wikipedia.org/wiki/CAC_40"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        tables = pd.read_html(StringIO(response.text))
        # On cherche le tableau avec la colonne 'Ticker'
        df = next(t for t in tables if 'Ticker' in t.columns)
        return df['Ticker'].tolist()
    except Exception as e:
        st.error(f"Erreur CAC 40 : {e}")
        return []

@st.cache_data(ttl=86400)
def get_dax40_tickers():
    url = "https://en.wikipedia.org/wiki/DAX"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        tables = pd.read_html(StringIO(response.text))
        
        # On cherche le tableau qui a une colonne 'Ticker symbol' ou 'Ticker'
        df = None
        for t in tables:
            # On vérifie si une des colonnes contient 'Ticker'
            cols = [str(c) for c in t.columns]
            if any("Ticker" in c for c in cols):
                df = t
                break
        
        if df is not None:
            # On identifie la colonne exacte
            col_name = [c for c in df.columns if "Ticker" in str(c)][0]
            tickers = df[col_name].str.strip().tolist()
            # Nettoyage pour Yahoo : SAPG -> SAP.DE
            tickers = [str(t).replace(" ", "-") for t in tickers]
            tickers = [t if ".DE" in t else f"{t}.DE" for t in tickers]
            return tickers
        return []
    except Exception as e:
        st.error(f"Erreur DAX : {e}")
        return []

@st.cache_data(ttl=86400)
def get_ftse100_tickers():
    url = "https://en.wikipedia.org/wiki/FTSE_100_Index"
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        tables = pd.read_html(StringIO(response.text))
        
        # Stratégie : Le tableau du FTSE 100 est celui qui a environ 100 lignes
        df = None
        for t in tables:
            if 95 <= len(t) <= 105: # Le FTSE a 100 composants
                df = t
                break
        
        if df is not None:
            # On cherche la colonne qui contient les codes (souvent 3 ou 4 lettres majuscules)
            # On regarde 'EPIC', ou 'Ticker', ou la 2ème colonne par défaut
            if 'EPIC' in df.columns:
                col = 'EPIC'
            elif 'Ticker' in df.columns:
                col = 'Ticker'
            else:
                col = df.columns[1] # Souvent la deuxième colonne après le nom de l'entreprise
            
            tickers = [f"{str(t).strip()}.L" for t in df[col].tolist()]
            return tickers
            
        return []
    except Exception as e:
        st.error(f"Erreur FTSE 100 : {e}")
        return []
    
@st.cache_data(ttl=84600)
def get_eurostoxx50_tickers():
    """Récupère les tickers de l'Euro Stoxx 50"""
    url = "https://en.wikipedia.org/wiki/Euro_Stoxx_50"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers)
        tables = pd.read_html(StringIO(response.text))
        
        # On cherche le tableau contenant la colonne 'Ticker'
        df = next(t for t in tables if 'Ticker' in t.columns)
        
        # Nettoyage : Yahoo Finance utilise des points pour les indices européens
        # On s'assure que le ticker est bien formaté
        tickers = df['Ticker'].str.strip().tolist()
        return tickers
    except Exception as e:
        st.error(f"Erreur Euro Stoxx 50 : {e}")
        return []

def get_index(index: str) -> list:
    if index == "S&P 500":
        return get_sp500_tickers()
    elif index == "Dow Jones Industrial":
        return get_dow30_tickers()
    elif index == "NASDAQ 100":
        return get_nasdaq100_tickers()
    elif index == "CAC 40":
        return get_cac40_tickers()
    elif index == "DAX 40":
        return get_dax40_tickers()
    elif index == "FTSE 100":
        return get_ftse100_tickers()
    if index == "Euro Stoxx 50":
        return get_eurostoxx50_tickers()    
    return []
    

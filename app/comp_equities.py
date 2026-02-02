import pandas as pd
import streamlit as st
import yfinance as yf

from app.metrics import get_returns,max_drawdown,sharpe_ratio,sortino_ratio,calmar_ratio,annual_return,volatility
@st.cache_data(ttl=3600)  # Garde les données en cache pendant 1 heure
def best_worst_equities_index(list_ticker: list, start: str, end: str) -> dict:
    if not list_ticker:
        return {"error": "Empty ticker list"}

    # 1. Téléchargement groupé (Bulk Download)
    # C'est ici que le gain de performance est massif (x10 à x20)
    try:
        raw_data = yf.download(list_ticker, start=start, end=end, group_by='ticker', progress=False)
    except Exception as e:
        return {"error": f"Download failed: {str(e)}"}

    stats = []
    
    # 2. Traitement des données en mémoire
    for ticker in list_ticker:
        try:
            # Extraction des données du ticker depuis le DataFrame global
            if len(list_ticker) > 1:
                df_ticker = raw_data[ticker].dropna(subset=['Close'])
            else:
                df_ticker = raw_data.dropna(subset=['Close'])

            if df_ticker.empty or len(df_ticker) < 5:
                continue
            
            # Calcul des métriques
            ann_ret = annual_return(df_ticker)
            vol_val = volatility(df_ticker)
            mdd_res = max_drawdown(df_ticker)
            
            # Gestion de m_dd qu'il soit un dict ou un float
            mdd_final = mdd_res["mdd"] if isinstance(mdd_res, dict) else mdd_res

            stats.append({
                "ticker": ticker,
                "return": float(ann_ret),
                "vol": float(vol_val),
                "m_dd": mdd_final,
                "sharpe": float(sharpe_ratio(df_ticker)),
                "sortino": float(sortino_ratio(df_ticker)),
                "calmar": float(calmar_ratio(df_ticker))
            })
        except Exception:
            continue 

    if not stats:
        return {"error": "No valid data processed."}

    df = pd.DataFrame(stats)

    # 3. Extraction rapide des Top/Bottom 5 pour chaque métrique
    # On définit toutes les clés attendues par ton mapping
    metrics = ["return", "vol", "sharpe", "sortino", "calmar"]
    results = {}
    
    for m in metrics:
        # Pour la volatilité, "Best" = plus basse, "Worst" = plus haute
        asc_best = True if m == "vol" else False
        asc_worst = False if m == "vol" else True
        
        results[f"best_5_{m}"] = df.sort_values(m, ascending=asc_best).head(5).to_dict('records')
        results[f"worst_5_{m}"] = df.sort_values(m, ascending=asc_worst).head(5).to_dict('records')

    results["all_results"] = df.to_dict('records') 
    
    return results


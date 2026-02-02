import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
from scipy.stats import norm
import plotly.express as px

from app.list_asset import link_index_ticker, global_equities
from app.comp_equities import best_worst_equities_index
from app.scrap_equities import get_index
from app.data import get_last_data,validate_ticker,calculate_performance
from app.metrics import get_returns,max_drawdown,sharpe_ratio,sortino_ratio,calmar_ratio,annual_return,volatility,rolling_volatility,var,cvar,win_rate,best_worst_days,skewness,kurtosis



def generate_analysis(ret, vol, mdd):
    # 1. Performance analysis
    if ret > 15:
        perf_txt = "an impressive performance"
    elif ret > 7:
        perf_txt = "solid growth"
    elif ret > 0:
        perf_txt = "moderate progress"
    else:
        perf_txt = "a downward trend"

    # 2. Risk analysis (Volatility)
    if vol > 25:
        risk_txt = "very volatile (risky)"
    elif vol > 15:
        risk_txt = "moderately choppy"
    else:
        risk_txt = "relatively defensive and stable"

    # 3. Resilience analysis (Max Drawdown)
    # Note: assume mdd is positive (e.g., 20 for -20%)
    mdd_val = abs(mdd)
    if mdd_val > 30:
        res_txt = "severe setbacks"
    elif mdd_val > 15:
        res_txt = "a notable correction"
    else:
        res_txt = "excellent crisis resistance"

    return f"The index shows {perf_txt} of {ret:.2f}% per year. Its profile is {risk_txt} (vol. {vol:.2f}%), having experienced {res_txt} with a historical low of -{mdd_val:.2f}%."

def affichage_first_index():
    st.title("Single Index Analysis")
    
    # 1. Date Selection
    today =datetime.today().date()
    default_start = (datetime.today() - pd.DateOffset(years=1)).date()
    c1, c2 = st.columns(2)
    start_date = c1.date_input(
        label="Start Date",
        value=default_start,
        max_value=today
    )
    end_date = c2.date_input(
        label="End Date",
        value=today,
        min_value=default_start,
        max_value=today
    )
    
    # 2. Index Selection
    name_single_index = st.selectbox(
        label="Select a Benchmark Index",
        options=[
            "S&P 500", "Dow Jones Industrial", "NASDAQ Composite", "S&P/TSX Composite (Canada)",
            "Euro Stoxx 50", "DAX 40 (Germany)", "CAC 40 (France)", "FTSE 100 (UK)", "SMI (Switzerland)",
            "Nikkei 225 (Japan)", "TOPIX (Japan)", "Shanghai Composite (China)", "BSE Sensex (India)", "KOSPI (Korea)",
            "IBOVESPA (Brazil)", "IPC (Mexico)", "MERVAL (Argentina)", "IPSA (Chile)",
            "Tadawul All Share (Saudi Arabia)", "DFM General Index (UAE)", "FTSE/JSE Top 40 (South Africa)", "TA-125 (Israel)",
            "MSCI World", "MSCI Emerging Markets", "FTSE All-World", "MSCI Asia ex-Japan", "MSCI Europe"
        ]
    )

    ticker_single_index = link_index_ticker[name_single_index]
    
    # Data Loading
    data_single_index = get_last_data([ticker_single_index], start_date, end_date)
    
    if ticker_single_index not in data_single_index or data_single_index[ticker_single_index].empty:
        st.error(f"No historical data available for {name_single_index} in this period.")
        return

    close_price = data_single_index[ticker_single_index]["Close"]
    
    # 3. Main Price Chart
    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(
        x=close_price.index,
        y=close_price,
        mode="lines",
        name=name_single_index,
        line=dict(color='#003366')
    ))

    fig_price.update_layout(
        title=f"{name_single_index} Historical Performance",
        xaxis_title="Date",
        yaxis_title="Close Price",
        template="plotly_white",    
        hovermode="x unified"
    )
    st.plotly_chart(fig_price, use_container_width=True) 
    

    # 4. Performance Metrics
    m1, m2, m3 = st.columns(3)

    ann_ret = annual_return(data_single_index[ticker_single_index])
    vol = volatility(data_single_index[ticker_single_index])
    mdd_data = max_drawdown(data_single_index[ticker_single_index])
    mdd_val = mdd_data["mdd"] if isinstance(mdd_data, dict) else mdd_data

    m1.metric(label="Annualized Return", value=f"{ann_ret:.2f}%")
    m2.metric(
        label="Annualized Volatility", 
        value=f"{vol:.2f}%",
        help="Measures the dispersion of returns. High volatility indicates higher investment risk."
    )
    m3.metric(
        label="Maximum Drawdown", 
        value=f"{mdd_val:.2f}%",
        help="The largest peak-to-trough decline during the period. Represents the worst-case loss scenario."
    )
    
    # Analysis summary (Corrected spelling)
    st.info(generate_analysis(ann_ret, vol, mdd_val))

    # 5. Return Distribution & Risk
    st.subheader("Return Distribution Analysis")
    dist_col, stats_col = st.columns([7, 3])
    
    returns = get_returns(data_single_index[ticker_single_index]).dropna()
    
    with dist_col:
        if not returns.empty:
            var_95 = np.percentile(returns, 5)
            fig_dist = go.Figure()

            # Histogram
            fig_dist.add_trace(go.Histogram(
                x=returns,
                histnorm='probability density',
                name='Returns Frequency',
                marker_color='#3366CC',
                opacity=0.6,
                nbinsx=40
            ))

            # KDE & Normal Curve
            x_range = np.linspace(returns.min(), returns.max(), 100)
            kde = gaussian_kde(returns)
            mu, std = returns.mean(), returns.std()
            
            fig_dist.add_trace(go.Scatter(x=x_range, y=kde(x_range), name='KDE (Empirical)', line=dict(color='red', width=2)))
            fig_dist.add_trace(go.Scatter(x=x_range, y=norm.pdf(x_range, mu, std), name='Normal Dist.', line=dict(color='gray', dash='dot')))
            
            fig_dist.add_vline(x=var_95, line_dash="dash", line_color="orange", annotation_text="VaR 95%")

            fig_dist.update_layout(
                template="plotly_white",
                xaxis_title="Daily Return (%)",
                yaxis_title="Probability Density",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_dist, use_container_width=True)

    with stats_col:
        st.write("Distribution Stats")
        skew_val = skewness(data_single_index[ticker_single_index])
        kurt_val = kurtosis(data_single_index[ticker_single_index])
        
        st.metric(label="Skewness", value=f"{skew_val:.2f}", 
                  help="Measures symmetry. Negative skew indicates a higher probability of large losses.")
        st.metric(label="Excess Kurtosis", value=f"{kurt_val:.2f}", 
                  help="Measures 'tail risk'. High kurtosis (>3) indicates more frequent extreme market events.")
        st.metric(label="Daily VaR (95%)", value=f"{var_95:.2f}%", 
                  help="The maximum expected daily loss with 95% confidence.")
        
def affichage_comp_index():
    st.title("Multi-Index Comparison")
    
    # 1. Date Configuration
    today = datetime.today()
    c1, c2 = st.columns(2)
    start_date = c1.date_input(label="Comparison Start Date",
                               value=today - pd.DateOffset(years=1),
                               max_value=today)
    end_date = c2.date_input(label="Comparison End Date",
                             value=today,
                             min_value=start_date,
                             max_value=today)

    # 2. Index Selection
    name_multi_index = st.multiselect(
        "Select up to 5 indices for comparison:",
        options=[
            "S&P 500", "Dow Jones Industrial", "NASDAQ Composite", "S&P/TSX Composite (Canada)",
            "Euro Stoxx 50", "DAX 40 (Germany)", "CAC 40 (France)", "FTSE 100 (UK)", "SMI (Switzerland)",
            "Nikkei 225 (Japan)", "TOPIX (Japan)", "Shanghai Composite (China)", "BSE Sensex (India)", "KOSPI (Korea)",
            "IBOVESPA (Brazil)", "IPC (Mexico)", "MERVAL (Argentina)", "IPSA (Chile)",
            "Tadawul All Share (Saudi Arabia)", "DFM General Index (UAE)", "FTSE/JSE Top 40 (South Africa)", "TA-125 (Israel)",
            "MSCI World", "MSCI Emerging Markets", "FTSE All-World", "MSCI Asia ex-Japan", "MSCI Europe"
        ],
        default=["S&P 500", "Euro Stoxx 50"],
        max_selections=5  
    )

    if not name_multi_index:
        st.warning("Please select at least one index to display data.")
        return

    # Data Fetching
    tickers = [link_index_ticker[name] for name in name_multi_index]
    data_multi = get_last_data(tickers, start_date, end_date)

    # 3. Main Comparison Chart
    is_normalized = st.checkbox("Normalize Performance (Base 100)", value=True, 
                               help="Rebases all indices to 100 at the start date for easier performance comparison.")

    fig = go.Figure()
    for t, name in zip(tickers, name_multi_index):
        if t in data_multi and not data_multi[t].empty:
            y_data = data_multi[t]["Close"]
            if is_normalized:
                y_data = (y_data / y_data.iloc[0]) * 100
            
            fig.add_trace(go.Scatter(x=y_data.index, y=y_data, mode="lines", name=name))
    
    fig.update_layout(
        title="Comparative Performance Analysis",
        xaxis_title="Date",
        yaxis_title="Performance (%)" if is_normalized else "Price (USD)",
        template="plotly_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    cols=st.columns(len(tickers))
    for col,t, name in zip(cols,tickers, name_multi_index):
        col.metric(name, f"{annual_return(data_multi[t]):.2f}%", "Ann. Return")
    # 4. Detailed Metrics Section
    st.divider()
    st.subheader("Comparative Risk Metrics")
    
    # Use Tabs for a cleaner UI
    choice = st.selectbox(
        label="Metrics",
        options=["Volatility", "Max Drawdown", "Risk-Adjusted Ratios"])

    if choice=="Volatility":
        window = st.slider("Rolling Window (Days)", 5, 60, 30)
        fig_vol = go.Figure()
        
        m_cols = st.columns(len(tickers))
        for i, (t, name) in enumerate(zip(tickers, name_multi_index)):
            v = volatility(data_multi[t])
            m_cols[i].metric(name, f"{v:.2f}%", "Ann. Vol")
            
            v_series = rolling_volatility(data_multi[t], window=window)
            fig_vol.add_trace(go.Scatter(x=v_series.index, y=v_series, name=name))
        
        fig_vol.update_layout(title=f"{window}-Day Rolling Annualized Volatility", template="plotly_white")
        st.plotly_chart(fig_vol, use_container_width=True)

    if choice=="Max Drawdown":
        mdd_cols = st.columns(len(tickers))
        for i, (t, name) in enumerate(zip(tickers, name_multi_index)):
            with mdd_cols[i]:
                m = max_drawdown(data_multi[t])
                st.markdown(f"**{name}**")
                st.metric("Max Drawdown", f"{m['mdd']:.2f}%")
                st.text(f"Peak: \n {m['peak'].strftime('%Y-%m-%d')}")
                st.text(f"Trough: \n {m['trough'].strftime('%Y-%m-%d')}")
                st.metric("Recovery Days", int(m['duration_days']))

    if choice=="Risk-Adjusted Ratios":
        ratio_cols = st.columns(len(tickers))
        for i, (t, name) in enumerate(zip(tickers, name_multi_index)):
            with ratio_cols[i]:
                st.markdown(f"**{name}**")
                st.metric("Sharpe Ratio", f"{sharpe_ratio(data_multi[t]):.2f}")
                st.metric("Sortino Ratio", f"{sortino_ratio(data_multi[t]):.2f}")
                st.metric("Calmar Ratio", f"{calmar_ratio(data_multi[t]):.2f}")

def comp_equities_vs_index():
    st.title("Index Constituents Analysis")
    
    today = datetime.today()
    c1, c2 = st.columns(2)
    
    start_date = c1.date_input("Analysis Start Date", 
                               value=today - pd.DateOffset(years=1), 
                               max_value=today, key="start_date_idx")
    end_date = c2.date_input("Analysis End Date", 
                             value=today, 
                             min_value=start_date, 
                             max_value=today, key="end_date_idx")
    
    index_choose = st.selectbox(
        label="Select Benchmark Index",
        options=["NASDAQ Composite", "Dow Jones Industrial", "S&P 500","CAC 40","DAX 40","FTSE 100","Euro Stoxx 50"],
        key="index_selection_box"
    )

    if st.button("Analyze Constituents", key="btn_analyze"):
        with st.spinner("Fetching and processing index data..."):
            list_equities = get_index(index_choose)
            list_equities = [t.replace('.', '-') for t in list_equities]
            st.session_state['data_bw'] = best_worst_equities_index(list_equities, start_date, end_date)
            st.session_state['list_len'] = len(list_equities)

    if 'data_bw' in st.session_state:
        data_bw = st.session_state['data_bw']
        if "error" in data_bw:
            st.error(data_bw["error"])
            return
            
        st.info(f"Total assets analyzed in index: {st.session_state['list_len']}")

        # --- ÉTAPE 1 : PRÉPARATION SILENCIEUSE (Calculs sans affichage) ---
        type_options = {
            "Best return": "Top 5 Returns", "Worst return": "Bottom 5 Returns",
            "Best vol": "Lowest Volatility", "Worst vol": "Highest Volatility",
            "Best sharpe": "Top Sharpe Ratios", "Worst sharpe": "Bottom Sharpe Ratios",
            "Best sortino": "Top Sortino Ratios", "Best calmar": "Top Calmar Ratios"
        }
        
        # On définit le mapping et la sélection immédiatement pour éviter UnboundLocalError
        mapping = {
            "Best return": "best_5_return", "Worst return": "worst_5_return",
            "Best vol": "best_5_vol", "Worst vol": "worst_5_vol",
            "Best sharpe": "best_5_sharpe", "Worst sharpe": "worst_5_sharpe",
            "Best sortino": "best_5_sortino", "Best calmar": "best_5_calmar"
        }

        # --- ÉTAPE 2 : AFFICHAGE MACRO (A & B) ---
        if "all_results" in data_bw:
            all_data = pd.DataFrame(data_bw["all_results"])
            avg_ret = all_data['return'].mean() # Calculé ici pour être utilisé plus bas
            
            st.write("---")
            st.subheader(f"Statistic : {index_choose}")

            # A. Market Breadth
            st.text("Market breadth")
            col_b1, col_b2 = st.columns([1, 2])
            ups = len(all_data[all_data['return'] > 0])
            downs = len(all_data[all_data['return'] <= 0])
            total = len(all_data)
            breadth_pct = (ups / total) * 100 if total > 0 else 0

            with col_b1:
                st.metric("Advancing Issues", f"{ups}", f"{breadth_pct:.1f}%")
                st.metric("Declining Issues", f"{downs}", f"{(downs/total)*100 if total > 0 else 0:.1f}%", delta_color="inverse")

            with col_b2:
                fig_pie = px.pie(names=['Positive Returns', 'Negative Returns'], values=[ups, downs],
                                 color_discrete_map={'Positive Returns': "#35A061B9", 'Negative Returns': '#e74c3c'},
                                 hole=0.5, height=250)
                st.plotly_chart(fig_pie, use_container_width=True)

            # B. Distribution
            st.text("Return Distribution")
            fig_hist = px.histogram(all_data, x="return", nbins=25, color_discrete_sequence=['#2c3e50'])
            fig_hist.add_vline(x=avg_ret, line_dash="dash", line_color="orange")
            st.plotly_chart(fig_hist, use_container_width=True)

        # --- ÉTAPE 3 : SÉLECTION DES TICKERS ET GRAPHIQUES ---
        st.write("---")
        type_label = st.selectbox("Rank by Metric:", options=list(type_options.keys()), 
                                  format_func=lambda x: type_options[x], key="rank_metric_unique")

        selection_key = mapping.get(type_label)
        data_selected = data_bw.get(selection_key, [])

        if data_selected:
            list_ticker_equities = [elt["ticker"] for elt in data_selected]
            data_equities = get_last_data(list_ticker_equities, start=start_date, end=end_date)

            bool_relative = st.checkbox(label="Normalize to Base 100", value=True, key="norm_base_100")
            fig = go.Figure()
            for ticker in list_ticker_equities:
                if ticker in data_equities and not data_equities[ticker].empty:
                    close_prices = data_equities[ticker]["Close"]
                    y_val = (close_prices / close_prices.iloc[0] * 100) if bool_relative else close_prices
                    fig.add_trace(go.Scatter(x=close_prices.index, y=y_val, mode="lines", name=ticker))
            st.plotly_chart(fig, use_container_width=True)

            selected_avg = pd.DataFrame(data_selected)['return'].mean()
            alpha = selected_avg - avg_ret
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Selection Average", f"{selected_avg:.1f}%")
            c2.metric("Index Average", f"{avg_ret:.1f}%")
            c3.metric("Excess Return (Alpha)", f"{alpha:.2f}%", delta=f"{alpha:.2f}% pts")

            # --- ÉTAPE 4 : STATISTIQUES DÉTAILLÉES ---
            choice = st.selectbox(label="Statistics", key="stats_choice_unique",
                                options=["Risk vs. Reward Profile","Detailed Statistics","Multi-Asset Correlation Matrix"])
            
            if choice=="Risk vs. Reward Profile":
                st.write("### Risk vs. Reward Profile")
                st.markdown("*Bubble size represents the **Sharpe Ratio** (Absolute value).*")

                df_plot = pd.DataFrame(data_selected)
                
                # 1. On crée une colonne pour la taille (toujours positive)
                # On ajoute un petit offset (+0.5) pour que les points ne disparaissent pas si Sharpe = 0
                df_plot['abs_sharpe'] = df_plot['sharpe'].abs() + 0.5

                fig_scatter = px.scatter(
                    df_plot,
                    x="vol",
                    y="return",
                    text="ticker",
                    size="abs_sharpe",  # Utilisation de la valeur absolue pour la taille
                    color="sharpe",      # La couleur garde le vrai signe (négatif = bleu/froid, positif = rouge/chaud)
                    labels={
                        "vol": "Annualized Volatility (%)",
                        "return": "Annualized Return (%)",
                        "sharpe": "Sharpe Ratio",
                        "abs_sharpe": "Sharpe Magnitude"
                    },
                    color_continuous_scale='RdBu_r', 
                    range_color=[-2, 2], # Centre l'échelle de couleur pour mieux voir les négatifs
                    template="plotly_white"
                )
                
                fig_scatter.update_traces(
                    textposition='top center', 
                    marker=dict(sizeref=0.05, sizemode='area') # sizeref ajuste la taille globale des bulles
                )
                
                # Lignes de repère pour le quadrant "Idéal" (Top-Left)
                fig_scatter.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.3)
                
                st.plotly_chart(fig_scatter, use_container_width=True)
                # 4. Metrics Display

            if choice=="Detailed Statistics":
                st.write("### Detailed Statistics")
                cols = st.columns(len(data_selected))
                for col, elt in zip(cols, data_selected):
                    with col:
                        st.markdown(f"**{elt['ticker']}**")
                        st.metric("Annual Return", f"{elt['return']:.1f}%")
                        st.metric("Volatility", f"{elt['vol']:.2f}%")
                        
                        # Check if m_dd is a dict or a float to prevent crashes
                        mdd_val = elt["m_dd"]["mdd"] if isinstance(elt["m_dd"], dict) else elt["m_dd"]
                        st.metric("Max Drawdown", f"{mdd_val:.2f}%")
                        
                        st.metric("Sharpe", f"{elt['sharpe']:.2f}")
                        st.metric("Sortino", f"{elt['sortino']:.2f}")

            if choice=="Multi-Asset Correlation Matrix":
                st.write("### Multi-Asset Correlation Matrix")
                st.markdown("""
                    *This matrix shows how the selected assets move relative to each other. 
                    A value of **1.0** means perfect correlation, while **0** means no relationship.*
                """)
                
                if not data_equities:
                    st.warning("No data available for correlation analysis.")
                    return

                # Extraction des colonnes 'Close' et calcul des rendements
                df_returns = pd.DataFrame()
                for ticker in list_ticker_equities:
                    if ticker in data_equities:
                        df_returns[ticker] = get_returns(data_equities[ticker])
                
                if df_returns.empty:
                    st.error("Insufficient data to calculate correlations.")
                    return

                corr_matrix = df_returns.corr()

                # Création du Heatmap Plotly
                fig_corr = px.imshow(
                    corr_matrix,
                    text_auto=".2f",
                    aspect="auto",
                    color_continuous_scale='RdBu_r', # Rouge pour corrélation positive, Bleu pour négative
                    labels=dict(color="Correlation"),
                    zmin=-1, zmax=1
                )
                
                fig_corr.update_layout(
                    template="plotly_white",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                
                st.plotly_chart(fig_corr, use_container_width=True)


def comp_equities_vs_index2():
    st.title("Index Constituents Analysis")
    
    today = datetime.today()
    c1, c2 = st.columns(2)
    
    start_date = c1.date_input("Analysis Start Date", 
                               value=today - pd.DateOffset(years=1), 
                               max_value=today)
    end_date = c2.date_input("Analysis End Date", 
                             value=today, 
                             min_value=start_date, 
                             max_value=today)
    
    index_choose = st.selectbox(
        label="Select Benchmark Index",
        options=["NASDAQ Composite", "Dow Jones Industrial", "S&P 500","CAC 40","DAX 40","FTSE 100","Euro Stoxx 50"]
    )

    # 1. Data loading with Session State
    if st.button("Analyze Constituents"):
        with st.spinner("Fetching and processing index data..."):
            list_equities = get_index(index_choose)
            # Remplace les points par des tirets pour les tickers US (S&P 500, etc.)
            list_equities = [t.replace('.', '-') for t in list_equities]
            # Make sure best_worst_equities_index calculates all the new keys (sharpe, etc.)
            st.session_state['data_bw'] = best_worst_equities_index(list_equities, start_date, end_date)
            st.session_state['list_len'] = len(list_equities)

    # 2. Check if data exists in state
    # 2. Check if data exists in state
    if 'data_bw' in st.session_state:
        data_bw = st.session_state['data_bw']
        
        if "error" in data_bw:
            st.error(data_bw["error"])
            return
            
        st.info(f"Total assets analyzed in index: {st.session_state['list_len']}")

        # --- STEP 1: DEFINE SELECTION FIRST (To avoid UnboundLocalError) ---
        type_options = {
            "Best return": "Top 5 Returns",
            "Worst return": "Bottom 5 Returns",
            "Best vol": "Lowest Volatility",
            "Worst vol": "Highest Volatility",
            "Best sharpe": "Top Sharpe Ratios",
            "Worst sharpe": "Bottom Sharpe Ratios",
            "Best sortino": "Top Sortino Ratios",
            "Best calmar": "Top Calmar Ratios"
        }
        
        type_label = st.selectbox("Rank by Metric:", options=list(type_options.keys()), 
                                  format_func=lambda x: type_options[x])

        mapping = {
            "Best return": "best_5_return", "Worst return": "worst_5_return",
            "Best vol": "best_5_vol", "Worst vol": "worst_5_vol",
            "Best sharpe": "best_5_sharpe", "Worst sharpe": "worst_5_sharpe",
            "Best sortino": "best_5_sortino", "Best calmar": "best_5_calmar"
        }

        selection_key = mapping.get(type_label)
        data_selected = data_bw.get(selection_key, [])

        # --- STEP 2: MACRO INDEX ANALYSIS (Now safe to run) ---
        if "all_results" in data_bw:
            all_data = pd.DataFrame(data_bw["all_results"])
            
            st.write("---")
            st.header(f"📊 Market Insight: {index_choose}")

            # A. MARKET BREADTH
            st.subheader("A. Market Breadth")
            col1, col2 = st.columns([1, 2])
            ups = len(all_data[all_data['return'] > 0])
            downs = len(all_data[all_data['return'] <= 0])
            total = len(all_data)
            breadth_pct = (ups / total) * 100 if total > 0 else 0

            with col1:
                st.metric("Advancing Issues", f"{ups}", f"{breadth_pct:.1f}% of Index")
                st.metric("Declining Issues", f"{downs}", f"{(downs/total)*100 if total > 0 else 0:.1f}%", delta_color="inverse")
                insight = "Healthy Participation" if breadth_pct > 55 else "Narrow Participation"
                st.info(f"**Market Status:** {insight}")

            with col2:
                fig_pie = px.pie(
                    names=['Positive Returns', 'Negative Returns'], 
                    values=[ups, downs],
                    color_discrete_map={'Positive Returns': '#27ae60', 'Negative Returns': '#e74c3c'},
                    hole=0.5, height=300
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            # B. RETURN DISTRIBUTION
            st.subheader("B. Return Distribution")
            
            fig_hist = px.histogram(
                all_data, x="return", nbins=25,
                title=f"Annualized Return Distribution ({index_choose})",
                color_discrete_sequence=['#2c3e50']
            )
            avg_ret = all_data['return'].mean()
            fig_hist.add_vline(x=avg_ret, line_dash="dash", line_color="orange", annotation_text=f"Mean: {avg_ret:.1f}%")
            st.plotly_chart(fig_hist, use_container_width=True)
            


        
        # Professional English labels for selection
        type_options = {
            "Best return": "Top 5 Returns",
            "Worst return": "Bottom 5 Returns",
            "Best vol": "Lowest Volatility",
            "Worst vol": "Highest Volatility",
            "Best sharpe": "Top Sharpe Ratios",
            "Worst sharpe": "Bottom Sharpe Ratios",
            "Best sortino": "Top Sortino Ratios",
            "Best calmar": "Top Calmar Ratios"
        }
        
        type_label = st.selectbox("Rank by Metric:", options=list(type_options.keys()), 
                                  format_func=lambda x: type_options[x])

        mapping = {
            "Best return": "best_5_return", "Worst return": "worst_5_return",
            "Best vol": "best_5_vol", "Worst vol": "worst_5_vol",
            "Best sharpe": "best_5_sharpe", "Worst sharpe": "worst_5_sharpe",
            "Best sortino": "best_5_sortino", "Best calmar": "best_5_calmar"
        }

        selection_key = mapping.get(type_label)
        data_selected = data_bw.get(selection_key, [])

        if not data_selected:
            st.warning(f"No data available for {type_label}. Ensure your analysis function supports this metric.")
            return

        list_ticker_equities = [elt["ticker"] for elt in data_selected]
        data_equities = get_last_data(list_ticker_equities, start=start_date, end=end_date)

        # 3. Chart Construction
        bool_relative = st.checkbox(label="Normalize to Base 100", value=True)
        fig = go.Figure()
        
        for ticker in list_ticker_equities:
            if ticker in data_equities and not data_equities[ticker].empty:
                close_prices = data_equities[ticker]["Close"]
                
                y_val = (close_prices / close_prices.iloc[0] * 100) if bool_relative else close_prices
                
                fig.add_trace(go.Scatter(
                    x=close_prices.index,
                    y=y_val,
                    mode="lines",
                    name=ticker
                ))

        fig.update_layout(
            title=f"Constituents Performance: {type_options[type_label]}",
            xaxis_title="Date",
            yaxis_title="Relative Performance (%)" if bool_relative else "Price ($)",
            template="plotly_white",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

        choice=st.selectbox(label="Statistics",
                            options=["Risk vs. Reward Profile","Detailed Statistics","Multi-Asset Correlation Matrix"])

        if choice=="Risk vs. Reward Profile":
            st.write("### Risk vs. Reward Profile")
            st.markdown("*Bubble size represents the **Sharpe Ratio** (Absolute value).*")

            df_plot = pd.DataFrame(data_selected)
            
            # 1. On crée une colonne pour la taille (toujours positive)
            # On ajoute un petit offset (+0.5) pour que les points ne disparaissent pas si Sharpe = 0
            df_plot['abs_sharpe'] = df_plot['sharpe'].abs() + 0.5

            fig_scatter = px.scatter(
                df_plot,
                x="vol",
                y="return",
                text="ticker",
                size="abs_sharpe",  # Utilisation de la valeur absolue pour la taille
                color="sharpe",      # La couleur garde le vrai signe (négatif = bleu/froid, positif = rouge/chaud)
                labels={
                    "vol": "Annualized Volatility (%)",
                    "return": "Annualized Return (%)",
                    "sharpe": "Sharpe Ratio",
                    "abs_sharpe": "Sharpe Magnitude"
                },
                color_continuous_scale='RdBu_r', 
                range_color=[-2, 2], # Centre l'échelle de couleur pour mieux voir les négatifs
                template="plotly_white"
            )
            
            fig_scatter.update_traces(
                textposition='top center', 
                marker=dict(sizeref=0.05, sizemode='area') # sizeref ajuste la taille globale des bulles
            )
            
            # Lignes de repère pour le quadrant "Idéal" (Top-Left)
            fig_scatter.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.3)
            
            st.plotly_chart(fig_scatter, use_container_width=True)
            # 4. Metrics Display

        if choice=="Detailed Statistics":
            st.write("### Detailed Statistics")
            cols = st.columns(len(data_selected))
            for col, elt in zip(cols, data_selected):
                with col:
                    st.markdown(f"**{elt['ticker']}**")
                    st.metric("Annual Return", f"{elt['return']:.1f}%")
                    st.metric("Volatility", f"{elt['vol']:.2f}%")
                    
                    # Check if m_dd is a dict or a float to prevent crashes
                    mdd_val = elt["m_dd"]["mdd"] if isinstance(elt["m_dd"], dict) else elt["m_dd"]
                    st.metric("Max Drawdown", f"{mdd_val:.2f}%")
                    
                    st.metric("Sharpe", f"{elt['sharpe']:.2f}")
                    st.metric("Sortino", f"{elt['sortino']:.2f}")

        if choice=="Multi-Asset Correlation Matrix":
            st.write("### Multi-Asset Correlation Matrix")
            st.markdown("""
                *This matrix shows how the selected assets move relative to each other. 
                A value of **1.0** means perfect correlation, while **0** means no relationship.*
            """)
            
            if not data_equities:
                st.warning("No data available for correlation analysis.")
                return

            # Extraction des colonnes 'Close' et calcul des rendements
            df_returns = pd.DataFrame()
            for ticker in list_ticker_equities:
                if ticker in data_equities:
                    df_returns[ticker] = get_returns(data_equities[ticker])
            
            if df_returns.empty:
                st.error("Insufficient data to calculate correlations.")
                return

            corr_matrix = df_returns.corr()

            # Création du Heatmap Plotly
            fig_corr = px.imshow(
                corr_matrix,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale='RdBu_r', # Rouge pour corrélation positive, Bleu pour négative
                labels=dict(color="Correlation"),
                zmin=-1, zmax=1
            )
            
            fig_corr.update_layout(
                template="plotly_white",
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)
    # C. ALPHA ANALYSIS (data_selected is now defined!)
        if data_selected:
            st.subheader("C. Selection Alpha vs. Benchmark")
            selected_avg = pd.DataFrame(data_selected)['return'].mean()
            alpha = selected_avg - avg_ret
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Selection Average", f"{selected_avg:.1f}%")
            c2.metric("Index Average", f"{avg_ret:.1f}%")
            c3.metric("Excess Return (Alpha)", f"{alpha:.2f}%", delta=f"{alpha:.2f}% pts")


def affichage_compare_two_assets():
    st.title("Asset vs. Asset: Direct Comparison")
    
    # 1. Configuration des dates
    today = datetime.today()
    c1, c2 = st.columns(2)
    start_date = c1.date_input("Start Date", value=today - pd.DateOffset(years=1), max_value=today, key="start_2a")
    end_date = c2.date_input("End Date", value=today, min_value=start_date, max_value=today, key="end_2a")

    # 2. Sélection des deux actifs
    st.subheader("Select Assets to Compare")
    col_a, col_b = st.columns(2)
    
    # On récupère tous les noms disponibles dans ton dictionnaire global link_index_ticker
    all_options = list(global_equities.keys())
    
    asset_name_1 = col_a.selectbox("First Asset", options=all_options, index=0)
    asset_name_2 = col_b.selectbox("Second Asset", options=all_options, index=1)

    ticker_1 = global_equities[asset_name_1]
    ticker_2 = global_equities[asset_name_2]

    # Chargement des données
    data = get_last_data([ticker_1, ticker_2], start_date, end_date)
    df1 = data[ticker_1]
    df2 = data[ticker_2]
    ret1 = get_returns(df1)
    ret2 = get_returns(df2)

    choice_relative=st.checkbox(label="Normalize to base 100")
    if ticker_1 in data and ticker_2 in data:


        # --- SECTION 1: PERFORMANCE RELATIVE ---
        st.subheader("Performance Spread")
        fig_perf = go.Figure()
        

        # Normalisation Base 100
        if choice_relative:
            rel_1 = (df1["Close"] / df1["Close"].iloc[0]) * 100
            rel_2 = (df2["Close"] / df2["Close"].iloc[0]) * 100
            fig_perf.add_trace(go.Scatter(x=rel_1.index, y=rel_1, name=asset_name_1))
            fig_perf.add_trace(go.Scatter(x=rel_2.index, y=rel_2, name=asset_name_2))
            
            # Ajout du "Spread" (différence de performance)
            spread = rel_1 - rel_2
            fig_perf.add_trace(go.Bar(x=spread.index, y=spread, name="Spread (A - B)", opacity=0.3, marker_color="gray"))

            fig_perf.update_layout(title="Rebased Performance (Base 100) & Spread", template="plotly_white", hovermode="x unified")
            st.plotly_chart(fig_perf, use_container_width=True)
        else :
            rel_1 = df1["Close"] 
            rel_2 = df2["Close"] 
        
            fig_perf.add_trace(go.Scatter(x=rel_1.index, y=rel_1, name=asset_name_1))
            fig_perf.add_trace(go.Scatter(x=rel_2.index, y=rel_2, name=asset_name_2))
         
            fig_perf.update_layout(title="Close : "+asset_name_1+" "+asset_name_2, template="plotly_white", hovermode="x unified")
            st.plotly_chart(fig_perf, use_container_width=True)

        choice=st.selectbox(label="Metrics",
                            options=["Side-by-Side Analysis","Rolling Correlation (30-Day Window)"])
        
        if choice=="Side-by-Side Analysis":
            # --- SECTION 2: MÉTRIQUES COMPARATIVES ---
            st.subheader("Side-by-Side Analysis")
            m_col1, m_col2, m_col3 = st.columns(3)
            
            # Calcul des retours pour la corrélation
            correlation = ret1.corr(ret2)

            with m_col1:
                st.write(f"**{asset_name_1}**")
                st.metric("Annual Return", f"{annual_return(df1):.2f}%")
                st.metric("Volatility", f"{volatility(df1):.2f}%")
                st.metric("Sharpe Ratio", f"{sharpe_ratio(df1):.2f}")

            with m_col2:
                st.write(f"**{asset_name_2}**")
                st.metric("Annual Return", f"{annual_return(df2):.2f}%")
                st.metric("Volatility", f"{volatility(df2):.2f}%")
                st.metric("Sharpe Ratio", f"{sharpe_ratio(df2):.2f}")

            with m_col3:
            
                
                st.write("**Relationship**")
                st.metric("Correlation", f"{correlation:.2f}", help="Closer to 1 means they move together. Closer to -1 means they move in opposite directions.")
                # Calcul du Beta de Asset 1 par rapport à Asset 2 (Optionnel mais pro)
                beta = (ret1.cov(ret2) / ret2.var())
                st.metric("Relative Beta", f"{beta:.2f}", help="Sensitivity of Asset 1 relative to Asset 2")

        if choice=="Rolling Correlation (30-Day Window)":
            # --- SECTION 3: CORRÉLATION GLISSANTE ---
            st.subheader("Rolling Correlation (30-Day Window)")
            rolling_corr = ret1.rolling(window=30).corr(ret2)
            
            fig_corr = px.line(rolling_corr, title="Correlation Stability Over Time", labels={"value": "Correlation", "index": "Date"})
            fig_corr.update_layout(template="plotly_white", yaxis_range=[-1, 1])
            st.plotly_chart(fig_corr, use_container_width=True)

    else:
        st.error("Missing data for one of the selected assets.")

def affichage_stock_index_market():
    single_index, multi_index,test,compare_asset=st.tabs(["Single Index Analysis","Multi-Index Comparison","Index Constituents Analysis","Asset vs. Asset"])
    with single_index:
        affichage_first_index()
    with multi_index:
        affichage_comp_index()
    with test:
        comp_equities_vs_index()
    with compare_asset:
        affichage_compare_two_assets()
    




import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
from scipy.stats import norm
import plotly.express as px

from app.list_asset import commodities_dict,energy_tickers,fx_tickers,metal_tickers
from app.data import get_last_data
from app.metrics import rolling_volatility,volatility,get_returns

def aff_general():
    return 0

def aff_energy():

    st.header("Energy Sector Analysis")
    today = datetime.today()
    c1, c2 = st.columns(2)
    start_date = c1.date_input(
        label="Start Date",
        value=today - pd.DateOffset(years=1),
        max_value=today,
        key="energy_start"
    )
    end_date = c2.date_input(
        label="End Date",
        value=today,
        min_value=start_date,
        max_value=today,
        key="energy_end"
    )

    # Inversion du dictionnaire pour retrouver le nom à partir du ticker
    names = {v: k for k, v in energy_tickers.items()}
    
    choice_energy = st.multiselect(
        "Choose your energy assets",
        options=list(energy_tickers.keys()), # Utilise les clés (noms)
        default=["Crude Oil WTI", "Brent Crude Oil"],
        max_selections=5
    )
    
    # Transformation en liste de tickers (=F)
    ticker_list = [energy_tickers[x] for x in choice_energy]
    
    if ticker_list:
        data = get_last_data(ticker_list, start_date, end_date)
        
        # 1. Dashboard de Prix (Metrics)
        # On vérifie que len(ticker_list) > 0 pour éviter l'erreur spec
        cols = st.columns(len(ticker_list))
        for i, t in enumerate(ticker_list):
            if t in data and not data[t].empty:
                last_p = data[t]['Close'].iloc[-1]
                prev_p = data[t]['Close'].iloc[-2]
                change = ((last_p / prev_p) - 1) * 100
                cols[i].metric(names[t], f"${last_p:.2f}", f"{change:.2f}%")

        # 2. Graphique de Performance Relative
        st.subheader("Performance Chart")
        choice_relative = st.checkbox("Normalize performance (to base 100)", value=True)
        
        fig_perf = go.Figure()
        for t in ticker_list:
            if t in data and not data[t].empty:
                y_val = data[t]["Close"]
                if choice_relative:
                    y_val = (y_val / y_val.iloc[0]) * 100
                
                fig_perf.add_trace(go.Scatter(x=y_val.index, y=y_val, name=names[t]))
        
        fig_perf.update_layout(
            template="plotly_white", 
            hovermode="x unified", 
            yaxis_title="Base 100" if choice_relative else "Price ($)"
        )
        st.plotly_chart(fig_perf, use_container_width=True)
        # --- 3. MOMENTUM METRICS (FIXED DISPLAY) ---
        st.text("Z-score :")     
        # On recrée une nouvelle rangée de colonnes pour les metrics de momentum
        mom_cols = st.columns(len(ticker_list))
    
        with st.expander("How to interpret Momentum & Z-Score?"):
            st.write("""
            The **Z-Score** measures how far the current price is from its 30-day average (SMA).
            - **Overbought (Z > 1.5):** The price is significantly higher than its recent average. It might be "too expensive" and due for a correction.
            - **Oversold (Z < -1.5):** The price is significantly lower than its recent average. It might be "too cheap" and due for a rebound.
            - **Neutral (-1.5 to 1.5):** The price is moving within its normal statistical range.
            """)
        for i, t in enumerate(ticker_list):
            if t in data:
                prices = data[t]['Close']
                # Window of 20 days for SMA/STD
                sma = prices.rolling(window=30).mean().iloc[-1]
                std = prices.rolling(window=30).std().iloc[-1]
                
                # Avoid division by zero
                z_score = (prices.iloc[-1] - sma) / std if std != 0 else 0
                
                # Logic for color and status
                if z_score > 1.5:
                    status = "Overbought"
                    d_color = "inverse" # Red
                elif z_score < -1.5:
                    status = "Oversold"
                    d_color = "normal"  # Green
                else:
                    status = "Neutral"
                    d_color = "off"     # Gray

                mom_cols[i].metric(
                    label=f"{names[t]} Momentum", 
                    value=round(z_score,2), 
                    delta=status,
                    delta_color=d_color
                )
            

        choice=st.selectbox(label="Analyze metrics",
                            options=["Spread between two energy","Rolling volatility","Processed volume","Corrélation","Saisonnalité","Energy vs Inflation & Rates"])
        
        #Spread bewteen asset
        if choice=="Spread between two energy":

            if len(choice_energy)>=2:
                fig_spread=go.Figure()
                c1,c2=st.columns(2)
                name_energy1=c1.selectbox(label="First Energy",
                            index=0,
                            options=choice_energy)
                name_energy2=c2.selectbox(label="Second Energy",
                            index=1,
                            options=choice_energy)
                energy1=energy_tickers[name_energy1]
                energy2=energy_tickers[name_energy2]
                spread = data[energy1]['Close'] - data[energy2]['Close']
                
                fig_spread = px.area(
                    x=spread.index, 
                    y=spread, 
                    title= name_energy1+" VS "+name_energy2+" Spread ($)",
                    labels={'y': 'Spread Value ($)', 'x': 'Date'},
                    color_discrete_sequence=['#ef553b']
                )
                st.plotly_chart(fig_spread, use_container_width=True)
                st.metric("Actual spread bewteen "+name_energy1 +" and " +name_energy2, f"${spread[-1]:.2f}", f"{ ((spread[-1] / spread[-2]) - 1) * 100:.2f}%")
            else :
                st.warning("Please select more assets.")
        if choice=="Rolling volatility":
            st.subheader("Rolling Volatility")
            fig_perf = go.Figure()
            for ticker,name_ticker in zip(ticker_list,choice_energy):
                rolling=rolling_volatility(data[ticker])
                fig_perf.add_trace(go.Scatter(x=rolling.index, y=rolling, name=name_ticker))
            fig_perf.update_layout(
                template="plotly_white", 
                yaxis_title="Volatility annual (%)",
                xaxis_title="Days",
            )
            st.plotly_chart(fig_perf, use_container_width=True)
            cols=st.columns(len(ticker_list))
            for col,ticker,name_ticker in zip(cols,ticker_list,choice_energy):
                col.text(name_ticker)
                col.metric(label="Volatility (%)",value=round(volatility(data[ticker]),2))
        if choice=="Processed volume":
            st.subheader("Processed volume")
            choice_relative_vol=st.checkbox("Normalize performance ( to base 100 )",value=True)
            fig_perf = go.Figure()
            for ticker,name_ticker in zip(ticker_list,choice_energy):
                volume=data[ticker]["Volume"]
                if choice_relative_vol:
                    volume_relat = (volume / volume.iloc[0]) * 100
                else :
                    volume_relat=volume
                fig_perf.add_trace(go.Scatter(x=volume_relat.index, y=volume_relat, name=name_ticker))
            fig_perf.update_layout(
                template="plotly_white", 
                yaxis_title="Volume",
                xaxis_title="Days",
            )
            st.plotly_chart(fig_perf, use_container_width=True)
            cols=st.columns(len(ticker_list))
            for col,ticker,name_ticker in zip(cols,ticker_list,choice_energy):
                col.text(name_ticker)
                col.metric(label="Average volume (days)",value=round(data[ticker]["Volume"].mean()))
                col.metric(label="Max volume (in one days)",value=round(data[ticker]["Volume"].max()))
        if choice=="Corrélation":
            df_returns = pd.DataFrame()
            for ticker in ticker_list:
                if ticker in data:
                    df_returns[ticker] = get_returns(data[ticker])
            
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
        if choice == "Saisonnalité":
            st.subheader("Monthly Seasonality (Last 5 Years)")
            # On prend une période plus longue pour la saisonnalité
            long_data = get_last_data(ticker_list, today - pd.DateOffset(years=5), today)
            
            selected_ticker = st.selectbox("Select asset for seasonality", options=ticker_list, format_func=lambda x: names[x])
            
            df_seas = long_data[selected_ticker].copy()
            df_seas['Month'] = df_seas.index.month
            # Calcul de la performance mensuelle moyenne
            monthly_perf = df_seas.groupby('Month')['Close'].apply(lambda x: x.pct_change().mean() * 100)
            
            fig_seas = px.bar(
                x=[datetime(2000, m, 1).strftime('%b') for m in monthly_perf.index],
                y=monthly_perf.values,
                title=f"Average Monthly Performance - {names[selected_ticker]}",
                labels={'x': 'Month', 'y': 'Average Return (%)'},
                color=monthly_perf.values,
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_seas, use_container_width=True)
        
        if choice == "Energy vs Inflation & Rates":
            st.subheader("Energy, Inflation & Interest Rates")
            
            # 1. Selection of study zone and assets
            c1, c2 = st.columns(2)
            name_ref = c1.selectbox(label="Reference Asset", options=choice_energy)
            ref_asset = energy_tickers[name_ref]
            
            zone = c2.selectbox(label="Study Zone", options=["Europe", "Americas"])
            
            # Define tickers based on zone
            if zone == "Europe":
                # INFL.PA (Lyxor Inflation) | IBGL.AS (Euro Gov Bond 15-30y as yield proxy)
                m_tickers = {"Inflation Proxy": "INFL.PA", "Yield Proxy": "IBGL.AS"}
            else:
                # TIP (iShares TIPS) | ^TNX (10Y Treasury Yield)
                m_tickers = {"Inflation Proxy": "TIP", "Yield Proxy": "^TNX"}

            # Fetch macro data
            macro_data = get_last_data(list(m_tickers.values()), start_date, end_date)
            
            if macro_data and ref_asset in data:
                fig_macro = go.Figure()
                
                # --- 1. DATA NORMALIZATION ---
                # Energy Asset
                oil_series = data[ref_asset]['Close']
                oil_norm = (oil_series / oil_series.iloc[0]) * 100
                
                # Inflation Proxy
                inf_ticker = m_tickers["Inflation Proxy"]
                inf_series = macro_data[inf_ticker]['Close']
                inf_norm = (inf_series / inf_series.iloc[0]) * 100
                
                # Yield Data
                yield_ticker = m_tickers["Yield Proxy"]
                y_data = macro_data[yield_ticker]['Close']
                
                # --- 2. CHART BUILDING ---
                fig_macro.add_trace(go.Scatter(x=oil_norm.index, y=oil_norm, name=f"{name_ref} (Price)"))
                fig_macro.add_trace(go.Scatter(x=inf_norm.index, y=inf_norm, name=f"{zone} Inflation Proxy"))
                
                fig_macro.add_trace(go.Scatter(
                    x=y_data.index, y=y_data, 
                    name=f"{zone} Yield/Rates", 
                    yaxis="y2", 
                    line=dict(dash='dot', color='gray')
                ))

                fig_macro.update_layout(
                    template="plotly_white",
                    yaxis=dict(title="Performance (Base 100)"),
                    yaxis2=dict(title="Yield / Rate (%)", overlaying="y", side="right"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig_macro, use_container_width=True)

                # --- 4. DYNAMIC MARKET INSIGHTS ---
                oil_perf = ((oil_norm.iloc[-1] / oil_norm.iloc[0]) - 1) * 100
                inf_perf = ((inf_norm.iloc[-1] / inf_norm.iloc[0]) - 1) * 100
                correlation = oil_norm.corr(inf_norm)
                
                # Determine the context
                if oil_perf > inf_perf and oil_perf > 0:
                    insight_status = "**Energy-Driven Inflation**"
                    explanation = f"{name_ref} is outperforming inflation proxies (+{oil_perf:.1f}% vs +{inf_perf:.1f}%). Energy is likely driving CPI up."
                elif oil_perf < inf_perf and oil_perf > 0:
                    insight_status = "**Absorbed Inflation**"
                    explanation = f"Inflation is outpacing {name_ref}. Prices are rising due to other macro factors (labor, services)."
                else:
                    insight_status = "**Deflationary Pressure**"
                    explanation = f"Both energy and inflation proxies show negative or weak momentum, suggesting an economic slowdown."

                st.info(f"{insight_status} : {explanation}")

                # Correlation check
                if correlation > 0.7:
                    st.success(f"🔗 **Strong Correlation ({correlation:.2f}):** Energy and Inflation are tightly linked. Watch for Central Bank rate hikes.")
                elif correlation < 0:
                    st.warning(f"🔄 **Divergence ({correlation:.2f}):** Energy prices are decoupled from inflation expectations.")

            else:
                st.error("Macro data unavailable for the selected period.")
                        



    else:
        st.warning("Please select at least one asset to display the analysis.")

def aff_energy2():

    """
    df = get_mock_data()

    # --- CALCULS STATISTIQUES (LOGIQUE MÉTIER) ---
    window = 20
    # 1. Log-Returns
    df['Returns'] = np.log(df['Close'] / df['Close'].shift(1))
    # 2. Rolling Volatility (annualisée 252 jours)
    df['Volatility'] = df['Returns'].rolling(window=window).std() * np.sqrt(252)
    # 3. Z-Score
    df['Mean_Price'] = df['Close'].rolling(window=window).mean()
    df['Std_Price'] = df['Close'].rolling(window=window).std()
    df['Z-Score'] = (df['Close'] - df['Mean_Price']) / df['Std_Price']

    # --- INTERFACE STREAMLIT ---
    st.title("⚡ Bloc A : Market Data Analysis")
    st.markdown("---")

    # Row 1: Graphique Maître (Price Action + Volatilité)
    st.subheader("1. Graphique Maître : Spot vs Futures")
    fig_master = go.Figure()

    # Candlestick
    fig_master.add_trace(go.Candlestick(
        x=df['Date'], open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name="Spot Price"
    ))
    # Overlay Future
    fig_master.add_trace(go.Scatter(x=df['Date'], y=df['Future_M1'], name="Future M+1", line=dict(color='orange', width=1.5)))
    # Overlay Volatilité (Area chart sur axe secondaire)
    fig_master.add_trace(go.Scatter(x=df['Date'], y=df['Volatility']*100, name="Vol (pts)", fill='tozeroy', yaxis="y2", opacity=0.3, line=dict(color='gray')))

    fig_master.update_layout(
        height=600,
        yaxis=dict(title="Prix (€/MWh)"),
        yaxis2=dict(title="Volatilité %", overlaying="y", side="right"),
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_master, use_container_width=True)

    # Row 2: Forward Curve & Heatmap
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("2. Forward Curve (Structure)")
        # Simulation de la courbe à date T
        maturities = ['Spot', 'Month+1', 'Quarter+1', 'Year+1', 'Year+2']
        prices = [df['Close'].iloc[-1], df['Future_M1'].iloc[-1], 65, 72, 68] # Scénario mix
        
        fig_forward = px.line(x=maturities, y=prices, markers=True, template="plotly_dark")
        fig_forward.update_traces(line_color='#00CC96', line_width=4)
        # Détection automatique Contango/Backwardation
        status = "Contango" if prices[1] > prices[0] else "Backwardation"
        st.plotly_chart(fig_forward, use_container_width=True)
        st.info(f"Structure actuelle : **{status}**")

    with col2:
        st.subheader("3. Heatmap des Rendements")
        # Simulation de données de returns
        assets = ['Elec Base', 'Elec Peak', 'Gas TTF', 'CO2 EUA']
        periods = ['1D', '1W', '1M', 'YTD']
        heat_data = np.random.uniform(-0.06, 0.06, size=(4, 4))
        
        fig_heat = px.imshow(heat_data, x=periods, y=assets, text_auto=".2%", color_continuous_scale='RdYlGn', template="plotly_dark")
        st.plotly_chart(fig_heat, use_container_width=True)

    # Row 3: Statistiques & Volume/OI
    st.markdown("---")
    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        st.subheader("Z-Score (20D)")
        current_z = df['Z-Score'].iloc[-1]
        fig_z = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = current_z,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {'axis': {'range': [-3, 3]}, 'bar': {'color': "white"},
                    'steps': [
                        {'range': [-3, -2], 'color': "blue"},
                        {'range': [2, 3], 'color': "red"}]}
        ))
        fig_z.update_layout(height=250, margin=dict(t=0, b=0), template="plotly_dark")
        st.plotly_chart(fig_z, use_container_width=True)

    with c2:
        st.subheader("Distribution Returns")
        fig_hist = px.histogram(df, x="Returns", nbins=30, template="plotly_dark")
        st.plotly_chart(fig_hist, use_container_width=True)

    with c3:
        st.subheader("Corrélation Volume / Open Interest")
        fig_voi = go.Figure()
        fig_voi.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name="Volume", marker_color='rgba(100,100,100,0.5)'))
        fig_voi.add_trace(go.Scatter(x=df['Date'], y=df['OI'], name="Open Interest", line=dict(color='cyan')))
        fig_voi.update_layout(height=300, template="plotly_dark", margin=dict(t=0))
        st.plotly_chart(fig_voi, use_container_width=True)
"""


def aff_metal():
    st.header("Metal Sector Analysis")
    today = datetime.today()
    
    # 1. Gestion des dates
    c1, c2 = st.columns(2)
    start_date = c1.date_input("Start Date", today - pd.DateOffset(years=1), max_value=today, key="metal_start")
    end_date = c2.date_input("End Date", today, min_value=start_date, max_value=today, key="metal_end")

    # 2. Sélection du groupe de métaux
    choice_type_metal = st.selectbox(
        label="Select Category",
        options=["Precious", "Industrial", "Battery & tech metals"],
        key="metal_type_selector"
    )

    # Définition du dictionnaire d'options selon le type
    if choice_type_metal == "Precious":
        options_available = ["Gold", "Silver", "Platinum", "Palladium"]
    elif choice_type_metal == "Industrial":
        options_available = ["Copper", "Aluminum", "Steel (HRC)", "Iron Ore", "Zinc", "Lead", "Tin"]
    else:
        options_available = ["Nickel", "Lithium (Index)", "Cobalt", "Magnesium"]
    
    # 3. NOUVEAU : Multiselect pour choisir précisément les assets
    selected_assets = st.multiselect(
        label=f"Choose {choice_type_metal} assets to analyze",
        options=options_available,
        default=options_available[:2], # Par défaut on en prend 2
        key="metal_assets_multiselect"
    )
    
    # Dictionnaire inverse pour les labels
    names_metal = {v: k for k, v in metal_tickers.items()}
    
    # Transformation en liste de tickers
    ticker_list = [metal_tickers[x] for x in selected_assets if x in metal_tickers]
    
    if ticker_list:
        data = get_last_data(ticker_list, start_date, end_date)
        valid_tickers = [t for t in ticker_list if t in data and not data[t].empty]
        
        if valid_tickers:
            # --- 1. DASHBOARD DE PRIX (Metrics) ---
            cols_per_row = 4
            for i in range(0, len(valid_tickers), cols_per_row):
                current_batch = valid_tickers[i : i + cols_per_row]
                cols = st.columns(len(current_batch))
                for j, t in enumerate(current_batch):
                    last_p = data[t]['Close'].iloc[-1]
                    prev_p = data[t]['Close'].iloc[-2]
                    change = ((last_p / prev_p) - 1) * 100
                    cols[j].metric(names_metal[t], f"${last_p:.2f}", f"{change:.2f}%")

            # --- 2. GRAPHIQUE DE PERFORMANCE ---
            st.subheader("Performance Chart")
            choice_relative = st.checkbox("Normalize (Base 100)", value=True, key="metal_rel_perf")
            
            fig_perf = go.Figure()
            for t in valid_tickers:
                y_val = data[t]["Close"]
                if choice_relative:
                    y_val = (y_val / y_val.iloc[0]) * 100
                fig_perf.add_trace(go.Scatter(x=y_val.index, y=y_val, name=names_metal[t]))
            
            fig_perf.update_layout(template="plotly_white", hovermode="x unified")
            st.plotly_chart(fig_perf, use_container_width=True)

            # --- 3. MOMENTUM (Z-SCORE) ---
            st.write("**Market Momentum (Z-Score 30D) :**")
            for i in range(0, len(valid_tickers), cols_per_row):
                current_batch = valid_tickers[i : i + cols_per_row]
                mom_cols = st.columns(len(current_batch))
                for j, t in enumerate(current_batch):
                    prices = data[t]['Close']
                    if len(prices) > 30:
                        sma = prices.rolling(window=30).mean().iloc[-1]
                        std = prices.rolling(window=30).std().iloc[-1]
                        z_score = (prices.iloc[-1] - sma) / std if std != 0 else 0
                        
                        status = "Overbought" if z_score > 1.5 else "Oversold" if z_score < -1.5 else "Neutral"
                        d_color = "inverse" if z_score > 1.5 else "normal" if z_score < -1.5 else "off"

                        mom_cols[j].metric(label=names_metal[t], value=round(z_score, 2), delta=status, delta_color=d_color)
        else:
            st.error("No data found for the selected assets.")
    else:
        st.info("Please select at least one asset to see the analysis.")

    choice=st.selectbox(label="Analyze metrics",
                            options=["Rolling volatility","Saisonnalité"])
    if choice=="Rolling volatility":
        st.subheader("Rolling Volatility")
        fig_perf = go.Figure()
        for ticker,name_ticker in zip(ticker_list,selected_assets):
            rolling=rolling_volatility(data[ticker])
            fig_perf.add_trace(go.Scatter(x=rolling.index, y=rolling, name=name_ticker))
        fig_perf.update_layout(
            template="plotly_white", 
            yaxis_title="Volatility annual (%)",
            xaxis_title="Days",
        )
        st.plotly_chart(fig_perf, use_container_width=True)
        cols=st.columns(len(ticker_list))
        for col,ticker,name_ticker in zip(cols,ticker_list,selected_assets):
            col.text(name_ticker)
            col.metric(label="Volatility (%)",value=round(volatility(data[ticker]),2))
    if choice == "Saisonnalité":
        st.subheader("Monthly Seasonality (Last 5 Years)")
        # On prend une période plus longue pour la saisonnalité
        long_data = get_last_data(ticker_list, today - pd.DateOffset(years=5), today)
        
        selected_ticker = st.selectbox("Select asset for seasonality", options=ticker_list, format_func=lambda x: names_metal[x])
        
        df_seas = long_data[selected_ticker].copy()
        df_seas['Month'] = df_seas.index.month
        # Calcul de la performance mensuelle moyenne
        monthly_perf = df_seas.groupby('Month')['Close'].apply(lambda x: x.pct_change().mean() * 100)
        
        fig_seas = px.bar(
            x=[datetime(2000, m, 1).strftime('%b') for m in monthly_perf.index],
            y=monthly_perf.values,
            title=f"Average Monthly Performance - {names_metal[selected_ticker]}",
            labels={'x': 'Month', 'y': 'Average Return (%)'},
            color=monthly_perf.values,
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig_seas, use_container_width=True)
    
        
def aff_agri():
    return 0

def aff_live():
    return 0


def affichage_commo():
    general_aff,energy,energy2,metal,agri,livestock=st.tabs(["General","Energy","Energy Test Evolution","Metals","Agriculture","Livestock"])
    with general_aff:
        aff_general()
    with energy:
        aff_energy()
    with energy2:
        aff_energy2()
    with metal:
        aff_metal()
    with agri:
        aff_agri()
    with livestock:
        aff_live()
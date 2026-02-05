import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from scipy.stats import gaussian_kde
from scipy.stats import norm
import plotly.express as px

from data.download_report_metal import telecharger_rapport_lme,traiter_rapport_cotr,get_full_cme_data_direct,colonnes_importantes_cme
from app.metrics_metal import calc_speculative_sentiment,calc_hedging_pressure,calc_market_conviction,metric_speculative_net_pos,metric_hedging_pressure,metric_crowding_score_improved,metric_commercial_spec_divergence,metric_market_conviction,metric_spreading_intensity
from data.list_asset import commodities_dict,energy_tickers,fx_tickers,metal_tickers
from data.data import get_last_data
from app.metrics_general import rolling_volatility,volatility,get_returns,rolling_corr,cor,max_drawdown

def aff_general():
    st.header("Commodities Market Overview")
    st.caption("Global performance across Energy, Metals, Agriculture and Livestock sectors")
    
    today = datetime.today()
    
    # === DATE SELECTOR ===
    col1, col2 = st.columns(2)
    start_date = col1.date_input(
        label="Start Date",
        value=today - pd.DateOffset(months=3),
        max_value=today,
        key="general_start"
    )
    end_date = col2.date_input(
        label="End Date",
        value=today,
        min_value=start_date,
        max_value=today,
        key="general_end"
    )
    # === BUILD ASSET UNIVERSE ===
    # Select key representatives from each category
    
    all_asset=metal_tickers |energy_tickers
    
    # Download data
    ticker_list = list(all_asset.values())
    data = get_last_data(ticker_list, start_date, end_date)
    
    if not data:
        st.warning("No data available for the selected period.")
        return
    # Calculate returns for all assets
    returns_data = {}
    for asset_name,ticker in all_asset.items():
        if ticker in data and not data[ticker].empty:
            returns = get_returns(data[ticker])
            if not returns.empty:
                returns_data[asset_name] = returns
    
    # === 5. NORMALIZED PRICE COMPARISON ===
    st.divider()
    st.subheader("Multi-Asset Price Evolution (Base 100)")
    st.caption("Compare relative performance of all commodities from the start date")
    
    selected_comparison = st.multiselect(
        "Select assets to compare",
        options=list(all_asset.keys()),
        default=["Crude Oil WTI", "Gold", "Copper", "Natural Gas Henry Hub"]
    )
    
    if selected_comparison:
        fig_comparison = go.Figure()
        
        for asset_name in selected_comparison:
            ticker = all_asset[asset_name]
            if ticker in data and not data[ticker].empty:
                prices = data[ticker]['Close']
                normalized = (prices / prices.iloc[0]) * 100
                fig_comparison.add_trace(
                    go.Scatter(
                        x=normalized.index,
                        y=normalized,
                        name=asset_name,
                        mode='lines'
                    )
                )
        
        fig_comparison.update_layout(
            template="plotly_white",
            hovermode="x unified",
            yaxis_title="Base 100",
            xaxis_title="Date",
            height=500
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
    st.divider()
    choice_metric=st.selectbox(label="Choose your comparaison :",options=["Performance Heatmap","Cross-Asset Correlation Matrix","Sector Performance Comparison","Volatility Ranking"])

    if choice_metric=="Performance Heatmap":

        st.subheader("Performance Heatmap")
        st.caption("Returns across multiple timeframes - darker green = better performance")
        
        periods = {
            "1D": 1,
            "1W": 5,
            "1M": 21,
            "3M": 63,
            "YTD": None  # Will calculate from year start
        }
        
        selected_perf = st.multiselect(
        "Select assets to compare",
        options=list(all_asset.keys()),
        default=["Crude Oil WTI", "Gold", "Copper", "Natural Gas Henry Hub"],
        key="Perofrmance heatmap"
        )   
        performance_data = []
        
        for asset_name in selected_perf:    
            ticker=all_asset[asset_name]
            if ticker in data and not data[ticker].empty:
                asset_perf = {"Asset": asset_name}
                prices = data[ticker]['Close']
                
                for period_name, days_back in periods.items():
                    if period_name == "YTD":
                        # Calculate from start of year
                        year_start = datetime(today.year, 1, 1)
                        ytd_prices = prices[prices.index.tz_localize(None) >= year_start]
                        if len(ytd_prices) > 1:
                            perf = ((ytd_prices.iloc[-1] / ytd_prices.iloc[0]) - 1) * 100
                        else:
                            perf = 0
                    else:
                        if len(prices) > days_back:
                            perf = ((prices.iloc[-1] / prices.iloc[-days_back]) - 1) * 100
                        else:
                            perf = 0
                    
                    asset_perf[period_name] = round(perf, 2)
                
                performance_data.append(asset_perf)
        
        if performance_data:
            df_perf = pd.DataFrame(performance_data)
            df_perf = df_perf.set_index("Asset")
            
            # Create heatmap
            fig_heatmap = px.imshow(
                df_perf,
                text_auto=".1f",
                aspect="auto",
                color_continuous_scale='RdYlGn',
                color_continuous_midpoint=0,
                labels=dict(color="Return (%)"),
                zmin=-10, zmax=10
            )
            
            fig_heatmap.update_layout(
                template="plotly_white",
                height=400,
                xaxis_title="Period",
                yaxis_title="Commodity"
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # === 2. TOP MOVERS ===
        st.divider()
        col_gain, col_loss = st.columns(2)
        
        # Calculate 1D performance for ranking
        daily_movers = []
        for asset_name, ticker in all_asset.items():
            if ticker in data and len(data[ticker]) >= 2:
                last_price = data[ticker]['Close'].iloc[-1]
                prev_price = data[ticker]['Close'].iloc[-2]
                daily_change = ((last_price / prev_price) - 1) * 100
                daily_movers.append({
                    "Asset": asset_name,
                    "Change": daily_change,
                    "Price": last_price
                })
        
        df_movers = pd.DataFrame(daily_movers).sort_values("Change", ascending=False)
        
        with col_gain:
            st.markdown("Top Gainers (24h)")
            top_gainers = df_movers.head(4)
            for _, row in top_gainers.iterrows():
                st.metric(
                    label=row['Asset'],
                    value=f"${row['Price']:.2f}",
                    delta=f"{row['Change']:.2f}%"
                )
        
        with col_loss:
            st.markdown("Top Losers (24h)")
            top_losers = df_movers.tail(4).sort_values("Change")
            for _, row in top_losers.iterrows():
                st.metric(
                    label=row['Asset'],
                    value=f"${row['Price']:.2f}",
                    delta=f"{row['Change']:.2f}%"
                )
    
    if choice_metric=="Cross-Asset Correlation Matrix":
     
        st.subheader("Cross-Asset Correlation Matrix")
        st.caption("How different commodities move together (based on daily returns)")
        
        selected_cross_asset = st.multiselect(
        "Select assets to compare",
        options=list(all_asset.keys()),
        default=["Crude Oil WTI", "Gold", "Copper", "Natural Gas Henry Hub"],
        key="cross asset"
        ) 
       
        if len(selected_cross_asset) > 1:
            df_returns=pd.DataFrame()
            for x in selected_cross_asset:
                df_returns[x]=returns_data[x]
            corr_matrix = df_returns.corr()
            
            fig_corr = px.imshow(
                corr_matrix,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale='RdBu_r',
                labels=dict(color="Correlation"),
                zmin=-1, zmax=1
            )
            
            fig_corr.update_layout(
                template="plotly_white",
                height=600,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig_corr, use_container_width=True)
            
               
    if choice_metric=="Sector Performance Comparison":

        st.subheader("Sector Performance Comparison")
        st.caption("Compare average performance by commodity sector")
        
        # Group assets by sector
        sectors = {
            "Oil": ["Crude Oil WTI", "Brent Crude"],
            "Gaz":["Natural Gas Henry Hub","European Natural Gas (TTF)","UK Natural Gas"],
            "Electricity":["PJM Electricity","California Electricity","German Power Baseload"],
            "Precious Metals": ["Gold", "Silver", "Platinum"],
            "Industrial Metals": ["Copper", "Aluminum", "Zinc","Steel (HRC)","Tin"]
        }
    
        
        sector_performance = []
        for sector_name, assets in sectors.items():
            sector_returns = []
            for asset in assets:
                if asset in returns_data:
                    total_return = ((1 + returns_data[asset]).prod() - 1) * 100
                    sector_returns.append(total_return)
            
            if sector_returns:
                avg_return = np.mean(sector_returns)
                sector_performance.append({
                    "Sector": sector_name,
                    "Avg Return (%)": round(avg_return, 2)
                })
        
        if sector_performance:
            df_sectors = pd.DataFrame(sector_performance)
            
            fig_sectors = px.bar(
                df_sectors,
                x="Sector",
                y="Avg Return (%)",
                color="Avg Return (%)",
                color_continuous_scale='RdYlGn',
                color_continuous_midpoint=0,
                text="Avg Return (%)"
            )
            
            fig_sectors.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_sectors.update_layout(
                template="plotly_white",
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_sectors, use_container_width=True)
        
        
    if choice_metric=="Volatility Ranking":

        st.subheader("Volatility Ranking")
        st.caption("Which commodities are most volatile? (30-day annualized volatility)")
        
        selected_comp_vol= st.multiselect(
        "Select assets to compare",
        options=list(all_asset.keys()),
        default=["Crude Oil WTI", "Gold", "Copper", "Natural Gas Henry Hub"],
        key="commo_selec_vol"
    )
        volatility_data = []
        for asset_name in selected_comp_vol:
            ticker=all_asset[asset_name]
            if ticker in data and not data[ticker].empty:
                vol = volatility(data[ticker])
                volatility_data.append({
                    "Asset": asset_name,
                    "Volatility (%)": round(vol, 2)
                })
        
        if volatility_data:
            df_vol = pd.DataFrame(volatility_data).sort_values("Volatility (%)", ascending=False)
            
            fig_vol = px.bar(
                df_vol,
                x="Volatility (%)",
                y="Asset",
                orientation='h',
                color="Volatility (%)",
                color_continuous_scale='Reds'
            )
            
            fig_vol.update_layout(
                template="plotly_white",
                height=500,
                showlegend=False
            )
            
            st.plotly_chart(fig_vol, use_container_width=True)

def aff_energy():
    st.header("Energy Sector Analysis")
    st.caption("Analyze energy prices, volatility, correlations and macro indicators")
    today = datetime.today()
    
    # 1. Date management
    col1, col2 = st.columns(2)
    start_date = col1.date_input(
        label="Start Date",
        value=today - pd.DateOffset(years=1),
        max_value=today,
        key="energy_start"
    )
    end_date = col2.date_input(
        label="End Date",
        value=today,
        min_value=start_date,
        max_value=today,
        key="energy_end"
    )

    # Reverse dictionary to find name from ticker
    ticker_to_name = {v: k for k, v in energy_tickers.items()}
    
    # 2. Energy assets selection
    selected_energy = st.multiselect(
        "Choose your energy assets",
        options=list(energy_tickers.keys()),
        default=["Crude Oil WTI", "Brent Crude Oil"],
        max_selections=5
    )
    
    # Convert to ticker list
    ticker_list = [energy_tickers[x] for x in selected_energy]
    
    if ticker_list:
        data = get_last_data(ticker_list, start_date, end_date)
        
        # --- 1. PRICE DASHBOARD ---
        cols = st.columns(len(ticker_list))
        for i, ticker in enumerate(ticker_list):
            if ticker in data and not data[ticker].empty:
                last_price = data[ticker]['Close'].iloc[-1]
                prev_price = data[ticker]['Close'].iloc[-2]
                price_change = ((last_price / prev_price) - 1) * 100
                cols[i].metric(ticker_to_name[ticker], f"${last_price:.2f}", f"{price_change:.2f}%")

        # --- 2. PERFORMANCE CHART ---
        st.subheader("Performance Chart")
        st.caption("Compare price evolution over the selected period")
        normalize_chart = st.checkbox("Normalize performance (to base 100)", value=True, key="energy_normalize_chart")
        
        fig_perf = go.Figure()
        for ticker in ticker_list:
            if ticker in data and not data[ticker].empty:
                y_values = data[ticker]["Close"]
                if normalize_chart:
                    y_values = (y_values / y_values.iloc[0]) * 100
                
                fig_perf.add_trace(go.Scatter(x=y_values.index, y=y_values, name=ticker_to_name[ticker]))
        
        fig_perf.update_layout(
            template="plotly_white", 
            hovermode="x unified", 
            yaxis_title="Base 100" if normalize_chart else "Price ($)"
        )
        st.plotly_chart(fig_perf, use_container_width=True)
        
        # --- 3. MOMENTUM METRICS ---
        st.text("Market Momentum (Z-Score 30D)")
        st.caption("Z-Score > 1.5: Overbought | Z-Score < -1.5: Oversold | Between: Neutral")
        
        with st.expander("How to interpret Momentum & Z-Score?"):
            st.write("""
            The **Z-Score** measures how far the current price is from its 30-day average (SMA).
            - **Overbought (Z > 1.5):** The price is significantly higher than its recent average. It might be "too expensive" and due for a correction.
            - **Oversold (Z < -1.5):** The price is significantly lower than its recent average. It might be "too cheap" and due for a rebound.
            - **Neutral (-1.5 to 1.5):** The price is moving within its normal statistical range.
            """)
        
        momentum_cols = st.columns(len(ticker_list))
        for i, ticker in enumerate(ticker_list):
            if ticker in data:
                prices = data[ticker]['Close']
                moving_avg = prices.rolling(window=30).mean().iloc[-1]
                std_dev = prices.rolling(window=30).std().iloc[-1]
                
                z_score = (prices.iloc[-1] - moving_avg) / std_dev if std_dev != 0 else 0
                
                # Determine momentum status
                if z_score > 1.5:
                    status = "Overbought"
                    delta_color = "inverse"
                elif z_score < -1.5:
                    status = "Oversold"
                    delta_color = "normal"
                else:
                    status = "Neutral"
                    delta_color = "off"

                momentum_cols[i].metric(
                    label=f"{ticker_to_name[ticker]} Momentum", 
                    value=round(z_score, 2), 
                    delta=status,
                    delta_color=delta_color
                )
        
        # --- 4. ADVANCED ANALYTICS ---
        st.divider()
        st.subheader("Advanced Analytics")
        metric_choice = st.selectbox(
            label="Analyze metrics",
            options=["Spread between two energy", "Rolling volatility", "Processed volume", 
                     "Correlation", "Seasonality", "Energy vs Inflation & Rates"]
        )
        
        # --- SPREAD ANALYSIS ---
        if metric_choice == "Spread between two energy":
            st.caption("Analyze the price difference between two energy commodities")
            
            if len(selected_energy) >= 2:
                col1, col2 = st.columns(2)
                energy_name1 = col1.selectbox(label="First Energy", index=0, options=selected_energy)
                energy_name2 = col2.selectbox(label="Second Energy", index=1, options=selected_energy)
                
                energy_ticker1 = energy_tickers[energy_name1]
                energy_ticker2 = energy_tickers[energy_name2]
                spread = data[energy_ticker1]['Close'] - data[energy_ticker2]['Close']
                
                fig_spread = px.area(
                    x=spread.index, 
                    y=spread, 
                    title=f"{energy_name1} vs {energy_name2} Spread ($)",
                    labels={'y': 'Spread Value ($)', 'x': 'Date'},
                    color_discrete_sequence=['#ef553b']
                )
                st.plotly_chart(fig_spread, use_container_width=True)
                
                spread_change = ((spread.iloc[-1] / spread.iloc[-2]) - 1) * 100
                st.metric(
                    f"Current spread between {energy_name1} and {energy_name2}", 
                    f"${spread.iloc[-1]:.2f}", 
                    f"{spread_change:.2f}%"
                )
            else:
                st.warning("Please select at least 2 assets to analyze spread.")
        
        # --- ROLLING VOLATILITY ---
        elif metric_choice == "Rolling volatility":
            st.caption("Measure price volatility over time")
            
            fig_vol = go.Figure()
            for ticker, energy_name in zip(ticker_list, selected_energy):
                rolling_vol = rolling_volatility(data[ticker])
                fig_vol.add_trace(go.Scatter(x=rolling_vol.index, y=rolling_vol, name=energy_name))
            
            fig_vol.update_layout(
                template="plotly_white", 
                yaxis_title="Annual Volatility (%)",
                xaxis_title="Date"
            )
            st.plotly_chart(fig_vol, use_container_width=True)
            
            vol_cols = st.columns(len(ticker_list))
            for col, ticker, energy_name in zip(vol_cols, ticker_list, selected_energy):
                with col:
                    st.markdown(f"**{energy_name}**")
                    st.metric(label="Volatility (%)", value=round(volatility(data[ticker]), 2))
        
        # --- VOLUME ANALYSIS ---
        elif metric_choice == "Processed volume":
            st.caption("Compare trading volume across energy commodities")
            
            normalize_volume = st.checkbox("Normalize performance (to base 100)", value=True, key="energy_normalize_volume")
            
            fig_volume = go.Figure()
            for ticker, energy_name in zip(ticker_list, selected_energy):
                volume = data[ticker]["Volume"]
                if normalize_volume:
                    volume_normalized = (volume / volume.iloc[0]) * 100
                else:
                    volume_normalized = volume
                fig_volume.add_trace(go.Scatter(x=volume_normalized.index, y=volume_normalized, name=energy_name))
            
            fig_volume.update_layout(
                template="plotly_white", 
                yaxis_title="Volume",
                xaxis_title="Date"
            )
            st.plotly_chart(fig_volume, use_container_width=True)
            
            volume_cols = st.columns(len(ticker_list))
            for col, ticker, energy_name in zip(volume_cols, ticker_list, selected_energy):
                with col:
                    st.markdown(f"**{energy_name}**")
                    st.metric(label="Average volume", value=f"{data[ticker]['Volume'].mean():,.0f}")
                    st.metric(label="Max volume", value=f"{data[ticker]['Volume'].max():,.0f}")
        
        # --- CORRELATION MATRIX ---
        elif metric_choice == "Correlation":
            st.caption("Visualize correlations between selected energy assets")
            
            df_returns = pd.DataFrame()
            for ticker in ticker_list:
                if ticker in data:
                    df_returns[ticker] = get_returns(data[ticker])
            
            if df_returns.empty:
                st.error("Insufficient data to calculate correlations.")
            else:
                corr_matrix = df_returns.corr()
                
                fig_corr = px.imshow(
                    corr_matrix,
                    text_auto=".2f",
                    aspect="auto",
                    color_continuous_scale='RdBu_r',
                    labels=dict(color="Correlation"),
                    zmin=-1, zmax=1
                )
                
                fig_corr.update_layout(
                    template="plotly_white",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                
                st.plotly_chart(fig_corr, use_container_width=True)
        
        # --- SEASONALITY ANALYSIS ---
        elif metric_choice == "Seasonality":
            st.caption("Analyze monthly performance patterns over the last 5 years")
            
            long_data = get_last_data(ticker_list, today - pd.DateOffset(years=5), today)
            
            selected_ticker = st.selectbox(
                "Select asset for seasonality", 
                options=ticker_list, 
                format_func=lambda x: ticker_to_name[x]
            )
            
            df_seasonality = long_data[selected_ticker].copy()
            df_seasonality['Month'] = df_seasonality.index.month
            monthly_performance = df_seasonality.groupby('Month')['Close'].apply(lambda x: x.pct_change().mean() * 100)
            
            fig_seasonality = px.bar(
                x=[datetime(2000, m, 1).strftime('%b') for m in monthly_performance.index],
                y=monthly_performance.values,
                title=f"Average Monthly Performance - {ticker_to_name[selected_ticker]}",
                labels={'x': 'Month', 'y': 'Average Return (%)'},
                color=monthly_performance.values,
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_seasonality, use_container_width=True)
        
        # --- ENERGY VS MACRO INDICATORS ---
        elif metric_choice == "Energy vs Inflation & Rates":
            st.caption("Analyze energy prices in relation to inflation and interest rates")
            
            col1, col2 = st.columns(2)
            reference_name = col1.selectbox(label="Reference Asset", options=selected_energy)
            reference_ticker = energy_tickers[reference_name]
            
            study_zone = col2.selectbox(label="Study Zone", options=["Europe", "Americas"])
            
            # Define macro tickers based on zone
            if study_zone == "Europe":
                macro_tickers = {"Inflation Proxy": "INFL.PA", "Yield Proxy": "IBGL.AS"}
            else:
                macro_tickers = {"Inflation Proxy": "TIP", "Yield Proxy": "^TNX"}

            macro_data = get_last_data(list(macro_tickers.values()), start_date, end_date)
            
            if macro_data and reference_ticker in data:
                fig_macro = go.Figure()
                
                # Normalize energy asset
                energy_series = data[reference_ticker]['Close']
                energy_normalized = (energy_series / energy_series.iloc[0]) * 100
                
                # Normalize inflation proxy
                inflation_ticker = macro_tickers["Inflation Proxy"]
                inflation_series = macro_data[inflation_ticker]['Close']
                inflation_normalized = (inflation_series / inflation_series.iloc[0]) * 100
                
                # Yield data
                yield_ticker = macro_tickers["Yield Proxy"]
                yield_data = macro_data[yield_ticker]['Close']
                
                # Build chart
                fig_macro.add_trace(go.Scatter(
                    x=energy_normalized.index, 
                    y=energy_normalized, 
                    name=f"{reference_name} (Price)"
                ))
                fig_macro.add_trace(go.Scatter(
                    x=inflation_normalized.index, 
                    y=inflation_normalized, 
                    name=f"{study_zone} Inflation Proxy"
                ))
                fig_macro.add_trace(go.Scatter(
                    x=yield_data.index, 
                    y=yield_data, 
                    name=f"{study_zone} Yield/Rates", 
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

                # Market insights
                energy_performance = ((energy_normalized.iloc[-1] / energy_normalized.iloc[0]) - 1) * 100
                inflation_performance = ((inflation_normalized.iloc[-1] / inflation_normalized.iloc[0]) - 1) * 100
                correlation = energy_normalized.corr(inflation_normalized)
                
                # Determine market context
                if energy_performance > inflation_performance and energy_performance > 0:
                    insight_status = "**Energy-Driven Inflation**"
                    explanation = f"{reference_name} is outperforming inflation proxies (+{energy_performance:.1f}% vs +{inflation_performance:.1f}%). Energy is likely driving CPI up."
                elif energy_performance < inflation_performance and energy_performance > 0:
                    insight_status = "**Absorbed Inflation**"
                    explanation = f"Inflation is outpacing {reference_name}. Prices are rising due to other macro factors (labor, services)."
                else:
                    insight_status = "**Deflationary Pressure**"
                    explanation = f"Both energy and inflation proxies show negative or weak momentum, suggesting an economic slowdown."

                st.info(f"{insight_status}: {explanation}")

                # Correlation analysis
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
    st.caption("Analyze metal prices, performance and key metrics")
    today = datetime.today()
    
    # 1. Date management
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start Date", today - pd.DateOffset(years=1), max_value=today, key="metal_start")
    end_date = col2.date_input("End Date", today, min_value=start_date, max_value=today, key="metal_end")

    # 2. Metal group selection
    metal_category = st.selectbox(
        label="Select Category",
        options=["Precious", "Industrial", "Battery & tech metals"],
        key="metal_type_selector"
    )

    # Define available options by type
    if metal_category == "Precious":
        available_options = ["Gold", "Silver", "Platinum", "Palladium"]
    elif metal_category == "Industrial":
        available_options = ["Copper", "Aluminum",  "Steel", "Iron Ore", "Zinc", "Lead", "Tin"]
    else:
        available_options = ["Nickel", "Lithium", "Cobalt", "Magnesium"]
    
    # 3. Multiselect to choose specific assets
    selected_metals = st.multiselect(
        label=f"Choose {metal_category} assets to analyze",
        options=available_options,
        default=available_options[:2],
        key="metal_assets_multiselect"
    )
    
    # Reverse dictionary for labels
    ticker_to_name = {v: k for k, v in metal_tickers.items()}
    
    # Convert to ticker list
    ticker_list = [metal_tickers[x] for x in selected_metals if x in metal_tickers]
    
    if ticker_list:
        data = get_last_data(ticker_list, start_date, end_date)
        valid_tickers = [t for t in ticker_list if t in data and not data[t].empty]
        
        if valid_tickers:
            # --- 1. PRICE DASHBOARD (Metrics) ---
    
            cols_per_row = 4
            for i in range(0, len(valid_tickers), cols_per_row):
                current_batch = valid_tickers[i : i + cols_per_row]
                cols = st.columns(len(current_batch))
                for j, ticker in enumerate(current_batch):
                    last_price = data[ticker]['Close'].iloc[-1]
                    prev_price = data[ticker]['Close'].iloc[-2]
                    price_change = ((last_price / prev_price) - 1) * 100
                    cols[j].metric(ticker_to_name[ticker], f"${last_price:.2f}", f"{price_change:.2f}%")

            # --- 2. PERFORMANCE CHART ---
            st.subheader("Performance Chart")
            st.caption("Compare price evolution over the selected period")
            normalize_chart = st.checkbox("Normalize (Base 100)", value=True, key="metal_rel_perf")
            
            fig_perf = go.Figure()
            for ticker in valid_tickers:
                y_values = data[ticker]["Close"]
                if normalize_chart:
                    y_values = (y_values / y_values.iloc[0]) * 100
                fig_perf.add_trace(go.Scatter(x=y_values.index, y=y_values, name=ticker_to_name[ticker]))
            
            fig_perf.update_layout(template="plotly_white", hovermode="x unified")
            st.plotly_chart(fig_perf, use_container_width=True)

            # --- 3. MOMENTUM (Z-SCORE) ---
            st.text("Market Momentum (Z-Score 30D)")
            st.caption("Z-Score > 1.5: Overbought | Z-Score < -1.5: Oversold | Between: Neutral")
            for i in range(0, len(valid_tickers), cols_per_row):
                current_batch = valid_tickers[i : i + cols_per_row]
                momentum_cols = st.columns(len(current_batch))
                for j, ticker in enumerate(current_batch):
                    prices = data[ticker]['Close']
                    if len(prices) > 30:
                        moving_avg = prices.rolling(window=30).mean().iloc[-1]
                        std_dev = prices.rolling(window=30).std().iloc[-1]
                        z_score = (prices.iloc[-1] - moving_avg) / std_dev if std_dev != 0 else 0
                        
                        status = "Overbought" if z_score > 1.5 else "Oversold" if z_score < -1.5 else "Neutral"
                        delta_color = "inverse" if z_score > 1.5 else "normal" if z_score < -1.5 else "off"

                        momentum_cols[j].metric(label=ticker_to_name[ticker], value=round(z_score, 2), delta=status, delta_color=delta_color)

            """
            if metal_category == "Industrial":
                choice_metric_analyse=["Correlation", "Volatility", "Volume", "Max Drawdown"]
            if metal_category == "Precious":     
                choice_metric_analyse=["Correlation", "Volatility", "Volume", "Max Drawdown"]
            if metal_category=="Battery & tech metals":
                choice_metric_analyse=["Correlation", "Volatility", "Volume", "Max Drawdown"]
            """

            st.divider()
            st.subheader("Advanced Analytics")
            metric_choice = st.selectbox(label="Choose your metrics", options=["Correlation", "Volatility", "Volume", "Max Drawdown","Advanced statistics ( LME or CME )"])

            if metric_choice == "Correlation":
                st.caption("Analyze the relationship between two precious metals")
                col1, col2 = st.columns(2)
                metal1 = col1.selectbox(label="Precious metal 1", options=selected_metals, index=0)
                metal2 = col2.selectbox(label="Precious metal 2", options=selected_metals, index=1)
                
                window_size = st.slider(label="Rolling window (days)", value=30, max_value=90, min_value=5)
                rolling_correlation = rolling_corr(data[metal_tickers[metal1]], data[metal_tickers[metal2]], window=window_size)
                
                fig_corr = go.Figure()
                fig_corr.add_trace(go.Scatter(x=rolling_correlation.index, y=rolling_correlation))
                fig_corr.update_layout(template="plotly_white", hovermode="x unified")
                st.plotly_chart(fig_corr, use_container_width=True)
                
                overall_corr = cor(data[metal_tickers[metal1]], data[metal_tickers[metal2]])
                st.metric(label="Overall correlation", value=round(overall_corr, 2))
            
            if metric_choice == "Volatility":
                st.caption("Measure price volatility over time")
                selected_metals_volatility = st.multiselect(
                    label=f"Choose {metal_category} assets to analyze volatility",
                    options=selected_metals,
                    default=selected_metals[:2],
                    key="metal_assets_multiselect_volatility"
                )
                window_size = st.slider(label="Rolling window (days)", value=30, max_value=90, min_value=5)
                
                fig_vol = go.Figure()
                for metal_name in selected_metals_volatility:
                    rolling_vol_metal = rolling_volatility(data[metal_tickers[metal_name]], window=window_size)
                    fig_vol.add_trace(go.Scatter(x=rolling_vol_metal.index, y=rolling_vol_metal,name=metal_name))
                fig_vol.update_layout(template="plotly_white", hovermode="x unified")
                st.plotly_chart(fig_vol, use_container_width=True)
                
                cols_volatility=st.columns(len(selected_metals_volatility))
                for col , metal_name in zip(cols_volatility,selected_metals_volatility):
                    overall_vol = volatility(data[metal_tickers[metal_name]])
                    col.metric(label="Overall volatility (%)", value=round(overall_vol, 2))
            
            if metric_choice == "Volume":
                st.caption("Compare trading volume across metals")
                selected_metals_vol = st.multiselect(
                    label=f"Choose {metal_category} assets to analyze volume",
                    options=selected_metals,
                    default=selected_metals[:2],
                    key="metal_assets_multiselect_volume"
                )
                
                fig_volume = go.Figure()
                for metal_name in selected_metals_vol:
                    metal_data = data[metal_tickers[metal_name]]
                    fig_volume.add_trace(go.Scatter(x=metal_data.index, y=metal_data["Volume"], name=metal_name))
                
                fig_volume.update_layout(template="plotly_white", hovermode="x unified")
                st.plotly_chart(fig_volume, use_container_width=True)
                
                volume_cols = st.columns(len(selected_metals_vol))
                for metal_name, vol_col in zip(selected_metals_vol, volume_cols):
                    volume_data = data[metal_tickers[metal_name]]["Volume"]
                    st.text(metal_name)
                    vol_col.metric(label="Max Volume", value=f"{volume_data.max():,.0f}")
                    vol_col.metric(label="Average Volume", value=f"{volume_data.mean():,.0f}")
            
            if metric_choice == "Max Drawdown":
                st.caption("Measure the largest peak-to-trough decline")
                selected_metals_mdd = st.multiselect(
                    label=f"Choose {metal_category} assets to analyze drawdown",
                    options=selected_metals,
                    default=selected_metals[:2],
                    key="metal_assets_multiselect_mdd"
                )
                
                mdd_cols = st.columns(len(selected_metals_mdd))
                for mdd_col, metal_name in zip(mdd_cols, selected_metals_mdd):
                    with mdd_col:
                        mdd_result = max_drawdown(data[metal_tickers[metal_name]])
                        st.markdown(f"**{metal_name}**")
                        st.metric("Max Drawdown", f"{mdd_result['mdd']:.2f}%")
                        st.text(f"Peak: \n {mdd_result['peak'].strftime('%Y-%m-%d')}")
                        st.text(f"Trough: \n {mdd_result['trough'].strftime('%Y-%m-%d')}")
                        st.metric("Recovery Days", int(mdd_result['duration_days']))

            HELP_METRICS = {
                        "Open_Interest": (
                            "Total number of outstanding derivative contracts. \n"
                            "⬆️ + Price ⬆️ = Strong trend confirmation (Bullish). \n"
                            "⬇️ + Price ⬆️ = Short Squeeze (Potential reversal/exhaustion)."
                        ),
                        "Spec_Sentiment": (
                            "Net position of Money Managers (Smart Money). \n"
                            "🟢 > 0%: Bullish sentiment. \n"
                            "🔴 < 0%: Bearish sentiment. \n"
                            "⚠️ > 20%: Crowded trade (High risk of sharp reversal)."
                        ),
                        "Hedging_Pressure": (
                            "Ratio of Commercial (Industrials) Longs vs Shorts. \n"
                            "🏭 < 1.0: Producer hedging dominates (selling to lock in prices). \n"
                            "🏗️ > 1.0: Consumer hedging dominates (buying due to supply fears)."
                        ),
                        "Divergence": (
                            "Conviction gap between Speculators and Industrials. \n"
                            "A high score indicates a major conflict. Historically, industrials "
                            "(Real Money) tend to be right in the long run."
                        ),
                        "Spreading": (
                            "Percentage of positions in arbitrage (Hedging both ways). \n"
                            "A rising trend suggests market indecision or a transitional phase "
                            "without a clear direction."
                        ),
                        "Bias": "Automated market direction summary based on Speculative Net Positioning."
                    }

            if metric_choice=="Advanced statistics ( LME or CME )":
                selected_metals_adv_stat = st.multiselect(
                    label=f"Choose {metal_category} assets to analyze advanced stats",
                    options=selected_metals,
                    default=selected_metals[:2],
                    key="metal_assets_multiselect_adv_stats"
                )
                available_lme_metal_name=["aluminum","lead","nickel","tin","copper","zinc","cobalt","steel"]
                available_cme_metal_name=["gold","silver","copper","platinum","palladium", "steel","steel_euro"]
                if metal_category == "Industrial" or metal_category=="Battery & tech metals":

                    st.text("The LME publishes a report every Friday summarizing the positions of all types of buyers and sellers who use the LME.")
                    today = datetime.now()
                    days_ago = (today.weekday() - 4) % 7
                    if days_ago == 0:
                        days_ago = 7
                    last_friday = today - timedelta(days=days_ago)
                    st.text("Last repport : "+last_friday.strftime('%d/%m/%Y'))
                    info_lme={}
                    not_avaiable=[]
                    for metal_name in selected_metals_adv_stat:
                        if metal_name.lower() in available_lme_metal_name:
                            info_lme[metal_name]=traiter_rapport_cotr(telecharger_rapport_lme(metal=metal_name.lower()))
                            
                        else :
                            not_avaiable.append(metal_name)
                    if len(not_avaiable)>1:
                        st.info(" ,".join(not_avaiable)+" aren't avaiable !")
                    if len(not_avaiable)==1:
                        st.info(" ,".join(not_avaiable)+" isn't avaiable !")

                    cols_adv_stat=st.columns(len(info_lme.keys()))
                    for col, metal_name in zip(cols_adv_stat,info_lme.keys()):
                        # Metrics :

                        pos = info_lme[metal_name].loc["Number of positions"].astype(float)
                        longs_totaux = pos['Bank_Long'] + pos['Funds_Long'] + pos['Other_Fin_Long'] + pos['Commercial_Long']
                        oi_total = longs_totaux
                        funds_net = pos['Funds_Long'] - pos['Funds_Short']
                        comm_net = pos['Commercial_Long'] - pos['Commercial_Short']
                        
                        spec_sentiment = metric_speculative_net_pos(pos['Funds_Long'], pos['Funds_Short'], oi_total)
                        hedging_ratio = metric_hedging_pressure(pos['Commercial_Long'], pos['Commercial_Short'])
                        divergence = metric_commercial_spec_divergence(comm_net, funds_net)
                        
                        spreading = (pos['Other_Fin_Long'] + pos['Other_Fin_Short']) / (oi_total * 2) * 100
                        col.text("Metal"+ metal_name)
                        col.metric("Open Interest Total",round(oi_total, 0),help=HELP_METRICS["Open_Interest"])
                        col.metric("Speculative Sentiment (%)", round(spec_sentiment, 2),help=HELP_METRICS["Spec_Sentiment"])
                        col.metric("Hedging Pressure (Ratio)",round(hedging_ratio, 2),help=HELP_METRICS["Hedging_Pressure"])
                        col.metric("Divergence Score", round(divergence, 2),help=HELP_METRICS["Divergence"])
                        col.metric("Spreading Intensity (%)", round(spreading, 2),help=HELP_METRICS["Spreading"])
                        col.metric("Bias","BULLISH" if spec_sentiment > 0 else "BEARISH")

                elif metal_category=="Precious":
                    st.text("The CME publishes a report every Friday summarizing the positions of all types of buyers and sellers who use the LME.")
                    today = datetime.now()
                    days_ago = (today.weekday() - 4) % 7
                    if days_ago == 0:
                        days_ago = 7
                    last_friday = today - timedelta(days=days_ago)
                    st.text("Last repport : "+last_friday.strftime('%d/%m/%Y'))
                    info_cme={}
                    not_avaiable=[]
                    for metal_name in selected_metals_adv_stat:
                        if metal_name.lower() in available_cme_metal_name:
                            data=get_full_cme_data_direct(metal_name.lower())
                            colonnes_existantes = [
                                c for c in colonnes_importantes_cme
                                if c in data.columns
                            ]
                            info_cme[metal_name]=data.loc[:,colonnes_existantes]
                        else :
                            not_avaiable.append(metal_name)
                    if len(not_avaiable)>1:
                        st.info(" ,".join(not_avaiable)+" aren't avaiable !")
                    if len(not_avaiable)==1:
                        st.info(" ,".join(not_avaiable)+" isn't avaiable !")
                    
                    cols_adv_stat=st.columns(len(info_cme.keys()))
                    for col, metal_name in zip(cols_adv_stat, info_cme.keys()):
                        df_metal = info_cme[metal_name]
                        pos = df_metal.iloc[0]  # NE PAS caster toute la ligne en float

                        # Sélection safe des colonnes numériques
                        def get_val(series, col_name):
                            return float(series[col_name]) if col_name in series and pd.notna(series[col_name]) else 0.0

                        oi_total = get_val(pos, 'Open_Interest_All')
                        funds_long = get_val(pos, 'M_Money_Positions_Long_All')
                        funds_short = get_val(pos, 'M_Money_Positions_Short_All')
                        prod_long = get_val(pos, 'Prod_Merc_Positions_Long_All')
                        prod_short = get_val(pos, 'Prod_Merc_Positions_Short_All')

                        funds_net = funds_long - funds_short
                        comm_net = prod_long - prod_short

                        spec_sentiment = metric_speculative_net_pos(funds_long, funds_short, oi_total)
                        hedging_ratio = metric_hedging_pressure(prod_long, prod_short)
                        divergence = metric_commercial_spec_divergence(comm_net, funds_net)

                        # Spread columns safely
                        mm_spread = get_val(pos, 'M_Money_Positions_Spread_All')
                        prod_spread = get_val(pos, 'Prod_Merc_Positions_Spread_All')
                        spreading_total = mm_spread + prod_spread
                        spreading_intensity = (spreading_total / oi_total) * 100 if oi_total > 0 else 0

                        # 5. Affichage Streamlit
                        col.text("CME Market: " + metal_name)
                        col.metric("Open Interest Total", round(oi_total, 0), help=HELP_METRICS["Open_Interest"])
                        col.metric("Speculative Sentiment (%)", round(spec_sentiment, 2), help=HELP_METRICS["Spec_Sentiment"])
                        col.metric("Hedging Pressure (Ratio)", round(hedging_ratio, 2), help=HELP_METRICS["Hedging_Pressure"])
                        col.metric("Divergence Score", round(divergence, 2), help=HELP_METRICS["Divergence"])
                        col.metric("Spreading Intensity (%)", round(spreading_intensity, 2), help=HELP_METRICS["Spreading"])
                        col.metric("Bias", "BULLISH" if spec_sentiment > 0 else "BEARISH")





    
        
def aff_agri():
    return 0

def aff_live():
    return 0


def affichage_commo():
    general_aff,energy,metal=st.tabs(["General","Energy","Metals"])
    with general_aff:
        aff_general()
    with energy:
        aff_energy()
    with metal:
        aff_metal()
    """
    with agri:
        aff_agri()
    with livestock:
        aff_live()
    """
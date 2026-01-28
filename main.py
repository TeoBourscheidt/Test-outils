import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

from app.equities_market import affichage_stock_index_market
from app.commodites_market import affichage_commo

page= st.sidebar.selectbox(
    label="Choose page",
    options=["Equities market","Commodities market"])

if page=="Equities market":
    affichage_stock_index_market()
if page=="Commodities market":
    affichage_commo()


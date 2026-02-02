import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

from app.equities_market import affichage_stock_index_market
from app.commodites_market import affichage_commo
from app.quizz import initialize_session_state,display_quiz
from app.concept import initialize_concepts_session_state,display_concepts_quiz

page= st.sidebar.selectbox(
    label="Choose page",
    options=["Equities market","Commodities market","Quizz metrics","Quizz concept"])

if page=="Equities market":
    affichage_stock_index_market()
if page=="Commodities market":
    affichage_commo()
if page=="Quizz metrics":
    initialize_session_state()
    display_quiz()

if page=="Quizz concept":
    initialize_concepts_session_state()
    display_concepts_quiz()


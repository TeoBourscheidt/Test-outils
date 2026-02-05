import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

from app.equities_market import affichage_stock_index_market
from app.commodites_market import affichage_commo
from quizz.quizz import initialize_session_state,display_quiz
from quizz.concept import initialize_concepts_session_state,display_concepts_quiz

page= st.sidebar.selectbox(
    label="Choose page",
    options=["Equities market","Commodities market ( en dev )","Quizz metrics","Quizz concept"])

if page=="Equities market":
    affichage_stock_index_market()
if page=="Commodities market ( en dev )":
    affichage_commo()
if page=="Quizz metrics":
    initialize_session_state()
    display_quiz()

if page=="Quizz concept":
    initialize_concepts_session_state()
    display_concepts_quiz()


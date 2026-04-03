import streamlit as st

from app.market.equities_market import affichage_stock_index_market
from app.market.commodites_market import affichage_commo
from quizz.quizz import initialize_session_state, display_quiz
from quizz.brain_teaser import initialize_brainteaser_session, display_brainteaser_quiz
from quizz.concept import initialize_concepts_session_state, display_concepts_quiz
from app.pricer.option_strat import run

st.set_page_config(
    page_title="Finance Pitch",
    page_icon="◈",
    layout="wide",
)

page = st.sidebar.selectbox(
    label="Choose page",
    options=["Equities market", "Commodities market ( en dev )", "Quizz metrics", "Quizz concept", "Brain Teaser", "Options Strategy"]
)

if page == "Equities market":
    affichage_stock_index_market()
if page == "Commodities market ( en dev )":
    affichage_commo()
if page == "Quizz metrics":
    initialize_session_state()
    display_quiz()
if page == "Quizz concept":
    initialize_concepts_session_state()
    display_concepts_quiz()
if page == "Brain Teaser":
    initialize_brainteaser_session()
    display_brainteaser_quiz()
if page == "Options Strategy":
    run()


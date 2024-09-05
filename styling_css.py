
import streamlit as st


def page_config():
    st.set_page_config(
        page_title="FeedbackFabriken",
        layout="wide",
        page_icon="❤️",
        initial_sidebar_state="collapsed")


def page_styling():
    st.markdown("""
    <style>
                
    h1 {
        padding: 0rem 0px 2rem;
        font-size: 2.1rem;
    }

    img {
    border-radius: 8px;
    border: 1px solid #dadada;
    }
                
    [data-baseweb="tab"] {
    background: #ededed;
    padding-left: 10px;
    padding-right: 10px;
    border-radius: 8px;
    }
                
    [data-baseweb="chackbox"] {
    height: 0rem;
    }
                
    
    [data-baseweb="tab-border"] {
    display: none;
    }
                
                
    [aria-roledescription="Calendar month"] {
        background: #fbfbfb;
    }
                
                
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
    }

    </style>
    """, unsafe_allow_html=True)
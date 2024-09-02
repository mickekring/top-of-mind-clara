
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
        padding: 0rem 0px 1rem;
    }
          
    .st-c7 {
    height: 0rem;
    }
                
    [data-baseweb="tab"] {
    background: #ededed;
    padding-left: 10px;
    padding-right: 10px;
    border-radius: 8px;
    }
                
    [alt="user avatar"] {
        height: 2.8rem;
        width: 2.8rem;
        border-radius: 50%;
    }
                
    [alt="assistant avatar"] {
        height: 2.8rem;
        width: 2.8rem;
        border-radius: 50%;
    }
                
    [aria-label="Chat message from user"] {
        background: #ffffff;
        padding: 10px;
        border-radius: 0.5rem;
    }
                
    [aria-label="Chat message from assistant"] {
        padding: 10px;
    }
        
    .st-emotion {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: rgb(255 255 255);
    }

    [data-testid="block-container"] {
        padding-left: 3rem;
        padding-right: 3rem;
        padding-top: 0rem;
        padding-bottom: 0rem;
        margin-bottom: -7rem;
    }
                
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
    }

    </style>
    """, unsafe_allow_html=True)
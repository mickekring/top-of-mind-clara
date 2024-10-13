
import streamlit as st
import config as c


def page_config():
    st.set_page_config(
        page_title = c.app_name,
        layout = "wide",
        page_icon = ":material/dashboard:",
        initial_sidebar_state = "collapsed")


def page_styling():
    st.markdown("""
    <style>
                
    h1, h2 {
        padding: 0rem 0px 2rem;
        font-size: 2.1rem;
    }

    img {
    border-radius: 8px;
    border: 1px solid #dadada;
    }
                
    [data-baseweb="tab"] {
    background: #ededed;
    padding-left: 24px;
    padding-right: 28px;
    border-radius: 8px;
    }
                
    [data-baseweb="tab-highlight"] {
    display: none;
    }
                
    .st-bz:focus {
    color: #fff;
    background: #5bbf83 !important;
    }
                
    .st-bd {
    color: #ffffff;
    background: #5bbf83 !important;
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


def page_styling_dashboard():
    st.markdown("""
    <style>
                
    h1, h2 {
        padding: 0rem 0px 2rem;
        font-size: 2.1rem;
    }

    img {
    border-radius: 8px;
    border: 1px solid #dadada;
    }
                
    [data-baseweb="tab"] {
    background: #ededed;
    padding-left: 24px;
    padding-right: 28px;
    border-radius: 8px;
    }
                
    [data-baseweb="tab-highlight"] {
    display: none;
    }
                
    .st-bz:focus {
    color: #fff;
    background: #5bbf83 !important;
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
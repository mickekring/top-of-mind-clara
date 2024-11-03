
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
    
    [aria-label="do_not_disturb_on icon"] {
    color: #ef7f5e !important;
    }
                
    [aria-label="add_circle icon"] {
    color: #5BBF83 !important;
    }
                
    [aria-label="stars icon"] {
    color: #e0dd83 !important;
    }

    img {
    border-radius: 8px;
    border: 0px solid #dadada;
    }
    
    [data-baseweb="tab-border"] {
    display: none;
    }                   
                
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
    }

    </style>
    """, unsafe_allow_html=True)
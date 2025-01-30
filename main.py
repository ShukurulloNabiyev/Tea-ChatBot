import streamlit as st
from api_key import api_key_page
from chatbot import chatbot_page

if "api_key" not in st.session_state:
    st.session_state["api_key"] = None

st.sidebar.title("Main menu")
page = st.sidebar.radio("Go to:", ["API-key", "Tea-chatbot"])

if page == "API-key":
    api_key_page()
elif page == "Tea-chatbot":
    chatbot_page()

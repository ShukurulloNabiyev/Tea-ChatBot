import streamlit as st

def api_key_page():
    st.title("API-key")
    st.write("Please enter your API key to continue using the app.")
    
    api_key = st.text_input("API-key", type="password")
    
    if st.button("Save key"):
        if api_key:
            st.session_state["api_key"] = api_key
            st.success("API key saved successfully!")
        else:
            st.error("Please enter your API key.")

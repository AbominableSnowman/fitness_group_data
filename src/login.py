import streamlit as st
import hashlib

# Store hashed passwords securely (store in st.secrets instead in production)
PASSWORDS = {
    "eu_grp": st.secrets.login_info["EU_APP_PASSWORD"],
    "us_grp": st.secrets.login_info["US_APP_PASSWORD"],
}

def login():
    """Handles authentication for the selected group."""
    if st.session_state.authenticated:
        return  # Avoids re-rendering login elements once authenticated
    
    st.title(f"Login for {st.session_state.group.capitalize()}")

    password = st.text_input("Enter Password", type="password")
    
    if st.button("Login"):
        #hashed_input = hashlib.sha256(password.encode()).hexdigest()
        #if hashed_input == PASSWORDS.get(st.session_state.group):
        if password == PASSWORDS.get(st.session_state.group):
            st.session_state.authenticated = True
            st.session_state.page = f"{st.session_state.group}_dashboard"
            st.rerun()
        else:
            st.error("Invalid password.")
    
    if st.button("Back to Selection"):
        st.session_state.page = "landing"
        st.rerun()
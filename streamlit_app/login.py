import streamlit as st

# Hardcoded credentials 
CREDENTIALS = {
    "User": "password123",
}

def login():
    if st.session_state.get("logged_in", False):
        st.sucess("Already logged in{st.session_state.get('username', 'User')}")
        return
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h4 style='text-align:center; color:#ccc;'>Welcome to UPI fraud Analytics Dashboard</h4>", unsafe_allow_html=True)
        st.title("🔐 Login")

        username = st.text_input("Username",key="User")
        password = st.text_input("Password", type="password",key="password123")
        
        if st.button("Login"):
            if username in CREDENTIALS and CREDENTIALS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid Username or Password")



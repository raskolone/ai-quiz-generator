import os
from supabase import create_client
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

def login_form():
    if "user" in st.session_state and st.session_state["user"] is not None:
        return st.session_state["user"]

    st.subheader("🔐 Zaloguj się lub załóż konto")
    mode = st.radio("Tryb", ["Zaloguj", "Zarejestruj"], horizontal=True)
    email = st.text_input("Email")
    password = st.text_input("Hasło", type="password")

    if st.button(mode):
        try:
            if mode == "Zarejestruj":
                res = supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                st.success("Konto utworzone! Zaloguj się teraz.")
            else:
                res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state["user"] = res.user
                st.rerun()
        except Exception as e:
            st.error(f"Błąd: {e}")

    return None

def logout():
    if "user" in st.session_state:
        supabase.auth.sign_out()
        del st.session_state["user"]
        st.rerun()
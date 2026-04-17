import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generuj_quiz(temat, liczba_pytan=5):
    prompt = f"""
    Wygeneruj quiz z {liczba_pytan} pytaniami na temat: "{temat}".
    Każde pytanie ma 4 opcje odpowiedzi (A, B, C, D) i jedną poprawną.
    Zwróć wynik WYŁĄCZNIE jako JSON w tym formacie:
    [
      {{
        "pytanie": "Treść pytania",
        "opcje": "A": "...", "B": "...", "C": "...", "D": "...",
        "poprawna": "A"
      }}
    ]
    """
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=prompt
    )
    tekst = response.text.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(tekst)

st.title("🧠 AI Quiz Generator")
temat = st.text_input("Podaj temat quizu:", placeholder="np. układ słoneczny")

if st.button("Generuj quiz") and temat:
    with st.spinner("Gemini generuje pytania..."):
        pytania = generuj_quiz(temat)
    st.session_state["pytania"] = pytania
    st.session_state["odpowiedzi"] = {}

if "pytania" in st.session_state:
    for i, p in enumerate(st.session_state["pytania"]):
        st.subheader(f"Pytanie {i+1}: {p['pytanie']}")
        opcje = list(p["opcje"].values())
        klucze = list(p["opcje"].keys())
        wybor = st.radio("", opcje, key=f"q{i}")
        st.session_state["odpowiedzi"][i] = klucze[opcje.index(wybor)]

    if st.button("Sprawdź odpowiedzi"):
        wynik = 0
        for i, p in enumerate(st.session_state["pytania"]):
            if st.session_state["odpowiedzi"].get(i) == p["poprawna"]:
                st.success(f"✅ Pytanie {i+1}: Poprawnie!")
                wynik += 1
            else:
                st.error(f"❌ Pytanie {i+1}: Błąd. Poprawna odpowiedź: {p['poprawna']}")
        st.info(f"Twój wynik: {wynik}/{len(st.session_state['pytania'])}")
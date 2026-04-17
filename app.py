import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import json
from pdf_export import quiz_to_pdf

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

LANGUAGES = {
    "Polski": "polish",
    "English": "english",
    "Deutsch": "german",
    "Español": "spanish",
}
UI_TEXTS = {
    "polish": {
        "question": "Pytanie",
        "check": "Sprawdź odpowiedzi",
        "correct": "✅ Pytanie {n}: Poprawnie!",
        "wrong": "❌ Pytanie {n}: Błąd. Poprawna odpowiedź: {ans}",
        "score": "Twój wynik: {s}/{t}",
        "generating": "Gemini generuje pytania...",
        "generate_btn": "Generuj quiz",
        "topic_label": "Podaj temat quizu:",
    },
    "english": {
        "question": "Question",
        "check": "Check answers",
        "correct": "✅ Question {n}: Correct!",
        "wrong": "❌ Question {n}: Wrong. Correct answer: {ans}",
        "score": "Your score: {s}/{t}",
        "generating": "Gemini is generating questions...",
        "generate_btn": "Generate quiz",
        "topic_label": "Enter quiz topic:",
    },
    "german": {
        "question": "Frage",
        "check": "Antworten prüfen",
        "correct": "✅ Frage {n}: Richtig!",
        "wrong": "❌ Frage {n}: Falsch. Richtige Antwort: {ans}",
        "score": "Dein Ergebnis: {s}/{t}",
        "generating": "Gemini generiert Fragen...",
        "generate_btn": "Quiz generieren",
        "topic_label": "Quiz-Thema eingeben:",
    },
    "spanish": {
        "question": "Pregunta",
        "check": "Comprobar respuestas",
        "correct": "✅ Pregunta {n}: ¡Correcto!",
        "wrong": "❌ Pregunta {n}: Incorrecto. Respuesta correcta: {ans}",
        "score": "Tu puntuación: {s}/{t}",
        "generating": "Gemini está generando preguntas...",
        "generate_btn": "Generar cuestionario",
        "topic_label": "Introduce el tema:",
    },
}

def generuj_quiz(temat, language, liczba_pytan=5):
    prompt = f"""Generate a quiz with {liczba_pytan} multiple-choice questions about: "{temat}".

IMPORTANT: All question texts and all answer options MUST be written in {language}. Do NOT use Polish unless {language} is "polish".

Each question has 4 options (A, B, C, D) and exactly one correct answer.
Return the result ONLY as JSON in this exact format (keep the JSON keys in Polish, only translate the values):
[
  {{
    "pytanie": "Question text in {language}",
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

language_label = st.selectbox(
    "Język quizu",
    list(LANGUAGES.keys())
)
language = LANGUAGES[language_label]
T = UI_TEXTS[language]

temat = st.text_input(T["topic_label"], placeholder="np. układ słoneczny / solar system")

if st.button(T["generate_btn"]) and temat:
    with st.spinner(T["generating"]):
        pytania = generuj_quiz(temat, language)
    st.session_state["pytania"] = pytania
    st.session_state["odpowiedzi"] = {}

if "pytania" in st.session_state:
    for i, p in enumerate(st.session_state["pytania"]):
        st.subheader(f"{T['question']} {i+1}: {p['pytanie']}")
        opcje = list(p["opcje"].values())
        klucze = list(p["opcje"].keys())
        wybor = st.radio("", opcje, key=f"q{i}")
        st.session_state["odpowiedzi"][i] = klucze[opcje.index(wybor)]
    pdf_bytes = quiz_to_pdf(st.session_state["pytania"])
    st.download_button(
    label="📥 Pobierz quiz jako PDF",
    data=pdf_bytes,
    file_name="quiz.pdf",
    mime="application/pdf",
)

    if st.button(T["check"]):
        wynik = 0
        for i, p in enumerate(st.session_state["pytania"]):
            if st.session_state["odpowiedzi"].get(i) == p["poprawna"]:
                st.success(T["correct"].format(n=i+1))
                wynik += 1
            else:
                st.error(T["wrong"].format(n=i+1, ans=p['poprawna']))
        st.info(T["score"].format(s=wynik, t=len(st.session_state['pytania'])))
       
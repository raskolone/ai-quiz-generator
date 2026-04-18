import streamlit as st
from google import genai
from dotenv import load_dotenv
import os
import json
from pdf_export import quiz_to_pdf
from auth import login_form, logout, supabase


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

def generuj_quiz(źródło, language, liczba_pytan=5):
    prompt = f"""Generate a quiz with {liczba_pytan} multiple-choice questions based on the source material below.

IMPORTANT: All question texts and all answer options MUST be written in {language}. Do NOT use Polish unless {language} is "polish".

Rules:
- Base questions STRICTLY on the content of the source material. Do not invent facts outside it.
- If the source is a short topic/phrase, use your general knowledge about that topic.
- Each question has 4 options (A, B, C, D) and exactly one correct answer.
- Return the result ONLY as JSON in this exact format (keep the JSON keys in Polish, only translate the values):
[
  {{
    "pytanie": "Question text in {language}",
    "opcje": "A": "...", "B": "...", "C": "...", "D": "...",
    "poprawna": "A"
  }}
]

SOURCE MATERIAL:
\"\"\"
{źródło}
\"\"\"
"""
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=prompt
    )
    tekst = response.text.strip().removeprefix("```json").removesuffix("```").strip()
    return json.loads(tekst)

st.title("🧠 AI Quiz Generator")

user = login_form()
if user is None:
    st.stop()

with st.sidebar:
    st.markdown(f"**Zalogowany:** {user.email}")
    if st.button("Wyloguj"):
        logout()
        # Historia wyników quizów z Supabase
with st.expander("📊 Moja historia quizów"):
    try:
        history = (
            supabase.table("quiz_results")
            .select("created_at, topic, score, total, language")
            .eq("user_id", user.id)
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        if history.data:
            for row in history.data:
                data_str = row["created_at"][:16].replace("T", " ")
                st.markdown(
                    f"🗓 **{data_str}** — {row['topic']} — "
                    f"**{row['score']}/{row['total']}** ({row['language']})"
                )
        else:
            st.info("Nie masz jeszcze żadnych ukończonych quizów.")
    except Exception as e:
        st.warning(f"Nie udało się wczytać historii: {e}")
language_label = st.selectbox(
    "Język quizu",
    list(LANGUAGES.keys())
)

language = LANGUAGES[language_label]
T = UI_TEXTS[language]

source = st.radio(T["source_label"] if "source_label" in T else "Źródło quizu",
                  ["Temat", "Tekst", "Plik"], horizontal=True)

temat = ""
content = ""

if source == "Temat":
    temat = st.text_input(T["topic_label"], placeholder="np. układ słoneczny / solar system")
elif source == "Tekst":
    content = st.text_area("Wklej tekst źródłowy", height=200)
elif source == "Plik":
    uploaded = st.file_uploader("Wgraj PDF, DOCX lub TXT", type=["pdf", "docx", "txt"])
    if uploaded is not None:
        from file_reader import read_file
        content = read_file(uploaded)
        MAX_CHARS = 12000
        if len(content) > MAX_CHARS:
            st.warning(f"Tekst za długi — użyję pierwszych {MAX_CHARS} znaków.")
            content = content[:MAX_CHARS]
        st.success(f"Wczytano {len(content)} znaków z pliku.")

if st.button(T["generate_btn"]) and (temat or content):
    with st.spinner(T["generating"]):
        źródło = temat if temat else content
        pytania = generuj_quiz(źródło, language)
    st.session_state["pytania"] = pytania
    st.session_state["odpowiedzi"] = {}
    st.session_state["quiz_topic"] = temat if temat else "Tekst/Plik"


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
    total = len(st.session_state['pytania'])
    st.info(T["score"].format(s=wynik, t=total))

    try:
        supabase.table("quiz_results").insert({
            "user_id": user.id,
            "topic": st.session_state.get("quiz_topic", "—"),
            "score": wynik,
            "total": total,
            "language": language,
        }).execute()
        st.toast("✅ Wynik zapisany do bazy", icon="💾")
    except Exception as e:
        st.warning(f"Nie udało się zapisać wyniku: {e}")
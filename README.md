
# 🧠 AI Quiz Generator

Aplikacja webowa generująca quizy z dowolnego tematu przy użyciu Google Gemini AI.
Wpisz temat, wybierz liczbę pytań — AI tworzy quiz w kilka sekund.

👉 Live demo: https://ai-quiz-generator-ru75vagcpjyv2dtd8kzbyg.streamlit.app 

---

## ✨ Funkcje

- Generowanie pytań wielokrotnego wyboru (A/B/C/D) z dowolnego tematu
- Wybór liczby pytań (5 / 10 / 15)
- Natychmiastowe sprawdzanie odpowiedzi z punktacją
- Prosty, czysty interfejs — działa w przeglądarce, bez instalacji

---

## 🛠️ Tech Stack

| Element | Narzędzie |
|---|---|
| Język | Python 3.11+ |
| Interfejs webowy | Streamlit |
| AI / LLM | Google Gemini API (gemini-3.1-flash-lite-preview) |
| Hosting | Streamlit Community Cloud |
| Repozytorium | GitHub |

---

## 🚀 Uruchomienie lokalne

### 1. Sklonuj repozytorium

```

git clone https://github.com/raskolone/ai-quiz-generator.git

cd ai-quiz-generator

```

### 2. Stwórz wirtualne środowisko i zainstaluj zależności

```

python -m venv venv

venvScriptsactivate  # Windows

source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt

```

### 3. Skonfiguruj klucz API

Stwórz plik `.env` w folderze projektu:

```

GEMINI_API_KEY=twoj_klucz_z_google_ai_studio

```

Klucz API uzyskasz bezpłatnie na [Google AI Studio](https://aistudio.google.com/app/apikey).

### 4. Uruchom aplikację

```

streamlit run [app.py](http://app.py)

```

Aplikacja otworzy się automatycznie pod adresem `http://localhost:8501`.

---

## 🤖 Jak AI pomagało przy budowie

Ten projekt powstał jako ćwiczenie z **AI-assisted development**. Oto mój proces:

- **Notion AI** — planowanie architektury, instrukcje krok po kroku, debugowanie błędów w czasie rzeczywistym
- **Google AI Studio** — testowanie promptów do generowania pytań quizowych
- **Własna praca** — integracja bibliotek, konfiguracja środowiska, deploy na Streamlit Cloud

### Czego się nauczyłem

- Jak bezpiecznie przechowywać klucze API (`.env` + `.gitignore` + Streamlit Secrets)
- Jak projektować prompty wymuszające konkretny format odpowiedzi (JSON)
- Jak obsługiwać `st.session_state` w Streamlit (pamięć między kliknięciami)
- Praktyczny workflow: lokalny dev → GitHub → cloud deploy

### Co musiałem naprawić ręcznie

- Gemini zwraca odpowiedzi owinięte w ` ```json ``` ` — dodałem `removeprefix/removesuffix` do parsowania
- `gemini-2.0-flash` i `gemini-1.5-flash` niedostępne dla nowych użytkowników — przeszedłem na `gemini-3.1-flash-lite-preview`
- Polityka bezpieczeństwa PowerShell blokowała aktywację `venv` — rozwiązanie: Command Prompt

---

## 📁 Struktura projektu

```

ai-quiz-generator/

├── [app.py](http://app.py)              # Główna aplikacja Streamlit

├── test_[api.py](http://api.py)         # Skrypt testowy połączenia z Gemini API

├── requirements.txt    # Zależności Python

├── .gitignore          # Ignorowane pliki (klucz API, venv)

└── [README.md](http://README.md)           # Ten plik

```

---

## 📝 Licencja

MIT — rób z tym co chcesz.
```

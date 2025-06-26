import streamlit as st
import google.generativeai as genai
import json, re, fitz, pandas as pd
from datetime import datetime
from newspaper import Article
from collections import Counter
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-1.5-flash"

def apply_darkmode():
    if st.session_state.get("theme") == "dark":
        st.markdown("""
            <style>
                body, .stApp {
                    background-color: #0e1117;
                    color: white;
                }
                .stTextArea textarea {
                    background-color: #1e2228;
                    color: white;
                }
            </style>
        """, unsafe_allow_html=True)

# === INIT ===
def init_session():
    defaults = {
        "page": "Home",
        "history": [],
        "current_text": "",
        "theme": "light",
        "language": "English",
        "input_method": "Paste Text",
        "url": ""
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# === SIDEBAR ===
def sidebar():
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/React-icon.svg/512px-React-icon.svg.png", width=60)
        st.title("🔎 Navigation")
        st.button("🏠 Home", on_click=lambda: st.session_state.update(page="Home"))
        st.button("📰 Detector", on_click=lambda: st.session_state.update(page="Detector"))
        st.button("📊 Dashboard", on_click=lambda: st.session_state.update(page="Dashboard"))
        st.button("📜 History", on_click=lambda: st.session_state.update(page="History"))
        st.button("📤 Export", on_click=lambda: st.session_state.update(page="Export"))
        st.markdown("---")
        st.selectbox("🌐 Language", ["English", "Hindi", "Telugu", "Spanish", "French"], key="language")
        if st.toggle("🌙 Dark Mode", key="theme_toggle"):
            st.session_state.theme = "dark"
        else:
            st.session_state.theme = "light"
        st.markdown("---")
        st.caption("Made with ❤ using Google Gemini Flash")
        st.caption("© 2025 Fake News Detector | Built by Team Vision")

# === GEMINI PROMPT ===
def build_prompt(news_text):
    return f"""
You are a multilingual fake news detection expert.

Translate the news to {st.session_state.language} if it's not already.

Then respond in {st.session_state.language} only.

Respond strictly in this JSON format:

{{
  "verdict": "Fake" or "Real" or "Uncertain",
  "reason": "Short explanation in {st.session_state.language}",
  "credibility_score": 0-100
}}

News:
\"\"\"
{news_text}
\"\"\"
"""

def extract_json(text):
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    return match.group(0) if match else None

def analyze_news(text):
    model = genai.GenerativeModel(MODEL_NAME)
    try:
        response = model.generate_content(build_prompt(text))
        raw_text = response.text
        json_str = extract_json(raw_text)
        return json.loads(json_str) if json_str else {"error": "Parse failed", "raw": raw_text}
    except Exception as e:
        return {"error": str(e)}

def verdict_style(verdict):
    v = verdict.lower()
    return ("❌ Fake", "red") if v == "fake" else ("✅ Real", "green") if v == "real" else ("⚠ Uncertain", "orange")

# === UTILITIES ===
def read_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def read_url(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except:
        return None

# === PAGES ===
def page_home():
    st.title("📰 Fake News Detector")
    st.markdown("""
This tool uses *Google Gemini Flash* to determine whether a news article is *Fake, **Real, or **Uncertain*.

### 💡 You Can:
- Paste news manually
- Upload a .pdf file
- Enter a news article URL
- View exportable results

> Built for multilingual content with translation + structured analysis.
""")

def page_detector():
    st.title("🧠 Fake News Detector")

    st.session_state.input_method = st.radio("Select Input Method", ["Paste Text", "Upload PDF", "Enter URL"])
    current_text = ""

    if st.session_state.input_method == "Paste Text":
        current_text = st.text_area("📝 Paste your news here", height=200)

    elif st.session_state.input_method == "Upload PDF":
        uploaded_file = st.file_uploader("📄 Upload PDF", type="pdf")
        if uploaded_file:
            with st.spinner("Extracting text..."):
                current_text = read_pdf(uploaded_file)
                st.success("Text extracted!")

    elif st.session_state.input_method == "Enter URL":
        url = st.text_input("🔗 Enter news article URL", value=st.session_state.url)
        st.session_state.url = url
        if url:
            with st.spinner("Fetching article..."):
                fetched = read_url(url)
                if fetched:
                    current_text = fetched
                    st.success("Content fetched.")
                else:
                    st.error("Could not extract content from the URL.")

    st.session_state.current_text = current_text

    if st.button("🧠 Run Fake News Analysis"):
        if not st.session_state.current_text.strip():
            st.warning("❗ Please provide content to analyze.")
            return
        with st.spinner("Analyzing with Gemini Flash..."):
            result = analyze_news(st.session_state.current_text)

        if "error" in result:
            st.error("❌ " + result["error"])
            if "raw" in result:
                st.code(result["raw"])
        else:
            label, color = verdict_style(result["verdict"])
            st.markdown(f"### Verdict: <span style='color:{color}; font-size: 22px;'>{label}</span>", unsafe_allow_html=True)
            st.markdown(f"*Score:* {result['credibility_score']} / 100")
            st.progress(int(result["credibility_score"]))
            with st.expander("💡 Reasoning"):
                st.write(result["reason"])

            st.session_state.history.append({
                "text": st.session_state.current_text[:300],
                "verdict": result["verdict"],
                "reason": result["reason"],
                "score": result["credibility_score"],
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "model": "Gemini Flash"
            })

def page_dashboard():
    st.title("📊 Verdict Dashboard")
    if not st.session_state.history:
        st.info("No analysis data yet.")
        return
    df = pd.DataFrame(st.session_state.history)
    st.bar_chart(df["verdict"].value_counts())
    st.metric("Average Score", f"{df['score'].mean():.1f}")

def page_history():
    st.title("📜 Past Analyses")
    if not st.session_state.history:
        st.info("No history yet.")
        return
    for entry in reversed(st.session_state.history):
        with st.expander(f"🕒 {entry['time']} | {entry['verdict']} | Score: {entry['score']}"):
            st.write(f"*News:* {entry['text']}...")
            st.write(f"*Reason:* {entry['reason']}")

def page_export():
    st.title("📤 Export History")
    if not st.session_state.history:
        st.info("No data to export.")
        return
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df[["time", "verdict", "score", "model"]])
    csv = df.to_csv(index=False).encode("utf-8")
    json_data = json.dumps(st.session_state.history, indent=2)
    st.download_button("⬇ Download CSV", csv, "fake_news_results.csv", "text/csv")
    st.download_button("⬇ Download JSON", json_data, "fake_news_results.json", "application/json")

# === MAIN ===
def main():
    st.set_page_config(page_title="Fake News Detector", layout="wide")
    init_session()
    apply_darkmode()
    sidebar()
    pages = {
        "Home": page_home,
        "Detector": page_detector,
        "Dashboard": page_dashboard,
        "History": page_history,
        "Export": page_export
    }
    pages[st.session_state.page]()

if __name__ == "__main__":
    main()
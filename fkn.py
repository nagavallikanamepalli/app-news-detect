import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd
from datetime import datetime
from collections import Counter
import os

# Try to import optional dependencies with fallbacks
try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    st.warning("PDF support not available. Install PyMuPDF to enable PDF uploads.")

try:
    from newspaper import Article
    URL_SUPPORT = True
except ImportError:
    URL_SUPPORT = False
    st.warning("URL support not available. Install newspaper3k to enable URL parsing.")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# Configure Gemini API
API_KEY = None

# Safe way to check for secrets
try:
    if hasattr(st, 'secrets') and "GOOGLE_API_KEY" in st.secrets:
        API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    pass  # Secrets not available, will try environment variables

# Fallback to environment variables
if not API_KEY:
    API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    MODEL_NAME = "gemini-1.5-flash"
else:
    st.error("❌ Google API Key not found. Please configure it using one of these methods:")
    st.markdown("""
    **For local development:**
    1. Create a `.env` file in your project folder with: `GEMINI_API_KEY=your_api_key_here`
    2. Or set environment variable: `GOOGLE_API_KEY=your_api_key_here`
    
    **For Streamlit Cloud deployment:**
    1. Go to your app settings in Streamlit Cloud
    2. Add `GOOGLE_API_KEY = your_api_key_here` in the secrets section
    
    **Get your API key from:** https://makersuite.google.com/app/apikey
    """)
    st.stop()

def apply_darkmode():
    """Apply dark mode styling if enabled"""
    if st.session_state.get("theme") == "dark":
        st.markdown("""
            <style>
                .stApp {
                    background-color: #0e1117;
                    color: white;
                }
                .stTextArea textarea {
                    background-color: #1e2228;
                    color: white;
                    border: 1px solid #30363d;
                }
                .stSelectbox > div > div {
                    background-color: #1e2228;
                    color: white;
                }
            </style>
        """, unsafe_allow_html=True)

def init_session():
    """Initialize session state variables"""
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

def sidebar():
    """Render sidebar navigation and settings"""
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Google_Gemini_logo.svg/512px-Google_Gemini_logo.svg.png", width=60)
        st.title("🔎 Navigation")
        
        # Navigation buttons
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "Home"
        if st.button("📰 Detector", use_container_width=True):
            st.session_state.page = "Detector"
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"
        if st.button("📜 History", use_container_width=True):
            st.session_state.page = "History"
        if st.button("📤 Export", use_container_width=True):
            st.session_state.page = "Export"
        
        st.markdown("---")
        
        # Settings
        st.session_state.language = st.selectbox(
            "🌐 Language", 
            ["English", "Hindi", "Telugu", "Spanish", "French"], 
            index=["English", "Hindi", "Telugu", "Spanish", "French"].index(st.session_state.language)
        )
        
        if st.toggle("🌙 Dark Mode", value=st.session_state.theme == "dark"):
            st.session_state.theme = "dark"
        else:
            st.session_state.theme = "light"
        
        st.markdown("---")
        st.caption("Made with ❤️ using Google Gemini")
        st.caption("© 2025 Fake News Detector")

def build_prompt(news_text):
    """Build the prompt for Gemini API"""
    return f"""
You are a multilingual fake news detection expert. Analyze the following news text and provide your assessment.

If the news is not in {st.session_state.language}, first translate it to {st.session_state.language}.

Respond strictly in this JSON format (use {st.session_state.language} for the reason):

{{
  "verdict": "Fake" or "Real" or "Uncertain",
  "reason": "Short explanation in {st.session_state.language}",
  "credibility_score": 0-100
}}

News text to analyze:
\"\"\"
{news_text}
\"\"\"
"""

def extract_json(text):
    """Extract JSON from Gemini response"""
    # Try to find JSON block
    json_match = re.search(r'\{.*?\}', text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    return None

def analyze_news(text):
    """Analyze news text using Gemini API"""
    if not API_KEY:
        return {"error": "API key not configured"}
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(build_prompt(text))
        raw_text = response.text
        
        # Extract JSON from response
        json_str = extract_json(raw_text)
        if json_str:
            result = json.loads(json_str)
            # Validate required fields
            if all(key in result for key in ["verdict", "reason", "credibility_score"]):
                return result
        
        return {"error": "Invalid response format", "raw": raw_text}
    
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

def verdict_style(verdict):
    """Get styling for verdict display"""
    v = verdict.lower()
    if v == "fake":
        return ("❌ Fake", "red")
    elif v == "real":
        return ("✅ Real", "green")
    else:
        return ("⚠️ Uncertain", "orange")

def read_pdf(file):
    """Extract text from PDF file"""
    if not PDF_SUPPORT:
        return "PDF support not available"
    
    try:
        text = ""
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def read_url(url):
    """Extract text from URL"""
    if not URL_SUPPORT:
        return None
    
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        st.error(f"Error fetching URL: {str(e)}")
        return None

def page_home():
    """Home page"""
    st.title("📰 Fake News Detector")
    st.markdown("""
    This tool uses **Google Gemini** to analyze news articles and determine whether they are **Fake**, **Real**, or **Uncertain**.

    ### 🚀 Features:
    - **Multi-language support** - Analyze news in multiple languages
    - **Multiple input methods** - Paste text, upload PDF, or enter URL
    - **Detailed analysis** - Get credibility scores and explanations
    - **History tracking** - View past analyses
    - **Export capabilities** - Download results as CSV or JSON

    ### 📊 How it works:
    1. Input your news content using any supported method
    2. Our AI analyzes the content for factual accuracy
    3. Get a verdict with confidence score and detailed reasoning
    4. View analytics and export your results

    ### 🌟 Supported Languages:
    English, Hindi, Telugu, Spanish, French

    ---
    **Get started by clicking "Detector" in the sidebar!**
    """)

def page_detector():
    """Main detection page"""
    st.title("🔍 Fake News Analysis")
    
    # Input method selection
    input_options = ["Paste Text"]
    if PDF_SUPPORT:
        input_options.append("Upload PDF")
    if URL_SUPPORT:
        input_options.append("Enter URL")
    
    st.session_state.input_method = st.radio(
        "📥 Select Input Method", 
        input_options,
        index=input_options.index(st.session_state.input_method) if st.session_state.input_method in input_options else 0
    )
    
    current_text = ""
    
    # Handle different input methods
    if st.session_state.input_method == "Paste Text":
        current_text = st.text_area(
            "📝 Paste your news article here", 
            height=200,
            placeholder="Enter the news text you want to analyze..."
        )
    
    elif st.session_state.input_method == "Upload PDF" and PDF_SUPPORT:
        uploaded_file = st.file_uploader("📄 Upload PDF file", type="pdf")
        if uploaded_file:
            with st.spinner("📖 Extracting text from PDF..."):
                current_text = read_pdf(uploaded_file)
                if "Error" not in current_text:
                    st.success("✅ Text extracted successfully!")
                    with st.expander("📄 Extracted Text Preview"):
                        st.text(current_text[:500] + "..." if len(current_text) > 500 else current_text)
                else:
                    st.error(current_text)
    
    elif st.session_state.input_method == "Enter URL" and URL_SUPPORT:
        url = st.text_input(
            "🔗 Enter news article URL", 
            value=st.session_state.url,
            placeholder="https://example.com/news-article"
        )
        st.session_state.url = url
        
        if url and st.button("🌐 Fetch Article"):
            with st.spinner("🌐 Fetching article content..."):
                fetched = read_url(url)
                if fetched:
                    current_text = fetched
                    st.success("✅ Content fetched successfully!")
                    with st.expander("📄 Fetched Content Preview"):
                        st.text(current_text[:500] + "..." if len(current_text) > 500 else current_text)
                else:
                    st.error("❌ Could not extract content from the URL.")
    
    st.session_state.current_text = current_text
    
    # Analysis section
    if current_text.strip():
        st.markdown("### 📊 Text Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Characters", len(current_text))
        with col2:
            st.metric("Words", len(current_text.split()))
        with col3:
            st.metric("Lines", len(current_text.split('\n')))
    
    # Analysis button
    if st.button("🧠 Analyze News", type="primary", use_container_width=True):
        if not current_text.strip():
            st.warning("⚠️ Please provide content to analyze.")
            return
        
        with st.spinner("🔍 Analyzing with Google Gemini..."):
            result = analyze_news(current_text)
        
        if "error" in result:
            st.error(f"❌ Analysis Error: {result['error']}")
            if "raw" in result:
                with st.expander("🔍 Raw Response"):
                    st.code(result["raw"])
        else:
            # Display results
            label, color = verdict_style(result["verdict"])
            
            st.markdown("### 🎯 Results")
            st.markdown(f"**Verdict:** <span style='color:{color}; font-size: 24px; font-weight: bold;'>{label}</span>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Credibility Score", f"{result['credibility_score']}/100")
            with col2:
                st.progress(int(result["credibility_score"]) / 100)
            
            with st.expander("💡 Reasoning & Analysis"):
                st.write(result["reason"])
            
            # Save to history
            st.session_state.history.append({
                "text": current_text[:300] + ("..." if len(current_text) > 300 else ""),
                "full_text": current_text,
                "verdict": result["verdict"],
                "reason": result["reason"],
                "score": result["credibility_score"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "language": st.session_state.language,
                "model": "Gemini 1.5 Flash"
            })
            
            st.success("✅ Analysis complete! Check History to view all analyses.")

def page_dashboard():
    """Analytics dashboard"""
    st.title("📊 Analytics Dashboard")
    
    if not st.session_state.history:
        st.info("📈 No analysis data yet. Run some analyses to see statistics here!")
        return
    
    df = pd.DataFrame(st.session_state.history)
    
    # Overall stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Analyses", len(df))
    with col2:
        st.metric("Average Score", f"{df['score'].mean():.1f}")
    with col3:
        st.metric("Fake News Detected", len(df[df['verdict'] == 'Fake']))
    with col4:
        st.metric("Real News Verified", len(df[df['verdict'] == 'Real']))
    
    # Charts
    st.markdown("### 📈 Verdict Distribution")
    verdict_counts = df['verdict'].value_counts()
    st.bar_chart(verdict_counts)
    
    st.markdown("### 📊 Score Distribution")
    st.histogram_chart(df['score'])
    
    # Recent activity
    st.markdown("### 🕒 Recent Activity")
    recent_df = df.tail(5)[['timestamp', 'verdict', 'score']].sort_values('timestamp', ascending=False)
    st.dataframe(recent_df, use_container_width=True)

def page_history():
    """History page"""
    st.title("📜 Analysis History")
    
    if not st.session_state.history:
        st.info("📝 No history yet. Start analyzing news to build your history!")
        return
    
    # Search and filter
    search_term = st.text_input("🔍 Search history", placeholder="Search by text content...")
    verdict_filter = st.selectbox("Filter by verdict", ["All", "Fake", "Real", "Uncertain"])
    
    # Filter history
    filtered_history = st.session_state.history.copy()
    if search_term:
        filtered_history = [h for h in filtered_history if search_term.lower() in h['text'].lower()]
    if verdict_filter != "All":
        filtered_history = [h for h in filtered_history if h['verdict'] == verdict_filter]
    
    st.write(f"Showing {len(filtered_history)} of {len(st.session_state.history)} analyses")
    
    # Display history
    for i, entry in enumerate(reversed(filtered_history)):
        label, color = verdict_style(entry['verdict'])
        
        with st.expander(f"🕒 {entry['timestamp']} | {label} | Score: {entry['score']}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("**Text Preview:**")
                st.text(entry['text'])
                st.markdown("**Analysis:**")
                st.write(entry['reason'])
            with col2:
                st.metric("Score", f"{entry['score']}/100")
                st.write(f"**Language:** {entry.get('language', 'English')}")
                st.write(f"**Model:** {entry.get('model', 'Gemini')}")
                
                if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                    # Find and remove this entry
                    for j, h in enumerate(st.session_state.history):
                        if h['timestamp'] == entry['timestamp']:
                            del st.session_state.history[j]
                            st.rerun()

def page_export():
    """Export page"""
    st.title("📤 Export Analysis Results")
    
    if not st.session_state.history:
        st.info("📊 No data to export. Run some analyses first!")
        return
    
    df = pd.DataFrame(st.session_state.history)
    
    # Export options
    st.markdown("### 📋 Data Preview")
    display_df = df[['timestamp', 'verdict', 'score', 'language', 'model']].copy()
    st.dataframe(display_df, use_container_width=True)
    
    st.markdown("### 💾 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV Export
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name=f"fake_news_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # JSON Export
        json_data = json.dumps(st.session_state.history, indent=2, ensure_ascii=False)
        st.download_button(
            label="📋 Download JSON",
            data=json_data.encode('utf-8'),
            file_name=f"fake_news_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    # Clear history option
    st.markdown("### 🗑️ Data Management")
    if st.button("🗑️ Clear All History", type="secondary"):
        if st.button("⚠️ Confirm Clear All", type="primary"):
            st.session_state.history = []
            st.success("✅ History cleared!")
            st.rerun()

def main():
    """Main application"""
    st.set_page_config(
        page_title="Fake News Detector",
        page_icon="📰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session()
    
    # Apply theme
    apply_darkmode()
    
    # Render sidebar
    sidebar()
    
    # Route to pages
    pages = {
        "Home": page_home,
        "Detector": page_detector,
        "Dashboard": page_dashboard,
        "History": page_history,
        "Export": page_export
    }
    
    # Render current page
    if st.session_state.page in pages:
        pages[st.session_state.page]()
    else:
        st.error("Page not found!")

if __name__ == "__main__":
    main()
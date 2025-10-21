# 📰 Fake News Detector

An AI-powered fake news detection application using **Google Gemini** and **Streamlit**. Analyze news articles in multiple languages, get credibility scores, and track your analysis history.

---

## 🚀 Features

- **Multi-language Support** - Analyze news in English, Hindi, Telugu, Spanish, and French
- **Multiple Input Methods** - Paste text, upload PDF files, or fetch from URLs
- **AI-Powered Analysis** - Uses Google Gemini 1.5 Flash for intelligent fact-checking
- **Credibility Scoring** - Get a 0-100 credibility score for each article
- **History Tracking** - Keep records of all your analyses
- **Analytics Dashboard** - View statistics and trends
- **Export Capabilities** - Download results as CSV or JSON
- **Dark Mode** - Eye-friendly dark theme option

---

## 📋 Setup Instructions

### Step 1: Get Your Google Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Copy your API key (it starts with `AIza...`)

### Step 2: Install Dependencies

Run the following command to install all required packages:

```bash
pip install -r requirements.txt
```

### Step 3: Configure Your API Key

**Your API key is already configured in two places:**

1. **`.env` file** (for local development):
   ```
   GEMINI_API_KEY=AIzaSyAU_L-RdtNXN8KmmfB_ZfNfkXFN1CCMDsI
   ```

2. **`.streamlit/secrets.toml` file** (for Streamlit Cloud deployment):
   ```
   GEMINI_API_KEY="AIzaSyAU_L-RdtNXN8KmmfB_ZfNfkXFN1CCMDsI"
   ```

**To use your own API key:**
- Replace the API key in both files with your own key from Step 1

---

## 🎯 How to Run

### Option 1: Run Locally

```bash
streamlit run fkn.py
```

The app will open automatically in your browser at `http://localhost:8501`

### Option 2: Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in and click **"New app"**
4. Select your repository and main file (`fkn.py`)
5. Add your API key in **Advanced settings → Secrets**:
   ```
   GEMINI_API_KEY = "your_api_key_here"
   ```
6. Click **"Deploy"**

---

## 📖 How to Use

### 1. Home Page
- Read about the features and capabilities
- Navigate using the sidebar

### 2. Detector Page
Choose your input method:

**A. Paste Text**
- Click on "Paste Text" radio button
- Paste your news article in the text area
- Click **"🧠 Analyze News"**

**B. Upload PDF**
- Click on "Upload PDF" radio button
- Upload a PDF file containing the news article
- Click **"🧠 Analyze News"**

**C. Enter URL**
- Click on "Enter URL" radio button
- Paste the URL of the news article
- Click **"🌐 Fetch Article"**
- Click **"🧠 Analyze News"**

**Results:**
- View the verdict (Fake/Real/Uncertain)
- Check the credibility score (0-100)
- Read the AI's reasoning and analysis

### 3. Dashboard Page
- View total analyses count
- Check average credibility score
- See verdict distribution charts
- Review recent activity

### 4. History Page
- Browse all past analyses
- Search by content
- Filter by verdict (Fake/Real/Uncertain)
- Delete specific entries
- View source URLs for fetched articles

### 5. Export Page
- Preview your analysis data
- Download as CSV or JSON
- Clear all history (with confirmation)

---

## ⚙️ Settings (Sidebar)

- **Language Selection**: Choose analysis language (English, Hindi, Telugu, Spanish, French)
- **Dark Mode**: Toggle dark theme for comfortable viewing

---

## 🛠️ Technical Details

### Dependencies

**Core:**
- `streamlit` - Web interface
- `google-generativeai` - Gemini API
- `pandas` - Data manipulation
- `numpy` - Numerical operations

**Optional (for enhanced features):**
- `PyMuPDF` - PDF text extraction
- `newspaper3k` - URL content extraction
- `requests` & `beautifulsoup4` - Alternative URL parsing
- `python-dotenv` - Environment variable management

### API Usage

The app uses:
- **Model**: Gemini 1.5 Flash
- **Purpose**: Fake news detection and analysis
- **Response Format**: JSON with verdict, reason, and credibility score

---

## 📊 Example Analysis

**Input:**
```
"Scientists have discovered that drinking coffee cures cancer completely."
```

**Output:**
- **Verdict**: ❌ Fake
- **Credibility Score**: 15/100
- **Reasoning**: "This claim is misleading and not supported by scientific evidence. While coffee has some health benefits, there is no research showing it can cure cancer completely. Such absolute claims about cancer cures should be treated with extreme skepticism."

---

## 🔒 Security Notes

- Your API key is stored locally in `.env` and `.streamlit/secrets.toml`
- Never share your API key publicly
- Add `.env` to `.gitignore` (already configured)
- For production, use environment variables or secure secrets management

---

## 🐛 Troubleshooting

**Issue: "API Key not found" error**
- Check that your `.env` file contains `GEMINI_API_KEY=your_key`
- Check that `.streamlit/secrets.toml` contains `GEMINI_API_KEY="your_key"`
- Restart the Streamlit app

**Issue: PDF upload not working**
- Install PyMuPDF: `pip install PyMuPDF`

**Issue: URL fetch not working**
- Install optional packages: `pip install newspaper3k requests beautifulsoup4`
- Some websites block automated scraping - use manual paste instead

**Issue: Analysis gives error**
- Ensure your API key is valid and active
- Check your internet connection
- Verify you haven't exceeded API quotas

---

## 📈 Future Enhancements

- [ ] Support for more languages
- [ ] Batch analysis for multiple articles
- [ ] Comparison of multiple sources
- [ ] Integration with fact-checking databases
- [ ] Social media post analysis
- [ ] Browser extension

---

## 📝 License

This project is for educational and research purposes.

---

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the [Streamlit documentation](https://docs.streamlit.io)
3. Check [Google AI Studio documentation](https://ai.google.dev/docs)

---

**Made with ❤️ using Google Gemini and Streamlit**

© 2025 Fake News Detector

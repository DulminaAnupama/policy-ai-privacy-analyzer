# 🔒 PolicyAI — Privacy Policy Analyser & Scenario Generator

A Flask web app that uses **Groq AI (free)** to summarise privacy policies and generate adapted policy drafts for different contexts — children's platforms, enterprise, GDPR, healthcare, and custom scenarios.

Pre-loaded with the **Netflix Privacy Statement (April 2025)** as a demo.

---

## ✨ Features

- 📄 **Smart Summarisation** — Upload a PDF, paste text, or use the pre-loaded policy to get a structured AI summary
- 🎭 **Scenario Generation** — Adapt any policy for 4 predefined contexts or define your own custom scenario
- ⚡ **Groq-Powered** — Uses LLaMA 3.3 70B via Groq's free API (no credit card needed)
- 📎 **PDF Support** — Extracts text from uploaded PDF files via `pdfplumber`

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/policy-ai-privacy-analyzer.git
cd policy-ai-privacy-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get a free Groq API key

1. Go to [https://console.groq.com](https://console.groq.com) and sign up (free)
2. Click **API Keys → Create API Key**
3. Copy the key — it starts with `gsk_`

### 4. Set your API key

**Option A — Environment variable (recommended):**
```bash
export GROQ_API_KEY=gsk_your_key_here
```

**Option B — Edit `app.py` directly:**
```python
GROQ_API_KEY = "gsk_your_key_here"
```

> ⚠️ **Never commit your API key to GitHub.** Use environment variables or a `.env` file (see below).

### 5. Run the app

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 📁 Project Structure

```
policy-ai-privacy-analyzer/
├── app.py                  # Flask app — routes, API calls, PDF extraction
├── templates/
│   └── index.html          # Jinja2 HTML template
├── static/
│   ├── css/
│   │   └── style.css       # All styles
│   └── js/
│       └── main.js         # All frontend JavaScript
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🔐 Keeping Your API Key Safe

Create a `.env` file (never commit this):
```
GROQ_API_KEY=gsk_your_key_here
```

Install `python-dotenv`:
```bash
pip install python-dotenv
```

Add to the top of `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

Add `.env` to your `.gitignore`:
```
.env
__pycache__/
*.pyc
```

---

## 🤖 AI Model

- **Provider:** [Groq](https://console.groq.com) (free tier)
- **Model:** `llama-3.3-70b-versatile`
- **Free tier limits:** 30 requests/min · 14,400 requests/day · No credit card required

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `flask` | Web framework |
| `requests` | HTTP calls to Groq API |
| `pdfplumber` | PDF text extraction (recommended) |

Optional PDF alternatives (any one works):
- `pypdf`
- `PyPDF2`

---

## 🗺️ Predefined Scenarios

| Scenario | Key Regulation |
|---|---|
| 👶 Children's Platform (Under-13) | COPPA |
| 🏢 Enterprise / Corporate Deployment | Employment law, data governance |
| 🇪🇺 EU / GDPR Strict Compliance | GDPR |
| 🏥 Health & Wellness Platform | HIPAA |

You can also define fully custom scenarios with your own name, description, and requirements.

---

## 📄 Licence

MIT

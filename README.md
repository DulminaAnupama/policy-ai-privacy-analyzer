# policy-ai-privacy-analyzer
AI-powered privacy policy analyzer and scenario-based generator using LLMs
# PolicyAI – Privacy Policy Analyzer & Generator

## 📌 Overview
PolicyAI is an AI-powered web application designed to analyze privacy policies and transform unstructured legal text into structured, actionable insights. The system leverages Large Language Models (LLMs) to support policy summarization and scenario-based policy generation.

## 🚀 Key Features
- Extracts and processes privacy policies from PDF and text inputs  
- Generates structured summaries using AI  
- Identifies key components such as data collection, usage, and user rights  
- Supports scenario-based policy generation (GDPR, healthcare, enterprise, etc.)  
- Allows custom scenarios for tailored analysis  
- Converts complex legal documents into decision-ready insights  

## 🛠 Tech Stack
- Python  
- Flask  
- Groq API (LLaMA 3.3)  
- HTML, CSS, JavaScript  

## 📊 Business Value
This project demonstrates how AI and data analytics techniques can be applied to extract value from unstructured text, supporting compliance, governance, and decision-making processes.

## ⚙️ How to Run
1. Clone the repository  
2. Install dependencies:
   ```bash
   pip install flask requests pdfplumber pypdf PyPDF2
3. Add your Groq API key in policy_app.py
4. Run the app
  '''bash
   python policy_app.py

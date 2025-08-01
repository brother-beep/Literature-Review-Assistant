# 🤖 AutoGen Literature Review Tool

A multi-agent, AI-powered literature review generator using cutting-edge LLMs (e.g., Gemini) to search arXiv, curate top research papers, and summarize them in clean, structured Markdown and PDF formats.

---

## 🚀 Features

- 🔍 **ArXiv-powered search agent** for discovering high-relevance research papers.
- 🧠 **Summarization agent** generates human-quality reviews in Markdown.
- 📄 **Exports** to `.md` and `.pdf` (via `pdfkit`) [pdf exploring features not added yet. Now you can download the .md file and open it through notebook].
- 📡 **Async streaming output** for real-time UI updates.
- 🖼️ **Beautiful Streamlit app** frontend with customization options.
- 🧰 **Modular backend** using FunctionTool and AssistantAgent APIs.

---


## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/autogen-litreview-tool.git
cd autogen-litreview-tool

# Create a virtual environment
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows

# Install required packages
pip install -r requirements.txt

# Run the application
streamlit run app.py

# OPTIONAL: Install wkhtmltopdf for PDF export
# Windows: https://wkhtmltopdf.org/downloads.html
# macOS: brew install wkhtmltopdf

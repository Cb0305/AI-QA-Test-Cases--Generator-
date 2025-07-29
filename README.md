# ⚙️ AI-QA Test Cases -Generator

AI-QA Test Cases -Generator is a powerful Streamlit-based automation tool designed to generate and validate test cases from instructional videos using AI models like Whisper, MiniLM, and Playwright.

This assistant allows users to:

* 🎥 Upload instructional videos
* 🧠 Auto-generate prompts and test cases
* 📄 Upload or convert JSON to Playwright scripts
* 🧪 Run tests and capture results
* 📤 Export reports to PDF and optionally email them

---

## 🚀 Features

✅ Upload instructional videos (MP4/MOV/AVI/MKV)
✅ Transcribe using OpenAI Whisper (tiny, base, etc.)
✅ Auto-generate structured prompts from transcriptions
✅ Upload JSON test cases and convert to Playwright scripts
✅ Run Playwright tests and view detailed execution logs
✅ Generate professional PDF reports
✅ Email reports via Gmail SMTP
✅ Manage and clean all uploaded, generated, and report files

---

## 📁 Project Structure

```
qa/
├── generator/
│   ├── transcribe_video.py
│   ├── chunk_and_embed.py
│   ├── generate_testcases.py
│   └── output/
├── scripts/
│   ├── convert_json_to_playwright.py
│   └── tests/
├── runner/
│   ├── run_tests.py
│   ├── run_playwright.sh
│   └── results/
├── dashboard/
│   └── app.py
├── uploaded_videos/
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🛠️ Setup Instructions

### 1. Clone the Repository


git clone https://github.com/Cb0305/AI-QA-Test-Cases-Generator.git


### 2. Create Virtual Environment


python -m venv venv
venv\Scripts\activate  # On Windows


### 3. Install Dependencies

pip install -r requirements.txt

### 4. Download Required Models

Optional script to download Whisper + MiniLM:

python download_models.py


This downloads:

* Whisper (base)
* all-MiniLM-L6-v2 (via sentence-transformers)

---

## 🧪 How to Use

Start the app:

streamlit run dashboard/app.py


### 🔄 Workflow:

1. 🔼 Upload a video (Max 50MB)
2. 🔠 Automatic audio transcription using Whisper
3. 📝 Prompt generated for test case design (ChatGPT or manual)
4. ⬇️ Upload JSON test cases
5. 🧪 Playwright tests are auto-generated and executed
6. 📄 PDF test reports generated
7. 📧 Optionally send via email

---

## 📤 Environment Variables

To enable email sending, set Gmail credentials:


# In .env or system environment
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
```

Use a [Google App Password](https://support.google.com/accounts/answer/185833?hl=en) for security.

---

## 📦 Major Dependencies

* `streamlit`
* `openai-whisper`
* `sentence-transformers`
* `playwright`
* `fpdf`
* `matplotlib`
* `smtplib`, `email`

---

## 📄 Output Locations

* `generator/output/` – Transcripts, prompts, and test cases
* `runner/results/logs/` – Playwright test logs
* `runner/results/test_bundle.zip` – Zipped test data
* `runner/results/*.pdf` – Final reports


## 🧹 Clean Git Setup

* Large model files (`*.pt`, `*.safetensors`) are excluded via `.gitignore`
* Use `download_models.py` to set up locally


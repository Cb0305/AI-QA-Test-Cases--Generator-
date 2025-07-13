⚙️ QA Agent Dashboard

QA Agent is a powerful Streamlit-based tool designed to automate test generation and execution from instructional videos using Whisper transcription and Playwright testing.
It enables users to:

Upload videos

Auto-generate test prompts

Upload/convert test cases

Execute tests and generate reports

Export results to PDF and send via email

🚀 Features
✅ Upload instructional videos (MP4/MOV/AVI/MKV)
✅ Transcribe with OpenAI Whisper (tiny, base, etc.)
✅ Auto-generate prompts to create structured test cases
✅ Upload JSON test cases and convert to Playwright scripts
✅ Run Playwright tests and capture logs
✅ Generate PDF reports from test results
✅ Email reports with Gmail SMTP
✅ View/download/delete all past logs, prompts, and PDFs

📁 Project Structure

qa_agent/
├── generator/
│   ├── transcribe_video.py
│   ├── chunk_and_embed.py
│   ├── generate_testcases.py
│   └── output/
├── scripts/
│   ├── convert_json_to_playwright.py
│   ├── tests/
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

🛠️ Setup Instructions
1. Clone the Repository

git clone https://github.com/<your-username>/QAAgent-Task---Chinna-Bathina.git
cd QAAgent-Task---Chinna-Bathina

2. Create Virtual Environment

python -m venv venv
venv\Scripts\activate  # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Download Required Models
Use this script (optional):

python download_models.py
It will:
Download Whisper model (base)
Download all-MiniLM-L6-v2 embeddings

🧪 How to Use
Launch the app:
streamlit run dashboard/app.py

Step-by-step workflow:

🔼 Upload a video (max 50MB)
🔠 Transcription auto-generated using Whisper
📝 Prompt generated to guide test case creation (manually via ChatGPT)
🔽 Upload the JSON test cases
🧪 Tests are auto-converted to Playwright and executed
📄 PDF reports are generated from test logs
📧 Optionally email report via Gmail

📤 Environment Variables
To use the email feature, set your Gmail credentials:

# .env or system env
SMTP_USER=your_gmail_address@gmail.com
SMTP_PASS=your_app_password
You must generate an App Password from your Google account.

📦 Dependencies
Major packages used:

streamlit
whisper
transformers / sentence-transformers
fpdf
matplotlib
playwright
smtplib / email

📄 Output Files
generator/output/: Transcripts, prompts, and JSON test cases

runner/results/logs/: Logs and test results

runner/results/test_bundle.zip: Exported test files

runner/results/*.pdf: Final QA test reports

🧹 Clean Git Setup
This repo excludes heavy models and caches. Large files like .pt and .safetensors are ignored via .gitignore.
Use download_models.py to fetch models locally.

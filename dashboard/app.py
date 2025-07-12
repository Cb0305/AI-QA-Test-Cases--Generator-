import streamlit as st
import os
import json
import subprocess
from datetime import datetime
import zipfile
import whisper
import smtplib
from email.message import EmailMessage
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
import textwrap

# === Config ===
UPLOAD_DIR = "uploaded_videos"
TRANSCRIPT_DIR = "generator/output"
PROMPT_DIR = TRANSCRIPT_DIR
MAX_SIZE_MB = 50
MODEL_SIZE = "base"
LOG_ARCHIVE_DIR = "runner/results/logs"
ZIP_EXPORT = "runner/results/test_bundle.zip"
FILE_DB = os.path.join(TRANSCRIPT_DIR, "file_index.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
os.makedirs(LOG_ARCHIVE_DIR, exist_ok=True)
os.environ["XDG_CACHE_HOME"] = os.path.abspath("whisper_cache")

# Paths
PDF_EXPORT = None  # Will be set dynamically

# === Streamlit Page Setup ===
st.set_page_config(page_title="⚙️ QA Agent Dashboard", layout="wide")
st.title(" ⚙️ QA Agent Test Dashboard")

# === Session State Initialization ===
for key in ["qa_check_triggered", "uploaded_video_name", "json_uploaded_name", "show_email_form", "transcribed", "pdf_ready", "base_name"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "qa_check_triggered" else False

# === Helper Functions ===

def update_file_db(entry):
    try:
        if os.path.exists(FILE_DB):
            with open(FILE_DB, "r", encoding="utf-8") as f:
                db = json.load(f)
        else:
            db = []
        db.append(entry)
        with open(FILE_DB, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        st.error(f"Failed to update file index: {e}")

def send_email_report(subject, body, attachment_path, to_email, smtp_user, smtp_pass):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg.set_content(body)
    with open(attachment_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=os.path.basename(attachment_path))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

def json_to_markdown(data):
    md = "# QA Test Cases\n\n"
    for tc in data:
        md += f"## {tc['id']}: {tc['title']}\n"
        md += "**Steps:**\n" + "\n".join([f"- {s}" for s in tc['steps']]) + "\n"
        md += f"**Expected Result:** {tc['expected_result']}\n\n"
    return md

def generate_pdf_from_log(log_text, pdf_path):
    from matplotlib import pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import textwrap

    # Config
    max_chars_per_line = 100
    margin_left = 0.05
    margin_top = 0.95
    line_spacing = 0.025  # vertical space between lines

    wrapped_lines = []
    for line in log_text.splitlines():
        wrapped_lines.extend(textwrap.wrap(line, width=max_chars_per_line) or [" "])

    with PdfPages(pdf_path) as pdf:
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")

        y = margin_top
        for line in wrapped_lines:
            if y <= 0.05:  # If space exhausted, create new page
                pdf.savefig(fig)
                plt.close(fig)
                fig, ax = plt.subplots(figsize=(8.5, 11))
                ax.axis("off")
                y = margin_top

            ax.text(margin_left, y, line, fontsize=10, family="monospace", verticalalignment='top')
            y -= line_spacing

        pdf.savefig(fig)
        plt.close(fig)


# === Main UI ===
if st.button("🛠️ Check QA from Video"):
    st.session_state.qa_check_triggered = True

if st.session_state.qa_check_triggered:
    st.subheader("📅 Upload video to transcribe and generate QA")

    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"], key="video_uploader")
    if uploaded_file and not st.session_state.transcribed:
        file_size_mb = len(uploaded_file.read()) / (1024 * 1024)
        uploaded_file.seek(0)
        if file_size_mb > MAX_SIZE_MB:
            st.error(f"⚠️ File too large ({file_size_mb:.2f}MB). Limit is {MAX_SIZE_MB}MB.")
        else:
            base_name = os.path.splitext(uploaded_file.name)[0]
            st.session_state.base_name = base_name
            video_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(video_path, "wb") as f:
                f.write(uploaded_file.read())

            st.info("🎠 Transcribing video with Whisper...")
            model = whisper.load_model(MODEL_SIZE)
            result = model.transcribe(video_path)
            transcript_text = result["text"]
            transcript_path = os.path.join(TRANSCRIPT_DIR, f"{base_name}.txt")
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)

            st.success("✅ Transcription complete!")
            st.session_state.transcribed = True
            st.text_area("📝 Transcript Preview", transcript_text, height=300)
            st.download_button("📅 Download Transcript", transcript_text, file_name=f"{base_name}.txt")

            prefilled_prompt = f"""You are a QA assistant. Convert the following transcript into structured JSON test cases.

Please generate test cases in this JSON format:
[
  {{
    "id": "TC001",
    "title": "Test title",
    "steps": ["step 1", "step 2"],
    "expected_result": "Expected result"
  }}
]

Transcript:
{transcript_text}
"""
            prompt_path = os.path.join(PROMPT_DIR, f"{base_name}_prompt.txt")
            with open(prompt_path, "w", encoding="utf-8") as f:
                f.write(prefilled_prompt)

            st.markdown("### 📋 Prompt to use in LLM")
            st.code(prefilled_prompt)
            st.markdown("""!! Please Generate JSON file using Prompt through ChatGPT manually""", unsafe_allow_html=True)
            st.download_button("📅 Download Prompt", prefilled_prompt, file_name=f"{base_name}_prompt.txt")

    st.subheader("📂 Or upload JSON test cases directly")
    json_file = st.file_uploader("Upload JSON test cases", type="json", key="json_upload")
    if json_file:
        try:
            json_content = json.load(json_file)
            base_name = os.path.splitext(json_file.name)[0]
            st.session_state.base_name = base_name
            json_path = os.path.join(TRANSCRIPT_DIR, f"{base_name}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_content, f, indent=2)
            st.success(f"✅ JSON saved to {json_path}")

            try:
                convert_cmd = ["python", "scripts/convert_json_to_playwright.py", base_name]
                subprocess.run(convert_cmd, check=True)
                st.success(f"🧪 Playwright test script generated for: {base_name}")
            except subprocess.CalledProcessError as e:
                st.error(f"❌ Failed to convert JSON to Playwright: {e}")

            md_content = json_to_markdown(json_content)
            md_path = os.path.join(TRANSCRIPT_DIR, f"{base_name}.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            st.download_button("📝 Download Markdown", md_content, file_name=f"{base_name}.md")
            if st.checkbox("👁️ Preview Markdown"):
                st.markdown(md_content)

        except Exception as e:
            st.error(f"❌ Failed to parse JSON: {e}")

if st.session_state.base_name and st.button("🔁 Run Tests Now"):
    with st.spinner("Running Playwright tests..."):
        result = subprocess.run(["python", "runner/run_tests.py",base_name], capture_output=True, text=True)

        base_name = st.session_state.base_name
        log_text = result.stdout + "\n" + result.stderr
        log_path = os.path.join(LOG_ARCHIVE_DIR, f"{base_name}_log.txt")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(log_text)

        all_test_logs = sorted([f for f in os.listdir(LOG_ARCHIVE_DIR) if f.startswith(f"test_{base_name}")], reverse=True)
        test_log_path = os.path.join(LOG_ARCHIVE_DIR, all_test_logs[0]) if all_test_logs else None
        test_log_text = ""
        if test_log_path and os.path.exists(test_log_path):
            with open(test_log_path, "r", encoding="utf-8") as tf:
                test_log_text = tf.read()

        combined_text = "[Playwright Output Log]\n\n" + log_text + "\n\n[Detailed Test Log]\n\n" + test_log_text
        st.text_area("📟 Log Output", combined_text, height=400)

        PDF_EXPORT = os.path.join(LOG_ARCHIVE_DIR, f"{base_name}_report.pdf")
        generate_pdf_from_log(combined_text, PDF_EXPORT)
        st.session_state.pdf_ready = True

if st.session_state.pdf_ready and PDF_EXPORT and os.path.exists(PDF_EXPORT):
    with open(PDF_EXPORT, "rb") as pdf_file:
        st.download_button(
            label="📄 Download Test Report PDF",
            data=pdf_file.read(),
            file_name=os.path.basename(PDF_EXPORT),
            mime="application/pdf"
        )

# === Email Section ===
st.subheader("📤 Send QA Report via Email")
if not st.session_state.show_email_form:
    if st.button("📤 Send Mail"):
        st.session_state.show_email_form = True
else:
    to_email = st.text_input("Recipient Email Address", key="recipient_input")
    custom_msg = st.text_area("Optional Message", "Attached is your QA Agent test report PDF.")
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    pdf_available = PDF_EXPORT and os.path.exists(PDF_EXPORT)

    if not smtp_user or not smtp_pass:
        st.warning("SMTP_USER and SMTP_PASS must be set in environment to enable emailing.")

    if st.button("✅ Send Email Now", disabled=not pdf_available or not to_email):
        if not pdf_available:
            st.error("PDF report not found. Generate the PDF first.")
        elif not to_email:
            st.error("Please enter a recipient email address.")
        else:
            sent = send_email_report(
                subject="QA Agent Test Report",
                body=custom_msg,
                attachment_path=PDF_EXPORT,
                to_email=to_email,
                smtp_user=smtp_user,
                smtp_pass=smtp_pass,
            )
            if sent:
                st.success("✅ Email sent successfully!")
    st.button("❌ Cancel", on_click=lambda: st.session_state.update(show_email_form=False))

# === Archive Management ===
st.subheader("📚 Archived Reports and Files")

# View & delete logs
log_files = sorted([f for f in os.listdir(LOG_ARCHIVE_DIR) if f.endswith(".txt")])
if log_files:
    selected_log = st.selectbox("📄 View Log File", log_files, key="log_select")
    with open(os.path.join(LOG_ARCHIVE_DIR, selected_log), "r", encoding="utf-8") as f:
        st.text_area("Log Contents", f.read(), height=300)
    if st.button("🗑️ Delete Selected Log"):
        try:
            os.remove(os.path.join(LOG_ARCHIVE_DIR, selected_log))
            st.success(f"Deleted: {selected_log}")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error deleting file: {e}")
else:
    st.info("No logs available.")

# View & delete prompt files
prompt_files = sorted([f for f in os.listdir(PROMPT_DIR) if f.endswith("_prompt.txt")])
if prompt_files:
    selected_prompt = st.selectbox("📜 View Prompt File", prompt_files, key="prompt_select")
    with open(os.path.join(PROMPT_DIR, selected_prompt), "r", encoding="utf-8") as f:
        content = f.read()
        st.text_area("Prompt Preview", content, height=300)
    st.download_button("⬇️ Download Prompt", content, file_name=selected_prompt)
    if st.button("🗑️ Delete Selected Prompt"):
        try:
            os.remove(os.path.join(PROMPT_DIR, selected_prompt))
            st.success(f"Deleted: {selected_prompt}")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error deleting file: {e}")
else:
    st.info("No prompts available.")

# View & delete PDF reports
pdf_files = sorted([f for f in os.listdir(LOG_ARCHIVE_DIR) if f.endswith("_report.pdf")])
if pdf_files:
    selected_pdf = st.selectbox("📑 View PDF Report", pdf_files, key="pdf_select")
    with open(os.path.join(LOG_ARCHIVE_DIR, selected_pdf), "rb") as f:
        pdf_data = f.read()
    st.download_button("⬇️ Download PDF", pdf_data, file_name=selected_pdf)
    if st.button("🗑️ Delete Selected PDF"):
        try:
            os.remove(os.path.join(LOG_ARCHIVE_DIR, selected_pdf))
            st.success(f"Deleted: {selected_pdf}")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error deleting file: {e}")
else:
    st.info("No PDF reports available.")

# === Final UI timestamp ===
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

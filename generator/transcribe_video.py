import os
import datetime
import whisper
import streamlit as st

# === Configuration ===
UPLOAD_DIR = "uploaded_videos"
TRANSCRIPT_DIR = "generator/output"
MAX_SIZE_MB = 50
MODEL_SIZE = "base"  # Change to "small" or "medium" if needed

# Safe cache for Whisper
os.environ["XDG_CACHE_HOME"] = os.path.abspath("whisper_cache")

# Ensure folders exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

# === Streamlit UI ===
st.title("🧪 QA Agent Dashboard")
st.subheader("🎥 Check QA from Video")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file:
    file_size_mb = len(uploaded_file.read()) / (1024 * 1024)
    uploaded_file.seek(0)

    if file_size_mb > MAX_SIZE_MB:
        st.error(f"⚠️ File too large ({file_size_mb:.2f}MB). Must be under {MAX_SIZE_MB}MB.")
    else:
        with st.spinner("🌀 Transcribing video using Whisper..."):

            # Step 1: Save uploaded video
            base_name = os.path.splitext(uploaded_file.name)[0]
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_base = f"{base_name}_{timestamp}"
            video_path = os.path.join(UPLOAD_DIR, f"{unique_base}.mp4")

            with open(video_path, "wb") as f:
                f.write(uploaded_file.read())

            # Step 2: Load Whisper model
            st.info("📥 Loading Whisper model...")
            model = whisper.load_model(MODEL_SIZE)

            # Step 3: Transcribe
            st.info(f"🔊 Transcribing {uploaded_file.name}...")
            result = model.transcribe(video_path)
            transcript_text = result["text"]

            # Step 4: Save transcript
            transcript_path = os.path.join(TRANSCRIPT_DIR, f"{unique_base}.txt")
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)

            st.success("✅ Transcription complete!")

            # Step 5: Display and allow download
            st.download_button("📥 Download Transcript", data=transcript_text, file_name=f"{unique_base}.txt")
            st.text_area("📝 Transcript Preview", transcript_text, height=300)


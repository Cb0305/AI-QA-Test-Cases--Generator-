import os
import whisper
from sentence_transformers import SentenceTransformer

def download_whisper_model(model_name="base", cache_dir="whisper_cache"):
    model_path = os.path.join(cache_dir, model_name)
    if not os.path.exists(model_path):
        print(f"Downloading Whisper model '{model_name}' to '{cache_dir}'...")
        os.makedirs(cache_dir, exist_ok=True)
        # This downloads and caches the model under cache_dir/whisper/base.pt internally
        model = whisper.load_model(model_name, download_root=cache_dir)
        print("Whisper model downloaded.")
    else:
        print(f"Whisper model '{model_name}' already exists at '{model_path}'.")

def download_sentence_transformer(model_name, cache_dir):
    model_path = os.path.join(cache_dir, model_name.replace("/", "_"))
    if not os.path.exists(model_path):
        print(f"Downloading SentenceTransformer model '{model_name}' to '{cache_dir}'...")
        os.makedirs(cache_dir, exist_ok=True)
        model = SentenceTransformer(model_name, cache_folder=cache_dir)
        print(f"SentenceTransformer model '{model_name}' downloaded.")
    else:
        print(f"SentenceTransformer model '{model_name}' already exists at '{model_path}'.")

if __name__ == "__main__":
    # Paths to cache directories (adjust as needed)
    whisper_cache_dir = "whisper_cache"
    hf_cache_dir = ".hf_cache"

    download_whisper_model("base", whisper_cache_dir)
    download_sentence_transformer("sentence-transformers/all-MiniLM-L6-v2", hf_cache_dir)
    download_sentence_transformer("sentence-transformers/multi-qa-MiniLM-L6-dot-v1", hf_cache_dir)

    print("All models are ready!")

# File: generator/chunk_and_embed.py

import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Configuration
DEFAULT_DB_DIR = "../faiss_index"
DEFAULT_TRANSCRIPT_DIR = "../generator/output"
CACHE_DIR = "./models_cache"

def chunk_and_embed_transcript(transcript_path, db_dir=DEFAULT_DB_DIR):
    if not os.path.exists(transcript_path):
        print(f"[❌] Transcript file not found: {transcript_path}")
        return

    print(f"[📄] Loading transcript: {transcript_path}")
    loader = TextLoader(transcript_path)
    documents = loader.load()

    print("[✂️] Splitting transcript into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"[🧠] Total chunks created: {len(chunks)}")

    print("[📦] Embedding chunks using HuggingFace model (offline)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/multi-qa-MiniLM-L6-dot-v1",
        cache_folder=CACHE_DIR
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)

    # Auto-create a subfolder for this specific file embedding
    base_name = os.path.splitext(os.path.basename(transcript_path))[0]
    output_path = os.path.join(db_dir, base_name)
    os.makedirs(output_path, exist_ok=True)

    print(f"[💾] Saving vectorstore to: {output_path}")
    vectorstore.save_local(output_path)

    print("[✅] Chunking & embedding complete!")


if __name__ == "__main__":
    # Sample usage for manual testing
    latest_file = sorted(
        [f for f in os.listdir(DEFAULT_TRANSCRIPT_DIR) if f.endswith(".txt")],
        key=lambda f: os.path.getmtime(os.path.join(DEFAULT_TRANSCRIPT_DIR, f)),
        reverse=True
    )[0]

    path_to_transcript = os.path.join(DEFAULT_TRANSCRIPT_DIR, latest_file)
    chunk_and_embed_transcript(path_to_transcript)

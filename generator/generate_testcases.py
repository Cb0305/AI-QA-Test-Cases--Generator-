# File: generator/generate_testcases.py

import os
import sys
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate

# Config
BASE_VECTORSTORE_DIR = "../faiss_index"
OUTPUT_DIR = "output"
HF_CACHE_DIR = "../.hf_cache"

def load_vectorstore(subdir):
    path = os.path.join(BASE_VECTORSTORE_DIR, subdir)
    if not os.path.exists(path):
        print(f"[❌] Vectorstore not found: {path}")
        return None

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        cache_folder=HF_CACHE_DIR
    )

    return FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=True  # ✅ required for langchain >= 0.2
    )

def retrieve_context(query, vectorstore, top_k=3):
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    docs = retriever.get_relevant_documents(query)
    return "\n\n".join([doc.page_content for doc in docs])

def format_for_chatgpt(context, query):
    prompt = f"""
You are a QA assistant. Convert the following user tutorial content into clear, structured test cases in JSON format.

🎯 Test Case Example:
{{
  "id": "TC001",
  "title": "Verify user login with valid credentials",
  "steps": [
    "Navigate to login page",
    "Enter valid email and password",
    "Click Login button"
  ],
  "expected_result": "User is redirected to dashboard",
  "priority": "High"
}}

Now generate test cases based on this instruction: "{query}".

📘 Tutorial Content:
\"\"\"
{context}
\"\"\"
"""
    return prompt.strip()

def save_prompt_file(content, base_name):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    prompt_file = os.path.join(OUTPUT_DIR, f"{base_name}_prompt.txt")
    with open(prompt_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[✅] Prompt saved to: {prompt_file}")

def main():
    if len(sys.argv) < 2:
        print("❗ Usage: python generate_testcases.py <base_name_from_transcript>")
        print("   Example: python generate_testcases.py myvideo_20250706_0830")
        return

    base_name = sys.argv[1]
    print(f"[🔁] Loading vectorstore for: {base_name}")
    vectorstore = load_vectorstore(base_name)
    if not vectorstore:
        return

    print("\n📌 Enter your test case topic (e.g., 'interview creation flow'):")
    query = input("🔍 Topic: ")

    print("[📂] Retrieving relevant transcript chunks...")
    context = retrieve_context(query, vectorstore)

    print("[📝] Formatting test case prompt...")
    prompt = format_for_chatgpt(context, query)

    save_prompt_file(prompt, base_name)

    print("\n🚀 Next Step:")
    print(f"1. Open the generated prompt: output/{base_name}_prompt.txt")
    print("2. Paste into ChatGPT or your LLM")
    print(f"3. Save the JSON result as: output/{base_name}.json")
    print("4. Run Playwright conversion!")

if __name__ == "__main__":
    main()

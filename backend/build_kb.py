# backend/build_kb.py

import os

from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import Chroma
from my_embeddings import GeminiEmbeddings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_DIR = os.path.join(BASE_DIR, "data", "lab_kb")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")


def load_kb_texts():
    docs = []
    for fname in os.listdir(KB_DIR):
        if fname.endswith(".txt"):
            path = os.path.join(KB_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                docs.append(f.read())
    return docs


def main():
    texts = load_kb_texts()
    if not texts:
        print(f"❌ No .txt files found in {KB_DIR}. Please add KB files (cbc.txt, lipids.txt, etc.).")
        return

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    # create_documents expects a list of strings or docs
    chunks = splitter.create_documents(texts)

    embeddings = GeminiEmbeddings()  # will read GEMINI_API_KEY env var
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
    )
    vectordb.persist()
    print("✅ Knowledge base built and stored at:", CHROMA_DIR)


if __name__ == "__main__":
    main()

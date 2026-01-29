# backend/main.py

import io
from typing import Optional, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader

from dotenv import load_dotenv
load_dotenv()


from rag_pipeline import answer_question
from parsed_report_utils import parse_report_text

app = FastAPI(title="Medical Report Explainer (Safe RAG)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage (per process)
SESSION_REPORT_TEXT: Optional[str] = None
SESSION_PARSED_VALUES: Optional[Dict[str, Any]] = None


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
        text += "\n"
    return text


@app.post("/upload_report")
async def upload_report(file: UploadFile = File(...)):
    global SESSION_REPORT_TEXT, SESSION_PARSED_VALUES

    content = await file.read()
    report_text = extract_text_from_pdf(content)
    SESSION_REPORT_TEXT = report_text
    SESSION_PARSED_VALUES = parse_report_text(report_text)

    return {
        "message": "Report uploaded and processed successfully.",
        "approx_length": len(report_text),
        "parsed_values": SESSION_PARSED_VALUES or {},
    }


@app.post("/ask")
async def ask(question: str = Form(...)):
    global SESSION_REPORT_TEXT, SESSION_PARSED_VALUES

    ans = answer_question(
        question,
        report_text=SESSION_REPORT_TEXT,
        parsed_values=SESSION_PARSED_VALUES,
    )

    return {"answer": ans, "parsed_values": SESSION_PARSED_VALUES or {}}

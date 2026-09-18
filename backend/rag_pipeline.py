# backend/rag_pipeline.py
import os
from typing import List, Optional, Dict, Any, Sequence

from dotenv import load_dotenv
load_dotenv()


from google import genai
try:
    # langchain community Chroma (you already use it)
    from langchain_chroma import Chroma
except Exception:
    from langchain_community.vectorstores import Chroma

# Document objects may vary; we only need .page_content or str conversion
from my_embeddings import GeminiEmbeddings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


SYSTEM_PROMPT = """
You are a cautious medical information assistant.
You ONLY provide general educational explanations about lab tests and blood reports.
You are NOT a doctor. You do NOT diagnose diseases, and you do NOT give treatment plans or medication doses.
If the user asks for a diagnosis or treatment, clearly say you cannot do that and ask them to consult a qualified doctor.
Use the retrieved context and parsed lab values to produce an educational answer, as points.
Always remind the user to consult their doctor for personal medical advice.
"""


def get_vectorstore():
    embeddings = GeminiEmbeddings(api_key=GEMINI_API_KEY)
    if not GEMINI_API_KEY:
        # raise at use time rather than import time
        raise ValueError("Please set GEMINI_API_KEY environment variable before running.")
    vectordb = Chroma(embedding_function=embeddings, persist_directory=CHROMA_DIR)
    return vectordb

def _format_parsed(parsed_values: Optional[Dict[str, Any]]) -> str:
    if not parsed_values:
        return "No structured values available."
    lines = []
    for k, v in parsed_values.items():
        val = v.get("value")
        unit = v.get("unit", "")
        lines.append(f"{k}: {val} {unit}".strip())
    return "\n".join(lines)


def _doc_to_text(doc) -> str:
    """Robust conversion of different document shapes to text."""
    if doc is None:
        return ""
    # LangChain Document: .page_content
    if hasattr(doc, "page_content"):
        return str(doc.page_content)
    # dict with page_content
    if isinstance(doc, dict) and "page_content" in doc:
        return str(doc["page_content"])
    # if it's a (doc, score) tuple sometimes returned by older retrievers
    if isinstance(doc, (list, tuple)) and len(doc) >= 1:
        candidate = doc[0]
        if hasattr(candidate, "page_content"):
            return str(candidate.page_content)
        return str(candidate)
    if isinstance(doc, str):
        return doc
    return str(doc)


def _call_retriever_for_docs(retriever, query: str) -> Sequence:
    """
    Call the available retriever function in a backwards-compatible manner.
    Supports:
      - retriever.get_relevant_documents(query)
      - retriever._get_relevant_documents(query, run_manager=None)
      - retriever.get_relevant_documents_with_score(query) -> returns docs or (doc,score)
    """
    # Preferred public API
    if hasattr(retriever, "get_relevant_documents"):
        try:
            return retriever.get_relevant_documents(query)
        except TypeError:
            # Some versions may require keyword-only args or different signature; fall through
            pass

    # Private variant that in some LC versions requires run_manager kwarg
    if hasattr(retriever, "_get_relevant_documents"):
        try:
            # call with run_manager=None to satisfy keyword-only requirement if present
            return retriever._get_relevant_documents(query, run_manager=None)
        except TypeError:
            # if still TypeError, try without run_manager
            return retriever._get_relevant_documents(query)

    # Older interface returning (doc, score)
    if hasattr(retriever, "get_relevant_documents_with_score"):
        docs_with_scores = retriever.get_relevant_documents_with_score(query)
        # Normalize to docs only
        normalized = []
        for item in docs_with_scores:
            if isinstance(item, (list, tuple)) and len(item) >= 1:
                normalized.append(item[0])
            else:
                normalized.append(item)
        return normalized

    # As a last resort, try calling retriever directly (some retrievers are callables)
    if callable(retriever):
        try:
            return retriever(query)
        except Exception:
            pass

    raise RuntimeError("Retriever has no known retrieval method for this LangChain version.")


def answer_question(question: str, report_text: Optional[str] = None, parsed_values: Optional[Dict[str, Any]] = None, raw_output: bool = True) -> str:
    """
    Retrieve relevant docs from vectorstore and call Gemini to generate a safe answer.

    If raw_output=True (default) returns the model's text exactly as received (no appended warnings).
    If raw_output=False the function will append the project safety reminder if missing.
    """
    try:
        vectordb = get_vectorstore()
        retriever = vectordb.as_retriever(search_kwargs={"k": 5})

        # Retrieve documents robustly
        docs = _call_retriever_for_docs(retriever, question)

        # Convert to text
        context_parts = []
        for d in docs:
            context_parts.append(_doc_to_text(d))
        context = "\n\n".join(context_parts).strip()

        if report_text:
            excerpt = report_text if len(report_text) <= 3000 else report_text[:3000]
            if context:
                context = context + "\n\n" + "Lab report text:\n" + excerpt
            else:
                context = "Lab report text:\n" + excerpt

        parsed_str = _format_parsed(parsed_values)

        user_content = f"""
User question:
{question}

Context from knowledge base:
{context}

Parsed values from user's report:
{parsed_str}

Please provide a clear, friendly explanation. Keep things general and give as points also include a reminder that this is not a diagnosis and to consult a qualified doctor.
"""

        client = genai.Client(api_key=GEMINI_API_KEY)
        model_name = os.getenv("GEMINI_MODEL") or "gemini-flash-latest"

        resp = client.models.generate_content(
            model=model_name,
            contents=user_content,
           # temperature=0.1,
           # max_output_tokens=800,
        )

        # Extract text from response robustly
        out_text = ""
        if hasattr(resp, "text") and resp.text:
            out_text = resp.text
        elif hasattr(resp, "output") and isinstance(resp.output, str):
            out_text = resp.output
        elif hasattr(resp, "candidates") and len(resp.candidates) > 0:
            cand = resp.candidates[0]
            if hasattr(cand, "content"):
                out_text = cand.content
            elif hasattr(cand, "text"):
                out_text = cand.text
            else:
                out_text = str(cand)
        else:
            out_text = str(resp)

        # If caller asked for raw LLM output, return it exactly.
        if raw_output:
            return out_text

        # Otherwise ensure safety note is present
        if "not a diagnosis" not in out_text.lower():
            out_text += "\n\n⚠️ This is general educational information, not a medical diagnosis. Please consult a qualified doctor."

        return out_text

    except Exception as e:
        # Log the error for debugging; re-raise so FastAPI returns 500 (or catch in main to return friendly message)
        print("RAG pipeline error:", repr(e))
        raise

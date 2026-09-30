# 🩺 Medical Report Explainer

An AI-powered web application that helps users understand medical laboratory reports in simple, easy-to-understand language.

The application allows users to upload a laboratory report, extracts report text and relevant laboratory values, retrieves relevant information from a curated medical knowledge base using semantic search, and uses Google's Gemini Large Language Model to generate contextual educational explanations.

The project implements a Retrieval-Augmented Generation (RAG) architecture to combine information from the application's medical knowledge base with values extracted from the user's laboratory report.

> ⚠️ **Medical Disclaimer:** This application is intended for educational and informational purposes only. It does not provide medical diagnosis, treatment recommendations, or medication advice. Users should consult a qualified healthcare professional for personal medical advice.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Solution](#-solution)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Application Workflow](#-application-workflow)
- [RAG Architecture](#-rag-architecture)
- [Technology Stack](#-technology-stack)
- [Why These Technologies](#-why-these-technologies)
- [Project Structure](#-project-structure)
- [Knowledge Base](#-knowledge-base)
- [Laboratory Value Extraction](#-laboratory-value-extraction)
- [Semantic Search](#-semantic-search)
- [Gemini Integration](#-gemini-integration)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [Running the Project](#-running-the-project)
- [Example](#-example)
- [Security](#-security)
- [Limitations](#-limitations)
- [Future Improvements](#-future-improvements)
- [Medical Disclaimer](#-medical-disclaimer)
- [Author](#-author)

---

## 🔎 Overview

Understanding laboratory reports can be difficult for people who are unfamiliar with medical terminology.

A laboratory report may contain measurements such as Hemoglobin, WBC, RBC, Platelets, Blood Glucose, HbA1c, Cholesterol, HDL, LDL, Triglycerides, Bilirubin, ALT, AST, Creatinine, Urea, Sodium, Potassium, TSH, Vitamin D, Vitamin B12, and many other parameters.

The **Medical Report Explainer** simplifies this information by allowing users to upload laboratory reports and ask questions about their results.

Instead of simply sending the report to an LLM, the application retrieves relevant information from a curated medical knowledge base and combines it with extracted report information before generating the response.

---

## 🎯 Problem Statement

Medical laboratory reports contain technical terms, abbreviations, numerical values, and measurement units that can be difficult for non-medical users to understand.

A general-purpose AI model can explain medical terminology, but relying only on an LLM does not provide a controlled knowledge source for the application.

This project therefore aims to:

1. Accept a laboratory report from the user.
2. Extract useful information from the report.
3. Identify laboratory test values.
4. Retrieve relevant medical information from a curated knowledge base.
5. Combine retrieved context with the user's report information.
6. Use Gemini to generate a clear educational explanation.

---

## 💡 Solution

The project uses a **Retrieval-Augmented Generation (RAG)** approach.

```text
User uploads laboratory report
              ↓
       PDF Text Extraction
              ↓
      Laboratory Value Parsing
              ↓
       User asks a question
              ↓
        Semantic Search
              ↓
      Retrieve relevant medical
          knowledge from ChromaDB
              ↓
       Combine retrieved context
       + report values + question
              ↓
             Gemini
              ↓
      Context-aware explanation
              ↓
           User Interface
```

---

## ✨ Key Features

- 📄 Upload medical laboratory reports
- 🔤 Extract text from PDF reports
- 🧪 Parse common laboratory values
- 🧠 Semantic search over a curated medical knowledge base
- 📚 Retrieval-Augmented Generation
- 🗄️ ChromaDB vector database
- 🤖 Gemini LLM response generation
- 💬 Ask questions about laboratory results
- 📊 Explain medical terminology in simple language
- 🔐 Environment-variable based API key configuration
- 🌐 HTML/CSS/JavaScript frontend
- ⚡ FastAPI backend

---

## 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │        USER          │
                         │ Upload Report        │
                         │ Ask Question         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FRONTEND        │
                         │ HTML / CSS / JS      │
                         └──────────┬───────────┘
                                    │
                              HTTP Request
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FASTAPI        │
                         │      BACKEND API     │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
          ┌────────────────────┐        ┌────────────────────┐
          │ PDF Text           │        │ Laboratory Value   │
          │ Extraction         │        │ Parsing             │
          └─────────┬──────────┘        └─────────┬──────────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │    RAG PIPELINE      │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
          ┌────────────────────┐        ┌────────────────────┐
          │      ChromaDB      │        │ Parsed Report      │
          │ Medical Knowledge  │        │ Values              │
          │ Embeddings         │        │                    │
          └─────────┬──────────┘        └─────────┬──────────┘
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │     GEMINI LLM       │
                         │ Response Generation  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FRONTEND        │
                         │ Display Explanation  │
                         └──────────────────────┘
```

---

## 🔄 Application Workflow

### 1. Upload Report

The user selects a laboratory report PDF through the frontend.

### 2. Extract PDF Text

The FastAPI backend extracts readable text from the uploaded report.

Example:

```text
Hemoglobin       13.5 g/dL
WBC              7,500 /µL
Glucose          105 mg/dL
Creatinine       0.9 mg/dL
Total Cholesterol 210 mg/dL
```

### 3. Parse Laboratory Values

The extracted text is processed to identify recognized laboratory parameters.

Example:

```python
{
    "Hemoglobin": {
        "value": 13.5,
        "unit": "g/dL"
    },
    "Glucose": {
        "value": 105,
        "unit": "mg/dL"
    },
    "Creatinine": {
        "value": 0.9,
        "unit": "mg/dL"
    }
}
```

### 4. Retrieve Relevant Knowledge

The user's question is converted into an embedding and compared against medical knowledge embeddings stored in ChromaDB.

### 5. Augment the Prompt

The retrieved knowledge is combined with:

- User question
- Parsed laboratory values
- Relevant report text

### 6. Generate the Answer

Gemini receives the augmented context and generates an educational explanation.

### 7. Display the Response

The response is returned through FastAPI and displayed by the frontend.

---

## 🧠 RAG Architecture

The project follows the three major stages of RAG:

```text
RETRIEVE
    ↓
AUGMENT
    ↓
GENERATE
```

### Retrieve

Relevant medical documents are retrieved from ChromaDB using semantic similarity.

### Augment

The retrieved medical context is combined with the user's question and the parsed laboratory information.

```text
User Question
       +
Retrieved Medical Knowledge
       +
Parsed Laboratory Values
       +
Relevant Report Text
```

### Generate

Gemini uses this augmented prompt to generate the final response.

---

## 📚 Knowledge Base

The project uses a curated medical knowledge base containing information about common laboratory tests.

Example structure:

```text
data/
└── lab_kb/
    ├── cbc.txt
    ├── electrolytes.txt
    ├── general_terms.txt
    ├── kidney.txt
    ├── lipids.txt
    ├── liver.txt
    ├── sugar.txt
    ├── thyroid.txt
    └── vitamins.txt
```

The knowledge-base documents are converted into embeddings and stored in ChromaDB.

---

## 🗄️ Why ChromaDB?

ChromaDB is used as the vector database for the medical knowledge base.

```text
Knowledge Base Documents
          ↓
       Embeddings
          ↓
   Numerical Vectors
          ↓
       ChromaDB
```

When a user asks a question:

```text
User Question
      ↓
Question Embedding
      ↓
Similarity Search
      ↓
Relevant Documents
```

The retrieved documents become context for the Gemini generation step.

### Why are report values not stored in ChromaDB?

The medical knowledge base is relatively static information that benefits from vector search.

The uploaded report values are **user-specific, temporary structured data**. They are extracted for the current question and passed directly into the prompt rather than being stored as knowledge-base embeddings.

---

## 🔍 Semantic Search

Semantic search finds information based on meaning rather than requiring an exact keyword match.

For example:

```text
User:
"Why is my bad cholesterol high?"
```

The system can retrieve information about:

```text
LDL cholesterol
```

even when the exact phrase "bad cholesterol" does not appear in the knowledge-base document.

This is achieved using embeddings and vector similarity search.

---

## 🧪 Laboratory Value Extraction

The parser identifies common laboratory parameters such as:

```text
Hemoglobin
RBC
WBC
Platelets
Glucose
HbA1c
Total Cholesterol
HDL
LDL
Triglycerides
Bilirubin
ALT
AST
Creatinine
Urea
Sodium
Potassium
TSH
Vitamin D
Vitamin B12
```

The parser attempts to extract:

```text
Test Name
     +
Value
     +
Unit
```

For example:

```text
Hemoglobin: 13.5 g/dL
```

becomes:

```text
Test: Hemoglobin
Value: 13.5
Unit: g/dL
```

---

## 🤖 Gemini Integration

Google Gemini is used as the **Large Language Model** responsible for generating the final explanation.

Gemini receives:

```text
User Question
+
Retrieved Knowledge
+
Parsed Report Values
+
Relevant Report Text
```

The project also uses a system prompt that instructs the model to:

- Provide general educational information
- Avoid diagnosis
- Avoid medication prescriptions
- Avoid medication doses
- Avoid treatment plans
- Recommend consulting a qualified healthcare professional

---

## 🧩 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend and AI processing |
| FastAPI | REST API and backend server |
| HTML5 | Frontend structure |
| CSS3 | Frontend styling |
| JavaScript | Frontend interaction and API communication |
| LangChain | Retrieval/vector-store integration |
| ChromaDB | Vector database |
| Gemini | LLM response generation |
| Embeddings | Semantic similarity search |
| PDF processing library | PDF text extraction |
| python-dotenv | Environment variable management |

---

## 💡 Why These Technologies?

### Python

Python provides a strong ecosystem for AI/ML, NLP, PDF processing, embeddings, and vector databases.

### FastAPI

FastAPI provides a lightweight and modern way to build REST APIs in Python and connects the frontend with the RAG pipeline.

### HTML/CSS/JavaScript

A simple frontend is sufficient for the current application's requirements and avoids unnecessary frontend-framework complexity.

### LangChain

LangChain provides components for document handling, vector-store integration, and retrieval workflows used in the RAG pipeline.

### ChromaDB

ChromaDB is designed for storing and retrieving vector embeddings and supports semantic similarity search.

### Gemini

Gemini performs natural-language generation using the retrieved context and report information.

---

## 📁 Project Structure

```text
medical-report-explainer/
│
├── backend/
│   ├── main.py
│   ├── rag_pipeline.py
│   ├── build_kb.py
│   ├── my_embeddings.py
│   ├── parsed_report_utils.py
│   ├── requirements.txt
│   │
│   ├── data/
│   │   └── lab_kb/
│   │       ├── cbc.txt
│   │       ├── electrolytes.txt
│   │       ├── general_terms.txt
│   │       ├── kidney.txt
│   │       ├── lipids.txt
│   │       ├── liver.txt
│   │       ├── sugar.txt
│   │       ├── thyroid.txt
│   │       └── vitamins.txt
│   │
│   └── chroma_db/
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── .gitignore
├── README.md
└── LICENSE
```

> `venv/`, `.env`, Python cache files, and other local/generated files should not be committed to GitHub.

---

## ⚙️ Installation

### Prerequisites

- Python 3.10+
- Git
- Gemini API key
- Internet connection

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd medical-report-explainer
```

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scriptsctivate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

## 🔑 Environment Variables

Create:

```text
backend/.env
```

Add:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=YOUR_AVAILABLE_GEMINI_MODEL
```

Never commit `.env` to GitHub.

---

## 🧠 Build the Knowledge Base

Navigate to the backend:

```bash
cd backend
```

Run:

```bash
python build_kb.py
```

This processes the medical knowledge documents and creates the vector database used by the RAG pipeline.

---

## ▶️ Run the Backend

From the `backend` directory:

```bash
uvicorn main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 🌐 Run the Frontend

The frontend is located in:

```text
frontend/
```

For local development:

```bash
cd frontend
python -m http.server 5500
```

Then open:

```text
http://localhost:5500
```

---

## 🧪 Example

Suppose a report contains:

```text
Hemoglobin: 13.5 g/dL
Glucose: 105 mg/dL
Total Cholesterol: 210 mg/dL
Creatinine: 0.9 mg/dL
```

The user asks:

```text
What does my cholesterol result mean?
```

The application performs:

```text
Question
   ↓
Semantic Search
   ↓
Retrieve cholesterol-related information
   ↓
Parsed report values
   ↓
Create augmented prompt
   ↓
Gemini
   ↓
Educational explanation
```

---

## 🔌 Backend Flow

```text
Frontend
    │
    │ HTTP Request
    ▼
FastAPI
    │
    ▼
Report Processing
    │
    ├───────────────┐
    │               │
    ▼               ▼
PDF Extraction   Lab Parsing
    │               │
    └───────┬───────┘
            │
            ▼
       RAG Pipeline
            │
       ┌────┴────┐
       ▼         ▼
   ChromaDB   Report Values
       │         │
       └────┬────┘
            ▼
       Gemini Prompt
            │
            ▼
          Gemini
            │
            ▼
        FastAPI
            │
            ▼
        Frontend
```

---

## 🔐 Security

The Gemini API key is stored using an environment variable:

```env
GEMINI_API_KEY=...
```

Recommended `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
.DS_Store
```

Never hard-code API keys in source code.

---

## ⚠️ Current Limitations

- Text-based PDFs are easier to process than scanned/image-only reports.
- Different laboratories use different layouts, abbreviations, units, and reference ranges.
- Laboratory parsing depends on predefined patterns.
- The application provides educational explanations rather than clinical diagnosis.
- LLM-generated responses can contain inaccuracies.
- RAG improves grounding but does not guarantee medical correctness.

---

## 🔮 Future Improvements

### PDF Processing
- OCR support
- Scanned report support
- Better table extraction
- Support for more report formats

### Laboratory Parser
- More laboratory tests
- Automatic unit detection
- Reference-range extraction
- Abnormal-value detection
- Better handling of different layouts

### RAG
- Improved chunking
- Metadata filtering
- Hybrid search
- Retrieval evaluation
- RAG evaluation
- Source citations

### User Features
- Authentication
- Report history
- Saved reports
- Report comparison
- Patient dashboard

### Accessibility
- Multi-language explanations
- Voice-based explanations
- Improved accessibility

### Deployment
- Cloud deployment
- Production database
- Secure API configuration
- Monitoring and logging
- Automated CI/CD

---

## 📝 Resume Description

> **Medical Report Explainer** — Developed an AI-powered web application that extracts laboratory report data, performs semantic search over a curated medical knowledge base using ChromaDB, and generates context-aware explanations using a RAG pipeline with Gemini LLM. Built REST APIs with FastAPI and integrated an HTML/CSS/JavaScript frontend for report upload and interactive question answering.

---

## 🧑‍💻 Technical Highlights

This project demonstrates practical implementation of:

- Retrieval-Augmented Generation (RAG)
- Semantic Search
- Vector Databases
- Text Embeddings
- Large Language Models
- PDF Text Extraction
- Natural Language Processing
- Structured Laboratory Value Extraction
- REST API Development
- Frontend–Backend Integration
- Environment-based Configuration

---

## ⚠️ Medical Disclaimer

This project is **not a medical diagnostic tool**.

The information generated by the application is intended only for general educational and informational purposes. It should not be considered professional medical advice, diagnosis, or treatment.

Always consult a qualified healthcare professional for interpretation of personal medical results.

---

## 👨‍💻 Author

**Jassim Ali**

B.Tech Computer Science & Engineering

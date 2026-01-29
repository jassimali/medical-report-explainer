// frontend/script.js

const API_BASE = "http://127.0.0.1:8000";

// State
let typingTimeout = null;
let isTyping = false;

// DOM Elements
const DOM = {
  uploadForm: document.getElementById("upload-form"),
  reportFileInput: document.getElementById("report-file"),
  uploadStatus: document.getElementById("upload-status"),
  parsedValuesDiv: document.getElementById("parsed-values"),
  uploadBtn: document.getElementById("upload-btn"),
  askForm: document.getElementById("ask-form"),
  questionInput: document.getElementById("question"),
  askBtn: document.getElementById("ask-btn"),
  chatDiv: document.getElementById("chat"),
  stopBtn: document.getElementById("stop-btn"),
};

// Utility function to format text with line breaks
const formatText = (text) => text.split('\n').map(line => line.trim()).filter(Boolean).join('<br>');

function addMessage(role, text, isStreaming = false) {
  const div = document.createElement("div");
  div.classList.add("message", role === "me" ? "me" : "bot");

  const bubble = document.createElement("span");
  div.appendChild(bubble);
  DOM.chatDiv.appendChild(div);
  DOM.chatDiv.scrollTop = DOM.chatDiv.scrollHeight;

  if (isStreaming && role === "bot") {
    typeWriter(bubble, text);
  } else {
    bubble.innerHTML = formatText(text);
  }
}

function stopTyping() {
  if (typingTimeout !== null) {
    clearTimeout(typingTimeout);
    typingTimeout = null;
    isTyping = false;
    DOM.stopBtn.style.display = "none";
  }
}

function typeWriter(element, text, speed = 30) {
  let index = 0;
  let currentText = "";
  isTyping = true;
  DOM.stopBtn.style.display = "inline-block";
  
  const typeNextChar = () => {
    if (index < text.length && isTyping) {
      currentText += text[index];
      element.innerHTML = formatText(currentText) + '<span class="cursor">|</span>';
      DOM.chatDiv.scrollTop = DOM.chatDiv.scrollHeight;
      index++;
      typingTimeout = setTimeout(typeNextChar, speed);
    } else if (index >= text.length) {
      element.innerHTML = formatText(currentText);
      isTyping = false;
      DOM.stopBtn.style.display = "none";
      DOM.chatDiv.scrollTop = DOM.chatDiv.scrollHeight;
    }
  };
  
  typeNextChar();
}

function renderParsedValues(parsed) {
  DOM.parsedValuesDiv.innerHTML = "";
  
  if (!parsed || Object.keys(parsed).length === 0) {
    DOM.parsedValuesDiv.innerHTML = "<p class='small'>No structured values were detected. You can still ask general questions.</p>";
    return;
  }

  const fragment = document.createDocumentFragment();
  
  const title = document.createElement("p");
  title.innerHTML = "<strong>Detected values (approx):</strong>";
  fragment.appendChild(title);

  const ul = document.createElement("ul");
  ul.id = "parsed-list";
  
  Object.entries(parsed).forEach(([testName, info]) => {
    const li = document.createElement("li");
    li.classList.add("small");
    li.textContent = `${testName}: ${info.value} ${info.unit || ""}`;
    ul.appendChild(li);
  });
  
  fragment.appendChild(ul);
  DOM.parsedValuesDiv.appendChild(fragment);
}

async function handleUpload(e) {
  e.preventDefault();
  const file = DOM.reportFileInput.files[0];
  
  if (!file) {
    alert("Please select a PDF file.");
    return;
  }

  DOM.uploadBtn.disabled = true;
  DOM.uploadStatus.textContent = "Uploading and processing report...";

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/upload_report`, {
      method: "POST",
      body: formData,
    });
    
    if (!res.ok) throw new Error("Upload failed");
    
    const data = await res.json();
    DOM.uploadStatus.textContent = "Report processed successfully.";
    renderParsedValues(data.parsed_values);
  } catch (err) {
    console.error(err);
    DOM.uploadStatus.textContent = "Error processing report.";
  } finally {
    DOM.uploadBtn.disabled = false;
  }
}

async function handleQuestion(e) {
  e.preventDefault();
  const q = DOM.questionInput.value.trim();
  
  if (!q) return;

  addMessage("me", q);
  DOM.questionInput.value = "";
  DOM.askBtn.disabled = true;

  const formData = new FormData();
  formData.append("question", q);

  try {
    const res = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      body: formData,
    });
    
    if (!res.ok) throw new Error("Failed to get answer");
    
    const data = await res.json();
    addMessage("bot", data.answer, true);
    
    if (data.parsed_values) {
      renderParsedValues(data.parsed_values);
    }
  } catch (err) {
    console.error(err);
    addMessage("bot", "Sorry, something went wrong while answering your question.");
  } finally {
    DOM.askBtn.disabled = false;
  }
}

// Event Listeners
DOM.uploadForm.addEventListener("submit", handleUpload);
DOM.askForm.addEventListener("submit", handleQuestion);
DOM.stopBtn.addEventListener("click", stopTyping);

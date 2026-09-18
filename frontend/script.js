// frontend/script.js

const API_BASE = "http://127.0.0.1:8000";


// =====================================
// STATE
// =====================================

let typingTimeout = null;
let isTyping = false;


// =====================================
// DOM ELEMENTS
// =====================================

const DOM = {
  uploadForm: document.getElementById("upload-form"),

  reportFileInput: document.getElementById("report-file"),

  uploadZone: document.getElementById("upload-zone"),

  uploadStatus: document.getElementById("upload-status"),

  parsedValuesDiv: document.getElementById("parsed-values"),

  uploadBtn: document.getElementById("upload-btn"),

  uploadLoader: document.getElementById("upload-loader"),

  selectedFile: document.getElementById("selected-file"),

  selectedFileName: document.getElementById("selected-file-name"),

  selectedFileSize: document.getElementById("selected-file-size"),

  askForm: document.getElementById("ask-form"),

  questionInput: document.getElementById("question"),

  askBtn: document.getElementById("ask-btn"),

  chatDiv: document.getElementById("chat"),

  stopBtn: document.getElementById("stop-btn"),

  suggestionButtons: document.querySelectorAll(".suggestion-chip"),
};


// =====================================
// HELPER FUNCTIONS
// =====================================

function escapeHTML(text = "") {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


function formatText(text = "") {
  return escapeHTML(text)
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .join("<br>");
}


function scrollChatToBottom() {
  DOM.chatDiv.scrollTop = DOM.chatDiv.scrollHeight;
}


function formatFileSize(bytes) {
  if (!bytes) return "0 KB";

  const kb = bytes / 1024;

  if (kb < 1024) {
    return `${kb.toFixed(1)} KB`;
  }

  const mb = kb / 1024;

  return `${mb.toFixed(2)} MB`;
}


// =====================================
// STATUS MESSAGE
// =====================================

function setUploadStatus(message, type = "neutral") {
  DOM.uploadStatus.textContent = message;

  DOM.uploadStatus.classList.remove(
    "status-success",
    "status-error",
    "status-loading"
  );

  if (type === "success") {
    DOM.uploadStatus.classList.add("status-success");
  }

  if (type === "error") {
    DOM.uploadStatus.classList.add("status-error");
  }

  if (type === "loading") {
    DOM.uploadStatus.classList.add("status-loading");
  }
}


// =====================================
// MESSAGE CREATION
// =====================================

function addMessage(role, text, isStreaming = false) {
  const message = document.createElement("div");

  message.classList.add(
    "message",
    role === "me" ? "me" : "bot"
  );


  const bubble = document.createElement("span");

  message.appendChild(bubble);

  DOM.chatDiv.appendChild(message);

  scrollChatToBottom();


  if (isStreaming && role === "bot") {
    typeWriter(bubble, text);
  } else {
    bubble.innerHTML = formatText(text);
  }
}


// =====================================
// THINKING MESSAGE
// =====================================

function addThinkingMessage() {
  const message = document.createElement("div");

  message.classList.add(
    "message",
    "bot",
    "thinking-message"
  );


  const bubble = document.createElement("span");

  bubble.innerHTML = `
    <span class="typing-dots">
      <i></i>
      <i></i>
      <i></i>
    </span>
  `;

  message.appendChild(bubble);

  DOM.chatDiv.appendChild(message);

  scrollChatToBottom();

  return message;
}


// =====================================
// STOP TYPEWRITER
// =====================================

function stopTyping() {
  if (typingTimeout !== null) {
    clearTimeout(typingTimeout);

    typingTimeout = null;
  }

  isTyping = false;

  DOM.stopBtn.style.display = "none";
}


// =====================================
// TYPEWRITER EFFECT
// =====================================

function typeWriter(element, text, speed = 18) {
  stopTyping();

  let index = 0;

  let currentText = "";

  isTyping = true;

  DOM.stopBtn.style.display = "inline-flex";


  const typeNextCharacter = () => {
    if (!isTyping) {
      element.innerHTML = formatText(currentText);

      return;
    }


    if (index < text.length) {
      currentText += text[index];

      element.innerHTML =
        formatText(currentText) +
        '<span class="cursor">|</span>';

      index++;

      scrollChatToBottom();

      typingTimeout = setTimeout(
        typeNextCharacter,
        speed
      );

      return;
    }


    element.innerHTML = formatText(currentText);

    isTyping = false;

    typingTimeout = null;

    DOM.stopBtn.style.display = "none";

    scrollChatToBottom();
  };


  typeNextCharacter();
}


// =====================================
// PARSED VALUES
// =====================================

function renderParsedValues(parsed) {
  DOM.parsedValuesDiv.innerHTML = "";


  if (
    !parsed ||
    Object.keys(parsed).length === 0
  ) {
    DOM.parsedValuesDiv.innerHTML = `
      <p class="small">
        No structured values were detected.
        You can still ask questions about the report.
      </p>
    `;

    return;
  }


  const title = document.createElement("p");

  title.innerHTML = `
    <strong>Detected values</strong>
  `;

  DOM.parsedValuesDiv.appendChild(title);


  const list = document.createElement("ul");

  list.id = "parsed-list";


  Object.entries(parsed).forEach(
    ([testName, info]) => {
      const item = document.createElement("li");


      const name = document.createElement("span");

      name.textContent = testName;


      const value = document.createElement("strong");


      if (
        info &&
        typeof info === "object"
      ) {
        value.textContent =
          `${info.value ?? ""} ${info.unit ?? ""}`.trim();
      } else {
        value.textContent =
          String(info ?? "");
      }


      item.appendChild(name);

      item.appendChild(value);

      list.appendChild(item);
    }
  );


  DOM.parsedValuesDiv.appendChild(list);
}


// =====================================
// FILE PREVIEW
// =====================================

function showSelectedFile(file) {
  if (!file) {
    DOM.selectedFile.style.display = "none";

    return;
  }


  DOM.selectedFileName.textContent =
    file.name;


  DOM.selectedFileSize.textContent =
    formatFileSize(file.size);


  DOM.selectedFile.style.display = "flex";
}


// =====================================
// FILE VALIDATION
// =====================================

function validatePDF(file) {
  if (!file) {
    return {
      valid: false,
      message: "Please select a PDF file."
    };
  }


  const isPDF =
    file.type === "application/pdf" ||
    file.name
      .toLowerCase()
      .endsWith(".pdf");


  if (!isPDF) {
    return {
      valid: false,
      message: "Only PDF files are supported."
    };
  }


  const maxSize =
    10 * 1024 * 1024;


  if (file.size > maxSize) {
    return {
      valid: false,
      message:
        "The PDF is too large. Please upload a file smaller than 10 MB."
    };
  }


  return {
    valid: true
  };
}


// =====================================
// FILE INPUT CHANGE
// =====================================

function handleFileChange() {
  const file =
    DOM.reportFileInput.files[0];


  if (!file) {
    DOM.selectedFile.style.display = "none";

    return;
  }


  const validation =
    validatePDF(file);


  if (!validation.valid) {
    setUploadStatus(
      validation.message,
      "error"
    );

    DOM.reportFileInput.value = "";

    DOM.selectedFile.style.display = "none";

    return;
  }


  showSelectedFile(file);

  setUploadStatus(
    "PDF ready to analyze."
  );
}


// =====================================
// DRAG AND DROP
// =====================================

function handleDragOver(event) {
  event.preventDefault();

  DOM.uploadZone.classList.add(
    "drag-active"
  );
}


function handleDragLeave() {
  DOM.uploadZone.classList.remove(
    "drag-active"
  );
}


function handleDrop(event) {
  event.preventDefault();

  DOM.uploadZone.classList.remove(
    "drag-active"
  );


  const files =
    event.dataTransfer.files;


  if (!files || files.length === 0) {
    return;
  }


  const file =
    files[0];


  const validation =
    validatePDF(file);


  if (!validation.valid) {
    setUploadStatus(
      validation.message,
      "error"
    );

    return;
  }


  const dataTransfer =
    new DataTransfer();


  dataTransfer.items.add(file);


  DOM.reportFileInput.files =
    dataTransfer.files;


  showSelectedFile(file);


  setUploadStatus(
    "PDF ready to analyze."
  );
}


// =====================================
// UPLOAD BUTTON STATE
// =====================================

function setUploadLoading(isLoading) {
  DOM.uploadBtn.disabled =
    isLoading;


  if (DOM.uploadLoader) {
    DOM.uploadLoader.style.display =
      isLoading
        ? "inline-block"
        : "none";
  }


  const buttonText =
    DOM.uploadBtn.querySelector(
      ".btn-text"
    );


  if (buttonText) {
    buttonText.textContent =
      isLoading
        ? "Analyzing..."
        : "Analyze Report";
  }
}


// =====================================
// REPORT UPLOAD
// =====================================

async function handleUpload(event) {
  event.preventDefault();


  const file =
    DOM.reportFileInput.files[0];


  const validation =
    validatePDF(file);


  if (!validation.valid) {
    setUploadStatus(
      validation.message,
      "error"
    );

    return;
  }


  setUploadLoading(true);


  setUploadStatus(
    "Uploading and analyzing your report...",
    "loading"
  );


  const formData =
    new FormData();


  formData.append(
    "file",
    file
  );


  try {
    const response =
      await fetch(
        `${API_BASE}/upload_report`,
        {
          method: "POST",

          body: formData,
        }
      );


    if (!response.ok) {
      let message =
        "Unable to process the report.";


      try {
        const errorData =
          await response.json();


        if (errorData.detail) {
          message =
            errorData.detail;
        }
      } catch (_) {
        // Ignore JSON parse error
      }


      throw new Error(message);
    }


    const data =
      await response.json();


    setUploadStatus(
      "Report processed successfully. You can now ask questions.",
      "success"
    );


    renderParsedValues(
      data.parsed_values
    );


    DOM.questionInput.focus();
  } catch (error) {
    console.error(
      "Upload error:",
      error
    );


    setUploadStatus(
      error.message ||
      "Something went wrong while processing the report.",
      "error"
    );
  } finally {
    setUploadLoading(false);
  }
}


// =====================================
// QUESTION SUBMISSION
// =====================================

async function handleQuestion(event) {
  event.preventDefault();


  const question =
    DOM.questionInput.value.trim();


  if (!question) {
    DOM.questionInput.focus();

    return;
  }


  if (isTyping) {
    stopTyping();
  }


  addMessage(
    "me",
    question
  );


  DOM.questionInput.value = "";

  DOM.askBtn.disabled = true;


  const thinkingMessage =
    addThinkingMessage();


  const formData =
    new FormData();


  formData.append(
    "question",
    question
  );


  try {
    const response =
      await fetch(
        `${API_BASE}/ask`,
        {
          method: "POST",

          body: formData,
        }
      );


    if (!response.ok) {
      throw new Error(
        "Failed to get an answer."
      );
    }


    const data =
      await response.json();


    thinkingMessage.remove();


    const answer =
      data.answer ||
      "I couldn't generate an answer for that question.";


    addMessage(
      "bot",
      answer,
      true
    );


    if (data.parsed_values) {
      renderParsedValues(
        data.parsed_values
      );
    }
  } catch (error) {
    console.error(
      "Question error:",
      error
    );


    thinkingMessage.remove();


    addMessage(
      "bot",
      "I couldn't process that question right now. Please try again in a moment."
    );
  } finally {
    DOM.askBtn.disabled = false;

    DOM.questionInput.focus();
  }
}


// =====================================
// SUGGESTED QUESTIONS
// =====================================

function handleSuggestionClick(event) {
  const question =
    event.currentTarget.dataset.question;


  if (!question) {
    return;
  }


  DOM.questionInput.value =
    question;


  DOM.questionInput.focus();
}


// =====================================
// ENTER KEY UX
// =====================================

function handleQuestionKeydown(event) {
  if (
    event.key === "Enter" &&
    !event.shiftKey
  ) {
    event.preventDefault();

    DOM.askForm.requestSubmit();
  }
}


// =====================================
// EVENT LISTENERS
// =====================================

DOM.uploadForm.addEventListener(
  "submit",
  handleUpload
);


DOM.reportFileInput.addEventListener(
  "change",
  handleFileChange
);


DOM.askForm.addEventListener(
  "submit",
  handleQuestion
);


DOM.stopBtn.addEventListener(
  "click",
  stopTyping
);


DOM.questionInput.addEventListener(
  "keydown",
  handleQuestionKeydown
);


DOM.suggestionButtons.forEach(
  (button) => {
    button.addEventListener(
      "click",
      handleSuggestionClick
    );
  }
);


DOM.uploadZone.addEventListener(
  "dragover",
  handleDragOver
);


DOM.uploadZone.addEventListener(
  "dragleave",
  handleDragLeave
);


DOM.uploadZone.addEventListener(
  "drop",
  handleDrop
);
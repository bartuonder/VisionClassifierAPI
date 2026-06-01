const API = "";

const $ = (sel) => document.querySelector(sel);

const authSection = $("#auth-section");
const dashboardSection = $("#dashboard-section");
const userBar = $("#user-bar");
const userGreeting = $("#user-greeting");
const loginForm = $("#login-form");
const signupForm = $("#signup-form");
const authError = $("#auth-error");
const authSuccess = $("#auth-success");
const fileInput = $("#file-input");
const dropZone = $("#drop-zone");
const previewImg = $("#preview-img");
const uploadBtn = $("#upload-btn");
const uploadError = $("#upload-error");
const resultEmpty = $("#result-empty");
const resultContent = $("#result-content");
const taskStatus = $("#task-status");
const taskIdEl = $("#task-id");
const predictionBlock = $("#prediction-block");
const predictionLabel = $("#prediction-label");
const confidenceFill = $("#confidence-fill");
const confidenceValue = $("#confidence-value");

let selectedFile = null;
let pollTimer = null;

function getToken() {
  return localStorage.getItem("access_token");
}

function setToken(token) {
  localStorage.setItem("access_token", token);
}

function clearToken() {
  localStorage.removeItem("access_token");
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      ...authHeaders(),
      ...(options.headers || {}),
    },
  });

  if (res.status === 204) return null;

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data.detail;
    const message = typeof detail === "string"
      ? detail
      : Array.isArray(detail)
        ? detail.map((d) => d.msg).join(", ")
        : "Bir hata oluştu.";
    throw new Error(message);
  }
  return data;
}

function showAuthError(msg) {
  authError.textContent = msg;
  authError.classList.remove("hidden");
  authSuccess.classList.add("hidden");
}

function showAuthSuccess(msg) {
  authSuccess.textContent = msg;
  authSuccess.classList.remove("hidden");
  authError.classList.add("hidden");
}

function hideAuthAlerts() {
  authError.classList.add("hidden");
  authSuccess.classList.add("hidden");
}

function switchTab(tab) {
  document.querySelectorAll(".tab").forEach((t) => {
    t.classList.toggle("active", t.dataset.tab === tab);
  });
  loginForm.classList.toggle("hidden", tab !== "login");
  signupForm.classList.toggle("hidden", tab !== "signup");
  hideAuthAlerts();
}

async function showDashboard() {
  authSection.classList.add("hidden");
  dashboardSection.classList.remove("hidden");
  userBar.classList.remove("hidden");

  try {
    const user = await api("/user/me");
    userGreeting.textContent = user.username;
  } catch {
    logout();
  }
}

function showAuth() {
  authSection.classList.remove("hidden");
  dashboardSection.classList.add("hidden");
  userBar.classList.add("hidden");
  stopPolling();
  resetUpload();
}

function logout() {
  clearToken();
  showAuth();
}

function resetUpload() {
  selectedFile = null;
  fileInput.value = "";
  previewImg.classList.add("hidden");
  dropZone.querySelector(".drop-zone-inner").classList.remove("hidden");
  uploadBtn.disabled = true;
  uploadError.classList.add("hidden");
}

function resetResult() {
  resultEmpty.classList.remove("hidden");
  resultContent.classList.add("hidden");
  predictionBlock.classList.add("hidden");
}

function setResultPending(id) {
  resultEmpty.classList.add("hidden");
  resultContent.classList.remove("hidden");
  predictionBlock.classList.add("hidden");
  taskIdEl.textContent = id;
  setStatusBadge("pending");
}

function setStatusBadge(status) {
  taskStatus.textContent = status;
  taskStatus.className = `badge ${status}`;
}

function showPrediction(label, confidence) {
  predictionBlock.classList.remove("hidden");
  predictionLabel.textContent = label.replace(/_/g, " ");
  confidenceValue.textContent = confidence ?? 0;
  confidenceFill.style.width = `${Math.min(confidence ?? 0, 100)}%`;
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

async function pollTaskStatus(taskId) {
  try {
    const data = await api(`/classify/status/${taskId}`);
    setStatusBadge(data.status);

    if (data.status === "completed") {
      showPrediction(data.prediction, data.confidence);
      stopPolling();
      uploadBtn.disabled = false;
    } else if (data.status === "failed") {
      uploadError.textContent = "Sınıflandırma başarısız oldu.";
      uploadError.classList.remove("hidden");
      stopPolling();
      uploadBtn.disabled = false;
    }
  } catch (err) {
    uploadError.textContent = err.message;
    uploadError.classList.remove("hidden");
    stopPolling();
    uploadBtn.disabled = false;
  }
}

function startPolling(taskId) {
  stopPolling();
  pollTaskStatus(taskId);
  pollTimer = setInterval(() => pollTaskStatus(taskId), 2000);
}

async function handleFile(file) {
  if (!file || !file.type.startsWith("image/")) {
    uploadError.textContent = "Lütfen bir görüntü dosyası seçin.";
    uploadError.classList.remove("hidden");
    return;
  }

  selectedFile = file;
  uploadError.classList.add("hidden");

  const url = URL.createObjectURL(file);
  previewImg.src = url;
  previewImg.classList.remove("hidden");
  dropZone.querySelector(".drop-zone-inner").classList.add("hidden");
  uploadBtn.disabled = false;
}

// Tabs
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => switchTab(tab.dataset.tab));
});

// Login
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAuthAlerts();

  const form = new FormData(loginForm);
  const body = new URLSearchParams();
  body.append("username", form.get("username"));
  body.append("password", form.get("password"));

  try {
    const data = await api("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    setToken(data.access_token);
    await showDashboard();
  } catch (err) {
    showAuthError(err.message);
  }
});

// Signup
signupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideAuthAlerts();

  const form = new FormData(signupForm);
  const payload = {
    username: form.get("username"),
    email: form.get("email"),
    password: form.get("password"),
  };

  try {
    await api("/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    showAuthSuccess("Hesap oluşturuldu. Giriş yapabilirsiniz.");
    switchTab("login");
    loginForm.querySelector('[name="username"]').value = payload.username;
  } catch (err) {
    showAuthError(err.message);
  }
});

$("#logout-btn").addEventListener("click", logout);

// File upload UI
$("#browse-btn").addEventListener("click", (e) => {
  e.stopPropagation();
  fileInput.click();
});

dropZone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
});

uploadBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  uploadBtn.disabled = true;
  uploadError.classList.add("hidden");
  resetResult();

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const data = await api("/classify/", {
      method: "POST",
      body: formData,
    });
    setResultPending(data.task_id);
    startPolling(data.task_id);
  } catch (err) {
    uploadError.textContent = err.message;
    uploadError.classList.remove("hidden");
    uploadBtn.disabled = false;
  }
});

// Init
(async () => {
  if (getToken()) {
    try {
      await showDashboard();
    } catch {
      logout();
    }
  } else {
    showAuth();
  }
})();

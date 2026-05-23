const USERS_KEY = "fp_users";
const SESSION_KEY = "fp_session";

const authScreen = document.getElementById("auth-screen");
const appRoot = document.getElementById("app");
const loginForm = document.getElementById("login-form");
const usernameInput = document.getElementById("username");
const passwordInput = document.getElementById("password");
const authError = document.getElementById("auth-error");
const currentUserEl = document.getElementById("current-user");
const logoutBtn = document.getElementById("logout-btn");

// Hash non crittografico: serve solo a non salvare la password in chiaro.
// Questo è un login demo lato client e NON offre sicurezza reale.
function hashPassword(str) {
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return (h >>> 0).toString(16);
}

function loadUsers() {
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY)) || {};
  } catch {
    return {};
  }
}

function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function showError(msg) {
  authError.textContent = msg;
  authError.hidden = false;
}

function clearError() {
  authError.textContent = "";
  authError.hidden = true;
}

function showApp(username) {
  currentUserEl.textContent = username;
  authScreen.hidden = true;
  appRoot.hidden = false;
}

function showLogin() {
  appRoot.hidden = true;
  authScreen.hidden = false;
  loginForm.reset();
  clearError();
  usernameInput.focus();
}

function login(username, password) {
  const users = loadUsers();
  const hash = hashPassword(password);

  if (Object.prototype.hasOwnProperty.call(users, username)) {
    if (users[username] !== hash) {
      showError("Password errata.");
      return;
    }
  } else {
    users[username] = hash;
    saveUsers(users);
  }

  localStorage.setItem(SESSION_KEY, username);
  showApp(username);
}

function logout() {
  localStorage.removeItem(SESSION_KEY);
  document.dispatchEvent(new CustomEvent("fp:logout"));
  showLogin();
}

loginForm.addEventListener("submit", (e) => {
  e.preventDefault();
  clearError();
  const username = usernameInput.value.trim();
  const password = passwordInput.value;
  if (!username || !password) {
    showError("Inserisci nome utente e password.");
    return;
  }
  login(username, password);
});

logoutBtn.addEventListener("click", logout);

const savedSession = localStorage.getItem(SESSION_KEY);
if (savedSession) {
  showApp(savedSession);
} else {
  showLogin();
}

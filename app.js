const FURNITURE_SPECS = {
  "table-round":  { w: 100, h: 100, label: "Tavolo rotondo",     category: "table" },
  "table-rect":   { w: 160, h: 90,  label: "Tavolo rettangolare", category: "table" },
  "table-square": { w: 100, h: 100, label: "Tavolo quadrato",    category: "table" },
  "chair":        { w: 48,  h: 48,  label: "Sedia",              category: "seat"  },
  "armchair":     { w: 72,  h: 72,  label: "Poltrona",           category: "seat"  },
  "stool":        { w: 40,  h: 40,  label: "Sgabello",           category: "seat"  },
};

const room = document.getElementById("room");
const statTables = document.getElementById("stat-tables");
const statSeats = document.getElementById("stat-seats");
const statTotal = document.getElementById("stat-total");

let selected = null;
let nextId = 1;

document.querySelectorAll(".palette-item").forEach((item) => {
  item.addEventListener("dragstart", (e) => {
    e.dataTransfer.setData("text/plain", item.dataset.type);
    e.dataTransfer.effectAllowed = "copy";
  });
});

room.addEventListener("dragover", (e) => {
  e.preventDefault();
  e.dataTransfer.dropEffect = "copy";
  room.classList.add("drag-over");
});

room.addEventListener("dragleave", (e) => {
  if (e.target === room) room.classList.remove("drag-over");
});

room.addEventListener("drop", (e) => {
  e.preventDefault();
  room.classList.remove("drag-over");
  const type = e.dataTransfer.getData("text/plain");
  if (!FURNITURE_SPECS[type]) return;

  const rect = room.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  createFurniture(type, x, y);
});

function createFurniture(type, centerX, centerY) {
  const spec = FURNITURE_SPECS[type];
  const el = document.createElement("div");
  el.className = `furniture ${type}`;
  el.dataset.type = type;
  el.dataset.id = String(nextId++);
  el.dataset.rotation = "0";
  el.style.width = `${spec.w}px`;
  el.style.height = `${spec.h}px`;
  el.title = spec.label;

  const x = Math.max(0, centerX - spec.w / 2);
  const y = Math.max(0, centerY - spec.h / 2);
  placeAt(el, x, y);

  el.addEventListener("mousedown", startDrag);
  el.addEventListener("click", (e) => {
    e.stopPropagation();
    selectItem(el);
  });

  room.appendChild(el);
  selectItem(el);
  updateStats();
}

room.addEventListener("click", (e) => {
  if (e.target === room || e.target.classList.contains("room-grid")) {
    selectItem(null);
  }
});

function selectItem(el) {
  if (selected) selected.classList.remove("selected");
  selected = el;
  if (selected) selected.classList.add("selected");
}

function placeAt(el, x, y) {
  const roomRect = room.getBoundingClientRect();
  const w = parseFloat(el.style.width);
  const h = parseFloat(el.style.height);
  const clampedX = Math.max(0, Math.min(roomRect.width - w, x));
  const clampedY = Math.max(0, Math.min(roomRect.height - h, y));
  el.style.left = `${clampedX}px`;
  el.style.top = `${clampedY}px`;
}

function startDrag(e) {
  if (e.button !== 0) return;
  const el = e.currentTarget;
  selectItem(el);

  const startX = e.clientX;
  const startY = e.clientY;
  const origLeft = parseFloat(el.style.left);
  const origTop = parseFloat(el.style.top);

  function onMove(ev) {
    placeAt(el, origLeft + (ev.clientX - startX), origTop + (ev.clientY - startY));
  }
  function onUp() {
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("mouseup", onUp);
  }
  document.addEventListener("mousemove", onMove);
  document.addEventListener("mouseup", onUp);
  e.preventDefault();
}

function rotateSelected() {
  if (!selected) return;
  const current = parseInt(selected.dataset.rotation, 10) || 0;
  const next = (current + 90) % 360;
  selected.dataset.rotation = String(next);
  selected.style.transform = `rotate(${next}deg)`;
}

function deleteSelected() {
  if (!selected) return;
  selected.remove();
  selected = null;
  updateStats();
}

function clearRoom() {
  if (!room.querySelector(".furniture")) return;
  if (!confirm("Svuotare la stanza?")) return;
  room.querySelectorAll(".furniture").forEach((el) => el.remove());
  selected = null;
  updateStats();
}

function updateStats() {
  const items = room.querySelectorAll(".furniture");
  let tables = 0, seats = 0;
  items.forEach((el) => {
    const cat = FURNITURE_SPECS[el.dataset.type]?.category;
    if (cat === "table") tables++;
    else if (cat === "seat") seats++;
  });
  statTables.textContent = String(tables);
  statSeats.textContent = String(seats);
  statTotal.textContent = String(items.length);
  room.classList.toggle("has-items", items.length > 0);
}

document.getElementById("rotate-btn").addEventListener("click", rotateSelected);
document.getElementById("delete-btn").addEventListener("click", deleteSelected);
document.getElementById("clear-btn").addEventListener("click", clearRoom);

document.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
  if (e.key === "r" || e.key === "R") rotateSelected();
  if (e.key === "Delete" || e.key === "Backspace") {
    if (selected) {
      e.preventDefault();
      deleteSelected();
    }
  }
});

updateStats();

/* ---------- Note vocali (stile Plaud) ---------- */
const recordBtn = document.getElementById("record-btn");
const recStatus = document.getElementById("rec-status");
const liveTranscript = document.getElementById("live-transcript");
const noteList = document.getElementById("note-list");
const clearNotesBtn = document.getElementById("clear-notes-btn");

const NOTES_KEY = "arredamento.voiceNotes";
const RECOGNITION_LANG = "zh-CN";
const SpeechRecognitionImpl =
  window.SpeechRecognition || window.webkitSpeechRecognition || null;

const sessionAudio = {}; // id nota -> object URL (solo sessione corrente)

let mediaRecorder = null;
let audioChunks = [];
let recognition = null;
let recording = false;
let finalText = "";
let interimText = "";
let recTimer = null;
let recStartedAt = 0;

function loadNotes() {
  try {
    return JSON.parse(localStorage.getItem(NOTES_KEY)) || [];
  } catch {
    return [];
  }
}

function saveNotes(notes) {
  try {
    localStorage.setItem(NOTES_KEY, JSON.stringify(notes));
  } catch {
    /* storage non disponibile o pieno: ignora */
  }
}

function formatTime(iso) {
  return new Date(iso).toLocaleString("it-IT", {
    dateStyle: "short",
    timeStyle: "short",
  });
}

function currentStats() {
  return {
    tables: statTables.textContent,
    seats: statSeats.textContent,
    total: statTotal.textContent,
  };
}

function renderNotes() {
  const notes = loadNotes();
  noteList.innerHTML = "";

  if (notes.length === 0) {
    const li = document.createElement("li");
    li.className = "note-empty";
    li.textContent = "Nessuna nota. Premi Registra per iniziare.";
    noteList.appendChild(li);
    clearNotesBtn.disabled = true;
    return;
  }

  clearNotesBtn.disabled = false;
  notes
    .slice()
    .reverse()
    .forEach((note) => {
      const li = document.createElement("li");
      li.className = "note";

      const meta = document.createElement("div");
      meta.className = "note-meta";
      meta.textContent = `${formatTime(note.time)} · Tavoli ${note.stats.tables}, Sedute ${note.stats.seats}`;
      li.appendChild(meta);

      const text = document.createElement("p");
      text.className = "note-text";
      text.textContent = note.text || "(nessuna trascrizione)";
      li.appendChild(text);

      const url = sessionAudio[note.id];
      if (url) {
        const audio = document.createElement("audio");
        audio.controls = true;
        audio.src = url;
        li.appendChild(audio);
      }

      const del = document.createElement("button");
      del.type = "button";
      del.className = "note-del";
      del.textContent = "Elimina";
      del.addEventListener("click", () => {
        if (sessionAudio[note.id]) {
          URL.revokeObjectURL(sessionAudio[note.id]);
          delete sessionAudio[note.id];
        }
        saveNotes(loadNotes().filter((n) => n.id !== note.id));
        renderNotes();
      });
      li.appendChild(del);

      noteList.appendChild(li);
    });
}

function updateRecTimer() {
  const secs = Math.floor((Date.now() - recStartedAt) / 1000);
  const mm = String(Math.floor(secs / 60)).padStart(2, "0");
  const ss = String(secs % 60).padStart(2, "0");
  recStatus.textContent = `Registrazione ${mm}:${ss}`;
}

function startRecognition() {
  if (!SpeechRecognitionImpl) {
    liveTranscript.textContent = "(Trascrizione non supportata da questo browser)";
    return;
  }
  recognition = new SpeechRecognitionImpl();
  recognition.lang = RECOGNITION_LANG;
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.addEventListener("result", (e) => {
    interimText = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const r = e.results[i];
      if (r.isFinal) finalText += r[0].transcript;
      else interimText += r[0].transcript;
    }
    liveTranscript.textContent = finalText + interimText;
  });

  recognition.addEventListener("end", () => {
    if (recording) {
      try {
        recognition.start();
      } catch {
        /* riavvio non riuscito: la registrazione audio continua */
      }
    }
  });

  try {
    recognition.start();
  } catch {
    /* avvio non riuscito: la registrazione audio continua comunque */
  }
}

async function startRecording() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    recStatus.textContent = "Registrazione non supportata";
    return;
  }

  finalText = "";
  interimText = "";
  audioChunks = [];
  liveTranscript.textContent = "";

  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  } catch {
    recStatus.textContent = "Microfono non disponibile";
    return;
  }

  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.addEventListener("dataavailable", (e) => {
    if (e.data.size > 0) audioChunks.push(e.data);
  });
  mediaRecorder.addEventListener("stop", () => {
    stream.getTracks().forEach((t) => t.stop());
    finalizeNote();
  });
  mediaRecorder.start();

  startRecognition();

  recording = true;
  recStartedAt = Date.now();
  recordBtn.classList.add("recording");
  recordBtn.textContent = "■ Stop";
  updateRecTimer();
  recTimer = setInterval(updateRecTimer, 500);
}

function stopRecording() {
  recording = false;
  clearInterval(recTimer);
  recTimer = null;

  if (recognition) {
    try {
      recognition.stop();
    } catch {
      /* ignora */
    }
  }

  recordBtn.classList.remove("recording");
  recordBtn.textContent = "● Registra";

  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop(); // l'evento 'stop' chiama finalizeNote()
  } else {
    finalizeNote();
  }
}

function finalizeNote() {
  const text = (finalText + interimText).trim();
  const note = {
    id: `n${Date.now()}`,
    time: new Date().toISOString(),
    text,
    stats: currentStats(),
  };

  if (audioChunks.length > 0) {
    const blob = new Blob(audioChunks, {
      type: mediaRecorder?.mimeType || "audio/webm",
    });
    sessionAudio[note.id] = URL.createObjectURL(blob);
  }

  const notes = loadNotes();
  notes.push(note);
  saveNotes(notes);

  finalText = "";
  interimText = "";
  liveTranscript.textContent = "";
  recStatus.textContent = "Salvata";
  renderNotes();
}

recordBtn.addEventListener("click", () => {
  if (recording) stopRecording();
  else startRecording();
});

clearNotesBtn.addEventListener("click", () => {
  if (!confirm("Eliminare tutte le note vocali?")) return;
  Object.values(sessionAudio).forEach((u) => URL.revokeObjectURL(u));
  for (const k in sessionAudio) delete sessionAudio[k];
  saveNotes([]);
  renderNotes();
});

if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
  recordBtn.disabled = true;
  recStatus.textContent = "Registrazione non supportata";
}

renderNotes();

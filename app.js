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

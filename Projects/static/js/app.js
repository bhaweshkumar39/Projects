// Browser side: receives note events from Flask and plays them with the Web Audio API.
const $ = (id) => document.getElementById(id);
let ctx = null;
const buffers = {};
let lastId = -1;

async function loadSounds() {
  const keys = await (await fetch("/api/keys")).json();
  await Promise.all(keys.map(async (k) => {
    const data = await (await fetch("/static/sounds/" + k.file)).arrayBuffer();
    buffers[k.name] = await ctx.decodeAudioData(data);
  }));
}

function play(name) {
  const buf = buffers[name];
  if (!buf) return;
  const src = ctx.createBufferSource();   // a new source per note => notes can overlap
  src.buffer = buf;
  const gain = ctx.createGain();
  gain.gain.value = 0.9;
  src.connect(gain).connect(ctx.destination);
  src.start();
}

async function pollNotes() {
  try {
    const res = await fetch("/api/notes?since=" + lastId);
    const data = await res.json();
    lastId = data.last_id;
    data.events.forEach((e) => { play(e.note); $("lastNote").textContent = e.note; });
  } catch (err) { /* server busy, try again */ }
  setTimeout(pollNotes, 40);
}

async function pollStatus() {
  try {
    const s = await (await fetch("/api/status")).json();
    $("fps").textContent = s.fps;
    $("msg").textContent = s.camera_ok ? "" : "⚠ Camera not available";
  } catch (err) {}
  setTimeout(pollStatus, 1000);
}

function sendConfig() {
  fetch("/api/config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      tips: $("tips").value,
      cooldown: parseFloat($("cooldown").value),
      landmarks: $("landmarks").checked,
    }),
  });
}

$("startBtn").addEventListener("click", async () => {
  $("startBtn").disabled = true;
  $("startBtn").textContent = "Loading sounds...";
  ctx = new (window.AudioContext || window.webkitAudioContext)();
  await ctx.resume();                     // browsers require a click to unlock audio
  await loadSounds();
  $("startBtn").textContent = "🔊 Sound on";
  pollNotes();
});

$("tips").addEventListener("change", sendConfig);
$("landmarks").addEventListener("change", sendConfig);
$("cooldown").addEventListener("input", () => {
  $("cdVal").textContent = parseFloat($("cooldown").value).toFixed(2);
  sendConfig();
});

pollStatus();

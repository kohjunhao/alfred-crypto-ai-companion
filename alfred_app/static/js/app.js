const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message");
const chatLog = document.getElementById("chat-log");
const engineIndicator = document.getElementById("engine-indicator");
const snapshotRoot = document.getElementById("data-snapshot");
const warningBox = document.getElementById("warning-box");
const warningShell = document.getElementById("warning-shell");
const healthMode = document.getElementById("health-mode");
const healthOllama = document.getElementById("health-ollama");
const healthModel = document.getElementById("health-model");
const modeButtons = [...document.querySelectorAll(".mode-button")];
const promptButtons = [...document.querySelectorAll(".prompt-tab")];
const revealNodes = [...document.querySelectorAll("[data-reveal]")];

let activeMode = "SIMPLE";

function setMode(mode) {
  activeMode = mode;
  modeButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.mode === mode);
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function renderInline(text) {
  return escapeHtml(text).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}

function renderMarkdownLite(text) {
  const lines = text.split("\n").filter((line) => line.trim().length > 0);
  const tableLines = lines.filter((line) => line.trim().startsWith("|"));

  if (tableLines.length >= 2) {
    const tableRows = tableLines
      .filter((line) => !line.includes(":---"))
      .map((line) =>
        line
          .split("|")
          .map((cell) => cell.trim())
          .filter(Boolean)
      );

    if (tableRows.length >= 2) {
      const [header, ...body] = tableRows;
      const table = `
        <table>
          <thead>
            <tr>${header.map((cell) => `<th>${renderInline(cell)}</th>`).join("")}</tr>
          </thead>
          <tbody>
            ${body
              .map(
                (row) =>
                  `<tr>${row.map((cell) => `<td>${renderInline(cell)}</td>`).join("")}</tr>`
              )
              .join("")}
          </tbody>
        </table>
      `;

      const nonTableLines = lines.filter((line) => !line.trim().startsWith("|"));
      const paragraphs = nonTableLines
        .map((line) => `<p>${renderInline(line)}</p>`)
        .join("");
      return `${table}${paragraphs}`;
    }
  }

  return lines.map((line) => `<p>${renderInline(line)}</p>`).join("");
}

function addMessage(role, text) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  article.innerHTML = `
    <span class="message-role">${role === "assistant" ? "ALFRED" : "USER"}</span>
    <div class="message-body">${renderMarkdownLite(text)}</div>
  `;
  chatLog.appendChild(article);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function renderMetrics(metrics) {
  if (!metrics) {
    snapshotRoot.className = "inspector-empty";
    snapshotRoot.textContent = "No live asset data has been retrieved yet.";
    return;
  }

  const cards = [
    ["Asset", metrics.resolved_name],
    ["Symbol", metrics.symbol],
    ["Price", metrics.formatted.price_usd],
    ["24h Change", metrics.formatted.change_24h],
    ["Market Cap", metrics.formatted.market_cap],
    ["24h Volume", metrics.formatted.volume_24h],
    ["FDV", metrics.formatted.fdv],
    ["TVL", metrics.formatted.tvl_usd],
    ["Sources", metrics.sources.join(", ") || "N/A"],
    ["Retrieved", metrics.retrieved_at],
  ];

  snapshotRoot.className = "ledger-grid";
  snapshotRoot.innerHTML = cards
    .map(
      ([label, value]) => `
        <div class="metric-row">
          <span class="meta-label">${label}</span>
          <span class="meta-value">${escapeHtml(String(value))}</span>
        </div>
      `
    )
    .join("");
}

function renderWarnings(warnings) {
  if (!warnings || warnings.length === 0) {
    warningShell.classList.add("hidden");
    warningBox.innerHTML = "";
    return;
  }

  warningShell.classList.remove("hidden");
  warningBox.innerHTML = warnings.map((warning) => `<div>${escapeHtml(warning)}</div>`).join("");
}

async function loadHealth() {
  try {
    const response = await fetch("/api/health");
    const payload = await response.json();
    healthMode.textContent = payload.mode === "ollama-or-fallback" ? "OLLAMA + FALLBACK" : "FALLBACK ONLY";
    healthOllama.textContent = payload.ollama_ready ? "READY" : "NOT READY";
    healthModel.textContent = payload.ollama_model || "N/A";
  } catch (error) {
    healthMode.textContent = "UNAVAILABLE";
    healthOllama.textContent = "UNAVAILABLE";
    healthModel.textContent = "UNAVAILABLE";
  }
}

async function sendMessage(message) {
  addMessage("user", message);
  addMessage("assistant", "Routing the request, checking live data, and preparing the final answer.");

  const loadingMessage = chatLog.lastElementChild;

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, mode: activeMode }),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Request failed.");
    }

    loadingMessage.remove();
    addMessage("assistant", payload.reply);
    const reasonLabel = payload.reason ? payload.reason.replaceAll("_", " ").toUpperCase() : "";
    const reasonText = reasonLabel ? ` · ${reasonLabel}` : "";
    engineIndicator.textContent = `${payload.engine.toUpperCase()} · ${payload.model}${reasonText}`;
    renderMetrics(payload.metrics);
    renderWarnings(payload.warnings);
  } catch (error) {
    loadingMessage.remove();
    addMessage("assistant", `Alfred hit an error: ${error.message}`);
    engineIndicator.textContent = "ERROR";
  }
}

modeButtons.forEach((button) => {
  button.addEventListener("click", () => setMode(button.dataset.mode));
});

promptButtons.forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.prompt;
    messageInput.focus();
  });
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) {
    return;
  }

  messageInput.value = "";
  await sendMessage(message);
});

messageInput.addEventListener("keydown", async (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.18 }
);

revealNodes.forEach((node) => observer.observe(node));
loadHealth();

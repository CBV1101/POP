const SOURCE_LABEL = {
  interview: "Interview",
  support: "Support",
  sales: "Sales",
  feature_request: "Feature request",
  review: "Review",
  slack: "Customer success",
  other: "Other",
};

function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

const COPY = {
  feedback: {
    bar: "Opportunities",
    kicker: "Workspace 02",
    headline: "Ranked opportunities",
    lede: "It turns messy feedback into ranked opportunities, and it keeps every claim tied to source quotes instead of collapsing them into a summary.",
    source: "Quotes, tickets, interviews",
    placeholder: "One quote per line. Mix interviews, tickets, reviews, and notes.",
    run: "Rank opportunities",
    empty: "Add source material first, or load the sample.",
    none: "Need a bit more feedback — we look for repeating problems, not one-off comments.",
  },
  requests: {
    bar: "Primitives",
    kicker: "Workspace 01",
    headline: "Smallest primitive",
    lede: "It finds the primitive among customer asks: the smallest build that can satisfy the whole pile, instead of shipping each requested feature.",
    source: "Feature and build requests",
    placeholder: "Can you add Terraform?\nWe need a setup wizard.\nPlease publish a permission catalog.",
    run: "Find the smallest build",
    empty: "Import a backlog or add requests first.",
    none: "Need a few related requests to find a shared primitive.",
  },
  priority: {
    bar: "Priorities",
    kicker: "Workspace 03",
    headline: "What to build first",
    lede: "Set how loaded you are, then say how much of the team each item takes. Must-dos and high-priority items start first; leftover team capacity fills with shorter items that can finish in parallel.",
    source: "Backlog items",
    placeholder: "",
    run: "Rank the backlog",
    empty: "Add backlog items first, or load the sample.",
    none: "Need at least one named backlog item to rank.",
  },
};

const state = {
  mode: "feedback",
  view: "chooser",
  result: null,
  selectedId: null,
  kindFilter: "all",
  showAll: false,
};

const els = {
  start: document.getElementById("start"),
  results: document.getElementById("results"),
  list: document.getElementById("list"),
  story: document.getElementById("story"),
  draft: document.getElementById("draft"),
  sample: document.getElementById("sample"),
  back: document.getElementById("back"),
  run: document.getElementById("run"),
  error: document.getElementById("error"),
  home: document.getElementById("home"),
  record: document.getElementById("record"),
  stop: document.getElementById("stop"),
  listen: document.getElementById("listen"),
  listenStatus: document.getElementById("listen-status"),
  interim: document.getElementById("interim"),
  kicker: document.getElementById("kicker"),
  headline: document.getElementById("headline"),
  lede: document.getElementById("lede"),
  chooser: document.getElementById("chooser"),
  barTitle: document.getElementById("bar-title"),
  sourceLabel: document.getElementById("source-label"),
  connect: document.getElementById("connect"),
  provider: document.getElementById("provider"),
  token: document.getElementById("token"),
  scope: document.getElementById("scope"),
  scopeLabel: document.getElementById("scope-label"),
  fieldHost: document.getElementById("field-host"),
  fieldEmail: document.getElementById("field-email"),
  fieldScope: document.getElementById("field-scope"),
  jiraHost: document.getElementById("jira-host"),
  jiraEmail: document.getElementById("jira-email"),
  importBtn: document.getElementById("import"),
  connectHint: document.getElementById("connect-hint"),
  source: document.getElementById("source"),
  priorityPanel: document.getElementById("priority-panel"),
  boardBody: document.getElementById("board-body"),
  addRow: document.getElementById("add-row"),
  capacity: document.getElementById("capacity"),
  define: document.getElementById("define"),
  defineToggle: document.getElementById("define-toggle"),
  defineBody: document.getElementById("define-body"),
  definePick: document.getElementById("define-pick"),
  defineText: document.getElementById("define-text"),
  defineCurrent: document.getElementById("define-current"),
};

const recorder = {
  active: false,
  recognition: null,
  startedAt: 0,
  timer: null,
  headerWritten: false,
};

function showError(message) {
  els.error.hidden = !message;
  els.error.textContent = message || "";
}

const LEVELS = ["none", "low", "medium", "high"];
const IMPACTS = [
  [0.25, "min"],
  [0.5, "low"],
  [1, "med"],
  [2, "high"],
  [3, "mass"],
];
const IMPACT_LABEL = Object.fromEntries(IMPACTS.map(([v, label]) => [String(v), label]));
const KINDS = [
  ["feature", "Feature"],
  ["ktlo", "Lights on"],
  ["security", "Security patch"],
  ["reliability", "Reliability"],
  ["compliance", "Legal / compliance"],
];

function emptyItem(partial = {}) {
  return {
    id: "",
    title: "",
    reach: "",
    impact: 1,
    confidence: 50,
    effort: 5,
    revenue: "",
    roi: "",
    deal: "none",
    dealValue: "",
    churn: "none",
    churnArr: "",
    debtAdded: "none",
    debtReduced: "none",
    blocksOthers: false,
    compliance: false,
    timeSensitive: false,
    blockedBy: false,
    workType: "feature",
    loadPct: 20,
    ...partial,
  };
}

function selectHtml(name, value, options) {
  return `<select data-f="${name}">${options
    .map(([v, label]) => `<option value="${v}" ${String(v) === String(value) ? "selected" : ""}>${label}</option>`)
    .join("")}</select>`;
}

function levelSelect(name, value) {
  return selectHtml(
    name,
    value || "none",
    LEVELS.map((l) => [l, l[0].toUpperCase() + l.slice(1)]),
  );
}

function rowHtml(item) {
  const i = emptyItem(item);
  const num = (name, value, extra = "") =>
    `<input data-f="${name}" type="number" min="0" ${extra} value="${value === "" || value == null ? "" : value}" />`;
  const check = (name, on) => `<input data-f="${name}" type="checkbox" ${on ? "checked" : ""} />`;
  return `<tr data-id="${escapeHtml(i.id)}">
    <td class="title-cell"><input data-f="title" type="text" value="${escapeHtml(i.title)}" placeholder="What to build" /></td>
    <td>${selectHtml("workType", i.workType, KINDS)}</td>
    <td>${num("reach", i.reach)}</td>
    <td>${selectHtml("impact", i.impact, IMPACTS)}</td>
    <td>${num("confidence", i.confidence, 'max="100"')}</td>
    <td>${num("effort", i.effort, 'step="0.25" min="0.25"')}</td>
    <td>${num("loadPct", i.loadPct, 'max="100"')}</td>
    <td>${num("revenue", i.revenue)}</td>
    <td>${num("roi", i.roi, 'step="0.1"')}</td>
    <td>${selectHtml("deal", i.deal, [
      ["none", "None"],
      ["signup", "Signs up if built"],
      ["expansion", "Expands if built"],
    ])}</td>
    <td>${num("dealValue", i.dealValue)}</td>
    <td>${levelSelect("churn", i.churn)}</td>
    <td>${num("churnArr", i.churnArr)}</td>
    <td>${levelSelect("debtAdded", i.debtAdded)}</td>
    <td>${levelSelect("debtReduced", i.debtReduced)}</td>
    <td>${check("blocksOthers", i.blocksOthers)}</td>
    <td>${check("compliance", i.compliance)}</td>
    <td>${check("timeSensitive", i.timeSensitive)}</td>
    <td>${check("blockedBy", i.blockedBy)}</td>
  </tr>`;
}

function fieldValue(el) {
  if (el.type === "checkbox") return el.checked;
  return el.value;
}

function collectBoard() {
  return [...els.boardBody.querySelectorAll("tr")].map((tr, index) => {
    const row = { id: tr.dataset.id || `BL-${String(index + 1).padStart(2, "0")}` };
    tr.querySelectorAll("[data-f]").forEach((el) => {
      row[el.dataset.f] = fieldValue(el);
    });
    return row;
  });
}

function fillBoard(items) {
  const rows = items && items.length ? items : [emptyItem()];
  els.boardBody.innerHTML = rows.map(rowHtml).join("");
}

function money(n) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(n || 0);
}

function daysLabel(n) {
  const value = Number(n);
  return `${value === 1 ? "1 day" : `${value} days`} of work`;
}

function priorityContext() {
  return {
    capacity: els.capacity.value,
  };
}

const DEFINITIONS = {
  capacity: {
    label: "Capacity (%)",
    text: "How loaded the team already is. 50% means half the team is busy and half is free. Free team is what new work can use, including items that run at the same time.",
  },
  title: {
    label: "Backlog item",
    text: "The name of the work. What you would put on a ticket: the feature, patch, or keep-the-lights-on job you are scoring.",
  },
  workType: {
    label: "Kind",
    text: "What kind of work this is. Feature competes on score. Lights on, security patch, reliability, and legal/compliance are must-dos — they start before ordinary features.",
  },
  reach: {
    label: "Reach",
    text: "How many people this will affect in a given period — customers, users, or accounts. Higher reach raises the RICE score.",
  },
  impact: {
    label: "Impact",
    text: "How much it helps each person reached. min is a tiny improvement, low is slight, med is noticeable, high is a clear win, mass is a game-changer for those users.",
  },
  confidence: {
    label: "Conf. %",
    text: "How sure you are about reach, impact, and effort. 100% means the numbers are solid. 50% means you are guessing — RICE treats the idea as half as strong.",
  },
  effort: {
    label: "Effort days",
    text: "How many days this item takes to finish. Used in RICE (more days = lower score) and for parallel work: a side item can only run with a main item if it finishes no later.",
  },
  loadPct: {
    label: "Takes %",
    text: "How much of the team this item uses while it is in progress. A 40% item and a 10% item can run together if 50% of the team is free, as long as the 10% item is not slower than the 40% item.",
  },
  revenue: {
    label: "Revenue $",
    text: "Expected revenue this item unlocks — new sales, expansion, or usage. Compared against effort when ranking.",
  },
  roi: {
    label: "ROI ×",
    text: "Return on investment as a multiple. 3× means you expect about three dollars back for each dollar of effort. Higher is better.",
  },
  deal: {
    label: "Deal",
    text: "Go/no-go: whether a customer signs up or expands only if this ships. None means no deal is tied to the item.",
  },
  dealValue: {
    label: "Deal $",
    text: "Dollar value of that go/no-go deal. Used only when Deal is signup or expansion.",
  },
  churn: {
    label: "Churn if skipped",
    text: "How likely customers are to leave if you do not build this. None, low, medium, or high. Pairs with ARR at risk.",
  },
  churnArr: {
    label: "ARR at risk $",
    text: "Annual recurring revenue you could lose if this is skipped. A high churn flag with large ARR at risk pulls the item up the list.",
  },
  debtAdded: {
    label: "Debt added",
    text: "How much technical debt this work creates — shortcuts, extra complexity, or cleanup later. More debt added hurts the rank.",
  },
  debtReduced: {
    label: "Debt reduced",
    text: "How much existing technical debt this work pays down. Reducing debt helps the rank.",
  },
  blocksOthers: {
    label: "Blocks others",
    text: "Check this if other work cannot start until this ships. That makes it more urgent.",
  },
  compliance: {
    label: "Compliance",
    text: "Check this if the item is needed for a legal, security, or audit requirement, even when Kind is not Legal/compliance.",
  },
  timeSensitive: {
    label: "Time-sensitive",
    text: "Check this if there is a real deadline — a launch window, contract date, or seasonal moment that will pass.",
  },
  blockedBy: {
    label: "Blocked by other work",
    text: "Check this if this item cannot start until something else is done. That lowers urgency so you do not pretend it can ship now.",
  },
  provider: {
    label: "Platform",
    text: "Where to import open backlog items from: Linear, GitHub Issues, or Jira.",
  },
  token: {
    label: "Token",
    text: "A personal API key for that platform. Used once for this import and not saved on the server.",
  },
  scope: {
    label: "Repo / JQL",
    text: "GitHub: owner/repo. Jira: optional JQL to filter issues. Linear does not need this.",
  },
  jiraHost: {
    label: "Jira site",
    text: "Your Jira cloud host, like your-team.atlassian.net.",
  },
  jiraEmail: {
    label: "Jira email",
    text: "The Atlassian account email that owns the API token.",
  },
  draft: {
    label: "Source material",
    text: "Paste interviews, tickets, or feature asks — usually one thought per line. Opportunities clusters this into ranked problems. Primitives looks for the smallest shared build.",
  },
};

function setGlossaryOpen(open) {
  els.defineBody.hidden = !open;
  els.defineToggle.setAttribute("aria-expanded", open ? "true" : "false");
  document.querySelector(".app").classList.toggle("glossary-open", open);
}

function showDefinition(key, open = true) {
  const def = DEFINITIONS[key];
  if (!def) return;
  els.definePick.value = key;
  els.defineCurrent.textContent = def.label;
  els.defineText.textContent = def.text;
  if (open) setGlossaryOpen(true);
}

function definitionKey(el) {
  if (!el || !el.getAttribute) return "";
  return el.dataset.define || el.dataset.f || "";
}

function fillDefinitionPick() {
  els.definePick.innerHTML = Object.entries(DEFINITIONS)
    .map(([key, def]) => `<option value="${key}">${def.label}</option>`)
    .join("");
}

function applyMode() {
  const copy = COPY[state.mode];
  els.kicker.textContent = copy.kicker;
  els.headline.textContent = copy.headline;
  els.lede.textContent = copy.lede;
  els.draft.placeholder = copy.placeholder;
  els.run.textContent = copy.run;
  els.sourceLabel.textContent = copy.source;
  els.barTitle.textContent = state.view === "chooser" ? "Choose a workspace" : copy.bar;
  els.start.classList.toggle("is-wide", state.mode === "priority");
  const ingest = state.view === "ingest" && !state.result;
  els.connect.hidden = !((state.mode === "requests" || state.mode === "priority") && ingest);
  els.priorityPanel.hidden = !(state.mode === "priority" && ingest);
  els.source.hidden = state.mode === "priority" || !ingest;
  els.record.hidden = state.mode === "priority" || recorder.active;
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.toggle("on", state.view !== "chooser" && btn.dataset.mode === state.mode);
  });
}

function showView() {
  const has = Boolean(state.result);
  els.chooser.hidden = has || state.view !== "chooser";
  els.start.hidden = has || state.view !== "ingest";
  els.results.hidden = !has;
  els.back.hidden = state.view === "chooser" && !has;
  applyMode();
}

function openWorkspace(mode) {
  stopListening();
  if (state.mode !== mode) els.draft.value = "";
  state.mode = mode;
  state.view = "ingest";
  state.result = null;
  showError("");
  if (mode === "priority" && !els.boardBody.children.length) {
    els.boardBody.innerHTML = [emptyItem(), emptyItem(), emptyItem()].map(rowHtml).join("");
  }
  showView();
}

async function analyze(payload) {
  const copy = COPY[state.mode];
  showError("");
  els.run.disabled = true;
  els.run.textContent = "Working…";
  const endpoint =
    state.mode === "requests" ? "/api/primitive" : state.mode === "priority" ? "/api/prioritize" : "/api/analyze";
  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    if (state.mode === "requests") {
      if (!data.primitives || data.primitives.length === 0) {
        showError(copy.none);
        return;
      }
      state.result = data;
      state.selectedId = data.primitives[0].id;
    } else if (state.mode === "priority") {
      if (!data.items || data.items.length === 0) {
        showError(copy.none);
        return;
      }
      state.result = data;
      state.selectedId = data.items[0].id;
    } else {
      if (!data.opportunities || data.opportunities.length === 0) {
        showError(copy.none);
        return;
      }
      state.result = data;
      state.selectedId = data.opportunities[0].id;
    }
    state.kindFilter = "all";
    state.showAll = false;
    render();
  } catch (err) {
    showError(err.message || "Couldn’t analyze that. Check the format and try again.");
  } finally {
    els.run.disabled = false;
    els.run.textContent = copy.run;
  }
}

function render() {
  showView();
  if (!state.result) return;
  els.results.classList.toggle("is-plan", state.result.kind === "priority");
  if (state.result.kind === "primitives") {
    renderPrimitives();
    return;
  }
  if (state.result.kind === "priority") {
    renderPriority();
    return;
  }
  renderOpportunities();
}

function bindList(items) {
  els.list.querySelectorAll(".item").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.selectedId = btn.dataset.id;
      state.kindFilter = "all";
      state.showAll = false;
      render();
    });
  });
}

function renderPrimitives() {
  const items = state.result.primitives;
  const selected = items.find((p) => p.id === state.selectedId) || items[0];
  els.list.innerHTML = `
    <h2>${items.length === 1 ? "Smallest build" : `${items.length} primitives`}</h2>
    ${items
      .map(
        (p) => `
      <button type="button" class="item ${selected.id === p.id ? "active" : ""}" data-id="${p.id}">
        <div class="title">${escapeHtml(p.title)}</div>
        <div class="meta">Covers ${p.requestCount} of ${p.totalRequests} requests</div>
      </button>`,
      )
      .join("")}
  `;
  bindList(items);

  const uncovered = state.result.uncovered || [];
  els.story.innerHTML = `
    <p class="kicker">${escapeHtml(state.result.summary)}</p>
    <h1>${escapeHtml(selected.title)}</h1>
    <p class="summary">${escapeHtml(selected.oneLiner)}</p>
    <div class="block">
      <h2>Smallest build</h2>
      <ul class="ways">${selected.smallestBuild.map((s) => `<li>${escapeHtml(s)}</li>`).join("")}</ul>
    </div>
    <div class="block">
      <h2>Don’t build yet</h2>
      <ul class="ways">${selected.defer.map((s) => `<li>${escapeHtml(s)}</li>`).join("")}</ul>
    </div>
    <div class="block">
      <h2>Covers these requests</h2>
      <div class="quotes">
        ${selected.coverage
          .map(
            (s) => `
          <div class="quote">
            <p>“${escapeHtml(s.text)}”</p>
            <p class="cover">${escapeHtml(s.how)}</p>
          </div>`,
          )
          .join("")}
      </div>
    </div>
    ${
      uncovered.length
        ? `<div class="block"><h2>Not covered by these primitives</h2>
           ${uncovered.map((s) => `<p class="summary">“${escapeHtml(s.text)}”</p>`).join("")}</div>`
        : ""
    }
  `;
}

function renderPriority() {
  const items = state.result.items;
  const scheduled = items.filter((item) => item.wave);
  const blocked = items.filter((item) => !item.wave);
  els.list.innerHTML = "";
  const row = (item) => {
    const parallel = item.parallelWith
      ? ` <span class="plan-par">(in parallel with ${escapeHtml(item.parallelWith)})</span>`
      : "";
    return `
      <li class="plan-row">
        <span class="plan-num">${item.step}.</span>
        <div>
          <p class="plan-name">${escapeHtml(item.title)}${parallel}</p>
          <p class="plan-why">${escapeHtml(item.rationale || "")}</p>
        </div>
      </li>`;
  };
  els.story.innerHTML = `
    <p class="kicker">Build order</p>
    <h1>What to do, in order</h1>
    <p class="summary">${escapeHtml(state.result.summary)}</p>
    <ol class="plan">
      ${scheduled.map(row).join("")}
    </ol>
    ${
      blocked.length
        ? `<h2 class="plan-hold">Cannot start yet</h2>
           <ul class="plan">
             ${blocked
               .map(
                 (item) => `
               <li class="plan-row">
                 <span class="plan-num">—</span>
                 <div>
                   <p class="plan-name">${escapeHtml(item.title)}</p>
                   <p class="plan-why">${escapeHtml(item.rationale || "")}</p>
                 </div>
               </li>`,
               )
               .join("")}
           </ul>`
        : ""
    }
  `;
}

function renderOpportunities() {
  const selected =
    state.result.opportunities.find((o) => o.id === state.selectedId) ||
    state.result.opportunities[0];
  const opps = state.result.opportunities;

  els.list.innerHTML = `
    <h2>${opps.length} opportunities</h2>
    ${opps
      .map(
        (opp) => `
      <button type="button" class="item ${selected.id === opp.id ? "active" : ""}" data-id="${opp.id}">
        <div class="title">${escapeHtml(opp.title)}</div>
        <div class="meta">${opp.customerCount} customers</div>
      </button>`,
      )
      .join("")}
  `;
  bindList(opps);

  const members = state.result.signals.filter((s) => selected.signalIds.includes(s.id));
  let quotes = members;
  if (state.kindFilter === "problem") quotes = members.filter((s) => s.kind === "problem" || s.kind === "mixed");
  if (state.kindFilter === "solution_request") {
    quotes = members.filter((s) => s.kind === "solution_request" || s.kind === "mixed");
  }
  const visible = state.showAll ? quotes : quotes.slice(0, 6);

  els.story.innerHTML = `
    <h1>${escapeHtml(selected.title)}</h1>
    <div class="facts">
      <span><strong>${selected.signalCount}</strong> related quotes</span>
      <span><strong>${selected.customerCount}</strong> customers</span>
      <span><strong>${selected.enterpriseCount}</strong> enterprise</span>
    </div>
    <p class="summary">${escapeHtml(selected.interpretation)}</p>
    <div class="block">
      <h2>What customers said</h2>
      <div class="tabs">
        <button type="button" class="tab ${state.kindFilter === "all" ? "on" : ""}" data-kind="all">All</button>
        <button type="button" class="tab ${state.kindFilter === "problem" ? "on" : ""}" data-kind="problem">Problems</button>
        <button type="button" class="tab ${state.kindFilter === "solution_request" ? "on" : ""}" data-kind="solution_request">Feature asks</button>
      </div>
      <div class="quotes">
        ${visible
          .map(
            (s) => `
          <div class="quote">
            <p>“${escapeHtml(s.text)}”</p>
            <span>${escapeHtml(s.customer)} · ${SOURCE_LABEL[s.source] || s.source}</span>
          </div>`,
          )
          .join("")}
      </div>
      ${
        quotes.length > 6 && !state.showAll
          ? `<button class="more" id="more" type="button">Show all ${quotes.length} quotes</button>`
          : ""
      }
    </div>
    <div class="block">
      <h2>Ways to solve it</h2>
      <ul class="ways">${selected.potentialSolutions.map((s) => `<li>${escapeHtml(s)}</li>`).join("")}</ul>
    </div>
  `;

  els.story.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.kindFilter = btn.dataset.kind;
      state.showAll = false;
      render();
    });
  });
  const more = document.getElementById("more");
  if (more) {
    more.addEventListener("click", () => {
      state.showAll = true;
      render();
    });
  }
}

function speechEngine() {
  return window.SpeechRecognition || window.webkitSpeechRecognition || null;
}

function formatElapsed(ms) {
  const total = Math.floor(ms / 1000);
  const m = Math.floor(total / 60);
  const s = String(total % 60).padStart(2, "0");
  return `${m}:${s}`;
}

function appendTranscript(text) {
  const clean = text.replace(/\s+/g, " ").trim();
  if (clean.length < 3) return;
  const current = els.draft.value.trimEnd();
  els.draft.value = current ? `${current}\n${clean}` : clean;
  els.draft.scrollTop = els.draft.scrollHeight;
}

function setListeningUi(on) {
  recorder.active = on;
  els.listen.hidden = !on;
  els.record.hidden = on;
  els.record.disabled = on;
  els.interim.textContent = "";
  if (on) {
    els.listenStatus.textContent = "Listening · 0:00";
  }
}

function stopListening() {
  recorder.active = false;
  if (recorder.timer) {
    clearInterval(recorder.timer);
    recorder.timer = null;
  }
  if (recorder.recognition) {
    const rec = recorder.recognition;
    recorder.recognition = null;
    try {
      rec.onend = null;
      rec.stop();
    } catch {
      /* already stopped */
    }
  }
  setListeningUi(false);
}

async function startListening() {
  showError("");
  const Ctor = speechEngine();
  if (!Ctor) {
    showError("Live interviews work in Chrome or Edge. Paste a transcript here if you’re on another browser.");
    return;
  }

  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop());
    } catch {
      showError("Microphone access is blocked. Allow the mic for this site, then try again.");
      return;
    }
  }

  const rec = new Ctor();
  rec.continuous = true;
  rec.interimResults = true;
  rec.lang = navigator.language || "en-US";

  rec.onresult = (event) => {
    let interim = "";
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const piece = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        appendTranscript(piece);
      } else {
        interim += piece;
      }
    }
    els.interim.textContent = interim.trim();
  };

  rec.onerror = (event) => {
    const err = event.error;
    if (err === "no-speech" || err === "aborted") return;
    if (err === "not-allowed" || err === "service-not-allowed") {
      stopListening();
      showError("Microphone access is blocked. Allow the mic for this site, then try again.");
      return;
    }
    if (err === "audio-capture") {
      stopListening();
      showError("No microphone found. Plug one in and try again.");
      return;
    }
    if (err === "network") {
      stopListening();
      showError("Live transcription needs Chrome or Edge, and an internet connection.");
      return;
    }
    stopListening();
    showError("Couldn’t start live transcription. Try Chrome, and allow the microphone.");
  };

  rec.onend = () => {
    if (!recorder.active) return;
    try {
      rec.start();
    } catch {
      stopListening();
    }
  };

  try {
    rec.start();
  } catch (err) {
    showError("Couldn’t start the microphone. Check permissions and try Chrome.");
    return;
  }

  recorder.recognition = rec;
  recorder.startedAt = Date.now();
  recorder.headerWritten = false;
  setListeningUi(true);
  recorder.timer = setInterval(() => {
    els.listenStatus.textContent = `Listening · ${formatElapsed(Date.now() - recorder.startedAt)}`;
  }, 250);
}

function syncProviderFields() {
  const provider = els.provider.value;
  els.fieldHost.hidden = provider !== "jira";
  els.fieldEmail.hidden = provider !== "jira";
  els.fieldScope.hidden = provider === "linear";
  if (provider === "github") {
    els.scopeLabel.textContent = "Repo";
    els.scope.placeholder = "owner/repo";
    els.connectHint.textContent = "GitHub token with read access to issues. Used once for this import, not saved on the server.";
  } else if (provider === "jira") {
    els.scopeLabel.textContent = "JQL (optional)";
    els.scope.placeholder = "statusCategory != Done";
    els.connectHint.textContent = "Jira API token from id.atlassian.com. Used once for this import, not saved on the server.";
  } else {
    els.connectHint.textContent = "Linear personal API key. Used once for this import, not saved on the server.";
  }
}

async function importBacklog() {
  showError("");
  els.importBtn.disabled = true;
  els.importBtn.textContent = "Importing…";
  const provider = els.provider.value;
  const body = { provider, token: els.token.value };
  if (provider === "github") body.repo = els.scope.value;
  if (provider === "jira") {
    body.host = els.jiraHost.value;
    body.email = els.jiraEmail.value;
    body.jql = els.scope.value;
  }
  try {
    const res = await fetch("/api/backlog", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || "Import failed");
    if (state.mode === "priority") {
      fillBoard(data.items.map((item) => emptyItem({ title: item.text })));
      els.connectHint.textContent = `Imported ${data.count} open items. Fill RICE and commercial factors, then rank.`;
    } else {
      els.draft.value = data.items.map((item) => item.text).join("\n");
      els.connectHint.textContent = `Imported ${data.count} open items. Rank the primitive next.`;
    }
  } catch (err) {
    showError(err.message || "Couldn’t import the backlog.");
  } finally {
    els.importBtn.disabled = false;
    els.importBtn.textContent = "Import open items";
  }
}

function reset() {
  stopListening();
  state.result = null;
  state.view = "chooser";
  els.results.classList.remove("is-plan");
  showError("");
  showView();
}

els.sample.addEventListener("click", async () => {
  stopListening();
  if (state.mode === "priority") {
    try {
      const res = await fetch("/api/sample-priority");
      const data = await res.json();
      els.capacity.value = data.capacity ?? 50;
      fillBoard(data.items);
      analyze({
        ...priorityContext(),
        items: data.items,
      });
    } catch (err) {
      showError(err.message || "Couldn’t load the sample.");
    }
    return;
  }
  analyze({ useSample: true });
});
els.back.addEventListener("click", reset);
els.home.addEventListener("click", (event) => {
  event.preventDefault();
  reset();
});
els.record.addEventListener("click", startListening);
els.stop.addEventListener("click", stopListening);

document.querySelectorAll(".nav-item, .choice").forEach((btn) => {
  btn.addEventListener("click", () => openWorkspace(btn.dataset.mode));
});

els.provider.addEventListener("change", syncProviderFields);
els.importBtn.addEventListener("click", importBacklog);

els.addRow.addEventListener("click", () => {
  els.boardBody.insertAdjacentHTML("beforeend", rowHtml(emptyItem()));
});

fillDefinitionPick();
els.defineToggle.addEventListener("click", () => {
  const opening = els.defineBody.hidden;
  if (opening) showDefinition(els.definePick.value || "capacity", true);
  else setGlossaryOpen(false);
});
els.definePick.addEventListener("change", () => {
  showDefinition(els.definePick.value, true);
});
document.addEventListener("focusin", (event) => {
  if (els.define.contains(event.target)) return;
  const key = definitionKey(event.target);
  if (key) showDefinition(key);
});
document.addEventListener("click", (event) => {
  const header = event.target.closest("th[data-define]");
  if (header) showDefinition(header.dataset.define);
});

els.run.addEventListener("click", () => {
  stopListening();
  if (state.mode === "priority") {
    const items = collectBoard().filter((item) => String(item.title || "").trim());
    if (!items.length) {
      showError(COPY.priority.empty);
      return;
    }
    analyze({
      ...priorityContext(),
      items,
    });
    return;
  }
  if (!els.draft.value.trim()) {
    showError(COPY[state.mode].empty);
    return;
  }
  analyze({ text: els.draft.value });
});

syncProviderFields();
showView();

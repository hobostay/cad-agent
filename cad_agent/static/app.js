const state = {
  schemas: {},
  selectedType: null,
  lastSpec: null,
  history: [],
};

function $(id) {
  return document.getElementById(id);
}

function showToast(message, isError = false) {
  const toast = $("toast");
  toast.textContent = message;
  toast.className = `toast ${isError ? "error" : "success"} show`;
  setTimeout(() => {
    toast.className = "toast";
  }, 2500);
}

function switchSection(sectionId) {
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.section === sectionId);
  });
  document.querySelectorAll(".content-section").forEach((section) => {
    section.classList.toggle("active", section.id === `${sectionId}-section`);
  });
  const titleMap = {
    design: "参数设计",
    "ai-chat": "AI 设计",
    history: "历史记录",
  };
  $(".page-title").textContent = titleMap[sectionId] || "参数设计";
}

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) {
    throw new Error(`请求失败: ${res.status}`);
  }
  return res.json();
}

async function loadSchemas() {
  const data = await fetchJSON("/api/schema");
  if (data.success) {
    state.schemas = data.data || {};
  }
}

async function loadPartTypes() {
  const data = await fetchJSON("/api/part-types");
  const container = $("partCategories");
  container.innerHTML = "";

  const categories = data.categories || {};
  Object.keys(categories).forEach((cat) => {
    const wrapper = document.createElement("div");
    wrapper.className = "category";
    const title = document.createElement("h3");
    title.textContent = cat;
    wrapper.appendChild(title);

    const grid = document.createElement("div");
    grid.className = "part-grid";
    Object.entries(categories[cat]).forEach(([key, label]) => {
      const btn = document.createElement("button");
      btn.className = "part-btn";
      btn.textContent = label;
      btn.addEventListener("click", () => selectPartType(key));
      grid.appendChild(btn);
    });
    wrapper.appendChild(grid);
    container.appendChild(wrapper);
  });
}

function selectPartType(partType) {
  state.selectedType = partType;
  $("parameterPanel").style.display = "block";
  $("resultPanel").style.display = "none";
  renderParameterForm(partType);
}

function renderParameterForm(partType) {
  const form = $("parameterForm");
  form.innerHTML = "";

  const schema = state.schemas[partType] || {};
  const hasSchema = Object.keys(schema).length > 0;

  const outputWrap = document.createElement("div");
  outputWrap.className = "form-row";
  outputWrap.innerHTML = `
    <label>输出格式</label>
    <select id="outputFormat">
      <option value="dxf">DXF (2D)</option>
      <option value="stl">STL (3D)</option>
    </select>
  `;
  form.appendChild(outputWrap);

  if (!hasSchema) {
    const note = document.createElement("div");
    note.className = "form-note";
    note.textContent = "当前零件没有参数 Schema，请直接输入 JSON。";
    form.appendChild(note);

    const textarea = document.createElement("textarea");
    textarea.id = "rawJson";
    textarea.rows = 10;
    textarea.placeholder = '{"param1": 100, "param2": 50}';
    form.appendChild(textarea);
    return;
  }

  Object.entries(schema).forEach(([key, meta]) => {
    const row = document.createElement("div");
    row.className = "form-row";

    const label = document.createElement("label");
    label.textContent = `${key}${meta.description ? ` (${meta.description})` : ""}`;
    row.appendChild(label);

    if (meta.type === "array" || meta.type === "object") {
      const textarea = document.createElement("textarea");
      textarea.id = `field_${key}`;
      textarea.rows = 3;
      textarea.placeholder = meta.type === "array" ? "[]" : "{}";
      row.appendChild(textarea);
    } else {
      const input = document.createElement("input");
      input.id = `field_${key}`;
      input.type = "number";
      if (meta.min !== undefined) input.min = meta.min;
      if (meta.max !== undefined) input.max = meta.max;
      input.placeholder = meta.description || key;
      row.appendChild(input);
    }
    form.appendChild(row);
  });
}

function collectParameters() {
  const schema = state.schemas[state.selectedType] || {};
  const hasSchema = Object.keys(schema).length > 0;

  if (!hasSchema) {
    const raw = $("rawJson").value.trim();
    if (!raw) return {};
    try {
      return JSON.parse(raw);
    } catch (e) {
      throw new Error("JSON 格式错误");
    }
  }

  const params = {};
  Object.entries(schema).forEach(([key, meta]) => {
    const el = $(`field_${key}`);
    if (!el) return;
    const val = el.value.trim();
    if (!val) return;
    if (meta.type === "array" || meta.type === "object") {
      params[key] = JSON.parse(val);
    } else if (meta.type === "int") {
      params[key] = parseInt(val, 10);
    } else {
      params[key] = parseFloat(val);
    }
  });
  return params;
}

async function generateCAD() {
  if (!state.selectedType) {
    showToast("请先选择零件类型", true);
    return;
  }
  try {
    const params = collectParameters();
    const outputFormat = $("outputFormat").value;

    const payload = {
      part_type: state.selectedType,
      parameters: params,
      output_format: outputFormat,
    };

    const result = await fetchJSON("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!result.success) {
      showToast(result.error || "生成失败", true);
      return;
    }

    state.lastSpec = payload;
    updateHistory({
      type: state.selectedType,
      params,
      filename: result.filename,
      format: outputFormat,
    });

    renderResult(result);
    showToast("生成成功");
  } catch (e) {
    showToast(e.message || "生成失败", true);
  }
}

async function validateDesign() {
  if (!state.selectedType) {
    showToast("请先选择零件类型", true);
    return;
  }
  try {
    const params = collectParameters();
    const payload = {
      part_type: state.selectedType,
      parameters: params,
      output_format: "dxf",
    };

    const result = await fetchJSON("/api/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!result.success) {
      showToast(result.error || "验证失败", true);
      return;
    }

    const msg = result.valid ? "验证通过" : "验证未通过";
    showToast(msg, !result.valid);
  } catch (e) {
    showToast(e.message || "验证失败", true);
  }
}

function renderResult(result) {
  const panel = $("resultPanel");
  const content = $("resultContent");
  panel.style.display = "block";
  content.innerHTML = `
    <div class="result-item">
      <div>文件名: <code>${result.filename}</code></div>
      <div>大小: ${result.size} bytes</div>
      <div>格式: ${result.format}</div>
      <div class="result-actions">
        <a class="btn btn-primary" href="/api/download/${result.filename}" target="_blank">下载文件</a>
      </div>
    </div>
  `;
}

function updateHistory(item) {
  const stored = JSON.parse(localStorage.getItem("cad_history") || "[]");
  stored.unshift({ ...item, time: new Date().toISOString() });
  localStorage.setItem("cad_history", JSON.stringify(stored.slice(0, 20)));
  renderHistory();
}

function renderHistory() {
  const list = $("historyList");
  const stored = JSON.parse(localStorage.getItem("cad_history") || "[]");
  if (!stored.length) {
    list.innerHTML = '<p class="empty-state">暂无历史记录</p>';
    return;
  }
  list.innerHTML = "";
  stored.forEach((item) => {
    const row = document.createElement("div");
    row.className = "history-item";
    row.innerHTML = `
      <div class="history-title">${item.type} (${item.format})</div>
      <div class="history-meta">${new Date(item.time).toLocaleString()}</div>
      <div class="history-actions">
        <a href="/api/download/${item.filename}" target="_blank">下载</a>
      </div>
    `;
    list.appendChild(row);
  });
}

async function sendDesignPrompt() {
  const input = $("chatInput");
  const text = input.value.trim();
  if (!text) return;

  appendMessage("user", text);
  input.value = "";

  try {
    const result = await fetchJSON("/api/design", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    if (!result.success) {
      appendMessage("assistant", result.error || "解析失败");
      showToast("解析失败", true);
      return;
    }
    appendMessage("assistant", "已生成参数，请查看右侧解析结果。");
    showParseResult(result.data, result.reasoning);
  } catch (e) {
    appendMessage("assistant", e.message || "解析失败");
    showToast("解析失败", true);
  }
}

function appendMessage(role, content) {
  const box = $("chatMessages");
  const item = document.createElement("div");
  item.className = `chat-message ${role}`;
  item.textContent = content;
  box.appendChild(item);
  box.scrollTop = box.scrollHeight;
}

function showParseResult(spec, reasoning) {
  $("parseResult").style.display = "block";
  $("parseJson").textContent = JSON.stringify(spec, null, 2);
  $("useSpecBtn").onclick = () => {
    if (!spec || !spec.type) {
      showToast("参数缺少 type", true);
      return;
    }
    switchSection("design");
    selectPartType(spec.type);

    const params = spec.parameters || {};
    const schema = state.schemas[spec.type] || {};
    const hasSchema = Object.keys(schema).length > 0;

    if (!hasSchema) {
      $("rawJson").value = JSON.stringify(params, null, 2);
      return;
    }

    Object.entries(schema).forEach(([key, meta]) => {
      const el = $(`field_${key}`);
      if (!el) return;
      const val = params[key];
      if (val === undefined || val === null) return;
      if (meta.type === "array" || meta.type === "object") {
        el.value = JSON.stringify(val);
      } else {
        el.value = val;
      }
    });
    showToast("参数已填充，可直接生成");
  };
}

function initNav() {
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.addEventListener("click", () => switchSection(item.dataset.section));
  });
}

function initEvents() {
  $("generateBtn").addEventListener("click", generateCAD);
  $("validateBtn").addEventListener("click", validateDesign);
  $("sendBtn").addEventListener("click", sendDesignPrompt);
  $("chatInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendDesignPrompt();
    }
  });
}

async function init() {
  initNav();
  initEvents();
  await loadSchemas();
  await loadPartTypes();
  renderHistory();
}

window.setPrompt = (text) => {
  $("chatInput").value = text;
  $("chatInput").focus();
};

document.addEventListener("DOMContentLoaded", init);

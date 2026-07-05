(function () {
  const historyStack = [];
  let currentId = START_NODE;

  const questionEl = document.getElementById("node-question");
  const optionsEl = document.getElementById("node-options");
  const solutionEl = document.getElementById("node-solution");
  const solutionTitleEl = document.getElementById("solution-title");
  const solutionStepsEl = document.getElementById("solution-steps");
  const solutionLinksEl = document.getElementById("solution-links");
  const breadcrumbEl = document.getElementById("breadcrumb");
  const backBtn = document.getElementById("back-btn");
  const restartBtn = document.getElementById("restart-btn");

  function render(nodeId) {
    const node = TREE[nodeId];
    if (!node) {
      console.error("Unknown troubleshooter node:", nodeId);
      return;
    }
    currentId = nodeId;

    if (node.type === "question") {
      questionEl.textContent = node.text;
      optionsEl.innerHTML = "";
      node.options.forEach((opt) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "btn btn-outline-primary w-100 text-start mb-2";
        btn.textContent = opt.label;
        btn.addEventListener("click", () => goTo(opt.next));
        optionsEl.appendChild(btn);
      });
      questionEl.closest(".card").classList.remove("d-none");
      solutionEl.classList.add("d-none");
    } else if (node.type === "solution") {
      solutionTitleEl.textContent = node.title;
      solutionStepsEl.innerHTML = "";
      node.steps.forEach((step) => {
        const li = document.createElement("li");
        li.textContent = step;
        solutionStepsEl.appendChild(li);
      });
      solutionLinksEl.innerHTML = "";
      (node.links || []).forEach((link) => {
        const a = document.createElement("a");
        a.href = link.href;
        a.target = "_blank";
        a.rel = "noopener";
        a.className = "btn btn-sm btn-outline-secondary me-2 mb-2";
        a.textContent = link.label;
        solutionLinksEl.appendChild(a);
      });
      questionEl.closest(".card").classList.add("d-none");
      solutionEl.classList.remove("d-none");
    }

    backBtn.disabled = historyStack.length === 0;
    renderBreadcrumb();
  }

  function goTo(nextId) {
    historyStack.push(currentId);
    render(nextId);
  }

  function goBack() {
    if (historyStack.length === 0) return;
    const prevId = historyStack.pop();
    render(prevId);
  }

  function restart() {
    historyStack.length = 0;
    render(START_NODE);
  }

  function renderBreadcrumb() {
    const trail = [...historyStack, currentId];
    breadcrumbEl.innerHTML = "";
    trail.forEach((id, idx) => {
      const li = document.createElement("li");
      li.className = "breadcrumb-item" + (idx === trail.length - 1 ? " active" : "");
      li.textContent = idx === 0 ? "Start" : "Step " + idx;
      breadcrumbEl.appendChild(li);
    });
  }

  backBtn.addEventListener("click", goBack);
  restartBtn.addEventListener("click", restart);

  render(START_NODE);
})();

window.NorthStarRender = {
  renderScenarios(scenarios, onSelect) {
    const list = document.querySelector("#scenario-list");
    const actions = document.querySelector("#quick-actions");

    list.innerHTML = scenarios
      .map((scenario) => `<li data-scenario="${scenario.id}">${scenario.label}<span>Ready</span></li>`)
      .join("");

    actions.innerHTML = "";
    scenarios.forEach((scenario) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = scenario.label;
      button.addEventListener("click", () => onSelect(scenario));
      actions.appendChild(button);
    });
  },

  addMessage(role, text) {
    const list = document.querySelector("#message-list");
    const message = document.createElement("div");
    message.className = `message ${role}`;
    message.textContent = text;
    list.appendChild(message);
    list.scrollTop = list.scrollHeight;
  },

  updateScenario(intent) {
    const scenarioByIntent = {
      order_tracking: "orders",
      returns_exchange: "returns",
      product_recommendation: "recommendations",
      human_handoff: "handoff",
      fallback: "fallback",
    };
    const scenarioId = scenarioByIntent[intent];
    if (!scenarioId) return;

    const item = document.querySelector(`[data-scenario="${scenarioId}"] span`);
    if (item) item.textContent = "Seen";
  },

  updateDebug(payload) {
    document.querySelector("#debug-output").textContent = JSON.stringify(payload, null, 2);
  },
};

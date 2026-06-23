window.NorthStarRender = {
  optionPattern: /^\s*-?\s*(\d+)\.\s+(.+)$/gm,

  renderScenarios(scenarios, onSelect) {
    const list = document.querySelector("#scenario-list");
    const actions = document.querySelector("#quick-actions");

    list.innerHTML = scenarios
      .map((scenario) => `<li data-scenario="${scenario.id}">${scenario.label}<span>Ready</span></li>`)
      .join("");

    actions.innerHTML = "";
    scenarios.filter((scenario) => scenario.showQuickAction !== false).forEach((scenario) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = scenario.label;
      button.addEventListener("click", () => onSelect(scenario));
      actions.appendChild(button);
    });
  },

  parseOptions(text) {
    const options = [];
    let match;

    while ((match = this.optionPattern.exec(text)) !== null) {
      options.push({
        value: match[1],
        label: match[2],
        fullText: match[0],
      });
    }

    this.optionPattern.lastIndex = 0;
    return options;
  },

  stripOptions(text, options) {
    return options.reduce(
      (messageText, option) => messageText.replace(option.fullText, "").trim(),
      text
    );
  },

  addMessage(role, text, onOptionSelect) {
    const list = document.querySelector("#message-list");
    const message = document.createElement("div");
    message.className = `message ${role}`;

    const options = role === "bot" ? this.parseOptions(text) : [];
    const messageText = options.length ? this.stripOptions(text, options) : text;

    const content = document.createElement("p");
    content.textContent = messageText;
    message.appendChild(content);

    if (options.length && typeof onOptionSelect === "function") {
      const optionList = document.createElement("div");
      optionList.className = "message-options";

      options.forEach((option) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = `${option.value}. ${option.label}`;
        button.addEventListener("click", () => onOptionSelect(option.value));
        optionList.appendChild(button);
      });

      message.appendChild(optionList);
    }

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

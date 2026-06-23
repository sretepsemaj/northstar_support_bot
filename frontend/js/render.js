window.NorthStarRender = {
  optionPattern: /^\s*-?\s*(\d+)\.\s+(.+)$/gm,
  optionLinePattern: /^\s*-?\s*(\d+)\.\s+(.+)$/,

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

  appendParagraph(message, lines) {
    const text = lines.join("\n").replace(/\n{3,}/g, "\n\n").trim();
    if (!text) return;

    const content = document.createElement("p");
    content.textContent = text;
    message.appendChild(content);
  },

  appendOptionButton(optionList, value, label, onOptionSelect) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `${value}. ${label}`;
    button.addEventListener("click", () => onOptionSelect(value));
    optionList.appendChild(button);
  },

  addMessage(role, text, onOptionSelect) {
    const list = document.querySelector("#message-list");
    const message = document.createElement("div");
    message.className = `message ${role}`;

    if (role !== "bot" || typeof onOptionSelect !== "function") {
      this.appendParagraph(message, [text]);
      list.appendChild(message);
      list.scrollTop = list.scrollHeight;
      return;
    }

    let paragraphLines = [];
    let optionList = null;

    text.split("\n").forEach((line) => {
      const optionMatch = line.match(this.optionLinePattern);

      if (!optionMatch) {
        optionList = null;
        paragraphLines.push(line);
        return;
      }

      this.appendParagraph(message, paragraphLines);
      paragraphLines = [];

      if (!optionList) {
        optionList = document.createElement("div");
        optionList.className = "message-options";
        message.appendChild(optionList);
      }

      this.appendOptionButton(optionList, optionMatch[1], optionMatch[2], onOptionSelect);
    });

    this.appendParagraph(message, paragraphLines);

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

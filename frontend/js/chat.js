const chatState = {
  conversation: {},
};

async function sendChatMessage(message) {
  const trimmed = message.trim();
  if (!trimmed) return;

  NorthStarWidget.open();
  NorthStarRender.addMessage("user", trimmed);

  try {
    const payload = await NorthStarApi.sendMessage(trimmed, chatState.conversation);
    chatState.conversation = payload.state || {};
    NorthStarRender.addMessage("bot", payload.reply, sendChatMessage);
    NorthStarRender.updateScenario(payload.intent);
    NorthStarRender.updateDebug(payload);
  } catch (error) {
    NorthStarRender.addMessage("bot", "Something went wrong reaching the local demo API.");
    NorthStarRender.updateDebug({ error: error.message });
  }
}

function bindChatForm() {
  const form = document.querySelector("#chat-form");
  const input = document.querySelector("#message-input");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value;
    input.value = "";
    await sendChatMessage(message);
  });
}

function initChat() {
  NorthStarWidget.bind();
  NorthStarRender.renderScenarios(window.NORTH_STAR_SCENARIOS, (scenario) => {
    sendChatMessage(scenario.prompt);
  });
  NorthStarRender.addMessage(
    "bot",
    "Hi, I'm North Star customer support. What may I help you with?",
    sendChatMessage
  );
  bindChatForm();
}

initChat();

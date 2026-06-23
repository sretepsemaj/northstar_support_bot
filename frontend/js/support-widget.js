window.NorthStarWidget = {
  nudgeTimer: null,

  open() {
    const widget = document.querySelector("#support-widget");
    const launcher = document.querySelector("#support-launcher");
    widget.hidden = false;
    launcher.setAttribute("aria-expanded", "true");
    this.hideNudge();
    document.querySelector("#message-input").focus();
  },

  close() {
    const widget = document.querySelector("#support-widget");
    const launcher = document.querySelector("#support-launcher");
    widget.hidden = true;
    launcher.setAttribute("aria-expanded", "false");
    this.scheduleNudge();
  },

  showNudge() {
    const widget = document.querySelector("#support-widget");
    if (!widget.hidden) return;

    const nudge = document.querySelector("#support-nudge");
    nudge.hidden = false;
    window.setTimeout(() => {
      nudge.hidden = true;
    }, 4500);
  },

  hideNudge() {
    document.querySelector("#support-nudge").hidden = true;
    if (this.nudgeTimer) window.clearTimeout(this.nudgeTimer);
  },

  scheduleNudge() {
    if (this.nudgeTimer) window.clearTimeout(this.nudgeTimer);
    this.nudgeTimer = window.setTimeout(() => this.showNudge(), 4500);
  },

  bind() {
    document.querySelector("#support-launcher").addEventListener("click", () => this.open());
    document.querySelector("#close-support").addEventListener("click", () => this.close());
    this.scheduleNudge();
  },
};

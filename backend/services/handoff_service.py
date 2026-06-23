from dataclasses import dataclass


@dataclass(frozen=True)
class HandoffResult:
    message: str
    queue: str
    reason: str
    should_handoff: bool = True


def create_handoff() -> HandoffResult:
    return HandoffResult(
        message=(
            "I can connect you with a live agent. "
            "I'll mark this conversation for human support now."
        ),
        queue="customer_support",
        reason="user_requested_human_support",
    )

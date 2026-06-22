from dataclasses import dataclass

from backend.data.policies import RETURN_POLICY


@dataclass(frozen=True)
class ReturnsPolicyResult:
    message: str
    returns_link: str


def get_returns_policy() -> ReturnsPolicyResult:
    window_days = RETURN_POLICY["window_days"]
    condition = RETURN_POLICY["condition"]
    packaging = RETURN_POLICY["packaging"]
    returns_link = RETURN_POLICY["returns_link"]

    return ReturnsPolicyResult(
        message=(
            f"North Star accepts returns and exchanges within {window_days} days "
            f"for {condition} in {packaging}. You can start here: {returns_link}"
        ),
        returns_link=returns_link,
    )


def get_exchange_policy() -> ReturnsPolicyResult:
    policy = get_returns_policy()
    return ReturnsPolicyResult(
        message=(
            "Exchanges follow the same policy as returns. "
            f"{policy.message}"
        ),
        returns_link=policy.returns_link,
    )

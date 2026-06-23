from dataclasses import dataclass

from backend.data.policies import SHIPPING_POLICY


@dataclass(frozen=True)
class ShippingPolicyResult:
    standard: str
    expedited: str
    message: str


def get_shipping_policy() -> ShippingPolicyResult:
    standard = SHIPPING_POLICY["standard"]
    expedited = SHIPPING_POLICY["expedited"]

    return ShippingPolicyResult(
        standard=standard,
        expedited=expedited,
        message=(
            f"North Star shipping options are Standard ({standard}) "
            f"and Expedited ({expedited})."
        ),
    )

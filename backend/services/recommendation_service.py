from dataclasses import dataclass


@dataclass(frozen=True)
class RecommendationResult:
    category: str | None
    message: str
    needs_clarification: bool = False
    questions: tuple[str, ...] = ()


CATEGORY_KEYWORDS = {
    "Camping Gear": {
        "camp",
        "camping",
        "tent",
        "sleeping bag",
        "backcountry",
        "campground",
    },
    "Outdoor Apparel": {
        "apparel",
        "clothing",
        "jacket",
        "layer",
        "layers",
        "pants",
        "shirt",
        "warm",
    },
    "Hiking Footwear": {
        "hike",
        "hiking",
        "boot",
        "boots",
        "trail",
        "footwear",
        "shoes",
    },
    "Climbing Essentials": {
        "climb",
        "climbing",
        "rock",
        "harness",
        "chalk",
        "belay",
    },
    "Weather Protection": {
        "rain",
        "snow",
        "storm",
        "waterproof",
        "wind",
        "shell",
    },
}

CLARIFYING_QUESTIONS = (
    "What activity are you shopping for: camping, hiking, climbing, or weather protection?",
    "What conditions do you expect: warm, cold, wet, or mixed weather?",
)


def recommend_category(message: str) -> RecommendationResult:
    normalized_message = message.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in normalized_message for keyword in keywords):
            return RecommendationResult(
                category=category,
                message=f"For that trip, I recommend starting with our {category} category.",
            )

    return RecommendationResult(
        category=None,
        message="I can help narrow that down with a couple quick questions.",
        needs_clarification=True,
        questions=CLARIFYING_QUESTIONS,
    )

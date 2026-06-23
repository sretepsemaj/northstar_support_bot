from dataclasses import dataclass


@dataclass(frozen=True)
class RecommendationResult:
    category: str | None
    message: str
    needs_clarification: bool = False
    questions: tuple[str, ...] = ()
    waiting_for_detail: bool = False


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
        "cold",
        "clothing",
        "insulated",
        "insulation",
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
        "rain coat",
        "rain coats",
        "rain gear",
        "raingear",
        "raincoat",
        "raincoats",
        "snow",
        "storm",
        "waterproof",
        "weather protection",
        "wind",
        "shell",
    },
}

CATEGORY_OPTIONS = (
    "Camping Gear",
    "Outdoor Apparel",
    "Hiking Footwear",
    "Climbing Essentials",
    "Weather Protection",
)

CATEGORY_DETAIL_OPTIONS = {
    "Camping Gear": (
        "Tents and shelters",
        "Sleeping bags and camp comfort",
        "Trail cooking and campsite basics",
    ),
    "Outdoor Apparel": (
        "Warm layers and fleece",
        "Insulated jackets",
        "Trail pants and everyday outdoor clothing",
    ),
    "Hiking Footwear": (
        "Hiking boots",
        "Trail shoes",
        "Wet-weather or rugged-terrain footwear",
    ),
    "Climbing Essentials": (
        "Climbing shoes",
        "Harnesses and belay basics",
        "Chalk, ropes, and protection essentials",
    ),
    "Weather Protection": (
        "Rain shells and waterproof layers",
        "Wind protection",
        "Cold-weather outer layers",
        "Snow or storm protection",
    ),
}

CATEGORY_SELECTIONS = {
    "1": "Camping Gear",
    "camping gear": "Camping Gear",
    "camping": "Camping Gear",
    "2": "Outdoor Apparel",
    "outdoor apparel": "Outdoor Apparel",
    "apparel": "Outdoor Apparel",
    "3": "Hiking Footwear",
    "hiking footwear": "Hiking Footwear",
    "footwear": "Hiking Footwear",
    "4": "Climbing Essentials",
    "climbing essentials": "Climbing Essentials",
    "climbing": "Climbing Essentials",
    "5": "Weather Protection",
    "weather protection": "Weather Protection",
}

CONTEXT_MODIFIERS = {
    "cold",
    "durable",
    "lightweight",
    "rain",
    "rugged",
    "warm",
    "waterproof",
    "wet",
    "wind",
}

CONTEXT_MODIFIER_FILLER_WORDS = {
    "a",
    "an",
    "for",
    "just",
    "kind",
    "maybe",
    "please",
    "something",
}

DETAIL_STOP_WORDS = {
    "a",
    "an",
    "and",
    "better",
    "do",
    "else",
    "for",
    "get",
    "have",
    "i",
    "like",
    "need",
    "no",
    "some",
    "the",
    "to",
    "want",
    "what",
    "you",
}


def _format_option_list(options: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(f"{index}. {option}" for index, option in enumerate(options, start=1))


def _parse_category_selection(message: str) -> str | None:
    normalized_message = message.strip().lower()
    if normalized_message in CATEGORY_SELECTIONS:
        return CATEGORY_SELECTIONS[normalized_message]

    for category in CATEGORY_OPTIONS:
        if category.lower() in normalized_message:
            return category

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in normalized_message for keyword in keywords):
            return category

    return None


def _build_category_detail_prompt(category: str) -> RecommendationResult:
    return RecommendationResult(
        category=category,
        message=f"{category} is a good fit. What kind of gear should we narrow that down to?",
        needs_clarification=True,
        questions=_format_option_list(CATEGORY_DETAIL_OPTIONS[category]),
        waiting_for_detail=True,
    )


def _build_category_switch_prompt(
    current_category: str,
    suggested_category: str,
) -> RecommendationResult:
    return RecommendationResult(
        category=current_category,
        message=(
            f"That sounds related to {suggested_category}, but we were narrowing "
            f"{current_category}. Would you like to switch categories or keep going "
            f"with {current_category}?"
        ),
        needs_clarification=True,
        questions=(
            f"Switch to {suggested_category}",
            f"Keep narrowing {current_category}",
        ),
        waiting_for_detail=True,
    )


def _is_context_modifier(message: str) -> bool:
    words = {
        word
        for word in message.split()
        if len(word) > 2 and word not in CONTEXT_MODIFIER_FILLER_WORDS
    }
    return bool(words and words.issubset(CONTEXT_MODIFIERS))


def _is_keep_narrowing_current_category_request(category: str, message: str) -> bool:
    normalized_message = message.strip().lower()
    return (
        "keep" in normalized_message
        and "narrow" in normalized_message
        and category.lower() in normalized_message
    )


def recommend_category_detail(category: str, message: str) -> RecommendationResult:
    normalized_message = message.strip().lower()
    if _is_keep_narrowing_current_category_request(category, message):
        return _build_category_detail_prompt(category)

    selected_category = None if normalized_message.isdigit() else _parse_category_selection(message)
    if selected_category is not None and selected_category != category:
        if _is_context_modifier(normalized_message):
            return _build_category_switch_prompt(category, selected_category)
        return _build_category_detail_prompt(selected_category)

    options = CATEGORY_DETAIL_OPTIONS.get(category)
    if options is None:
        return RecommendationResult(
            category=category,
            message=f"For that trip, I recommend starting with our {category} category.",
        )

    meaningful_words = {
        word
        for word in normalized_message.split()
        if len(word) > 2 and word not in DETAIL_STOP_WORDS
    }
    selected_detail = None
    if normalized_message.isdigit():
        option_index = int(normalized_message) - 1
        if 0 <= option_index < len(options):
            selected_detail = options[option_index]

    if selected_detail is None:
        selected_detail = next(
            (
                option
                for option in options
                if normalized_message in option.lower()
                or any(word in option.lower() for word in meaningful_words)
            ),
            None,
        )

    if selected_detail is not None:
        return RecommendationResult(
            category=category,
            message=(
                f"Great choice. I recommend our {category} category, "
                f"especially {selected_detail.lower()}."
            ),
        )

    return RecommendationResult(
        category=None,
        message="I may be outside that category. What are you shopping for today?",
        needs_clarification=True,
        questions=_format_option_list(CATEGORY_OPTIONS),
    )


def recommend_category(message: str) -> RecommendationResult:
    selected_category = _parse_category_selection(message)
    if selected_category is not None:
        return _build_category_detail_prompt(selected_category)

    return RecommendationResult(
        category=None,
        message="I can help with that. What are you shopping for today?",
        needs_clarification=True,
        questions=_format_option_list(CATEGORY_OPTIONS),
    )

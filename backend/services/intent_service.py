from dataclasses import dataclass
from difflib import get_close_matches
from enum import StrEnum
import re


class Intent(StrEnum):
    MAIN_MENU = "main_menu"
    PRODUCT_RECOMMENDATION = "product_recommendation"
    ORDER_TRACKING = "order_tracking"
    RETURNS_EXCHANGE = "returns_exchange"
    GRATITUDE = "gratitude"
    HUMAN_HANDOFF = "human_handoff"
    FALLBACK = "fallback"


class MatchStrategy(StrEnum):
    TYPO_ALIAS = "typo_alias"
    ORDER_NUMBER = "order_number"
    EXACT_PHRASE = "exact_phrase"
    EXACT_KEYWORD = "exact_keyword"
    FUZZY_KEYWORD = "fuzzy_keyword"
    FALLBACK = "fallback"


@dataclass(frozen=True)
class IntentResult:
    intent: Intent
    matched_terms: tuple[str, ...] = ()
    normalized_message: str = ""
    match_strategy: MatchStrategy = MatchStrategy.FALLBACK
    needs_review: bool = False


INTENT_PHRASES: dict[Intent, tuple[str, ...]] = {
    Intent.MAIN_MENU: (
        "what can you do",
        "what can you help with",
        "main menu",
        "show me options",
    ),
    Intent.PRODUCT_RECOMMENDATION: (
        "what should i buy",
        "help me choose",
        "what do you recommend",
        "recommend a",
        "suggest a",
    ),
    Intent.ORDER_TRACKING: (
        "where is my order",
        "where's my order",
        "track my order",
        "track my package",
        "shipping status",
        "order status",
    ),
    Intent.RETURNS_EXCHANGE: (
        "return policy",
        "start a return",
        "send it back",
        "wrong size",
        "doesn't fit",
        "does not fit",
    ),
    Intent.GRATITUDE: (
        "thank you",
        "appreciate it",
        "appreciate your help",
        "you were a great help",
        "that helped",
        "this helped",
        "perfect thanks",
    ),
    Intent.HUMAN_HANDOFF: (
        "live agent",
        "talk to a person",
        "talk to someone",
        "speak to a person",
        "speak to someone",
        "customer service",
        "support team",
    ),
}

INTENT_KEYWORDS: dict[Intent, tuple[str, ...]] = {
    Intent.GRATITUDE: (
        "thanks",
        "thx",
    ),
    Intent.MAIN_MENU: (
        "hi",
        "hello",
        "hey",
        "help",
        "start",
        "menu",
    ),
    Intent.HUMAN_HANDOFF: (
        "human",
        "person",
        "agent",
        "representative",
        "someone",
    ),
    Intent.ORDER_TRACKING: (
        "order",
        "track",
        "tracking",
        "package",
        "shipment",
        "shipping",
        "delivery",
        "delivered",
    ),
    Intent.RETURNS_EXCHANGE: (
        "return",
        "returns",
        "exchange",
        "refund",
        "damaged",
        "defective",
    ),
    Intent.PRODUCT_RECOMMENDATION: (
        "recommend",
        "recommendation",
        "suggest",
        "gear",
        "tent",
        "jacket",
        "boots",
        "camping",
        "hiking",
        "climbing",
        "waterproof",
    ),
}

INTENT_PRIORITY = (
    Intent.HUMAN_HANDOFF,
    Intent.ORDER_TRACKING,
    Intent.RETURNS_EXCHANGE,
    Intent.PRODUCT_RECOMMENDATION,
    Intent.GRATITUDE,
    Intent.MAIN_MENU,
)

TYPO_ALIASES: dict[str, tuple[Intent, str]] = {
    "thnak": (Intent.GRATITUDE, "thanks"),
    "thanx": (Intent.GRATITUDE, "thanks"),
}

FUZZY_MATCH_CUTOFF = 0.8


def normalize_message(message: str) -> str:
    normalized = message.lower().strip()
    normalized = re.sub(r"[^a-z0-9#'\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def tokenize(message: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[a-z0-9#']+", normalize_message(message)))


def _contains_order_number(tokens: tuple[str, ...]) -> bool:
    return any(re.fullmatch(r"#?\d{3}", token) for token in tokens)


def _exact_phrase_matches(message: str, intent: Intent) -> tuple[str, ...]:
    return tuple(phrase for phrase in INTENT_PHRASES.get(intent, ()) if phrase in message)


def _exact_keyword_matches(tokens: tuple[str, ...], intent: Intent) -> tuple[str, ...]:
    keywords = set(INTENT_KEYWORDS.get(intent, ()))
    return tuple(token for token in tokens if token in keywords)


def _fuzzy_keyword_matches(tokens: tuple[str, ...], intent: Intent) -> tuple[str, ...]:
    keywords = INTENT_KEYWORDS.get(intent, ())
    matches: list[str] = []

    for token in tokens:
        if len(token) < 4 or token.isdigit():
            continue
        close_matches = get_close_matches(token, keywords, n=1, cutoff=FUZZY_MATCH_CUTOFF)
        if close_matches:
            matches.append(close_matches[0])

    return tuple(dict.fromkeys(matches))


def _build_result(
    intent: Intent,
    normalized_message: str,
    match_strategy: MatchStrategy,
    matched_terms: tuple[str, ...] = (),
) -> IntentResult:
    return IntentResult(
        intent=intent,
        matched_terms=matched_terms,
        normalized_message=normalized_message,
        match_strategy=match_strategy,
        needs_review=match_strategy in {
            MatchStrategy.TYPO_ALIAS,
            MatchStrategy.FUZZY_KEYWORD,
            MatchStrategy.FALLBACK,
        },
    )


def detect_intent(message: str) -> IntentResult:
    normalized_message = normalize_message(message)
    tokens = tokenize(message)

    if not normalized_message:
        return _build_result(
            intent=Intent.FALLBACK,
            normalized_message=normalized_message,
            match_strategy=MatchStrategy.FALLBACK,
        )

    if _contains_order_number(tokens):
        return _build_result(
            intent=Intent.ORDER_TRACKING,
            normalized_message=normalized_message,
            match_strategy=MatchStrategy.ORDER_NUMBER,
            matched_terms=("order_number",),
        )

    for intent in INTENT_PRIORITY:
        phrase_matches = _exact_phrase_matches(normalized_message, intent)
        if phrase_matches:
            return _build_result(
                intent=intent,
                normalized_message=normalized_message,
                match_strategy=MatchStrategy.EXACT_PHRASE,
                matched_terms=phrase_matches,
            )

    for intent in INTENT_PRIORITY:
        keyword_matches = _exact_keyword_matches(tokens, intent)
        if keyword_matches:
            return _build_result(
                intent=intent,
                normalized_message=normalized_message,
                match_strategy=MatchStrategy.EXACT_KEYWORD,
                matched_terms=keyword_matches,
            )

    for token in tokens:
        typo_alias = TYPO_ALIASES.get(token)
        if typo_alias:
            intent, matched_term = typo_alias
            return _build_result(
                intent=intent,
                normalized_message=normalized_message,
                match_strategy=MatchStrategy.TYPO_ALIAS,
                matched_terms=(matched_term,),
            )

    for intent in INTENT_PRIORITY:
        fuzzy_matches = _fuzzy_keyword_matches(tokens, intent)
        if fuzzy_matches:
            return _build_result(
                intent=intent,
                normalized_message=normalized_message,
                match_strategy=MatchStrategy.FUZZY_KEYWORD,
                matched_terms=fuzzy_matches,
            )

    return _build_result(
        intent=Intent.FALLBACK,
        normalized_message=normalized_message,
        match_strategy=MatchStrategy.FALLBACK,
    )

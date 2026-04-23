"""
intent.py – Rule-based intent classifier.

Classifies user input into one of three categories:
  - greeting       : casual hello/hi messages
  - pricing        : questions about plans, cost, features, policies
  - high_intent    : user is ready or near-ready to sign up
  - general        : anything else (fallback)
"""

import re

# --- Keyword lists for each intent ---

GREETING_KEYWORDS = [
    "hi", "hello", "hey", "howdy", "good morning",
    "good afternoon", "good evening", "sup", "what's up",
    "greetings", "yo"
]

PRICING_KEYWORDS = [
    "price", "pricing", "plan", "plans", "cost", "costs",
    "how much", "fee", "fees", "subscription", "basic", "pro",
    "features", "feature", "resolution", "4k", "720p",
    "videos", "unlimited", "refund", "support", "policy",
    "policies", "cancel", "money back", "upgrade", "tier",
    "package", "what do i get", "what's included", "include"
]

HIGH_INTENT_KEYWORDS = [
    "sign up", "signup", "subscribe", "buy", "purchase",
    "get started", "start", "join", "try", "ready", "let's go",
    "i'll take", "i'm in", "count me in",
    "register", "enroll", "onboard"
]


def classify_intent(user_input: str) -> str:
    """
    Classify the user's message into an intent category.

    Args:
        user_input: Raw text from the user.

    Returns:
        One of: 'greeting', 'pricing', 'high_intent', 'general'
    """
    text = user_input.lower().strip()

    # Check high_intent first — it takes priority
    for kw in HIGH_INTENT_KEYWORDS:
        if kw in text:
            return "high_intent"

    # Precise greeting check
    # We use regex word boundaries to avoid matching "hi" inside "this"
    for kw in GREETING_KEYWORDS:
        if re.search(rf'\b{re.escape(kw)}\b', text):
            return "greeting"

    # Pricing / Product queries
    for kw in PRICING_KEYWORDS:
        if re.search(rf'\b{re.escape(kw)}\b', text):
            return "pricing"

    # General fallback
    return "general"

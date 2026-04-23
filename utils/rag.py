"""
rag.py – Lightweight keyword-based RAG (Retrieval-Augmented Generation).

No embeddings, no vector DB — just JSON keyword matching.
The knowledge base is loaded once at import time from knowledge.json.
"""

import json
import os

# --- Load the knowledge base ---
_KB_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge.json")

with open(_KB_PATH, "r") as f:
    KNOWLEDGE_BASE = json.load(f)


def retrieve(query: str) -> str:
    """
    Search the knowledge base for content relevant to the user's query.

    Strategy:
      1. Lower-case the query.
      2. Walk every section/entry in the knowledge base.
      3. Check if any of that entry's keywords appear in the query.
      4. Collect all matching descriptions and return a formatted response.

    Args:
        query: The user's message text.

    Returns:
        A human-readable string with all relevant knowledge, or a
        fallback message if nothing matched.
    """
    query_lower = query.lower()
    results = []

    # --- Pricing section ---
    for plan_key, plan in KNOWLEDGE_BASE.get("pricing", {}).items():
        if any(kw in query_lower for kw in plan.get("keywords", [])):
            # Build a clean description of the plan
            captions = "✅ AI Captions included" if plan["ai_captions"] else "❌ No AI Captions"
            results.append(
                f"📦 **{plan['name']}**\n"
                f"  • Price       : {plan['price']}\n"
                f"  • Videos      : {plan['videos']}\n"
                f"  • Resolution  : {plan['resolution']}\n"
                f"  • {captions}\n"
                f"  • Support     : {plan['support']}"
            )

    # If query mentions pricing/plan/cost in general, return ALL plans
    general_price_triggers = ["price", "pricing", "plan", "cost", "how much", "subscription", "package"]
    if not results and any(t in query_lower for t in general_price_triggers):
        for plan_key, plan in KNOWLEDGE_BASE.get("pricing", {}).items():
            captions = "✅ AI Captions" if plan["ai_captions"] else "❌ No AI Captions"
            results.append(
                f"📦 **{plan['name']}**\n"
                f"  • Price       : {plan['price']}\n"
                f"  • Videos      : {plan['videos']}\n"
                f"  • Resolution  : {plan['resolution']}\n"
                f"  • {captions}\n"
                f"  • Support     : {plan['support']}"
            )

    # --- Policies section ---
    for policy_key, policy in KNOWLEDGE_BASE.get("policies", {}).items():
        if any(kw in query_lower for kw in policy.get("keywords", [])):
            results.append(f"📋 **Policy – {policy_key.title()}**: {policy['description']}")

    # --- General / About section ---
    for info_key, info in KNOWLEDGE_BASE.get("general", {}).items():
        if any(kw in query_lower for kw in info.get("keywords", [])):
            results.append(f"ℹ️  {info['description']}")

    # --- Return aggregated results or fallback ---
    if results:
        return "\n\n".join(results)

    return None  # Caller will handle the None case with a fallback reply


def get_all_pricing() -> str:
    """Return a formatted summary of ALL pricing plans (used for generic pricing queries)."""
    lines = ["Here are our AutoStream plans:\n"]
    for plan_key, plan in KNOWLEDGE_BASE.get("pricing", {}).items():
        captions = "✅ AI Captions" if plan["ai_captions"] else "❌ No AI Captions"
        lines.append(
            f"📦 **{plan['name']}** – {plan['price']}\n"
            f"  • {plan['videos']} | {plan['resolution']} | {captions}\n"
            f"  • {plan['support']}"
        )
    return "\n\n".join(lines)

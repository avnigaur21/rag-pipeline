"""
state.py – Conversation state management.

Uses a plain Python dict as the single source of truth for the agent session.
Persists across all turns within a single CLI run.

State schema
------------
{
    "history"        : list[dict]   – full conversation turns {role, content}
    "intent"         : str | None   – last classified intent
    "collecting_lead": bool         – True when we're mid lead-collection flow
    "lead_data": {
        "name"    : str | None,
        "email"   : str | None,
        "platform": str | None,
    },
    "lead_captured"  : bool         – True after mock_lead_capture() is called
}
"""


def create_state() -> dict:
    """Initialise a fresh session state."""
    return {
        "history": [],
        "intent": None,
        "collecting_lead": False,
        "lead_data": {
            "name": None,
            "email": None,
            "platform": None,
        },
        "lead_captured": False,
    }


def add_turn(state: dict, role: str, content: str) -> None:
    """
    Append a conversation turn to history.

    Args:
        state  : Current session state (mutated in place).
        role   : 'user' or 'assistant'.
        content: The message text.
    """
    state["history"].append({"role": role, "content": content})


def get_history_text(state: dict, max_turns: int = 10) -> str:
    """
    Return the last `max_turns` turns as a formatted string.
    Useful for injecting into LLM prompts if needed.
    """
    recent = state["history"][-max_turns:]
    lines = []
    for turn in recent:
        prefix = "User" if turn["role"] == "user" else "Agent"
        lines.append(f"{prefix}: {turn['content']}")
    return "\n".join(lines)


def reset_lead_data(state: dict) -> None:
    """Clear lead fields (e.g. if the user wants to restart)."""
    state["lead_data"] = {"name": None, "email": None, "platform": None}
    state["collecting_lead"] = False
    state["lead_captured"] = False

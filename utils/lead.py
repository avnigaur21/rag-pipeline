"""
lead.py – Lead capture tool and collection logic.

The mock_lead_capture function is triggered ONLY after all three
required fields (name, email, platform) have been collected from the user.
"""

import re


# ── Mock API (as specified in the assignment) ──────────────────────────────────

def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """
    Simulate a CRM / backend lead submission.

    In a real system this would POST to a CRM like HubSpot, Salesforce, etc.
    For this assignment it prints confirmation and returns a success message.
    """
    print(f"Lead captured successfully: {name}, {email}, {platform}")
    return (
        f"🎉 You're all set, {name}! We've captured your details and a member of our "
        f"team will reach out to your {platform} creator account at {email} shortly.\n"
        f"Welcome to AutoStream Pro!"
    )


# ── Validation helpers ─────────────────────────────────────────────────────────

def is_valid_email(text: str) -> bool:
    """Basic email format check."""
    pattern = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, text.strip()))


KNOWN_PLATFORMS = [
    "youtube", "instagram", "tiktok", "twitter", "x",
    "facebook", "twitch", "linkedin", "snapchat", "pinterest"
]

def is_valid_platform(text: str) -> bool:
    """Check if the input looks like a known creator platform."""
    return any(p in text.lower() for p in KNOWN_PLATFORMS)


# ── Sequential field collection ────────────────────────────────────────────────

def get_next_lead_prompt(lead_data: dict) -> str | None:
    """
    Given the currently collected lead data, return the next question to ask,
    or None if all fields have been collected.

    Args:
        lead_data: dict with keys 'name', 'email', 'platform' (may be None).

    Returns:
        A prompt string for the missing field, or None if complete.
    """
    if not lead_data.get("name"):
        return "Great! I'd love to get you started. What's your name?"

    if not lead_data.get("email"):
        return f"Nice to meet you, {lead_data['name']}! What's your email address?"

    if not lead_data.get("platform"):
        return (
            f"Almost there! Which creator platform do you primarily use? "
            f"(e.g. YouTube, Instagram, TikTok...)"
        )

    # All fields collected
    return None


def try_collect_field(user_input: str, lead_data: dict) -> tuple[dict, str | None]:
    """
    Attempt to fill the next missing lead field from the user's input.

    Returns:
        (updated_lead_data, error_message_or_None)
        If there's a validation error, the field is NOT saved and an error
        message is returned so the agent can re-ask.
    """
    text = user_input.strip()

    if not lead_data.get("name"):
        # Ensure the name is reasonably long and contains letters
        if len(text) < 2 or not any(c.isalpha() for c in text):
            return lead_data, "I didn't quite catch your name. Could you please tell me your name?"
        lead_data["name"] = text.title()
        return lead_data, None

    if not lead_data.get("email"):
        if not is_valid_email(text):
            return lead_data, "That doesn't look like a valid email. Please enter a valid email address (e.g. you@example.com)."
        lead_data["email"] = text.lower()
        return lead_data, None

    if not lead_data.get("platform"):
        # Accept any platform name; warn but still accept unknown platforms
        if len(text) < 1:
             return lead_data, "Please tell me which platform you use (e.g. YouTube, Instagram)."
        lead_data["platform"] = text.title()
        return lead_data, None

    return lead_data, None


def is_lead_complete(lead_data: dict) -> bool:
    """Return True only when all three required fields are present."""
    return bool(lead_data.get("name") and lead_data.get("email") and lead_data.get("platform"))

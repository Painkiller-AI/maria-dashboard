from typing import Any, Dict


def get_user_name(user: Dict[str, Any] | None) -> str | None:
    """
    Get full name from user dict (bot and human_users)
    """
    if not user:
        return None

    if "name" in user:
        return user["name"].strip()

    first_name = user.get("first_name", "").strip()
    last_name = user.get("last_name", "").strip()

    if first_name and last_name:
        return f"{first_name} {last_name}".strip()

    return None

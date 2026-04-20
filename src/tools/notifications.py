import os
from typing import Optional
import httpx


def _clean(s: str) -> str:
    """Strip newlines from header values to prevent injection."""
    return s.replace("\r", "").replace("\n", " ")


NTFY_BASE_URL = os.getenv("NTFY_URL") or "https://ntfy.sh"
NTFY_TOKEN = os.getenv("NTFY_TOKEN") or ""
DEFAULT_TOPIC = os.getenv("NTFY_DEFAULT_TOPIC") or "claudebox"

VALID_PRIORITIES = {"min", "low", "default", "high", "urgent", "max", "1", "2", "3", "4", "5"}


def _build_headers(
    title: Optional[str],
    priority: Optional[str],
    tags: Optional[list[str]],
    markdown: bool,
    click: Optional[str],
    icon: Optional[str],
) -> dict[str, str]:
    headers: dict[str, str] = {}

    if NTFY_TOKEN:
        headers["Authorization"] = f"Bearer {NTFY_TOKEN}"

    if title:
        headers["X-Title"] = _clean(title)

    if priority:
        p = priority.lower()
        if p not in VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority '{priority}'. Valid values: min, low, default, high, urgent/max"
            )
        headers["X-Priority"] = p

    if tags:
        headers["X-Tags"] = ",".join(_clean(t) for t in tags)

    if markdown:
        headers["X-Markdown"] = "true"

    if click:
        headers["X-Click"] = _clean(click)

    if icon:
        headers["X-Icon"] = _clean(icon)

    return headers


async def send_notification_handler(
    message: str,
    topic: Optional[str],
    title: Optional[str],
    priority: Optional[str],
    tags: Optional[list[str]],
    markdown: bool,
    click: Optional[str],
    icon: Optional[str],
) -> dict:
    resolved_topic = topic or DEFAULT_TOPIC
    if "/" in resolved_topic or ".." in resolved_topic:
        return {"ok": False, "error": "Invalid topic: must not contain '/' or '..'"}
    url = f"{NTFY_BASE_URL.rstrip('/')}/{resolved_topic}"

    try:
        headers = _build_headers(title, priority, tags, markdown, click, icon)
    except ValueError as e:
        return {"ok": False, "error": str(e)}

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, content=message.encode("utf-8"), headers=headers)

    if resp.status_code in (200, 204):
        return {"ok": True, "topic": resolved_topic, "status": resp.status_code}
    else:
        return {
            "ok": False,
            "topic": resolved_topic,
            "status": resp.status_code,
            "error": resp.text[:200],
        }

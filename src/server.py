import os
from typing import Optional

from fastmcp import FastMCP
from src.tools.notifications import send_notification_handler


mcp = FastMCP("ntfy-mcp")


@mcp.tool()
async def send_notification(
    message: str,
    topic: Optional[str] = None,
    title: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None,
    markdown: bool = False,
    click: Optional[str] = None,
    icon: Optional[str] = None,
) -> dict:
    """Send a push notification via ntfy.

    Sends to the default topic (claudebox) unless overridden. Tags support emoji
    short codes (e.g. 'white_check_mark', 'warning', 'rotating_light').

    Args:
        message: Notification body. Supports Markdown if markdown=True.
        topic: ntfy topic to publish to. Defaults to the NTFY_DEFAULT_TOPIC env var (claudebox).
        title: Optional notification title shown in bold above the message.
        priority: min | low | default | high | urgent (alias: max). Defaults to ntfy default.
        tags: List of tag strings or emoji short codes, e.g. ['white_check_mark', 'claudebox'].
        markdown: Enable Markdown rendering in the notification body.
        click: URL to open when the notification is tapped.
        icon: URL of an icon image to display with the notification.
    """
    return await send_notification_handler(
        message=message,
        topic=topic,
        title=title,
        priority=priority,
        tags=tags,
        markdown=markdown,
        click=click,
        icon=icon,
    )


if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", "8484"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port)

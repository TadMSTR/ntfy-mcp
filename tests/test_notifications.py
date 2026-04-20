import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.tools.notifications import send_notification_handler, _build_headers


# --- _build_headers unit tests ---

def test_build_headers_minimal():
    headers = _build_headers(None, None, None, False, None, None)
    assert "X-Title" not in headers
    assert "X-Priority" not in headers
    assert "X-Tags" not in headers
    assert "X-Markdown" not in headers


def test_build_headers_full():
    headers = _build_headers(
        title="Alert",
        priority="high",
        tags=["warning", "claudebox"],
        markdown=True,
        click="https://example.com",
        icon="https://example.com/icon.png",
    )
    assert headers["X-Title"] == "Alert"
    assert headers["X-Priority"] == "high"
    assert headers["X-Tags"] == "warning,claudebox"
    assert headers["X-Markdown"] == "true"
    assert headers["X-Click"] == "https://example.com"
    assert headers["X-Icon"] == "https://example.com/icon.png"


def test_build_headers_invalid_priority():
    with pytest.raises(ValueError, match="Invalid priority"):
        _build_headers(None, "critical", None, False, None, None)


def test_build_headers_priority_aliases():
    for p in ("urgent", "max", "5"):
        headers = _build_headers(None, p, None, False, None, None)
        assert headers["X-Priority"] == p.lower()


def test_build_headers_bearer_token(monkeypatch):
    monkeypatch.setenv("NTFY_TOKEN", "tk_test123")
    import importlib
    import src.tools.notifications as mod
    importlib.reload(mod)
    headers = mod._build_headers(None, None, None, False, None, None)
    assert headers.get("Authorization") == "Bearer tk_test123"


# --- send_notification_handler integration tests (mocked HTTP) ---

@pytest.mark.asyncio
async def test_send_notification_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = ""

    with patch("src.tools.notifications.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await send_notification_handler(
            message="test message",
            topic="claudebox",
            title="Test",
            priority=None,
            tags=None,
            markdown=False,
            click=None,
            icon=None,
        )

    assert result["ok"] is True
    assert result["topic"] == "claudebox"
    assert result["status"] == 200


@pytest.mark.asyncio
async def test_send_notification_uses_default_topic():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = ""

    with patch("src.tools.notifications.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await send_notification_handler(
            message="hello",
            topic=None,
            title=None,
            priority=None,
            tags=None,
            markdown=False,
            click=None,
            icon=None,
        )

    assert result["ok"] is True
    assert result["topic"] == "claudebox"


@pytest.mark.asyncio
async def test_send_notification_server_error():
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"

    with patch("src.tools.notifications.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_client

        result = await send_notification_handler(
            message="test",
            topic=None,
            title=None,
            priority=None,
            tags=None,
            markdown=False,
            click=None,
            icon=None,
        )

    assert result["ok"] is False
    assert result["status"] == 403
    assert "Forbidden" in result["error"]


@pytest.mark.asyncio
async def test_send_notification_invalid_priority():
    result = await send_notification_handler(
        message="test",
        topic=None,
        title=None,
        priority="critical",
        tags=None,
        markdown=False,
        click=None,
        icon=None,
    )
    assert result["ok"] is False
    assert "priority" in result["error"].lower()


@pytest.mark.asyncio
async def test_send_notification_rejects_path_traversal_topic():
    result = await send_notification_handler(
        message="test",
        topic="../admin",
        title=None,
        priority=None,
        tags=None,
        markdown=False,
        click=None,
        icon=None,
    )
    assert result["ok"] is False
    assert "Invalid topic" in result["error"]


@pytest.mark.asyncio
async def test_rejects_url_encoded_slash():
    result = await send_notification_handler(
        message="t",
        topic="a%2Fb",
        title=None,
        priority=None,
        tags=None,
        markdown=False,
        click=None,
        icon=None,
    )
    assert result["ok"] is False
    assert "Invalid topic" in result["error"]


@pytest.mark.asyncio
async def test_rejects_url_encoded_dotdot():
    result = await send_notification_handler(
        message="t",
        topic="%2E%2E",
        title=None,
        priority=None,
        tags=None,
        markdown=False,
        click=None,
        icon=None,
    )
    assert result["ok"] is False
    assert "Invalid topic" in result["error"]

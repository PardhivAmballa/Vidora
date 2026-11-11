import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.server import handle_call_tool, handle_list_tools


def test_list_tools_exposes_current_stage_1_capabilities():
    """The Stage 1 server surface should expose the known MVP tools."""
    tools = asyncio.run(handle_list_tools())

    assert [tool.name for tool in tools] == [
        "get_similar_videos",
        "create_constrained_playlist",
    ]

    tool_map = {tool.name: tool for tool in tools}
    assert tool_map["get_similar_videos"].input_schema["required"] == ["video_id"]
    assert tool_map["create_constrained_playlist"].input_schema["required"] == [
        "topic",
        "total_duration_minutes",
    ]


def test_get_similar_videos_accepts_video_id_and_returns_stub_result():
    """Current implementation supports the staged stub contract for FR-1."""
    response = asyncio.run(
        handle_call_tool("get_similar_videos", {"video_id": "dQw4w9WgXcQ"})
    )

    assert len(response) == 1
    assert "FR-1" in response[0].text
    assert "dQw4w9WgXcQ" in response[0].text


def test_create_constrained_playlist_requires_topic_before_writing():
    """The playlist workflow must require a topic before generating a proposal."""
    with pytest.raises(ValueError, match="Missing required parameter: topic"):
        asyncio.run(handle_call_tool("create_constrained_playlist", {"total_duration_minutes": 60}))


def test_create_constrained_playlist_returns_confirmation_required_stub():
    """Current Stage 1 implementation should show a proposal and wait for explicit user confirmation."""
    response = asyncio.run(
        handle_call_tool(
            "create_constrained_playlist",
            {"topic": "Python basics", "total_duration_minutes": 60},
        )
    )

    assert len(response) == 1
    assert "Python basics" in response[0].text
    assert "Awaiting explicit user confirmation" in response[0].text


def test_unknown_tool_raises_clear_error():
    """Unknown tool calls should fail with a clear, explicit validation error."""
    with pytest.raises(ValueError, match="Unknown tool requested"):
        asyncio.run(handle_call_tool("not_a_real_tool", {"sample": "value"}))
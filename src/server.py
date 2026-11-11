"""
Core Model Context Protocol (MCP) Server implementation for Vidora.
Handles server lifecycle, tool routing, and input validation middleware.
"""

import sys
import logging
from typing import Any, Dict

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

# Configure logging securely (excluding sensitive data per NFR-SEC-8)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("vidora-mcp-server")


def _tool_result(text: str) -> types.CallToolResult:
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=text)],
        isError=False,
    )


async def handle_list_tools() -> list[types.Tool]:
    """Expose available Vidora tools to the connected MCP client."""
    return [
        types.Tool(
            name="get_similar_videos",
            description="Compute and return a ranked list of similar videos using metadata feature vectors (FR-1).",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_id": {"type": "string", "description": "YouTube video ID or URL"}
                },
                "required": ["video_id"],
            },
        ),
        types.Tool(
            name="create_constrained_playlist",
            description="Curate and create an educational playlist based on topic, duration, and constraints (FR-5).",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Subject or topic for the playlist"},
                    "total_duration_minutes": {"type": "integer", "description": "Maximum total duration budget"},
                    "max_video_length_minutes": {"type": "integer", "description": "Maximum length per video"},
                },
                "required": ["topic", "total_duration_minutes"],
            },
        ),
    ]


async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> list[types.TextContent]:
    """Handle tool execution requests with server-side validation (NFR-SEC-5)."""
    logger.info(f"Received tool execution request: {name}")

    if not arguments:
        raise ValueError("Invalid arguments: Tool arguments cannot be empty.")

    if name == "get_similar_videos":
        video_id = arguments.get("video_id")
        if not video_id:
            raise ValueError("Missing required parameter: video_id")

        return [
            types.TextContent(
                type="text",
                text=f"Executing FR-1 similar video discovery for target identifier: {video_id}",
            )
        ]

    if name == "create_constrained_playlist":
        topic = arguments.get("topic")
        if not topic:
            raise ValueError("Missing required parameter: topic")

        return [
            types.TextContent(
                type="text",
                text=f"Generated playlist proposal for topic '{topic}'. Awaiting explicit user confirmation.",
            )
        ]

    raise ValueError(f"Unknown tool requested: {name}")


async def _list_tools_handler(context, params=None):
    return types.ListToolsResult(tools=await handle_list_tools())


async def _call_tool_handler(context, params):
    result = await handle_call_tool(params.name, params.arguments or {})
    return types.CallToolResult(content=result, isError=False)


# Initialize the MCP Server instance
app = Server(
    "vidora-youtube-intelligence",
    on_list_tools=_list_tools_handler,
    on_call_tool=_call_tool_handler,
)


async def main():
    """Run the MCP server using standard input/output transport."""
    logger.info("Starting Vidora MCP Server via stdio transport...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
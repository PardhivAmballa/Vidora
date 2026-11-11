# ADR-01: MCP Transport and Server Framework Selection

## Status
Approved / Implemented

## Context
Vidora requires a robust, standardized protocol layer to bridge conversational AI clients (such as Claude or Gemini) with backend YouTube integration tools. As analyzed in [[mcp-protocol-architecture]], the Model Context Protocol (MCP) provides standard schemas for tools, resources, and server-client lifecycles. We needed to choose a Python framework implementation and communication transport that satisfies local execution requirements while integrating seamlessly with CI environments and standard input/output streams.

## Decision
1. **Framework:** We selected the official Python `mcp` SDK to implement the server backend (`src/server.py`).
2. **Transport:** We implemented standard input/output (`stdio`) transport for local client communication (`src/server.py`), ensuring secure, isolated message passing between the AI client process and the backend server without exposing raw network sockets locally.

## Consequences
* **Positive:** Standardized tool discovery and schema validation out of the box; eliminates custom socket boilerplate; directly complies with standard MCP client configurations.
* **Negative:** Requires local process execution management by the connected AI client application.
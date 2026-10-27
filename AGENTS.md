# Agent Guidelines for YouTube MCP Server (Python)

## Overview
This repository contains the Python backend implementation for the YouTube Video Intelligence Model Context Protocol (MCP) Server. All AI-assisted development must adhere to the shared AI-Assisted SDLC guidelines.

## Core Rules for Agents
1. **Official API Only:** Strictly integrate with the official YouTube Data API v3. Scraping or unofficial APIs are prohibited.
2. **Second Brain Traceability:** All architectural decisions and skills must cite notes from the `brain/` vault using `[[wikilinks]]`.
3. **No Secrets in Code:** Never commit API keys, OAuth tokens, or client secrets. Use environment variables.
4. **Agent Skills Format:** All custom agent skills must reside in `skills/<skill-name>/SKILL.md` following the standard agent skills specification.
5. **Human Review:** Every AI-generated change must go through a pull request with explicit human review.
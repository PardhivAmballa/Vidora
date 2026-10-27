# Software Requirements Specification (SRS): YouTube Video Intelligence MCP Server

## 1. Introduction
The YouTube Video Intelligence MCP Server bridges conversational AI clients with the YouTube Data API v3. It enables users to bypass engagement-driven algorithmic noise and curate distraction-free educational playlists based on objective metadata and strict time constraints.

## 2. Functional Requirements (FR)
- **FR-1 (Similar Videos):** Given a video URL or ID, the system shall compute and return a ranked list of similar videos using metadata feature vectors and cosine similarity.
- **FR-2 (Similar Channels):** Given a channel URL, handle, or ID, the system shall return a ranked list of similar channels based on channel metadata.
- **FR-3 (Recommendations):** The system shall recommend videos based on the authorized user's liked videos, subscriptions, and playlists.
- **FR-4 (Engagement Analysis):** The system shall analyze the user's liked videos, subscriptions, and playlists, reporting top channels, categories, trends over time, duration preferences, and period comparisons.
- **FR-5 (Playlist Creation):** The system shall accept natural-language requests with explicit constraints (topic, total duration, max video length, language), build a complying playlist, present it to the user for explicit confirmation, and automatically create it in the user's YouTube account.

## 3. Non-Functional Requirements (NFR)
- **NFR-1 (Quota Management):** The system shall track API quota costs per request and reject workflows exceeding the remaining daily budget (default 10,000 units/day) prior to executing API calls.
- **NFR-2 (Testing & CI Isolation):** CI test suites shall run exclusively against recorded fixtures or mocks, preserving live API quotas.
- **NFR-3 (Security & OAuth):** OAuth implementation shall request minimum necessary scopes, store tokens securely, and gracefully handle 7-day test-mode refresh token expirations and missing YouTube channel conditions.

## 4. Skill Requirements (SK)
- **SK-1 (`video-to-playlist`):** The system shall expose a product-specific agent skill that executes a 5-step workflow: (1) Summarize a given video, (2) Find similar videos via FR-1, (3) Propose a playlist and request user confirmation, (4) Create the playlist via FR-5, and (5) Display post-creation analytics.
- **SK-2 (`brain-ingest`):** The system shall support ingesting and structuring new research notes into the Obsidian Second Brain.
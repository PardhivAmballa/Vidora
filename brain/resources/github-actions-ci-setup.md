---
title: GitHub Actions CI for the YouTube MCP Server
tags: [github-actions, ci, pytest, lint, security, SDLC]
status: research
---

# GitHub Actions CI Setup

## Purpose

CI should provide repeatable evidence that each PR builds, passes linting, contains no accidental secrets, validates agent skills and brain notes, and passes offline tests. The supplied repository has `.github/workflows/ci.yml` with checkout, Python setup, pip caching, dependency installation, placeholder security output, and pytest. Evolve it into enforceable checks.

The SDLC brief requires build, lint, tests, secret scanning, `SKILL.md` frontmatter/naming validation, and brain-note schema/broken-link validation on PRs. AI-generated changes still require human review. See [[para-knowledge-management]] and [[adr-governance-workflow]].

## Job design

Use separate jobs for quality, tests, security, docs, and optional live API checks. Pin actions to reviewed versions or immutable SHAs according to team policy. Grant minimal `GITHUB_TOKEN` permissions. Do not expose secrets to fork pull requests.

## Example workflow

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
          cache-dependency-path: requirements.txt
      - name: Install
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install ruff pytest-cov pyyaml
      - name: Lint
        run: ruff check .
      - name: Validate skills and brain notes
        run: python scripts/validate_docs.py
      - name: Test offline suite
        env:
          YOUTUBE_MCP_TEST_MODE: "1"
        run: pytest tests/ --cov=src --cov-report=term-missing
```

Adjust Python versions, package layout, and test paths to the actual repository. If the project has no `src/` package, do not keep an invalid coverage target.

## Dependencies and caching

`setup-python` can cache pip downloads keyed from requirements. Pin dependencies and use a lock or constraints file for reproducible builds. Broad lower bounds such as `mcp>=1.0.0` can pull incompatible future versions; upgrade intentionally and rerun protocol tests. Cache packages, never credentials or token files.

## Secret scanning

Replace placeholder `echo` commands with Gitleaks or an approved scanner. Also establish policy: no client-secret JSON, `.env`, token files, or real user data in fixtures. Rotate any accidentally committed credential; deleting it in a later commit does not remove it from Git history. A scanner is a detection layer, not permission to commit secrets it misses.

## SKILL.md validation

Validate required YAML frontmatter fields (`name`, `description`), naming rules, and duplicate names against the selected Agent Skills specification.

```python
from pathlib import Path
import yaml

seen = set()
for path in Path("skills").glob("*/SKILL.md"):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"{path}: missing YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise SystemExit(f"{path}: malformed frontmatter")
    data = yaml.safe_load(parts[1]) or {}
    for field in ("name", "description"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise SystemExit(f"{path}: missing {field}")
    if data["name"] != path.parent.name:
        raise SystemExit(f"{path}: name must match directory")
    if data["name"] in seen:
        raise SystemExit(f"{path}: duplicate skill name")
    seen.add(data["name"])
```

A production validator should report YAML parse locations and enforce the official specification rather than inventing conflicting rules.

## Brain-note validation

Check frontmatter, Markdown encoding, requirement IDs, broken wikilinks, and accidental secrets/personal data. Obsidian aliases and subpaths make naive regex validation fragile; use a parser if the vault grows. Normalise `.md` extensions and case rules consistently.

## Offline guarantee

Inject a fixture provider, mock network boundaries, and fail tests if the production provider is constructed without a live-test marker. Keep live API checks in a separate scheduled/manual workflow with credentials and a fixed quota budget. Never run live calls for every PR.

## PR governance

Require passing status checks and at least one human review. Code, skills, brain notes, and ADRs all go through PRs. Significant defects need regression tests; stage review notes should record what worked, failed, and changes next.

## Related notes

- [[sqlite-fixture-caching]]
- [[para-knowledge-management]]
- [[adr-governance-workflow]]

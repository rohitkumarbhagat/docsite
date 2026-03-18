---
name: data-commons-dev
description: Standalone Data Commons developer documentation skill. Use when answering developer questions about Data Commons concepts, REST or Python APIs, Google Sheets or Web Components integrations, BigQuery, MCP, or Custom Data Commons setup and operations. Use only the bundled references inside this skill at runtime; do not depend on sibling docsite files or external paths.
---

# Data Commons Dev

## Overview

Use this skill to answer Data Commons developer questions from the bundled documentation snapshot in `references/raw/`. Start with `references/scenario-index.md`, route to the right scenario, and then read only the relevant bundled pages.

## Workflow

1. Open `references/scenario-index.md` and choose the closest scenario before reading any raw docs.
2. Read only the bundled files listed for that scenario under `references/raw/`.
3. Prefer current docs by default:
   - REST V2 before older REST patterns
   - Python V2 before Python V1 unless the user explicitly asks for legacy behavior
4. Keep base-product guidance separate from `custom_dc` guidance unless the user explicitly asks for a comparison.
5. If `references/scenario-guide.md` exists, treat it as supplemental navigation only. `references/scenario-index.md` is the authoritative routing file.
6. Cite the exact bundled reference paths you used in the answer.

## Scenario Routing

- `Core Concepts`: shared concepts such as DCIDs, places, statistical variables, observations, and provenance
- `API Clients and Integrations`: REST, Python, Sheets, and Web Components
- `BigQuery`: SQL access patterns and joins
- `MCP`: hosted or self-hosted MCP guidance for base Data Commons
- `Custom Data Commons`: setup, configuration, deployment, MCP, and operational guidance for custom instances

## Working Rules

- Answer from bundled references, not memory.
- Ignore missing screenshots or broken asset links unless the user specifically asks about visuals.
- Do not use datasets coverage pages, courseware, blog posts, or maintainer docs for ordinary developer questions.
- When the bundled docs are silent or contradictory, say so explicitly and mark any conclusion as an inference.

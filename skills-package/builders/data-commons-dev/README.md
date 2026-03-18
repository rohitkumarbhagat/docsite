# Data Commons Dev Builder

This directory contains the deterministic packaging machinery for the standalone
`data-commons-dev` skill. It is maintainer-only content; the actual runtime
skill lives at:

`skills-package/skills/data-commons-dev/`

## Contents

- `update_snapshot.py`: sync tool that copies the selected docsite pages into
  the runtime skill and regenerates the deterministic routing index
- `manifest.json`: authoritative list of included source docs and scenario tags
- `sources.lock.json`: generated hash file that records the current packaged
  snapshot

## Update Flow

Run from the repo root:

```bash
python3 skills-package/builders/data-commons-dev/update_snapshot.py
```

Default behavior:

- reads source docs from this docsite repo
- reads builder inputs from this directory
- writes runtime outputs into `skills-package/skills/data-commons-dev/`
- copies raw docs verbatim into `references/raw/`
- regenerates `references/scenario-index.md`
- updates `sources.lock.json` only when packaged content changes

The tool is deterministic:

- fixed manifest order
- stable output paths
- no timestamps or random identifiers
- unchanged output files are left byte-for-byte intact

## Markdown Handling

The builder does not convert Kramdown/Jekyll Markdown in v1. It copies the
selected source files verbatim to preserve stability and avoid churn.

Accepted as-is:

- YAML frontmatter
- Kramdown attribute lists such as `{:toc}`
- Liquid snippets
- Jekyll-style image and link syntax

If a specific syntax later proves harmful for skill consumers, add a
deterministic normalization step here rather than hand-editing packaged docs.

# `llms.txt` guardrails

`llms.txt` is manually maintained. Do not auto-generate it.

The guardrail checker exists to catch structural drift, not to rewrite or
reorganize the file. It validates raw repo doc links and coverage only.

## Local command

Run the checker locally with:

```sh
ruby scripts/check_llms_txt.rb
```

## What the checker validates

- every eligible docs page is represented somewhere in `llms.txt`
- every raw repo docs URL in `llms.txt` points to a real page
- excluded or forbidden pages are not linked
- `llms:` front matter uses only supported values

The checker does not validate:

- displayed labels
- section/group organization
- note wording
- content churn inside linked pages

## Page-level control

Use page front matter for page-specific participation:

```yaml
llms: ignore
```

This forbids the page from appearing in `llms.txt`.

```yaml
llms: include
```

This forces the page to be considered for coverage even if its folder is
centrally ignored.

Supported values are only:

- `ignore`
- `include`

Any other `llms:` value fails the checker.

## Folder-level control

Folder-level defaults live in [`llms_guardrails.yml`](./llms_guardrails.yml).

Example:

```yaml
ignored_files:
  - AGENTS.md

excluded_prefixes:
  - scripts/

ignored_prefixes:
  - courseware/
  - papers/
```

Pages under an ignored prefix are forbidden from appearing in `llms.txt` unless
they explicitly set `llms: include`.

Use `ignored_files` and `excluded_prefixes` for repo paths that should be
outside llms checking entirely. Use `ignored_prefixes` only for docs areas that
should remain valid docs pages but be forbidden from appearing in `llms.txt`.

## Precedence

The checker applies these rules in order:

1. hard exclusions always win
2. `llms: include` overrides folder ignore
3. `llms: ignore` forbids linking
4. `ignored_prefixes` forbids linking
5. everything else is eligible and must be represented

## Hard exclusions

The checker always excludes:

- paths listed in `ignored_files`
- paths under `excluded_prefixes`
- paths with `_...` segments or filenames starting with `_`
- files with `layout: redirect`
- files with `layout: code-preview`
- files with `published: false`
- empty files

## Coverage rules

Only raw repo Markdown URLs of this form count for coverage:

```text
https://raw.githubusercontent.com/datacommonsorg/docsite/master/<path>.md
```

Custom labels, duplicate links, and manual section organization are allowed.

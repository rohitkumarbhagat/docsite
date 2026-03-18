#!/usr/bin/env python3
"""Synchronize the standalone Data Commons developer skill snapshot."""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Update the standalone Data Commons developer skill snapshot.",
    )
    parser.add_argument(
        "--builder-root",
        help="Path to the builder root. Defaults to the parent of this script.",
    )
    parser.add_argument(
        "--skill-root",
        help="Path to the runtime skill root. Defaults to skills-package/skills/<skill-name>.",
    )
    parser.add_argument(
        "--source-root",
        help="Path to the docsite source root. Defaults to the repo root.",
    )
    parser.add_argument(
        "--manifest",
        help="Path to the manifest JSON. Defaults to <builder-root>/manifest.json.",
    )
    parser.add_argument(
        "--agentic-index",
        action="store_true",
        help="Regenerate references/scenario-guide.md using an external command after the deterministic sync.",
    )
    parser.add_argument(
        "--agentic-command",
        help=(
            "Shell command that writes the agentic scenario guide to stdout. "
            "If omitted, DATA_COMMONS_DEV_AGENTIC_INDEX_COMMAND is used."
        ),
    )
    return parser.parse_args()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def read_text(path):
    return path.read_text(encoding="utf-8")


def parse_title(text, fallback):
    frontmatter = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if frontmatter:
        title_match = re.search(r"(?m)^title:\s*(.+?)\s*$", frontmatter.group(1))
        if title_match:
            return title_match.group(1).strip().strip('"').strip("'")
    heading_match = re.search(r"(?m)^#\s+(.+?)\s*$", text)
    if heading_match:
        return heading_match.group(1).strip()
    return fallback


def write_bytes_if_changed(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == data:
        return "unchanged"
    path.write_bytes(data)
    return "updated" if path.exists() else "created"


def write_text_if_changed(path, text):
    data = text.encode("utf-8")
    existed = path.exists()
    status = write_bytes_if_changed(path, data)
    if status == "updated" and not existed:
        return "created"
    return status


def remove_empty_dirs(root):
    for directory, _, _ in os.walk(root, topdown=False):
        path = Path(directory)
        if path == root:
            continue
        try:
            path.rmdir()
        except OSError:
            pass


def load_manifest(path):
    manifest = json.loads(read_text(path))
    if manifest.get("version") != 1:
        raise ValueError("manifest.json version must be 1")
    scenarios = manifest.get("scenarios", [])
    entries = manifest.get("entries", [])
    if not scenarios or not entries:
        raise ValueError("manifest.json must define scenarios and entries")

    scenario_ids = [item["id"] for item in scenarios]
    if len(scenario_ids) != len(set(scenario_ids)):
        raise ValueError("scenario ids must be unique")

    seen_dest = set()
    seen_source = set()
    for entry in entries:
        scenario = entry["scenario"]
        source = entry["source"]
        dest = entry["dest"]
        if scenario not in scenario_ids:
            raise ValueError(f"unknown scenario '{scenario}' in manifest entry")
        if source in seen_source:
            raise ValueError(f"duplicate source '{source}' in manifest entry")
        if dest in seen_dest:
            raise ValueError(f"duplicate dest '{dest}' in manifest entry")
        seen_source.add(source)
        seen_dest.add(dest)
    return manifest


def build_scenario_index(manifest, entry_rows):
    scenario_order = {item["id"]: index for index, item in enumerate(manifest["scenarios"])}
    rows_by_scenario = {item["id"]: [] for item in manifest["scenarios"]}
    for row in sorted(entry_rows, key=lambda item: (scenario_order[item["scenario"]], item["dest"])):
        rows_by_scenario[row["scenario"]].append(row)

    lines = [
        "# Scenario Index",
        "",
        "This file is generated deterministically by the builder sync tool.",
        "Use it as the authoritative routing map for the skill. If `scenario-guide.md` exists, treat it as supplemental only.",
        "",
    ]
    for scenario in manifest["scenarios"]:
        rows = rows_by_scenario[scenario["id"]]
        lines.append(f"## {scenario['title']} ({len(rows)} docs)")
        lines.append("")
        lines.append(scenario["description"])
        lines.append("")
        lines.append(f"Routing note: {scenario['routing_note']}")
        lines.append("")
        for row in rows:
            lines.append(f"- [{row['title']}](raw/{row['dest']})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def sync_snapshot(builder_root, skill_root, source_root, manifest_path):
    manifest = load_manifest(manifest_path)
    raw_root = skill_root / manifest["raw_root"]
    authoritative_index = skill_root / manifest["authoritative_index"]
    lock_path = builder_root / "sources.lock.json"

    expected_raw = set()
    entry_rows = []
    stats = {"created": 0, "updated": 0, "unchanged": 0, "removed": 0}

    for entry in manifest["entries"]:
        source_path = source_root / entry["source"]
        if not source_path.exists():
            raise FileNotFoundError(f"source file not found: {source_path}")
        if not source_path.is_file():
            raise FileNotFoundError(f"source path is not a file: {source_path}")

        dest_path = raw_root / entry["dest"]
        data = source_path.read_bytes()
        existed = dest_path.exists()
        status = write_bytes_if_changed(dest_path, data)
        if status == "updated" and not existed:
            status = "created"
        stats[status] += 1

        text = data.decode("utf-8")
        title = entry.get("title") or parse_title(text, entry["dest"])
        rel_dest = dest_path.relative_to(skill_root).as_posix()
        expected_raw.add(dest_path.resolve())
        entry_rows.append(
            {
                "scenario": entry["scenario"],
                "source": entry["source"],
                "dest": entry["dest"],
                "raw_path": rel_dest,
                "title": title,
                "sha256": sha256_bytes(data),
            }
        )

    if raw_root.exists():
        for path in sorted(raw_root.rglob("*")):
            if path.is_file() and path.resolve() not in expected_raw:
                path.unlink()
                stats["removed"] += 1
        remove_empty_dirs(raw_root)

    index_status = write_text_if_changed(authoritative_index, build_scenario_index(manifest, entry_rows))

    lock = {
        "version": 1,
        "skill_name": manifest["skill_name"],
        "raw_root": manifest["raw_root"],
        "authoritative_index": manifest["authoritative_index"],
        "entries": sorted(
            [
                {
                    "scenario": row["scenario"],
                    "source": row["source"],
                    "dest": row["raw_path"],
                    "title": row["title"],
                    "sha256": row["sha256"],
                }
                for row in entry_rows
            ],
            key=lambda item: item["dest"],
        ),
    }
    lock_status = write_text_if_changed(lock_path, json.dumps(lock, indent=2) + "\n")
    return manifest, stats, index_status, lock_status


def run_agentic_index(builder_root, skill_root, manifest, manifest_path, command):
    guide_path = skill_root / manifest["agentic_index"]
    scenario_index_path = skill_root / manifest["authoritative_index"]
    env = os.environ.copy()
    env["DATA_COMMONS_DEV_BUILDER_ROOT"] = str(builder_root)
    env["DATA_COMMONS_DEV_SKILL_ROOT"] = str(skill_root)
    env["DATA_COMMONS_DEV_MANIFEST_PATH"] = str(manifest_path)
    env["DATA_COMMONS_DEV_SCENARIO_INDEX_PATH"] = str(scenario_index_path)
    env["DATA_COMMONS_DEV_SCENARIO_GUIDE_PATH"] = str(guide_path)

    result = subprocess.run(
        command,
        shell=True,
        cwd=skill_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "agentic index command failed with exit code "
            f"{result.returncode}:\n{result.stderr.strip()}"
        )

    guide_text = result.stdout
    if not guide_text.strip():
        raise RuntimeError("agentic index command produced empty output")
    if not guide_text.endswith("\n"):
        guide_text += "\n"
    return write_text_if_changed(guide_path, guide_text)


def main():
    args = parse_args()
    builder_root = Path(args.builder_root).resolve() if args.builder_root else Path(__file__).resolve().parent
    package_root = builder_root.parents[1]
    skill_root = (
        Path(args.skill_root).resolve()
        if args.skill_root
        else package_root / "skills" / builder_root.name
    )
    source_root = Path(args.source_root).resolve() if args.source_root else package_root.parent
    manifest_path = Path(args.manifest).resolve() if args.manifest else builder_root / "manifest.json"

    manifest, stats, index_status, lock_status = sync_snapshot(
        builder_root, skill_root, source_root, manifest_path
    )
    print(
        "snapshot: "
        f"created={stats['created']} updated={stats['updated']} "
        f"unchanged={stats['unchanged']} removed={stats['removed']}"
    )
    print(f"scenario-index: {index_status}")
    print(f"sources.lock.json: {lock_status}")

    if args.agentic_index:
        command = args.agentic_command or os.environ.get("DATA_COMMONS_DEV_AGENTIC_INDEX_COMMAND")
        if not command:
            raise RuntimeError(
                "--agentic-index requires --agentic-command or DATA_COMMONS_DEV_AGENTIC_INDEX_COMMAND"
            )
        guide_status = run_agentic_index(builder_root, skill_root, manifest, manifest_path, command)
        print(f"scenario-guide: {guide_status}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3
"""Bundle every .md file inside any folder named `notes` into notes-data.js,
so index.html can show them (browsers can't list a folder on their own).

You usually don't need to run this by hand:
  - `python3 serve.py` rebuilds the notes on every page refresh.
  - A GitHub Action reruns it whenever .md notes are pushed.
"""
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "notes-data.js"


def title_for(path: Path, text: str) -> str:
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+?)\s*#*\s*$", line)
        if m:
            return m.group(1)
    return path.stem.replace("-", " ").replace("_", " ")


def modified_for(path: Path) -> str:
    """Last commit date for the note, or the file's own timestamp if it isn't committed yet."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cI", "--", str(path)], cwd=ROOT,
                             capture_output=True, text=True, timeout=10).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--", str(path)], cwd=ROOT,
                               capture_output=True, text=True, timeout=10).stdout.strip()
        if out and not dirty:
            return out[:16]
    except (OSError, subprocess.SubprocessError):
        pass
    return datetime.fromtimestamp(os.path.getmtime(path)).isoformat(timespec="minutes")


def note_files():
    for notes_dir in sorted(p for p in ROOT.rglob("notes") if p.is_dir() and ".git" not in p.parts):
        yield from sorted(notes_dir.rglob("*.md"))


def bundle() -> tuple[str, int]:
    """Return the notes-data.js text and how many notes it holds."""
    notes = []
    for path in note_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        notes.append({
            "file": path.relative_to(ROOT).as_posix(),
            "title": title_for(path, text),
            "modified": modified_for(path),
            "content": text,
        })
    return "window.NOTES = " + json.dumps(notes, ensure_ascii=False, indent=1) + ";\n", len(notes)


def main() -> None:
    text, count = bundle()
    OUT.write_text(text, encoding="utf-8")
    print(f"Bundled {count} note(s) into {OUT.name}")


if __name__ == "__main__":
    main()

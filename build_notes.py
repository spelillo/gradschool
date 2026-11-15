#!/usr/bin/env python3
"""Bundle every .md file inside any folder named `notes` into notes-data.js,
so index.html can show them (browsers can't list a folder on their own).

Run this again whenever you add, edit or remove a note:
    python3 build_notes.py
"""
import json
import os
import re
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


def note_files():
    for notes_dir in sorted(p for p in ROOT.rglob("notes") if p.is_dir() and ".git" not in p.parts):
        yield from sorted(notes_dir.rglob("*.md"))


def main() -> None:
    notes = []
    for path in note_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        notes.append({
            "file": path.relative_to(ROOT).as_posix(),
            "title": title_for(path, text),
            "modified": datetime.fromtimestamp(os.path.getmtime(path)).isoformat(timespec="minutes"),
            "content": text,
        })
    OUT.write_text("window.NOTES = " + json.dumps(notes, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(f"Bundled {len(notes)} note(s) into {OUT.name}")


if __name__ == "__main__":
    main()

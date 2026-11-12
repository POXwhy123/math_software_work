"""Validate the course vault layout and local file links (Python standard library)."""
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []
    required = ["README.md", "00-首页.md", "01-课程计划/本地环境检查.md",
                "01-课程计划/第01-11周任务与验收清单.md"]
    for week in range(1, 12):
        required.append(f"02-每周笔记/第{week:02d}周.md")
        required.append(f"06-课程成果/第{week:02d}周/README.md")
        for folder in ("source", "output", "evidence"):
            required.append(f"06-课程成果/第{week:02d}周/{folder}")
    for name in required:
        if not (ROOT / name).exists():
            errors.append(f"Missing: {name}")
    for name in ("app.json", "core-plugins.json", "templates.json"):
        try:
            json.loads((ROOT / ".obsidian" / name).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"Invalid Obsidian config {name}: {exc}")
    notes = [p for p in ROOT.rglob("*.md")
             if not any(part in {".git", ".local", "node_modules", ".venv"}
                        for part in p.relative_to(ROOT).parts)]
    link_count = 0
    for note in notes:
        content = note.read_text(encoding="utf-8")
        content = re.sub(r"```.*?```", "", content, flags=re.S)
        content = re.sub(r"`[^`\n]+`", "", content)
        relative = note.relative_to(ROOT)
        for raw in re.findall(r"(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)", content):
            target = raw.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (note.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                errors.append(f"Broken or external local link: {relative}: {target}")
            link_count += 1
        for raw in re.findall(r"\[\[([^\]\n]+)\]\]", content):
            target = raw.split("|", 1)[0].split("#", 1)[0]
            if not target:
                continue
            candidate = ROOT / target
            if not candidate.suffix:
                candidate = candidate.with_suffix(".md")
            if not candidate.is_file():
                errors.append(f"Broken wiki link: {relative}: {target}")
            link_count += 1
    print(f"Checked {len(notes)} Markdown files and {link_count} local file links.")
    print("Scope: file targets and directory/config presence; headings, GUI and coursework are not verified.")
    for error in errors:
        print(error)
    print(f"RESULT: {'FAIL' if errors else 'PASS'} ({len(errors)} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

"""Validate the course vault layout and local file links (Python standard library)."""
import json
import re
import sys
from urllib.parse import unquote, urlsplit

from course_paths import PROCESS, ROOT, VAULT, WEEK01_SOURCE


COURSE_FOLDERS = {"01-GeoGebra", "02-计算实验", "03-LaTeX", "04-展示材料", "05-过程记录"}


def main():
    errors = []
    if not VAULT.is_dir():
        print(f"Missing Obsidian vault: {VAULT.name}")
        return 1
    visible_entries = {entry.name for entry in VAULT.iterdir() if not entry.name.startswith(".")}
    if visible_entries != COURSE_FOLDERS:
        errors.append(f"Expected vault entries {sorted(COURSE_FOLDERS)}, found {sorted(visible_entries)}")
    for folder in COURSE_FOLDERS:
        if not (VAULT / folder).is_dir():
            errors.append(f"Missing vault directory: {folder}")
    for extension, folder in ((".ggb", "01-GeoGebra"), (".tex", "03-LaTeX")):
        for source in VAULT.rglob(f"*{extension}"):
            if not source.is_relative_to(VAULT / folder):
                errors.append(f"Misplaced source: {source.relative_to(VAULT)}")
    required = [
        ROOT / "README.md", PROCESS / "00-首页.md", PROCESS / "课程计划" / "本地环境检查.md",
        PROCESS / "课程计划" / "第01-11周任务与验收清单.md", WEEK01_SOURCE,
        VAULT / "02-计算实验" / "Mathematica.md",
        VAULT / "04-展示材料" / "第01周" / "基础对象展示.md",
    ]
    required.extend(PROCESS / "每周笔记" / f"第{week:02d}周.md" for week in range(1, 12))
    required.extend(PROCESS / "成果" / f"第{week:02d}周" / "README.md" for week in range(1, 12))
    for path in required:
        if not path.is_file():
            errors.append(f"Missing: {path.relative_to(ROOT)}")
    for name in ("app.json", "core-plugins.json", "templates.json"):
        try:
            config = json.loads((VAULT / ".obsidian" / name).read_text(encoding="utf-8"))
            if name == "templates.json" and not (VAULT / config.get("folder", ".missing")).is_dir():
                errors.append("Missing Obsidian template folder")
        except (OSError, ValueError) as exc:
            errors.append(f"Invalid Obsidian config {name}: {exc}")
    notes = [ROOT / "README.md", *sorted(VAULT.glob("*/**/*.md"))]
    link_count = 0
    for note in notes:
        if not note.is_file():
            continue
        content = note.read_text(encoding="utf-8")
        content = re.sub(r"```.*?```", "", content, flags=re.S)
        content = re.sub(r"`[^`\n]+`", "", content)
        relative = note.relative_to(ROOT)
        link_root = VAULT if note.is_relative_to(VAULT) else ROOT
        for raw in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", content):
            target = raw.strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (note.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(link_root) or not resolved.exists():
                errors.append(f"Broken or external local link: {relative}: {target}")
            link_count += 1
        for raw in re.findall(r"\[\[([^\]\n]+)\]\]", content):
            target = raw.split("|", 1)[0].split("#", 1)[0]
            if not target:
                continue
            candidate = VAULT / target
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

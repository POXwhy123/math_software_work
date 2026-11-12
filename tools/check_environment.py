"""Read-only Windows inventory. No installs, GUI launches, login or remote writes."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ("git", "python", "node", "xelatex", "pdflatex", "lualatex", "latex",
            "latexmk", "biber", "bibtex", "kpsewhich", "wolframscript",
            "WolframKernel", "math", "make", "pandoc")
URLS = {
    "course_profile": "https://ob.vanabel.cn/04-courses/mathsoftwear/07-作业与评价/11-学生个人学习档案模板",
    "course_roadmap": "https://ob.vanabel.cn/04-courses/mathsoftwear/08-教学实施/01-14周课堂实施路线图",
    "texbrain": "https://tex.vanabel.cn",
    "geogebra_classic": "https://www.geogebra.org/classic",
}


def installed_apps():
    if os.name != "nt":
        return []
    import winreg
    found = []
    entries = [(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", view)
               for view in (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY)]
    entries.append((winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0))
    for hive, keyname, view in entries:
        try:
            with winreg.OpenKey(hive, keyname, 0, winreg.KEY_READ | view) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        with winreg.OpenKey(key, winreg.EnumKey(key, i)) as sub:
                            def value(name):
                                try:
                                    return winreg.QueryValueEx(sub, name)[0]
                                except OSError:
                                    return ""
                            name = value("DisplayName")
                            if re.search(r"Obsidian|GeoGebra|Mathematica|Wolfram|MiKTeX|TeX Live|Chrome|Microsoft Edge$", name, re.I):
                                found.append({"name": name, "version": value("DisplayVersion"),
                                              "location": value("InstallLocation"),
                                              "icon": value("DisplayIcon")})
                    except OSError:
                        pass
        except OSError:
            pass
    return found


def command_info(name):
    path = shutil.which(name)
    data = {"name": name, "path": path, "status": "found" if path else "not_on_PATH"}
    # Do not start a licensed kernel or invoke make in the project.
    if path and name in {"git", "python", "node", "xelatex", "pdflatex", "lualatex",
                          "latex", "latexmk", "biber", "bibtex", "kpsewhich", "pandoc"}:
        try:
            result = subprocess.run([path, "--version"], capture_output=True, text=True,
                                    encoding="utf-8", errors="replace", timeout=15)
            data.update(exit_code=result.returncode,
                        version_output=(result.stdout + result.stderr).strip()[:1200])
        except (OSError, subprocess.TimeoutExpired) as exc:
            data.update(status="version_probe_failed", error=str(exc))
    return data


def network_info(item):
    name, url = item
    # Encode non-ASCII path components while preserving URL syntax.
    from urllib.parse import quote
    request = Request(quote(url, safe=":/?=&%"), headers={"User-Agent": "MathSoftwareEnvironmentCheck/1.0"})
    try:
        with urlopen(request, timeout=15) as response:
            response.read(2048)
            return {"name": name, "url": url, "http_status": response.status,
                    "note": "HTTP only; browser execution, WASM, file access and compilation unverified"}
    except HTTPError as exc:
        return {"name": name, "url": url, "http_status": exc.code}
    except Exception as exc:
        return {"name": name, "url": url, "error": str(exc)}


def executable_files(apps):
    paths = set()
    for app in apps:
        if app["icon"]:
            icon = app["icon"].split(",", 1)[0].strip('"')
            if icon.lower().endswith(".exe") and Path(icon).is_file():
                paths.add(icon)
        if app["location"]:
            root = Path(app["location"])
            for pattern in ("*.exe", "app-*/*.exe", "Executables/*.exe"):
                paths.update(str(p) for p in root.glob(pattern) if p.is_file())
    return sorted(paths)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", action="store_true", help="GET course and browser-tool entry pages")
    args = parser.parse_args()
    apps = installed_apps()
    with ThreadPoolExecutor(max_workers=6) as pool:
        commands = list(pool.map(command_info, COMMANDS))
        network = list(pool.map(network_info, URLS.items())) if args.network else []
    missing = [name for name in ("xelatex", "biber") if not shutil.which(name)]
    kernel_found = any(shutil.which(name) for name in ("wolframscript", "WolframKernel", "math"))
    if not kernel_found:
        missing.append("Wolfram kernel command (license and notebook frontend also need verification)")
    report = {
        "checked_at": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "platform": platform.platform(), "python": sys.version.split()[0],
        "free_workspace_gib": round(shutil.disk_usage(ROOT).free / 1024**3, 1),
        "commands": commands, "installed_apps": apps,
        "existing_executables": executable_files(apps), "network": network,
        "missing_core_commands": missing,
        "limits": ["Registry and PATH inventory; unregistered custom installs may be missed.",
                   "A found executable or HTTP 200 does not prove a usable app or successful coursework.",
                   "Mathematica license, fresh-kernel .nb run, GeoGebra save/drag/CAS/spreadsheet, Obsidian UI and TeXbrain compile/export remain manual checks."]}
    output = ROOT / ".local" / "checks"
    output.mkdir(parents=True, exist_ok=True)
    (output / "environment.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# Local environment inventory", "", f"Checked: {report['checked_at']}", "",
             "| Command | Detection |", "| --- | --- |"]
    lines += [f"| {c['name']} | {c['status']} |" for c in commands]
    lines += ["", "## Registered applications", ""]
    lines += [f"- {a['name']}: {a['version']}" for a in apps]
    lines += ["", "## HTTP probes", ""]
    lines += [f"- {n['name']}: {n.get('http_status', n.get('error'))}" for n in network]
    lines += ["", "## Missing core commands", ""] + [f"- {m}" for m in missing]
    lines += ["", "## Limits", ""] + [f"- {item}" for item in report["limits"]]
    (output / "environment.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Reports: .local/checks/environment.json and environment.md (ignored by Git)")
    for app in apps:
        print(f"APP: {app['name']} {app['version']}")
    for item in network:
        print(f"HTTP: {item['name']} {item.get('http_status', item.get('error'))}")
    print("Missing core commands: " + ("; ".join(missing) or "none detected; runtime checks still required"))
    return 2 if missing else 0


if __name__ == "__main__":
    sys.exit(main())

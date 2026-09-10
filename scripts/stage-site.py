#!/usr/bin/env python3
"""Stage only public web assets for the Sites static deployment."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "dist"
if DEST.exists():
    shutil.rmtree(DEST)
DEST.mkdir()
for pattern in ("*.html", "*.css", "*.js", "robots.txt", "sitemap.xml"):
    for source in ROOT.glob(pattern):
        if source.name != "config.template.js":
            shutil.copy2(source, DEST / source.name)
for name in ("assets", "static", "content", ".well-known"):
    source = ROOT / name
    if source.exists():
        shutil.copytree(source, DEST / name)
print(f"Staged {sum(p.is_file() for p in DEST.rglob('*'))} public assets in {DEST}")

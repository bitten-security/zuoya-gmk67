"""Converts the vendor KeyboardLayout.xml (not valid XML) into gmk67/layout.json."""
import html
import json
import re
from pathlib import Path

SRC = Path(r"C:\Program Files (x86)\ZUOYO GMK67 Driver\KeyboardLayout.xml")
DST = Path(__file__).resolve().parent.parent / "gmk67" / "layout.json"
SHORT = {"control": "ctrl", "page up": "pgup", "page down": "pgdn", "backspace": "bksp", "enter": "enter",
         "caps": "caps", "shift": "shift", "space": "space"}

keys = []
for line in SRC.read_text(encoding="utf-8").splitlines():
    if not line.lstrip().startswith("<key "):
        continue
    attr = {k: html.unescape(v) for k, v in re.findall(r'(\w+)="(.*?)"(?=\s+\w+="|\s*/>)', line)}
    keys.append({"name": attr["name"], "label": SHORT.get(attr["name"], attr["name"]),
                 "x": int(attr["rect_left"]), "y": int(attr["rect_top"]),
                 "w": int(attr["rect_width"]), "h": int(attr["rect_height"]), "idx": int(attr["light_index"])})
DST.write_text(json.dumps({"width": 800, "height": 300, "keys": keys}, ensure_ascii=False), encoding="utf-8")
print(len(keys), "keys ->", DST)

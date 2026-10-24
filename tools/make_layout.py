"""Converts the vendor KeyboardLayout.xml (not valid XML) into gmk67/layout.json."""
import html
import json
import re
from pathlib import Path

SRC = Path(r"C:\Program Files (x86)\ZUOYO GMK67 Driver\KeyboardLayout.xml")
DST = Path(__file__).resolve().parent.parent / "gmk67" / "layout.json"

text = SRC.read_text(encoding="utf-8")
keys = []
for m in re.finditer(r'<key code="([^"]+)" name="([^"]*)"[^>]*?rect_left="(\d+)" rect_top="(\d+)" '
                     r'rect_width="(\d+)" rect_height="(\d+)"[^>]*?light_index="(\d+)"', text):
    keys.append({"name": html.unescape(m[2]), "x": int(m[3]), "y": int(m[4]),
                 "w": int(m[5]), "h": int(m[6]), "idx": int(m[7])})
DST.write_text(json.dumps({"width": 800, "height": 300, "keys": keys}, ensure_ascii=False), encoding="utf-8")
print(len(keys), "keys ->", DST)

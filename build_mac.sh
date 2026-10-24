#!/usr/bin/env bash
# Builds dist/GMK67Control-mac-<arch>.dmg  (run on macOS: pip install -r requirements.txt pyinstaller)
set -euo pipefail
ARCH="${1:-$(uname -m)}"
cd "$(dirname "$0")"

# icon.icns from the PNG
ICONSET=build_tmp/icon.iconset
rm -rf "$ICONSET" && mkdir -p "$ICONSET"
for s in 16 32 64 128 256; do
  sips -z $s $s gmk67/icon.png --out "$ICONSET/icon_${s}x${s}.png" >/dev/null
  sips -z $((s*2)) $((s*2)) gmk67/icon.png --out "$ICONSET/icon_${s}x${s}@2x.png" >/dev/null
done
iconutil -c icns "$ICONSET" -o build_tmp/icon.icns

python -m PyInstaller --noconfirm --clean --windowed --name "GMK67 Control" \
  --icon build_tmp/icon.icns --osx-bundle-identifier io.github.gmk67control \
  --add-data "gmk67/layout.json:gmk67" --add-data "gmk67/icon.png:gmk67" \
  --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.Qt3DCore \
  --distpath dist --workpath build_tmp --specpath build_tmp run.py

# ad-hoc signature so the app launches on Apple silicon (it is not notarized)
codesign --force --deep --sign - "dist/GMK67 Control.app"
hdiutil create -volname "GMK67 Control" -srcfolder "dist/GMK67 Control.app" -ov -format UDZO "dist/GMK67Control-mac-$ARCH.dmg"
echo "built dist/GMK67Control-mac-$ARCH.dmg"

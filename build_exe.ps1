# Builds dist\GMK67Control.exe (needs: pip install -r requirements.txt pyinstaller)
python -m PyInstaller --noconfirm --clean --windowed --onefile --name GMK67Control `
  --add-data "$PSScriptRoot\gmk67\layout.json;gmk67" `
  --collect-submodules comtypes --collect-submodules pycaw `
  --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.Qt3DCore `
  --distpath dist --workpath build_tmp --specpath build_tmp run.py

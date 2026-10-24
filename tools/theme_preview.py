"""Renders the real window with every theme:  python tools/theme_preview.py <output dir>  (tab: 0 effects, 1 per key)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PySide6.QtWidgets import QApplication  # noqa: E402

from gmk67 import app as appmod  # noqa: E402
from gmk67.theme import THEMES  # noqa: E402

if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    tab = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    qa = QApplication(sys.argv)
    qa.setStyle("Fusion")
    appmod.save_cfg_orig = appmod.Main.save_cfg
    appmod.Main.save_cfg = lambda self: None            # previews must not touch the user's settings
    m = appmod.Main()
    m.resize(1060, 640)
    m.tabs.setCurrentIndex(tab)
    from PySide6.QtGui import QColor, QImage, QPainter
    demo = {}                                           # a rainbow along the top rows, the rest left to the theme
    for i, k in enumerate(sorted(m.board.keys, key=lambda k: (k["y"], k["x"]))[:28]):
        c = QColor.fromHsvF((i % 14) / 14, .85, 1)
        demo[k["idx"]] = (c.red(), c.green(), c.blue())
    m.board.colors = demo
    m.board.selected = {m.board.keys[20]["idx"], m.board.keys[21]["idx"]}
    m.show()
    shots = []
    for key in THEMES:
        m.themeBox.setCurrentIndex(m.themeBox.findData(key))
        qa.processEvents()
        img = m.grab().toImage()
        img.save(str(out / f"theme-{key}.png"))
        shots.append(img.scaled(530, 320, mode=__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.SmoothTransformation))
        print("saved", key)
    sheet = QImage(3 * 540 + 10, 2 * 330 + 10, QImage.Format_ARGB32)
    sheet.fill(QColor("#888"))
    p = QPainter(sheet)
    for i, s in enumerate(shots):
        p.drawImage(10 + (i % 3) * 540, 10 + (i // 3) * 330, s)
    p.end()
    sheet.save(str(out / "themes-sheet.png"))
    m.tray.hide()

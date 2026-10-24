QSS = """
* { font-family: 'Segoe UI'; font-size: 13px; color: #d7deea; }
QMainWindow, QWidget#root { background: #0f1217; }
QLabel#title { font-size: 22px; font-weight: 700; color: #ffffff; }
QLabel#subtitle { color: #7d8799; }
QLabel#chip { background: #1a1f29; border: 1px solid #2a2f3a; border-radius: 10px; padding: 3px 10px; }
QLabel#chipOn { background: #12301f; border: 1px solid #1f6b3e; border-radius: 10px; padding: 3px 10px; color: #6be39a; }
QLabel#status { color: #7d8799; }
QFrame#card { background: #171b23; border: 1px solid #242a35; border-radius: 12px; }
QTabWidget::pane { border: none; }
QTabBar::tab { background: transparent; padding: 8px 18px; margin-right: 4px; color: #7d8799; border-bottom: 2px solid transparent; }
QTabBar::tab:selected { color: #ffffff; border-bottom: 2px solid #5b8cff; }
QPushButton { background: #232a37; border: 1px solid #323a4a; border-radius: 8px; padding: 7px 14px; }
QPushButton:hover { background: #2b3445; }
QPushButton:pressed { background: #1c2230; }
QPushButton#primary { background: #4a7bff; border: none; color: white; font-weight: 600; }
QPushButton#primary:hover { background: #5b8cff; }
QPushButton#danger:hover { background: #4a2128; border-color: #7a2f3a; }
QComboBox, QListWidget { background: #1a1f29; border: 1px solid #2a3140; border-radius: 8px; padding: 6px 8px; }
QComboBox QAbstractItemView { background: #1a1f29; selection-background-color: #34508f; border: 1px solid #2a3140; }
QListWidget::item { padding: 7px 8px; border-radius: 6px; }
QListWidget::item:selected { background: #2c4378; }
QSlider::groove:horizontal { height: 6px; background: #262d3b; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #4a7bff; border-radius: 3px; }
QSlider::handle:horizontal { width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; background: #ffffff; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 5px; border: 1px solid #3a4254; background: #1a1f29; }
QCheckBox::indicator:checked { background: #4a7bff; border-color: #4a7bff; }
"""

PALETTE = ["#ff0000", "#ff7a00", "#ffd000", "#00ff00", "#00ffd0", "#00a2ff", "#0000ff", "#8000ff",
           "#ff00ff", "#ff0080", "#ffffff", "#000000"]

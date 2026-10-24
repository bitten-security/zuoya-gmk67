"""Themes: each is a palette of tokens; build_qss() turns the active one into the application style sheet."""

THEMES = {
    "dark": {
        "name": "Dark", "bg": "#0f1217", "card": "#171b23", "border": "#242a35", "text": "#d7deea",
        "muted": "#7d8799", "title": "#ffffff", "button": "#232a37", "button_hover": "#2b3445",
        "button_border": "#323a4a", "input": "#1a1f29", "input_border": "#2a3140", "accent": "#4a7bff",
        "accent_hover": "#5b8cff", "select": "#2c4378", "groove": "#262d3b", "handle": "#ffffff",
        "ok_bg": "#12301f", "ok_border": "#1f6b3e", "ok_text": "#6be39a", "danger": "#e0485a",
        "kbd_bg": "#15181f", "kbd_key": "#232834", "kbd_border": "#3a4150", "kbd_text": "#c9d1e0",
        "sel": "#ffffff", "knob_bg": "#0c0e13", "knob_ring": "#2a3040",
    },
    "light": {
        "name": "Light", "bg": "#eef1f6", "card": "#ffffff", "border": "#d8dee9", "text": "#1d2433",
        "muted": "#6a7385", "title": "#0d1220", "button": "#e8ecf3", "button_hover": "#dce2ed",
        "button_border": "#ccd3e0", "input": "#f6f8fb", "input_border": "#ccd3e0", "accent": "#3b6cf0",
        "accent_hover": "#2f5ad0", "select": "#cfdcff", "groove": "#d6dce8", "handle": "#ffffff",
        "ok_bg": "#dcf5e5", "ok_border": "#7fcf9f", "ok_text": "#1b7a45", "danger": "#d63a4d",
        "kbd_bg": "#e3e8f1", "kbd_key": "#ffffff", "kbd_border": "#b9c2d3", "kbd_text": "#2b3447",
        "sel": "#1d2433", "knob_bg": "#f4f6fa", "knob_ring": "#cdd4e2",
    },
    "midnight": {
        "name": "Midnight", "bg": "#090b14", "card": "#10142a", "border": "#1c2347", "text": "#cdd6f4",
        "muted": "#7280b3", "title": "#ffffff", "button": "#181e3d", "button_hover": "#222a52",
        "button_border": "#2a335f", "input": "#0d1124", "input_border": "#232c55", "accent": "#7aa2f7",
        "accent_hover": "#8fb2ff", "select": "#27356b", "groove": "#1a2144", "handle": "#e6ecff",
        "ok_bg": "#10282a", "ok_border": "#1f7a72", "ok_text": "#5de0cf", "danger": "#f7768e",
        "kbd_bg": "#0b0e1f", "kbd_key": "#161c3a", "kbd_border": "#2b356b", "kbd_text": "#b9c4f0",
        "sel": "#7aa2f7", "knob_bg": "#080a18", "knob_ring": "#1d2547",
    },
    "neon": {
        "name": "Neon", "bg": "#0d0714", "card": "#170d24", "border": "#2c1a45", "text": "#ecdcff",
        "muted": "#9a7fc0", "title": "#ffffff", "button": "#241338", "button_hover": "#32194d",
        "button_border": "#43256a", "input": "#1a0f2a", "input_border": "#3a2260", "accent": "#d946ef",
        "accent_hover": "#e879f9", "select": "#5a1f7a", "groove": "#2b1844", "handle": "#ffffff",
        "ok_bg": "#0f2a2a", "ok_border": "#14b8a6", "ok_text": "#5eead4", "danger": "#fb7185",
        "kbd_bg": "#120a1e", "kbd_key": "#21123a", "kbd_border": "#4b2b78", "kbd_text": "#e2cdfb",
        "sel": "#22d3ee", "knob_bg": "#0a0510", "knob_ring": "#33204f",
    },
    "forest": {
        "name": "Forest", "bg": "#0c1411", "card": "#121e19", "border": "#1f3228", "text": "#d4e6dc",
        "muted": "#7f9a8b", "title": "#f2fff8", "button": "#1a2b23", "button_hover": "#233a2f",
        "button_border": "#2c4a3b", "input": "#0f1a15", "input_border": "#254035", "accent": "#34d399",
        "accent_hover": "#4ae0ab", "select": "#1f5a43", "groove": "#1f3329", "handle": "#ffffff",
        "ok_bg": "#143023", "ok_border": "#34d399", "ok_text": "#86efc0", "danger": "#f87171",
        "kbd_bg": "#0e1813", "kbd_key": "#1a2b23", "kbd_border": "#33503f", "kbd_text": "#cfe6da",
        "sel": "#fde047", "knob_bg": "#09100d", "knob_ring": "#23382d",
    },
    "sunset": {
        "name": "Sunset", "bg": "#160d0d", "card": "#211413", "border": "#3a2220", "text": "#f3dfd6",
        "muted": "#a88a80", "title": "#fff7f2", "button": "#2e1a18", "button_hover": "#3d2321",
        "button_border": "#55302c", "input": "#1b100f", "input_border": "#4a2a26", "accent": "#fb923c",
        "accent_hover": "#fdae62", "select": "#6b3418", "groove": "#352120", "handle": "#ffffff",
        "ok_bg": "#1f2a14", "ok_border": "#84cc16", "ok_text": "#bef264", "danger": "#f43f5e",
        "kbd_bg": "#1a0f0e", "kbd_key": "#2b1a18", "kbd_border": "#5a352f", "kbd_text": "#f0d8cd",
        "sel": "#fde68a", "knob_bg": "#100908", "knob_ring": "#3d2723",
    },
}

DEFAULT = "dark"
PALETTE = ["#ff0000", "#ff7a00", "#ffd000", "#00ff00", "#00ffd0", "#00a2ff", "#0000ff", "#8000ff",
           "#ff00ff", "#ff0080", "#ffffff", "#000000"]

_current = [THEMES[DEFAULT]]


def set_theme(key):
    _current[0] = THEMES.get(key, THEMES[DEFAULT])
    return _current[0]


def pal():
    """The active palette (tokens by name)."""
    return _current[0]


def build_qss(p=None):
    p = p or pal()
    return f"""
* {{ font-family: 'Segoe UI'; font-size: 13px; color: {p['text']}; }}
QMainWindow, QWidget#root {{ background: {p['bg']}; }}
QLabel#title {{ font-size: 22px; font-weight: 700; color: {p['title']}; }}
QLabel#subtitle {{ color: {p['muted']}; }}
QLabel#chip {{ background: {p['input']}; border: 1px solid {p['border']}; border-radius: 10px; padding: 3px 10px; }}
QLabel#chipOn {{ background: {p['ok_bg']}; border: 1px solid {p['ok_border']}; border-radius: 10px;
  padding: 3px 10px; color: {p['ok_text']}; }}
QLabel#status {{ color: {p['muted']}; }}
QFrame#card {{ background: {p['card']}; border: 1px solid {p['border']}; border-radius: 12px; }}
QTabWidget::pane {{ border: none; }}
QTabBar::tab {{ background: transparent; padding: 8px 18px; margin-right: 4px; color: {p['muted']};
  border-bottom: 2px solid transparent; }}
QTabBar::tab:selected {{ color: {p['title']}; border-bottom: 2px solid {p['accent']}; }}
QPushButton {{ background: {p['button']}; border: 1px solid {p['button_border']}; border-radius: 8px;
  padding: 7px 14px; }}
QPushButton:hover {{ background: {p['button_hover']}; }}
QPushButton#primary {{ background: {p['accent']}; border: none; color: white; font-weight: 600; }}
QPushButton#primary:hover {{ background: {p['accent_hover']}; }}
QPushButton#danger:hover {{ border-color: {p['danger']}; }}
QComboBox, QListWidget, QLineEdit, QPlainTextEdit, QSpinBox {{ background: {p['input']};
  border: 1px solid {p['input_border']}; border-radius: 8px; padding: 6px 8px; }}
QComboBox QAbstractItemView {{ background: {p['input']}; selection-background-color: {p['select']};
  border: 1px solid {p['input_border']}; }}
QListWidget::item {{ padding: 7px 8px; border-radius: 6px; }}
QListWidget::item:selected {{ background: {p['select']}; }}
QProgressBar {{ background: {p['input']}; border: 1px solid {p['input_border']}; border-radius: 6px;
  text-align: center; height: 16px; }}
QProgressBar::chunk {{ background: {p['accent']}; border-radius: 5px; }}
QSlider::groove:horizontal {{ height: 6px; background: {p['groove']}; border-radius: 3px; }}
QSlider::sub-page:horizontal {{ background: {p['accent']}; border-radius: 3px; }}
QSlider::handle:horizontal {{ width: 16px; height: 16px; margin: -6px 0; border-radius: 8px;
  background: {p['handle']}; border: 1px solid {p['button_border']}; }}
QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 5px; border: 1px solid {p['input_border']};
  background: {p['input']}; }}
QCheckBox::indicator:checked {{ background: {p['accent']}; border-color: {p['accent']}; }}
QMenu {{ background: {p['card']}; border: 1px solid {p['border']}; }}
QMenu::item:selected {{ background: {p['select']}; }}
"""

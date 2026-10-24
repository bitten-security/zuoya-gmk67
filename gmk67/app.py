import json
import os
import sys
from pathlib import Path

import tempfile

from PySide6.QtCore import QLockFile, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QIcon
from PySide6.QtWidgets import (QApplication, QCheckBox, QColorDialog, QComboBox, QFrame, QGridLayout,
                               QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListWidget, QMainWindow,
                               QMenu, QPlainTextEdit, QProgressBar, QPushButton, QSlider, QSpinBox,
                               QSystemTrayIcon, QTabWidget, QVBoxLayout, QWidget)

from .i18n import TEXT
from .keyboard_widget import KeyboardWidget
from .protocol import (EFFECTS, KEYS, MACRO_BASE, MACRO_END, MEDIA, MIN_DELAY_MS, PID, VID, Keyboard,
                       build_macro_area, entry_key, entry_macro, entry_media, text_to_events)
from .theme import PALETTE, QSS
from .usbrate import polling_rates

STORE = Path(os.environ.get("APPDATA", Path.home())) / "GMK67Control"
STORE.mkdir(parents=True, exist_ok=True)
CFG = STORE / "config.json"
DEFAULT_FX = {"effect": 1, "rgb": [255, 0, 0], "random": False, "brightness": 16, "speed": 11, "direction": 0}


_ICON = []


def app_icon():
    """Created lazily: a QIcon needs the QApplication to exist first."""
    if not _ICON:
        _ICON.append(QIcon(str(Path(__file__).parent / "icon.png")))
    return _ICON[0]


RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_NAME = "GMK67Control"


def autostart_command():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}" --minimized'
    return f'"{Path(sys.executable).with_name("pythonw.exe")}" "{Path(sys.argv[0]).resolve()}" --minimized'


def autostart_enabled():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            return winreg.QueryValueEx(k, RUN_NAME)[0] == autostart_command()
    except OSError:
        return False


def set_autostart(on):
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        if on:
            winreg.SetValueEx(k, RUN_NAME, 0, winreg.REG_SZ, autostart_command())
        else:
            try:
                winreg.DeleteValue(k, RUN_NAME)
            except FileNotFoundError:
                pass


def load_cfg():
    try:
        cfg = json.loads(CFG.read_text(encoding="utf-8"))
    except Exception:
        cfg = {}
    cfg.setdefault("lang", "pt")
    cfg.setdefault("profiles", {})
    cfg.setdefault("fx", dict(DEFAULT_FX))
    cfg.setdefault("keys", {})
    cfg.setdefault("tab", 0)
    cfg.setdefault("macros", [])
    cfg.setdefault("remap", {})
    return cfg


def card():
    f = QFrame()
    f.setObjectName("card")
    return f


def swatch(hex_color):
    b = QPushButton()
    b.setFixedSize(26, 26)
    b.setCursor(Qt.PointingHandCursor)
    b.setStyleSheet(f"background:{hex_color}; border:1px solid #3a4254; border-radius:13px;")
    return b


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = load_cfg()
        self.kb = Keyboard()
        self.fx_rgb = tuple(self.cfg["fx"]["rgb"])
        self.pen = (255, 0, 0)
        self.fx_timer = QTimer(self, singleShot=True, interval=150)
        self.fx_timer.timeout.connect(self.apply_fx)
        self.key_timer = QTimer(self, singleShot=True, interval=200)
        self.key_timer.timeout.connect(self.apply_keys)
        self.build()
        self.build_tray()
        self.set_fx_state(self.cfg["fx"])
        self.board.colors = {int(k): tuple(v) for k, v in self.cfg["keys"].items()}
        self.tabs.setCurrentIndex(self.cfg["tab"])
        self.retext()
        self.poll = QTimer(self, interval=3000)
        self.poll.timeout.connect(self.refresh_status)
        self.poll.start()

    def t(self, k):
        return TEXT[self.cfg["lang"]][k]

    # ---------------------------------------------------------------- layout
    def build(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(24, 20, 24, 16)
        outer.setSpacing(14)

        head = QHBoxLayout()
        tl = QVBoxLayout()
        tl.setSpacing(0)
        self.title = QLabel()
        self.title.setObjectName("title")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("subtitle")
        tl.addWidget(self.title)
        tl.addWidget(self.subtitle)
        head.addLayout(tl)
        head.addStretch()
        self.chipUsb, self.chipDongle = QLabel(), QLabel()
        head.addWidget(self.chipUsb)
        head.addSpacing(6)
        head.addWidget(self.chipDongle)
        head.addSpacing(14)
        self.chkAuto = QCheckBox()
        self.chkAuto.setChecked(autostart_enabled())
        self.chkAuto.toggled.connect(self.toggle_autostart)
        head.addWidget(self.chkAuto)
        head.addSpacing(10)
        self.lang = QComboBox()
        self.lang.addItems(["pt", "en"])
        self.lang.setCurrentText(self.cfg["lang"])
        self.lang.currentTextChanged.connect(self.set_lang)
        head.addWidget(self.lang)
        outer.addLayout(head)

        body = QHBoxLayout()
        body.setSpacing(16)
        self.tabs = QTabWidget()
        self.tabs.addTab(self.build_fx_tab(), "")
        self.tabs.addTab(self.build_keys_tab(), "")
        self.tabs.addTab(self.build_macros_tab(), "")
        self.tabs.addTab(self.build_funcs_tab(), "")
        self.tabs.currentChanged.connect(self.tab_changed)
        body.addWidget(self.tabs, 1)
        body.addWidget(self.build_profiles(), 0)
        outer.addLayout(body, 1)

        self.msg = QLabel()
        self.msg.setObjectName("status")
        outer.addWidget(self.msg)
        self.refresh_list()

    def build_fx_tab(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 12, 0, 0)
        c = card()
        g = QGridLayout(c)
        g.setContentsMargins(20, 18, 20, 18)
        g.setVerticalSpacing(14)
        self.lEffect, self.lBright, self.lSpeed, self.lDir, self.lColor = (QLabel() for _ in range(5))
        self.effect = QComboBox()
        for i, n in EFFECTS.items():
            self.effect.addItem(n, i)
        self.bright = QSlider(Qt.Horizontal)
        self.bright.setRange(1, 16)
        self.speed = QSlider(Qt.Horizontal)
        self.speed.setRange(1, 16)
        self.vBright, self.vSpeed = QLabel(), QLabel()
        self.dir = QComboBox()
        self.dir.addItems(["0", "1", "2", "3"])
        self.random = QCheckBox()
        self.colorBtn = QPushButton()
        self.colorBtn.clicked.connect(self.pick_fx_color)
        self.live = QCheckBox()
        self.live.setChecked(True)
        self.applyBtn = QPushButton()
        self.applyBtn.setObjectName("primary")
        self.applyBtn.clicked.connect(self.apply_fx)
        g.addWidget(self.lEffect, 0, 0)
        g.addWidget(self.effect, 0, 1, 1, 2)
        g.addWidget(self.lBright, 1, 0)
        g.addWidget(self.bright, 1, 1)
        g.addWidget(self.vBright, 1, 2)
        g.addWidget(self.lSpeed, 2, 0)
        g.addWidget(self.speed, 2, 1)
        g.addWidget(self.vSpeed, 2, 2)
        g.addWidget(self.lDir, 3, 0)
        g.addWidget(self.dir, 3, 1, 1, 2)
        g.addWidget(self.lColor, 4, 0)
        g.addWidget(self.colorBtn, 4, 1, 1, 2)
        g.addWidget(self.random, 5, 1, 1, 2)
        g.addWidget(self.live, 6, 1, 1, 2)
        g.addWidget(self.applyBtn, 7, 1, 1, 2)
        g.setColumnStretch(1, 1)
        for s in (self.effect, self.dir):
            s.currentIndexChanged.connect(self.fx_changed)
        for s in (self.bright, self.speed):
            s.valueChanged.connect(self.fx_changed)
        self.random.toggled.connect(self.fx_changed)
        lay.addWidget(c)
        lay.addStretch()
        return page

    def build_keys_tab(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 12, 0, 0)
        c = card()
        v = QVBoxLayout(c)
        v.setContentsMargins(16, 14, 16, 14)
        self.hint = QLabel()
        self.hint.setObjectName("subtitle")
        self.hint.setWordWrap(True)
        v.addWidget(self.hint)
        self.board = KeyboardWidget()
        self.board.selectionChanged.connect(self.sel_changed)
        self.board.knobClicked.connect(lambda: self.say(self.t("knob_info")))
        self.board.indicatorClicked.connect(lambda: self.say(self.t("led_info")))
        v.addWidget(self.board, 1)

        row = QHBoxLayout()
        self.penBtn = QPushButton()
        self.penBtn.setFixedWidth(150)
        self.penBtn.clicked.connect(self.pick_pen)
        row.addWidget(self.penBtn)
        self.lPalette = QLabel()
        row.addWidget(self.lPalette)
        for hx in PALETTE:
            b = swatch(hx)
            b.clicked.connect(lambda _=False, h=hx: self.set_pen(QColor(h)))
            row.addWidget(b)
        row.addStretch()
        self.selLabel = QLabel()
        self.selLabel.setObjectName("subtitle")
        row.addWidget(self.selLabel)
        v.addLayout(row)

        row2 = QHBoxLayout()
        self.bSelAll, self.bSelNone = QPushButton(), QPushButton()
        self.bPaintSel, self.bFill, self.bClear = QPushButton(), QPushButton(), QPushButton()
        self.bSend = QPushButton()
        self.bSend.setObjectName("primary")
        self.bSelAll.clicked.connect(self.select_all)
        self.bSelNone.clicked.connect(self.select_none)
        self.bPaintSel.clicked.connect(self.paint_selected)
        self.bFill.clicked.connect(self.paint_all)
        self.bClear.clicked.connect(self.clear_all)
        self.bSend.clicked.connect(self.apply_keys)
        for b in (self.bSelAll, self.bSelNone, self.bPaintSel, self.bFill, self.bClear):
            row2.addWidget(b)
        row2.addStretch()
        row2.addWidget(self.bSend)
        v.addLayout(row2)
        lay.addWidget(c, 1)
        return page

    def build_macros_tab(self):
        page = QWidget()
        lay = QHBoxLayout(page)
        lay.setContentsMargins(0, 12, 0, 0)
        left = card()
        lv = QVBoxLayout(left)
        self.mlist = QListWidget()
        self.mlist.currentRowChanged.connect(self.macro_selected)
        self.bMNew, self.bMDel = QPushButton(), QPushButton()
        self.bMDel.setObjectName("danger")
        self.bMNew.clicked.connect(self.macro_new)
        self.bMDel.clicked.connect(self.macro_delete)
        lv.addWidget(self.mlist, 1)
        lv.addWidget(self.bMNew)
        lv.addWidget(self.bMDel)
        left.setFixedWidth(200)
        right = card()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(16, 14, 16, 14)
        self.mHint = QLabel()
        self.mHint.setObjectName("subtitle")
        self.mHint.setWordWrap(True)
        rv.addWidget(self.mHint)
        self.lMName, self.lMText, self.lMDelay, self.lMSpace = (QLabel() for _ in range(4))
        self.mName = QLineEdit()
        self.mText = QPlainTextEdit()
        self.mDelay = QSpinBox()
        self.mDelay.setRange(MIN_DELAY_MS, 5000)
        self.mDelay.setValue(MIN_DELAY_MS)
        self.lMKey = QLabel()
        self.mKey = QComboBox()
        self.mKey.addItem("-", None)
        for k in sorted(self.board.keys, key=lambda k: (k["y"], k["x"])):
            self.mKey.addItem(k["name"].upper(), k["idx"])
        self.mBar = QProgressBar()
        self.mBar.setRange(0, MACRO_END - MACRO_BASE)
        self.mBar.setTextVisible(True)
        self.bMSave, self.bMSend = QPushButton(), QPushButton()
        self.bMSend.setObjectName("primary")
        self.bMSave.clicked.connect(self.macro_save)
        self.bMSend.clicked.connect(self.macro_send)
        self.mText.textChanged.connect(self.macro_space)
        self.mDelay.valueChanged.connect(self.macro_space)
        for w in (self.lMName, self.mName, self.lMText, self.mText, self.lMDelay, self.mDelay, self.lMKey,
                  self.mKey, self.lMSpace, self.mBar):
            rv.addWidget(w)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(self.bMSave)
        row.addWidget(self.bMSend)
        rv.addLayout(row)
        lay.addWidget(left)
        lay.addWidget(right, 1)
        self.refresh_macros()
        return page

    def refresh_macros(self, select=None):
        self.mlist.blockSignals(True)
        self.mlist.clear()
        self.mlist.addItems([f"{i + 1}. {m['name']}" for i, m in enumerate(self.cfg["macros"])])
        self.mlist.blockSignals(False)
        if self.cfg["macros"]:
            self.mlist.setCurrentRow(min(select if select is not None else 0, len(self.cfg["macros"]) - 1))
        else:
            self.macro_selected(-1)

    def macro_selected(self, row):
        m = self.cfg["macros"][row] if 0 <= row < len(self.cfg["macros"]) \
            else {"name": "", "text": "", "delay": 0, "key": None}
        self.mName.setText(m["name"])
        self.mText.setPlainText(m["text"])
        self.mDelay.setValue(m["delay"])
        self.mKey.setCurrentIndex(max(0, self.mKey.findData(m.get("key"))))
        self.macro_space()

    def macro_list(self, current=None):
        """Macros as stored, with the row being edited replaced by the editor contents."""
        ms = [dict(m) for m in self.cfg["macros"]]
        row = self.mlist.currentRow()
        cur = {"name": self.mName.text() or "macro", "text": self.mText.toPlainText(),
               "delay": self.mDelay.value(), "key": self.mKey.currentData()}
        if 0 <= row < len(ms):
            ms[row] = cur
        else:
            ms.append(cur)
        return ms

    def macro_space(self):
        try:
            _, used = build_macro_area([(text_to_events(m["text"]), m["delay"]) for m in self.macro_list()])
            self.mBar.setValue(used)
            self.mBar.setFormat(f"{used} / {MACRO_END - MACRO_BASE} bytes")
            return True
        except ValueError:
            self.mBar.setValue(self.mBar.maximum())
            self.mBar.setFormat(self.t("m_full"))
            return False

    def macro_new(self):
        self.cfg["macros"].append({"name": f"macro{len(self.cfg['macros']) + 1}", "text": "", "delay": 0})
        self.save_cfg()
        self.refresh_macros(len(self.cfg["macros"]) - 1)

    def macro_save(self):
        row = self.mlist.currentRow()
        ms = self.macro_list()
        self.cfg["macros"] = ms
        self.save_cfg()
        self.refresh_macros(row if row >= 0 else len(ms) - 1)

    def macro_delete(self):
        row = self.mlist.currentRow()
        if 0 <= row < len(self.cfg["macros"]):
            self.cfg["macros"].pop(row)
            self.save_cfg()
            self.refresh_macros(row)

    def macro_send(self):
        self.macro_save()
        if not self.macro_space():
            self.say(self.t("m_full"))
            return
        macros = [(text_to_events(m["text"]), m["delay"]) for m in self.cfg["macros"]]

        def go():
            self.kb.write_macros(macros)
            self.kb.write_keymap(self.keymap_entries())
        self.send(go)

    def keymap_entries(self):
        """Function remaps plus macro keys (a macro key wins over a plain remap on the same key)."""
        entries = {}
        for idx, r in self.cfg["remap"].items():
            if r["t"] == "key":
                entries[int(idx)] = entry_key(KEYS[r["v"]])
            elif r["t"] == "media":
                entries[int(idx)] = entry_media(MEDIA[r["v"]])
        for slot, m in enumerate(self.cfg["macros"]):
            if m.get("key") is not None:
                entries[m["key"]] = entry_macro(slot)
        return entries

    # ------------------------------------------------------------- functions
    def build_funcs_tab(self):
        page = QWidget()
        lay = QHBoxLayout(page)
        lay.setContentsMargins(0, 12, 0, 0)
        c = card()
        v = QVBoxLayout(c)
        v.setContentsMargins(16, 14, 16, 14)
        self.fHint = QLabel()
        self.fHint.setObjectName("subtitle")
        self.fHint.setWordWrap(True)
        v.addWidget(self.fHint)
        self.board2 = KeyboardWidget()
        self.board2.selectionChanged.connect(lambda: self.fSel.setText(
            f"{len(self.board2.selected)} {self.t('selected')}"))
        v.addWidget(self.board2, 1)
        row = QHBoxLayout()
        self.fCat, self.fFunc = QComboBox(), QComboBox()
        self.fCat.addItem("", "key")
        self.fCat.addItem("", "media")
        self.fCat.currentIndexChanged.connect(self.funcs_fill)
        row.addWidget(self.fCat)
        row.addWidget(self.fFunc, 1)
        self.fSel = QLabel()
        self.fSel.setObjectName("subtitle")
        row.addWidget(self.fSel)
        v.addLayout(row)
        osrow = QHBoxLayout()
        self.lOs = QLabel()
        self.bWin, self.bMac = QPushButton("WIN"), QPushButton("MAC")
        self.bWin.clicked.connect(lambda: self.set_os("win"))
        self.bMac.clicked.connect(lambda: self.set_os("mac"))
        for w in (self.lOs, self.bWin, self.bMac):
            osrow.addWidget(w)
        osrow.addStretch()
        v.addLayout(osrow)
        row2 = QHBoxLayout()
        self.bFApply, self.bFReset, self.bFSend = QPushButton(), QPushButton(), QPushButton()
        self.bFSend.setObjectName("primary")
        self.bFApply.clicked.connect(self.funcs_apply)
        self.bFReset.clicked.connect(self.funcs_reset)
        self.bFSend.clicked.connect(self.funcs_send)
        row2.addWidget(self.bFApply)
        row2.addWidget(self.bFReset)
        row2.addStretch()
        row2.addWidget(self.bFSend)
        v.addLayout(row2)
        lay.addWidget(c, 1)
        self.funcs_fill()
        self.funcs_paint()
        return page

    def funcs_fill(self):
        self.fFunc.clear()
        self.fFunc.addItems(list(KEYS if self.fCat.currentData() == "key" else MEDIA))

    # Mac layout: Windows keys sit where Option goes and vice versa (Ctrl | Opt | Cmd), keys by light index
    MAC_REMAP = {"92": ("Left Alt"), "93": ("Left Win"), "95": ("Right Win")}

    def os_mode(self):
        r = self.cfg["remap"]
        return "mac" if all(r.get(i, {}).get("v") == v for i, v in self.MAC_REMAP.items()) else "win"

    def set_os(self, mode):
        for i in self.MAC_REMAP:
            self.cfg["remap"].pop(i, None)
        if mode == "mac":
            for i, v in self.MAC_REMAP.items():
                self.cfg["remap"][i] = {"t": "key", "v": v}
        self.save_cfg()
        self.funcs_paint()
        self.funcs_send()

    def funcs_paint(self):
        self.board2.colors = {int(i): (74, 123, 255) for i in self.cfg["remap"]}
        self.board2.update()
        mac = self.os_mode() == "mac"
        for b, on in ((self.bMac, mac), (self.bWin, not mac)):
            b.setObjectName("primary" if on else "")
            b.style().unpolish(b)
            b.style().polish(b)

    def funcs_apply(self):
        for i in self.board2.selected:
            self.cfg["remap"][str(i)] = {"t": self.fCat.currentData(), "v": self.fFunc.currentText()}
        self.save_cfg()
        self.funcs_paint()

    def funcs_reset(self):
        for i in self.board2.selected:
            self.cfg["remap"].pop(str(i), None)
        self.save_cfg()
        self.funcs_paint()

    def funcs_send(self):
        entries = self.keymap_entries()
        self.send(lambda: self.kb.write_keymap(entries))

    def build_profiles(self):
        c = card()
        c.setFixedWidth(230)
        v = QVBoxLayout(c)
        v.setContentsMargins(14, 14, 14, 14)
        self.pTitle = QLabel()
        self.pTitle.setObjectName("title")
        self.pTitle.setStyleSheet("font-size:16px")
        v.addWidget(self.pTitle)
        self.plist = QListWidget()
        self.plist.itemDoubleClicked.connect(lambda _: self.load_profile())
        v.addWidget(self.plist, 1)
        self.bSave, self.bLoad, self.bDel = QPushButton(), QPushButton(), QPushButton()
        self.bDel.setObjectName("danger")
        self.bSave.clicked.connect(self.save_profile)
        self.bLoad.clicked.connect(self.load_profile)
        self.bDel.clicked.connect(self.del_profile)
        for b in (self.bSave, self.bLoad, self.bDel):
            v.addWidget(b)
        return c

    # ------------------------------------------------------------------ tray
    def build_tray(self):
        self.setWindowIcon(app_icon())
        self._quit = False
        self.tray = QSystemTrayIcon(app_icon(), self)
        menu = QMenu()
        self.actOpen = QAction(self)
        self.actOpen.triggered.connect(self.show_window)
        self.actAuto = QAction(self, checkable=True)
        self.actAuto.setChecked(self.chkAuto.isChecked())
        self.actAuto.toggled.connect(self.chkAuto.setChecked)
        self.actQuit = QAction(self)
        self.actQuit.triggered.connect(self.quit_app)
        for a in (self.actOpen, self.actAuto):
            menu.addAction(a)
        menu.addSeparator()
        menu.addAction(self.actQuit)
        self.tray.setContextMenu(menu)
        self.tray.setToolTip("Zuoya GMK67")
        self.tray.activated.connect(lambda r: self.show_window() if r == QSystemTrayIcon.Trigger else None)
        self.tray.show()

    def show_window(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def quit_app(self):
        self._quit = True
        self.tray.hide()
        QApplication.quit()

    def closeEvent(self, e):
        if self._quit or not self.tray.isVisible():
            e.accept()
            return
        e.ignore()
        self.hide()
        if not self.cfg.get("tray_hint"):
            self.cfg["tray_hint"] = True
            self.save_cfg()
            self.tray.showMessage(self.t("title"), self.t("tray_hint"), app_icon(), 4000)

    def toggle_autostart(self, on):
        try:
            set_autostart(on)
        except OSError as e:
            self.say(f"{self.t('err')}: {e}")
        self.actAuto.blockSignals(True)
        self.actAuto.setChecked(on)
        self.actAuto.blockSignals(False)

    def retext(self):
        self.setWindowTitle(self.t("title"))
        self.chkAuto.setText(self.t("autostart"))
        self.actOpen.setText(self.t("tray_open"))
        self.actAuto.setText(self.t("autostart"))
        self.actQuit.setText(self.t("tray_quit"))
        self.title.setText(self.t("title"))
        self.subtitle.setText(self.t("subtitle"))
        self.tabs.setTabText(0, self.t("tab_fx"))
        self.tabs.setTabText(1, self.t("tab_keys"))
        self.tabs.setTabText(2, self.t("tab_macros"))
        self.tabs.setTabText(3, self.t("tab_funcs"))
        self.fCat.setItemText(0, self.t("f_keys"))
        self.fCat.setItemText(1, self.t("f_media"))
        for w, k in ((self.fHint, "f_hint"), (self.bFApply, "f_apply"), (self.bFReset, "f_reset"),
                     (self.bFSend, "f_send"), (self.lOs, "os_label")):
            w.setText(self.t(k))
        for w, k in ((self.mHint, "m_hint"), (self.lMName, "m_name"), (self.lMText, "m_text"),
                     (self.lMDelay, "m_delay"), (self.lMKey, "m_key"), (self.lMSpace, "m_space"), (self.bMSave, "m_save"),
                     (self.bMSend, "m_send"), (self.bMNew, "m_new"), (self.bMDel, "delete")):
            w.setText(self.t(k))
        for w, k in ((self.lEffect, "effect"), (self.lBright, "brightness"), (self.lSpeed, "speed"),
                     (self.lDir, "direction"), (self.lColor, "color"), (self.random, "random"),
                     (self.live, "live"), (self.applyBtn, "apply"), (self.hint, "hint"),
                     (self.lPalette, "palette"), (self.bSelAll, "sel_all"), (self.bSelNone, "sel_none"),
                     (self.bPaintSel, "paint_sel"), (self.bFill, "fill_all"), (self.bClear, "clear_keys"),
                     (self.bSend, "send"), (self.pTitle, "profiles"), (self.bSave, "save"),
                     (self.bLoad, "load"), (self.bDel, "delete")):
            w.setText(self.t(k))
        self.paint_buttons()
        self.sel_changed()
        self.refresh_status()

    def set_lang(self, lang):
        self.cfg["lang"] = lang
        self.save_cfg()
        self.retext()

    # ---------------------------------------------------------------- status
    def refresh_status(self):
        c = Keyboard.connections()
        if c != getattr(self, "_conn", None):        # polling rates only change when the links change
            self._conn = c
            try:
                self.rates = {r["kind"]: r["hz"] for r in polling_rates(VID, PID)}
            except Exception:
                self.rates = {}
        link = "usb" if c["usb"] else "dongle" if c["dongle"] else None
        for b in (self.board, self.board2):
            if b.link != link:
                b.link = link
                b.update()
        for chip, key, on in ((self.chipUsb, "usb", c["usb"]), (self.chipDongle, "dongle", c["dongle"])):
            hz = f" · {self.rates[key]} Hz" if on and key in self.rates else ""
            chip.setText(f"{self.t(key)}: {self.t('connected') if on else self.t('missing')}{hz}")
            chip.setObjectName("chipOn" if on else "chip")
            chip.style().unpolish(chip)
            chip.style().polish(chip)

    def say(self, text):
        self.msg.setText(text)

    def save_cfg(self):
        CFG.write_text(json.dumps(self.cfg, indent=1), encoding="utf-8")

    def tab_changed(self, i):
        self.cfg["tab"] = i
        self.save_cfg()

    # --------------------------------------------------------------- effects
    def paint_buttons(self):
        for btn, rgb in ((self.colorBtn, self.fx_rgb), (self.penBtn, self.pen)):
            c = QColor(*rgb)
            btn.setStyleSheet(f"background:{c.name()}; color:{'black' if c.lightness() > 128 else 'white'};"
                              "border:1px solid #3a4254; border-radius:8px; padding:7px 14px;")
        self.colorBtn.setText(self.t("pick"))
        self.penBtn.setText(self.t("pick"))

    def pick_fx_color(self):
        c = QColorDialog.getColor(QColor(*self.fx_rgb), self)
        if c.isValid():
            self.fx_rgb = (c.red(), c.green(), c.blue())
            self.paint_buttons()
            self.random.setChecked(False)
            self.fx_changed()

    def fx_changed(self, *_):
        self.vBright.setText(str(self.bright.value()))
        self.vSpeed.setText(str(self.speed.value()))
        if self.live.isChecked():
            self.fx_timer.start()

    def fx_state(self):
        return {"effect": self.effect.currentData(), "rgb": list(self.fx_rgb), "random": self.random.isChecked(),
                "brightness": self.bright.value(), "speed": self.speed.value(),
                "direction": int(self.dir.currentText())}

    def set_fx_state(self, s):
        for w in (self.effect, self.dir, self.bright, self.speed, self.random):
            w.blockSignals(True)
        self.effect.setCurrentIndex(max(0, self.effect.findData(s["effect"])))
        self.fx_rgb = tuple(s["rgb"])
        self.random.setChecked(s["random"])
        self.bright.setValue(s["brightness"])
        self.speed.setValue(s["speed"])
        self.dir.setCurrentText(str(s["direction"]))
        for w in (self.effect, self.dir, self.bright, self.speed, self.random):
            w.blockSignals(False)
        self.vBright.setText(str(self.bright.value()))
        self.vSpeed.setText(str(self.speed.value()))
        self.paint_buttons()

    def send(self, fn):
        try:
            if not self.kb.dev:
                self.kb.open()
            fn()
            self.say(self.t("applied"))
            return True
        except Exception as e:
            self.kb.close()
            self.say(f"{self.t('err')}: {e}")
            return False

    def apply_fx(self):
        s = self.fx_state()
        if self.send(lambda: self.kb.set_light(s["effect"], tuple(s["rgb"]), s["random"], s["brightness"],
                                               s["speed"], s["direction"])):
            self.cfg["fx"] = s
            self.cfg["tab"] = 0
            self.save_cfg()

    # -------------------------------------------------------------- per key
    def set_pen(self, c):
        self.pen = (c.red(), c.green(), c.blue())
        self.paint_buttons()
        if self.board.selected:
            self.paint_selected()

    def pick_pen(self):
        c = QColorDialog.getColor(QColor(*self.pen), self)
        if c.isValid():
            self.set_pen(c)

    def sel_changed(self):
        self.selLabel.setText(f"{len(self.board.selected)} {self.t('selected')}")

    def select_all(self):
        self.board.selected = {k["idx"] for k in self.board.keys}
        self.board.update()
        self.sel_changed()

    def select_none(self):
        self.board.selected = set()
        self.board.update()
        self.sel_changed()

    def paint_selected(self):
        for i in self.board.selected:
            self.board.colors[i] = self.pen
        self.board.update()
        self.key_timer.start()

    def paint_all(self):
        for k in self.board.keys:
            self.board.colors[k["idx"]] = self.pen
        self.board.update()
        self.key_timer.start()

    def clear_all(self):
        self.board.colors = {}
        self.board.update()
        self.key_timer.start()

    def apply_keys(self):
        colors = dict(self.board.colors)
        bright = self.bright.value()
        if self.send(lambda: self.kb.set_custom(colors, bright)):
            self.cfg["keys"] = {str(k): list(v) for k, v in colors.items()}
            self.cfg["tab"] = 1
            self.save_cfg()

    # -------------------------------------------------------------- profiles
    def refresh_list(self):
        self.plist.clear()
        self.plist.addItems(sorted(self.cfg["profiles"]))

    def save_profile(self):
        n, ok = QInputDialog.getText(self, self.t("save"), self.t("name"))
        if ok and n.strip():
            self.cfg["profiles"][n.strip()] = {"tab": self.tabs.currentIndex(), "fx": self.fx_state(),
                                               "keys": {str(k): list(v) for k, v in self.board.colors.items()}}
            self.save_cfg()
            self.refresh_list()

    def load_profile(self):
        it = self.plist.currentItem()
        if not it:
            return
        p = self.cfg["profiles"][it.text()]
        self.set_fx_state(p["fx"])
        self.board.colors = {int(k): tuple(v) for k, v in p["keys"].items()}
        self.board.update()
        self.tabs.setCurrentIndex(p["tab"])
        (self.apply_keys if p["tab"] == 1 else self.apply_fx)()

    def del_profile(self):
        it = self.plist.currentItem()
        if it:
            self.cfg["profiles"].pop(it.text(), None)
            self.save_cfg()
            self.refresh_list()


def main():
    app = QApplication(sys.argv)
    lock = QLockFile(str(Path(tempfile.gettempdir()) / "gmk67control.lock"))
    if not lock.tryLock(0):                       # already running (maybe hidden in the tray)
        sys.exit(0)
    app.setStyle("Fusion")
    app.setStyleSheet(QSS)
    app.setWindowIcon(app_icon())
    app.setQuitOnLastWindowClosed(False)
    m = Main()
    m.resize(1060, 640)
    if "--minimized" not in sys.argv:
        m.show()
    sys.exit(app.exec())

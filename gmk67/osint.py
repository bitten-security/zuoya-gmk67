"""Operating-system integration: settings folder and start-at-login (Windows registry, macOS LaunchAgent)."""
import os
import plistlib
import sys
from pathlib import Path

RUN_NAME = "GMK67Control"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
AGENT = Path.home() / "Library" / "LaunchAgents" / "io.github.gmk67control.plist"


def store_dir():
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    d = base / "GMK67Control"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _argv():
    """Command line that starts this app minimized."""
    if getattr(sys, "frozen", False):
        return [sys.executable, "--minimized"]
    if sys.platform == "win32":
        return [str(Path(sys.executable).with_name("pythonw.exe")), str(Path(sys.argv[0]).resolve()), "--minimized"]
    return [sys.executable, str(Path(sys.argv[0]).resolve()), "--minimized"]


def autostart_command():
    return " ".join(f'"{a}"' if " " in a or a.endswith(".exe") else a for a in _argv())


def autostart_enabled():
    try:
        if sys.platform == "win32":
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
                return winreg.QueryValueEx(k, RUN_NAME)[0] == " ".join(f'"{a}"' for a in _argv())
        if sys.platform == "darwin":
            return AGENT.exists() and plistlib.loads(AGENT.read_bytes()).get("ProgramArguments") == _argv()
    except (OSError, ValueError):
        pass
    return False


def set_autostart(on):
    if sys.platform == "win32":
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
            if on:
                winreg.SetValueEx(k, RUN_NAME, 0, winreg.REG_SZ, " ".join(f'"{a}"' for a in _argv()))
            else:
                try:
                    winreg.DeleteValue(k, RUN_NAME)
                except FileNotFoundError:
                    pass
    elif sys.platform == "darwin":
        if on:
            AGENT.parent.mkdir(parents=True, exist_ok=True)
            AGENT.write_bytes(plistlib.dumps({"Label": "io.github.gmk67control", "ProgramArguments": _argv(),
                                              "RunAtLoad": True}))
        else:
            AGENT.unlink(missing_ok=True)

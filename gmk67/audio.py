"""System master volume / mute, used to show the knob state. Windows: Core Audio (pycaw). macOS: osascript."""
import subprocess
import sys


class Volume:
    def __init__(self):
        self._ep = None

    # ------------------------------------------------------------------ Windows
    def _endpoint(self):
        if self._ep is None:
            from pycaw.pycaw import AudioUtilities
            self._ep = AudioUtilities.GetSpeakers().EndpointVolume
        return self._ep

    # -------------------------------------------------------------------- macOS
    @staticmethod
    def _osa(script):
        return subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=2).stdout.strip()

    def read(self):
        """(percent 0..100, muted) or None when no audio device is available."""
        try:
            if sys.platform == "darwin":
                vol = self._osa("output volume of (get volume settings)")
                muted = self._osa("output muted of (get volume settings)")
                return int(vol), muted == "true"
            ep = self._endpoint()
            return round(ep.GetMasterVolumeLevelScalar() * 100), bool(ep.GetMute())
        except Exception:
            self._ep = None
            return None

    def toggle_mute(self):
        try:
            if sys.platform == "darwin":
                muted = self._osa("output muted of (get volume settings)") == "true"
                self._osa(f"set volume output muted {'false' if muted else 'true'}")
                return
            ep = self._endpoint()
            ep.SetMute(0 if ep.GetMute() else 1, None)
        except Exception:
            self._ep = None

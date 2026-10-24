"""Windows master volume / mute (Core Audio), used to show the knob state."""


class Volume:
    def __init__(self):
        self._ep = None

    def _endpoint(self):
        if self._ep is None:
            from pycaw.pycaw import AudioUtilities
            self._ep = AudioUtilities.GetSpeakers().EndpointVolume
        return self._ep

    def read(self):
        """(percent 0..100, muted) or None when no audio device is available."""
        try:
            ep = self._endpoint()
            return round(ep.GetMasterVolumeLevelScalar() * 100), bool(ep.GetMute())
        except Exception:
            self._ep = None
            return None

    def toggle_mute(self):
        try:
            ep = self._endpoint()
            ep.SetMute(0 if ep.GetMute() else 1, None)
        except Exception:
            self._ep = None

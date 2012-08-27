"""CameraState
Constants for camera state
"""
import gettext
t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext
Idle = 0
Waiting = 1
Exposing = 2
Reading = 3
Downloading = 4
Error = 5
Busy = 5

State = (_("Idle"), _("Waiting"), _("Exposing"), _("Reading"), _("Downloading"), _("Error"), _("Busy"))

"""Pure Python mock of Texas Instruments ti_hub module for TI-84 Plus CE / Evo Python.
Headless PC execution without external dependencies.
Compliant with Python 3.4 (no f-strings, no re module).
"""

_connected = False
_history = []
_light_state = "off"
_color = (0, 0, 0)


def connect(port=""):
    """Simulate connection to TI-Innovator Hub."""
    global _connected
    _connected = True
    _history.append(("connect", str(port)))
    return True


def sleep(duration=0):
    """Simulate hub delay."""
    _history.append(("sleep", float(duration)))


def sound(freq, duration=0):
    """Simulate tone generation."""
    _history.append(("sound", float(freq), float(duration)))


def send(command):
    """Send command to hub."""
    _history.append(("send", str(command)))


def read(sensor_name):
    """Read simulated value from sensor."""
    _history.append(("read", str(sensor_name)))
    return 0.0


def light(state):
    """Control built-in LED/light."""
    global _light_state
    _light_state = str(state)
    _history.append(("light", _light_state))


def color(r, g=None, b=None):
    """Set RGB LED color."""
    global _color
    if isinstance(r, (tuple, list)) and len(r) == 3:
        _color = (int(r[0]), int(r[1]), int(r[2]))
    elif g is not None and b is not None:
        _color = (int(r), int(g), int(b))
    elif isinstance(r, int):
        _color = (r, r, r)
    _history.append(("color", _color))


# Mock testing helper functions
def get_history():
    """Return record of all function calls."""
    return list(_history)


def is_connected():
    """Return connection state."""
    return _connected


def reset():
    """Reset mock state to defaults."""
    global _connected, _history, _light_state, _color
    _connected = False
    _history = []
    _light_state = "off"
    _color = (0, 0, 0)

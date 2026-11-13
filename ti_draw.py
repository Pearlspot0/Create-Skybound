"""Pure Python mock of Texas Instruments ti_draw module for TI-84 Plus CE / Evo Python.
Headless PC execution without external dependencies.
Compliant with Python 3.4 (no f-strings, no re module).
"""

WIDTH = 320
HEIGHT = 240

_color = (0, 0, 0)
_pen_thickness = "thin"
_pen_style = "solid"
_window = (0, WIDTH, 0, HEIGHT)
_use_buffer = False
_history = []
_drawings = []


def clear():
    """Clear drawing canvas."""
    global _drawings
    _drawings = []
    _history.append(("clear",))


def set_color(r, g=None, b=None):
    """Set current drawing color.
    
    Accepts:
      set_color(r, g, b)
      set_color((r, g, b))
      set_color(palette_code)
    """
    global _color
    if isinstance(r, (tuple, list)) and len(r) == 3:
        _color = (int(r[0]), int(r[1]), int(r[2]))
    elif g is not None and b is not None:
        _color = (int(r), int(g), int(b))
    elif isinstance(r, int):
        # Palette index / grayscale
        _color = (r, r, r)
    _history.append(("set_color", _color))


def set_pen(thickness="thin", style="solid"):
    """Set pen thickness ('thin', 'medium', 'thick') and style ('solid', 'dot', 'dash')."""
    global _pen_thickness, _pen_style
    _pen_thickness = thickness
    _pen_style = style
    _history.append(("set_pen", thickness, style))


def set_window(xmin, xmax, ymin, ymax):
    """Set user coordinate window mapping."""
    global _window
    _window = (float(xmin), float(xmax), float(ymin), float(ymax))
    _history.append(("set_window", _window))


def draw_line(x1, y1, x2, y2):
    """Draw a straight line from (x1, y1) to (x2, y2)."""
    entry = ("draw_line", float(x1), float(y1), float(x2), float(y2), _color, _pen_thickness, _pen_style)
    _drawings.append(entry)
    _history.append(entry)


def draw_rect(x, y, w, h):
    """Draw rectangle outline."""
    entry = ("draw_rect", float(x), float(y), float(w), float(h), _color, _pen_thickness)
    _drawings.append(entry)
    _history.append(entry)


def fill_rect(x, y, w, h):
    """Fill rectangle."""
    entry = ("fill_rect", float(x), float(y), float(w), float(h), _color)
    _drawings.append(entry)
    _history.append(entry)


def draw_circle(x, y, r):
    """Draw circle outline."""
    entry = ("draw_circle", float(x), float(y), float(r), _color, _pen_thickness)
    _drawings.append(entry)
    _history.append(entry)


def fill_circle(x, y, r):
    """Fill circle."""
    entry = ("fill_circle", float(x), float(y), float(r), _color)
    _drawings.append(entry)
    _history.append(entry)


def draw_arc(x, y, r, start_angle, end_angle):
    """Draw arc outline."""
    entry = ("draw_arc", float(x), float(y), float(r), float(start_angle), float(end_angle), _color)
    _drawings.append(entry)
    _history.append(entry)


def fill_arc(x, y, r, start_angle, end_angle):
    """Fill arc."""
    entry = ("fill_arc", float(x), float(y), float(r), float(start_angle), float(end_angle), _color)
    _drawings.append(entry)
    _history.append(entry)


def draw_poly(x_pts, y_pts=None):
    """Draw polygon outline from points."""
    if y_pts is None:
        pts = list(x_pts)
    else:
        pts = list(zip(x_pts, y_pts))
    entry = ("draw_poly", pts, _color, _pen_thickness)
    _drawings.append(entry)
    _history.append(entry)


def fill_poly(x_pts, y_pts=None):
    """Fill polygon from points."""
    if y_pts is None:
        pts = list(x_pts)
    else:
        pts = list(zip(x_pts, y_pts))
    entry = ("fill_poly", pts, _color)
    _drawings.append(entry)
    _history.append(entry)


def draw_text(x, y, text):
    """Draw text string at coordinate (x, y)."""
    entry = ("draw_text", float(x), float(y), str(text), _color)
    _drawings.append(entry)
    _history.append(entry)


def use_buffer():
    """Enable double buffering."""
    global _use_buffer
    _use_buffer = True
    _history.append(("use_buffer",))


def paint_buffer():
    """Flush double buffer to display."""
    _history.append(("paint_buffer",))


# Mock testing helper functions
def get_history():
    """Return record of all function calls."""
    return list(_history)


def get_drawings():
    """Return list of active drawing primitives."""
    return list(_drawings)


def get_color():
    """Return current color tuple."""
    return _color


def get_pen():
    """Return current pen thickness and style."""
    return _pen_thickness, _pen_style


def get_window():
    """Return current window coordinate tuple."""
    return _window


def reset():
    """Reset mock state to defaults."""
    global _color, _pen_thickness, _pen_style, _window, _use_buffer, _history, _drawings
    _color = (0, 0, 0)
    _pen_thickness = "thin"
    _pen_style = "solid"
    _window = (0, WIDTH, 0, HEIGHT)
    _use_buffer = False
    _history = []
    _drawings = []

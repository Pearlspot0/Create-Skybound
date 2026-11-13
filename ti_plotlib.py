"""Pure Python mock of Texas Instruments ti_plotlib module for TI-84 Plus CE / Evo Python.
Headless PC execution without external dependencies.
Compliant with Python 3.4 (no f-strings, no re module).
"""

_window = (-10.0, 10.0, -10.0, 10.0)
_axes_mode = "off"
_grid_settings = None
_title_text = ""
_labels_settings = None
_color = (0, 0, 0)
_pen = (1, "solid")
_plots = []
_shown = False
_history = []


def cls():
    """Clear plotting canvas and stored plots."""
    global _plots, _shown
    _plots = []
    _shown = False
    _history.append(("cls",))


def window(xmin, xmax, ymin, ymax):
    """Set plotting coordinates manually."""
    global _window
    _window = (float(xmin), float(xmax), float(ymin), float(ymax))
    _history.append(("window", _window))


def auto_window(xs, ys):
    """Automatically calculate and set viewing window boundaries."""
    global _window
    x_list = list(xs)
    y_list = list(ys)
    if not x_list or not y_list:
        return
    min_x, max_x = min(x_list), max(x_list)
    min_y, max_y = min(y_list), max(y_list)
    dx = (max_x - min_x) * 0.1 if max_x != min_x else 1.0
    dy = (max_y - min_y) * 0.1 if max_y != min_y else 1.0
    _window = (float(min_x - dx), float(max_x + dx), float(min_y - dy), float(max_y + dy))
    _history.append(("auto_window", _window))


def axes(mode="on"):
    """Enable or disable coordinate axes."""
    global _axes_mode
    _axes_mode = str(mode)
    _history.append(("axes", _axes_mode))


def grid(x_scale=1, y_scale=1, style="dot"):
    """Set background grid."""
    global _grid_settings
    _grid_settings = (float(x_scale), float(y_scale), str(style))
    _history.append(("grid", _grid_settings))


def title(text):
    """Set graph title."""
    global _title_text
    _title_text = str(text)
    _history.append(("title", _title_text))


def labels(xlabel="", ylabel="", xloc=0, yloc=0):
    """Set axis labels."""
    global _labels_settings
    _labels_settings = (str(xlabel), str(ylabel), float(xloc), float(yloc))
    _history.append(("labels", _labels_settings))


def color(r, g=None, b=None):
    """Set plot color."""
    global _color
    if isinstance(r, (tuple, list)) and len(r) == 3:
        _color = (int(r[0]), int(r[1]), int(r[2]))
    elif g is not None and b is not None:
        _color = (int(r), int(g), int(b))
    elif isinstance(r, int):
        _color = (r, r, r)
    _history.append(("color", _color))


def pen(thickness=1, style="solid"):
    """Set pen thickness and style."""
    global _pen
    _pen = (thickness, str(style))
    _history.append(("pen", _pen))


def plot(xs, ys, mark=""):
    """Plot connected line segments or marked points."""
    entry = ("plot", list(xs), list(ys), str(mark), _color, _pen)
    _plots.append(entry)
    _history.append(entry)


def line(xs, ys):
    """Draw continuous line through points."""
    entry = ("line", list(xs), list(ys), _color, _pen)
    _plots.append(entry)
    _history.append(entry)


def scatter(xs, ys, mark="o"):
    """Draw unconnected scatter plot points."""
    entry = ("scatter", list(xs), list(ys), str(mark), _color)
    _plots.append(entry)
    _history.append(entry)


def show_plot():
    """Render and display buffered plot."""
    global _shown
    _shown = True
    _history.append(("show_plot",))


def lin_reg(xs, ys):
    """Calculate linear regression y = a*x + b."""
    x_list = [float(x) for x in xs]
    y_list = [float(y) for y in ys]
    n = len(x_list)
    if n == 0:
        return 0.0, 0.0
    mean_x = sum(x_list) / n
    mean_y = sum(y_list) / n
    ss_xx = sum((x - mean_x) ** 2 for x in x_list)
    ss_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_list, y_list))
    if ss_xx == 0.0:
        return 0.0, mean_y
    slope = ss_xy / ss_xx
    intercept = mean_y - slope * mean_x
    _history.append(("lin_reg", slope, intercept))
    return slope, intercept


# Mock testing helper functions
def get_history():
    """Return record of all function calls."""
    return list(_history)


def get_plots():
    """Return recorded plot calls."""
    return list(_plots)


def get_window():
    """Return current window coordinate tuple."""
    return _window


def is_shown():
    """Check if show_plot() was invoked."""
    return _shown


def reset():
    """Reset mock state to defaults."""
    global _window, _axes_mode, _grid_settings, _title_text, _labels_settings
    global _color, _pen, _plots, _shown, _history
    _window = (-10.0, 10.0, -10.0, 10.0)
    _axes_mode = "off"
    _grid_settings = None
    _title_text = ""
    _labels_settings = None
    _color = (0, 0, 0)
    _pen = (1, "solid")
    _plots = []
    _shown = False
    _history = []

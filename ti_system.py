"""Pure Python mock of Texas Instruments ti_system module for TI-84 Plus CE / Evo Python.
Headless PC execution without external dependencies.
Compliant with Python 3.4 (no f-strings, no re module).
"""

# Screen dimensions for TI-84 CE text shell: 10 rows x 26 cols (or 11 x 32)
_NUM_ROWS = 11
_NUM_COLS = 32

_screen_buffer = [" " * _NUM_COLS for _ in range(_NUM_ROWS)]
_stored_lists = {}
_stored_values = {}
_key_queue = []
_history = []
_cursor_state = False


def disp_clr(row=None):
    """Clear entire screen or a specific row (1-indexed)."""
    global _screen_buffer
    _history.append(("disp_clr", row))
    if row is None:
        _screen_buffer = [" " * _NUM_COLS for _ in range(_NUM_ROWS)]
    else:
        idx = int(row) - 1
        if 0 <= idx < len(_screen_buffer):
            _screen_buffer[idx] = " " * _NUM_COLS


def disp_at(row, col_or_text, text=None, align="left"):
    """Display text at row (1-indexed) and optional col (1-indexed).
    
    Supports:
        disp_at(row, col, text, align="left")
        disp_at(row, text, align="left")
    """
    global _screen_buffer
    row_idx = int(row) - 1
    if not (0 <= row_idx < len(_screen_buffer)):
        return

    if text is None:
        # disp_at(row, text, align)
        msg = str(col_or_text)
        align_mode = align
        col_idx = 0
    elif text in ("left", "center", "right") and not isinstance(col_or_text, int):
        # disp_at(row, text, align) with positional align
        msg = str(col_or_text)
        align_mode = text
        col_idx = 0
    else:
        # disp_at(row, col, text, align)
        try:
            col_idx = int(col_or_text) - 1
            msg = str(text)
            align_mode = align
        except (ValueError, TypeError):
            col_idx = 0
            msg = str(col_or_text)
            align_mode = str(text)

    _history.append(("disp_at", row, col_or_text, text, align_mode))

    if align_mode == "center":
        start_col = max(0, (_NUM_COLS - len(msg)) // 2)
    elif align_mode == "right":
        start_col = max(0, _NUM_COLS - len(msg))
    else:
        start_col = max(0, col_idx)

    curr_line = list(_screen_buffer[row_idx])
    for i, ch in enumerate(msg):
        pos = start_col + i
        if pos < len(curr_line):
            curr_line[pos] = ch
    _screen_buffer[row_idx] = "".join(curr_line)


def disp_cursor(on_off=None):
    """Enable or disable screen cursor."""
    global _cursor_state
    _history.append(("disp_cursor", on_off))
    if on_off is not None:
        _cursor_state = bool(on_off)
    return _cursor_state


def disp_wait():
    """Wait for key press and return key."""
    _history.append(("disp_wait",))
    if _key_queue:
        return _key_queue.pop(0)
    return ""


def get_key(mode=0):
    """Poll or wait for key press.
    
    mode=0: non-blocking, returns "" if no key.
    mode=1: blocking, returns next key.
    """
    _history.append(("get_key", mode))
    if _key_queue:
        return _key_queue.pop(0)
    return ""


def recall_list(name):
    """Recall list variable from calculator memory."""
    name_str = str(name)
    _history.append(("recall_list", name_str))
    return list(_stored_lists.get(name_str, []))


def store_list(name, list_data):
    """Store list variable into calculator memory."""
    name_str = str(name)
    data = [float(x) if isinstance(x, (int, float)) else x for x in list_data]
    _stored_lists[name_str] = data
    _history.append(("store_list", name_str, data))


def recall_value(name):
    """Recall numeric/string variable from calculator memory."""
    name_str = str(name)
    _history.append(("recall_value", name_str))
    return _stored_values.get(name_str, 0.0)


def store_value(name, val):
    """Store numeric/string variable into calculator memory."""
    name_str = str(name)
    _stored_values[name_str] = val
    _history.append(("store_value", name_str, val))


# Mock testing helper functions
def push_key(key):
    """Queue key for get_key() / disp_wait()."""
    _key_queue.append(str(key))


def set_keys(keys):
    """Set the full queue of mock keys."""
    global _key_queue
    _key_queue = [str(k) for k in keys]


def get_screen():
    """Return current screen buffer as list of strings."""
    return list(_screen_buffer)


def get_screen_text():
    """Return current screen buffer as joined multiline string."""
    return "\n".join(_screen_buffer)


def get_history():
    """Return record of all function calls."""
    return list(_history)


def reset():
    """Reset mock state to defaults."""
    global _screen_buffer, _stored_lists, _stored_values, _key_queue, _history, _cursor_state
    _screen_buffer = [" " * _NUM_COLS for _ in range(_NUM_ROWS)]
    _stored_lists = {}
    _stored_values = {}
    _key_queue = []
    _history = []
    _cursor_state = False

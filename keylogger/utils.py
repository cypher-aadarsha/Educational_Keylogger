"""
Utility functions for the Educational Keyboard Input Logger.

Provides timestamp generation and key-name formatting helpers used
by the core logger and file manager modules.
"""

from datetime import datetime
from pynput.keyboard import Key

from keylogger.config import TIMESTAMP_FORMAT


def get_timestamp() -> str:
    """Return the current local time as a formatted string.

    Uses the format defined in ``config.TIMESTAMP_FORMAT``.

    Returns:
        str: Formatted timestamp, e.g. ``"2026-06-29 14:05:32"``.
    """
    return datetime.now().strftime(TIMESTAMP_FORMAT)


# Mapping of special pynput Key constants to human-readable labels.
# Keys not listed here will fall through to their `.name` attribute.
_SPECIAL_KEY_NAMES: dict[Key, str] = {
    Key.space: "SPACE",
    Key.enter: "ENTER",
    Key.tab: "TAB",
    Key.backspace: "BACKSPACE",
    Key.delete: "DELETE",
    Key.esc: "ESC",
    Key.shift: "SHIFT",
    Key.shift_r: "SHIFT_R",
    Key.ctrl_l: "CTRL_L",
    Key.ctrl_r: "CTRL_R",
    Key.alt_l: "ALT_L",
    Key.alt_r: "ALT_R",
    Key.caps_lock: "CAPS_LOCK",
    Key.up: "UP",
    Key.down: "DOWN",
    Key.left: "LEFT",
    Key.right: "RIGHT",
    Key.home: "HOME",
    Key.end: "END",
    Key.page_up: "PAGE_UP",
    Key.page_down: "PAGE_DOWN",
    Key.insert: "INSERT",
    Key.f1: "F1",
    Key.f2: "F2",
    Key.f3: "F3",
    Key.f4: "F4",
    Key.f5: "F5",
    Key.f6: "F6",
    Key.f7: "F7",
    Key.f8: "F8",
    Key.f9: "F9",
    Key.f10: "F10",
    Key.f11: "F11",
    Key.f12: "F12",
    Key.cmd: "CMD",
    Key.cmd_r: "CMD_R",
    Key.menu: "MENU",
    Key.num_lock: "NUM_LOCK",
    Key.scroll_lock: "SCROLL_LOCK",
    Key.print_screen: "PRINT_SCREEN",
    Key.pause: "PAUSE",
}


def format_key(key) -> str:
    """Convert a pynput key object into a human-readable string.

    Alphanumeric characters are returned as-is (e.g. ``"a"``, ``"B"``).
    Special keys are wrapped in square brackets (e.g. ``"[ENTER]"``).

    Args:
        key: A ``pynput.keyboard.Key`` or ``pynput.keyboard.KeyCode``
             object received from a listener callback.

    Returns:
        str: Human-readable representation of the key.
    """
    # Special key (Key.enter, Key.space, etc.)
    if isinstance(key, Key):
        label = _SPECIAL_KEY_NAMES.get(key, key.name.upper())
        return f"[{label}]"

    # Regular character key (KeyCode)
    try:
        char = key.char
        if char is not None:
            return char
        # char is None for some virtual key codes (e.g. media keys)
        return f"[VKEY_{key.vk}]" if key.vk is not None else "[UNKNOWN]"
    except AttributeError:
        return "[UNKNOWN]"

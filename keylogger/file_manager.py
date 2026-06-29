"""
File Manager module for the Educational Keyboard Input Logger.

Handles log file creation, writing, and automatic rotation.
A new timestamped log file is created every ``ROTATION_INTERVAL`` seconds
(default 30 minutes). Previous log files are never overwritten.
"""

import os
import time
from datetime import datetime

from keylogger.config import LOG_DIR, ROTATION_INTERVAL, FILE_NAME_FORMAT


class LogFileManager:
    """Manages the lifecycle of log files — creation, writing, and rotation.

    Attributes:
        log_dir (str): Absolute path to the directory that stores log files.
        rotation_interval (int): Seconds between file rotations.
        _current_file: The currently active file handle.
        _rotation_deadline (float): UNIX timestamp when the next rotation
            should occur.
    """

    def __init__(self) -> None:
        """Initialize the file manager and open the first log file.

        Creates the ``logs/`` directory if it does not already exist.

        Raises:
            OSError: If the log directory cannot be created.
        """
        self.log_dir: str = LOG_DIR
        self.rotation_interval: int = ROTATION_INTERVAL
        self._current_file = None
        self._rotation_deadline: float = 0.0

        # Ensure the output directory exists.
        os.makedirs(self.log_dir, exist_ok=True)

        # Open the first log file.
        self._create_new_file()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _create_new_file(self) -> None:
        """Close any open file and create a new timestamped log file.

        Writes a descriptive session header at the top of each new file
        so that analysts can quickly identify the logging session.
        """
        # Close the previous file, if one is open.
        if self._current_file is not None and not self._current_file.closed:
            self._current_file.close()

        # Build the filename from the current time.
        now = datetime.now()
        filename = now.strftime(FILE_NAME_FORMAT)
        filepath = os.path.join(self.log_dir, filename)

        # Open the new file and write a session header.
        self._current_file = open(filepath, "a", encoding="utf-8")
        self._current_file.write(
            f"{'=' * 72}\n"
            f"  Keyboard Input Log — Session started at {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"  File: {filename}\n"
            f"{'=' * 72}\n\n"
        )
        self._current_file.flush()

        # Set the next rotation deadline.
        self._rotation_deadline = time.time() + self.rotation_interval

        print(f"[INFO] Logging to: {filepath}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def write(self, text: str) -> None:
        """Write a line of text to the current log file.

        Before writing, checks whether the rotation interval has elapsed.
        If so, the current file is closed and a new one is opened.

        Args:
            text: The formatted log line to write (should include a
                  trailing newline).

        Raises:
            IOError: If writing to the file fails.
        """
        try:
            # Rotate if the interval has elapsed.
            if time.time() >= self._rotation_deadline:
                print("\n[INFO] 30-minute interval reached — rotating log file...")
                self._create_new_file()

            self._current_file.write(text)
            self._current_file.flush()

        except IOError as exc:
            print(f"[ERROR] Failed to write to log file: {exc}")
            raise

    def close(self) -> None:
        """Flush and close the active log file.

        Safe to call multiple times; subsequent calls are no-ops.
        """
        if self._current_file is not None and not self._current_file.closed:
            self._current_file.flush()
            self._current_file.close()
            print("[INFO] Log file closed.")

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self):
        """Enable use as a context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure the file is closed when exiting a ``with`` block."""
        self.close()
        return False  # Do not suppress exceptions.

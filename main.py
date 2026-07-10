#!/usr/bin/env python3
"""
Educational Keyboard Input Logger — Entry Point
================================================

University Cybersecurity Course Project

This application captures keyboard input events on the LOCAL system for
educational, defensive, and cybersecurity research purposes.  It is
designed to operate **only** with the user's explicit knowledge and
consent and should be tested exclusively in a controlled laboratory
environment.

Features:
    • Captures every key press with a precise timestamp.
    • Writes logs as human-readable plain-text (.txt) files.
    • Automatically rotates to a new log file every 30 minutes.
    • Preserves all previous log files (no overwriting).
    • Requires explicit user consent before starting.
    • Console window auto-hides after consent; press Ctrl+H to
      toggle visibility.

Usage:
    python main.py

Press Ctrl+C at any time to stop the logger gracefully.
Press Ctrl+H at any time to show/hide the console window.

DISCLAIMER:
    Unauthorized use of keylogging software is ILLEGAL in most
    jurisdictions.  The authors assume NO liability for misuse.
"""

import os
import sys
import time
import tkinter as tk
from tkinter import messagebox

from keylogger.config import CONSENT_BANNER, CONSENT_KEYWORD
from keylogger.file_manager import LogFileManager
from keylogger.logger import KeyboardLogger
from keylogger.window_manager import ConsoleWindowManager


def safe_print(msg: str) -> None:
    """Print to console only if sys.stdout is available (no-console builds)."""
    try:
        print(msg)
    except Exception:
        pass


def get_user_consent() -> bool:
    """Display a GUI consent dialog and return True if the user agrees.

    Uses tkinter so it works in both console and --noconsole (no sys.stdin)
    PyInstaller builds.

    Returns:
        bool: ``True`` if the user clicked Yes/Agree, ``False`` otherwise.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the blank root window

    # Build a readable message from the consent banner
    message = (
        "EDUCATIONAL KEYLOGGER — CONSENT REQUIRED\n"
        "─────────────────────────────────────────\n\n"
        "This tool is part of a University Cybersecurity Course Project.\n\n"
        "It will:\n"
        "  • Capture every key press with a timestamp\n"
        "  • Write logs to a local 'logs/' folder\n"
        "  • Rotate log files every 30 minutes\n\n"
        "⚠  Unauthorized use of keylogging software is ILLEGAL.\n"
        "    Use only on YOUR OWN system in a controlled environment.\n\n"
        "Do you understand and consent to proceed?"
    )

    result = messagebox.askyesno(
        title="Educational Keylogger — Consent",
        message=message,
        icon=messagebox.WARNING
    )

    root.destroy()
    return result


def show_info(title: str, message: str) -> None:
    """Show a simple informational GUI popup."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title=title, message=message)
    root.destroy()


def show_error(title: str, message: str) -> None:
    """Show a GUI error popup."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title=title, message=message)
    root.destroy()


def main() -> None:
    """Application entry point.

    Workflow:
        1. Display the consent dialog and obtain explicit permission.
        2. Initialize the window manager and auto-hide the console.
        3. Initialize the file manager (creates ``logs/`` directory).
        4. Start the keyboard listener.
        5. Wait for Ctrl+C, then shut down cleanly.
    """
    # ── Step 1: Obtain consent ────────────────────────────────────────
    if not get_user_consent():
        show_info(
            "Educational Keylogger",
            "Consent not granted.\nNo data has been captured.\n\nGoodbye."
        )
        safe_print("[INFO] Consent not granted.  No data has been captured.  Goodbye.")
        sys.exit(0)

    safe_print("\n[INFO] Consent granted.  Initializing logger...")

    # ── Step 2: Initialize window manager and auto-hide ───────────────
    window_manager = ConsoleWindowManager()

    if window_manager.is_supported:
        safe_print("[INFO] Console will hide in 2 seconds.  Press Ctrl+H to show it again.\n")
        time.sleep(2)
        window_manager.hide()
    else:
        safe_print("[INFO] Console hiding is not supported on this platform.\n")

    # ── Step 3–4: Initialize and start ────────────────────────────────
    file_manager = None
    logger = None

    try:
        file_manager = LogFileManager()
        logger = KeyboardLogger(file_manager, window_manager)
        logger.start()

        # Block the main thread until the user interrupts.
        logger._listener.join()

    except KeyboardInterrupt:
        safe_print("\n\n[INFO] Ctrl+C detected — shutting down gracefully...")

    except Exception as exc:
        safe_print(f"\n[ERROR] An unexpected error occurred: {exc}")
        show_error("Educational Keylogger — Error", f"An unexpected error occurred:\n\n{exc}")
        sys.exit(1)

    finally:
        # ── Step 5: Clean shutdown ────────────────────────────────────
        if logger is not None:
            logger.stop()
        elif file_manager is not None:
            file_manager.close()

    safe_print("[INFO] Application terminated successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # ── Last-resort crash handler ─────────────────────────────────
        # In a --noconsole PyInstaller build, unhandled exceptions vanish
        # silently. Write them to a file AND show a popup so the user
        # always gets feedback.
        import traceback
        from keylogger.config import _BASE_DIR

        crash_log = os.path.join(_BASE_DIR, "error_log.txt")
        try:
            with open(crash_log, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"  Crash at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*60}\n")
                traceback.print_exc(file=f)
        except Exception:
            pass

        try:
            show_error(
                "Educational Keylogger — Fatal Error",
                f"The application crashed:\n\n{exc}\n\nDetails saved to:\n{crash_log}"
            )
        except Exception:
            pass
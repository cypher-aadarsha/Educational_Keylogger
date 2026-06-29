"""
Configuration module for the Educational Keyboard Input Logger.

Centralizes all tuneable constants used across the application.
Modify these values to adjust logging behavior, file paths, and
timestamp formatting.

IMPORTANT: This application is intended for educational and research
purposes only. Use exclusively in controlled laboratory environments
with explicit user consent.
"""

import os

# ---------------------------------------------------------------------------
# Directory Settings
# ---------------------------------------------------------------------------

# Base directory where all log files will be stored.
# Resolved relative to the project root (where main.py is located).
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")

# ---------------------------------------------------------------------------
# Rotation Settings
# ---------------------------------------------------------------------------

# How often (in seconds) to rotate to a new log file.
# Default: 1800 seconds = 30 minutes.
ROTATION_INTERVAL = 1800

# ---------------------------------------------------------------------------
# Timestamp & Filename Formatting
# ---------------------------------------------------------------------------

# Format string for per-event timestamps written inside log files.
# Example output: "2026-06-29 14:05:32"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

# Format string for log filenames.
# Example output: "keylog_2026-06-29_14-05-32.txt"
FILE_NAME_FORMAT = "keylog_%Y-%m-%d_%H-%M-%S.txt"

# ---------------------------------------------------------------------------
# Consent Banner
# ---------------------------------------------------------------------------

CONSENT_BANNER = """
================================================================================
          EDUCATIONAL KEYBOARD INPUT LOGGER — CYBERSECURITY LAB TOOL
================================================================================

PURPOSE:
  This application captures keyboard input events on the LOCAL system for
  educational, defensive, and cybersecurity research purposes as part of a
  university course project.

WHAT IT DOES:
  • Records every key press with a timestamp.
  • Saves logs as plain-text (.txt) files in the 'logs/' directory.
  • Rotates to a new log file every 30 minutes (previous files are preserved).
  • Runs until you press Ctrl+C to stop.

ETHICAL NOTICE:
  • This tool must ONLY be used in a controlled laboratory environment.
  • You must have EXPLICIT CONSENT from every user of this machine.
  • Unauthorized use of keylogging software is ILLEGAL in most jurisdictions.
  • The developers assume NO liability for misuse of this software.

================================================================================
"""

# The exact string the user must type to grant consent.
CONSENT_KEYWORD = "YES"

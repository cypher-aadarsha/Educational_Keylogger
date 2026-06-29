# Educational Keyboard Input Logger

> **Cybersecurity Project**

A Python-based keyboard input logging application designed for **educational, defensive, and cybersecurity research purposes**. This tool captures keyboard events on the local system with explicit user consent and logs them to timestamped plain-text files.

---

## ⚠️ Ethical & Legal Disclaimer

> **This software is provided strictly for educational use within controlled laboratory environments.**
>
> - **Do NOT** deploy this tool on any system without the explicit knowledge and consent of **every** user of that system.
> - Unauthorized use of keylogging software is **illegal** in most jurisdictions and may result in criminal prosecution.
> - The developers assume **NO liability** for any misuse of this software.
> - By running this application, you acknowledge that you are using it solely for authorized educational or research purposes.

---

## Features

| Feature | Description |
|---|---|
| 🔑 **Key Capture** | Records every key press — alphanumeric, special keys, function keys |
| ⏱️ **Timestamps** | Each event is logged with a precise `YYYY-MM-DD HH:MM:SS` timestamp |
| 🔄 **Auto-Rotation** | Creates a new log file every 30 minutes — no data is ever overwritten |
| 📂 **Organized Logs** | Files are stored in `logs/` with descriptive names like `keylog_2026-06-29_14-05-32.txt` |
| ✅ **Consent Gate** | Application will NOT start until the user explicitly types `YES` |
| 🪟 **Auto-Hide Console** | Console hides automatically after consent; **Ctrl+H** toggles visibility |
| 🛡️ **Error Handling** | Robust exception handling ensures clean shutdown on errors |
| 📖 **Documentation** | Every module, class, and function has comprehensive docstrings |

---

## Project Structure

```
Educational_Keylogger/
├── main.py                    # Entry point — consent prompt & orchestration
├── keylogger/
│   ├── __init__.py            # Package initializer
│   ├── config.py              # Constants and configuration
│   ├── utils.py               # Timestamp & key formatting helpers
│   ├── file_manager.py        # Log file creation, writing, and rotation
│   └── logger.py              # Core keyboard capture engine
├── logs/                      # Auto-created directory for log output
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Prerequisites

- **Python 3.10+** (tested on 3.10, 3.11, 3.12)
- **pip** (Python package manager)
- **Operating System**: Windows, macOS, or Linux
  - On Linux, you may need to run with `sudo` or add your user to the `input` group for keyboard access.

---

## Installation

1. **Clone or download** this repository:
   ```bash
   cd "e:\Python Projects\Educational_Keylogger"
   ```

2. **(Recommended) Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Starting the Logger

```bash
python main.py
```

You will be presented with a consent banner explaining exactly what the application does. Type `YES` to proceed or anything else to exit safely.

### Sample Console Output

```
================================================================================
          EDUCATIONAL KEYBOARD INPUT LOGGER — CYBERSECURITY LAB TOOL
================================================================================

PURPOSE:
  This application captures keyboard input events on the LOCAL system for
  educational, defensive, and cybersecurity research purposes...

================================================================================

Type "YES" to confirm you understand and consent, or anything else to exit: YES

[INFO] Consent granted.  Initializing logger...
[INFO] Console will hide in 2 seconds.  Press Ctrl+H to show it again.

[INFO] Logging to: e:\Python Projects\Educational_Keylogger\logs\keylog_2026-06-29_14-05-32.txt
[INFO] Keyboard listener started.  Press Ctrl+C to stop.
[INFO] Press Ctrl+H to toggle console visibility.
```

> **Note:** After you type `YES`, the console window will automatically hide after 2 seconds. The logger continues running silently in the background. Press **Ctrl+H** at any time to show/hide the console window.

### Stopping the Logger

Press **Ctrl+H** first to show the console (if hidden), then press **Ctrl+C**. The application will:
1. Stop the keyboard listener.
2. Flush and close the current log file.
3. Print a summary of keys captured.

---

## Log File Format

Each log file is a plain-text `.txt` file with the following structure:

```
========================================================================
  Keyboard Input Log — Session started at 2026-06-29 14:05:32
  File: keylog_2026-06-29_14-05-32.txt
========================================================================

[2026-06-29 14:05:33]  h
[2026-06-29 14:05:33]  e
[2026-06-29 14:05:34]  l
[2026-06-29 14:05:34]  l
[2026-06-29 14:05:34]  o
[2026-06-29 14:05:35]  [SPACE]
[2026-06-29 14:05:36]  w
[2026-06-29 14:05:36]  o
[2026-06-29 14:05:37]  r
[2026-06-29 14:05:37]  l
[2026-06-29 14:05:37]  d
[2026-06-29 14:05:38]  [ENTER]
```

### Key Representation

| Key Type | Example Output |
|---|---|
| Letters | `a`, `B`, `z` |
| Numbers | `1`, `9`, `0` |
| Symbols | `!`, `@`, `#` |
| Space | `[SPACE]` |
| Enter | `[ENTER]` |
| Backspace | `[BACKSPACE]` |
| Modifier keys | `[SHIFT]`, `[CTRL_L]`, `[ALT_R]` |
| Function keys | `[F1]` through `[F12]` |
| Arrow keys | `[UP]`, `[DOWN]`, `[LEFT]`, `[RIGHT]` |

---

## Configuration

All tuneable parameters are in [`keylogger/config.py`](keylogger/config.py):

| Parameter | Default | Description |
|---|---|---|
| `LOG_DIR` | `./logs` | Directory where log files are stored |
| `ROTATION_INTERVAL` | `1800` (30 min) | Seconds between log file rotations |
| `TIMESTAMP_FORMAT` | `%Y-%m-%d %H:%M:%S` | Per-event timestamp format |
| `FILE_NAME_FORMAT` | `keylog_%Y-%m-%d_%H-%M-%S.txt` | Log filename pattern |

### Testing Rotation Quickly

To verify file rotation without waiting 30 minutes, temporarily reduce the interval in `config.py`:

```python
ROTATION_INTERVAL = 10  # Rotate every 10 seconds for testing
```

---

## Module Documentation

### `main.py`
Entry point. Displays the consent banner, prompts for explicit agreement, initializes the logger, and handles graceful shutdown via Ctrl+C.

### `keylogger/config.py`
Centralizes all configuration constants — paths, intervals, formats, and the consent banner text.

### `keylogger/utils.py`
Provides `get_timestamp()` for formatted time strings and `format_key()` for converting pynput key objects to human-readable labels.

### `keylogger/file_manager.py`
`LogFileManager` class handles log file creation with session headers, automatic rotation after the configured interval, and context manager support.

### `keylogger/logger.py`
`KeyboardLogger` class bridges pynput's keyboard listener with the file manager. Each key press is formatted, timestamped, and written to the current log file.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'pynput'` | Run `pip install -r requirements.txt` |
| `Permission denied` on Linux | Run with `sudo` or add your user to the `input` group |
| No keys being captured | Ensure no other application is intercepting keyboard events |
| Log directory not created | Check write permissions in the project directory |

---

## License

This project is developed as part of a university cybersecurity course by [cypher-aadarsha](https://github.com/cypher-aadarsha) and is provided **as-is** for educational purposes only.

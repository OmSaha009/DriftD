# 🚗 Driftd

**I built this because I'm lazy.**

During online classes, I got tired of reaching for my laptop just to change volume or brightness. So I built Driftd – a voice-controlled time tracker that runs in the background and obeys voice commands.

---

## ✨ Features

| Mode | What it does |
|------|--------------|
| **Daemon** | Tracks active windows every 2 seconds → logs to SQLite |
| **Analyzer** | Shows how you spent your time (study vs social vs gaming) |
| **Listener** | Push-to-talk voice control (hold `` ` `` or F8) |

### Voice Commands

```
"volume up" / "volume down"
"mute"
"light" / "dark"          (brightness control)
"focus mode on" / "off"   (blocks distracting websites)
```

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/OmSaha009/driftd.git
cd driftd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run

```bash
# Background tracking (default)
python main.py

# View your day
python main.py --report

# Voice control
python main.py --listen
```

### 3. First-Time Setup

- **Voice control** downloads Whisper model (~145MB) on first run
- **Focus mode** requires **administrator** (modifies hosts file)
- **Microphone** needs Windows permission (Settings → Privacy → Microphone)

---

## Usage

### Three Modes

| Command | Mode | What happens |
|---------|------|--------------|
| `python main.py` | Daemon | Tracks silently in background |
| `python main.py --report` | Analyzer | Prints today's + weekly summary |
| `python main.py --listen` | Listener | Push-to-talk voice control |

### Voice Control (Listener Mode)

1. Hold `` ` `` (backtick) or `F8`
2. Speak clearly: *"volume up"*
3. Release – command executes

**Works from across the room.**

### Focus Mode

Blocks: YouTube, Instagram, Twitter, Reddit, Facebook

```bash
# Terminal control (requires admin)
python main.py --listen
# Then say "focus mode on"
```

**Note:** Chrome/Edge may bypass hosts file due to DNS-over-HTTPS.  
**Fix:** Disable "Use secure DNS" in `chrome://settings/security`

---

## Project Structure

```
driftd/
├── main.py           # CLI entry point (3 modes)
├── config.py         # Categories, paths, settings
├── tracker.py        # Window tracking + SQLite
├── analyzer.py       # Usage reports
├── controller.py     # Volume, brightness, focus mode
├── recorder.py       # Whisper + push-to-talk
├── data/
│   └── usage.db      # Your tracked sessions
└── requirements.txt
```

---

## What I Learned

- **Threading** – Background tracker without blocking main thread
- **SQLite** – Session logging, aggregations, date filtering
- **OOP** – Single responsibility, dependency injection
- **Voice recognition** – Whisper (offline, accurate)
- **Windows API** – Volume/brightness via PowerShell, window tracking via `win32gui`
- **CLI design** – argparse with three clean modes

---

## Limitations

| Issue | Status |
|-------|--------|
| Chrome/Edge bypass hosts file | Works in Firefox, partial in Chrome |
| Whisper has 1-2s delay | Normal for local LLM |
| One mode at a time per terminal | Use multiple terminal windows |
| Windows only | No Mac/Linux support |

---

## Requirements

```
python >= 3.10
openai-whisper
sounddevice
keyboard
pywin32
psutil
numpy
```

---

## Credits

- [OpenAI Whisper](https://github.com/openai/whisper) – Offline STT
- [pywin32](https://github.com/mhammond/pywin32) – Windows API
- [sounddevice](https://github.com/spatialaudio/python-sounddevice) – Audio recording
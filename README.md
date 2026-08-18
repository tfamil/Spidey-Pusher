# Spidey-Pusher
# 🕷️ Spidey Pusher

A borderless, always-on-top desktop overlay that reminds you to push your code to GitHub every day at 5:00 PM — Spider-Man-style.

Spider-Man descends from the top of your screen on a web line, lands, and a spider-web text panel asks:

> **DID YOU PUSH YOUR CODES IN YOUR GITHUB REPO?**

You answer with **YES** or **NO**.

## What it does

- **Transparent overlay** — no window chrome, no background panel. Only Spider-Man and the text are visible; your desktop shows through everywhere else.
- **Descends from the top of your screen** — the window is anchored to the very top edge, so it looks like he's genuinely swinging in from above, not popping up in the middle of the screen.
- **Spider-web styled text** — the reminder is framed in hand-drawn web strands instead of a plain box.
- **YES** → closes the app immediately. You're done for the day.
- **NO** → hides the window and snoozes for 5 minutes, then brings Spider-Man back down to ask again. Repeats until you click YES.
- **Runs on a schedule** — a Task Scheduler entry triggers it daily at 5:00 PM, and catches up automatically if your laptop was asleep at that time.

## Files

| File | Purpose |
|---|---|
| `spidey_pusher.py` | The Tkinter app itself |
| `image_0.png` | Transparent Spider-Man graphic used by the app |
| `requirements.txt` | Python dependencies (Pillow) |
| `setup_push_scheduler.ps1` | Registers the daily 5 PM Windows Task Scheduler job |

## Requirements

- Windows (the transparent-overlay effect relies on a Windows-only Tkinter attribute)
- Python 3.8+
- [Pillow](https://pypi.org/project/Pillow/)

## Setup

1. Clone or download this repo into a folder, e.g. `C:\Users\you\spidey`.
2. Install dependencies:
   ```powershell
   cd C:\Users\you\spidey
   python -m pip install -r requirements.txt
   ```
3. Test it manually:
   ```powershell
   python spidey_pusher.py
   ```
4. (Optional) Schedule it to run automatically every day at 5:00 PM:
   - Open PowerShell **as Administrator**
   - Navigate to the project folder
   - Allow the script to run once: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
   - Run: `.\setup_push_scheduler.ps1`

This registers a scheduled task named **`Github_Push_Guard_Spidey`** that runs daily at 5:00 PM, runs on battery power too, and fires as soon as possible if the computer was asleep at the scheduled time.

## Uninstalling the scheduled task

```powershell
Unregister-ScheduledTask -TaskName "Github_Push_Guard_Spidey" -Confirm:$false
```

## Notes

- Press `Esc` at any time to close the app (same as clicking YES).
- The app writes a short warning to the console (not a popup) if `image_0.png` is missing or Pillow isn't installed, and falls back to a simple placeholder shape so it still runs.

# Spidey Push Guard 🕷️

A small Windows accountability tool that drops a transparent, always-on-top Spider-Man-style reminder onto your desktop and asks one question: **did you push your code to GitHub?**

The included PowerShell installer can register the reminder with Windows Task Scheduler so it appears every day at **5:00 PM**. Press **YES** to dismiss it for the day, or **NO** to snooze it for five minutes and let it come back.

> This project is a reminder, not a GitHub client. It does not inspect your repositories, verify commits, push code, track contribution streaks, or know whether you have been hired.

## What it does

- Creates a borderless Tkinter desktop overlay.
- Keeps the overlay above other windows.
- Uses Windows' transparent-color support so only the image, web graphics, text, and buttons are visible.
- Animates the bundled image down from the top of the screen over roughly three seconds.
- Draws a simple spider-web pattern behind the reminder text.
- Shows **YES** and **NO** controls.
- **YES** exits the reminder.
- **NO** hides it for five minutes, then rebuilds and replays the reminder.
- **Esc** behaves like **YES** and closes the reminder.
- Includes a PowerShell script that registers a daily Windows Scheduled Task.

## How the scheduled reminder works

`setup_push_scheduler.ps1` creates a task named:

```text
Github_Push_Guard_Spidey
```

The task is configured to:

- run every day at **5:00 PM**;
- start when available after a missed scheduled time;
- run on battery power;
- run only as the current interactive user so the GUI is visible;
- ignore a new launch if another instance is already running.

The scheduled action uses the Python interpreter found on your `PATH` and launches `spidey_pusher.py` from the project directory.

## Project structure

```text
spidey-push-guard/
├── image_0.png
├── requirements.txt
├── setup_push_scheduler.ps1
└── spidey_pusher.py
```

## Requirements

- Windows 10/11 recommended
- Python 3
- Tkinter (normally included with the standard Windows Python installer)
- Pillow

The transparent desktop effect relies on Tkinter's Windows-only `-transparentcolor` attribute. On other operating systems, the Python script falls back to an opaque dark background.

## Setup

Clone or download the project, open PowerShell in the project directory, and install the Python dependency:

```powershell
python -m pip install -r requirements.txt
```

Then test the reminder manually:

```powershell
python .\spidey_pusher.py
```

You should see the image descend from the top of the screen, followed by the GitHub reminder and the **YES / NO** buttons.

## Install the 5 PM Windows task

The provided installer intentionally requires an elevated PowerShell window.

1. Open **PowerShell as Administrator**.
2. Change into the project directory.
3. Run:

```powershell
.\setup_push_scheduler.ps1
```

If PowerShell blocks script execution for the current process, you can temporarily allow it with:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run the setup script again.

## Controls

| Action | Result |
|---|---|
| **YES** | Closes the reminder process for that run |
| **NO** | Hides the window and brings it back after 5 minutes |
| **Esc** | Same behavior as **YES** |

## Customization

The main settings are near the top of `spidey_pusher.py`:

```python
SPIDEY_MAX_WIDTH = 260
DESCEND_DURATION_MS = 3000
DESCEND_FPS = 60
SNOOZE_MS = 5 * 60 * 1000
DIALOGUE_LINES = [
    "DID YOU PUSH YOUR CODES",
    "IN YOUR GITHUB REPO?",
]
```

Change these values to adjust the animation, snooze duration, image size, or reminder copy.

The scheduled time is set separately in `setup_push_scheduler.ps1`:

```powershell
$Trigger = New-ScheduledTaskTrigger -Daily -At 5:00PM
```

## Stopping the reminder permanently

There is currently no uninstall script in the project. When you no longer want the daily reminder, remove or disable the `Github_Push_Guard_Spidey` task in **Windows Task Scheduler**.

This is also the manual step you would take once the reminder has done its job—for example, when you no longer want the internship-search accountability routine.

## Current limitations

- It does not connect to the GitHub API.
- It cannot tell whether you actually committed or pushed anything.
- It cannot determine whether you have been hired.
- The reminder time is hard-coded to 5:00 PM in the PowerShell setup script.
- The task launches `python.exe`, so a console window may also appear depending on your Windows/Python setup.
- The app uses a fixed 640 px window width, so very small displays may not lay out perfectly.
- Missing Pillow or a missing/broken `image_0.png` causes the app to fall back to a simple placeholder graphic.

## Why this exists

Job searching can turn "I should keep building" into something easy to postpone. This project turns that intention into a small daily interruption: ship something, push your work, then dismiss the reminder.

It is deliberately simple. The tool does not automate the work or fake activity—it only nudges you to do the work yourself.

## Media and licensing note

This repository currently contains a Spider-Man image asset and does not include a license file. Before publishing or distributing the repository, make sure you have permission to redistribute every bundled media asset. If necessary, replace the image with artwork you created yourself or an asset whose license allows redistribution.

The source code also has no explicit software license in the supplied project. Add one only after deciding how you want others to be allowed to use your code.

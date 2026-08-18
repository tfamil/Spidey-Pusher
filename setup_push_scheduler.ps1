<#
.SYNOPSIS
    Registers a Windows Task Scheduler task that runs spidey_pusher.py
    every day at 5:00 PM, catching up immediately if the machine was
    asleep/off at the scheduled time.

.DESCRIPTION
    - Task name: Github_Push_Guard_Spidey
    - Trigger:   Daily at 5:00 PM
    - Missed runs: Executed as soon as possible after the computer wakes
    - Power condition: Runs on battery power too (AC-only restriction disabled)

.NOTES
    Run this script from an elevated (Administrator) PowerShell prompt.
#>

# ----------------------------------------------------------------------
# 0. Require Administrator privileges
# ----------------------------------------------------------------------
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal(
    [Security.Principal.WindowsIdentity]::GetCurrent()
)
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "ERROR: This script must be run as Administrator." -ForegroundColor Red
    Write-Host "Right-click PowerShell and choose 'Run as Administrator', then re-run this script." -ForegroundColor Yellow
    exit 1
}

# ----------------------------------------------------------------------
# 1. Locate spidey_pusher.py (assumed to sit next to this script)
# ----------------------------------------------------------------------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetScript = Join-Path $ScriptDir "spidey_pusher.py"

if (-not (Test-Path $TargetScript)) {
    Write-Host "ERROR: Could not find 'spidey_pusher.py' in $ScriptDir" -ForegroundColor Red
    Write-Host "Place setup_push_scheduler.ps1 in the same folder as spidey_pusher.py and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host "Found spidey_pusher.py at $TargetScript" -ForegroundColor Green

# ----------------------------------------------------------------------
# 2. Locate the Python interpreter
# ----------------------------------------------------------------------
$PythonPath = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
if (-not $PythonPath) {
    $PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
}
if (-not $PythonPath) {
    Write-Host "ERROR: Could not find python.exe on PATH." -ForegroundColor Red
    Write-Host "Install Python or add it to PATH, then re-run this script." -ForegroundColor Yellow
    exit 1
}

Write-Host "Using Python interpreter at $PythonPath" -ForegroundColor Green

# ----------------------------------------------------------------------
# 3. Build the scheduled task
# ----------------------------------------------------------------------
$TaskName = "Github_Push_Guard_Spidey"

# Action: run python.exe against the target script, working directory set
# so the script can find image_0.png next to it.
$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$TargetScript`"" `
    -WorkingDirectory $ScriptDir

# Trigger: every day at 5:00 PM
$Trigger = New-ScheduledTaskTrigger -Daily -At 5:00PM

# Settings:
#   - StartWhenAvailable: run ASAP after a missed start (e.g., laptop asleep at 5PM)
#   - DisallowStartIfOnBatteries $false / DontStopOnIdleEnd etc: allow running
#     on battery power (i.e., do NOT restrict to AC power only)
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -MultipleInstances IgnoreNew

# Principal: run as the current interactive user so the GUI pop-up is visible.
$Principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Limited

Write-Host "Registering Task '$TaskName' at 5:00 PM daily..." -ForegroundColor Cyan

try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description "Daily 5 PM reminder to push code to GitHub (Spidey Pusher)." `
        -Force | Out-Null

    Write-Host "Registration successful." -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Failed to register scheduled task." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# ----------------------------------------------------------------------
# 4. Manual run instructions
# ----------------------------------------------------------------------
Write-Host ""
Write-Host "-----------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "HOW TO RUN THIS SCRIPT MANUALLY (with Administrator rights):" -ForegroundColor White
Write-Host "  1. Click Start, type 'PowerShell'." -ForegroundColor White
Write-Host "  2. Right-click 'Windows PowerShell' and choose 'Run as administrator'." -ForegroundColor White
Write-Host "  3. In the elevated window, navigate to this script's folder, e.g.:" -ForegroundColor White
Write-Host "       cd `"$ScriptDir`"" -ForegroundColor White
Write-Host "  4. Run:" -ForegroundColor White
Write-Host "       .\setup_push_scheduler.ps1" -ForegroundColor White
Write-Host "     (If script execution is blocked, run once:" -ForegroundColor White
Write-Host "       Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)" -ForegroundColor White
Write-Host "-----------------------------------------------------------" -ForegroundColor DarkGray

# setup_scheduler.ps1
# Sets up Windows Task Scheduler for the AI Employee
# Run as Administrator: powershell -ExecutionPolicy Bypass -File setup_scheduler.ps1

$ProjectPath = "D:\PIAIC\hackathon-0"
$PythonPath = (Get-Command python).Source

# Task 1: Daily briefing trigger at 8:00 AM
$action1 = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "$ProjectPath\orchestrator.py --daily-briefing" `
    -WorkingDirectory $ProjectPath

$trigger1 = New-ScheduledTaskTrigger -Daily -At "08:00AM"
$settings1 = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

Register-ScheduledTask `
    -TaskName "AIEmployee-DailyBriefing" `
    -Action $action1 `
    -Trigger $trigger1 `
    -Settings $settings1 `
    -Description "AI Employee daily morning briefing" `
    -Force

Write-Host "Daily briefing scheduled at 8:00 AM" -ForegroundColor Green

# Task 2: Weekly CEO Briefing every Sunday at 11:00 PM
$action2 = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "$ProjectPath\briefings\ceo_briefing.py" `
    -WorkingDirectory $ProjectPath

$trigger2 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "11:00PM"
$settings2 = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask `
    -TaskName "AIEmployee-WeeklyCEOBriefing" `
    -Action $action2 `
    -Trigger $trigger2 `
    -Settings $settings2 `
    -Description "AI Employee weekly CEO briefing generation" `
    -Force

Write-Host "Weekly CEO Briefing scheduled for Sunday 11:00 PM" -ForegroundColor Green
Write-Host ""
Write-Host "Scheduled tasks created successfully!" -ForegroundColor Cyan
Write-Host "View in Task Scheduler -> Task Scheduler Library"

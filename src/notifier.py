"""Windows desktop notification utility."""
import subprocess


def show_desktop_notification(title: str, message: str):
    """Display a native Windows notification balloon."""
    # Escape quotes
    clean_title = title.replace('"', '`"')
    clean_msg = message.replace('"', '`"')

    ps_code = f"""
Add-Type -AssemblyName System.Windows.Forms
$balloon = New-Object System.Windows.Forms.NotifyIcon
$balloon.Icon = [System.Drawing.SystemIcons]::Information
$balloon.BalloonTipIcon = "Info"
$balloon.BalloonTipTitle = "{clean_title}"
$balloon.BalloonTipText = "{clean_msg}"
$balloon.Visible = $true
$balloon.ShowBalloonTip(6000)
Start-Sleep -Seconds 2
$balloon.Dispose()
"""
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_code],
            capture_output=True,
            timeout=8
        )
    except Exception as e:
        print(f"[Notification] Could not display toast: {e}")

Add-Type -AssemblyName System.Windows.Forms
$balloon = New-Object System.Windows.Forms.NotifyIcon
$balloon.Icon = [System.Drawing.SystemIcons]::Information
$balloon.BalloonTipIcon = "Info"
$balloon.BalloonTipTitle = "Internship Hunter (10:00 AM Scan)"
$balloon.BalloonTipText = "Automated daily search ran successfully!"
$balloon.Visible = $true
$balloon.ShowBalloonTip(4000)
Start-Sleep -Seconds 1
$balloon.Dispose()

$ws = New-Object -ComObject WScript.Shell
$shortcut = $ws.CreateShortcut("C:\Users\Admin\Desktop\MAHI System v2.lnk")
$shortcut.TargetPath = "C:\Users\Admin\MAHI\MAHI.bat"
$shortcut.WorkingDirectory = "C:\Users\Admin\MAHI"
$shortcut.Description = "MAHI Multi-Agent Orchestrator v2.0"
$shortcut.IconLocation = "C:\Windows\System32\shell32.dll,47"
$shortcut.Save()
Write-Host "Desktop shortcut created: MAHI System v2.lnk"

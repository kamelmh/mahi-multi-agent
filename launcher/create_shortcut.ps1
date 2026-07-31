
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut("C:\Users\Admin\Desktop\MAHI System.lnk")
$s.TargetPath = "C:\Users\Admin\MAHI\launcher\MAHI.bat"
$s.WorkingDirectory = "C:\Users\Admin\MAHI\launcher"
$s.Description = "MAHI All-in-One System Launcher"
$s.Save()
Write-Host "Shortcut created: MAHI System.lnk"

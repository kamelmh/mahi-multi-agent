import os
import sys

# Create desktop shortcut using PowerShell
ps_script = '''
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut("C:\\Users\\Admin\\Desktop\\MAHI System.lnk")
$s.TargetPath = "C:\\Users\\Admin\\MAHI\\launcher\\MAHI.bat"
$s.WorkingDirectory = "C:\\Users\\Admin\\MAHI\\launcher"
$s.Description = "MAHI All-in-One System Launcher"
$s.Save()
Write-Host "Shortcut created: MAHI System.lnk"
'''

# Write and execute PowerShell script
script_path = "C:/Users/Admin/MAHI/launcher/create_shortcut.ps1"
with open(script_path, 'w') as f:
    f.write(ps_script)

os.system(f'powershell -ExecutionPolicy Bypass -File "{script_path}"')

# Verify
shortcut_path = "C:/Users/Admin/Desktop/MAHI System.lnk"
if os.path.exists(shortcut_path):
    print(f"Shortcut created: {shortcut_path}")
else:
    print("Failed to create shortcut")

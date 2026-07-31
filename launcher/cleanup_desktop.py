import os
import shutil

desktop = "C:/Users/Admin/Desktop"
archive_dir = os.path.join(desktop, "_ARCHIVED_BATS")

# Create archive directory
os.makedirs(archive_dir, exist_ok=True)

# Files to move
files_to_move = [
    "AI_Command_Center.bat",
    "ClaudeCode.bat",
    "OpenCode.bat",
    "Kimi.bat",
    "Grok.bat",
    "Freebuff.bat",
    "Deploy_Portfolio.bat",
    "Export_CV_to_PDF.bat",
    "Take_Screenshots.bat",
    "AI_Command_Center.ps1",
    "start.bat.lnk",
    "claude-free.bat.lnk",
    "New Text Document.txt"
]

moved = []
for f in files_to_move:
    src = os.path.join(desktop, f)
    if os.path.exists(src):
        dst = os.path.join(archive_dir, f)
        shutil.move(src, dst)
        moved.append(f)
        print(f"Moved: {f}")

print(f"\nTotal moved: {len(moved)} files to _ARCHIVED_BATS/")
print("Desktop now has only: MAHI System.lnk")

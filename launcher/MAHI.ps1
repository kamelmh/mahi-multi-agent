# MAHI System Launcher - PowerShell Version
# Location: C:\Users\Admin\MAHI\launcher\MAHI.ps1
# Run: powershell -ExecutionPolicy Bypass -File MAHI.ps1

$Host.UI.RawUI.WindowTitle = "MAHI System Launcher"
$Host.UI.RawUI.BackgroundColor = "Black"
Clear-Host

function Show-MainMenu {
    Clear-Host
    Write-Host ""
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host "           M A H I   S Y S T E M" -ForegroundColor Cyan
    Write-Host "           All-in-One Launcher" -ForegroundColor Cyan
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    [1]  AI Agents & Code" -ForegroundColor Green
    Write-Host "    [2]  Portfolio & Career" -ForegroundColor Green
    Write-Host "    [3]  DSS & Tools" -ForegroundColor Green
    Write-Host "    [4]  Quick Launch" -ForegroundColor Yellow
    Write-Host "    [0]  Exit" -ForegroundColor Red
    Write-Host ""
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""
    $choice = Read-Host "  >"
    return $choice
}

function Show-AIMenu {
    Clear-Host
    Write-Host ""
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host "        AI AGENTS & CODE" -ForegroundColor Cyan
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    [1]  OpenCode      (Multi-Agent, FREE)" -ForegroundColor Green
    Write-Host "    [2]  Claude Code   (via FCC proxy)" -ForegroundColor Green
    Write-Host "    [3]  Kimi Code     (Quick edits)" -ForegroundColor Green
    Write-Host "    [4]  Freebuff      (Free AI coding)" -ForegroundColor Green
    Write-Host "    [5]  Start FCC     (Free Claude server)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    [0]  Back" -ForegroundColor Red
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""
    $a = Read-Host "  >"
    return $a
}

function Show-CareerMenu {
    Clear-Host
    Write-Host ""
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host "      PORTFOLIO & CAREER" -ForegroundColor Magenta
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    [1]  Portfolio Site   (Netlify deploy)" -ForegroundColor Green
    Write-Host "    [2]  Export CV to PDF (Technical/Academic)" -ForegroundColor Green
    Write-Host "    [3]  Take Screenshots (DSS gallery)" -ForegroundColor Green
    Write-Host "    [4]  Open Portfolio   (kamelmahi.netlify.app)" -ForegroundColor Green
    Write-Host ""
    Write-Host "    [0]  Back" -ForegroundColor Red
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""
    $c = Read-Host "  >"
    return $c
}

function Show-ToolsMenu {
    Clear-Host
    Write-Host ""
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host "          DSS & TOOLS" -ForegroundColor Yellow
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    [1]  Academix DSS    (ERP_v13.4.xlsm)" -ForegroundColor Green
    Write-Host "    [2]  LifeWorkspace   (Obsidian vault)" -ForegroundColor Green
    Write-Host "    [3]  Grok            (xAI web chat)" -ForegroundColor Green
    Write-Host "    [4]  VS Code         (Code editor)" -ForegroundColor Green
    Write-Host ""
    Write-Host "    [0]  Back" -ForegroundColor Red
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""
    $t = Read-Host "  >"
    return $t
}

function Show-QuickMenu {
    Clear-Host
    Write-Host ""
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host "         QUICK LAUNCH" -ForegroundColor Yellow
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    [1] OpenCode        [5] Portfolio" -ForegroundColor Green
    Write-Host "    [2] Claude Code     [6] LifeWorkspace" -ForegroundColor Green
    Write-Host "    [3] Kimi Code       [7] Academix DSS" -ForegroundColor Green
    Write-Host "    [4] Grok            [8] VS Code" -ForegroundColor Green
    Write-Host ""
    Write-Host "    [0] Back" -ForegroundColor Red
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""
    $q = Read-Host "  >"
    return $q
}

function Show-CVMenu {
    Clear-Host
    Write-Host ""
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host "        SELECT CV" -ForegroundColor Cyan
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "    [1]  Technical CV (VBA/DSS Developer)" -ForegroundColor Green
    Write-Host "    [2]  Academic CV  (English Teacher)" -ForegroundColor Green
    Write-Host "    [3]  Both" -ForegroundColor Green
    Write-Host ""
    Write-Host "    [0]  Back" -ForegroundColor Red
    Write-Host "  ========================================" -ForegroundColor Cyan
    Write-Host ""
    $cv = Read-Host "  >"
    return $cv
}

# Main loop
$running = $true
while ($running) {
    $choice = Show-MainMenu
    
    switch ($choice) {
        "1" {
            $a = Show-AIMenu
            switch ($a) {
                "1" { opencode }
                "2" { 
                    $env:ANTHROPIC_BASE_URL = "http://localhost:8083"
                    $env:ANTHROPIC_API_KEY = "freecc"
                    claude
                }
                "3" { & "C:\Users\Admin\.kimi-code\bin\kimi.exe" }
                "4" { freebuff }
                "5" { 
                    Start-Process cmd -ArgumentList "/k", "cd C:\Users\Admin\free-claude-code && start.bat"
                    Write-Host "  FCC Server starting..." -ForegroundColor Yellow
                    Start-Sleep -Seconds 2
                }
            }
        }
        "2" {
            $c = Show-CareerMenu
            switch ($c) {
                "1" { python "C:\Users\Admin\deploy_portfolio.py" }
                "2" {
                    $cv = Show-CVMenu
                    switch ($cv) {
                        "1" { Start-Process "C:\Users\Admin\My Drive\LifeWorkspace\01_Identities_&_Assets\CV_MAHI_Technical.html" }
                        "2" { Start-Process "C:\Users\Admin\My Drive\LifeWorkspace\01_Identities_&_Assets\CV_MAHI_Academic.html" }
                        "3" {
                            Start-Process "C:\Users\Admin\My Drive\LifeWorkspace\01_Identities_&_Assets\CV_MAHI_Technical.html"
                            Start-Process "C:\Users\Admin\My Drive\LifeWorkspace\01_Identities_&_Assets\CV_MAHI_Academic.html"
                        }
                    }
                }
                "3" {
                    Clear-Host
                    Write-Host ""
                    Write-Host "  ========================================" -ForegroundColor Cyan
                    Write-Host "       SCREENSHOT GUIDE" -ForegroundColor Cyan
                    Write-Host "  ========================================" -ForegroundColor Cyan
                    Write-Host ""
                    Write-Host "  Open Academix DSS, then use Win+Shift+S:" -ForegroundColor White
                    Write-Host ""
                    Write-Host "    1. Dashboard (main overview)" -ForegroundColor White
                    Write-Host "    2. Stock Entry form" -ForegroundColor White
                    Write-Host "    3. CONFIG sheet" -ForegroundColor White
                    Write-Host "    4. Inventory report" -ForegroundColor White
                    Write-Host "    5. Wilson EOQ calculations" -ForegroundColor White
                    Write-Host "    6. Alerts sheet" -ForegroundColor White
                    Write-Host "    7. Orders sheet" -ForegroundColor White
                    Write-Host "    8. Dashboard chart/graph" -ForegroundColor White
                    Write-Host ""
                    Write-Host "  ========================================" -ForegroundColor Cyan
                    Write-Host ""
                    Start-Process "C:\Users\Admin\Projects\active\apps\academix-dss\education\ERP_dss_inventory_system_v13.4_for_directorate_of_education.xlsm"
                    Read-Host "  Press Enter after taking screenshots"
                }
                "4" { Start-Process "https://kamelmahi.netlify.app" }
            }
        }
        "3" {
            $t = Show-ToolsMenu
            switch ($t) {
                "1" { Start-Process "C:\Users\Admin\Projects\active\apps\academix-dss\education\ERP_dss_inventory_system_v13.4_for_directorate_of_education.xlsm" }
                "2" { Start-Process "obsidian://open?vault=LifeWorkspace" }
                "3" { Start-Process "https://grok.com" }
                "4" { code . }
            }
        }
        "4" {
            $q = Show-QuickMenu
            switch ($q) {
                "1" { opencode }
                "2" { 
                    $env:ANTHROPIC_BASE_URL = "http://localhost:8083"
                    $env:ANTHROPIC_API_KEY = "freecc"
                    claude
                }
                "3" { & "C:\Users\Admin\.kimi-code\bin\kimi.exe" }
                "4" { Start-Process "https://grok.com" }
                "5" { Start-Process "https://kamelmahi.netlify.app" }
                "6" { Start-Process "obsidian://open?vault=LifeWorkspace" }
                "7" { Start-Process "C:\Users\Admin\Projects\active\apps\academix-dss\education\ERP_dss_inventory_system_v13.4_for_directorate_of_education.xlsm" }
                "8" { code . }
            }
        }
        "0" { $running = $false }
    }
}

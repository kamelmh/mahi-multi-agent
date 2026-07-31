@echo off
:: MAHI Launcher - Single entry point for everything
:: Usage: Double-click MAHI.bat or run from anywhere
:: Location: C:\Users\Admin\MAHI\launcher\MAHI.bat

title MAHI System Launcher
color 0F
mode con: cols=60 lines=40
cls

echo.
echo  ========================================
echo           M A H I   S Y S T E M
echo           All-in-One Launcher
echo  ========================================
echo.
echo    [1]  AI Agents ^& Code
echo    [2]  Portfolio ^& Career
echo    [3]  DSS ^& Tools
echo    [4]  Quick Launch (direct)
echo    [0]  Exit
echo.
echo  ========================================
echo.
set /p choice="  > "

if "%choice%"=="1" goto ai
if "%choice%"=="2" goto career
if "%choice%"=="3" goto tools
if "%choice%"=="4" goto quick
if "%choice%"=="0" exit /b
goto main

:ai
cls
echo.
echo  ========================================
echo        AI AGENTS ^& CODE
echo  ========================================
echo.
echo    [1]  OpenCode      (Multi-Agent, FREE)
echo    [2]  Claude Code   (via FCC proxy)
echo    [3]  Hermes        (AI agent, tool-calling)
echo    [4]  Kimi Code     (Quick edits)
echo    [5]  Freebuff      (Free AI coding)
echo    [6]  Start FCC     (Free Claude server)
echo.
echo    [0]  Back
echo  ========================================
echo.
set /p a="  > "
if "%a%"=="1" goto opencode
if "%a%"=="2" goto claude
if "%a%"=="3" goto hermes
if "%a%"=="4" goto kimi
if "%a%"=="5" goto freebuff
if "%a%"=="6" goto fcc
if "%a%"=="0" goto main
goto ai

:career
cls
echo.
echo  ========================================
echo      PORTFOLIO ^& CAREER
echo  ========================================
echo.
echo    [1]  Portfolio Site   (Netlify deploy)
echo    [2]  Export CV to PDF (Technical/Academic)
echo    [3]  Take Screenshots (DSS gallery)
echo    [4]  Open Portfolio   (kamelmahi.netlify.app)
echo.
echo    [0]  Back
echo  ========================================
echo.
set /p c="  > "
if "%c%"=="1" goto deploy
if "%c%"=="2" goto cv
if "%c%"=="3" goto screenshots
if "%c%"=="4" start https://kamelmahi.netlify.app & goto career
if "%c%"=="0" goto main
goto career

:tools
cls
echo.
echo  ========================================
echo          DSS ^& TOOLS
echo  ========================================
echo.
echo    [1]  Academix DSS    (ERP_v13.4.xlsm)
echo    [2]  LifeWorkspace   (Obsidian vault)
echo    [3]  Grok            (xAI web chat)
echo    [4]  VS Code         (Code editor)
echo    [5]  Job Search AI   (CV, cover letters, interviews)
echo.
echo    [0]  Back
echo  ========================================
echo.
set /p t="  > "
if "%t%"=="1" start "" "C:\Users\Admin\Dropbox\Logistics.Public.Sector.Refactor\ERP_v13.4.xlsm" & goto tools
if "%t%"=="2" start obsidian://open?vault=LifeWorkspace & goto tools
if "%t%"=="3" start https://grok.com & goto tools
if "%t%"=="4" code . & goto tools
if "%t%"=="5" goto jobsearch
if "%t%"=="0" goto main
goto tools

:jobsearch
title AI Job Search
code "C:\Users\Admin\Projects\active\job-search"
if %errorlevel% neq 0 (echo [ERROR] VS Code failed & pause)
goto tools

:quick
cls
echo.
echo  ========================================
echo         QUICK LAUNCH
echo  ========================================
echo.
echo    [1] OpenCode        [5] Portfolio
echo    [2] Claude Code     [6] LifeWorkspace
echo    [3] Kimi Code       [7] Academix DSS
echo    [4] Grok            [8] VS Code
echo.
echo    [0] Back
echo  ========================================
echo.
set /p q="  > "
if "%q%"=="1" goto opencode
if "%q%"=="2" goto claude
if "%q%"=="3" goto kimi
if "%q%"=="4" start https://grok.com & goto quick
if "%q%"=="5" start https://kamelmahi.netlify.app & goto quick
if "%q%"=="6" start obsidian://open?vault=LifeWorkspace & goto quick
if "%q%"=="7" start "" "C:\Users\Admin\Dropbox\Logistics.Public.Sector.Refactor\ERP_v13.4.xlsm" & goto quick
if "%q%"=="8" code . & goto quick
if "%q%"=="0" goto main
goto quick

:opencode
title OpenCode
opencode
if %errorlevel% neq 0 (echo [ERROR] OpenCode failed & pause)
goto main

:claude
title Claude Code
set ANTHROPIC_BASE_URL=http://localhost:8083
set ANTHROPIC_API_KEY=freecc
claude
if %errorlevel% neq 0 (echo [ERROR] Claude Code failed - start FCC first & pause)
goto main

:hermes
title Hermes Agent
hermes
if %errorlevel% neq 0 (echo [ERROR] Hermes failed & pause)
goto main

:kimi
title Kimi Code
"C:\Users\Admin\.kimi-code\bin\kimi.exe"
if %errorlevel% neq 0 (echo [ERROR] Kimi failed & pause)
goto main

:freebuff
title Freebuff
call freebuff
if %errorlevel% neq 0 (echo [ERROR] Freebuff failed & pause)
goto main

:fcc
title FCC Server
start "FCC Server" cmd /k "cd C:\Users\Admin\free-claude-code && start.bat"
echo FCC Server starting in new window...
timeout /t 3 >nul
goto ai

:deploy
title Deploy Portfolio
python "C:\Users\Admin\deploy_portfolio.py"
if %errorlevel% neq 0 (echo [ERROR] Deploy failed & pause)
goto career

:cv
cls
echo.
echo  ========================================
echo        SELECT CV
echo  ========================================
echo.
echo    [1]  Technical CV (VBA/DSS Developer)
echo    [2]  Academic CV  (English Teacher)
echo    [3]  Both
echo.
echo    [0]  Back
echo  ========================================
echo.
set /p cvchoice="  > "
if "%cvchoice%"=="1" start "" "C:\Users\Admin\My Drive\LifeWorkspace\01_Identities_&_Assets\CV_MAHI_Technical.html" & goto career
if "%cvchoice%"=="2" start "" "C:\Users\Admin\My Drive\LifeWorkspace\01_Identities_&_Assets\CV_MAHI_Academic.html" & goto career
if "%cvchoice%"=="3" start "" "C:\Users\Admin\My Drive\LifeWorkspace\01_Identities_&_Assets\CV_MAHI_Technical.html" & start "" "C:\Users\Admin\My Drive\LifeWorkspace\01_Identities_&_Assets\CV_MAHI_Academic.html" & goto career
goto cv

:screenshots
cls
echo.
echo  ========================================
echo       SCREENSHOT GUIDE
echo  ========================================
echo.
echo  Open Academix DSS, then use Win+Shift+S:
echo.
echo    1. Dashboard (main overview)
echo    2. Stock Entry form
echo    3. CONFIG sheet
echo    4. Inventory report
echo    5. Wilson EOQ calculations
echo    6. Alerts sheet
echo    7. Orders sheet
echo    8. Dashboard chart/graph
echo.
echo  ========================================
echo.
echo  Opening Academix DSS...
start "" "C:\Users\Admin\Dropbox\Logistics.Public.Sector.Refactor\ERP_v13.4.xlsm"
echo.
echo  Press any key after taking screenshots...
pause >nul
goto career

:main
cls
goto eof

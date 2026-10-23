@echo off
setlocal
cd /d "%~dp0frontend"
if not exist node_modules\vite\package.json (
  call npm.cmd ci
  if errorlevel 1 (
    echo Dependency installation failed. Please check Node.js and network access.
    pause
    exit /b 1
  )
)
echo Opening the local UI preview with fictional data. Keep this window open.
call npm.cmd run dev -- --host 127.0.0.1 --port 5178 --strictPort --open /tests/design-preview.html
pause

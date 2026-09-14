@echo off
setlocal DisableDelayedExpansion
if "%~1"=="" (
  echo Open this folder in Codex App and start a conversation.
  echo This command-line tool is used by the Agent. Examples: work.cmd doctor / work.cmd --help
  pause
  exit /b 0
)
set "PYTHONUTF8=1"
set "PYTHON=%~dp0runtime\python\python.exe"
if not exist "%PYTHON%" (
  >&2 echo work: bundled Python runtime is missing: %PYTHON%
  exit /b 1
)
"%PYTHON%" -B "%~dp0.studio\windows_runtime.py" %*
exit /b %ERRORLEVEL%

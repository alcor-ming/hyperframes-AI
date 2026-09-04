@echo off
setlocal
set "PYTHONUTF8=1"
set "PYTHON=%~dp0runtime\python\python.exe"
if not exist "%PYTHON%" (
  >&2 echo asr-wsl: bundled Python runtime is missing: %PYTHON%
  exit /b 1
)
"%PYTHON%" "%~dp0.studio\asr_wsl_bridge.py" %*
exit /b %ERRORLEVEL%

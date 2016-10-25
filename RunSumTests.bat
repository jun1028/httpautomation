@echo off
set thisdir=.
set PYTHONPATH=%thisdir%;%thisdir%\src
python "%THISDIR%\src\runner\Runner.py" "%thisdir%\testcases\Example.html" "%thisdir%\Reports\Sample-report.html" 
pause

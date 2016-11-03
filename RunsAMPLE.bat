@echo off
set thisdir=.
set PYTHONPATH=%thisdir%;%thisdir%\src
python "%THISDIR%\src\runner\Runner.py" "%thisdir%\testcases\moonjjAPI72.xlsx"
pause

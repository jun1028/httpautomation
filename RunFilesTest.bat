@echo off
set thisdir=.
set PYTHONPATH=%thisdir%;%thisdir%\src
python "%THISDIR%\src\runner\FilesRunner.py" "%thisdir%\QE\testcases" 
@echo 按任意键打开测试报告
pause

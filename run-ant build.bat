@echo off
@echo start to automation test
call ant  -f antxml\build-py.xml -Dtestcase.filename=.\excel\bigdata-monjingser1.xlsx
pause 


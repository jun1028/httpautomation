@echo off
@echo start to monkey test
call ant  -f antxml\build-py.xml -Dtestcase.filename=.\excel\bigdata-monjingser.xlsx
pause 


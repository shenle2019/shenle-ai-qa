@echo off
cd /d D:\Code\AIQECourse\Phase2\apps\shenle-api-cli
call shenle-api-cli send task2_req.json > send_out.txt
type send_out.txt
for /f "tokens=*" %%i in ('findstr /r "result_file=" send_out.txt') do set RESULT_LINE=%%i
echo RESULT_LINE=%RESULT_LINE%
for /f "tokens=2 delims==" %%i in ("%RESULT_LINE%") do set RESULT_FILE=%%i
echo RESULT_FILE=%RESULT_FILE%
shenle-api-cli extract "%RESULT_FILE%" --field "$.data.token"
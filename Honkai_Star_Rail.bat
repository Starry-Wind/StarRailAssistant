chcp 65001
:: BatchGotAdmin (Run as Admin code starts)
REM --> Check for permissions
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
REM --> If error flag set, we do not have admin.
if '%errorlevel%' NEQ '0' (
echo Requesting administrative privileges...
goto UACPrompt
) else ( goto gotAdmin )
:UACPrompt
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
"%temp%\getadmin.vbs"
exit /B
:gotAdmin
if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
pushd "%CD%"
CD /D "%~dp0"
:: BatchGotAdmin (Run as Admin code ends)
:: Your codes should start from the following line

@echo off
cd /d %~dp0

chcp 65001
echo 已设定此终端编码为UTF-8
echo.

echo Python版本
python --version
echo 如果没出现版本号代表你没有安装Python
echo.

echo 正在检查并更新依赖
pip install -r requirements.txt
echo 自动依赖检查已完成
echo.

echo 正在自动更新地图档
py Honkai_Star_Rail.py
echo 在刚开启程序就看到这条信息? 你可能没有安装Python? 或是Python安装时没有勾选"Add Python to PATH"?
echo 如果有可能是上面那些问题 请不要去Github回报issue或是来QQ群问这个问题 建议重新阅读Github页面的使用教学
echo.

pause
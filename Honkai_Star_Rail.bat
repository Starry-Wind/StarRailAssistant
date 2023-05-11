@echo off
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
cd /d %~dp0

echo Python版本
python --version
echo.

echo 正在檢查並更新依賴
pip install -r requirements.txt
echo 自動依賴檢查已完成
echo.

echo 正在自動更新地圖檔
python "main.py"
echo 你沒有安裝Python!!!!!!!!!!!!!!!!!!!!!請詳細閱讀Github的使用說明安裝完Python後再啟動!!!!!!!!!!!!!!!!!!!!!
echo 這不是腳本的問題!!!!!!!!!!!!!!!!!!!!!請不要去QQ群問這個問題或去Github開issue都不要!!!!!!!!!!!!!!!!!!!!!
echo 你沒有安裝Python!!!!!!!!!!!!!!!!!!!!!請詳細閱讀Github的使用說明安裝完Python後再啟動!!!!!!!!!!!!!!!!!!!!!
echo 這不是腳本的問題!!!!!!!!!!!!!!!!!!!!!請不要去QQ群問這個問題或去Github開issue都不要!!!!!!!!!!!!!!!!!!!!!
echo 你沒有安裝Python!!!!!!!!!!!!!!!!!!!!!請詳細閱讀Github的使用說明安裝完Python後再啟動!!!!!!!!!!!!!!!!!!!!!
echo 這不是腳本的問題!!!!!!!!!!!!!!!!!!!!!請不要去QQ群問這個問題或去Github開issue都不要!!!!!!!!!!!!!!!!!!!!!
echo 你沒有安裝Python!!!!!!!!!!!!!!!!!!!!!請詳細閱讀Github的使用說明安裝完Python後再啟動!!!!!!!!!!!!!!!!!!!!!
echo 這不是腳本的問題!!!!!!!!!!!!!!!!!!!!!請不要去QQ群問這個問題或去Github開issue都不要!!!!!!!!!!!!!!!!!!!!!
echo 你沒有安裝Python!!!!!!!!!!!!!!!!!!!!!請詳細閱讀Github的使用說明安裝完Python後再啟動!!!!!!!!!!!!!!!!!!!!!
echo 這不是腳本的問題!!!!!!!!!!!!!!!!!!!!!請不要去QQ群問這個問題或去Github開issue都不要!!!!!!!!!!!!!!!!!!!!!
echo 你沒有安裝Python!!!!!!!!!!!!!!!!!!!!!請詳細閱讀Github的使用說明安裝完Python後再啟動!!!!!!!!!!!!!!!!!!!!!
echo 這不是腳本的問題!!!!!!!!!!!!!!!!!!!!!請不要去QQ群問這個問題或去Github開issue都不要!!!!!!!!!!!!!!!!!!!!!
echo 你沒有安裝Python!!!!!!!!!!!!!!!!!!!!!請詳細閱讀Github的使用說明安裝完Python後再啟動!!!!!!!!!!!!!!!!!!!!!
echo 這不是腳本的問題!!!!!!!!!!!!!!!!!!!!!請不要去QQ群問這個問題或去Github開issue都不要!!!!!!!!!!!!!!!!!!!!!
echo 你沒有安裝Python!!!!!!!!!!!!!!!!!!!!!請詳細閱讀Github的使用說明安裝完Python後再啟動!!!!!!!!!!!!!!!!!!!!!
echo 這不是腳本的問題!!!!!!!!!!!!!!!!!!!!!請不要去QQ群問這個問題或去Github開issue都不要!!!!!!!!!!!!!!!!!!!!!
echo 你沒有安裝Python!!!!!!!!!!!!!!!!!!!!!請詳細閱讀Github的使用說明安裝完Python後再啟動!!!!!!!!!!!!!!!!!!!!!
echo 這不是腳本的問題!!!!!!!!!!!!!!!!!!!!!請不要去QQ群問這個問題或去Github開issue都不要!!!!!!!!!!!!!!!!!!!!!
echo 你沒有安裝Python!!!!!!!!!!!!!!!!!!!!!請詳細閱讀Github的使用說明安裝完Python後再啟動!!!!!!!!!!!!!!!!!!!!!
echo 這不是腳本的問題!!!!!!!!!!!!!!!!!!!!!請不要去QQ群問這個問題或去Github開issue都不要!!!!!!!!!!!!!!!!!!!!!
echo 你沒有安裝Python!!!!!!!!!!!!!!!!!!!!!請詳細閱讀Github的使用說明安裝完Python後再啟動!!!!!!!!!!!!!!!!!!!!!
echo 這不是腳本的問題!!!!!!!!!!!!!!!!!!!!!請不要去QQ群問這個問題或去Github開issue都不要!!!!!!!!!!!!!!!!!!!!!

pause


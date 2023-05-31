@echo off
setlocal enabledelayedexpansion
chcp 65001

set python=python
set pip=pip
set env_path=.\temp
set venv_path=!env_path!\venv

echo 安装启动途中 如遇杀毒软件提醒 选择信任即可

rem 检查 系统是否已安装 Python 3.11
set sys_py311=0
where python >nul 2>&1 && python --version 2>nul | findstr /i "3.11" >nul && set sys_py311=1
if !sys_py311! == 1 (
    goto py311-install-done
)

rem 检查 本地是否已安装 Python 3.11
set local_py_path=!env_path!\python3.11
set local_py311=0
if exist !local_py_path!\python.exe (
    !local_py_path!\python.exe --version 2>nul | findstr /i "3.11" >nul && set local_py311=1
)
if !local_py311! == 1 (
    set python=!local_py_path!\python.exe
    goto py311-install-done
) 

rem 在当前目录根据系统下载python
echo 准备在当前目录安装Python 3.11
set bit=!PROCESSOR_ARCHITECTURE!
echo 当前系统为 !bit!

set py_url=https://www.python.org/ftp/python/3.11.3/python-3.11.3-embed-win32.zip
set py_file_name=!env_path!\python-3.11.3-embed.zip
if "!bit!"=="AMD64" (
    set py_url=https://www.python.org/ftp/python/3.11.3/python-3.11.3-embed-amd64.zip
)

if not exist "!env_path!" mkdir "!env_path!"

if exist !py_file_name! (
    echo 下载Python3.11完成
) else (
    echo 开始下载Python3.11 !py_url!
    echo 下载目录 !py_file_name!
    certutil -urlcache -split -f "!py_url!" "!py_file_name!"
    echo 下载Python3.11完成
)

rem 解压缩python
echo 开始解压缩Python3.11
powershell Expand-Archive -LiteralPath !py_file_name! -DestinationPath !local_py_path!
echo 解压缩Python3.11完成

set python=!local_py_path!\python.exe
set local_py311=1

:py311-install-done
echo 当前使用Python版本 & !python! --version

rem 检查是否安装pip
if !sys_py311! == 0 (
    set pip=!local_py_path!\Scripts\pip.exe
)
set with_pip=0
!python! -m pip --version >nul 2>nul && set with_pip=1
if !with_pip! == 1 (
    goto pip-install-done
) 

rem 使用get-pip.py安装
set get_pip_url=https://bootstrap.pypa.io/get-pip.py
set get_pip_file_name=!env_path!\get-pip.py
if exist !get_pip_file_name! (
    echo 下载get-pip.py完成
) else (
    echo 开始下载get-pip.py !get_pip_url!
    echo 下载目录 !get_pip_file_name!
    certutil -urlcache -split -f "!get_pip_url!" "!get_pip_file_name!"
    echo 下载get-pip.py完成
)

echo 开始安装pip
!python! !get_pip_file_name!
rem embed版本检查pip模块是否在python依赖中
if !local_py311! == 1 (
    !python! -m pip --version >nul 2>nul && set with_pip=1
    if !with_pip! == 0 (
        echo.>> !local_py_path!\python311._pth
        echo Lib\site-packages >> !local_py_path!\python311._pth
        echo.>> !local_py_path!\python311._pth
    )
)
echo pip安装完成

:pip-install-done
echo pip版本 & !pip! --version


rem 检查 本地虚拟环境是否已经安装
set venv_installed=0
if exist !venv_path!\Scripts\python.exe (
    !venv_path!\Scripts\python.exe --version 2>nul | findstr /i "3.11" >nul && set venv_installed=1
    if !venv_installed! == 1 (
        goto venv-done
    )
)

rem 安装项目依赖
echo 创建虚拟环境
!pip! install virtualenv
!python! -m virtualenv !env_path!\venv

:venv-done
echo 虚拟环境已准备
set python=!venv_path!\Scripts\python.exe
set pip=!venv_path!\Scripts\pip.exe

rem 检查是否已经安装依赖
for /f "tokens=1,2 delims= " %%a in ('dir /T:W /A:-D /O:-D /T:C /T:A /T:W requirements.txt ^| find " requirements.txt"') do set file_time=%%a%%b
set "file_time=%file_time:/=%"
set "file_time=%file_time:-=%"
set "file_time=%file_time::=%"
if exist !env_path!\!file_time!.txt goto requirements-install-done

echo 开始安装依赖包
!pip! install -r requirements.txt
echo 安装依赖包完成
echo.>> !env_path!\!file_time!.txt

:requirements-install-done
echo 依赖包已准备

:start
echo 准备启动......
echo 如果失败 可手动删除 .env 文件夹后重试
!python! Honkai_Star_Rail.py

endlocal
pause
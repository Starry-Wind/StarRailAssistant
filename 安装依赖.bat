@echo off
::编码方式设置为utf-8
chcp 65001
::升级pip
echo 正在获取pip版本，若版本过低，会自动升级
python -m pip install --upgrade pip
echo.
echo 正在获取需要升级的包。。。

::正在安装依赖
pip install ort_nightly -i https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/ORT-Nightly/pypi/simple/ 
pip install -r requirements.txt
echo.
echo 按任意键关闭
pause 

@echo off
::编码方式设置为utf-8
chcp 65001
::升级pip
echo 正在获取pip版本，若版本过低，会自动升级
python -m pip install --upgrade pip
echo.
for /f "tokens=2 delims=." %%a in ('python -V') do set abc=%%a
if %abc% == 11 (
    pip install coloredlogs flatbuffers numpy packaging protobuf sympy
    pip install ort_nightly -i https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/ORT-Nightly/pypi/simple/ 
    pip install whl//Polygon3-3.0.9-cp311-cp311-win_amd64.whl
    pip install whl//cnstd-1.2.2-py3-none-any.whl
    pip install whl//cnocr-2.2.2.3-py3-none-any.whl
)
if %abc% == 10 (
    pip install whl//Polygon3-3.0.9.1-cp310-cp310-win_amd64.whl
    pip install cnocr
)
pip install -r requirements.txt
echo.
echo 按任意键关闭
pause 

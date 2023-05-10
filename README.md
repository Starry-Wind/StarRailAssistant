<div align="center">

<h1 align="center">

[嗨！点点我！点点我！点点我！](#注意)

<img alt="LOGO" src="https://github.com/Starry-Wind/Honkai-Star-Rail/blob/318c2c19c45d7c26f6b663a57018519f367a09a5/temp/love!.png" style="border-radius:50%">

崩坏：星穹铁道自动锄大地脚本

</h1>
 
[![GitHub Stars](https://img.shields.io/github/stars/Starry-Wind/Honkai-Star-Rail?style=flat-square)](https://github.com/Starry-Wind/Honkai-Star-Rail/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Starry-Wind/Honkai-Star-Rail?style=flat-square)](https://github.com/Starry-Wind/Honkai-Star-Rail/network)
[![GitHub Issues](https://img.shields.io/github/issues/Starry-Wind/Honkai-Star-Rail?style=flat-square)](https://github.com/Starry-Wind/Honkai-Star-Rail/issues)
[![GitHub Contributors](https://img.shields.io/github/contributors/Starry-Wind/Honkai-Star-Rail?style=flat-square)](https://github.com/Starry-Wind/Honkai-Star-Rail/graphs/contributors)
[![GitHub License](https://img.shields.io/github/license/Starry-Wind/Honkai-Star-Rail?style=flat-square)](https://github.com/Starry-Wind/Honkai-Star-Rail/blob/main/LICENSE)
</div>

*****该脚本仍然处于测试阶段，可能会出现奇奇怪怪的BUG*****

***寻路撞墙？走的路径不对？嫌弃路线太慢？ 现在beta-2.7新增加地图录制功能，你现在可以使用tool目录下的record_v7.2.py自行录制地图路径，包你走到满意 XD***

找到BUG了？，代码问题想吐槽？欢迎加入 技术 & 吹水群：[星穹◇Time(QQ 群)](https://qm.qq.com/cgi-bin/qm/qr?k=xdCO46fHlVcY7D2L7elXzqcxL3nyTGnW&jump_from=webapi&authKey=uWZooQ2szv+nG/re7luCKn8LW1KibSb0vvi0FycA45Mglm5AGM1GP2iJ+SiWmDwg)<br>

~~该脚本当前版本仅支持 缩放150%，屏幕分辨率2560x1440，现在在大改动中，尽快解决屏幕旋转适配问题~~

## 使用说明

1：安裝[Python 3.9](https://www.python.org/downloads/release/python-390/) (其他版本安裝依賴項時會有很多問題)

2：確認遊戲語言為**簡體中文**，按鍵配置皆為預設，靈敏度皆為預設值

3：如果你的电脑分辨率为2560\*1440，请将游戏分辨率调为1920\*1080（窗口化）
   如果你的电脑分辨率为1920\*1080，请将游戏分辨率调为1920\*1080（全屏幕）
   
4：战斗为游戏自带的自动战斗，确保你的队伍有足够实力平推小怪**
   (如启用了沿用自动战斗设定，请把config.json里的 "auto_battle_persistence" 改成 1) 

5：建議不要在地圖上追蹤任何東西，並且人物初始位置最好在**觀景車廂**

6：開怪角色請使用**遠程攻擊**角色，目前推薦**三七**及**站長**，跑圖效果較穩定

7：開啟**Honkai-Star-Rail.bat**等待程序自動運行至可輸入**地圖編號**處

8：如果你不知道**地圖編號**是什麼，或是你想要**重頭開始**跑圖，輸入"0"後回車

9：在等待開始五秒期間，請點回遊戲畫面，確保沒有開啟任何選單及介面，並等待程序運行

10：程序運行期間，**請勿移動**鍵盤及滑鼠，如果移動了極有可能造成**偏離**或**撞牆**的問題

## 脚本录制 **感谢**[@AlisaCat](https://github.com/AlisaCat-S)

1：WASD移动，X是进战斗，鼠标左键是打障碍物等，不要用鼠标移动视角，用方向键左右来移动视角（脚本运行后方向键左右会映射成鼠标），F9停止录制并保存**

2：完成后将会生成output.json文件，请把他重命名替换成你要更改的地图json即可使用** （原地图json将执行的路线将会在5月8日详细更新介绍）
 
## 注意事項
 
1：识图为截取游戏画面，所以不能有任何覆蓋
 
2：支持地图 **空间站「黑塔」、雅利洛VI、仙舟「羅浮」**

3：如果你發現地圖有撞牆問題，可以協助更新[地图文件提交到这里](https://github.com/Starry-Wind/Honkai-Star-Rail/tree/map)

4：$\color{#FF0000}{请使用**三七**及**站長**來跑图}$

****如果喜欢，点个星星~****

## 更新日志 (Release-v1.0.0)

1：新增bat執行檔一鍵開啟

2：新增地圖自動更新功能

3：完善requirements.txt的依賴列表

4：新增更多後台提示訊息

5：新增自動獲取視窗大小

6：日常修復一些小bug

7：更新了新的地图json，能解决大部分撞墙问题

## 未來目標

1：模拟宇宙正在开发

2：后续将会新增找宝箱、锄大地顺带捡垃圾等功能

## 贡献者

感谢以下贡献者对本项目做出的贡献

<a href="https://github.com/Starry-Wind/Honkai-Star-Rail/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Starry-Wind/Honkai-Star-Rail" />

</a>

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Starry-Wind/Honkai-Star-Rail&type=Date)](https://star-history.com/#Starry-Wind/Honkai-Star-Rail&Date)

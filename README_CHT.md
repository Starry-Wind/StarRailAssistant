<div align="center">

 [嗨！ 點點我！ 點點我！ 點點我！  ](#使用說明)

 [簡體中文](README.md) | [繁體中文](README_CHT.md)
 
 <img alt="LOGO" src="https://github.com/Starry-Wind/Honkai-Star-Rail/blob/318c2c19c45d7c26f6b663a57018519f367a09a5/temp/love!.png" style="border-radius:50%">

 <h1 align="center">

 崩壞：星穹鐵道自動鋤大地腳本

 </h1>
 
 [![GitHub Stars](https://img.shields.io/github/stars/Starry-Wind/Honkai-Star-Rail?style=flat-square)](https://github.com/Starry-Wind/Honkai-Star-Rail/stargazers)
 [![GitHub Forks](https://img.shields.io/github/forks/Starry-Wind/Honkai-Star-Rail?style=flat-square)](https://github.com/Starry-Wind/Honkai-Star-Rail/network)
 [![GitHub Issues](https://img.shields.io/github/issues/Starry-Wind/Honkai-Star-Rail?style=flat-square)](https://github.com/Starry-Wind/Honkai-Star-Rail/issues)
 [![GitHub Contributors](https://img.shields.io/github/contributors/Starry-Wind/Honkai-Star-Rail?style=flat-square)](https://github.com/Starry-Wind/Honkai-Star-Rail/graphs/contributors)
 [![GitHub License](https://img.shields.io/github/license/Starry-Wind/Honkai-Star-Rail?style=flat-square)](https://github.com/Starry-Wind/Honkai-Star-Rail/blob/main/LICENSE)
 </div>

 *****該腳本仍然處於測試階段，可能會出現奇奇怪怪的BUG*****

 ***尋路撞牆？ 走的路徑不對？ 嫌棄路線太慢？ 現在beta-2.7新增加地圖錄製功能***<br>
 ***你現在可以使用tool目錄下的record_v7.2.py自行錄製地圖路徑，包你走到滿意 XD***

 找到BUG了？ 代碼問題想吐槽？ 歡迎加入 技術 & 吹水群：[星穹◇Time(QQ 群)](https://qm.qq.com/cgi-bin/qm/qr?k=xdCO46fHlVcY7D2L7elXzqcxL3nyTGnW&jump_from=webapi&authKey=uWZooQ2szv+nG/re7luCKn8LW1KibSb0vvi0FycA45Mglm5AGM1GP2iJ+SiWmDwg)<br>

 ~~該腳本當前版本僅支持 縮放150%，屏幕分辨率2560x1440，現在在大改動中，盡快解決屏幕旋轉適配問題~~

 ## 使用說明

 1：安裝[Python 3.9](https://www.python.org/downloads/release/python-390/) (其他版本安裝依賴項時會有很多問題)

 2：確認遊戲語言為**簡體中文**，按鍵配置皆為默認，靈敏度皆為默認值

 3：如果你的電腦分辨率為2560\*1440，請將游戲分辨率調為1920\*1080（窗口化）<br>
    如果你的電腦分辨率為1920\*1080，請將游戲分辨率調為1920\*1080（全屏幕）
   
 4：戰鬥為遊戲自帶的自動戰鬥，確保你的隊伍有足夠實力平推小怪<br>
    (如啟用了沿用自動戰鬥設定，請把config.json裡的 "auto_battle_persistence" 改成 1) 

 5：建議不要在地圖上追踪任何東西，並且人物初始位置最好在**觀景車廂**

 6：開怪角色請使用**遠程攻擊**角色，目前推薦**三月七**及**艾絲妲**，跑圖效果較穩定

 7：開啟**Honkai_Star_Rail.exe**等待程序自動運行至可輸入**地圖編號**處

 8：如果你不知道**地圖編號**是什麼，或是你想要**重頭開始**跑圖，輸入"0"後回車

 9：在等待開始五秒期間，請點回游戲畫面，確保沒有開啟任何菜單及界面，並等待程序運行

 10：程序運行期間，**請勿移動**鍵盤及鼠標，如果移動了極有可能造成**偏離**或**撞牆**的問題

 ## 腳本錄製 感謝[@AlisaCat](https://github.com/AlisaCat-S)

 1：WASD移動，X是進戰鬥，鼠標左鍵是打障礙物等，不要用鼠標移動視角，用方向鍵左右來移動視角（腳本運行後方向鍵左右會映射成鼠標），F9停止錄製並保存

 2：完成後將會生成output.json文件，請把他重命名替換成你要更改的地圖json即可使用 （原地圖json將執行的路線將會在5月8日詳細更新介紹）
 
 ## 注意事項
 
 1：識圖為截取遊戲畫面，所以不能有任何覆蓋
 
 2：支持地圖 **空間站「黑塔」、雅利洛VI、仙舟「羅浮」**

 3：如果你發現地圖有撞牆問題，可以協助更新[地圖文件提交到這裡](https://github.com/Starry-Wind/Honkai-Star-Rail/tree/map)

 4：請使用**三月七**或**艾絲妲**來跑圖

 ⭐**如果喜歡，點個星星~**⭐

 ## 更新日誌 (Release-v1.0.0)

 1：新增exe執行檔一鍵開啟 感謝[@apple050620312
 ](https://github.com/apple050620312)

 2：新增地圖自動更新功能

 3：將pynput重新加入依賴列表

 4：新增更多後台提示信息

 5：新增自動獲取視窗大小

 6：日常修復一些小bug

 7：更新了新的地圖json，能解決大部分撞牆問題

 ## 未來目標

 1：模擬宇宙正在開發

 2：後續將會新增找寶箱、鋤大地順帶撿垃圾等功能

 ## Star History

 [![Star History Chart](https://api.star-history.com/svg?repos=Starry-Wind/Honkai-Star-Rail&type=Date)](https://star-history.com/#Starry-Wind/Honkai-Star-Rail&Date)
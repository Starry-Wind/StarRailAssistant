<div align="center">

[海！點點我！點點我！點點我！](#使用說明)

[簡體中文](README.md) | [繁體中文](README_CHT.md) | [English](README_EN.md) | [文档](https://sra.stysqy.top)
 
<img alt="LOGO" src="../../blob/map/temp/love!.png" style="border-radius:50%">

<h1 align="center">

崩壞：星穹鐵道小助手|StarRailAssistant|StarRailAssistant

</h1>

[![GitHub Stars](https://img.shields.io/github/stars/Starry-Wind/StarRailAssistant?style=flat-square)](https://github.com/Starry-Wind/StarRailAssistant/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Starry-Wind/StarRailAssistant?style=flat-square)](https://github.com/Starry-Wind/StarRailAssistant/network)
[![GitHub Issues](https://img.shields.io/github/issues/Starry-Wind/StarRailAssistant?style=flat-square)](https://github.com/Starry-Wind/StarRailAssistant/issues)
[![GitHub Contributors](https://img.shields.io/github/contributors/Starry-Wind/StarRailAssistant?style=flat-square)](https://github.com/Starry-Wind/StarRailAssistant/graphs/contributors)
[![GitHub License](https://img.shields.io/github/license/Starry-Wind/StarRailAssistant?style=flat-square)](https://github.com/Starry-Wind/StarRailAssistant/blob/main/LICENSE)
</div>

*****該腳本仍然處于測試階段，可能會出現奇奇怪怪的BUG*****

***尋路撞牆？走的路徑不對？嫌棄路線太慢？現在beta-2.7新增加地圖錄制功能***<br>
***妳現在可以使用tool目錄下的record_v7.2.py自行錄制地圖路徑，包妳走到滿意 XD***

找到BUG了？代碼問題想吐槽？歡迎加入 技術 & 吹水群：[QQ 群](https://qm.qq.com/cgi-bin/qm/qr?k=xdCO46fHlVcY7D2L7elXzqcxL3nyTGnW&jump_from=webapi&authKey=uWZooQ2szv+nG/re7luCKn8LW1KibSb0vvi0FycA45Mglm5AGM1GP2iJ+SiWmDwg)|[Telegram Group](https://t.me/+yeQEhnuT9O41NDM1)<br>

~~該腳本當前版本僅支持 縮放150%，屏幕分辨率2560x1440，現在在大改動中，盡快解決屏幕旋轉適配問題~~

## 免責聲明

本軟件是壹個外部工具旨在自動化崩壞星軌的遊戲玩法。它被設計成僅通過現有用戶界面與遊戲交互,並遵守相關法律法規。該軟件包旨在提供簡化和用戶通過功能與遊戲交互,並且它不打算以任何方式破壞遊戲平衡或提供任何不公平的優勢。該軟件包不會以任何方式修改任何遊戲文件或遊戲代碼。

This software is open source, free of charge and for learning and exchange purposes only. The developer team has the final right to interpret this project. All problems arising from the use of this software are not related to this project and the developer team. If you encounter a merchant using this software to practice on your behalf and charging for it, it may be the cost of equipment and time, etc. The problems and consequences arising from this software have nothing to do with it.

本軟件開源、免費，僅供學習交流使用。開發者團隊擁有本項目的最終解釋權。使用本軟件産生的所有問題與本項目與開發者團隊無關。若您遇到商家使用本軟件進行代練並收費，可能是設備與時間等費用，産生的問題及後果與本軟件無關。

請注意，根據MiHoYo的 [崩壞:星穹鐵道的公平遊戲宣言](https://sr.mihoyo.com/news/111246?nav=news&type=notice):

    "嚴禁使用外挂、加速器、腳本或其他破壞遊戲公平性的第三方工具。"
    "壹經發現，米哈遊（下亦稱“我們”）將視違規嚴重程度及違規次數，采取扣除違規收益、凍結遊戲賬號、永久封禁遊戲賬號等措施。"

## 使用說明

1. 安裝[Python 3.11](https://www.python.org/downloads/release/python-3113/) (其他版本安裝依賴項時會有很多問題)
    1. 输入`pip install -r requirements.txt`安裝依賴
2. 確認遊戲語言爲**簡體中文**，按鍵配置皆爲默認，靈敏度皆爲默認值
3. 如果妳的電腦分辨率爲2560\*1440，請將遊戲分辨率調爲1920\*1080（窗口化）<br>
   如果妳的電腦分辨率爲1920\*1080，請將遊戲分辨率調爲1920\*1080（全屏幕）
4. 戰鬥爲遊戲自帶的自動戰鬥，確保妳的隊伍有足夠實力平推小怪<br>
   (如啓用了沿用自動戰鬥設定，請把config.json裏的 "auto_battle_persistence" 改成 1) 
5. 建議不要在地圖上追蹤任何東西，並且人物初始位置最好在**觀景車廂**
6. 開怪角色請使用**遠程攻擊**角色，目前推薦**三月七**，跑圖效果較穩定
7. 開啓**Honkai_Star_Rail.bat**等待程序自動運行至可輸入**地圖編號**處
8. 如果妳不知道**地圖編號**是什麽，或是妳想要**重頭開始**跑圖，輸入"0"後回車
9. 在等待開始五秒期間，請點回遊戲畫面，確保沒有開啓任何菜單及界面，並等待程序運行
10. 程序運行期間，**請勿移動**鍵盤及鼠標，如果移動了極有可能造成**偏離**或**撞牆**的問題

## 配置文件說明

```json
{
    "real_width": 0, (實際寬度)
    "auto_battle_persistence": 0, (遊戲內是否開啓自動自動，填1則爲開啓)
    "real_height": 0, (實際長度)
    "map_debug": false,  (是否檢測更新)
    "github_proxy": "", (github代理)
    "rawgithub_proxy": "", (github代理)
    "webhook_url": "",
    "start": true, (是否第壹次運行腳本)
    "temp_version": "20230515205738",
    "star_version": "20230515220742",
    "open_map": "m", (打開地圖按鈕)
    "map_version": "20230515205738",
    "script_debug": true (是否檢測腳本更新)
}
```

## 腳本錄制 感謝[@AlisaCat](https://github.com/AlisaCat-S)

1. WASD移動，X是進戰鬥，鼠標左鍵是打障礙物，F鍵是交互，禁止用鼠標移動視角，只能使用方向鍵左右來移動視角（腳本運行後方向鍵左右會映射鼠標移動），錄制期間能且只能按動鍵盤上的壹個有效按鍵（也就是不能同時按下多鍵），腳本只會錄制按鍵按下時間和移動的視角，不會錄制停頓的時間（可以慢慢壹個鍵壹個鍵錄制，保證錄制准確性），錄制完成後F9停止錄制並保存。
2. 完成後將會生成output(時間).json文件，請把他重命名替換成妳要更改的地圖json，並且將傳送點截圖重命名並保存到temp即可使用 （就可以申請到map分支提交，或者交給管理提交）
3. 地圖json中的空白填寫示例：
    ```json
    {
        "name": "烏拉烏拉-1",       （地圖json名爲1-1_1.json）
        "author": "Starry-Wind",   （作者名，第二作者不能覆蓋第壹作者名稱）
        "start": [           （開局傳送地圖識別圖片，並將鼠標移動至圖片中間並按下按鍵）
            {"map": 1},         （按下m鍵打開地圖）
            {"temp\\orientation_1.jpg": 1.5},     （識別到orientation_1.jpg圖片後，將鼠標移動至圖片中間並按下按鍵）
            {"temp\\map_1.jpg": 2},               （具體圖片自己看，壹般爲該區域名"烏拉烏拉"的地圖文字）
            {"temp\\map_1_point_1.jpg": 1.5},       （第壹個傳送點的圖片）
            {"temp\\transfer.jpg": 1.5}              （"傳送"字的圖片）
        ]
    }
    ```
 
## 注意事項
 
1. 識圖爲截取遊戲畫面，所以不能有任何覆蓋
2. 支持地圖 **空間站「黑塔」、雅利洛VI、仙舟「羅浮」**
3. 如果妳發現地圖有撞牆問題，可以協助更新[地圖文件提交到這裏](https://github.com/Starry-Wind/StarRailAssistant/tree/map)
4. 請使用**三月七**來跑圖以獲得最佳體驗

⭐**如果喜歡，點個星星~**⭐

## 未來目標

- [ ] 模擬宇宙正在開發
- [x] GUI開發
- [ ] 後續將會新增找寶箱、鋤大地順帶撿垃圾等功能

## 贡献

[問題反饋](https://github.com/Starry-Wind/StarRailAssistant/issues/new/choose) | [PR 提交](https://github.com/Starry-Wind/StarRailAssistant/compare)

歡迎各種形式的貢獻，包括但不限於：錯誤修復、代碼改進、功能添加、問題反饋。

- StarRailAssistant 的 `main` 分支是穩定的版本，所有開發均在 `main-beta` 分支進行。所以如果你想開 Pull Request，你的 commits 需要提交至 `main-beta`。

## 貢獻者

感謝以下貢獻者對本項目做出的貢獻

<a href="https://github.com/Starry-Wind/StarRailAssistant/graphs/contributors">

  <img src="https://contrib.rocks/image?repo=Starry-Wind/StarRailAssistant" />

</a>

![Alt](https://repobeats.axiom.co/api/embed/79d87540c597fc0b30893860e7b92da60c555fa9.svg "Repobeats analytics image")

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Starry-Wind/StarRailAssistant&type=Date)](https://star-history.com/#Starry-Wind/StarRailAssistant&Date)

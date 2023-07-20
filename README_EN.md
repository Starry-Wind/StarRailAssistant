<div align="center">

[Hey! Click me! Click me! Click me!](#usage)

[简体中文](README.md) | [繁体中文](README_CHT.md) | [English](README_EN.md) | [Documentation](https://sra.stysqy.top)

<img alt="LOGO" src="../../blob/map/temp/love!.png" style="border-radius:50%">

<h1 align="center">

Honkai Impact - Star Rail Assistant

</h1>

[![GitHub Stars](https://img.shields.io/github/stars/Starry-Wind/StarRailAssistant?style=flat-square)](https://github.com/Starry-Wind/StarRailAssistant/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Starry-Wind/StarRailAssistant?style=flat-square)](https://github.com/Starry-Wind/StarRailAssistant/network)
[![GitHub Issues](https://img.shields.io/github/issues/Starry-Wind/StarRailAssistant?style=flat-square)](https://github.com/Starry-Wind/StarRailAssistant/issues)
[![GitHub Contributors](https://img.shields.io/github/contributors/Starry-Wind/StarRailAssistant?style=flat-square)](https://github.com/Starry-Wind/StarRailAssistant/graphs/contributors)
[![GitHub License](https://img.shields.io/github/license/Starry-Wind/StarRailAssistant?style=flat-square)](https://github.com/Starry-Wind/StarRailAssistant/blob/main/LICENSE)
</div>

*****This script is still in the testing phase and may cause some strange issues.*****

***Hitting a wall while navigating? The path is wrong? Complaining about the slow pace? The map recording function has been added in beta-2.7.***

***You can now use the record_v7.2.py tool to record the path, and confirm that you are happy with the route XD***

Found a BUG? Want to give feedback on the code issues? Join the Technical & Blowwater Group：[QQ Group](https://qm.qq.com/cgi-bin/qm/qr?k=xdCO46fHlVcY7D2L7elXzqcxL3nyTGnW&jump_from=webapi&authKey=uWZooQ2szv+nG/re7luCKn8LW1KibSb0vvi0FycA45Mglm5AGM1GP2iJ+SiWmDwg)|[Telegram群组](https://t.me/+yeQEhnuT9O41NDM1)<br>

~~At present, this script only supports scaling 150%, screen resolution 2560x1440, and is now being greatly changed to solve the problem of screen rotation adaptation as soon as possible~~

## Disclaimer
This software is an external tool designed to automate playing Honkai Impact 3 - Star Rail. It is designed to interact with the game only through existing user interfaces and comply with relevant laws and regulations. The package aims to provide simplified and user-friendly interaction with the game, and it is not intended to disrupt game balance in any way or provide any unfair advantages. The package will not modify any game files or game code in any way.

This software is open source, free of charge, and for learning and exchange purposes only. The developer team has the final right to interpret this project. All problems arising from the use of this software are not related to this project and the developer team. If you encounter a merchant using this software to practice on your behalf and charging for it, it may be the cost of equipment and time, etc. The problems and consequences arising from this software have nothing to do with it.

Please note that based on MiHoYo's [FairPlay statement for Honkai Impact 3 - Star Rail](https://sr.mihoyo.com/news/111246?nav=news&type=notice):

    "It is strictly forbidden to use hack tools, accelerators, scripts or other third-party tools that undermine game fairness."
    "Once discovered, miHoYo (hereinafter referred to as "we") will take measures such as deducting illegal gains - freezing game accounts - permanent bans based on the severity and frequency of violations."

## Usage

1. Install [Python 3.11](https://www.python.org/downloads/release/python-3113/) (other versions may have many problems when installing dependencies)
    1. Enter `pip install -r requirements.txt` to install dependencies
2. Confirm that the game language is **Simplified Chinese**, key configuration is default, and sensitivity is default value.
3. If your computer resolution is 2560\*1440, please adjust the game resolution to 1920\*1080 (windowed); <br> if your computer resolution is 1920\*1080, please adjust the game resolution to 1920\*1080 (full screen).
4. The battle is automatic in the game, and ensure that your team has enough strength to push small monsters flatly. <br> (If you enable auto-battle persistence, change "auto_battle_persistence" in config.json to 1)
5. It is recommended not to track anything on the map, and the character's initial position is better in the **observation car**
6. Use a **long-range attack** character as the starter character. Currently, it is recommended to use **March 7** with more stable running.
7. Open **Honkai_Star_Rail.py** and wait for the program to automatically run to the "map number" entry
8. If you do not know what the **map number** is or if you want to **start over**running, enter "0" and press Enter.
9. During the five-second waiting period before starting, click back to the game screen to ensure that no menus or interfaces are open and wait for the program to run.
10. During the program running, **do not move** the keyboard and mouse, otherwise it may cause **deviation** or **collision** problems.
11. If using a simulator, please use a resolution of 1280\*720p. The default is the Nox simulator. For other simulators, please connect to the adb first. (The simulator may swallow mobile phone actions.)
12. If any problem occurs during the running process, or if you do not want to continue running and want to return to the main menu, use Ctrl+C and silently recite <font color= #E2027F>Long live Aileshia!</font>

## Configuration File Description

```json
{
    "real_width": 0, (actual width)
    "auto_battle_persistence": 0, (whether to enable auto-battle in the game, fill in 1 to enable)
    "real_height": 0, (actual length)
    "github_proxy": "", (github proxy)
    "rawgithub_proxy": "", (github proxy)
    "webhook_url": "",
    "start": true, (is it the first time running the script)
    "temp_version": "20230515205738",
    "star_version": "20230515220742",
    "level": "INFO",
    "adb": "127.0.0.1:62001",（62001 is the adb port）
    "adb_path": "temp\\adb\\adb",（adb file path）
    "proxies": ""
}
```

## Script Recording Thank you[@AlisaCat](https://github.com/AlisaCat-S)

1. Move with WASD. X is to enter combat. The left mouse button is to hit obstacles. F key is interact. Moving perspective with the mouse is forbidden. Only the direction keys left and right can be used to move perspective during recording. (During script execution, the left and right direction keys will be mapped = mouse movement.) During recording, you can only press one effective key on the keyboard (that is, multiple keys cannot be pressed at the same time). The script will only record the time when the key is pressed and the movement of the perspective, and will not record the pause time. (You can slowly record one key at a time to ensure accuracy). F9 stops recording and saves.
2. After completion, an output (time).json file will be generated. Please rename it and replace the map json you want to modify, and save the screenshot of the teleportation point in temp. (Then it can be submitted to the map branch or submitted to the management.)
3. Blank space filling in the map json example:

    ```json
    {
        "name": "Uraura-1",       （The map json name is 1-1_1.json）
        "author": "Starry-Wind",   （Author name. The second author cannot overwrite the name of the first author.）
        "start": [           （Identify the image of the map where the teleportation starts, move the mouse to the middle of the image, and press the button）
            {"map": 1},         （Press the m key to open the map）
            {"temp\\orientation_1.jpg": 1.5},     （After recognizing the picture of orientation_1.jpg, move the mouse to the middle of the picture and press the button）
            {"temp\\map_1.jpg": 2},               （See the specific image, usually the map text named "Uraura"）
            {"temp\\map_1_point_1.jpg": 1.5},       （The picture of the first teleportation point）
            {"temp\\transfer.jpg": 1.5}              （The picture of the word "Teleportation"）
        ]
    }
    ```

## Precautions

1. Image recognition is a screenshot of the game screen, so there should be no overlap.
2. Support maps **Space Station "Black Tower", Yaliluo VI, and Fairy Ship "Luo Fu"**
3. If you encounter wall collision problems in the map, you can help update the [map file submission here](https://github.com/Starry-Wind/StarRailAssistant/tree/map)
4. Please use **March 7** to run the map to get the best experience.
5. If you encounter any problem, please make sure you are using the latest version and check the [document](https://sra.stysqy.top)

⭐ **If you like it, give it a star~** ⭐

## Future Goals

- [ ] The simulated universe is under development.
- [x] GUI development
- [ ] Additional features will be added, such as treasure hunting, field exploration, and litter picking.

## Contributions

[Issue & Report a Bug](https://github.com/Starry-Wind/StarRailAssistant/issues/new/choose) | [Fork & Open a New PR](https://github.com/Starry-Wind/StarRailAssistant/compare)

All kinds of contributions including enhancements, new features, code improvements, issues and bugs reporting are welcome.

- The `main` branch of StarRailAssistant is the stable version, and all development is done in the `main-beta` branch. So if you want to open a Pull Request, your commits need to be submitted to the `main-beta` branch.

## Contributors

Thanks to the following contributors for their contributions to this project.

<a href="https://github.com/Starry-Wind/StarRailAssistant/graphs/contributors">

  <img src="https://contrib.rocks/image?repo=Starry-Wind/StarRailAssistant" />

</a>

![Alt](https://repobeats.axiom.co/api/embed/79d87540c597fc0b30893860e7b92da60c555fa9.svg "Repobeats analytics image")

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Starry-Wind/StarRailAssistant&type=Date)](https://star-history.com/#Starry-Wind/StarRailAssistant&Date)

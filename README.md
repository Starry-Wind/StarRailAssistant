# SRA
# 崩坏：星穹铁道小助手地图库
<img alt="LOGO" src="./temp/love!.png" style="border-radius:50%">


## | 文件结构
`map`文件夹为崩坏：星穹铁道自动锄大地脚本的导航文件。

> map文件提交规范:
> * `name`为地图名称
>   * 编写方式为 星球代号-地图代号_文件序号
>   * 星球代号: 空间站:1|雅利洛:2|仙舟:3
>   * 地图和文件代号: 按数序来
> * `author`请在后面添加作者名字，而不是覆盖前者的名字，每个作者的努力都不应该被遗忘
>   * ps: 无论你对map文件做了什么修改，你都应该写上你的名字并且不能覆盖前者的名字，包括但不仅限与修改一行文字、重写整个文件，都应该保留签字的名字
> * `start`为选择地图的步骤，其中`map`为打开地图
> * `map`为地图导航文件
> ```json
> {
>   "name": "流云渡-3",
>   "author": "xxx,xxx"
>   "start": [
>       {"map": 1},
>       {"temp\\map_3-1_point_3.png": 1.5},
>       {"temp\\transfer.jpg": 1.5}
>   ],
>   "map": []
> }
> ```
    
`temp`文件夹为崩坏：星穹铁道自动锄大地脚本的图片识别文件。

## 贡献者

感谢以下贡献者对本项目做出的贡献

<a href="https://github.com/Starry-Wind/Honkai-Star-Rail/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Starry-Wind/Honkai-Star-Rail" />

</a>

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Starry-Wind/Honkai-Star-Rail&type=Date)](https://star-history.com/#Starry-Wind/Honkai-Star-Rail&Date)

'''
Author: Night-stars-1 nujj1042633805@gmail.com
Date: 2023-05-13 03:08:07
LastEditors: Night-stars-1 nujj1042633805@gmail.com
LastEditTime: 2023-05-13 13:25:08
FilePath: \Honkai-Star-Rail-beta-2.4h:\Download\Zip\Honkai-Star-Rail-beta-2.7\map_res_list.py
Description: 

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
'''
import datetime
import hashlib
import json
import os
from pathlib import Path

star_path = Path(__file__).parent

star_list = []

this_path = str(Path(__file__).parent)


for file in star_path.rglob('*'):
    if '.git' not in str(file) and '__' not in str(file) and os.path.isfile(file):
        star_list.append({
            'path': str(file).replace(this_path, '').replace('\\', '/').lstrip('/'),
            'hash': hashlib.md5(file.read_bytes()).hexdigest()
        })

with open('star_list.json', 'w', encoding='utf-8') as f:
    json.dump(star_list, f, ensure_ascii=False, indent=2)

# 获取当前时间（UTC+8）
current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=8)

# 生成版本号
version = current_time.strftime("%Y%m%d%H%M%S")

# 创建版本号字典
version_dict = {
    "version": version
}

# 写入到version.json文件
with open("version.json", "w") as file:
    json.dump(version_dict, file)
'''
with open('config.json','r') as f:
    config = json.load(f)
    config['start'] = False

with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
'''

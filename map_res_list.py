import os
import datetime
import hashlib
import json
import zipfile
from pathlib import Path
from tqdm import tqdm
map_path = Path(__file__).parent / 'map'
picture_path = Path(__file__).parent / 'picture'

map_list = []
picture_list = []

this_path = str(Path(__file__).parent)

def zip_files(source_folder, zip_file):
    total_files = 0
    for root, dirs, files in os.walk(source_folder):
        total_files += len(files)
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        with tqdm(total=total_files, desc=zip_file, unit='files') as pbar:
            for root, dirs, files in os.walk(source_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    save_name = file_path.replace("./", "./map/")
                    zf.write(file_path, save_name)
                    pbar.update(1)

for file in map_path.rglob('*'):
    if os.path.isfile(file):
        map_list.append({
            'path': str(file).replace(this_path, '').replace('\\', '/').lstrip('/'),
            'hash': hashlib.md5(file.read_bytes()).hexdigest()
        })

for file in picture_path.rglob('*'):
    if os.path.isfile(file):
        picture_list.append({
            'path': str(file).replace(this_path, '').replace('\\', '/').lstrip('/'),
            'hash': hashlib.md5(file.read_bytes()).hexdigest()
        })

with open('map_list.json', 'w', encoding='utf-8') as f:
    json.dump(map_list, f, ensure_ascii=False, indent=2)

with open('picture_list.json', 'w', encoding='utf-8') as f:
    json.dump(picture_list, f, ensure_ascii=False, indent=2)

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

zip_files("./map", "map.zip")
zip_files("./picture", "picture.zip")
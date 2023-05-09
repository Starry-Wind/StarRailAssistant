import hashlib
import json
import zipfile
from pathlib import Path

map_path = Path(__file__).parent / 'map'
temp_path = Path(__file__).parent / 'temp'

map_list = []
temp_list = []

this_path = str(Path(__file__).parent)

for file in map_path.rglob('*'):
    map_list.append({
        'path': str(file).replace(this_path, '').replace('\\', '/').lstrip('/'),
        'hash': hashlib.md5(file.read_bytes()).hexdigest()
    })

for file in temp_path.rglob('*'):
    temp_list.append({
        'path': str(file).replace(this_path, '').replace('\\', '/').lstrip('/'),
        'hash': hashlib.md5(file.read_bytes()).hexdigest()
    })

with open('map_list.json', 'w', encoding='utf-8') as f:
    json.dump(map_list, f, ensure_ascii=False, indent=2)

with open('temp_list.json', 'w', encoding='utf-8') as f:
    json.dump(temp_list, f, ensure_ascii=False, indent=2)

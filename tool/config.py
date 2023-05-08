import os, orjson
def normalize_file_path(filename):
    # 尝试在当前目录下读取文件
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, filename)
    if os.path.exists(file_path):
        return file_path
    else:
        # 如果当前目录下没有该文件，则尝试在上一级目录中查找
        parent_dir = os.path.dirname(current_dir)
        file_path = os.path.join(parent_dir, filename)
        if os.path.exists(file_path):
            return file_path
        else:
            # 如果上一级目录中也没有该文件，则返回None
            return None
    
def read_json_file(file_path):
    file_path = normalize_file_path(file_path)
    with open(file_path, 'r') as f:
        data = orjson.load(f)
        return data, file_path

def modify_json_file(filename, key, value):
    data, file_path = read_json_file(filename)
    data[key] = value
    current_dir = os.getcwd()
    with open(file_path, 'w') as f:
        orjson.dump(data, f, indent=4, ensure_ascii=False)
        return True
    return False




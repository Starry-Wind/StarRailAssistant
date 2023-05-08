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
    
def read_json_file(filename):
    # 找到文件的绝对路径
    file_path = normalize_file_path(filename)
    with open(file_path, 'rb') as f:
        data = orjson.load(f.read())
        return data, file_path

def modify_json_file(filename, key, value):
    #先读，再写 
    data, file_path = read_json_file(filename)
    data[key] = value
    current_dir = os.getcwd()   
    with open(file_path, 'w') as f:
        f.write(orjson.dumps(data, indent=4, ensure_ascii=False))
        return 




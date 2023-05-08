import pymem
import pymem.process
class MemoryReader:
    def __init__(self):
        self.offset_x = 30815264
        self.offset_y = 30815268
        self.offset_z = 30815272

    def init(self):
        self.game = pymem.Pymem("StarRail.exe")
        self.base_address = pymem.process.module_from_name(self.game.process_handle, "unityplayer.dll").lpBaseOfDll
    
    def close(self):
        result = pymem.process.close_handle(self.game.process_handle)
        if result != True:
            raise Exception("关闭进程句柄失败")

    def get_location(self):
        try:
            # X, Y, Z
            return self.game.read_float(self.base_address + self.offset_x), self.game.read_float(self.base_address + self.offset_y), self.game.read_float(self.base_address + self.offset_z)
        except:
            print("读取坐标错误（大概率是游戏版本比软件支持的版本高）")
            return -65535, -65535, -65535
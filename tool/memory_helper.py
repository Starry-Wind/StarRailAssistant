import pymem
import pymem.process

class PlayerLocation:
    def __init__(self) -> None:
        try:
            self.game = pymem.Pymem("StarRail.exe")
            self.base_address = pymem.process.module_from_name(self.game.process_handle, "unityplayer.dll").lpBaseOfDll
        except:
            print("游戏初始化错误")
        self.offset_x = 30815264
        self.offset_y = 30815268
        self.offset_z = 30815272
    def get_xyz(self):
        try:
            return self.game.read_float(self.base_address + self.offset_x), self.game.read_float(self.base_address + self.offset_y), self.game.read_float(self.base_address + self.offset_z)
        except:
            print("读取坐标错误（大概率是游戏版本比软件支持的版本高）")
            return -65535, -65535, -65535
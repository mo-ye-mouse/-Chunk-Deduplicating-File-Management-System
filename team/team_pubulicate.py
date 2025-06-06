import hashlib
from concurrent.futures import ThreadPoolExecutor
import os


class TTTDS:
    def __init__(self):
        self.file_path = ""
        self.window = 1000  # 滑动窗口大小
        self.Tmax = 4096  # 最大阈值
        self.Tmin = 2048  # 最小阈值
        self.D = 540  # 主除数
        self.Ddash = 270  # 次除数
        self.R = 0
        self.breakpoint = [0]
        self.hash = hash  # 哈希函数

    def init(self, file_path, window_size=1000, max=4096, min=2048, main_d=540, minor_d=270, r=0):
        self.__init__()
        self.window = window_size
        self.Tmax = max
        self.Tmin = min
        self.D = main_d
        self.Ddash = minor_d
        self.R = r
        self.file_path = file_path

    def back_point(self):
        return self.breakpoint

    def chunking(self, file_path, end, start=0):
        # 分块
        pass


def delicate():
    # 去重
    pass


def hash():
    pass

# if __name__ == '__main__':
#     测试代码

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
        self.breakpoint = [start]
        try:
            with open(file_path, 'rb') as f:
                f.seek(start)
                window_buffer = f.read(self.window)
                position = start + len(window_buffer)
                while position < end:
                    # 内联SHA-256哈希计算
                    hash_val = int(hashlib.sha256(window_buffer).hexdigest(), 16)
                    # TTTD断点检测条件
                    if (hash_val % self.D == self.R) or \
                            (hash_val % self.Ddash == self.R and len(window_buffer) >= self.Tmin):
                        self.breakpoint.append(position)
                        window_buffer = bytes()
                    # 滑动窗口
                    next_byte = f.read(1)
                    if not next_byte:
                        break
                    window_buffer = window_buffer[1:] + next_byte
                    position += 1
                    # 强制分块条件
                    if len(window_buffer) > self.Tmax:
                        self.breakpoint.append(position - len(window_buffer))
                        window_buffer = bytes()
                # 添加最终断点
                if position not in self.breakpoint:
                    self.breakpoint.append(position)
            return self.breakpoint
        except Exception as e:
            print(f"分块错误: {str(e)}")
            return None


def delicate():
    # 去重
    pass


def hash():
    pass

# if __name__ == '__main__':
#     测试代码

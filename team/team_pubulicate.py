import hashlib
from concurrent.futures import ThreadPoolExecutor
import os
from sys import orig_argv

class TTTDS:
    def __init__(self):
        self.file_path = ""
        self.window = 48  # 滑动窗口大小
        self.Tmax = 2800  # 最大阈值
        self.Tmin = 460  # 最小阈值
        self.D = 540  # 主除数
        self.Ddash = 270  # 次除数
        self.R = -1 # 余数
        self.breakpoint = [0]
        self.backupBreak = 0
        self.switchP = 1600 # 切换参数

    def init(self, file_path):
        self.file_path = file_path

    def back_point(self):
        return self.breakpoint

    def chunking(self, file_path, end, start=0):
        try:
            with open(file_path, 'rb') as f:
                f.seek(start)
                window_buffer = f.read(self.window)
                if not window_buffer:
                    return self.breakpoint
                # 初始化滚动哈希
                hash_value = rolling_hash(window_buffer)
                position = start + len(window_buffer)
                lastP = start
                currP = start + len(window_buffer)
                original_D = self.D
                original_Ddash = self.Ddash
                while position < end:
                    # TTTDS断点检测条件
                    if hash_value % self.D == self.R:
                        self.breakpoint.append(position)
                        lastP = position
                        currP = position
                        self.backupBreak = 0
                        self.D = original_D
                        self.Ddash = original_Ddash
                    elif hash_value % self.Ddash == self.R:
                        self.backupBreak = position
                    # 滑动窗口
                    next_byte = f.read(1)
                    if not next_byte:
                        break
                    # 更新滚动哈希值
                    window_buffer = window_buffer[1:] + next_byte
                    hash_value = rolling_hash(window_buffer)
                    currP += 1
                    position += 1
                    # 切换主除数和次除数
                    if (currP - lastP) > self.switchP:
                        temp_Ddash = self.Ddash
                        self.D = self.Ddash
                        self.Ddash = temp_Ddash // 2
                    # 强制分块条件
                    if (currP - lastP) >= self.Tmax:
                        if self.backupBreak != 0:
                            self.breakpoint.append(self.backupBreak)
                            lastP = self.backupBreak
                        else:
                            self.breakpoint.append(position - len(window_buffer))
                            lastP = position - len(window_buffer)
                        self.backupBreak = 0
                        # 恢复原始的主除数和次除数
                        self.D = original_D
                        self.Ddash = original_Ddash
                        # 检查最小阈值
                    if (currP - lastP) < self.Tmin:
                        continue
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

def rolling_hash(content):
    window_size = 48  # 固定窗口大小
    position = 0  # 固定起始位置
    base = 256  # 字符集大小
    prime = 101  # 用于取模的素数
    h = 1
    for _ in range(window_size - 1):
        h = (h * base) % prime
    hash_value = 0
    for byte in content[position:position + window_size]:
        hash_value = (base * hash_value + byte) % prime
    return hash_value

# if __name__ == '__main__':
#     测试代码

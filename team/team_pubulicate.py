import hashlib
from concurrent.futures import ThreadPoolExecutor
import os
from sys import orig_argv

class TTTDS:
    def __init__(self):
        self.file_path = " "
        self.window = 48  # 滑动窗口大小
        self.Tmax = 2800  # 最大阈值
        self.Tmin = 460  # 最小阈值
        self.D = 540  # 主除数
        self.second_D = 270  # 次除数
        self.breakpoint = [0]
        self.backupBreak = 0
        self.switchP = 1600 # 切换参数

    def init(self, file_path):
        self.file_path = file_path

    def reset_divisor(self):
        # 恢复主除数和次除数的原始值
        self.D = 540
        self.second_D = 270

    def chunking(self, file_path):
        file_size = os.path.getsize(file_path)
        buffer = bytearray(self.window)     # 读取初始窗口数据
        lastP = 0
        currP = 0
        try:
            with open(file_path, 'rb') as f:
                f.seek(lastP)          # 移动指针到上一个块的结束位置
                f.readinto(buffer)     # 读取初始窗口数据
                currP = self.window    # 当前位置设置为窗口大小
                while currP < file_size:
                    byte = f.read(1)
                    if not byte:
                        break
                    buffer = buffer[1:] + byte
                    currP += 1   # 更新当前位置
                    # 判断是否达到最小阈值，没有则currP继续前进
                    if currP - lastP < self.Tmin:
                        continue
                    # 判断是否超过switchP,切换主除数和次除数
                    if currP - lastP > self.switchP:
                        self.D, self.second_D = self.second_D // 2, self.D
                    # 计算初始窗口的哈希值
                    hash_value = rolling_hash(buffer)
                    # 判断是否满足主次除数的条件，记录备份断点和确定块边界
                    if hash_value % self.second_D == self.second_D - 1:
                        self.backupBreak = currP
                    if hash_value % self.D == self.D - 1:
                        self.breakpoint.append(currP)
                        self.backupBreak = 0    # 重置备份断点
                        lastP = currP   # 更新最后一个块的结束位置
                        self.reset_divisor()
                        continue
                    # 判断是否达到最大阈值，如果有备份断点，使用备份断点作为块边界；否则，使用当前位置作为块边界
                    if currP - lastP >= self.Tmax:
                        if self.backupBreak:
                            self.breakpoint.append(self.backupBreak)
                            lastP = self.backupBreak
                        else:
                            self.breakpoint.append(currP)
                            lastP = currP   # 继续前进，分块
                        self.backupBreak = 0    # 重置备份断点
                        self.reset_divisor()
                if lastP < file_size:  # 确保最后一个块被添加
                    self.breakpoint.append(file_size)
        except Exception as e:
            print(f"分块错误: {str(e)}")
            return None
        return self.breakpoint


def delicate(path1, path2):
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

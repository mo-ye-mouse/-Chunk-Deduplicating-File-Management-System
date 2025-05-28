import hashlib
from concurrent.futures import ThreadPoolExecutor
import os
import time


class Chunking:
    def __init__(self, window_size=256, max_chunk_size=8196, min_chunk_size=512, main_d=16, minor_d=8, r=0):
        self.window_size = window_size
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.footer_size = 1
        self.main_d = main_d
        self.minor_d = minor_d
        self.R = r
        self.breakpoint = [0]
        self.hash = hash_cal

    def back_point(self):
        return self.breakpoint

    def chunking(self, file_path, end, start=0):
        with open(file_path, 'rb') as f:
            start += self.min_chunk_size - self.window_size
            f.seek(start)
            new_chunk = True  # 新块判断
            change_d = False
            while end - start > self.min_chunk_size:
                if new_chunk:
                    # 进入新块
                    content = f.read(self.window_size)
                    new_chunk = False
                else:
                    # 进入旧块，每次读取相应补偿的字节数
                    content = content[self.footer_size:] + f.read(self.footer_size)
                # 计算hash值，判断是否更换除数
                hash_int = self.hash(content)
                current_d = self.minor_d if change_d else self.main_d
                # 判断断点
                if hash_int % current_d == self.R:
                    self.breakpoint.append(start + self.window_size - 1)
                    start += self.min_chunk_size
                    new_chunk = True
                else:
                    start += self.footer_size
                f.seek(start)
                # 如果到达最大块尺寸，则切换除数并重新设置断点
                if start - self.breakpoint[-1] >= self.max_chunk_size:
                    change_d = not change_d
                    new_chunk = True
                    # 如果都无法设置断点，那么将最大块作为断点*
                    if change_d:
                        start = self.breakpoint[-1] + 1 - self.window_size + self.min_chunk_size
                    else:
                        self.breakpoint.append(start + self.window_size - 1)
                        start += self.min_chunk_size
                    f.seek(start)
            self.breakpoint.append(end - 1)

    def start(self, file_path):
        # 设置线程参数
        file_size = os.path.getsize(file_path)
        standard_size = 1024*100  # 标准分块大小
        if file_size <= standard_size:
            self.chunking(file_path, file_size)
            return
        num = min(file_size // standard_size, 16)  # 线程数
        chunk_num = file_size // standard_size  # 块数
        if file_size % standard_size != 0:
            chunk_num += 1
        overlap = 100
        # 线程池
        with ThreadPoolExecutor(max_workers=num) as executor:
            futures = []
            for i in range(chunk_num):
                start_pos = i * standard_size
                end_pos = min(start_pos + standard_size + overlap, file_size)
                future = executor.submit(self.chunking, file_path, end_pos, start_pos)
                futures.append(future)
            # 等待所有线程结束
            for future in futures:
                future.result()
        self.treat_breakpoint()

    def treat_breakpoint(self):
        # 去重
        self.breakpoint = sorted(set(self.breakpoint))
        i = 0
        while i < len(self.breakpoint) - 2:
            if self.breakpoint[i+1] - self.breakpoint[i] < self.min_chunk_size:
                if (self.breakpoint[i+2] - self.breakpoint[i] < self.max_chunk_size and
                        self.breakpoint[i+1] - self.breakpoint[i] >= self.min_chunk_size):
                    self.breakpoint.pop(i+1)
                else:
                    if i + 2 < len(self.breakpoint):
                        self.breakpoint[i+1] = (self.breakpoint[i] + self.breakpoint[i+2])//2
                        i += 1
            else:
                i += 1


class Delicate:
    def __init__(self):
        self.hasher = hash_cal
        self.index = {}

    def delicate(self, path1, path2):
        indicate = []
        chunking1 = Chunking()
        chunking2 = Chunking()
        chunking1.start(path1)
        chunking2.start(path2)
        breakpoint1 = chunking1.back_point()
        breakpoint2 = chunking2.back_point()
        hasher1 = self.gat_hash(chunking1.back_point(), path1)
        hasher2 = self.gat_hash(chunking2.back_point(), path2)
        for j in range(len(hasher2)):
            for i in range(len(hasher1)):
                if hasher1[i] == hasher2[j]:
                    self.index[breakpoint1[i]] = path1
                    i += 1
                    break
                elif i == len(hasher1) - 1:
                    self.index[breakpoint2[j]] = path2
                    indicate.append(breakpoint2[j])
                    indicate.append(breakpoint2[j+1])
                    break
            j += 1
        self.remove(file_path2, indicate)

    def gat_hash(self, breakpoints, path):
        hasher = []
        with open(path, 'rb') as f:
            for i in range(len(breakpoints)-1):
                f.seek(breakpoints[i])
                content = f.read(breakpoints[i+1]-breakpoints[i])
                hasher.append(self.hasher(content))
        return hasher

    def remove(self, path, sat_new):
        with open(path, 'rb') as source_file:
            dir_path = os.path.dirname(path)
            s = time.time()
            for sat in range(0, len(sat_new), 2):
                source_file.seek(sat_new[sat])
                data = source_file.read(sat_new[sat + 1] - sat_new[sat])
                with open(os.path.join(dir_path, str(sat//2+10)) + '.txt', 'ab') as target_file:
                    target_file.write(data)
            end = time.time()
            print("耗时：", end - s)
        # os.remove(path)

    def store_index(self):
        return self.index


def hash_cal(content):
    hash_256 = hashlib.sha256(content)
    return int(hash_256.hexdigest(), 16)


if __name__ == '__main__':
    file_path1 = input("请输入文件路径：")
    file_path2 = input("请输入文件路径：")
    delicate = Delicate()
    delicate.delicate(file_path1, file_path2)
    print(delicate.store_index())

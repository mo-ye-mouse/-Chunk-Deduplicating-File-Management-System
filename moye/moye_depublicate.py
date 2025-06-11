import hashlib
from concurrent.futures import ThreadPoolExecutor
import os
import mmap
from collections import defaultdict


class Chunking:
    def __init__(self, file_path, window_size=256, max_chunk_size=8196, min_chunk_size=512, main_d=16, minor_d=8, r=0):
        self.window_size = window_size
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.footer_size = 1
        self.main_d = main_d
        self.minor_d = minor_d
        self.R = r
        self.breakpoint = [0]
        self.hash = rolling_hash
        self.chunking(file_path, os.path.getsize(file_path))

    def back_point(self):
        return self.breakpoint

    def chunking(self, file_path, end, start=0):
        with open(file_path, 'rb') as f:
            start += self.min_chunk_size
            f.seek(start - self.window_size)
            new_chunk = True  # 新块判断
            change_d = False  # 除数切换判断
            while end - start > self.min_chunk_size:
                # 进入块判断
                if new_chunk:
                    f.read(self.min_chunk_size-self.window_size)
                    content = f.read(self.window_size)
                    new_chunk = False
                else:
                    content = content[self.footer_size:] + f.read(self.footer_size)
                # 计算hash值，判断是否更换除数
                hash_int = self.hash(content)
                current_d = self.minor_d if change_d else self.main_d
                # 判断断点
                if hash_int % current_d == self.R and start - self.breakpoint[-1] >= self.min_chunk_size:
                    self.breakpoint.append(start + self.window_size - 1)
                    start = f.tell() + self.min_chunk_size
                    new_chunk = True
                else:
                    start += self.footer_size
                # 如果到达最大块尺寸，则切换除数并重新设置断点
                if start - self.breakpoint[-1] >= self.max_chunk_size:
                    change_d = not change_d
                    new_chunk = True
                    # 如果都无法设置断点，那么将最大块作为断点
                    if change_d:
                        start = self.breakpoint[-1]
                        f.seek(start)
                    else:
                        self.breakpoint.append(f.tell() - 1)
                        start = f.tell()
            self.breakpoint.append(end - 1)


class Delicate:
    def __init__(self):
        self.hasher = hash_cal
        self.index = {}

    def delicate(self, path1, path2):
        indicate = []
        chunking1 = Chunking(path1)
        chunking2 = Chunking(path2)
        breakpoint1 = chunking1.back_point()
        breakpoint2 = chunking2.back_point()
        hasher1 = self.gat_hash(chunking1.back_point(), path1)
        hasher2 = self.gat_hash(chunking2.back_point(), path2)
        # 线程池处理去重,处理大小小于800mb的文件
        with ThreadPoolExecutor(max_workers=6) as executor:
            features = []
            dex = 0
            for j in range(len(hasher2)):
                for i in range(len(hasher1)):
                    if len(indicate) == 100*1024:
                        feature = executor.submit(self.removes, path2, indicate)
                        features.append(feature)
                        indicate.clear()
                    if len(self.index) == 500:
                        self.store(dex)
                        dex += 1
                        self.index.clear()
                    if hasher1[i] == hasher2[j]:
                        self.index[breakpoint1[i]] = path1
                        i += 1
                        break
                    elif i == len(hasher1) - 1:
                        self.index[breakpoint2[j]] = path2
                        indicate.append(breakpoint2[j])
                        indicate.append(breakpoint2[j+1])
                        break
            if len(indicate) > 0:
                feature = executor.submit(self.removes, path2, indicate)
                features.append(feature)
                j += 1
            self.store(dex)
            for feature in features:
                feature.result()
        os.remove(path2)

    def gat_hash(self, breakpoints, path):
        hasher = []
        with open(path, 'rb') as f:
            for i in range(len(breakpoints)-1):
                f.seek(breakpoints[i])
                content = f.read(breakpoints[i+1]-breakpoints[i])
                hasher.append(self.hasher(content))
        return hasher  # 返回hash列表

    def removes(self, path, sat_new):
        # 映射文件实现去重
        segments = [(sat_new[sat], sat_new[sat+1])for sat in range(0, len(sat_new), 2)]
        target_files = defaultdict(list)  # 目标文件字典，key为目标文件路径，value为数据列表，默认值为[]
        with open(path, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
            for start, end in segments:
                data = mm[start:end]  # 从映射内存读取数据
                file_idx = segments.index((start, end)) // 2 + 10  # 计算文件编号
                target_path = os.path.join(os.path.dirname(path), f"{file_idx}.txt")  # 目标文件路径
                target_files[target_path].append(data)
            mm.close()  # 关闭映射文件
        # 写入目标文件
        for filename, datas in target_files.items():
            with open(filename, 'ab') as target_file:
                target_file.write(b''.join(datas))

    def store(self, dex):
        with open(f"D:\\try\\path\\index\\{dex}.txt", 'ab') as f:
            for key, value in self.index.items():
                f.write(f"{key} {value}\n".encode())


def hash_cal(content):
    hash_256 = hashlib.sha256(content)
    return int(hash_256.hexdigest(), 16)


def rolling_hash(content):
    window_size = 3  # 固定窗口大小
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


if __name__ == '__main__':
    file_path1 = input("请输入文件路径：")
    file_path2 = input("请输入文件路径：")
    delicate = Delicate()
    delicate.delicate(file_path1, file_path2)

    #     断点多线程
    # def start(self, file_path):
    #     a = time.time()
    #     # 设置线程参数
    #     file_size = os.path.getsize(file_path)
    #     standard_size = 1024*100  # 标准分块大小
    #     if file_size <= standard_size:
    #         self.chunking(file_path, file_size)
    #         return
    #     num = min(file_size // standard_size, 16)  # 线程数
    #     chunk_num = file_size // standard_size  # 块数
    #     if file_size % standard_size != 0:
    #         chunk_num += 1
    #     overlap = 100
    #     # 线程池
    #     with ThreadPoolExecutor(max_workers=num) as executor:
    #         futures = []
    #         for i in range(chunk_num):
    #             start_pos = i * standard_size
    #             end_pos = min(start_pos + standard_size + overlap, file_size)
    #             future = executor.submit(self.chunking, file_path, end_pos, start_pos)
    #             futures.append(future)
    #         # 等待所有线程结束
    #         for future in futures:
    #             future.result()
    #     self.treat_breakpoint()
    #     b = time.time()
    #     c = b - a
    #     print(f"分块耗时：{c}s")
    #     print(f"分块数：{len(self.breakpoint)}")
    #
    # def treat_breakpoint(self):
    #     # 调整断点，去除重复断点
    #     self.breakpoint = sorted(set(self.breakpoint))
    #     i = 0
    #     while i < len(self.breakpoint) - 2:
    #         if self.breakpoint[i+1] - self.breakpoint[i] < self.min_chunk_size:
    #             if (self.breakpoint[i+2] - self.breakpoint[i] < self.max_chunk_size and
    #                     self.breakpoint[i+1] - self.breakpoint[i] >= self.min_chunk_size):
    #                 self.breakpoint.pop(i+1)
    #             else:
    #                 if i + 2 < len(self.breakpoint):
    #                     self.breakpoint[i+1] = (self.breakpoint[i] + self.breakpoint[i+2])//2
    #                     i += 1
    #         else:
    #             i += 1

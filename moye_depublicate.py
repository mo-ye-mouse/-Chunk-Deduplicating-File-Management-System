import hashlib
import threading
import os


class MyThread(threading.Thread):
    def __init__(self, func, args):
        super().__init__()
        self.func = func
        self.args = args


class Chunking:
    def __init__(self, hasher=None):
        # 初始化超参数
        self.window_size = 1024
        self.max_chunk_size = 4096
        self.min_chunk_size = 128
        self.footer_size = 1
        self.main_d = 6
        self.minor_d = 3
        self.R = 2
        self.breakpoint = [0]
        self.use = False
        self.hash = hash_cal
        if hasher is not None:
            self.hash = hasher

    def init(self, use=False, window_size=1024, max_chunk_size=4096, min_chunk_size=128, footer_size=1,
             main_d=6, minor_d=3, r=2):
        self.window_size = window_size
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.footer_size = footer_size
        self.main_d = main_d
        self.minor_d = minor_d
        self.R = r
        self.use = use

    def back_point(self):
        return self.breakpoint

    def chunking(self, file_path, fs, start=0):
        file_size = fs
        with open(file_path, 'rb') as f:
            start += self.min_chunk_size - self.window_size
            f.seek(start)
            judge1 = True  # 新块判断
            judge2 = False  # 旧块判断
            while True:
                if file_size < self.min_chunk_size:
                    return None
                elif file_size - start < self.min_chunk_size:
                    self.breakpoint.append(file_size - 1)
                    break
                if judge1:
                    # 进入新块
                    content = f.read(self.window_size)
                    judge1 = False
                else:
                    # 进入旧块，每次读取相应补偿的字节数
                    byte = f.read(self.footer_size)
                    content = content[self.footer_size:] + byte
                # 计算hash值
                hash_int = self.hash(content)
                # 判断断点*
                if hash_int % self.main_d == self.R:
                    self.breakpoint.append(start + self.window_size - 1)
                    start += self.min_chunk_size
                    judge1 = True
                    f.seek(start)
                else:
                    start += self.footer_size
                    f.seek(start)
                # 如果到达最大块尺寸，则切换除数并重新设置断点
                if start - self.breakpoint[-1] >= self.max_chunk_size:
                    self.main_d, self.minor_d = self.minor_d, self.main_d
                    judge1 = True
                    # 如果都无法设置断点，那么将最大块作为断点*
                    if judge2:
                        self.breakpoint.append(start + self.window_size - 1)
                        start += self.min_chunk_size
                        judge2 = False
                        f.seek(start)
                        continue
                    start = self.breakpoint[-1] + 1 - self.window_size + self.min_chunk_size
                    judge2 = True
                    f.seek(start)

    def start(self, file_path, start=0):
        file_size = os.path.getsize(file_path)
        if not self.use:
            self.chunking(file_path, file_size)
        else:
            standard_size = 1024*1024*100
            if file_size <= standard_size:
                self.chunking(file_path, file_size)
            else:
                num = file_size // standard_size
                if file_size % standard_size != 0:
                    num += 1
                if num > 16:
                    num = 16
                chunk_size = file_size // num
                overlap = 1024*10
                threads = []
                for i in range(num):
                    start = start + i * chunk_size
                    end = start + chunk_size + overlap
                    if end > file_size:
                        end = file_size
                    part_size = end - start
                    thread = MyThread(self.chunking, (file_path, part_size, start))
                    threads.append(thread)
                    thread.start()
                for thread in threads:
                    thread.join()
        self.treat_breakpoint()

    def treat_breakpoint(self):
        ls = list(set(self.breakpoint))
        self.breakpoint = ls
        self.breakpoint.sort()
        for i in range(len(self.breakpoint)-1):
            if self.breakpoint[i+1] - self.breakpoint[i] < self.min_chunk_size:
                if (self.breakpoint[i+2] - self.breakpoint[i] < self.max_chunk_size and
                        self.breakpoint[i+1] - self.breakpoint[i] >= self.min_chunk_size):
                    self.breakpoint.pop(i+1)
                else:
                    self.breakpoint[i+1] = (self.breakpoint[i] + self.breakpoint[i+2])//2


class Delicate:
    def __init__(self):
        self.hasher = hash_cal
        self.index = {}

    def delicate(self, file_path1, file_path2):
        indicate = []
        chunking1 = Chunking()
        chunking2 = Chunking()
        chunking1.init(True)
        chunking2.init(True)
        chunking1.start(file_path1)
        chunking2.start(file_path2)
        breakpoint1 = chunking1.back_point()
        breakpoint2 = chunking2.back_point()
        hasher1 = self.gat_hash(breakpoint1, file_path1)
        hasher2 = self.gat_hash(breakpoint2, file_path2)
        j = 0
        for h2 in hasher2:
            i = 0
            for h1 in hasher1:
                if h1 == h2:
                    self.index[str(i)+' '+str(breakpoint1[i])] = file_path1
                    i += 1
                else:
                    self.index[str(i)+' '+str(breakpoint2[j])] = file_path2
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
                hash_int = self.hasher(content)
                hasher.append(hash_int)
        return hasher

    def remove(self, path, sat_new):
        i = 0
        with open(path, 'rb') as source_file:
            dir_path = os.path.dirname(path)
            for sat in range(0, len(sat_new), 2):
                source_file.seek(sat_new[sat])
                data = source_file.read(sat_new[sat + 1] - sat_new[sat])
                with open(os.path.join(dir_path, "delicate" + str(i)), 'ab') as target_file:
                    target_file.write(data)
        os.remove(path)

    def return_index(self):
        return self.index


def hash_cal(content):
    hash_256 = hashlib.sha256()
    hash_256.update(content)
    hash_value = hash_256.hexdigest()
    hash_int = int(hash_value, 16)
    return hash_int


def main():
    file_path1 = input("请输入文件路径：")
    file_path2 = input("请输入文件路径：")
    delicate = Delicate()
    delicate.delicate(file_path1, file_path2)
    index = delicate.return_index()
    print(index)


if __name__ == '__main__':
    main()

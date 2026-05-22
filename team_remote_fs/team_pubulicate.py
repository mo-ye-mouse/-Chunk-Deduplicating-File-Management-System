import hashlib
import os
from collections import defaultdict
import file_hash_tree
from concurrent.futures import ThreadPoolExecutor
import mmap
import mysql.connector


class TTTDS:
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
                    content = content[1:] + f.read(1)
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
                # 如果到达最大块尺寸，则切换除数并重新设置断点D--d
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


def gat_hash(breakpoints, path):
    hasher = []
    with open(path, 'rb') as f:
        for i in range(len(breakpoints) - 1):
            content = f.read(breakpoints[i + 1] - breakpoints[i])
            hasher.append(hash256(content))
    return hasher  # 返回hash列表


def hash256(content):
    hash_256 = hashlib.sha256(content)
    return hash_256.hexdigest()


def hashMD5(content):
    hash_md5 = hashlib.md5(content)
    return int(hash_md5.hexdigest(), 16)


def rolling_hash(content):
    window_size = 48  # 固定窗口大小
    position = 0  # 固定起始位置
    h = 1
    for _ in range(window_size - 1):
        h = (h * 256) % 101
    hash_value = 0
    for byte in content[:position + window_size]:
        hash_value = (256 * hash_value + byte) % 101
    return hash_value


def moving(unique_chunks, unique_hashes, tar):
    """
    根据唯一块列表将文件块从源文件复制到目标文件，然后删除源文件
    :param unique_hashes:
    :param unique_chunks: 唯一块的位置列表，每个元素是一个元组(start_pos,end_pos)
    :param tar: 源文件路径
    :return: 操作是否成功
    """
    extension = os.path.splitext(tar)[1]  # 文件扩展名.txt
    target_files = defaultdict(list)  # 目标文件字典，key为目标文件路径，value为数据列表，默认值为[]
    with open(tar, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        for i in range(len(unique_chunks)):
            data = mm[unique_chunks[i][0]:unique_chunks[i][1]]  # 从映射内存读取数据
            dir_path = f"D:/try/path/{unique_hashes[i][0:2]}/{unique_hashes[i][2:4]}/{unique_hashes[i][-4:]}"
            target_path = os.path.join(dir_path, f"{unique_hashes[i]}.{extension}")  # 目标文件路径
            target_files[target_path].append(data)
        mm.close()  # 关闭映射文件
    # 写入目标文件
    for filename, datas in target_files.items():
        with open(filename, 'wb') as target_file:
            target_file.write(b''.join(datas))


def store(hashes, file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
        file_hash = hashMD5(content)
        extension = os.path.splitext(file_path)[1]
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "sha256_directories"
    }
    try:
        # 连接数据库
        con1 = mysql.connector.connect(**db_config)
        cur1 = con1.cursor(dictionary=True)
        file_tree = file_hash_tree.FileHashTree(con1, cur1)
        file_tree.add(file_hash, hashes)
        cur1.close()
        con1.close()
        con2 = mysql.connector.connect(**db_config)
        cur2 = con2.cursor()
        hash_tree = file_hash_tree.HashTree(con2, cur2)
        for hash_value in hashes:
            tp = len(str(hash_value))
            print()
            hash_tree.add_file(str(hash_value), extension)
        cur2.close()
        con2.close()

    except Exception as e:
        print(f"连接数据库失败: {str(e)}")


def deduplicate(file1_path, file2_path):
    """
    比较两个文件的块哈希值，找出不重复的块
    :param file1_path: 第一个文件路径
    :param file2_path: 第二个文件路径
    :return: 不重复的块信息列表
    """
    # 创建源文件和目标文件分块对象， 获取所有块的哈希值
    root_fs = TTTDS(file1_path)
    target_fs = TTTDS(file2_path)
    r_points = root_fs.back_point()
    t_points = target_fs.back_point()
    r_hashes = gat_hash(r_points, file1_path)
    t_hashes = gat_hash(t_points, file2_path)  # 目标文件块哈希值列表

    unique_chunks = []  # 唯一块前后断点列表
    unique_hashes = []  # 唯一块哈希值列表
    # 线程池处理去重
    with ThreadPoolExecutor(max_workers=6) as executor:
        features = []
        for i in range(len(t_hashes)):
            if not t_hashes[i] in r_hashes:
                unique_chunks.append((t_points[i], t_points[i+1]))
                unique_hashes.append(t_hashes[i])
            if len(unique_chunks) == 20:
                feature = executor.submit(moving, unique_chunks, unique_hashes, file2_path)
                features.append(feature)
                unique_chunks.clear()
        if len(unique_chunks) > 0:
            feature = executor.submit(moving, unique_chunks, unique_hashes, file2_path)
            features.append(feature)
        # 存储目录
        store(t_hashes, file2_path)
        for feature in features:
            feature.result()
    # os.remove(file2_path)

#
# if __name__ == '__main__':
#     file1_path = "D:/try/2.txt"
#     file2_path = "D:/try/3.txt"
#     deduplicate(file1_path, file2_path)
#     print("Deduplication completed.")


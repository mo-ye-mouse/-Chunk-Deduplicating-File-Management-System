import hashlib
import os
from collections import defaultdict
import file_hash_tree
from concurrent.futures import ThreadPoolExecutor
import mmap
import mysql.connector


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
        self.switchP = 1600   # 切换参数

    def back_point(self):
        return self.breakpoint

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


def calculate_chunk_hash(file_path, breakpoints):
    """
    计算文件各块的哈希值
    :param file_path: 文件路径
    :param breakpoints: 断点列表
    :return: 顺序块哈希值列表
    """
    chunks_hashes = []
    try:
        with open(file_path, 'rb') as f:
            for i in range(len(breakpoints)-1):
                content = f.read(breakpoints[i+1] - breakpoints[i])
                chunks_hashes.append(hash256(content))
        return chunks_hashes
    except Exception as e:
        print(f"计算哈希值错误:{str(e)}")
        return[]


def hash256(content):
    hash_256 = hashlib.sha256(content)
    return int(hash_256.hexdigest(), 16)


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
    extension = os.path.splitext(tar)[1]  # 文件扩展名
    target_files = defaultdict(list)  # 目标文件字典，key为目标文件路径，value为数据列表，默认值为[]
    with open(tar, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
        for i in range(len(unique_chunks)):
            data = mm[unique_chunks[i][0]:unique_chunks[i][1]]  # 从映射内存读取数据
            dir_path = f"D:/try/path/{unique_hashes[i][0:2]}/{unique_hashes[i][2:4]}/{unique_hashes[i][-4:]}"
            target_path = os.path.join(dir_path, f"{unique_hashes[i]}.{extension}")  # 目标文件路径
            target_files[target_path].append(data)
        mm.close()  # 关闭映射文件
    # 写入目标文件
    for filename, datas in target_files.items():
        with open(filename, 'ab') as target_file:
            target_file.write(b''.join(datas))


def store(hashes, file_path):
    with open(file_path, 'wb') as f:
        content = f.read()
        file_hash = hash256(content)
        extension = os.path.splitext(file_path)[1]
    db_config = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "sha256_directories"
    }
    try:
        # 连接数据库
        con = mysql.connector.connect(**db_config)
        cur = con.cursor(dictionary=True)
        file_tree = file_hash_tree.FileHashTree(con, cur)
        hash_tree = file_hash_tree.HashTree(con, cur)
        file_tree.add(file_hash, hashes)
        for hash_value in hashes:
            hash_tree.add_file(hash_value, extension)
        cur.close()
        con.close()
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
    root_fs = TTTDS()
    target_fs = TTTDS()
    root_fs.init(file1_path)
    target_fs.init(file2_path)
    r_points = root_fs.back_point()
    t_points = target_fs.back_point()
    r_hashes = calculate_chunk_hash(file1_path, r_points)
    t_hashes = calculate_chunk_hash(file2_path, t_points)  # 目标文件块哈希值列表

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
    os.remove(file2_path)

# if __name__ == '__main__':
#     测试代码

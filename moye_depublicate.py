import hashlib
import os

# 初始化参数：窗口尺寸，最大块尺寸和最小块尺寸，步长
# hasher2是旧文件
chunk_size = 10
max_chunk_size = 25
min_chunk_size = 15
footer_size = 1
root_file = []


def hash_cal(content):
    hash_256 = hashlib.sha256()
    hash_256.update(content)
    hash_value = hash_256.hexdigest()
    hash_int = int(hash_value, 16)
    return hash_int


def chunking(file_path, main_d=6, minor_d=3, r=2):
    sat = [0]
    hasher = {}
    all_size = os.path.getsize(file_path)
    # 判断文件
    with open(file_path, 'rb') as file:
        # 满足最小块尺寸
        if all_size <= min_chunk_size:
            return None
        # 从最小块尺寸开始读取
        start = min_chunk_size - chunk_size
        file.seek(start)
        content = file.read(chunk_size)
        judge1 = True  # 新块判断
        judge2 = False  # 旧块判断
        point1 = sat[-1]
        i = 0
        while True:
            if judge1:
                # 进入新块
                content = file.read(chunk_size)
                judge1 = False
            else:
                # 进入旧块，每次读取相应补偿的字节数
                byte = file.read(footer_size)
                content = content[footer_size:] + byte
            # 计算hash值
            hash_int = hash_cal(content)
            # 判断断点*
            if hash_int % main_d == 0:
                sat.append(start+chunk_size-1)

                point2 = sat[-1]
                file.seek(point2)
                content = file.read(point2-point1)
                rel_hash = hash_cal(content)
                hasher[i] = rel_hash
                i += 1

                start += min_chunk_size
                judge1 = True
                file.seek(start)
            else:
                start += footer_size
                file.seek(start)
            # 如果到达最大块尺寸，则切换除数并重新设置断点
            if start - sat[-1] >= max_chunk_size:
                main_d, minor_d = minor_d, main_d
                start = sat[-1] + 1 - chunk_size + min_chunk_size
                judge1 = True
                judge2 = True
                file.seek(start)
            # 如果都无法设置断点，那么将最大块作为断点*
            if judge2:
                sat.append(start+chunk_size-1)

                point2 = sat[-1]
                file.seek(point2)
                content = file.read(point2-point1)
                rel_hash = hash_cal(content)
                hasher[i] = rel_hash
                i += 1

                main_d, minor_d = minor_d, main_d
                start += min_chunk_size
                judge1 = True
                judge2 = False
                file.seek(start)
            # 最后的块处理
            if all_size-start < min_chunk_size:
                break
        return sat, hasher


def remove(file_path, sat_new):
    i = 0
    with open(file_path, 'rb') as source_file:
        dir_path = os.path.dirname(file_path)
        for sat in range(len(sat_new)-1, 0, 2):
            source_file.seek(sat_new[sat])
            data = source_file.read(sat_new[sat+1]-sat_new[sat])
            with open(os.path.join(dir_path, "delicate" + str(i)), 'ab') as target_file:
                target_file.write(data)
    os.remove(file_path)


def delicate_chunk(file_path1, file_path2):
    adjust = True
    sat = []
    sat_new = []
    sat1, hasher1 = chunking(file_path1)
    sat2, hasher2 = chunking(file_path2)
    print(type(hasher2))
    print(hasher2)

    if hasher1 is None or hasher2 is None:
        return None
    else:
        for i, value_i in hasher2.items():
            adjust = True
            for j, value_j in hasher1.items():
                if value_i == value_j:
                    sat.append(" "+str(sat1[j]))
                    adjust = False
                    break
            if adjust:
                sat.append(" n"+str(sat2[i]))
                sat_new.append(sat2[i])
                sat_new.append(sat2[i+1])
    remove(file_path2, sat_new)
    return sat


def main():
    file_path1 = input("请输入文件路径：")
    file_path2 = input("请输入文件路径：")
    result = delicate_chunk(file_path1, file_path2)
    if result is not None:
        for i in range(len(result)):
            print(result[i], end=" ")


if __name__ == '__main__':
    main()

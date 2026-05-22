import json
import mysql.connector
from typing import List, Any
import mysql.connector
import os
from typing import Dict, Optional
import hashlib
from pathlib import Path


# 原文件哈希
class FileHashTree:
    """
    管理 hash_data 表的工具类，提供数据添加和查询功能
    """

    def __init__(self, con: mysql.connector.connect, cursor):
        """初始化数据库连接"""
        self.conn = con
        self.cursor = cursor

    def add(self, data_hash, data_list: List[Any]):
        """
        添加数据列表，返回该数据列表的哈希值

        Args:
            data_list: 要存储的数据列表

        Returns:
            数据列表计算得到的SHA-256哈希值
            :param data_list:
            :param data_hash:
        """
        # 将列表转换为JSON字符串并编码为字节
        data_bytes = json.dumps(data_list, sort_keys=True).encode('utf-8')

        # 插入或更新数据
        insert_sql = """
        INSERT INTO file_hash_tree (data_hash, data_content)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE data_content = VALUES(data_content)
        """
        self.cursor.execute(insert_sql, (data_hash, data_bytes))
        self.conn.commit()

    def get(self, data_hash: str) -> Optional[List[Any]]:
        """
        通过哈希值查询数据内容

        Args:
            data_hash: 数据的SHA-256哈希值

        Returns:
            原始数据列表，如果未找到则返回None
        """
        select_sql = "SELECT data_content FROM file_hash_tree WHERE data_hash = %s"
        self.cursor.execute(select_sql, (data_hash,))
        result = self.cursor.fetchone()

        if result:
            # 从BLOB数据中解析原始列表
            data_bytes = result['data_content']
            try:
                return json.loads(data_bytes.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                # 如果不是JSON格式，直接返回字节数据
                return data_bytes
        return None


# 文件的块哈希目录表
class HashTree:
    def __init__(self, con, cursor, storage_base_dir: str = "D:/try/path") -> None:
        """
        初始化元数据管理器
        参数:
        - db_config: 数据库连接配置
        - storage_base_dir: 物理存储基础目录
        """
        self.conn = con
        self.cursor = cursor
        self.storage_base_dir = storage_base_dir
        Path(storage_base_dir).mkdir(parents=True, exist_ok=True)

    def add_file(self, file_hash: str, file_extension: str, file_size: int = 0, file_name: Optional[str] = None) -> str:
        """
        添加文件元数据，直接传入哈希值和扩展名
        参数:
        - file_hash: 文件哈希值
        - file_extension: 文件扩展名
        - file_size: 文件大小(字节)
        - file_name: 文件名(可选)
        返回:
        - 数据库中的逻辑路径
        """
        # 构建存储路径组件
        dir1 = file_hash[0:2]
        dir2 = file_hash[2:4]
        dir_path = f"/{dir1}/{dir2}"
        shard = file_hash[-4:]
        file_name_body = file_hash[4:-4]

        # 数据库逻辑路径
        file_db_path = f"{dir_path}/[{shard}].{file_name_body}"

        # 物理存储路径  # ~/dir1/dir2/shard
        storage_subdir = os.path.join(dir1, dir2, shard)
        storage_dir = os.path.join(self.storage_base_dir, storage_subdir)
        os.makedirs(storage_dir, exist_ok=True)

        # 物理文件名  # {file_hash}{file_extension}
        original_file_name = file_name or f"{file_hash}{file_extension}"
        physical_file_name = f"{file_hash}{file_extension}"
        file_system_path = os.path.join(storage_dir, physical_file_name)

        # 确保目录存在
        self._ensure_directory_exists(f"/{dir1}")
        self._ensure_directory_exists(dir_path)

        # 插入元数据记录
        insert_file_sql = """
        INSERT INTO sha256_directories 
        (id, path, is_directory, name, parent_id, file_system_path, original_file_size)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        file_system_path = VALUES(file_system_path),
        original_file_size = VALUES(original_file_size)
        """

        self.cursor.execute(
            insert_file_sql,
            (file_hash, file_db_path, False, original_file_name, dir_path, file_system_path, file_size)
        )
        self.conn.commit()

        return file_db_path

    def get_file_metadata(self, file_hash: str) -> Optional[Dict]:
        """通过哈希值获取文件元数据"""
        # 前四位作为两层目录
        dir1 = file_hash[0:2]
        dir2 = file_hash[2:4]
        dir_path = f"/{dir1}/{dir2}"

        # 后四位作为哈希分片
        shard = file_hash[-4:]

        # 剩余哈希作为文件名主体
        file_name_body = file_hash[4:-4]

        # 构建优化后的路径
        file_path = f"{dir_path}/[{shard}].{file_name_body}"

        # 查询文件元数据
        self.cursor.execute(
            "SELECT id, path, name, file_system_path, original_file_size, created_at "
            "FROM sha256_directories WHERE path = %s",
            (file_path,)
        )

        return self.cursor.fetchone()

    def _ensure_directory_exists(self, dir_path: str) -> None:
        """处理某目录级所有信息"""
        # 检查目录是否存在
        self.cursor.execute(
            "SELECT 1 FROM sha256_directories WHERE path = %s",
            (dir_path,)
        )

        if not self.cursor.fetchone():
            # 解析目录路径
            parts = dir_path.strip('/').split('/')
            dir_name = parts[-1]

            # 获取父目录路径
            parent_path = None
            if len(parts) > 1:
                parent_path = '/' + '/'.join(parts[:-1])

            # 查询父目录ID
            parent_id = None
            if parent_path:
                self.cursor.execute(
                    "SELECT id FROM sha256_directories WHERE path = %s",
                    (parent_path,)
                )
                parent_result = self.cursor.fetchone()
                if parent_result:
                    parent_id = parent_result[0]

            # 插入目录记录
            insert_dir_sql = """
            INSERT INTO sha256_directories (id, path, is_directory, name, parent_id)
            VALUES (%s, %s, %s, %s, %s)
            """

            dir_id = hashlib.sha256(dir_path.encode()).hexdigest()

            self.cursor.execute(
                insert_dir_sql,
                (dir_id, dir_path, True, dir_name, parent_id)
            )
            self.conn.commit()

    def delete_file(self, file_hash: str) -> bool:
        """通过哈希值删除文件元数据"""
        metadata = self.get_file_metadata(file_hash)
        if not metadata:
            return False

        file_path = metadata["path"]

        # 删除元数据
        self.cursor.execute(
            "DELETE FROM sha256_directories WHERE path = %s",
            (file_path,)
        )

        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_file_system_path(self, file_hash: str) -> Optional[str]:
        """通过哈希值获取文件物理存储路径"""
        metadata = self.get_file_metadata(file_hash)
        if not metadata:
            return None
        return metadata["file_system_path"]

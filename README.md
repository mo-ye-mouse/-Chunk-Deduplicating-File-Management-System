# 分块去重的远端文件管理系统

基于内容定义分块（CDC）和哈希树的文件去重与远端文件管理系统。

## 文件结构

```
├── team_filesystem.py    # FileManager：远端文件系统核心（dir/cd/copy/move/del 等）
├── team_fs_server.py     # TCP Socket 服务端（多线程处理客户端请求）
├── team_fs_client.py     # TCP Socket 客户端
├── team_pubulicate.py    # TTTDS 分块去重引擎 + 文件发布逻辑
└── file_hash_tree.py     # 文件哈希树工具（基于 MySQL 存储 SHA-256 哈希）
```

## 功能特性

- **内容定义分块 (CDC)**：基于滚动哈希的内容感知分块，支持可变块大小（512B ~ 8KB）
- **块级去重**：相同内容块只存储一次，节省存储空间
- **哈希树**：基于 SHA-256 的 Merkle 树，确保数据完整性
- **远端文件管理**：客户端-服务端架构，支持远程文件操作
- **MySQL 持久化**：哈希数据持久化存储

## 环境依赖

- Python 3.10+
- MySQL
- 依赖库：`mysql-connector-python`

## 快速开始

### 1. 启动服务端

```bash
python team_fs_server.py
```

### 2. 启动客户端

```bash
python team_fs_client.py
```

客户端支持的命令：`dir` / `cd` / `mkdir` / `type` / `rename` / `del` / `rmdir` / `copy` / `move` / `cls` / `help`

## 技术要点

### CDC 分块算法（TTTDS）

- 使用滚动哈希以滑动窗口方式扫描文件
- 主除数 `main_d=16` + 辅除数 `minor_d=8` 双除数机制
- 哈希值满足 `hash % d == R` 时标记分块点
- 块大小范围：512B ~ 8KB（可配置）

### 去重流程

1. 文件经 CDC 分块
2. 逐块计算 SHA-256 哈希
3. 在哈希树 / MySQL 中查找是否已存在相同哈希块
4. 仅存储新块，重复块引用已有数据

## License

MIT License

# 分块去重的远端文件管理系统

基于内容定义分块（CDC）和哈希树的文件去重与远端文件管理系统。

## 项目结构

```
├── 消解算法.py               # 命题逻辑公式消解算法（离散数学）
├── moye/                     # 本地文件系统与分块去重模块
│   ├── moye_filesystem.py    # 本地文件系统 CLI（支持 dir/cd/mkdir/rm/delicate）
│   ├── moye_depublicate.py   # CDC 分块引擎（滚动哈希 + 可变大小分块）
│   └── mysql/                # MySQL Docker 部署
│       └── docker-compose.yml
└── team_remote_fs/           # 远端文件管理子系统
    ├── team_filesystem.py    # FileManager：远端文件系统核心（dir/cd/copy/move/del 等）
    ├── team_fs_server.py     # TCP Socket 服务端（多线程处理客户端请求）
    ├── team_fs_client.py     # TCP Socket 客户端
    ├── team_pubulicate.py    # TTTDS 分块去重引擎 + 文件发布逻辑
    └── file_hash_tree.py     # 文件哈希树工具（基于 MySQL 存储 SHA-256 哈希）
```

## 功能特性

- **内容定义分块 (CDC)**：基于滚动哈希的内容感知分块，支持可变块大小
- **块级去重**：相同内容块只存储一次，节省存储空间
- **哈希树**：基于 SHA-256 的 Merkle 树，确保数据完整性
- **远端文件管理**：客户端-服务端架构，支持远程文件操作
- **MySQL 持久化**：哈希数据持久化存储

## 环境依赖

- Python 3.10+
- MySQL 9.3（Docker）
- 依赖库：`mysql-connector-python`

## 快速开始

### 1. 启动 MySQL

```bash
cd moye/mysql
docker-compose up -d
```

### 2. 启动远端文件管理服务端

```bash
cd team_remote_fs
python team_fs_server.py
```

### 3. 启动客户端连接

```bash
cd team_remote_fs
python team_fs_client.py
```

### 4. 本地文件系统

```bash
cd moye
python moye_filesystem.py
```

## 技术要点

### CDC 分块算法

- 使用滚动哈希（Rabin-Karp 变体）以滑动窗口方式扫描文件
- 主除数 `main_d=16` + 辅除数 `minor_d=8` 双除数机制
- 块大小范围：512B ~ 8KB（可配置）
- 哈希值满足 `hash % d == R` 时标记分块点

### 去重流程

1. 文件经 CDC 分块
2. 逐块计算 SHA-256 哈希
3. 在哈希树 / MySQL 中查找是否已存在相同哈希块
4. 仅存储新块，重复块引用已有数据

## License

MIT License

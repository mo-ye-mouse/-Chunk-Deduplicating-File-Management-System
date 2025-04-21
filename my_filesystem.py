class File:
    def __init__(self, name, content=""):
        self.name = name
        self.content = content

    def read(self):
        return self.content

    def write(self, new_content):
        self.content = new_content


class Directory:
    def __init__(self, name):
        self.name = name
        self.files = {}
        self.directories = {}

    def create_file(self, file_name):
        if file_name in self.files:
            print(f"文件 {file_name} 已存在。")
        else:
            self.files[file_name] = File(file_name)
            print(f"文件 {file_name} 创建成功。")

    def create_directory(self, dir_name):
        if dir_name in self.directories:
            print(f"目录 {dir_name} 已存在。")
        else:
            self.directories[dir_name] = Directory(dir_name)
            print(f"目录 {dir_name} 创建成功。")

    def list_files(self):
        print("文件列表：")
        for file_name in self.files:
            print(file_name)

    def list_directories(self):
        print("目录列表：")
        for dir_name in self.directories:
            print(dir_name)

    def get_file(self, file_name):
        return self.files.get(file_name)

    def get_directory(self, dir_name):
        return self.directories.get(dir_name)


# 主程序示例
if __name__ == "__main__":
    root = Directory("/")
    root.create_directory("documents")
    root.create_file("test.txt")

    doc_dir = root.get_directory("documents")
    doc_dir.create_file("report.txt")

    root.list_directories()
    root.list_files()

    test_file = root.get_file("test.txt")
    test_file.write("这是测试文件的内容。")
    print(test_file.read())
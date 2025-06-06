import os
import shutil
import time
from os import remove


class FileManager:
    def __init__(self):
        self.current_dir = os.getcwd()  # 初始目录为当前工作目录
        self.supported_commands = {
            'dir': self.dir,
            'cd': self.cd,
            'mkdir': self.mkdir,
            'type': self.type,
            'rename': self.rename,
            'del': self.delete_item,
            'rmdir': self.delete_directory,
            'copy': self.copy,
            'move': self.move,
            'cls': self.clear,
            'delicate': self.delicate
        }

    def menu(self):
        """显示操作菜单"""
        print(f"{self.current_dir}> ")

    def dir(self, *args):
        """dir：列出当前目录下的所有文件和文件夹, 并显示文件大小和修改时间"""

    def cd(self, *args):
        """cd：切换到某目录，可以处理相对路径和绝对路径"""

    def mkdir(self, *args):
        """mkdir：创建文件夹"""

    def type(self, *args):
        """处理type文件名命令"""

    def rename(self, *args):
        """处理rename命令"""
        if len(args) != 2:
            print("格式错误，用法: rename 旧名 新名")
            return
        old_name,new_name=args
        old_path=os.path.join(self.current_dir,old_name)
        new_path=os.path.join(self.current_dir,new_name)
        if not os.path.exists(old_path):
            print(f"错误：{old_name}不存在")
            return
        try:
            os.rename(old_path,new_path)
            print("重命名成功")
        except Exception as e:
            print(f"重命名失败：{e}")

    def delete_item(self, *args):
        """处理del/rm命令"""
        if len(args) != 1:
            print("格式错误，用法：del 单个文件的文件名")
            return
        file_name=args[0]
        file_path=os.path.join(self.current_dir,file_name)
        if not os.path.isfile(file_path):
            print(f"错误：{file_path}不是单个文件或不存在")
            return
        try:
            os.remove(file_path)
            print("成功删除该文件")
        except Exception as e:
            print(f"删除文件失败：{e}")

    def delete_directory(self, *args):
        """处理rmdir/rd命令"""

    def copy(self, *args):
        """处理copy命令"""

    def move(self, *args):
        """处理move命令"""
        if len(args) < 2:
            print("错误：使用格式 'move 源文件/文件夹 目标位置'")
            return

        source_name, destination_name = args[0], args[1]
        source_path = os.path.join(self.current_dir, source_name)
        destination_path = os.path.join(self.current_dir, destination_name)

        try:
            shutil.move(source_path, destination_path)
            print(f"成功移动 {source_name} 到 {destination_name}")
        except FileNotFoundError:
            print("错误：指定的源文件/文件夹不存在。")
        except PermissionError:
            print("错误：没有权限移动。")
        except Exception as e:
            print(f"错误：{e}")

    def clear(self, *args):
        """清屏命令"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def delicate(self, *args):
        """处理delicate命令"""

    def parse_command(self, command):
        """解析用户输入的命令"""
        parts = command.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()  # 转换为小写字母
        args = parts[1:]

        if cmd in self.supported_commands:
            self.supported_commands[cmd](*args)
        return True

    def run(self):
        """运行文件管理系统"""
        while True:
            self.menu()
            command = input(f"\n{self.current_dir}> ")
            if not self.parse_command(command):
                break


if __name__ == "__main__":
    manager = FileManager()
    manager.run()

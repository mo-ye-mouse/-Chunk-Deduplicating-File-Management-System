import os
import shutil
import time


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
            'delicate':self.delicate
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

    def delete_item(self, *args):
        """处理del/rm命令"""

    def delete_directory(self, *args):
        """处理rmdir/rd命令"""

    def copy(self, *args):
        """处理copy命令"""

    def move(self, *args):
        """处理move命令"""

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

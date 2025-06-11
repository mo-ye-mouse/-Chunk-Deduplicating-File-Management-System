import os
import shutil
import time
import team_pubulicate


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
            'help': self.help,
            'delicate': self.delicate
        }

    @staticmethod
    def help():
        print("directory commands:")
        print("*dir [directory] *cd [directory] *mkdir [directory] *type [file] *rename [old_name] [new_name]")
        print("*del [file] *rmdir [directory] *copy [src] [dst] *move [src] [dst] *cls *delicate: 此命令尚未实现")

    def dir(self, *args):  # yes
        """dir：列出目录下的所有文件和文件夹, 并显示文件大小和修改时间"""
        # 获取当前工作目录
        if len(args) > 1:
            print("Error: usage: dir [directory]")
            return
        try:
            os.chdir(args[0] if args else self.current_dir)
        except Exception as e:
            print(f"Error: {e}")
            return
        dirs = os.getcwd()
        if not os.path.isdir(dirs):
            print(f"Error: {dirs} is not a directory")
            return
        for item in os.listdir(dirs):
            item_path = os.path.join(dirs, item)  # 拼接完整路径
            size = os.path.getsize(item_path)  # 获取大小
            modify_time = time.ctime(os.path.getmtime(item_path))
            if os.path.isfile(item_path):
                file_type = "文件"
            else:
                file_type = "文件夹"
            print(f"{item:<30}{file_type:<10}{size:>10}字节  {modify_time}")
        os.chdir(self.current_dir)

    def cd(self, *args):  # yes
        """cd：切换到某目录，可以处理相对路径和绝对路径，但是没有过于严格"""
        if len(args) > 1:
            print("Error: usage: cd [directory]")
            return
        if not args:
            # 切换到用户主目录
            os.chdir(os.path.expanduser("~"))
            self.current_dir = os.getcwd()
            return

        # 获取第一个参数作为路径
        path = args[0]
        try:
            os.chdir(path)
            self.current_dir = os.getcwd()
        except Exception as e:  # 处理所有异常
            print(f"Error：{e}")

    def rename(self, *args):  # yes
        """处理rename命令"""
        if len(args) != 2:
            print("格式错误，用法: rename 旧名 新名")
            return
        old_name, new_name = args
        old_path = os.path.join(self.current_dir, old_name)
        new_path = os.path.join(self.current_dir, new_name)
        if not os.path.exists(old_path):
            print(f"错误：{old_name}不存在")
            return
        try:
            os.rename(old_path, new_path)
            print("重命名成功")
        except Exception as e:
            print(f"重命名失败：{e}")

    def delete_item(self, *args):  # yes
        """处理del/rm命令"""
        if len(args) != 1:
            print("格式错误，用法：del 单个文件的文件名")
            return
        file_name = args[0]
        file_path = os.path.join(self.current_dir, file_name)
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
        if not args:
            return print("用法: rmdir 目录名")
        try:
            path = os.path.join(self.current_dir, args[0])
            os.rmdir(path)
            print(f"已删除目录: {args[0]}")
        except Exception as e:
            print(f"错误:{e}")

    def copy(self, *args):  # yes
        """处理copy命令"""
        if len(args) < 2:
            return print("用法: copy 源路径 目标路径")
        try:
            src = os.path.join(self.current_dir, args[0])
            dst = os.path.join(self.current_dir, args[1])
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst if not os.path.isdir(dst) else os.path.join(dst, os.path.basename(src)))
            print(f"复制完成: {args[0]} → {args[1]}")
        except Exception as e:
            print(f"复制失败: {str(e)}")

    def move(self, *args):
        """处理move命令"""
        if len(args) < 2:
            print("error: usage：move 源文件/文件夹 目标位置")
            return

        source_name, destination_name = args[0], args[1]
        source_path = os.path.join(self.current_dir, source_name)
        destination_path = os.path.join(self.current_dir, destination_name)

        try:
            shutil.move(source_path, destination_path)
            print(f"success: move {source_name} to {destination_name}")
        except Exception as e:
            print(f"error：{e}")

    @staticmethod
    def mkdir(*args):  # yes
        """mkdir：创建文件夹"""
        if len(args) != 1:
            print("error: usage: mkdir [directory]")
            return
        folder_name = args[0]
        try:
            # 使用os.makedirs创建文件夹，exist_ok=True表示如果文件存在则不报错
            os.makedirs(folder_name, exist_ok=True)
            print(f"Directory '{folder_name}' created successfully")
        except Exception as e:
            print(f"mkdir: error creating direction: {e}")

    @staticmethod
    def type(*args):  # 处理不了部分txt，比如日文
        """处理type文件名命令"""
        if not args:
            print("type: missing argument")
            return
        file_name = args[0]
        try:
            # 检查文件是否存在
            if not os.path.isfile(file_name):
                print(f"type: file'{file_name} not found")
                return
            # 读取文件内容并打印
            with open(file_name, 'r') as file:
                content = file.read()
                print(content)
        except Exception as e:
            print(f"type: error reading file: {e}")

    @staticmethod
    def clear():
        """清屏命令"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def delicate(self, *args):
        """处理delicate命令"""
        if len(args) != 2:
            print("error: usage: delicate 源文件 目标文件")
            return
        source_name, destination_name = args[0], args[1]
        try:
            source_path = os.path.join(self.current_dir, source_name)
            destination_path = os.path.join(self.current_dir, destination_name)
        except Exception as e:
            print(f"error: {e}")
            return
        team_pubulicate.delicate(source_path, destination_path)
        print(f"success: delicate {source_name} to {destination_name}")

    def parse_command(self, command):
        """解析用户输入的命令"""
        parts = command.strip().split()
        if not parts:
            return

        cmd = parts[0].lower()  # 转换为小写字母
        args = parts[1:]

        if cmd in self.supported_commands:
            self.supported_commands[cmd](*args)
        else:
            print(f"Error: command '{cmd}' not found")
        return True

    def run(self):
        """运行文件管理系统"""
        while True:
            command = input(f"\n{self.current_dir}> ")
            if not self.parse_command(command):
                break


if __name__ == "__main__":
    manager = FileManager()
    manager.run()

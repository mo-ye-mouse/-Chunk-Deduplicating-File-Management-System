import os
import shutil
import cmd

class FileSystemShell(cmd.Cmd):
    intro = '欢迎使用本地文件系统交互工具。输入 help 或 ? 列出命令。\n'
    prompt = 'FileSystem> '

    def do_dir(self, arg):
        """列出目录内容。可以指定目录路径，默认为当前目录。
        用法: dir [目录路径]
        """
        if arg.strip():
            directory = arg.strip()
        else:
            directory = os.getcwd()
        self._list_directory(directory)

    def do_type(self, arg):
        """显示文件内容。
        用法: type <文件路径>
        """
        file_path = arg.strip()
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    print(content)
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"Error: 文件 '{file_path}' 不存在。")

    def do_echo(self, arg):
        """将内容写入文件。
        用法: echo "内容" > <文件路径>
        """
        if '>' in arg:
            parts = arg.split('>', 1)
            if len(parts) == 2:
                content = parts[0].strip().strip('"')
                file_path = parts[1].strip()
                self._write_file(file_path, content)
            else:
                print("用法: echo \"内容\" > <文件路径>")
        else:
            print("用法: echo \"内容\" > <文件路径>")

    def do_copy(self, arg):
        """复制文件。
        用法: copy <源文件路径> <目标文件路径>
        """
        args = arg.split()
        if len(args) == 2:
            src, dst = args
            self._copy_file(src, dst)
        else:
            print("用法: copy <源文件路径> <目标文件路径>")

    def do_del(self, arg):
        """删除文件。
        用法: del <文件路径>
        """
        file_path = arg.strip()
        self._delete_file(file_path)

    def do_mkdir(self, arg):
        """创建目录。
        用法: mkdir <目录路径>
        """
        directory = arg.strip()
        self._create_directory(directory)

    def do_cd(self, arg):
        """切换当前目录。
        用法: cd <目录路径>
        """
        directory = arg.strip()
        if directory:
            try:
                os.chdir(directory)
                print(f"当前目录已切换到: {os.getcwd()}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"当前目录: {os.getcwd()}")

    def do_exit(self, arg):
        """退出程序。
        用法: exit
        """
        print("退出程序。")
        return True

    def do_EOF(self, arg):
        """处理 EOF（Ctrl+D）以退出程序"""
        print("\n退出程序。")
        return True

    def help_dir(self):
        print("列出目录内容。可以指定目录路径，默认为当前目录。")
        print("用法: dir [目录路径]")

    def help_type(self):
        print("显示文件内容。")
        print("用法: type <文件路径>")

    def help_echo(self):
        print("将内容写入文件。")
        print("用法: echo \"内容\" > <文件路径>")

    def help_copy(self):
        print("复制文件。")
        print("用法: copy <源文件路径> <目标文件路径>")

    def help_del(self):
        print("删除文件。")
        print("用法: del <文件路径>")

    def help_mkdir(self):
        print("创建目录。")
        print("用法: mkdir <目录路径>")

    def help_cd(self):
        print("切换当前目录。")
        print("用法: cd <目录路径>")

    def help_exit(self):
        print("退出程序。")
        print("用法: exit")

    def _list_directory(self, directory):
        try:
            files = os.listdir(directory)
            for file in files:
                file_path = os.path.join(directory, file)
                if os.path.isdir(file_path):
                    print(f"<DIR> {file}")
                else:
                    file_size = os.path.getsize(file_path)
                    print(f"{file:<20} {file_size:>10} bytes")
        except Exception as e:
            print(f"Error: {e}")

    def _write_file(self, file_path, content):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"文件 '{file_path}' 写入成功。")
        except Exception as e:
            print(f"Error: {e}")

    def _copy_file(self, src, dst):
        try:
            shutil.copy2(src, dst)
            print(f"文件已从 '{src}' 复制到 '{dst}'。")
        except Exception as e:
            print(f"Error: {e}")

    def _delete_file(self, file_path):
        try:
            os.remove(file_path)
            print(f"文件 '{file_path}' 删除成功。")
        except Exception as e:
            print(f"Error: {e}")

    def _create_directory(self, directory):
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"目录 '{directory}' 创建成功。")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    fs_shell = FileSystemShell()
    fs_shell.cmdloop()
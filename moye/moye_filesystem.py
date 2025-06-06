import os
import shutil
from moye import moye_depublicate


class FileSystem:
    def __init__(self):
        self.root = os.path.abspath(os.sep)
        self.current = self.root
        os.chdir(self.current)

    def handel_path(self, path, adjust=True):
        path_lists = [p for p in path.split("\\") if p]
        if path[0] == "\\" or path[0] == ".":
            try:
                if path_lists[0] == ".":
                    current_parent = os.path.dirname(self.current)
                    if path_lists[1] == ".":
                        current_parent = os.path.dirname(current_parent)
                    os.chdir(current_parent)
                    path_lists = path_lists[1:]
            except FileNotFoundError:
                print("No such file or directory")
                os.chdir(self.current)
                return False
        else:
            return path
        if adjust:
            lengths = len(path_lists) - 1
        else:
            lengths = len(path_lists)
        for i in range(lengths):
            try:
                os.chdir(path_lists[i])
            except FileNotFoundError:
                os.chdir(self.current)
                print("No such file or directory")
                return False
        self.current = os.getcwd()
        if adjust:
            return path_lists[-1]
        return True

    def ls(self, commend=""):
        if commend not in ["/a:d", "/a:-d", ""]:
            print("Invalid option")
            return
        os.chdir(self.current)
        item = os.listdir()
        for i in item:
            if commend == "/a:d" and os.path.isfile(i):
                print(f"{i}")
            elif commend == "/a:-d" and os.path.isdir(i):
                print(f"{i}")
            else:
                print(f"{i}")

    def cd(self, path):
        if path[0] not in [".", "\\", self.root[0]]:
            print("Invalid option")
            return
        get = self.handel_path(path, False)

    def mkdir(self, path):
        old_path = os.getcwd()
        if path[0] not in [".", "\\", self.root[0]]:
            print("Invalid option")
            return
        get = self.handel_path(path)
        if not get:
            return
        try:
            os.mkdir(get)
            print(f"Directory {get} created")
        except FileExistsError:
            print("File or directory already exists")
        os.chdir(old_path)

    def rm(self, path):
        old_path = os.getcwd()
        parts = [p for p in path.split(" ")]
        if path[0] not in [".", "\\", self.root[0]]:
            if len(parts) == 3:
                if not parts[0] == "/s" or not parts[1] == "/q" or not parts[2][0] in [".", "\\", self.root[0]]:
                    print("Invalid option")
                    return
                else:
                    get = self.handel_path(parts[2], False)
                    if not get:
                        return
                    else:
                        shutil.rmtree(self.current)
                        print(f"Directory {get} deleted")
                        os.chdir(self.root)
                        self.current = os.getcwd()
                        return
            else:
                print("Invalid option")
        elif len(parts) == 1 and path[0] in [".", "\\", self.root[0]]:
            get = self.handel_path(path)
            if not get:
                return
            try:
                os.remove(self.current + "\\" + get)
            except FileNotFoundError:
                print("No such file or directory")
                os.chdir(old_path)
                self.current = os.getcwd()

    def do_EOF(self, arg):
        return True


def main():
    fs = FileSystem()
    while True:
        # 对于输入的命令进行处理
        try:
            get = input(f"{fs.current}$ ").strip().split(" ")
        except EOFError:
            fs.do_EOF(None)
            break
        # 功能实现
        if get[0] == "exit":
            break
        if get[0] == "dir":
            if len(get) > 1:
                fs.ls(get[1])
            else:
                fs.ls()
            continue
        elif get[0] == "cd":
            if len(get) == 1:
                print("No directory specified")
                continue
            else:
                fs.cd(get[1])
                continue
        elif get[0] == "mkdir":
            if len(get) == 1:
                print("No directory specified")
                continue
            else:
                fs.mkdir(get[1])
                continue
        elif get[0] == "rm":
            if len(get) == 2:
                fs.rm(get[1])
                continue
            elif len(get) == 4:
                fs.rm(get[1]+" "+get[2]+" "+get[3])
                continue
            else:
                print("Invalid option")
                continue
        # 去重功能
        elif get[0] == "delicate":
            if len(get) == 3:
                delicate = moye_depublicate.Delicate()
                delicate.delicate(get[1], get[2])
                print("Depublicate complete")
        else:
            print("Invalid command")


if __name__ == "__main__":
    main()

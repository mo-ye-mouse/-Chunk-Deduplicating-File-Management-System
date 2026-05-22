import os
import shutil
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from moye import moye_depublicate


class FileSystem:
    def __init__(self):
        self.root = os.path.abspath(os.sep)
        self.current = self.root
        self.menu = {
            "dir": self.ls,
            "cd": self.cd,
            "mkdir": self.mkdir,
            "rm": self.rm,
            "delicate": self.delicate
        }
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
            return "Invalid option"
        os.chdir(self.current)
        item = os.listdir()
        back = []
        for i in item:
            if commend == "/a:d" and os.path.isfile(i):
                back.append(i)
            elif commend == "/a:-d" and os.path.isdir(i):
                back.append(i)
            else:
                back.append(i)
        return back

    def cd(self, path):
        if path[0] not in [".", "\\", self.root[0]]:
            return "Invalid option"
        get = self.handel_path(path, False)
        if not get:
            return "Invalid option"
        return "Directory changed to " + str(get)

    def mkdir(self, path):
        old_path = os.getcwd()
        if path[0] not in [".", "\\", self.root[0]]:
            return "Invalid option"
        get = self.handel_path(path)
        if not get:
            return "Invalid option"
        os.chdir(old_path)
        try:
            os.mkdir(get)
            return "Directory " + str(get) + " created"
        except FileExistsError:
            return "File or directory already exists"

    def rm(self, path):
        old_path = os.getcwd()
        parts = [p for p in path.split(" ")]
        if path[0] not in [".", "\\", self.root[0]]:
            if len(parts) == 3:
                if not parts[0] == "/s" or not parts[1] == "/q" or not parts[2][0] in [".", "\\", self.root[0]]:
                    return "Invalid option"
                else:
                    get = self.handel_path(parts[2], False)
                    if not get:
                        return "Invalid option"
                    else:
                        shutil.rmtree(self.current)
                        print(f"Directory {get} deleted")
                        os.chdir(self.root)
                        self.current = os.getcwd()
                        return "Directory " + str(get) + " deleted"
            else:
                return "Invalid option"
        elif len(parts) == 1 and path[0] in [".", "\\", self.root[0]]:
            get = self.handel_path(path)
            if not get:
                return "Invalid option"
            try:
                os.remove(self.current + "\\" + get)
                return "Directory " + str(get) + " deleted"
            except FileNotFoundError:
                os.chdir(old_path)
                self.current = os.getcwd()
                return "No such file or directory"

    def delicate(self, path1, path2):
        delicate = moye_depublicate.Delicate()
        delicate.upload(path1, path2)

    def tackle(self, message):
        if message[0] in self.menu:
            info = self.menu[message[0]](message[1:])
        else:
            info = "Invalid command"
        return info


def handle_conn(addr, conn, fs):
    while True:
        try:
            get = conn.recv(1024).decode("utf-8")
            print(f"{addr}: {get}")
            get = get.strip().split(" ")
            if get[0] == "exit":
                break
            info = fs.tackle(get)
            conn.send(info.encode("utf-8"))
        except ConnectionResetError:
            break
    conn.close()
    print(f"{addr} disconnected")


def main():
    fs = FileSystem()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 8080))
    s.listen(5)
    print("Waiting for connection...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        features = []
        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            feature = executor.submit(handle_conn, addr, conn, fs)
            features.append(feature)


if __name__ == "__main__":
    main()

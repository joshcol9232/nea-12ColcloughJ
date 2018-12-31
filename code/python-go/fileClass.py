from os import path as osPath
from os import listdir
from subprocess import Popen, PIPE

class File:

    def __init__(self, screen, hexPath, hexName, fileSep, extension=None, isDir=False, name=None, path=None):
        self.outerScreen = screen
        self._totalSize = 0
        self.hexPath, self.hexName, self.isDir, self.fileSep, self.extension = hexPath, hexName, isDir, fileSep, extension
        self.thumbDir = ""
        self.checkSum = None
        self.rawSize = self.__getFileSize()
        self.size = self.outerScreen.getGoodUnit(self.rawSize)
        self.isDir = isDir
        if name == None:
            self.name = self.outerScreen.decString(self.hexName)
        else:
            self.name = name
        if path == None:
            self.path = self.__getNormDir(self.hexPath)
        else:
            self.path = path
        if extension == None:
            extension = self.path.split(".")
            self.extension = extension[-1].lower()
        else:
            extension = extension.lower()

        if self.isDir:
            self.hexPath += self.fileSep
            self.path += self.fileSep

        self.relPath = self.hexPath.replace(self.outerScreen.path, "")   # Encrypted path relative to root folder of Vault

    def __getNormDir(self, hexDir):          # Private functions as they are usually only needed once and should only be callable from within the class
        dir = self.fileSep.join(self.outerScreen.decListString(hexDir.replace(self.outerScreen.path, "").split(self.fileSep)[:-1]))+self.name
        if self.isDir:
            dir += self.fileSep
        return dir

    def __getFileSize(self, recurse=True):
        if self.isDir:
            if recurse:
                self._totalSize = 0
                self.__recursiveSize(self.hexPath)
                size = self._totalSize
                return size
            else:
                return " -"
        else:
            try:
                size = osPath.getsize(self.hexPath) # Imported from os module
                return size
            except Exception as e:
                print(e, "couldn't get size.")
                return " -"

    def __recursiveSize(self, f):  #Get size of folders.
        fs = listdir(f)
        for item in fs:
            if osPath.isdir(f+self.fileSep+item):
                try:
                    self.__recursiveSize(f+self.fileSep+item)
                except OSError:
                    pass
            else:
                try:
                    self._totalSize += osPath.getsize(f+self.fileSep+item)
                except PermissionError: #Thrown when the file is owned by another user/administrator.
                    pass

    def decryptRelPath(self):       # Gets relative path from root of Vault in human form
        splitPath = self.relPath.split(self.fileSep)
        return self.fileSep.join(self.outerScreen.decListString(splitPath))

    def getCheckSum(self, new=True):
        if self.checkSum == None or new:
            if self.fileSep == "\\":
                goproc = Popen(self.outerScreen.startDir+"BLAKEWin.exe", stdin=PIPE, stdout=PIPE)
            elif self.fileSep == "/":
                goproc = Popen(self.outerScreen.startDir+"BLAKE/BLAKE", stdin=PIPE, stdout=PIPE)

            out, err = goproc.communicate((self.hexPath).encode())
            if err != None:
                raise ValueError(err)

            self.checkSum = out.decode()

        return self.checkSum

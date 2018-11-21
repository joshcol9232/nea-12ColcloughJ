from os.path import getsize
import aesFName

class File:

    def __init__(self, screen, hexPath, hexName, fileSep, isDir=False, name=None, path=None):
        self.outerScreen = screen
        self.hexPath, self.hexName, self.isDir, self.fileSep = hexPath, hexName, isDir, fileSep
        self.rawSize = self._getFileSize()
        self.size = self.outerScreen.getGoodUnit(self.rawSize)
        self.isDir = isDir
        self.path = path
        self.name = name
        if path == None:
            self.path = self._getNormDir(self.hexPath)
        if name == None:
            self.name = aesFName.decryptFileName(self.outerScreen.key, self.hexName)
        if self.isDir:
            self.hexPath += self.fileSep
            self.path += self.fileSep


    def _getNormDir(self, hexDir):          # Private functions as they are usually only needed once and should only be callable from within the class
        hexDir = (hexDir.replace(self.outerScreen.path, "")).split(self.fileSep)
        for i in range(len(hexDir)):
            hexDir[i] = aesFName.decryptFileName(self.outerScreen.key, hexDir[i])

        return self.fileSep.join(hexDir)

    def _getFileSize(self, recurse=True):
        if self.isDir:
            if recurse:
                self.outerScreen.totalSize = 0
                self.outerScreen.recursiveSize(self.hexPath)
                size = self.outerScreen.totalSize
                return size
            else:
                return " -"
        else:
            try:
                size = getsize(self.hexPath) # Imported from os module
                return size
            except Exception as e:
                print(e, "couldn't get size.")
                return " -"
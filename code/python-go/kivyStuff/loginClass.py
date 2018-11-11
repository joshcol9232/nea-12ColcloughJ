from os import listdir
from os.path import isdir as osIsDir
from subprocess import Popen, PIPE

from kivy.uix.screenmanager import Screen
from kivy.lang.builder import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label

import SHA

class LoginScreen(Screen):

    def __init__(self, fileSep, path, startDir, **kwargs):
        self.fileSep, self.path, self.startDir = fileSep, path, startDir  # Start dir is location of running program, path is path of vault
        super(Screen, self).__init__(**kwargs)
        self.key = ""

    def findFile(self, dir):    #For finding a file to decrypt first block and compare it with key given.
        fs = listdir(dir)
        for item in fs:
            if osIsDir(dir+item+"/"):
                if self.count == 0:
                    self.findFile(dir+item+"/")
                else:
                    return
            else:
                self.decryptTestFile = dir+item
                self.count += 1
                return

    def passToTerm(self, key, d):           #Makes a pipe to communicate with the AES written in go.
        if self.fileSep == "\\":
            progname = "AESWin"
        else:
            progname = "AES"
        goproc = Popen(self.startDir+progname, stdin=PIPE, stdout=PIPE)
        out, err = goproc.communicate(("test, "+d+", 0, ").encode()+key.encode())
        return out

    def getIfValidKey(self, inputKey):              #Gets the output of the AES key checker.
        if len(listdir(self.path)) > 1:
            self.decryptTestFile = ""
            self.count = 0
            self.findFile(self.path)
            diditwork = self.passToTerm(inputKey, self.decryptTestFile)
            if diditwork == b"-Valid-\n": #The go program prints "-Valid-\n" or "-Invalid-\n" once it is done checking the key.
                return True
            else:
                return False
        else:
            return True

    def checkKey(self, inputKey):   #Handles the UI while the key is checked, and passes key to functions to check it.
        try:
            int(inputKey)
        except:
            pop = Popup(title="Invalid", content=Label(text="Invalid key, valid key\ncontains no letters."), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4))
            pop.open()
            return "Login"
        else:
            if len(str(inputKey)) > 16:
                pop = Popup(title="Invalid", content=Label(text="Invalid key, longer than\n 16 characters."), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4))
                pop.open()
                return "Login"
            else:
                inputKeyTemp = []
                for i in range(len(inputKey)):
                    inputKeyTemp.append(int(inputKey[i]))
                inputKey = inputKeyTemp
                inputKey = SHA.getSHA128of16(inputKey)
                key = " ".join(str(i) for i in inputKey)
                valid = self.getIfValidKey(key)
                if valid:
                    self.ids.keyInput.text = "" #reset key input if valid
                    self.key = key
                    return "Main"
                else:
                    pop = Popup(title="Invalid", content=Label(text="Invalid key."), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4))
                    pop.open()
                    return "Login"

    def needToSetKey(self):             #For checking if the user needs to make a new key.
        if len(listdir(self.path)) == 0:
            return "Input New Key (Write this down if you have to)"
        else:
            return "Input Key"

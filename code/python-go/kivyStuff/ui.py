import os
import sys
import shutil
import threading
import fileinput
from functools import partial
from tempfile import gettempdir
from subprocess import Popen, PIPE
import time

from kivy.config import Config
Config.set("graphics", "resizable", False)
Config.set("graphics", "width", "1000")
Config.set("graphics", "height", "600")
Config.set("input", "mouse", "mouse,disable_multitouch")
Config.write()

from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.base import EventLoop
from kivy.lang import Builder

############Import SHA Module###########
import SHA

###########Import filename encryption###
import aesFName     #AES easier to use when written in python, but slower, which isn't much of an issue for file names hence why this part is python.

###########Import cython sorts##########
import sortsCy

#######Load OS Specific settings####
global fileSep #linux has different file separators to windows and different temp dir
global osTemp  #Different OS have different temp folder locations.
if sys.platform.startswith("win32"):
    fileSep = "\\"
else:          #windows bad
    fileSep = "/"
osTemp = gettempdir()+fileSep #From tempfile module

######Load config and define shared variables#####
global startDir
global useBT
global config
#global root #For use like root.x in kv file
useBT = False

##Check if config file is in /home/user/.config/FileMate/config
startDir = os.path.dirname(os.path.realpath(__file__))+fileSep
tempDir = startDir.split(fileSep)
del tempDir[len(tempDir)-2]
startDir = fileSep.join(tempDir)
for i in range(2):
    del tempDir[len(tempDir)-2]

tempDir = fileSep.join(tempDir)
tempDir += "assets"+fileSep+"exports"+fileSep
sharedAssets = tempDir

def findConfigFile():
    config = None
    if fileSep == "/":
        try:
            home = os.listdir(os.path.expanduser("~/.config/FileMate/"))
        except:
            print("No config file in .config")
        else:
            if "config" in home:
                config = os.path.expanduser("~/.config/FileMate/config")

    if config == None:
        try:
            configFile = open(startDir+"config.cfg", "r")
        except Exception as e:
            raise FildNotFoundError("No config file found. Refer to the README if you need help.")
        else:
            configFile.close()
            config = startDir+"config.cfg"

    return config


def readConfigFile(configLocation):
    configFile = open(configLocation, "r")
    for line in configFile:
        lineSplit = line.split("--")
        lineSplit[1] = lineSplit[1].replace("\n", "")
        if lineSplit[0] == "vaultDir":
            path = lineSplit[1]
        elif lineSplit[0] == "searchRecursively":
            if lineSplit[1] == "True":
                recurse = True
            elif lineSplit[1] == "False":
                recurse = False
            else:
                raise ValueError("Recursive search settings not set correctly in config file: Not True or False.")
        elif lineSplit[0] == "bluetooth":
            if lineSplit[1] == "True":
                bt = True
            elif lineSplit[1] == "False":
                bt = False
            else:
                raise ValueError("Bluetooth not configured correctly in config file: Not True or False.")

    configFile.close()

    return path, recurse, bt

config = findConfigFile()
sharedPath, searchRecursively, useBT = readConfigFile(config)


def runUI():
    Clock.max_iteration = 20
    ui = uiApp(title="FileMate")
    ui.run()
    print("Deleting temp files.")
    try:
        shutil.rmtree(osTemp+"FileMate"+fileSep)
    except:
        print("No temp files.")
    print("App closed.")




class File:

    def __init__(self, screen, hexPath, hexName, isDir=False, name=None, path=None):
        self.outerScreen = screen
        self.hexPath, self.hexName, self.isDir = hexPath, hexName, isDir
        self.rawSize = self.getFileSize()
        self.size = self.outerScreen.getGoodUnit(self.rawSize)
        self.isDir = isDir
        if path == None:
            self.path = self.getNormDir(self.hexPath)
        else:
            self.path = path
        if name == None:
            self.name = aesFName.decryptFileName(self.outerScreen.key, self.hexName)
        else:
            self.name = name

        if self.isDir:
            self.hexPath += fileSep
            self.path += fileSep


    def getNormDir(self, hexDir):
        hexDir = hexDir.replace(self.outerScreen.path, "")
        hexDir = hexDir.split(fileSep)
        for i in range(len(hexDir)):
            hexDir[i] = aesFName.decryptFileName(self.outerScreen.key, hexDir[i])

        return fileSep.join(hexDir)

    def getFileSize(self, recurse=True):
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
                size = os.path.getsize(self.hexPath)
                return size
            except Exception as e:
                print(e, "couldn't get size.")
                return " -"


class LoginScreen(Screen, FloatLayout):
    globalKey = StringProperty('')

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)


    def findFile(self, dir):    #For finding a file to decrypt first block and compare it with key given.
        fs = os.listdir(dir)
        for item in fs:
            if os.path.isdir(dir+item+"/"):
                if self.count == 0:
                    self.findFile(dir+item+"/")
                else:
                    return
            else:
                self.decryptTestFile = dir+item
                self.count += 1
                return

    def passToTerm(self, key, d):           #Makes a pipe to communicate with the AES written in go.
        if sys.platform.startswith("win32"):
            progname = "AESWin"
        else:
            progname = "AES"
        goproc = Popen(startDir+progname, stdin=PIPE, stdout=PIPE)
        out, err = goproc.communicate(("test, "+d+", 0, ").encode()+key.encode())
        return out

    def getIfValidKey(self, inputKey):              #Gets the output of the AES key checker.
        if len(os.listdir(sharedPath)) != 0:
            self.decryptTestFile = ""
            self.count = 0
            self.findFile(sharedPath)
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
                    self.globalKey = key
                    #self.manager.current = "main"
                    return "main"
                else:
                    pop = Popup(title="Invalid", content=Label(text="Invalid key."), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4))
                    pop.open()
                    return "Login"

    def needToSetKey(self):             #For checking if the user needs to make a new key.
        if len(os.listdir(sharedPath)) == 0:
            return "Input New Key (Write this down if you have to)"
        else:
            return "Input Key"



if useBT:   #Some of this stuff doesn't need to be loaded unless bt is used.
    from bluetooth import *


    class LoginScreenBT(LoginScreen, Screen, FloatLayout):      #Has the same methods as LoginScreen, but some overwritten with bluetooth.

        def __init__(self, **kwargs):
            super(LoginScreenBT, self).__init__(**kwargs)

        def on_enter(self):
            Clock.schedule_once(self.startSrv, 0.7) #Use the clock to allow the screen to be rendered. (Waits 0.7 seconds for screen to be loaded.)

        def checkKey(self, inputKey):
            inputKey = inputKey.split(",")
            inputKey = inputKey[:len(inputKey)-1]
            key = " ".join(str(i) for i in inputKey)    #Formatting for AES
            valid = self.getIfValidKey(key)
            if valid:
                self.ids.keyInput.text = "" #reset key input if valid
                self.globalKey = key
                return True
            else:
                return False


        def startSrv(self, dt=None):
            self.serverThread = threading.Thread(target=self.manager.get_screen("main").startBT, daemon=True)       #Runs the function in MainScreen, which prevents segmentation, so I don't have to shutdown server when screen is switched
            self.serverThread.start()   #Starting server in thread lets the screen be rendered while the server is waiting.




class MainScreen(Screen, FloatLayout):

    class listButton(Button):           #File button when using main screen.

        def __init__(self, mainScreen, fileObj, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.fileObj = fileObj          #The file the button corresponds to.

    class addNewFolderPop(Popup):

        def __init__(self, mainScreen, **kwargs):
            super(Popup, self).__init__(**kwargs)
            self.outerScreen = mainScreen

        def dirInputValid(self, inp):       #much rather re define it than do "self.outerScreen.SettingsPop.dirInputValid(self.outerScreen.SettingsPop, self.outerScreen.currentDir+text)" later on
            valid = (inp[0] == fileSep) and ("\n" not in inp)       #If it starts with the file separator and doesn't contain any new lines, then it is valid for now.
            inp = inp.split(fileSep)
            focusIsSlash = False
            for item in inp:            #Checks for multiple file separators next to each other, as that would be an invalid folder name.
                if item == "":
                    if focusIsSlash:
                        valid = False
                    focusIsSlash = True
                else:
                    focusIsSlash = False
            return valid

        def makeFolder(self, text):
            if self.dirInputValid(self.outerScreen.currentDir+text):
                try:
                    os.makedirs(self.outerScreen.currentDir+aesFName.encryptFileName(self.outerScreen.key, text))
                except OSError as e:
                    if "[Errno 36]" in str(e):  #OSError doesn't store the error code for some reason.
                        pop = Popup(title="Invalid Folder Name", content=Label(text="Folder name too long.", halign="center"), size_hint=(.3, .3), pos_hint={"x_center": .5, "y_center": .5})
                        pop.open()

                self.outerScreen.refreshFiles()
                self.dismiss()

    class SettingsPop(Popup):

        def __init__(self, mainScreen, **kwargs):
            self.outerScreen = mainScreen
            super(Popup, self).__init__(**kwargs)

            self.ids.searchSwitch.bind(active=self.searchSwitchCallback)
            self.ids.btSwitch.bind(active=self.btSwitchCallback)

        def searchSwitchCallback(self, switch, value):
            return self.editConfLoc("searchRecursively", str(value))

        def btSwitchCallback(self, switch, value):
            return self.editConfLoc("bluetooth", str(value))


        def editConfLoc(self, term, newContent):
            with open(config, "r") as conf:
                confContent = conf.readlines()

            for i in range(len(confContent)):
                a = confContent[i].split("--")
                if term == a[0]:
                    a[1] = newContent+"\n"
                    confContent[i] = "--".join(a)

            with open(config, "w") as confW:
                confW.writelines(confContent)

            if term == "bluetooth":
                self.outerScreen.useBTTemp = not self.outerScreen.useBTTemp
            elif term == "searchRecursively":
                self.outerScreen.searchRecursively = not self.outerScreen.searchRecursively


        def dirInputValid(self, inp):
            valid = (inp[0] == fileSep) and ("\n" not in inp)       #If it starts with the file separator and doesn't contain any new lines, then it is valid for now.
            inp = inp.split(fileSep)
            focusIsSlash = False
            for item in inp:            #Checks for multiple file separators next to each other, as that would be an invalid folder name.
                if item == "":
                    if focusIsSlash:
                        valid = False
                    focusIsSlash = True
                else:
                    focusIsSlash = False
            return valid

        def changeVaultLoc(self, inp):      #Sorts out the UI while the vault location is changed.
            if inp == "":
                pass
            else:
                if inp[len(inp)-1] != fileSep:
                    inp += fileSep
                if self.dirInputValid(inp):
                    if os.path.exists(inp) and os.path.isdir(inp):
                        self.editConfLoc("vaultDir", inp)
                        print("EDITING")
                        done = Popup(title="Done", content=self.outerScreen.infoLabel(text="Changed Vault Location to:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                        self.outerScreen.path = inp
                        self.outerScreen.currentDir = inp
                        self.outerScreen.resetButtons()
                        done.open()
                    else:
                        try:
                            os.makedirs(inp)
                            os.makedirs(inp+aesFName.encryptFileName(self.outerScreen.key, ".$recycling"))
                        except FileNotFoundError:
                            warn = Popup(title="Invalid", content=self.outerScreen.infoLabel(text="Directory not valid:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                            warn.open()
                        except PermissionError as e:
                            print(e, "what.")
                            warn = Popup(title="Invalid", content=self.outerScreen.infoLabel(text="Can't make a folder here:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                            warn.open()
                        except Exception as e:
                            print(e)
                            warn = Popup(title="Invalid", content=self.outerScreen.infoLabel(text="Can't make a folder here:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                            warn.open()
                        else:
                            if inp[len(inp)-1] != fileSep:
                                inp += fileSep
                            self.editConfLoc("vaultDir", inp)
                            done = Popup(title="Done", content=self.outerScreen.infoLabel(text="Changed Vault Location to:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                            self.outerScreen.path = inp
                            self.outerScreen.currentDir = inp
                            self.outerScreen.resetButtons()
                            done.open()
                else:
                    warn = Popup(title="Invalid", content=self.outerScreen.infoLabel(text="Directory not valid."), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                    warn.open()

    class infoButton(Button):       #The button that displays information about the file.

        def __init__(self, mainScreen, fileObj, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.fileObj = fileObj

    class infoLabel(Label):
        pass

    class encPopup(Popup): #For single files

        def __init__(self, outerScreen, encType, labText, fileList, locList, **kwargs):
            super(Popup, self).__init__(**kwargs)
            self.outerScreen = outerScreen
            #kivy stuff
            self.title = "Please wait..."
            self.pos_hint = {"center_x": .5, "center_y": .5}
            self.size_hint = (.7, .4)
            self.auto_dismiss = False

            self.fileList = fileList
            self.locList = locList

            self.grid = GridLayout(cols=1)
            self.subGrid = GridLayout(cols=3)
            self.currFile = Label(text="")
            self.per = Label(text="")
            self.spd = Label(text="")
            self.tim = Label(text="")
            self.pb = ProgressBar(value=0, max=os.path.getsize(self.fileList[0]), size_hint=(.9, .2))
            self.wholePb = ProgressBar(value=0, max=self.getTotalSize(), size_hint=(.9, .2))
            self.grid.add_widget(Label(text=labText))
            self.grid.add_widget(self.currFile)
            self.subGrid.add_widget(self.per)
            self.subGrid.add_widget(self.spd)
            self.subGrid.add_widget(self.tim)
            self.grid.add_widget(self.subGrid)
            self.grid.add_widget(self.pb)
            self.grid.add_widget(self.wholePb)
            self.content = self.grid

            self.checkThread = threading.Thread(target=self.enc, args=(encType,), daemon=True)
            self.checkThread.start()

        def getTotalSize(self):
            total = 0
            for file in self.fileList:
                total += os.path.getsize(file)
            return total

        def getGoodUnit(self, bps):
            divCount = 0
            divisions = {0: "B/s", 1: "KB/s", 2: "MB/s", 3: "GB/s", 4: "TB/s"}
            while bps > 1000:
                bps = bps/1000
                divCount += 1

            return ("%.2f" % bps) + divisions[divCount]

        def enc(self, encType):
            total = 0
            totalPer = 0
            for i in range(len(self.fileList)):
                self.pb.value = 0
                self.pb.max = os.path.getsize(self.fileList[i])
                if i == len(self.fileList)-1:
                    self.outerScreen.encDecTerminal(encType, self.fileList[i], self.locList[i], True, True)
                else:
                    self.outerScreen.encDecTerminal(encType, self.fileList[i], self.locList[i], True)

                prevInt = 0
                timeFor1per = 0
                timeAtLastP = time.time()
                lastSize = 0
                per = 0
                while self.pb.value < (self.pb.max-16): #-16 because padding might make it not be exactly equal
                    self.currFile.text = str(self.fileList[i] +"   "+ str(i)+"/"+str(len(self.fileList)))
                    try:
                        self.pb.value = os.path.getsize(self.locList[i])
                        self.wholePb.value = total + self.pb.value
                    except:
                        pass

                    else:
                        per = self.wholePb.value_normalized*100

                        if int(per) != prevInt:
                            timeFor1per = time.time()- timeAtLastP
                            timeAtLastP = time.time()

                            self.tim.text = "{0:.1f}\nSeconds left.".format(timeFor1per*(((self.wholePb.max - self.wholePb.value)/self.wholePb.max)*100))
                            sizeDelta = self.wholePb.value - lastSize
                            self.spd.text = self.getGoodUnit(sizeDelta/timeFor1per)

                            prevInt = int(per)
                            lastSize = self.wholePb.value

                        self.per.text = "{0:.2f}%".format(per)
                    time.sleep(0.01)

                totalPer += 100
                total += self.pb.value

            self.dismiss()


    class btTransferPop(encPopup):

        def __init__(self, mainScreen, fileObjTmp, **kwargs):
            super(Popup, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.title = "Please wait..."
            self.size_hint = (.7, .4)
            self.pos_hint = {"center_x": .5, "center_y": .5}
            self.auto_dismiss = False
            self.grid = GridLayout(cols=1)
            self.subGrid = GridLayout(cols=3)
            self.currFile = Label(text=fileObjTmp.path)
            self.per = Label(text="")
            self.spd = Label(text="")
            self.tim = Label(text="")
            self.pb = ProgressBar(value=0, max=1, size_hint=(.9, .2))
            self.grid.add_widget(Label(text="Sending..."))
            self.grid.add_widget(self.currFile)
            self.subGrid.add_widget(self.per)
            self.subGrid.add_widget(self.spd)
            self.subGrid.add_widget(self.tim)
            self.grid.add_widget(self.subGrid)
            self.grid.add_widget(self.pb)
            self.content = self.grid

            self.sendThread = threading.Thread(target=self.sendFile, args=(fileObjTmp,), daemon=True) # can be cancelled mid way through
            self.sendThread.start()

        def sendFile(self, fileObj):
            # File name is sent with !NAME!#!!<name here>!!~
            # File data is sent right afterwards, ending with ~!!ENDF!
            # Overall, it is sent as: !NAME!#!!<name here>!!~<datahere>~!!ENDF!
            self.outerScreen.clientSock.send("!NAME!#!!{}!!~".format(fileObj.name))
            print("!NAME!#!!{}!!~".format(fileObj.name), "Sent")

            newLoc = osTemp+"FileMate"+fileSep+fileObj.name
            if not os.path.isdir(osTemp+"FileMate"+fileSep):
                os.makedirs(osTemp+"FileMate"+fileSep)

            self.outerScreen.passToPipe("n", fileObj.hexPath, newLoc, fileObj.name, op=False)   #self, type, d, targetLoc, newName=None, endOfFolderList=False

            bufferSize = 1024
            buff = []
            fr = open(newLoc, "rb")
            buff = fr.read(bufferSize)    #Read 1Kb of data
            buffCount = 0
            self.per.text = "{0:.2f}%".format(0)

            start = time.time()
            #Send data
            while buff:
                self.outerScreen.clientSock.send(buff)
                buffCount += bufferSize
                buff = fr.read(bufferSize)

                self.pb.value = buffCount/fileObj.rawSize
                self.per.text = "{0:.2f}%".format(self.pb.value*100)
                self.spd.text = self.getGoodUnit(buffCount/(time.time() - start))

            self.outerScreen.clientSock.send("~!!ENDF!")
            self.dismiss()




    class deleteButton(Button):

        def __init__(self, mainScreen, fileObj, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.fileObj = fileObj

    class nameSortButton(Button):           #Sorts the listButtons alphabetically and by folders/files.

        def __init__(self, mainScreen, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen

        def changeSortOrder(self):
            self.outerScreen.ascending = not self.outerScreen.ascending
            if self.outerScreen.ascending:
                self.text = "^"
                self.outerScreen.removeButtons()
                self.outerScreen.createButtons(self.outerScreen.currentList, True)
            else:
                self.text = "v"
                self.outerScreen.removeButtons()
                self.outerScreen.createButtons(self.outerScreen.currentList[::-1], False)

    class sizeSortButton(Button):           #Sorts the files/folders by size

        def __init__(self, mainScreen, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.ascending = True
            self.sortList = []


        def sortBySize(self):
            self.sortList = sortsCy.quickSortSize(self.outerScreen.currentList)
            if not self.ascending:
                self.sortList = self.sortList[::-1]

            self.outerScreen.removeButtons()
            self.outerScreen.createButtons(self.sortList, False)

        def changeSizeOrder(self):
            self.ascending = not self.ascending
            if self.ascending:
                self.text = "v"
            else:
                self.text = "^"

            if (self.sortList) and (self.outerScreen.previousDir == self.outerScreen.currentDir):
                self.sortList = self.sortList[::-1]
                print("Using old list")
                self.outerScreen.removeButtons()
                self.outerScreen.createButtons(self.sortList, False)
            else:
                self.outerScreen.previousDir = self.outerScreen.currentDir
                print("Re-sorting")
                self.sortBySize()

    class addFileScreen(Popup):     #The screen (it's actually a Popup) for adding folders/files to the vault.

        def __init__(self, mainScreen, **kwargs):
            super(Popup, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.layout = FloatLayout()

        class ConfirmationPopup(Popup):     #Popup for confirming encryption.

            def __init__(self, fileScreen, input, **kwargs):
                super(Popup, self).__init__(**kwargs)
                self.fileScreen = fileScreen
                self.inputText = input


        def checkIfSure(self, input):
            sure = self.ConfirmationPopup(self, input)
            sure.open()


    key = StringProperty('')        #Shared key between LoginScreen and MainScreen

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.ascending = True
        self.key = ""
        self.encPop = None
        self.entered = False
        self.validBTKey = False
        self.useBTTemp = useBT
        self.previousDir = None
        self.lastPathSent = ""
        self.recycleFolder = ""
        self.recycleName = ""
        self.searchRecursively = searchRecursively

        Window.bind(on_dropfile=self.onFileDrop)    #Binding the function to execute when a file is dropped into the window.
        self.path = sharedPath
        self.assetsPath = sharedAssets
        self.currentDir = self.path
        print(self.currentDir, "CURRENT DIR")
        self.scroll = ScrollView(size_hint=(.9, .79), pos_hint={"x": .005, "y": 0})


    def __repr__(self):
        return "MainScreen"

    def on_enter(self): #When the screen is started.
        if not self.entered:
            self.setupSortButtons() #Put sort buttons in place.
            self.recycleName = aesFName.encryptFileName(self.key, ".$recycling")
            self.recycleFolder = self.path+self.recycleName+fileSep

            if not os.path.exists(self.recycleFolder):
                print("Recycling folder not found in directory, making one now.")
                os.makedirs(self.recycleFolder)

            self.entered = True

        if self.recycleFolder in self.currentDir:
            self.createButtons(self.List(self.path))     # Don't want to log into the recycling bin, as the user might get confused.
        else:
            self.createButtons(self.List(self.currentDir)) # Loads previous directory.

    def on_leave(self):     #Kept separate from lock because i may want to add more screens.
        self.remove_widget(self.scroll)

    def lock(self):         #Procedure for when the program is locked.
        self.clearUpTempFiles() #Delete all temporary files (decrypted files ready for use).
        if useBT:
            self.manager.get_screen("Login").ids.clientLabel.text = ""
            self.validBTKey = False
        return mainthread(self.changeToLogin())      #Change screen to the login screen. Ran on mainthread in case it was called in 


    def runServMain(self):
        self.serverSock = BluetoothSocket( RFCOMM )
        self.serverSock.bind(("",PORT_ANY))
        self.serverSock.listen(1)

        port = self.serverSock.getsockname()[1]

        uuid = "80677070-a2f5-11e8-b568-0800200c9a66"

        advertise_service(self.serverSock, "FileMateServer",
                          service_id = uuid,
                          service_classes = [ uuid, SERIAL_PORT_CLASS ],
                          profiles = [ SERIAL_PORT_PROFILE ],)

        print("[BT]: Waiting for connection on RFCOMM channel", port)

        self.clientSock, self.clientInfo = self.serverSock.accept()
        print("[BT]: Accepted connection from ", self.clientInfo)
        self.manager.get_screen("Login").ids.clientLabel.text = "Connected to: "+str(self.clientInfo[0])

        numbers = []
        append = True

        try:
            data = ""
            buff = []
            backCommand = [33, 66, 65, 67, 75, 33]                                            # !BACK!
            fileSelectCommand = [33, 70, 73, 76, 69, 83, 69, 76, 69, 67, 84, 33, 35, 33, 33]  # !FILESELECT!#!!
            endHeader = [126, 33 ,33]                                                         # ~!!

            while len(data) > -1:
                data = self.clientSock.recv(1024)
                print("[BT]: Received data.")
                if not self.validBTKey:
                    if append:
                        numbers.append(str(data, "utf-8"))
                    if b"~" in data:    ##End of message
                        append = False
                        tempNums = "".join(numbers)
                        tempNums = tempNums.replace("#", "")
                        tempNums = tempNums.replace("~", "")
                        if self.manager.get_screen("Login").checkKey(tempNums):
                            numbers = []
                            append = True
                            self.clientSock.send("1")
                            print("[BT]: Send true.")
                            self.validBTKey = True
                            self.sendFileList(self.getListForSend(self.path))
                            mainthread(self.changeToMain())
                        else:
                            numbers = []
                            append = True
                            self.clientSock.send("0")
                            print("[BT]: Send false.")
                            self.validBTKey = False

                else:
                    for i in data:
                        buff.append(i)

                    if buff[:6] == backCommand:   # Buffer is reset every time a header is found
                        pathBack = self.getPathBack(self.lastPathSent)
                        print(pathBack, "pathBack")
                        if (not pathBack) or (pathBack.replace(self.path, "") == pathBack):    # If you can't go further back (if pathBack has less than path, then remove returns the original string).
                            print("Can't go further back.")
                            self.clientSock.send("!ENDOFTREE!")
                        else:
                            self.sendFileList(self.getListForSend(pathBack))
                            print("Should have sent now.")
                        buff = []

                    elif buff[:15] == fileSelectCommand:
                        commandParams = buff[15:]
                        if commandParams[len(commandParams)-3:] == endHeader:
                            fileWantedList = commandParams[:len(commandParams)-3]
                            fileWanted = ""
                            for letter in fileWantedList:
                                fileWanted += chr(letter)

                            print(fileWanted, "fileWanted")
                            buff = []
                            filesInPath = self.List(self.lastPathSent)

                            f = 0
                            fileObj = None
                            while (f < len(filesInPath)) and (fileObj == None):
                                if filesInPath[f].name == fileWanted:
                                    fileObj = filesInPath[f]
                                f += 1

                            if fileObj != None:
                                if fileObj.isDir:
                                    # Return list of that directory.
                                    self.sendFileList(self.getListForSend(fileObj.hexPath))
                                else:
                                    self.makeSendFile(fileObj)

                            else:
                                print("Couldn't find that file :/")
                                self.clientSock.send("!NOTFOUND!")


                    elif len(buff) >= 15: # Re-set to wait for next command.
                        buff = []



        except IOError as e:
            print(e)

        print("Closed.")

        self.clientSock.close()
        self.serverSock.close()
        print("all done, LOCK")
        self.lock()


    def sendFileList(self, fileList):
        # File list sent like: !FILELIST!#!!--fileName1--filename2~!!ENDLIST!
        self.clientSock.send("!FILELIST!#!!")
        print("Sent !FILELIST!#!!")

        for i in fileList:
            self.clientSock.send("--{}".format(i))

        print("Sent full list, now sent end.")
        self.clientSock.send("~!!ENDLIST!")


    def getListForSend(self, path):
        if not path:
            return False
        else:
            fs = os.listdir(path)
            listOfFolders = []
            listOfFiles = []
            for item in fs:
                if os.path.isdir(path+item):
                    listOfFolders.append(aesFName.decryptFileName(self.key, item))
                else:
                    listOfFiles.append(aesFName.decryptFileName(self.key, item))

            self.lastPathSent = path

            return sortsCy.quickSortAlph(listOfFolders, fileObjects=False)+sortsCy.quickSortAlph(listOfFiles, fileObjects=False)



##Functions for changing screen within threads
    @mainthread
    def changeToMain(self):
        self.manager.current = "main"

    @mainthread
    def changeToLogin(self):    #Only used for checkServerStatus because you can only return a function or variable, and if i execute this within the thread then it causes a segmentation fault.
        self.manager.current = "Login"
##############################################

    def startBT(self):
        self.serverThread = threading.Thread(target=self.runServMain, daemon=True)      #Start BT server as thread so the screen still renders.
        self.serverThread.start()

    def setupSortButtons(self):
        self.sortsGrid = GridLayout(cols=2, size_hint=(.9, .04), pos_hint={"x": .005, "y": .79})    #Make a grid of 1 row (colums=2 and i am only adding 2 widgets) to hold sort buttons.
        self.nameSort = self.nameSortButton(self, text="^", size_hint_x=.87)
        self.sizeSort = self.sizeSortButton(self, size_hint_x=.13)
        self.sortsGrid.add_widget(self.nameSort)
        self.sortsGrid.add_widget(self.sizeSort)
        self.add_widget(self.sortsGrid) #Add the sort buttons grid to the float layout of MainScreen.

    def getGoodUnit(self, bytes):       #Get a good unit for displaying the sizes of files.
        if bytes == " -":
            return " -"
        else:
            divCount = 0
            divisions = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB", 5: "PB"}
            while bytes > 1000:
                bytes = bytes/1000
                divCount += 1

            return ("%.2f" % bytes) + divisions[divCount]

    def getSortedFoldersAndFiles(self, fileObjects, inverse=False): #Get a sorted list of files for display.
        folders = []
        files = []
        for i in range(len(fileObjects)):   #Separate into folders and files
            if fileObjects[i].isDir:
                folders.append(fileObjects[i])
            else:
                files.append(fileObjects[i])

        foldersSort = sortsCy.quickSortAlph(folders)   #Quick sort the list of folders and the list of files.
        filesSort = sortsCy.quickSortAlph(files)

        if inverse: #If inverse
            foldersSort = foldersSort[::-1] #Invert the array/
            filesSort = filesSort[::-1]

        return foldersSort+filesSort


    def recursiveSize(self, f, encrypt=False):  #Get size of folders.
        fs = os.listdir(f)
        for item in fs:
            if encrypt:
                item = aesFName.encryptFileName(self.key, item)
            if os.path.isdir(f+fileSep+item):
                try:
                    self.recursiveSize(f+fileSep+item)
                except OSError:
                    pass
            else:
                try:
                    self.totalSize += os.path.getsize(f+fileSep+item)
                except PermissionError: #Thrown when the file is owned by another user/administrator or root.
                    pass


    def openRecycling(self):
        warnPop = Popup(title="Changed Mode", content=Label(text="You are now in the\nrecycling folder.\nClick files to restore, and \nenter the INFO menu\nto see more information,\nor delete the file permanently."), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4))
        warnPop.open()
        self.currentDir = self.recycleFolder
        self.removeButtons()
        print(self.currentDir, "current dir")
        self.createButtons(self.List(self.currentDir))

############################################

#######Button Creation and button functions#######
    def createButtonsCore(self, array): #Makes each file button with it's information and adds it to a grid.
        self.currentList = array
        for item in array:
            if item.name != ".$recycling":
                if item.isDir:
                    btn = self.listButton(self, item, text=("    "+item.name), background_color=(0.3, 0.3, 0.3, 1))
                    info = self.infoButton(self, item, background_color=(0.3, 0.3, 0.3, 1))
                else:
                    btn = self.listButton(self, item, text=("    "+item.name))
                    info = self.infoButton(self, item)

                btn.bind(size=btn.setter("text_size"))
                info.bind(size=info.setter("text_size"))
                fileS = Label(text=" "+str(item.size), size_hint=(.1, 1), halign="left", valign="middle")
                fileS.bind(size=fileS.setter("text_size"))
                self.grid.add_widget(btn)
                self.grid.add_widget(info)
                self.grid.add_widget(fileS)

    def createButtons(self, fileObjects, sort=True):
        self.currentList = []
        if sort:
            sortedArray = self.getSortedFoldersAndFiles(fileObjects)    #Sort the list of files.

        self.grid = GridLayout(cols=3, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll = ScrollView(size_hint=(.9, .79), pos_hint={"x": .005, "y": 0}) #Grid is added to the scroll view.
        self.scroll.add_widget(self.grid)
        self.add_widget(self.scroll)    #Scroll view is added to the float layout of MainScreen.

        if sort:
            self.createButtonsCore(sortedArray)
        else:
            self.createButtonsCore(fileObjects)

    def removeButtons(self):    #Remove the list of files.
        self.grid.clear_widgets()
        self.scroll.clear_widgets()
        try:
            self.remove_widget(self.scroll)
        except Exception as e:
            print(e, "Already removed?")


    def getFileNameFromText(self, itemName):    #Get the file name.
        return itemName[4:]


    def traverseButton(self, fileObj):  #Function when file is clicked.
        if self.recycleFolder not in self.currentDir:
            if fileObj.isDir:   #If is a folder, then display files within that folder.
                self.previousDir = self.currentDir
                self.currentDir = fileObj.hexPath
                self.resetButtons()
            else:   #If is a file, decrypt the file and open it.
                self.decrypt(fileObj)
        else:
            print("Recovering this file to path:", fileObj.name)
            shutil.move(fileObj.hexPath, self.path)
            self.refreshFiles()


    def getFileInfo(self, fileObj):     #Get information about a file/folder.
        fileViewDir = fileObj.path.replace(self.path, "")   #Remove the vault path from the file's path so that it displays nicely.

        internalView = ScrollView()
        self.infoPopup = Popup(title="File Information", content=internalView, pos_hint={"center_x": .5, "center_y": .5}, size_hint=(.8, .4))
        internalLayout = GridLayout(cols=2, size_hint_y=None, row_default_height=self.infoPopup.size[1]/4)

        internalLayout.add_widget(self.infoLabel(text="File Name:", halign="left", valign="middle"))
        internalLayout.add_widget(self.infoLabel(text=fileObj.name, halign="left", valign="middle"))

        internalLayout.add_widget(self.infoLabel(text="Current Location:", halign="left", valign="middle"))
        internalLayout.add_widget(self.infoLabel(text="/Vault/"+fileViewDir, halign="left", valign="middle"))

        internalLayout.add_widget(self.infoLabel(text="Size:", halign="left", valign="middle"))
        internalLayout.add_widget(self.infoLabel(text=str(fileObj.size), halign="left", valign="middle"))

        internalLayout.add_widget(self.infoLabel())
        internalLayout.add_widget(self.infoLabel())

        internalLayout.add_widget(self.infoLabel())
        internalLayout.add_widget(self.infoLabel())


        if useBT and not fileObj.isDir:
            btButton = Button(text="Send to mobile (BT)", halign="left", valign="middle")
            btButton.bind(on_release=partial(self.makeSendFile, fileObj))
            internalLayout.add_widget(btButton)


        if fileObj.isDir:
            decBtn = Button(text="Decrypt Folder", halign="left", valign="middle")
            decBtn.bind(on_release=self.decryptDir)
            internalLayout.add_widget(decBtn)

        delText = "Delete"
        if self.recycleFolder in self.currentDir:
            delText = "Delete Permanently"

        internalLayout.add_widget(self.deleteButton(self, fileObj,text=delText))

        internalView.add_widget(internalLayout)
        self.infoPopup.open()

    def makeSendFile(self, fileObj, buttonInstance=None):
        self.sendFile = self.btTransferPop(self, fileObj)
        self.sendFile.open()

    def makeFolder(self, folderName):
        print(folderName, "folderName")

    def moveFileToRecycling(self, fileObj):
        print("Moving", fileObj.hexPath)
        if os.path.exists(fileObj.hexPath):
            shutil.move(fileObj.hexPath, self.recycleFolder)
        else:
            raise FileNotFoundError(fileObj.hexPath, "Not a file, can't move to recycling.")

    def deleteFile(self, fileObj):
        if os.path.exists(fileObj.hexPath): #Checks file actually exists before trying to delete it.
            if self.recycleFolder not in self.currentDir:
                print("Moving", fileObj.hexPath)
                shutil.move(fileObj.hexPath, self.recycleFolder)
            else:
                print("Deleting", fileObj.hexPath)
                if fileObj.isDir:
                    shutil.rmtree(fileObj.hexPath)
                else:
                    os.remove(fileObj.hexPath)
            self.refreshFiles()
            self.infoPopup.dismiss()
        else:
            raise FileNotFoundError(fileObj.hexPath, "Not a file, can't delete.")

    def goBackFolder(self):     #Go up a folder.
        if self.currentDir != self.path:    #Can't go further past the vault dir.
            self.previousDir = self.currentDir
            if self.currentDir in self.recycleFolder:
                self.goHome()
            else:
                self.currentDir = self.getPathBack(self.currentDir)
            self.resetButtons()
        else:
            print("Can't go further up.")
            return False

    def getPathForButton(self, item):   #Get the path to the picture for each button.
        return self.assetsPath+item

    def resetButtons(self): #Goes back to self.currentDir, different to refresh.
        self.removeButtons()
        self.nameSort.text = "^"
        self.sizeSort.text = ""
        self.createButtons(self.List(self.currentDir))

    def refreshFiles(self):   #Refreshes the file buttons currently on the screen in case of issues.
        self.removeButtons()
        self.createButtons(self.List(self.currentDir))

    def refreshButtons(self):
        self.removeButtons()
        self.createButtons(self.currentList, False)

    def goHome(self):   #Takes the user back to the vault dir.
        self.removeButtons()
        self.nameSort.text = "^"
        self.sizeSort.text = ""
        self.previousDir = self.currentDir
        self.currentDir = self.path
        self.createButtons(self.List(self.currentDir))


    def List(self, dir):    #Lists a directory.
        fs = os.listdir(dir)
        listOfFolders = []
        listOfFiles = []
        for item in fs:
            if os.path.isdir(dir+item):
                listOfFolders.append(File(self, dir+item, item, True))
            else:
                listOfFiles.append(File(self, dir+item, item))
        return listOfFolders+listOfFiles

    def getPathBack(self, origPath):  #Gets the path above the current folder.
        tempDir = origPath.split(fileSep)
        del tempDir[len(tempDir)-2]
        tempDir = fileSep.join(tempDir)
        return tempDir

###########Sorts + Searches############
    def quickSortTuples(self, tuples):  #Quick sorts tuples (for search results).
        if len(tuples) > 1:
            left = []
            right = []  #Make seperate l+r lists, and add on at the end.
            middle = []
            pivot = tuples[int(len(tuples)/2)]
            for i in tuples:
                if i[0] < pivot[0]:
                    left.append(i)
                elif i[0] > pivot[0]:
                    right.append(i)
                else:
                    middle.append(i)
            return self.quickSortTuples(left)+middle+self.quickSortTuples(right)
        else:
            return tuples

    def findAndSortCore(self, dirName, item):
        files = self.List(dirName)
        for fileObj in files:
            loc = fileObj.name.find(item)

            if fileObj.name == item:
                self.searchResults = [fileObj] + self.searchResults
                self.removeButtons()
                self.createButtons(self.searchResults)
            elif loc != -1:
                self.unsorted.append((loc, fileObj))   #Adds loc found in word, so that it can be sorted by where it is found

            if fileObj.isDir and self.searchRecursively:
                self.findAndSortCore(fileObj.hexPath, item)


    def findAndSort(self, item):    #Main search function.
        self.unsorted = []

        self.findAndSortCore(self.currentDir, item)

        if len(self.unsorted) > 0:
            sorted = self.quickSortTuples(self.unsorted)
            for i in sorted:
                self.searchResults.append(i[1])
            self.removeButtons()
            self.createButtons(self.searchResults, False)

        else:
            pop = Popup(title="No Results", content=Label(text="No results found for:\n"+item, halign="center"), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4))
            pop.open()



    def searchThread(self, item):
        self.findAndSort(item)
        return "Done"


##################################


####Progress Bar Information####

    def values(self, st):   #Information for space left on device.
        values = shutil.disk_usage(self.path)
        if st:
            return self.getGoodUnit(int(values[1]))+" / " + self.getGoodUnit(int(values[0])) + " used."
        else:
            return [values[0], values[1]]

################################

####Search Bar functions####

    def searchForItem(self, item):
        self.resetButtons()
        self.searchResults = []
        self.t = threading.Thread(target=self.searchThread, args=(item,), daemon=True)
        self.t.start()

############################

######Encryption Stuff + opening decrypted files######
    def passToPipe(self, type, d, targetLoc, newName=None, endOfFolderList=False, op=True):     #Passes parameters to AES written in go.
        if sys.platform.startswith("win32"):
            progname = "AESWin.exe"
        else:
            progname = "AES"


        goproc = Popen(startDir+progname, stdin=PIPE, stdout=PIPE)
        out, err = goproc.communicate((type+", "+d+", "+targetLoc+", "+self.key).encode()) #dont use d for fileNames, use targetLoc for file name and self.key for self.key
        if err != None:
            raise ValueError("Key not valid.")

        if endOfFolderList:
            if self.encPop != None:
                self.encPop.dismiss()
                self.encPop = None

            print("Refreshing files.")
            self.refreshFiles()

        if type == "n" and op and endOfFolderList:
            mainthread(self.openFileTh(targetLoc, d))
        return out

    def openFileTh(self, fileLoc, startLoc):
        self.openFileThread = threading.Thread(target=self.openFile, args=(fileLoc, startLoc,), daemon=True)
        self.openFileThread.start()

    def encDecTerminal(self, type, d, targetLoc, isPartOfFolder=False, endOfFolderList=False, newName=None):     #Handels passToPipe and UI while encryption/decryption happens.
        alreadyDecrypted = False
        fileName = ""
        if type == "y":     #The file name also needs to be encrypted
            tempDir = d.split(fileSep)
            fileName = tempDir[len(tempDir)-1]
            popText = "Encrypting..."
            if os.path.exists(targetLoc):
                if os.path.isdir(targetLoc):
                    shutil.rmtree(targetLoc)
                else:
                    os.remove(targetLoc)

                #replace file name with new hex
            targetLoc = targetLoc.split(fileSep)
            targetLoc[len(targetLoc)-1] = aesFName.encryptFileName(self.key, fileName)
            targetLoc = fileSep.join(targetLoc)

        elif type == "n":   #Need to decrypt file name if decrypting
            tempDir = d.split(fileSep)
            fileName = tempDir[len(tempDir)-1]
            targetLoc = targetLoc.split(fileSep)
            newName = targetLoc[len(targetLoc)-1] #Stops you from doing it twice in decrypt()
            targetLoc = fileSep.join(targetLoc)
            popText = "Decrypting..."

        if not isPartOfFolder:
            self.encPop = self.encPopup(self, type, popText, [d], [targetLoc]) #self, labText, d, newLoc, **kwargs
            mainthread(Clock.schedule_once(self.encPop.open, -1))

        if len(fileName) <= 112: #Any bigger than this and the file name is too long (os throws the error).
            self.encryptProcess = threading.Thread(target=self.passToPipe, args=(type, d, targetLoc, newName, endOfFolderList,), daemon=False) #Don't want to be mid-way through decrypting otherwise it may corrupt file.
            self.encryptProcess.start()
        else:
            print("File name too long :(")
            self.encPop.dismiss()
            print("Dismissed?")
            pop = Popup(title="Invalid file name.", content=Label(text="File name too long,\nplease try again with shorter\nfile name."))
            pop.open()

    def openFile(self, location, startLoc):
        if sys.platform.startswith("win32"):
            location = location.split("\\")
            location = "/".join(location) #Windows actually accepts forward slashes in terminal
            command = "cmd /k start "+'"" '+'"'+location+'"'+" /D"
        else:
            command = "xdg-open "+'"'+location+'"'      #Quotation marks for if the dir has spaces in it
        os.system(command)#Using the same for both instead of os.startfile because os.startfile doesn't wait for file to close
        self.encDecTerminal("y", location, startLoc)   #Is encrypted when program closes anyway


    def onFileDrop(self, window, filePath):  #Drag + drop files
        self.checkCanEncrypt(filePath.decode())
        self.resetButtons()
        return "Done"

    def decrypt(self, fileObj, op=True):
        if not os.path.isdir(osTemp+"FileMate"+fileSep):
            os.makedirs(osTemp+"FileMate"+fileSep)
        fileLoc = osTemp+"FileMate"+fileSep+fileObj.name  #Place in temporary files where it is going to be stored.
        if os.path.exists(fileLoc) and op:         #Checks file exits already in temp files, so it doesn't have to decrypt again.
            self.openFileTh(fileLoc, fileObj.hexPath)
        else:
            self.encDecTerminal("n", fileObj.hexPath, fileLoc, newName=fileObj.name)


    def checkDirExists(self, dir):  #Handles UI for checking directory exits when file added.
        if os.path.exists(dir):
            return True
        else:
            self.popup = Popup(title="Invalid", content=Label(text=dir+" - Not a valid directory."), pos_hint={"center_x": .5, "center_y": .5}, size_hint=(.4, .4))
            self.popup.open()
            return False

    def encDecDir(self, encType, d, targetLoc):
        if self.encPop != None:
            self.encPop.dismiss()
            self.encPop = None

        self.fileList = []
        self.locList = []
        self.encDecDirCore(d, targetLoc)

        self.encPop = self.encPopup(self, encType, "Encrypting...", self.fileList, self.locList) #self, labText, fileList, locList, **kwargs
        mainthread(Clock.schedule_once(self.encPop.open, -1))

    def decryptDir(self, buttonInstance=None):
        pass

    def encDecDirCore(self, d, targetLoc): #Encrypts whole directory.
        fs = os.listdir(d)
        targetLoc = targetLoc.split(fileSep)
        targetLoc[len(targetLoc)-1] = aesFName.encryptFileName(self.key, targetLoc[len(targetLoc)-1])
        targetLoc = fileSep.join(targetLoc)
        for item in fs:
            if os.path.isdir(d+item):
                try:
                    self.encDecDirCore(d+item+fileSep, targetLoc+fileSep+item) #Recursive
                except OSError:
                    pass
            else:
                try:
                    self.createFolders(targetLoc+fileSep)
                    self.fileList.append(d+item)
                    self.locList.append(targetLoc+fileSep+aesFName.encryptFileName(self.key, item))
                except PermissionError:
                    pass

    def checkCanEncrypt(self, inp):
        if "--" in inp: #Multiple files/folders input.
            inp = inp.split("--")
            for d in inp:
                if self.checkDirExists(d):
                    if os.path.isdir(d):
                        if d[len(d)-1] != fileSep:
                            d += fileSep
                        dSplit = d.split(fileSep)
                        self.encDecDir("y", d, self.currentDir+dSplit[len(dSplit)-2]+fileSep)
                    else:
                        dSplit = d.split(fileSep)
                        self.encDecTerminal("y", d, self.currentDir+dSplit[len(dSplit)-1])

        else:
            if self.checkDirExists(inp):
                if os.path.isdir(inp):
                    if inp[len(inp)-1] != fileSep:
                        inp += fileSep
                    inpSplit = inp.split(fileSep)
                    self.encDecDir("y", inp, self.currentDir+inpSplit[len(inpSplit)-2])
                else:
                    inpSplit = inp.split(fileSep)
                    self.encDecTerminal("y", inp, self.currentDir+inpSplit[len(inpSplit)-1])

        self.resetButtons()


    def createFolders(self, targetLoc):
        if not os.path.exists(targetLoc):
            os.makedirs(targetLoc)


    def clearUpTempFiles(self):     #Deletes temp files.
        print("Deleting temp files.")
        try:
            shutil.rmtree(osTemp+"FileMate"+fileSep)
        except:
            print("No temp files.")
###########################



class ScreenManagement(ScreenManager):
    pass



if useBT:   #Two ways of loading, one for BT one not for BT
    presentation = Builder.load_file(os.path.dirname(os.path.realpath(__file__))+fileSep+"mainBT.kv")
else:
    print("Using:", os.path.dirname(os.path.realpath(__file__))+fileSep+"mainNoBT.kv")
    presentation = Builder.load_file(os.path.dirname(os.path.realpath(__file__))+fileSep+"mainNoBT.kv")

class uiApp(App):

    def build(self):
        return presentation


if __name__ == "__main__":
    runUI()

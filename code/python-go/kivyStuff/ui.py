import os
import sys
import shutil
import threading
import time
import multiprocessing
import fileinput
import tempfile
import pickle
from subprocess import Popen, PIPE

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
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.progressbar import ProgressBar
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.widget import WidgetException
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
#import kivy.uix.contextmenu
from kivy.base import EventLoop
from kivy.lang import Builder

##########Import Bluetooth Module##########
#from bluetooth import *
# blueDir = str(os.path.dirname(os.path.realpath(__file__)))
# blueDir = blueDir.split("/")
# print(blueDir)
# del blueDir[len(blueDir)-1]
# blueDir = "/".join(blueDir)
# blueDir += "/bluetoothStuff"
# print(blueDir, "egg")
#
# sys.path.insert(0, blueDir)
# import bluetoothMain
########################################

############Import SHA Module###########
import SHA

###########Import filename encryption###
import aesFName

#######Load OS Specific settings####
global fileSep #linux has different file separators to windows and different temp dir
global osTemp
if sys.platform.startswith("win32"):
    fileSep = "\\"
else:          #windows bad
    fileSep = "/"
osTemp = tempfile.gettempdir()+fileSep

######Load config and define shared variables#####
global sharedPath
global sharedAssets
global startDir
global searchRecursively
global useBT
#global root #For use like root.x in kv file
useBT = False

startDir = os.path.dirname(os.path.realpath(__file__))+fileSep
tempDir = startDir.split(fileSep)
del tempDir[len(tempDir)-2]
startDir = fileSep.join(tempDir)
print(tempDir, "TEMP DIR")
for i in range(2):
    del tempDir[len(tempDir)-2]

tempDir = fileSep.join(tempDir)
tempDir += "assets"+fileSep+"exports"+fileSep
sharedAssets = tempDir
configFile = open(startDir+"config.cfg", "r")

for line in configFile:
    lineSplit = line.split("--")
    lineSplit[1] = lineSplit[1].replace("\n", "")
    if lineSplit[0] == "vaultDir":
        sharedPath = lineSplit[1]
    elif lineSplit[0] == "searchRecursively":
        if lineSplit[1] == "True":
            searchRecursively = True
        elif lineSplit[1] == "False":
            searchRecursively = False
        else:
            raise ValueError("Recursive search settings not set correctly in config file: Not True or False.")
    elif lineSplit[0] == "bluetooth":
        if lineSplit[1] == "True":
            useBT = True
        elif lineSplit[1] == "False":
            useBT = False
        else:
            raise ValueError("Bluetooth not configured correctly in config file: Not True or False.")

configFile.close()


###TO DO LIST###
#~ Bluetooth
#~ SHA names of files - store encrypted tree of files

###Bluetooth stuff### needs to be accessable by both screens.
# def runServ(currentLogIn):
#     server_sock=BluetoothSocket( RFCOMM )
#     server_sock.bind(("",PORT_ANY))
#     server_sock.listen(1)
#
#     port = server_sock.getsockname()[1]
#
#     uuid = "80677070-a2f5-11e8-b568-0800200c9a66"
#
#     advertise_service( server_sock, "FileMateServer",
#                        service_id = uuid,
#                        service_classes = [ uuid, SERIAL_PORT_CLASS ],
#                        profiles = [ SERIAL_PORT_PROFILE ],)
#
#     print("Waiting for connection on RFCOMM channel %d" % port)
#
#     client_sock, client_info = server_sock.accept()
#     print("Accepted connection from ", client_info)
#     LOCK = False
#
#     numbers = []
#     append = True
#
#     try:
#         while True:
#             data = client_sock.recv(1024)
#             if len(data) == 0: break
#             print("received [%s]" % data)
#             if append:
#                 numbers.append(str(data, "utf-8"))
#             if b"~" in data:    ##End of message
#                 append = False
#                 print(numbers)
#                 tempNums = "".join(numbers)
#                 print(tempNums, "join")
#                 time.sleep(1)
#                 tempNums = tempNums.replace("#", "")
#                 tempNums = tempNums.replace("~", "")
#                 print(tempNums, "tempnums")
#                 valid = currentLogIn.checkKey(tempNums)
#                 if valid:
#                     numbers = []
#                     append = True
#                     client_sock.send("1")
#                     print("Send true.")
#                     currentLogIn.validBTKey = True
#                 else:
#                     numbers = []
#                     append = True
#                     client_sock.send("0")
#                     print("Send false.")
#                     currentLogIn.validBTKey = False
#
#     except IOError as e:
#         print(e)
#
#     print("Closed.")
#     LOCK = True
#
#     client_sock.close()
#     server_sock.close()
#     print("all done")
#
# validBTKey = False
# def checkForWhenBTKeyIsValid(self):
#     while not validBTKey:
#         time.sleep(1)
#     print("VALID KEYYYY")
#     self.parent.current = "main"
#
# BTthread = threading.Thread(target=runServ, args=())
# #BTthread.start()
# checkBTthread = threading.Thread(target=checkForWhenBTKeyIsValid, daemon=True)
# #checkBTthread.start()
# if useBT:
#     BTthread.start()
#     checkBTthread.start()

def runUI():
    global ui
    ui = uiApp()
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
        self.size = self.getFileSize()
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
        noPath = hexDir.replace(self.outerScreen.path, "")
        noPath = noPath.split(fileSep)
        for i in range(len(noPath)):
            noPath[i] = aesFName.decryptFileName(self.outerScreen.key, noPath[i])

        return fileSep.join(noPath)

    def getFileSize(self, recurse=True):
        if self.isDir:
            if recurse:
                self.outerScreen.totalSize = 0
                self.outerScreen.recursiveSize(self.hexPath)
                size = self.outerScreen.getGoodUnit(self.outerScreen.totalSize)
                if size == 0:
                    return " -"
                else:
                    return size
            else:
                return " -"
        else:
            try:
                size = self.outerScreen.getGoodUnit(os.path.getsize(self.hexPath))
                if size == 0:
                    return " -"
                else:
                    return size
            except Exception as e:
                print(e, "couldn't get size.")
                return " -"


class LoginScreen(Screen, FloatLayout):
    globalKey = StringProperty('')

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

    def startBTServer(self):
        lock = self.runServ()
        if lock == True:
            print("LOCK")
        return "done"

    def checkValid(self):   #Bound to checkbutton
        if len(self.lockList) > 0:
            print("UNLOCK")
            return True
        return False

    def findFile(self, dir):
        fs = os.listdir(dir)
        print(dir)
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

    def passToTerm(self, key, d):
        if sys.platform.startswith("win32"):
            progname = "AESWin"
        else:
            progname = "AES"
        goproc = Popen(startDir+progname, stdin=PIPE, stdout=PIPE)
        out, err = goproc.communicate(("test, "+d+", 0, ").encode()+key.encode())
        #print(id(key), d, "Key, D")
        #success = os.system("./AES test '"+key+"' '"+d+"' '0'") #Passes parameters to compiled go AES.
        #print(out, err, "OUTPUT OF PIPE")
        return out

    def getIfValidKey(self, inputKey):
        if len(os.listdir(sharedPath)) != 0:
            self.decryptTestFile = ""
            self.count = 0
            self.findFile(sharedPath)
            print("file", self.decryptTestFile)
            print(self.decryptTestFile, "File chosen.")
            diditwork = self.passToTerm(inputKey, self.decryptTestFile)
            #print(diditwork)
            if diditwork == b"-Valid-\n": #if error code is 0 then it worked, as in aes.go I added a panic() if it was invalid
                return True
            else:
                return False
        else:
            return True

    def checkKey(self, inputKey):
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

    def needToSetKey(self):
        if len(os.listdir(sharedPath)) == 0:
            return "Input New Key (Write this down if you have to)"
        else:
            return "Input Key"



    ##BT attempt##
    # globalKey = StringProperty("")
    #
    # def __init__(self, **kwargs):
    #     super(LoginScreen, self).__init__(**kwargs)
    #
    #
    # def getWelcomeText(self):
    #     if useBT:
    #         return "Connect via bluetooth."
    #     else:
    #         return "Enter the key below:"
    #
    # def findFile(self, dir):
    #     fs = os.listdir(dir)
    #     print(dir)
    #     for item in fs:
    #         if os.path.isdir(dir+item+fileSep):
    #             if self.count == 0:
    #                 self.findFile(dir+item+fileSep)
    #             else:
    #                 return
    #         else:
    #             self.decryptTestFile = dir+item
    #             self.count += 1
    #             return
    #
    # def passToPipe(self, key, d):
    #     goproc = Popen(startDir+"AES", stdin=PIPE, stdout=PIPE)
    #     out, err = goproc.communicate(("test, "+d+", 0, ").encode()+key.encode())
    #     #print(id(key), d, "Key, D")
    #     #success = os.system("./AES test '"+key+"' '"+d+"' '0'") #Passes parameters to compiled go AES.
    #     print(out, err, "OUTPUT OF PIPE")
    #     return out
    #
    #
    # def getIfValidKey(self, inputKey):
    #     if len(os.listdir(sharedPath)) != 0:
    #         self.decryptTestFile = ""
    #         self.count = 0
    #         self.findFile(sharedPath)
    #         print("file", self.decryptTestFile)
    #         print(self.decryptTestFile, "File chosen.")
    #         diditwork = self.passToPipe(inputKey, self.decryptTestFile)
    #         print(diditwork)
    #         if diditwork == b"-Valid-\n": #if error code is 0 then it worked, as in aes.go I added a panic() if it was invalid
    #             return True
    #         else:
    #             return False
    #     else:
    #         return True
    #
    # def checkKey(self, inputKey):
    #     if len(inputKey) > 16:
    #         pop = Popup(title="Invalid", content=Label(text="Invalid key, longer than\n 16 characters."), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4))
    #         pop.open()
    #         return "Login"
    #     else:
    #         inputKey = SHA.getSHA128of16(inputKey)
    #         key = " ".join(str(i) for i in inputKey)
    #         print(key, "KEYYY")
    #         valid = self.getIfValidKey(key)
    #         if valid:
    #             #self.ids.keyInput.text = "" #reset key input if valid
    #             self.globalKey = key
    #             return "main"
    #         else:
    #             pop = Popup(title="Invalid", content=Label(text="Invalid key."), pos_hint={"x_center": .5, "y_center": .5}, size_hint=(.4, .4))
    #             pop.open()
    #             return "Login"
    #
    # # def keyValidated(self):
    # #     print(self.validBTKey, "validBTKey")
    # #     if self.validBTKey:
    # #         return "main"
    # #     else:
    # #         return "Login"
    #
    # def needToSetKey(self):
    #     if len(os.listdir(sharedPath)) == 0:
    #         return "Input New Key (Write this down if you have to)"
    #     else:
    #         return "Input Key"
    #

    # def lockThreadFunc(self):
    #     while len(self.lockList) == 0:
    #         pass
    #     self.unlocc = True
    #     print("UNLOCK")
    #     return "done"




class MainScreen(Screen, FloatLayout):

    class listButton(Button):

        def __init__(self, mainScreen, fileObj, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.fileObj = fileObj


    class searchResultButton(Button):

        def __init__(self, mainScreen, fullDir, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.fullDir = fullDir

    class SettingsPop(Popup):

        def __init__(self, mainScreen, **kwargs):
            self.outerScreen = mainScreen
            super(Popup, self).__init__(**kwargs)

        def editConfLoc(self, term, dir):
            for line in fileinput.input(startDir+"config.cfg", inplace=1):
                if term in line:
                    line = line.replace(line, term+dir+"\n")
                sys.stdout.write(line)

        def changeVaultLoc(self, inp):
            if inp == "":
                pass
            else:
                if os.path.exists(inp):
                    if os.path.isdir(inp):
                        self.editConfLoc("vaultDir:", inp)
                        done = Popup(title="Done", content=self.outerScreen.infoLabel(text="Changed Vault Location to:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                        self.outerScreen.path = inp
                        self.outerScreen.currentDir = inp
                        self.outerScreen.resetButtons()
                        done.open()
                else:
                    try:
                        os.makedirs(inp)
                    except FileNotFoundError:
                        warn = Popup(title="Invalid", content=self.outerScreen.infoLabel(text="Directory not valid:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                        warn.open()
                    except PermissionError:
                        warn = Popup(title="Invalid", content=self.outerScreen.infoLabel(text="Can't make a folder here:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                        warn.open()
                    else:
                        self.editConfLoc("vaultDir:", inp)
                        done = Popup(title="Done", content=self.outerScreen.infoLabel(text="Changed Vault Location to:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                        self.outerScreen.path = inp
                        self.outerScreen.currentDir = inp
                        self.outerScreen.resetButtons()
                        done.open()


    class infoButton(Button):

        def __init__(self, mainScreen, fileReference, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.fileReference = fileReference

    class infoLabel(Label):
        pass

    class deleteButton(Button):

        def __init__(self, mainScreen, fileDir, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.fileDir = fileDir

    class nameSortButton(Button):

        def __init__(self, mainScreen, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen

        def changeSortOrder(self):
            if self.outerScreen.ascending:
                self.outerScreen.ascending = False
                self.outerScreen.resetButtons()
            else:
                self.outerScreen.ascending = True
                self.outerScreen.resetButtons()

    class addFileScreen(Popup):

        def __init__(self, mainScreen, **kwargs):
            super(Popup, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.layout = FloatLayout()

        class ConfirmationPopup(Popup):

            def __init__(self, fileScreen, input, **kwargs):
                super(Popup, self).__init__(**kwargs)
                self.fileScreen = fileScreen
                self.inputText = input


        def checkIfSure(self, input):
            sure = self.ConfirmationPopup(self, input)
            sure.open()

        # def reAddSubmit(self):
        #     try:
        #         self.add_widget(self.submitDirs)
        #     except WidgetException:
        #         print("Submit button already there.")


    key = StringProperty('')

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.sizeCount = 0
        self.ascending = True
        self.addFile = 0
        self.key = ""
        self.currentDecList = []
        #self.key = StringProperty('')
        #key = "1234" #Super secret secure key for testing (before bluetooth is added)
        Window.bind(on_dropfile=self.onFileDrop)
        self.path = sharedPath
        self.assetsPath = sharedAssets
        self.currentDir = self.path
        print(self.currentDir, "CURRENT DIR")
        self.scroll = ScrollView(size_hint=(.9, .79), pos_hint={"x": .005, "y": 0})
        self.waitThread = threading.Thread(target=self.waitForKey, daemon=True)
        self.waitThread.start()



    def __repr__(self):
        return "MainScreen"

    def waitForKey(self):   #Waits for the key so that file names can be shown (as they need to be decrypted)
        while self.key == "":
            time.sleep(0.1)

        print("CHANGED TO MAIN")
        return self.createButtons(self.List(self.currentDir))

    def getGoodUnit(self, bytes):
        if bytes == " -":
            return " -"
        else:
            divCount = 0
            divisions = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB", 5: "PB"}
            while bytes > 1000:
                bytes = bytes/1000
                divCount += 1

            return ("%.2f" % bytes) + divisions[divCount]

    def getSortedFoldersAndFiles(self, fileObjects, inverse=False):
        #print(fileObjects, "ARRAY GIVEN getSortedFoldersAndFiles")
        folders = []
        files = []
        for i in range(len(fileObjects)):
            if fileObjects[i].isDir:
                folders.append(fileObjects[i])
            else:
                files.append(fileObjects[i])

        #print(files, folders, "arrays")

        if inverse:
            fol = self.quickSortAlph(folders)
            fil = self.quickSortAlph(files)
            foldersSort = fol[::-1]
            filesSort = fil[::-1]
        else:
            foldersSort = self.quickSortAlph(folders)
            filesSort = self.quickSortAlph(files)
        return foldersSort+filesSort


##########Getting File Information##########
    def recursiveSize(self, f, encrypt=False):
        fs = os.listdir(f)
        #print(f)
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
                except PermissionError:
                    pass


    # def getFileSize(self, item, recurse=True):
    #     item = aesFName.encryptFileName(self.key, item)
    #     if os.path.isdir(self.currentDir+item):
    #         if recurse:
    #             self.totalSize = 0
    #             self.recursiveSize(self.currentDir+item)
    #             size = self.getGoodUnit(self.totalSize)
    #             if size == 0:
    #                 return " -"
    #             else:
    #                 return size
    #         else:
    #             return " -"
    #     else:
    #         try:
    #             size = self.getGoodUnit(os.path.getsize(self.currentDir+item))
    #             if size == 0:
    #                 return " -"
    #             else:
    #                 return size
    #         except Exception as e:
    #             print(e, "couldn't get size.")
    #             return " -"

    # def getGoodUnit(self, bytes):
    #     if bytes == " -":
    #         return " -"
    #     else:
    #         divCount = 0
    #         divisions = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB", 5: "PB"}
    #         while bytes > 1000:
    #             bytes = bytes/1000
    #             divCount += 1

    #         return ("%.2f" % bytes) + divisions[divCount]

    # def deleteFile(self, location):
    #     if os.path.exists(location):
    #         if os.path.isdir(location):
    #             shutil.rmtree(location)
    #         else:
    #             os.remove(location)

############################################

#######Button Creation and button functions#######

    def createButtons(self, fileObjects, sort=True):
        self.currentList = []
        if self.ascending:
            if sort:
                sortedArray = self.getSortedFoldersAndFiles(fileObjects)
            btn = self.nameSortButton(self, text="^")
            self.add_widget(btn)
        else:
            if sort:
                sortedArray = self.getSortedFoldersAndFiles(fileObjects, True)
            btn = self.nameSortButton(self, text="V")
            self.add_widget(btn)

        self.grid = GridLayout(cols=3, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        if sort:
            self.currentList = sortedArray
            for item in sortedArray:
                btn = self.listButton(self, item, text=("    "+item.name), height=30, halign="left", valign="middle")
                btn.bind(size=btn.setter("text_size"))
                info = self.infoButton(self, item, text=(" INFO"), size_hint=(.05, 1), halign="left", valign="middle")
                info.bind(size=info.setter("text_size"))
                fileS = Label(text=" "+str(item.size), size_hint=(.1, 1), halign="left", valign="middle")
                fileS.bind(size=fileS.setter("text_size"))
                self.grid.add_widget(btn)
                self.grid.add_widget(info)
                self.grid.add_widget(fileS)
            self.scroll = ScrollView(size_hint=(.9, .79), pos_hint={"x": .005, "y": 0})
            self.scroll.add_widget(self.grid)
            self.add_widget(self.scroll)
        else:
            self.currentList = fileObjects
            for item in fileObjects:
                btn = self.listButton(self, item, text=("    "+item.name), height=30, halign="left", valign="middle")
                btn.bind(size=btn.setter("text_size"))
                info = self.infoButton(self, item, text=(" INFO"), size_hint=(.05, 1), halign="left", valign="middle")
                info.bind(size=info.setter("text_size"))
                fileS = Label(text=" "+str(item.size), size_hint=(.1, 1), halign="left", valign="middle")
                fileS.bind(size=fileS.setter("text_size"))
                self.grid.add_widget(btn)
                self.grid.add_widget(info)
                self.grid.add_widget(fileS)
            self.scroll = ScrollView(size_hint=(.9, .79), pos_hint={"x": .005, "y": 0})
            self.scroll.add_widget(self.grid)
            self.add_widget(self.scroll)

    def removeButtons(self):
        self.grid = 0
        self.remove_widget(self.scroll)
        self.scroll = 0


    def getFileNameFromText(self, itemName):
        return itemName[4:]


    def traverseButton(self, fileObj):
        print("traversing:", fileObj)
        print(fileObj.isDir, "ISDIR n baib", fileObj.name, "Name")
        print(self.currentDir, "Current dir")
        if fileObj.isDir:
            self.currentDir = fileObj.hexPath
            currentDirShare = self.currentDir
            self.resetButtons()
        else:
            self.decrypt(fileObj)

    def deleteFile(self, location):
        if os.path.exists(location):
            if os.path.isdir(location):
                shutil.rmtree(location)
            else:
                os.remove(location)

    def getFileInfo(self, fileObj):
        fileViewDir = fileObj.path.replace(self.path, "")
        print(fileViewDir, "FILE VIEW Dir")
        #print(fileViewDir, "fileViewDir")

        #print(fileFullDir, "FULL")
        internalView = ScrollView()
        self.infoPopup = Popup(title="File Information", content=internalView, pos_hint={"center_x": .5, "center_y": .5}, size_hint=(.8, .4))
        internalLayout = GridLayout(cols=2, size_hint_y=None)

        internalLayout.add_widget(self.infoLabel(text="File Name:", size_hint_x=.2, halign="left", valign="middle"))
        internalLayout.add_widget(self.infoLabel(text=fileObj.name, halign="left", valign="middle"))

        internalLayout.add_widget(self.infoLabel(text="Current Location:", size_hint_x=.2, halign="left", valign="middle"))
        internalLayout.add_widget(self.infoLabel(text="/Vault/"+fileViewDir, halign="left", valign="middle"))


        internalLayout.add_widget(self.infoLabel(text="Size:", size_hint_x=.2, halign="left", valign="middle"))
        internalLayout.add_widget(self.infoLabel(text=str(fileObj.size), halign="left", valign="middle"))

        internalLayout.add_widget(self.infoLabel(text=str(fileObj.size), halign="left", valign="middle"))

        delBtn = Button(text="Delete", size_hint_x=.2)
        delBtn.bind(on_press=self.deleteFile)
        #delBtn.bind(on_press=self.deleteFile, args=(hexDir))
        internalLayout.add_widget(delBtn)

        internalView.add_widget(internalLayout)
        self.infoPopup.open()


    def deleteFile(self, fileObj):   #Can't pass more than self in bind
        print("INPUTS TO DELET", fileObj)
        print("Deleting,", fileObj.hexPath)
        if os.path.exists(fileObj.hexPath):
            if fileObj.isDir:
                shutil.rmtree(fileObj.hexPath)
            else:
                os.remove(fileObj.hexPath)
            self.resetButtons()
            self.infoPopup.dismiss()
        else:
            raise FileNotFoundError(fileObj.hexPath, "Not a file, can't delete.")

    def goBackFolder(self):
        if self.currentDir != self.path:
            self.currentDir = self.getPathBack()
            currentDirShare = self.currentDir
            self.resetButtons()
        else:
            print("Can't go further up.")

    def getPathForButton(self, item):
        return self.assetsPath+item

    def resetButtons(self): #Goes back to self.currentDir, different to search.
        self.removeButtons()
        self.createButtons(self.List(self.currentDir))

    def refreshButtons(self):
        self.removeButtons()
        self.createButtons(self.currentList, False)


####File Handling####

    def List(self, dir):
        #print(dir, "LIST DIR")
        fs = os.listdir(dir)
        count = 0
        listOfFiles = []
        for item in fs:
            if os.path.isdir(dir+item):
                listOfFiles.append(File(self, dir+item, item, True))
        for item in fs:
            if not os.path.isdir(dir+item):
                listOfFiles.append(File(self, dir+item, item))
        return listOfFiles

    def getPathBack(self):
        tempDir = self.currentDir.split(fileSep)
        print(tempDir, "TEMPDIR")
        del tempDir[len(tempDir)-2]
        tempDir = fileSep.join(tempDir)
        return tempDir

###########Sorts + Searches############
    def compareStrings(self, fileObj, string2):     #returns True if string1 < string2 alphabetically, and "Found" if string1 == string2
        count = 0
        while not (count >= len(fileObj.name) or count >= len(string2)):
            if ord(string2[count].lower()) < ord(fileObj.name[count].lower()):
                return True
            elif ord(string2[count].lower()) > ord(fileObj.name[count].lower()):
                return False
            else:
                if ord(string2[count]) < ord(fileObj.name[count]):    #if the same name but with capitals - e.g (Usb Backup) and (usb backup)
                    return True
                elif ord(string2[count]) > ord(fileObj.name[count]):
                    return False
                else:
                    if string2 == fileObj.name:
                        return "Found"
                    else:
                        count += 1
        if len(fileObj.name) > len(string2):
            return True
        elif len(fileObj.name) < len(string2):
            return False
        else:
            raise ValueError("Two strings are the same in compareStrings.")
            print(string2, fileObj.name, len(string2), len(fileObj.name))


    def quickSortAlph(self, myList, fileObjects=True):
        if len(myList) > 1:
            left = []
            right = []  #Make seperate l+r lists, and add on at the end.
            middle = []
            pivot = myList[int(len(myList)/2)]
            for item in myList:
                if fileObjects:
                    leftSide = self.compareStrings(pivot, item.name)
                else:
                    leftSide = self.compareStrings(pivot, item)
                if leftSide == "Found":
                    middle.append(item)
                elif leftSide:
                    left.append(item)
                elif not leftSide:
                    right.append(item)

            return self.quickSortAlph(left)+middle+self.quickSortAlph(right)
        else:
            return myList


    def quickSortNums(self, myList):
        if len(myList) > 1:
            left = []
            right = []  #Make seperate l+r lists, and add on at the end.
            middle = []
            pivot = myList[int(len(myList)/2)]
            for i in myList:
                if i < pivot:
                    left.append(i)
                elif i > pivot:
                    right.append(i)
                else:
                    middle.append(i)
            return self.quickSortByLength(left)+middle+self.quickSortByLength(right)
        else:
            return myList


    def quickSortTuples(self, tuples):    # def encrypt(self, key, dir, outputDir):
    #     encryptThread = multiprocessing.Process(target=AES.encryptFile, args=(key, dir, outputDir))
    #     encryptThread.start()
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
        files = self.List(dirName) #Updates currentX variables
        for fileObj in files:
            loc = fileObj.name.find(item)

            if fileObj.name == item:
                self.searchResults = [fileObj] + self.searchResults
                self.removeButtons()
                self.createButtons(self.searchResults)
            elif loc != -1:
                self.unsorted.append((loc, fileObj))   #Adds loc found in word, so that it can be sorted by where it is found
                #print(self.unsorted)

            if fileObj.isDir and searchRecursively:
                #print("Isdir:", fileObj.hexPath)
                self.findAndSortCore(fileObj.hexPath, item)


    def findAndSort(self, item):
        self.unsorted = []

        self.findAndSortCore(self.currentDir, item)

        if len(self.unsorted) > 0:
            sorted = self.quickSortTuples(self.unsorted)
            for i in sorted:
                self.searchResults.append(i[1])
            self.removeButtons()
            self.createButtons(self.searchResults, False)

    # def traverseFileTree(self, f):
    #     fs = os.listdir(f)
    #     for item in fs:
    #         if os.path.isdir(f+item):
    #             try:
    #                 self.traverseFileTree(f+item+"/")
    #             except OSError:
    #                 pass
    #         else:
    #             if os.path.islink(f+item) == False:
    #                 self.findAndSort()


    def searchThread(self, item):
        self.findAndSort(item)
        return "Done"


##################################


####Progress Bar Information####

    def values(self, st):
        values = shutil.disk_usage(self.path)
        if st:
            return self.getGoodUnit(int(values[1]))+" / " + self.getGoodUnit(int(values[0])) + " used."
        else:
            return [values[0], values[1]]

################################

####Search Bar functions####

    # def printStuff(self, val): #test
    #     print(val)

    def searchForItem(self, item):
        self.resetButtons()
        self.searchResults = []
        self.t = threading.Thread(target=self.searchThread, args=(item,), daemon=True)
        self.t.start()

############################

######Encryption Stuff + opening decrypted files######
    def passToPipe(self, type, d, targetLoc, newName=None):
        print("PIPE INPUTS:", self, type, d, targetLoc, newName)
        if sys.platform.startswith("win32"):
            progname = "AESWin"
        else:
            progname = "AES"

        tempDir = d.split(fileSep)
        fileName = tempDir[len(tempDir)-1]
        print("File name given:", fileName)
        if type == "y":
            ##need to encrypt file name too if enc

            #replace file name with new hex
            tempTargetLoc = targetLoc.split(fileSep)
            tempTargetLoc[len(tempTargetLoc)-1] = aesFName.encryptFileName(self.key, fileName)
            targetLoc = fileSep.join(tempTargetLoc)
            print("New targetLoc", targetLoc)

        elif type == "n":   #Need to decrypt file name if decrypting
            tempTargetLoc = targetLoc.split(fileSep)
            tempTargetLoc[len(tempTargetLoc)-1] = newName #Stops you from doing it twice in decrypt()
            targetLoc = fileSep.join(tempTargetLoc)
            print("New targetLoc", targetLoc)


        goproc = Popen(startDir+progname, stdin=PIPE, stdout=PIPE)
        out, err = goproc.communicate((type+", "+d+", "+targetLoc+", "+self.key).encode()) #dont use d for fileNames, use targetloc for file name and self.key for self.key
        if err != None:
            raise ValueError("key not valid.")
        return out

    def encDecTerminal(self, type, d, targetLoc, newName=None):
        print("encDecTerminal inp:", type, d, targetLoc, newName)
        self.encryptProcess = threading.Thread(target=self.passToPipe, args=(type, d, targetLoc, newName,))
        self.encryptProcess.start()
        self.encryptProcess.join()
        #pop.dismiss()

    def openFile(self, location, startLoc):
        if sys.platform.startswith("win32"):
            locationTemp = location.split("\\")
            location = "/".join(locationTemp) #Windows actually accepts forward slashes in terminal
            command = "cmd /k start "+'"" '+'"'+location+'"'+" /D"
        else:
            command = "xdg-open "+'"'+location+'"'      #Quotation marks for if the dir has spaces in it
        #print("Command:", command)
        os.system(command)#Using the same for both instead of os.startfile because os.startfile doesn't wait for file to close
        self.encDecTerminal("y", location, startLoc)


    def onFileDrop(self, window, file_path):  #Drag + drop files
        self.checkCanEncrypt(file_path.decode())
        self.resetButtons()
        return "Done"

    def decrypt(self, fileObj):
        if not os.path.isdir(osTemp+"FileMate"+fileSep):
            os.makedirs(osTemp+"FileMate"+fileSep)
        fileLoc = osTemp+"FileMate"+fileSep+fileObj.name
        if os.path.exists(fileLoc):
            self.openFileThread = threading.Thread(target=self.openFile, args=(fileObj,))
            self.openFileThread.start()
        else:
            self.encDecTerminal("n", fileObj.path, fileLoc, fileObj.name)

            self.openFileThread = threading.Thread(target=self.openFile, args=(fileLoc, fileObj.path))
            self.openFileThread.start()

        #os.startfile("/tmp/"+fileName)
        #subprocess.call(["xdg-open", file])

    def checkDirExists(self, dir):
        if os.path.exists(dir):
            return True

        else:
            self.popup = Popup(title="Invalid", content=Label(text=dir+" - Not a valid directory."), pos_hint={"center_x": .5, "center_y": .5}, size_hint=(.4, .4))
            self.popup.open()
            return False


    def encryptDir(self, d, targetLoc):
        print(targetLoc, "LINE 1008 targetLoc encryptDir")

        fs = os.listdir(d)
        #print(d, targetLoc)
        targetLoc = targetLoc.split(fileSep)
        targetLoc[len(targetLoc)-1] = aesFName.encryptFileName(self.key, targetLoc[len(targetLoc)-1])
        targetLoc = fileSep.join(targetLoc)
        print("NEW TARGET LOC encryptDir", targetLoc)
        for item in fs:
            if os.path.isdir(d+item):
                try:
                    self.encryptDir(d+item+fileSep, targetLoc+fileSep+item)
                except OSError:
                    pass
            else:
                try:
                    #print(d+item, targetLoc+"/"+item, "AAAAAAAAAAAAAAAAAAAAAA")
                    self.createFolders(targetLoc+fileSep)
                    self.encDecTerminal("y", d+item, targetLoc+fileSep+item)
                except PermissionError:
                    pass

    def checkCanEncrypt(self, inp):
        if "--" in inp:
            #print("--")
            inp = inp.split("--")
            for d in inp:
                exists = self.checkDirExists(d)
                if exists:
                    if os.path.isdir(d):
                        if d[len(d)-1] != fileSep:
                            d += fileSep
                        dSplit = d.split(fileSep)
                        # print(d, "ISDIR")
                        self.encryptDir(d, self.currentDir+dSplit[len(dSplit)-2]+fileSep)
                    else:
                        dSplit = d.split(fileSep)
                        self.encDecTerminal("y", d, self.currentDir+dSplit[len(dSplit)-1])



        else:
            exists = self.checkDirExists(inp)
            if exists:
                if os.path.isdir(inp):
                    if inp[len(inp)-1] != fileSep:
                        inp += fileSep
                    inpSplit = inp.split(fileSep)
                    # print(inp, "ISDIR")
                    #print(self.outerScreen.currentDir+inpSplit[len(inpSplit)-2]+"/")
                    self.encryptDir(inp, self.currentDir+inpSplit[len(inpSplit)-2])
                else:
                    inpSplit = inp.split(fileSep)
                    self.encDecTerminal("y", inp, self.currentDir+inpSplit[len(inpSplit)-1])


        self.resetButtons()


    def createFolders(self, targetLoc):
        if not os.path.exists(targetLoc):
            os.makedirs(targetLoc)


    def clearUpTempFiles(self):
        print("Deleting temp files.")
        try:
            shutil.rmtree(osTemp+"FileMate"+fileSep)
        except:
            print("No temp files.")
###########################



class ScreenManagement(ScreenManager):
    # LoginScreen = ObjectProperty(None)
    # MainScreen = ObjectProperty(None)
    # addFileScreen = ObjectProperty(None)
    def update(self, dt):
        self.current_screen.update(dt)


presentation = Builder.load_file(os.path.dirname(os.path.realpath(__file__))+fileSep+"main.kv")

class uiApp(App):

    def build(self):
        return presentation


if __name__ == "__main__":
    runUI()

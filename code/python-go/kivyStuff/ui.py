import os
import sys
import shutil
import threading
import fileinput
from tempfile import gettempdir
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
print(tempDir, "TEMP DIR")
for i in range(2):
    del tempDir[len(tempDir)-2]

tempDir = fileSep.join(tempDir)
tempDir += "assets"+fileSep+"exports"+fileSep
sharedAssets = tempDir

configFile = None
try:
    home = os.listdir(os.path.expanduser("~/.config/FileMate/"))
except:
    print("No config file in .config")
else:
    if "config" in home:
        configFile = open(os.path.expanduser("~/.config/FileMate/config"), "r")
        config = os.path.expanduser("~/.config/FileMate/config")

if configFile == None:
    try:
        configFile = open(startDir+"config.cfg", "r")
        config = startDir+"config.cfg"
    except Exception as e:
        print(e, "Config file not found.")
        raise FildNotFoundError("No config file found. Refer to the README if you need help.")

for line in configFile:
    print(line)
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
        print(lineSplit[1], "Bluetooth config adb ahdhinaadsajdaujdahhdahdhuhyu")
        if lineSplit[1] == "True":
            useBT = True
        elif lineSplit[1] == "False":
            useBT = False
        else:
            raise ValueError("Bluetooth not configured correctly in config file: Not True or False.")

configFile.close()

# try:
#     from bluetooth import *
#     a = get_acl_conn_handle()


# except Exception as e:
#     print(e, "Reverting to no-bluetooth.")
#     useBT = False
# else:
#     print("Worked")


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
                if size == 0:
                    return " -"
                else:
                    return size
            else:
                return " -"
        else:
            try:
                size = os.path.getsize(self.hexPath)
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


    def findFile(self, dir):
        fs = os.listdir(dir)
        #print(dir)
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
            #print("file", self.decryptTestFile)
            #print(self.decryptTestFile, "File chosen.")
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

    def needToSetKey(self):
        if len(os.listdir(sharedPath)) == 0:
            return "Input New Key (Write this down if you have to)"
        else:
            return "Input Key"



###Bluetooth stuff### needs to be accessable by both screens.
if useBT:   #Some of this stuff doesn't need to be loaded unless bt is used.
    from bluetooth import *


    class LoginScreenBT(LoginScreen, Screen, FloatLayout):

        def __init__(self, **kwargs):
            super(LoginScreenBT, self).__init__(**kwargs)
            self.validBTKey = False
            #print(useBT, "USE BT ADAHDHAHDAHYHYU")

        def on_enter(self):
            Clock.schedule_once(self.startSrv, 0.7)


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
            self.runServLogin()

        def runServLogin(self):
            serverSock = BluetoothSocket( RFCOMM )
            serverSock.bind(("",PORT_ANY))
            serverSock.listen(1)

            port = serverSock.getsockname()[1]

            uuid = "80677070-a2f5-11e8-b568-0800200c9a66"

            advertise_service(serverSock, "FileMateServer",
                              service_id = uuid,
                              service_classes = [ uuid, SERIAL_PORT_CLASS ],
                              profiles = [ SERIAL_PORT_PROFILE ],)

            print("[BT]: Waiting for connection on RFCOMM channel", port)

            clientSock, clientInfo = serverSock.accept()
            print("[BT]: Accepted connection from ", clientInfo)

            numbers = []
            append = True

            try:
                while True:
                    data = clientSock.recv(1024)
                    if len(data) == 0: break
                    print("[BT]: Received data.")
                    if append:
                        numbers.append(str(data, "utf-8"))
                    if b"~" in data:    ##End of message
                        append = False
                        tempNums = "".join(numbers)
                        #time.sleep(1)
                        tempNums = tempNums.replace("#", "")
                        tempNums = tempNums.replace("~", "")
                        valid = self.checkKey(tempNums)
                        if valid:
                            numbers = []
                            append = True
                            clientSock.send("1")
                            print("[BT]: Send true.")
                            self.validBTKey = True
                            clientSock.close()
                            serverSock.close()
                            print("[BT]: Shutting down for mainscreen check.")
                            self.manager.current = "main"
                        else:
                            numbers = []
                            append = True
                            clientSock.send("0")
                            print("[BT]: Send false.")
                            self.validBTKey = False

            except IOError as e:
                print(e)

            print("Closed.")

            clientSock.close()
            serverSock.close()
            print("all done")




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
            with open(config, "r") as conf:
                confContent = conf.readlines()

            for i in range(len(confContent)):
                if term in confContent[i]:
                    a = confContent[i].split("--")
                    a[1] = dir+"\n"
                    confContent[i] = "--".join(a)
                    #print(confContent[i], "Done")

            #print(confContent)
            with open(config, "w") as confW:
                confW.writelines(confContent)



        def dirInputValid(self, inp):
            valid = (inp[0] == fileSep) and ("\n" not in inp)
            inp = inp.split(fileSep)
            focusIsSlash = False
            for item in inp:
                if item == "":
                    if focusIsSlash:
                        valid = False
                    focusIsSlash = True
                else:
                    focusIsSlash = False
            return valid

        def changeVaultLoc(self, inp):
            if inp == "":
                pass
            else:
                if self.dirInputValid(inp):
                    if os.path.exists(inp):
                        if os.path.isdir(inp):
                            if inp[len(inp)-1] != fileSep:
                                inp += fileSep
                            self.editConfLoc("vaultDir--", inp)
                            print("EDITING")
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
                        except Exception as e:
                            print(e)
                            warn = Popup(title="Invalid", content=self.outerScreen.infoLabel(text="Can't make a folder here:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                            warn.open()
                        else:
                            if inp[len(inp)-1] != fileSep:
                                inp += fileSep
                            self.editConfLoc("vaultDir--", inp)
                            done = Popup(title="Done", content=self.outerScreen.infoLabel(text="Changed Vault Location to:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                            self.outerScreen.path = inp
                            self.outerScreen.currentDir = inp
                            self.outerScreen.resetButtons()
                            done.open()
                else:
                    warn = Popup(title="Invalid", content=self.outerScreen.infoLabel(text="Directory not valid."), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                    warn.open()

    class infoButton(Button):

        def __init__(self, mainScreen, fileReference, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.fileReference = fileReference

    class infoLabel(Label):
        pass

    class deleteButton(Button):

        def __init__(self, mainScreen, fileObj, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.fileObj = fileObj

    class nameSortButton(Button):

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

    class sizeSortButton(Button):

        def __init__(self, mainScreen, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen
            self.ascending = True

        def quickSortSize(self, fileObjects):
            if len(fileObjects) > 1:
                left = []
                right = []  #Make seperate l+r lists, and add on at the end.
                middle = []
                pivot = fileObjects[int(len(fileObjects)/2)]
                for i in fileObjects:
                    if i.rawSize < pivot.rawSize:
                        left.append(i)
                    elif i.rawSize > pivot.rawSize:
                        right.append(i)
                    else:
                        middle.append(i)
                return self.quickSortSize(left)+middle+self.quickSortSize(right)
            else:
                return fileObjects

        def sortBySize(self, asc=True):
            sortList = self.quickSortSize(self.outerScreen.currentList)
            if not asc:
                sortList = sortList[::-1]

            self.outerScreen.removeButtons()
            self.outerScreen.createButtons(sortList, False)

        def changeSizeOrder(self):
            self.ascending = not self.ascending
            if self.ascending:
                self.text = "v"
            else:
                self.text = "^"

            #print(self.ascending, "Self.ascending")
            self.sortBySize(self.ascending)

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
        self.locked = True
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
        #self.waitThread = threading.Thread(target=self.waitForKey, daemon=True)
        #self.waitThread.start() #Wait for the key so that the file names can be decrypted.


    def __repr__(self):
        return "MainScreen"

    def lock(self):
        self.clearUpTempFiles()
        try:
            self.clientSock.close()
            self.serverSock.close()
        except Exception as e:
            print(e, "Already closed? Shouldn't be")
        self.manager.current = "Login"

    def runServMain(self):
        self.serverSock = BluetoothSocket( RFCOMM )
        self.serverSock.bind(("",PORT_ANY))
        self.serverSock.listen(1)

        port = self.serverSock.getsockname()[1]

        uuid = "80677070-a2f5-11e8-b568-0800200c9a66" #Random UUID from https://www.famkruithof.net/uuid/uuidgen

        advertise_service( self.serverSock, "FileMateServer",
                           service_id = uuid,
                           service_classes = [ uuid, SERIAL_PORT_CLASS ],
                           profiles = [ SERIAL_PORT_PROFILE ],)

        print("[BT]: Waiting for connection on RFCOMM channel", port)

        self.clientSock, self.clientInfo = self.serverSock.accept()
        print("[BT]: Accepted connection from ", self.clientInfo)

        #Send current file list
        #clientSock.send(self.currentList)

        try:
            while self.manager.current == "main":
                data = self.clientSock.recv(1024)
                # print("Connection lost")
                # self.clientSock.close()
                # self.serverSock.close()
                # print("BT sockets closed.")
                # self.clearUpTempFiles()
                # return mainthread(self.changeToLogin())

        except IOError as e:
            print(e ,"Connection lost")
            self.clientSock.close()
            self.serverSock.close()
            print("BT sockets closed.")
            self.clearUpTempFiles()
            return mainthread(self.changeToLogin())

    # def checkServerStatus(self):
    #     while self.serverThread.is_alive() and self.manager.current == "main":
    #         print("Server is alive")
    #         time.sleep(0.1)
    #     self.serverThread.join(1)
    #     print("Locking...")
    #     self.clearUpTempFiles()
    #     return mainthread(self.changeToLogin())

    @mainthread
    def changeToLogin(self):    #Only used for checkServerStatus because you can only return a function or variable, and if i execute this within the thread then it causes a segmentation fault.
        self.manager.current = "Login"

    def startBT(self):
        self.serverThread = threading.Thread(target=self.runServMain, daemon=True)
        #self.serverStopped = threading.Event()
        #self.serverCheckThread = threading.Thread(target=self.checkServerStatus, daemon=True)
        self.serverThread.start()
        #self.serverCheckThread.start()

    def setupSortButtons(self):
        self.sortsGrid = GridLayout(cols=3, size_hint=(.9, .04), pos_hint={"x": .005, "y": .79})
        self.nameSort = self.nameSortButton(self, text="^", size_hint_x=6.66) #Not sure why it has to be the devil
        self.sizeSort = self.sizeSortButton(self)
        print("Re-drawn")
        self.sortsGrid.add_widget(self.nameSort)
        self.sortsGrid.add_widget(self.sizeSort)
        self.add_widget(self.sortsGrid)

    def on_enter(self):
        self.locked = False
        self.setupSortButtons()
        self.createButtons(self.List(self.currentDir))
        if useBT:
            self.startBT()

    ###Replaced with on_enter
    # def waitForKey(self):   #Waits for the key so that file names can be shown (as they need to be decrypted)
    #     while self.key == "":
    #         time.sleep(0.1)

    #     print("CHANGED TO MAIN")
    #     return self.createButtons(self.List(self.currentDir)), self.startBT()

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


############################################

#######Button Creation and button functions#######
    def createButtonsCore(self, array):
        self.currentList = array
        for item in array:
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

    def createButtons(self, fileObjects, sort=True):
        self.currentList = []
        if sort:
            sortedArray = self.getSortedFoldersAndFiles(fileObjects)

        self.grid = GridLayout(cols=3, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))

        if sort:
            self.createButtonsCore(sortedArray)
        else:
            self.createButtonsCore(fileObjects)

    def removeButtons(self):
        self.grid = 0
        try:
            self.remove_widget(self.scroll)
        except Exception as e:
            print(e, "Already removed?")
        self.scroll = 0


    def getFileNameFromText(self, itemName):
        return itemName[4:]


    def traverseButton(self, fileObj):
        #print("traversing:", fileObj)
        #print(fileObj.isDir, "ISDIR n baib", fileObj.name, "Name")
        #print(self.currentDir, "Current dir")
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

        delBtn = self.deleteButton(self, fileObj,text="Delete", size_hint_x=.2)
        #delBtn.bind(on_press=self.deleteFile, args=(hexDir))
        internalLayout.add_widget(delBtn)

        internalView.add_widget(internalLayout)
        self.infoPopup.open()


    def deleteFile(self, fileObj):   #Can't pass more than self in bind
        #print("INPUTS TO DELET", fileObj)
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
        self.nameSort.text = "^"
        self.sizeSort.text = ""
        self.createButtons(self.List(self.currentDir))

    def refreshButtons(self):
        self.removeButtons()
        self.createButtons(self.currentList, False)

    def goHome(self):
        self.removeButtons()
        self.nameSort.text = "^"
        self.sizeSort.text = ""
        self.currentDir = self.path
        self.createButtons(self.List(self.currentDir))


####File Handling####

    def List(self, dir):
        fs = os.listdir(dir)
        count = 0
        listOfFolders = []
        listOfFiles = []
        for item in fs:
            if os.path.isdir(dir+item):
                listOfFolders.append(File(self, dir+item, item, True))
            else:
                listOfFiles.append(File(self, dir+item, item))
        return listOfFolders+listOfFiles

    def getPathBack(self):
        tempDir = self.currentDir.split(fileSep)
        #print(tempDir, "TEMPDIR")
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


    def quickSortTuples(self, tuples):
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
        if sys.platform.startswith("win32"):
            progname = "AESWin.exe"
        else:
            progname = "AES"

        tempDir = d.split(fileSep)
        fileName = tempDir[len(tempDir)-1]
        if type == "y":
            #replace file name with new hex
            targetLoc = targetLoc.split(fileSep)
            targetLoc[len(targetLoc)-1] = aesFName.encryptFileName(self.key, fileName)
            targetLoc = fileSep.join(targetLoc)

        elif type == "n":   #Need to decrypt file name if decrypting
            targetLoc = targetLoc.split(fileSep)
            targetLoc[len(targetLoc)-1] = newName #Stops you from doing it twice in decrypt()
            targetLoc = fileSep.join(targetLoc)


        goproc = Popen(startDir+progname, stdin=PIPE, stdout=PIPE)
        out, err = goproc.communicate((type+", "+d+", "+targetLoc+", "+self.key).encode()) #dont use d for fileNames, use targetloc for file name and self.key for self.key
        if err != None:
            raise ValueError("Key not valid.")
        return out

    def encDecTerminal(self, type, d, targetLoc, newName=None):
        self.encPop = None

        if type == "y" or "n":
            if type == "y":
                popText = "Encrypting..."
            elif type == "n":
                popText = "Decrypting..."

            self.encPop = Popup(title="Please wait...", content=Label(text=popText), pos_hint={"center_x": .5, "center_y": .5}, size_hint=(.4, .4), auto_dismiss=False)
            self.encPop.open()

        self.encryptProcess = threading.Thread(target=self.passToPipe, args=(type, d, targetLoc, newName,), daemon=True)
        self.encryptProcess.start()
        self.encryptProcess.join()
        if self.encPop != None:
            self.encPop.dismiss()
            self.encPop = None

    def scheduleStart(self, dt): #Had to make to handle dt variable
        self.encryptProcess.start()
        self.encryptProcess.join()

    def openFile(self, location, startLoc):
        if sys.platform.startswith("win32"):
            location = location.split("\\")
            location = "/".join(location) #Windows actually accepts forward slashes in terminal
            command = "cmd /k start "+'"" '+'"'+location+'"'+" /D"
        else:
            command = "xdg-open "+'"'+location+'"'      #Quotation marks for if the dir has spaces in it
        os.system(command)#Using the same for both instead of os.startfile because os.startfile doesn't wait for file to close
        self.encDecTerminal("y", location, startLoc)


    def onFileDrop(self, window, filePath):  #Drag + drop files
        self.checkCanEncrypt(filePath.decode())
        self.resetButtons()
        return "Done"

    def decrypt(self, fileObj):
        if not os.path.isdir(osTemp+"FileMate"+fileSep):
            os.makedirs(osTemp+"FileMate"+fileSep)
        fileLoc = osTemp+"FileMate"+fileSep+fileObj.name
        if os.path.exists(fileLoc):
            self.openFileThread = threading.Thread(target=self.openFile, args=(fileLoc, fileObj.hexPath), daemon=True)
            self.openFileThread.start()
        else:
            self.encDecTerminal("n", fileObj.hexPath, fileLoc, fileObj.name)

            self.openFileThread = threading.Thread(target=self.openFile, args=(fileLoc, fileObj.hexPath), daemon=True)
            self.openFileThread.start()


    def checkDirExists(self, dir):
        if os.path.exists(dir):
            return True
        else:
            self.popup = Popup(title="Invalid", content=Label(text=dir+" - Not a valid directory."), pos_hint={"center_x": .5, "center_y": .5}, size_hint=(.4, .4))
            self.popup.open()
            return False


    def encryptDir(self, d, targetLoc):
        fs = os.listdir(d)
        targetLoc = targetLoc.split(fileSep)
        targetLoc[len(targetLoc)-1] = aesFName.encryptFileName(self.key, targetLoc[len(targetLoc)-1])
        targetLoc = fileSep.join(targetLoc)
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
                if self.checkDirExists(d):
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
            if self.checkDirExists(inp):
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
    
    def changeScreen(self, screen):
        self.current = screen



if useBT:
    presentation = Builder.load_file(os.path.dirname(os.path.realpath(__file__))+fileSep+"mainBT.kv")
else:
    print("Using:", os.path.dirname(os.path.realpath(__file__))+fileSep+"mainNoBT.kv")
    presentation = Builder.load_file(os.path.dirname(os.path.realpath(__file__))+fileSep+"mainNoBT.kv")

class uiApp(App):

    def build(self):
        return presentation


if __name__ == "__main__":
    runUI()

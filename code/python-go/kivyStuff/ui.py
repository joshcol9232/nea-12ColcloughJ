import os
import sys
import shutil
import threading
import time
import multiprocessing
import fileinput

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
import bluetooth
########################################

############Import AES Module########### -- Replaced with go implementation




class MainScreen(Screen, FloatLayout):

    class listButton(Button):

        def __init__(self, mainScreen, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen

    class SettingsPop(Popup):

        def __init__(self, mainScreen, **kwargs):
            self.outerScreen = mainScreen
            super(Popup, self).__init__(**kwargs)

        def editConfLoc(self, term, dir):
            for line in fileinput.input(self.outerScreen.startDir+"config.cfg", inplace=1):
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




    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.startDir = os.path.dirname(os.path.realpath(__file__))+"/"
        tempDir = self.startDir.split("/")
        del tempDir[len(tempDir)-2]
        self.startDir = "/".join(tempDir)
        self.configFile = open(self.startDir+"config.cfg", "r")
        self.path = "/"
        self.assetsPath = "/"
        self.sizeCount = 0
        self.ascending = True
        self.addFile = 0
        self.key = "1234" #Super secret secure key for testing (before bluetooth is added)
        Window.bind(on_dropfile=self.onFileDrop)

        for line in self.configFile:
            lineSplit = line.split(":")
            lineSplit[1] = lineSplit[1].replace("\n", "")
            if lineSplit[0] == "vaultDir":
                self.path = lineSplit[1]
            elif lineSplit[0] == "assetsDir":
                self.assetsPath = lineSplit[1]


        self.currentDir = self.path
        currentDirShare = self.currentDir
        print(self.currentDir, "CURRENT DIR")
        self.configFile.close()
        self.scroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        #self.encrypt(b"aaaaaaa", "/run/media/josh/USB/File Security program Analysis.odt", "/run/media/josh/USB/nea-12ColcloughJ-master/code/python/testing/Aes/temp")
        self.createButtons(self.List(self.currentDir))



    def __repr__(self):
        return "MainScreen"

    def getSortedFoldersAndFiles(self, array):
        folders = []
        files = []
        for file in array:
            if os.path.isdir(self.currentDir+file):
                folders.append(file)
            else:
                files.append(file)

        foldersSort = self.quickSortAlph(folders)
        filesSort = self.quickSortAlph(files)
        return foldersSort+filesSort


##########Getting File Information##########
    def recursiveSize(self, f):
        fs = os.listdir(f)
        #print(f)
        for item in fs:
            if os.path.isdir(f+item):
                try:
                    self.recursiveSize(f+item+"/")
                except OSError:
                    pass
            else:
                try:
                    self.totalSize += os.path.getsize(f+item)
                except PermissionError:
                    pass


    def getFileSize(self, item, recurse=False):
        if os.path.isdir(self.currentDir+item):
            if recurse:
                self.totalSize = 0
                self.recursiveSize(self.currentDir+item)
                size = self.getGoodUnit(self.totalSize)
                if size == 0:
                    return " -"
                else:
                    return size
            else:
                return " -"
        else:
            try:
                size = self.getGoodUnit(os.path.getsize(self.currentDir+item))
                if size == 0:
                    return " -"
                else:
                    return size
            except Exception as e:
                print(e, "couldn't get size.")
                return " -"

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

    def deleteFile(self, location):
        if os.path.exists(location):
            if os.path.isdir(location):
                shutil.rmtree(location)
            else:
                os.remove(location)

############################################

#######Button Creation and button functions#######

    def createButtons(self, array, sort=True):
        if self.ascending:
            if sort:
                sortedArray = self.getSortedFoldersAndFiles(array)
            btn = Button(text="^", size_hint=(.7, .015), pos_hint={"x": .005, "y": .805}, font_size=14)
            self.add_widget(btn)
        else:
            if sort:
                pass
            btn = Button(text="^", size_hint=(.7, .015), pos_hint={"x": .005, "y": .805}, font_size=14)
            self.add_widget(btn)

        self.grid = GridLayout(cols=3, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        if sort:
            for item in sortedArray:
                fileSize = self.getFileSize(item)
                btn = self.listButton(self, text=("    "+item), height=30, halign="left", valign="middle")
                btn.bind(size=btn.setter("text_size"))
                info = self.infoButton(self, item, text=(" INFO"), size_hint=(.05, 1), halign="left", valign="middle")
                info.bind(size=info.setter("text_size"))
                fileS = Label(text=" "+str(fileSize), size_hint=(.1, 1), halign="left", valign="middle")
                fileS.bind(size=fileS.setter("text_size"))
                self.grid.add_widget(btn)
                self.grid.add_widget(info)
                self.grid.add_widget(fileS)
            self.scroll = ScrollView(size_hint=(.9, None), size=(Window.width, Window.height), pos_hint={"x": .005, "y": -.21})
            self.scroll.add_widget(self.grid)
            self.add_widget(self.scroll)
        else:
            for item in array:
                fileSize = self.getFileSize(item)
                btn = self.listButton(self, text=("    "+item), height=30, halign="left", valign="middle")
                btn.bind(size=btn.setter("text_size"))
                info = self.infoButton(self, item, text=(" INFO"), size_hint=(.05, 1), halign="left", valign="middle")
                info.bind(size=info.setter("text_size"))
                fileS = Label(text=" "+str(fileSize), size_hint=(.1, 1), halign="left", valign="middle")
                fileS.bind(size=fileS.setter("text_size"))
                self.grid.add_widget(btn)
                self.grid.add_widget(info)
                self.grid.add_widget(fileS)
            self.scroll = ScrollView(size_hint=(.9, None), size=(Window.width, Window.height), pos_hint={"x": .005, "y": -.21})
            self.scroll.add_widget(self.grid)
            self.add_widget(self.scroll)

    def removeButtons(self):
        self.grid = 0
        self.remove_widget(self.scroll)
        self.scroll = 0

    def getFileNameFromText(self, itemName):
        return itemName[4:]

    def traverseButton(self, itemName):
        fileName = self.getFileNameFromText(itemName)
        if os.path.isdir(self.currentDir+fileName+"/"):
            self.currentDir = self.currentDir+fileName+"/"
            currentDirShare = self.currentDir
            self.resetButtons()
        else:
            self.decrypt(self.currentDir+fileName, fileName)

    def deleteFile(self, location):
        if os.path.exists(location):
            if os.path.isdir(location):
                shutil.rmtree(location)
            else:
                os.remove(location)

    def getFileInfo(self, fileRef):
        fileFullDir = self.currentDir+fileRef
        isFolder = False
        if os.path.isdir(fileFullDir):
            fileFullDir += "/"
            folderRef = fileRef + "/"
            isFolder = True

        #print(fileFullDir, "FULL")
        internalView = ScrollView()
        infoPopup = Popup(title="File Information", content=internalView, pos_hint={"center_x": .5, "center_y": .5}, size_hint=(.8, .4))
        internalLayout = GridLayout(cols=2, size_hint_y=None)

        internalLayout.add_widget(self.infoLabel(text="File Name:", size_hint_x=.2, halign="left", valign="middle"))
        internalLayout.add_widget(self.infoLabel(text=fileRef, halign="left", valign="middle"))

        internalLayout.add_widget(self.infoLabel(text="Current Location:", size_hint_x=.2, halign="left", valign="middle"))
        internalLayout.add_widget(self.infoLabel(text="/Vault/"+fileRef, halign="left", valign="middle"))

        if isFolder:
            fileSize = self.getFileSize(folderRef, True) #Do recurse on folders
        else:
            fileSize = self.getFileSize(fileRef)
        internalLayout.add_widget(self.infoLabel(text="Size:", size_hint_x=.2, halign="left", valign="middle"))
        internalLayout.add_widget(self.infoLabel(text=str(fileSize), halign="left", valign="middle"))

        internalView.add_widget(internalLayout)
        infoPopup.open()



    def goBackFolder(self):
        if self.currentDir != self.path:
            self.currentDir = self.getPathBack()
            currentDirShare = self.currentDir
            self.resetButtons()
        else:
            print("Can't go further up.")

    def getPathForButton(self, item):
        return self.assetsPath+item

    def resetButtons(self):
        self.removeButtons()
        self.createButtons(self.List(self.currentDir))


####File Handling####
    def List(self, dir):
        #print(dir, "LIST DIR")
        fs = os.listdir(dir)
        count = 0
        listOfFiles = []
        for item in fs:
            if os.path.isdir(dir+item):
                listOfFiles.append(item)
        for item in fs:
            if not os.path.isdir(dir+item):
                listOfFiles.append(item)
        return listOfFiles

    def getPathBack(self):
        tempDir = self.currentDir.split("/")
        del tempDir[len(tempDir)-2]
        tempDir = "/".join(tempDir)
        return tempDir

###########Sorts + Searches############
    def compareStrings(self, string1, string2):     #returns True if string1 < string2 alphabetically, and "Found" if string1 == string2
        count = 0
        while not (count >= len(string1) or count >= len(string2)):
            if ord(string2[count].lower()) < ord(string1[count].lower()):
                return True
            elif ord(string2[count].lower()) > ord(string1[count].lower()):
                return False
            else:
                if ord(string2[count]) < ord(string1[count]):    #if the same name but with capitals - e.g (Usb Backup) and (usb backup)
                    return True
                elif ord(string2[count]) > ord(string1[count]):
                    return False
                else:
                    if string2 == string1:
                        return "Found"
                    else:
                        count += 1
        if len(string1) > len(string2):
            return True
        elif len(string1) < len(string2):
            return False
        else:
            print("bit of a problem -------------------------------EROOR")
            print(string2, string1, len(string2), len(string1))


    def quickSortAlph(self, myList):
        if len(myList) > 1:
            left = []
            right = []  #Make seperate l+r lists, and add on at the end.
            middle = []
            pivot = myList[int(len(myList)/2)]
            for item in myList:
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


    def findAndSort(self, myList, item):
        unsorted = []
        self.temp = []
        for file in myList:
            loc = file.find(item)

            # if os.path.isdir(self.currentDir+item):
            #     self.traverseFileTree(self.currentDir+item)

            if file == item:
                self.searchResults = [item] + self.searchResults
                self.removeButtons()
                self.createButtons(self.searchResults)
            elif loc != -1:
                unsorted.append((loc, file))


        if len(unsorted) > 0:
            sorted = self.quickSortTuples(unsorted)
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


    def searchThread(self, myList, item):
        self.findAndSort(myList, item)
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

    def searchForItem(self, array, item):
        self.resetButtons()
        self.searchResults = []
        self.t = threading.Thread(target=self.searchThread, args=(array, item,), daemon=True)
        self.t.start()

############################

######Encryption Stuff + opening decrypted files######
    def passToTerm(self, type, key, d, targetLoc):
        os.system("./AES "+type+" "+key+" '"+d+"' '"+targetLoc+"'") #Passes parameters to compiled go AES

    def encDecTerminal(self, type, key, d, targetLoc):
        self.encryptProcess = threading.Thread(target=self.passToTerm, args=(type, key, d, targetLoc))###get rid
        self.encryptProcess.start()

    def openFile(self, location):
        os.system("xdg-open " + "'"+location+"'")

    def checkThread(self, fileName, startSize, fullPath):
        print(fullPath)
        while self.openFileThread.is_alive():
            pass

        print("DONE THREAD")
        if os.path.getsize("/tmp/FileMate/"+fileName) != startSize:
            print("FILE CHANGED")
            #self.encryptWhenModified("/tmp/FileMate/"+fileName, fullPath)
            popup = Popup(title="One second :)", content=Label(text="Encrypting edited file, please wait."), pos_hint={"center_x": .5, "center_y": .5}, size_hint=(.4, .4))
            popup.open()
            self.encDecTerminal("y", self.key, "/tmp/FileMate/"+fileName, fullPath)
            popup.dismiss()

    def onFileDrop(self, window, file_path):  #Drag + drop files
        self.checkCanEncrypt(file_path.decode())
        self.resetButtons()
        return "Done"


    def decrypt(self, fileDir, fileName):
        if not os.path.isdir("/tmp/FileMate/"):
            os.makedirs("/tmp/FileMate/")
        fileLoc = "/tmp/FileMate/"+fileName
        if os.path.exists(fileLoc):
            self.openFileThread = threading.Thread(target=self.openFile, args=(fileLoc,))
            self.openFileThread.start()
        else:
            decryptThread = multiprocessing.Process(target=self.encDecTerminal, args=("n", self.key, fileDir, fileLoc))
            decryptThread.start()
            print("decrypt")
            decryptThread.join()

            self.openFileThread = threading.Thread(target=self.openFile, args=(fileLoc,))
            self.openFileThread.start()

        checkOpenThread = threading.Thread(target=self.checkThread, args=(fileName, os.path.getsize(fileLoc), fileDir))
        checkOpenThread.start()
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
        fs = os.listdir(d)
        print(d, targetLoc)
        for item in fs:
            if os.path.isdir(d+item):
                try:
                    self.encryptDir(d+item+"/", targetLoc+"/"+item)
                except OSError:
                    pass
            else:
                try:
                    #print(d+item, targetLoc+"/"+item, "AAAAAAAAAAAAAAAAAAAAAA")
                    self.createFolders(targetLoc+"/")
                    self.encDecTerminal("y", self.key, d+item, targetLoc+"/"+item)
                except PermissionError:
                    pass

    def checkCanEncrypt(self, inp):
        if ":" in inp:
            print("COLON")
            inp = input.split(":")
            for d in inp:
                exists = self.checkDirExists(d)
                if exists:
                    if os.path.isdir(d):
                        if d[len(d)-1] != "/":
                            d += "/"
                        dSplit = d.split("/")
                        # print(d, "ISDIR")
                        self.encryptDir(d, self.currentDir+dSplit[len(dSplit)-2]+"/")
                    else:
                        dSplit = d.split("/")
                        self.encDecTerminal("y", self.key, d, self.currentDir+dSplit[len(dSplit)-1])



        else:
            exists = self.checkDirExists(inp)
            if exists:
                if os.path.isdir(inp):
                    if inp[len(inp)-1] != "/":
                        inp += "/"
                    inpSplit = inp.split("/")
                    # print(inp, "ISDIR")
                    #print(self.outerScreen.currentDir+inpSplit[len(inpSplit)-2]+"/")
                    self.encryptDir(inp, self.currentDir+inpSplit[len(inpSplit)-2])
                else:
                    inpSplit = inp.split("/")
                    self.encDecTerminal("y", self.key, inp, self.currentDir+inpSplit[len(inpSplit)-1])


        self.resetButtons()


    def createFolders(self, targetLoc):
        if not os.path.exists(targetLoc):
            os.makedirs(targetLoc)
###########################




class LoginScreen(Screen, FloatLayout):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.lockCode = b"1234"
        self.lockList = []
        self.unlock = False
        self.threads = []
        self.checkButton = Button(size_hint= (.16, .16))
        self.btThread = threading.Thread(target=self.startBTServer, daemon=True)
        # self.lockThread = threading.Thread(target=self.lockThreadFunc, daemon=True)
        # self.threads.append(self.btThread)
        # self.threads.append(self.lockThread)
        self.btThread.start()
        # self.lockThread.start()

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



    # def lockThreadFunc(self):
    #     while len(self.lockList) == 0:
    #         pass
    #     self.unlocc = True
    #     print("UNLOCK")
    #     return "done"



    def runServ(self):
        hostMACAddress = '00:1a:7d:da:71:0a' # mac of bt adapter
        port = 5
        backlog = 1
        size = 1024
        s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        s.bind((hostMACAddress, port))
        s.listen(backlog)
        try:
            client, clientInfo = s.accept()
            while True:
                data = client.recv(size)
                if data:
                    client.send(data) # Echo back to client
                    print(data)
                    if data == self.lockCode:
                        self.lockList.append(data)

        except bluetooth.btcommon.BluetoothError as e:
            client.close()
            s.close()
            return True



class ScreenManagement(ScreenManager):
    # LoginScreen = ObjectProperty(None)
    # MainScreen = ObjectProperty(None)
    # addFileScreen = ObjectProperty(None)
    pass


presentation = Builder.load_file(os.path.dirname(os.path.realpath(__file__))+"/main.kv")

class uiApp(App):

    def build(self):
        return presentation

def runUI():
    ui = uiApp()
    ui.run()
    print("Deleting temp files.")
    shutil.rmtree("/tmp/FileMate/")
    print("App closed.")


if __name__ == "__main__":
    runUI()

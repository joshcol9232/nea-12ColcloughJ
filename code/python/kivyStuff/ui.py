import os
import subprocess
import sys
import shutil

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
from kivy.lang import Builder

##########Import Bluetooth Module########
blueDir = str(os.path.dirname(os.path.realpath(__file__)))
blueDir = blueDir.split("/")
print(blueDir)
del blueDir[len(blueDir)-1]
blueDir = "/".join(blueDir)
blueDir += "/bluetoothStuff"
print(blueDir, "egg")

sys.path.insert(0, bluDir)
import bluetoothMain
########################################

class MainScreen(Screen, FloatLayout):

    class listButton(Button):

        def __init__(self, mainScreen, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = mainScreen


    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.startDir = os.path.dirname(os.path.realpath(__file__))+"/"
        tempDir = self.startDir.split("/")
        del tempDir[len(tempDir)-2]
        self.startDir = "/".join(tempDir)
        self.configFile = open(self.startDir+"config.cfg", "r")
        self.path = "/"
        self.sizeCount = 0
        self.ascending = True
        self.assetsPath = "/"
        for line in self.configFile:
            lineSplit = line.split(":")
            lineSplit[1] = lineSplit[1].replace("\n", "")
            if lineSplit[0] == "mainDir":
                self.path = lineSplit[1]
            elif lineSplit[0] == "assetsDir":
                self.assetsPath = lineSplit[1]

        self.currentDir = self.path
        self.configFile.close()
        self.root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
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

        foldersSort = self.quickSortAlphabetical(folders)
        filesSort = self.quickSortAlphabetical(files)
        return foldersSort+filesSort


##########Getting File Information##########
    def getFolderSize(self, f):
        fs = os.listdir(f)
        for item in fs:
            if os.path.isdir(f+item):
                try:
                    self.getFolderSize(f+item+"/")
                except OSError:
                    print("Not allowed xd")
            else:
                if os.path.islink(f+item) == False:
                    try:
                        self.sizeCount += os.path.getsize(f+item)
                    except Exception as e:
                        print(e, "error reeeeeeeeeeee")




    def getFileSize(self, item):
        if os.path.isdir(self.currentDir+item):
            return " -"
        else:
            try:
                size = self.getGoodUnit(os.path.getsize(self.currentDir+item))
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


############################################

#######Button Creation and button functions#######

    def createButtons(self, array):
        sortedArray = self.getSortedFoldersAndFiles(array)
        self.grid = GridLayout(cols=2, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        for item in sortedArray:
            fileSize = self.getFileSize(item)
            btn = self.listButton(self, text=("    "+item), height=30, halign="left", valign="middle")
            btn.bind(size=btn.setter("text_size"))
            fileS = Label(text=" "+str(fileSize), size_hint=(.1, 1), halign="left", valign="middle")
            fileS.bind(size=fileS.setter("text_size"))
            self.grid.add_widget(btn)
            self.grid.add_widget(fileS)
        self.root = ScrollView(size_hint=(.9, None), size=(Window.width, Window.height), pos_hint={"x": .02, "y": -.22})
        self.root.add_widget(self.grid)
        self.add_widget(self.root)

    def removeButtons(self):
        self.grid = 0
        self.remove_widget(self.root)
        self.root = 0

    def getFileNameFromText(self, itemName):
        return itemName[4:]

    def traverseButton(self, itemName):
        fileName = self.getFileNameFromText(itemName)
        if os.path.isdir(self.currentDir+fileName+"/"):
            self.currentDir = self.currentDir+fileName+"/"
            self.removeButtons()
            self.createButtons(self.List(self.currentDir))

    def goBackFolder(self):
        if self.currentDir != "/":
            self.currentDir = self.getPathBack()
            self.removeButtons()
            self.createButtons(self.List(self.currentDir))
        else:
            print("Can't go further up.")

    def List(self, dir):
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

    def getPathForButton(self, item):
        return self.assetsPath+item


###########Name Sort Button############

    def getSortOrder(self):
        if self.ascending:
            return "v"
        else:
            return "^"

    def changeSortOrder(self):
        if self.ascending:
            self.ascending = False
        else:
            self.ascending = True

#######################################
###########Sorts + Searches############
    def quickSortAlphabetical(self, myList):
        if len(myList) > 1:
            left = []
            right = []  #Make seperate l+r lists, and add on at the end.
            middle = []
            pivot = myList[int(len(myList)/2)]
            for item in myList:
                compared = False
                count = 0
                while not compared:
                    if count >= len(pivot) or count >= len(item):
                        if len(pivot) > len(item):
                            left.append(item)
                            compared = True
                        elif len(pivot) < len(item):
                            right.append(item)
                            compared = True
                        else:
                            print("bit of a problem -------------------------------EROOR")
                            print(item, pivot, len(item), len(pivot))
                            compared = True

                    else:
                        if ord(item[count].lower()) < ord(pivot[count].lower()):
                            left.append(item)
                            compared = True
                        elif ord(item[count].lower()) > ord(pivot[count].lower()):
                            right.append(item)
                            compared = True
                        else:
                            if item == pivot:
                                middle.append(item)
                                compared = True
                            else:
                                count += 1

            return self.quickSortAlphabetical(left)+middle+self.quickSortAlphabetical(right)
        else:
            return myList


    def binarySearch(self, myList, item):
        mid = int(len(myList)/2)
        if len(myList) == 1 and myList[mid] != item:
            return "Not found."
        else:
            if myList[mid] == item:
                return "Found."
            elif myList[mid] > item:
                return self.binarySearch(myList[:mid], item)     #If middle bigger than item, look through left side.
            elif myList[mid] < item:
                return self.binarySearch(myList[mid:], item)     #If middle less than item, look through right side.

##################################


####Progress Bar Information####

    def values(self, st):
        values = shutil.disk_usage(self.path)
        if st:
            return self.getGoodUnit(int(values[1]))+" / " + self.getGoodUnit(int(values[0])) + " used."
        else:
            return [values[0], values[1]]

################################

    def printStuff(self, val):
        print(val)

    def searchForItem(self, item):
        pass

class LoginScreen(Screen, FloatLayout):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)


class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file(os.path.dirname(os.path.realpath(__file__))+"/main.kv")

class uiApp(App):

    def build(self):
        return presentation

def runUI():
    ui = uiApp()
    ui.run()

if __name__ == "__main__":
    runUI()

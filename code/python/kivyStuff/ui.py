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

sys.path.insert(0, blueDir)
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
        self.assetsPath = "/"
        self.sizeCount = 0
        self.ascending = True

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

        foldersSort = self.quickSortAlph(folders)
        filesSort = self.quickSortAlph(files)
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
        if self.ascending:
            sortedArray = self.getSortedFoldersAndFiles(array)
            btn = Button(text="^", size_hint=(.7, .015), pos_hint={"x": .005, "y": .805}, font_size=14)
            self.add_widget(btn)
        else:
            btn = Button(text="^", size_hint=(.7, .015), pos_hint={"x": .005, "y": .805}, font_size=14)
            self.add_widget(btn)

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
        self.root = ScrollView(size_hint=(.9, None), size=(Window.width, Window.height), pos_hint={"x": .005, "y": -.21})
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
            self.resetButtons()

    def goBackFolder(self):
        if self.currentDir != "/":
            self.currentDir = self.getPathBack()
            self.resetButtons()
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

    def resetButtons(self):
        self.removeButtons()
        self.createButtons(self.List(self.currentDir))


###########Name Sort Button############
    class nameSortButton(Button):

        def __init__(self, outerScreen, **kwargs):
            super(Button, self).__init__(self, **kwargs)


    def getSortOrder(self):
        if self.ascending:
            return "v"
        else:
            return "^"

    def changeSortOrder(self):
        if self.ascending:
            self.ascending = False
            self.resetButtons()
        else:
            self.ascending = True
            self.resetButtons()

#######################################
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


    def binarySearchAlph(self, myList, item):
        mid = int(len(myList)/2)
        print(myList[mid])
        if item in myList[mid]:
            self.searchResults.append(myList[mid])





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
        self.searchResults = []
        self.binarySearchAlph(array, item)
        print(self.searchResults, "SEARCH FOUND TINGS")

############################

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

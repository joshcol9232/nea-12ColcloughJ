import os
import shutil

from kivy.config import Config
Config.set("graphics", "resizable", False)
Config.set("graphics", "width", "1000")
Config.set("graphics", "height", "600")
Config.set("input", "mouse", "mouse,disable_on_activity")
Config.write()

from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooser
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.progressbar import ProgressBar
from kivy.lang import Builder


class MainScreen(Screen, FloatLayout):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.buttons = []
        self.currentDir = os.path.dirname(os.path.realpath(__file__))+"/"
        self.configDir = self.getPathBack()
        self.configFile = open(self.configDir+"config.cfg", "r")
        self.files = []
        self.path = self.currentDir
        for line in self.configFile:
            lineSplit = line.split(":")
            lineSplit[1] = lineSplit[1].replace("\n", "")
            if lineSplit[0] == "mainDir":
                self.path = lineSplit[1]
        self.configFile.close()
        self.listFiles(self.path)

    def __repr__(self):
        return "MainScreen"


    class listButton(Button):

        def __init__(self, outerScreen, **kwargs):
            super(Button, self).__init__(**kwargs)
            self.outerScreen = outerScreen

        def __repr__(self):
            return self.text

        def listNextFiles(self):
            if self.text == "V":
                return self.outerScreen.moveListDown() ##############
            else:
                return self.outerScreen.listNextFiles(self.text)


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
                    if count >= len(item):
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

    def listFiles(self, dir):
        self.tempList = []
        files = self.quickSortAlphabetical(self.List(dir))
        self.currentDir = dir
        self.displayList(files)

    def displayList(self, array):
        self.fileCount = 0 #19 count = filled, 20 for full but one is the down button
        for file in array:
            self.y = 0.78 - (0.04 * self.fileCount)
            self.buttonTemp = self.listButton(self, text=str(file), pos_hint={"x": 0.01, "y": self.y})
            if self.fileCount < 19:
                self.buttons.append(self.buttonTemp)
                self.add_widget(self.buttonTemp)
                self.fileCount += 1
            else:
                self.tempList.append(self.buttonTemp)

        if len(self.tempList) > 0:
            print("BIG BUTTON EEEEEEEEEEEEEEEE")
            self.buttonDownTemp = self.listButton(self, text="V", pos_hint={"x": 0.01, "y": 0.01})
            self.buttons.append(self.buttonDownTemp)
            self.add_widget(self.buttonDownTemp)

    def removeCurrentList(self):
        for self.buttonItem in self.buttons:
            self.remove_widget(self.buttonItem)
        self.buttons = []

    def listNextFiles(self, next):
        if os.path.isdir(self.currentDir+next):
            self.removeCurrentList()
            return self.listFiles(self.currentDir+next+"/")
        else:
            return "not dir"

    def getPathBack(self):
        tempDir = self.currentDir.split("/")
        del tempDir[len(tempDir)-2]
        tempDir = "/".join(tempDir)
        return tempDir

    def goBackFolder(self):
        self.removeCurrentList()
        return self.listFiles(self.getPathBack())

    def moveListDown(self):
        self.removeCurrentList()
        print("removed list")
        #self.displayList(self.tempList)


    def values(self, st):
        values = shutil.disk_usage(self.path)
        if st:
            return str(int(values[1]/1000000))+" MB / " + str(int(values[0]/1000000)) + " MB used."
        else:
            return [values[0], values[1]]

    def getPathForButton(self, name):
        return os.path.dirname(os.path.realpath(__file__))+"/"+str(name)

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


class LoginScreen(Screen):
    pass

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

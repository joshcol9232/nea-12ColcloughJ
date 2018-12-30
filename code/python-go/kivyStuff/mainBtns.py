from kivy.uix.button import Button
from kivy.uix.image import Image

from sortsCy import quickSortSize

class listButton(Button):           #File button when using main screen.

    def __init__(self, mainScreen, fileObj, **kwargs):
        super(Button, self).__init__(**kwargs)
        self.outerScreen = mainScreen
        self.fileObj = fileObj          #The file the button corresponds to.

class nameSortButton(Button):           #Sorts the listButtons alphabetically and by folders/files.

    def __init__(self, mainScreen, **kwargs):
        super(Button, self).__init__(**kwargs)   # Run kivy Button.__init__ class with it's key word arguments.
        self.outerScreen = mainScreen

    def changeSortOrder(self):
        self.outerScreen.ascending = not self.outerScreen.ascending
        if self.outerScreen.ascending:
            self.text = "^"
            self.outerScreen.removeButtons()
            self.outerScreen.createButtons(self.outerScreen.currentList[::-1], False)
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
        self.sortList = quickSortSize(self.outerScreen.currentList)
        if not self.ascending:
            self.sortList = self.sortList[::-1]    # Reverse sorted list.

        self.outerScreen.removeButtons()
        self.outerScreen.createButtons(self.sortList, False)

    def changeSizeOrder(self):
        self.ascending = not self.ascending
        if self.ascending:
            self.text = "v"
        else:
            self.text = "^"

        if (self.sortList) and (self.outerScreen.previousDir == self.outerScreen.currentDir):   # Checking that the sortList is for the current directory and we haven't moved.
            self.sortList = self.sortList[::-1]
            self.outerScreen.currentList = self.sortList
            self.outerScreen.removeButtons()
            self.outerScreen.createButtons(self.sortList, False)
        else:
            self.outerScreen.previousDir = self.outerScreen.currentDir
            self.sortBySize()

class infoButton(Button):       #The button that displays information about the file.

    def __init__(self, mainScreen, fileObj, **kwargs):
        self.outerScreen = mainScreen
        super(Button, self).__init__(**kwargs)
        self.fileObj = fileObj


class deleteButton(Button):

    def __init__(self, mainScreen, fileObj, **kwargs):
        super(Button, self).__init__(**kwargs)
        self.outerScreen = mainScreen
        self.fileObj = fileObj

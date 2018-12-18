from kivy.uix.button import Button
from kivy.uix.bubble import Bubble
from kivy.core.window import Window

from sortsCy import quickSortSize

class listButton(Button):           #File button when using main screen.

    def __init__(self, mainScreen, fileObj, **kwargs):
        super(Button, self).__init__(**kwargs)
        self.outerScreen = mainScreen
        self.fileObj = fileObj          #The file the button corresponds to.
        self.outerScreen.bubb = None

    def showBubble(self, touch):
        if self.outerScreen.bubb != None:
            self.outerScreen.remove_widget(self.outerScreen.bubb)
        self.outerScreen.bubb = listButtonBubble(self, touch)
        self.outerScreen.add_widget(self.outerScreen.bubb)

    def on_touch_down(self, touch):
        if touch.button == "left":   # Remove bubble if left click regardless of where in the scroll view.
            if self.outerScreen.bubb != None:
                self.outerScreen.remove_widget(self.outerScreen.bubb)
                self.outerScreen.bubb = None

        if self.touchInBounds(touch):  # Since I am overriding the Button class' "on_touch_down" function, i have to check if the touch is in bounds, as before the kivy Button class did it for me.
            if touch.button == "left":
                self.outerScreen.traverseButton(self.fileObj)
            elif touch.button == "right":
                print("right click on:", self.text)
                self.showBubble(touch)

    def touchInBounds(self, touch):
        return bool((touch.opos[0] > self.pos[0] and touch.opos[0] < self.pos[0]+self.width) and (touch.opos[1] > self.pos[1] and touch.opos[1] < self.pos[1]+self.height))

class listButtonBubble(Bubble):

    def __init__(self, hostButton, touch, **kwargs):
        self.hostButton = hostButton
        self.touch = touch
        self.pos = self.touch.pos
        super(listButtonBubble, self).__init__(**kwargs)  # Run default bubble init with kwargs after doing my other stuff


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
        self.sortList = quickSortSize(self.outerScreen.currentList)
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
            self.outerScreen.currentList = self.sortList
            print("Using old list")
            self.outerScreen.removeButtons()
            self.outerScreen.createButtons(self.sortList, False)
        else:
            self.outerScreen.previousDir = self.outerScreen.currentDir
            print("Re-sorting")
            self.sortBySize()

class infoButton(Button):       #The button that displays information about the file.

    def __init__(self, mainScreen, fileObj, **kwargs):
        super(Button, self).__init__(**kwargs)
        self.outerScreen = mainScreen
        self.fileObj = fileObj


class deleteButton(Button):

    def __init__(self, mainScreen, fileObj, **kwargs):
        super(Button, self).__init__(**kwargs)
        self.outerScreen = mainScreen
        self.fileObj = fileObj

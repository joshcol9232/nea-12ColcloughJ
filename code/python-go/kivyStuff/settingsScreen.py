from os import path, makedirs
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

from configOperations import changeVaultLoc, editConfTerm

class SettingsScreen(Screen):

    def __init__(self, mainScreen, configLoc, **kwargs):
        self.outerScreen = mainScreen
        self.config = configLoc
        super(Screen, self).__init__(**kwargs)   # Done after so that when Screen.__init__ runs, it already has those attributes.

        self.ids.searchSwitch.bind(active=self.searchSwitchCallback)
        self.ids.btSwitch.bind(active=self.btSwitchCallback)

    def searchSwitchCallback(self, switch, value):
        self.outerScreen.searchRecursively = not self.outerScreen.searchRecursively
        return editConfTerm("searchRecursively", str(value), self.config)

    def btSwitchCallback(self, switch, value):
        self.outerScreen.useBTTemp = not self.outerScreen.useBTTemp
        return editConfTerm("bluetooth", str(value), self.config)

    def changeVault(self, inp):
        if inp[len(inp)-1] != self.outerScreen.fileSep:
            inp += self.outerScreen.fileSep
        try:
            worked = changeVaultLoc(inp, self.outerScreen.fileSep, self.config)
        except FileNotFoundError:
            Popup(title="Invalid", content=self.outerScreen.infoLabel(text="Directory not valid:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5}).open()
        except PermissionError as e:
            Popup(title="Invalid", content=self.outerScreen.infoLabel(text="Can't make a folder here:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5}).open()
        except Exception as e:
            print(e)
            Popup(title="Invalid", content=self.outerScreen.infoLabel(text="Can't make a folder here:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5}).open()
        else:
            if worked:
                done = Popup(title="Done", content=self.outerScreen.infoLabel(text="Changed Vault Location to:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                self.outerScreen.path = inp
                self.outerScreen.currentDir = inp
                self.recycleFolder = self.outerScreen.path+self.outerScreen.recycleName+self.outerScreen.fileSep
                self.outerScreen.resetButtons()
                done.open()
            else:
                Popup(title="Invalid", content=self.outerScreen.infoLabel(text="Directory not valid:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5}).open()

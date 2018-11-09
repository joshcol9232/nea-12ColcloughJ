import os
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup

# Large popups are popups that fill the entire screen.

class addFilePop(Popup):     #The screen (it's actually a Popup) for adding folders/files to the vault.

    def __init__(self, mainScreen, **kwargs):
        super(Popup, self).__init__(**kwargs)
        self.outerScreen = mainScreen

    class ConfirmationPopup(Popup):     #Popup for confirming encryption.

        def __init__(self, fileScreen, input, **kwargs):
            super(Popup, self).__init__(**kwargs)
            self.fileScreen = fileScreen
            self.inputText = input


    def checkIfSure(self, input):
        sure = self.ConfirmationPopup(self, input)
        sure.open()


class SettingsPop(Popup):

    def __init__(self, mainScreen, configLoc, **kwargs):
        self.outerScreen = mainScreen
        self.config = configLoc
        super(Popup, self).__init__(**kwargs)

        self.ids.searchSwitch.bind(active=self.searchSwitchCallback)
        self.ids.btSwitch.bind(active=self.btSwitchCallback)

    def searchSwitchCallback(self, switch, value):
        return self.editConfLoc("searchRecursively", str(value))

    def btSwitchCallback(self, switch, value):
        return self.editConfLoc("bluetooth", str(value))

    def editConfLoc(self, term, newContent):
        with open(self.config, "r") as conf:
            confContent = conf.readlines()

        for i in range(len(confContent)):
            a = confContent[i].split("--")
            if term == a[0]:
                a[1] = newContent+"\n"
                confContent[i] = "--".join(a)

        with open(self.config, "w") as confW:
            confW.writelines(confContent)

        if term == "bluetooth":
            self.outerScreen.useBTTemp = not self.outerScreen.useBTTemp
        elif term == "searchRecursively":
            self.outerScreen.searchRecursively = not self.outerScreen.searchRecursively

    def dirInputValid(self, inp, fileSep):      # Filesep required when self is none
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
            if inp[len(inp)-1] != self.outerScreen.fileSep:
                inp += self.outerScreen.fileSep
            if self.dirInputValid(inp, self.outerScreen.fileSep):
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
                        if inp[len(inp)-1] != self.outerScreen.fileSep:
                            inp += self.outerScreen.fileSep
                        self.editConfLoc("vaultDir", inp)
                        done = Popup(title="Done", content=self.outerScreen.infoLabel(text="Changed Vault Location to:\n"+inp), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                        self.outerScreen.path = inp
                        self.outerScreen.currentDir = inp
                        self.outerScreen.resetButtons()
                        done.open()
            else:
                warn = Popup(title="Invalid", content=self.outerScreen.infoLabel(text="Directory not valid."), size_hint=(.4, .4), pos_hint={"x_center": .5, "y_center": .5})
                warn.open()

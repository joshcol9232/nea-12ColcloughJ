from tempfile import gettempdir
import shutil

from kivy.config import Config
Config.set("graphics", "resizable", False)
Config.set("graphics", "width", "1000")
Config.set("graphics", "height", "600")
Config.set("input", "mouse", "mouse,disable_multitouch")
Config.write()

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder

######Import personal classes######
from mainScClass import MainScreen
from loginClass import LoginScreen
from loginBTClass import LoginScreenBT

#########Import config functions########
import configOperations

############Import SHA Module###########
import SHA

###########Import filename encryption###
import aesFName     #AES easier to use when written in python, but slower, which isn't much of an issue for file names hence why this part is python.

###########Import cython sorts##########
import sortsCy


def runUI():
    ui = uiApp(title="FileMate")
    ui.run()

    # When program closes:
    print("Deleting temp files.")
    try:
        fSep = configOperations.getFileSep()
        shutil.rmtree(gettempdir()+fSep+"FileMate"+fSep) # Imported from shutil
    except:
        print("No temp files.")
    print("App closed.")

class uiApp(App):

    def build(self):
        sm = ScreenManager()

        sm.transition = FadeTransition()
        fileSep, osTemp, startDir, assetsPath, path, recurseSearch, useBT, configLoc = configOperations.runConfigOperations()
        print("Screen manager starting.")
        # Load kv files for each screen.
        Builder.load_file(startDir+"kivyStuff/kvFiles/mainSc.kv")

        if useBT:
            print("Using BT")
            Builder.load_file(startDir+"kivyStuff/kvFiles/loginScBT.kv")
            sm.add_widget(LoginScreenBT(fileSep, path, startDir, name="Login"))
        else:
            Builder.load_file(startDir+"kivyStuff/kvFiles/loginSc.kv")
            sm.add_widget(LoginScreen(fileSep, path, startDir, name="Login")) #fileSep, startDir, sharedPath, 

        sm.add_widget(MainScreen(fileSep, osTemp, startDir, assetsPath, path, recurseSearch, useBT, configLoc, name="main")) # fileSep, osTemp, startDir, assetsPath, path, recurseSearch, useBT, **kwargs
        sm.current = "Login"

        return sm


if __name__ == "__main__":
    runUI()

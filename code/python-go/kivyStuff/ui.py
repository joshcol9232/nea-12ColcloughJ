#from threading import Thread
#from functools import partial
from tempfile import gettempdir
#from subprocess import Popen, PIPE
#from time import time, sleep

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

import configOperations

############Import SHA Module###########
import SHA

###########Import filename encryption###
import aesFName     #AES easier to use when written in python, but slower, which isn't much of an issue for file names hence why this part is python.

###########Import cython sorts##########
import sortsCy


def runUI():
    sm = ScreenManager()

    fileSep, osTemp, startDir, assetsPath, path, recurseSearch, useBT = configOperations.runConfigOperations()
    print("Screen manager starting.")
    if useBT:
        print("Using BT")
        sm.add_widget(LoginScreenBT(fileSep, startDir, name="Login"))
    else:
        sm.add_widget(LoginScreen(fileSep, startDir, name="Login"))

    sm.add_widget(MainScreen(fileSep, osTemp, startDir, assetsPath, path, recurseSearch, useBT, name="main")) # fileSep, osTemp, startDir, assetsPath, path, recurseSearch, useBT, **kwargs
    sm.current = "Login"

    ui = uiApp(sm, title="FileMate")
    ui.run()

    # When program closes:
    print("Deleting temp files.")
    try:
        rmtree(osTemp+"FileMate"+fileSep) # Imported from shutil
    except:
        print("No temp files.")
    print("App closed.")
    

class uiApp(App):

    def __init__(self, sm, **kwargs):
        super(uiApp, self).__init__(**kwargs)
        print("In app init")
        self.sm = sm

    def build(self):
        return self.sm


if __name__ == "__main__":
    runUI()

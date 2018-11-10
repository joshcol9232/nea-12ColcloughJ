from loginClass import LoginScreen

from threading import Thread
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.lang.builder import Builder

from bluetooth import *

class LoginScreenBT(LoginScreen, Screen):      #Has the same methods as LoginScreen, but some overwritten with bluetooth.

    def __init__(self, fileSep, path, startDir, **kwargs):
        self.fileSep, self.path, self.startDir = fileSep, path, startDir
        super(Screen, self).__init__(**kwargs)
        Builder.load_file(self.startDir+"kivyStuff/kvFiles/loginScBT.kv")
        self.key = ""

    def on_enter(self):
        Clock.schedule_once(self.startSrv, 0.7) #Use the clock to allow the screen to be rendered. (Waits 0.7 seconds for screen to be loaded.)

    def checkKey(self, inputKey):
        inputKey = inputKey.split(",")
        inputKey = inputKey[:len(inputKey)-1]
        key = " ".join(str(i) for i in inputKey)    #Formatting for AES
        valid = self.getIfValidKey(key)
        if valid:
            self.key = key
            self.manager.get_screen("main").key = key
            return True
        else:
            return False


    def startSrv(self, dt=None):
        self.serverThread = Thread(target=self.manager.get_screen("main").startBT, daemon=True)       #Runs the function in MainScreen, which prevents segmentation, so I don't have to shutdown server when screen is switched
        self.serverThread.start()   #Starting server in thread lets the screen be rendered while the server is waiting.

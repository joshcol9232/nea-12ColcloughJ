from tempfile import gettempdir
from shutil import rmtree

from kivy.config import Config
Config.set("graphics", "resizable", True)
Config.set("graphics", "width", "1000") # Set default window size
Config.set("graphics", "height", "600")
Config.set("input", "mouse", "mouse,disable_multitouch") # Disable multitouch features used on mobile apps.
Config.write()

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder

######Import personal classes######
from mainScClass import MainScreen
from loginClass import LoginScreen, LoginScreenBT
from settingsScreen import SettingsScreen

#########Import config functions########
import configOperations


def runUI():
    ui = uiApp(title="FileMate")
    ui.run()

    # When program closes:
    print("Deleting temp files.")
    try:
        fSep = configOperations.getFileSep()
        rmtree(gettempdir()+fSep+"FileMate"+fSep) # Remove all temporary files.
    except FileNotFoundError:
        print("No temp files.")
    print("App closed.")

class uiApp(App):

    def build(self):
        sm = ScreenManager()

        sm.transition = FadeTransition() # Set transition animation when changing screens.
        fileSep, osTemp, startDir, assetsPath, path, recurseSearch, useBT, configLoc = configOperations.runConfigOperations()
        # Load kv files for each screen.
        Builder.load_file(startDir+"kivyStuff/kvFiles/mainSc.kv")     # MainScreen styling.
        Builder.load_file(startDir+"kivyStuff/kvFiles/settingsSc.kv") # SettingsScreen styling.

        if useBT:
            Builder.load_file(startDir+"kivyStuff/kvFiles/loginScBT.kv")
            sm.add_widget(LoginScreenBT(fileSep, path, startDir, name="Login"))
        else:
            Builder.load_file(startDir+"kivyStuff/kvFiles/loginSc.kv")
            sm.add_widget(LoginScreen(fileSep, path, startDir, name="Login"))

        sm.add_widget(MainScreen(fileSep, osTemp, startDir, assetsPath, path, recurseSearch, useBT, configLoc, name="Main")) # fileSep, osTemp, startDir, assetsPath, path, recurseSearch, useBT, **kwargs
        sm.add_widget(SettingsScreen(sm.get_screen("Main"), configLoc, name="Settings"))
        sm.current = "Login"

        return sm


if __name__ == "__main__":
    runUI()

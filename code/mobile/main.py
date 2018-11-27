from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder

from padScreen import PadScreen
from mainScreen import MainScreen
from fileSelectionScreen import FileSelectionScreen


class ScreenManagement(ScreenManager):
    pass

presentation = Builder.load_file(u"pad.kv")

class uiApp(App):

    def build(self):
        return presentation

def runUI():
    ui = uiApp()
    ui.run()


if __name__ == u"__main__":
    runUI()

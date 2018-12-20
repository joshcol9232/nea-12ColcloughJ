from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen

from btShared import recieveFile

class MainScreen(Screen, FloatLayout):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.sStream = None
        self.rStream = None

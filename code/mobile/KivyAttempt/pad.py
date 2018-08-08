import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import bluetooth

presentation = Builder.load_file(os.path.dirname(os.path.realpath(__file__))+"/pad.kv")

class padApp(App):

    def build(self):
        return presentation

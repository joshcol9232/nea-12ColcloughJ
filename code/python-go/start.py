from sys import path
from os.path import dirname, realpath
path.insert(0, str(dirname(realpath(__file__))+"/kivyStuff"))
import ui

ui.runUI()

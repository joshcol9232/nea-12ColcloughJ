from sys import path
from os.path import dirname, realpath
path.append(str(dirname(realpath(__file__))+"/kivyStuff"))
import ui
# This file is used so that the namespace of the other python files are the same as this one, as then it is easier to access the main folder.
ui.runUI()

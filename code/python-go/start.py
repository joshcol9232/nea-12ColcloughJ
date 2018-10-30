import sys
from os.path import dirname, realpath
sys.path.insert(0, str(dirname(realpath(__file__))+"/kivyStuff"))
import ui

ui.runUI()

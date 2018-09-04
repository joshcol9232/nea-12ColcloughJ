import sys, os
print(str(os.path.dirname(os.path.realpath(__file__))+"/kivyStuff"))
sys.path.insert(0, str(os.path.dirname(os.path.realpath(__file__))+"/kivyStuff"))
import ui

ui.runUI()

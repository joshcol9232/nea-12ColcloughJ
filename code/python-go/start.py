from sys.path import insert
from os.path import dirname, realpath
insert(0, str(dirname(realpath(__file__))+"/kivyStuff"))
import ui

ui.runUI()

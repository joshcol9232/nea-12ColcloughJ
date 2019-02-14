from os import path
from os import makedirs
from pickle import dump as pickleDump

class RecycleData:

    def __init__(self, originalLoc, dateDeleted):
       self.originalLoc = originalLoc
       self.dateDeleted = dateDeleted


def pickleRecData(dataObj, location, folder):
    if not path.exists(folder):
        makedirs(folder)

    fo = open(location, "wb")
    pickleDump(dataObj, fo)
    fo.close()

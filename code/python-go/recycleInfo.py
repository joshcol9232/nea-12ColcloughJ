from os import path
from os import makedirs
from pickle import dump as pickleDump

class RecycleData:

    def __init__(self, originalLoc, dateDeleted):
       self.originalLoc = originalLoc
       self.dateDeleted = dateDeleted


def pickleRecData(dataObj, location, folder):
    if not path.exists(folder):		# If the path doesn't exist, make it
        makedirs(folder)

    fo = open(location, "wb")		# Open the file for writing in binary
    pickleDump(dataObj, fo)			# Serialise the object into the file
    fo.close()						# Close the file

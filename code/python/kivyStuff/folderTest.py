import os
import shutil

def values():
    path = os.path.realpath(__file__)
    values = shutil.disk_usage(path)
    return values[0], values[1]

print(values())

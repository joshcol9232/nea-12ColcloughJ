import os

def List(dir):
      fs = os.listdir(dir)
      count = 0
      listOfFiles = []
      for item in fs:
          if os.path.isdir(dir+item):
              listOfFiles.append(item)
      for item in fs:
          if not os.path.isdir(dir+item):
              listOfFiles.append(item)
      return listOfFiles

print(List("/home/josh/"))

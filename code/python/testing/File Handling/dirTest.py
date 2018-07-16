import os

f = "\\\lytchett.school\\student\\2012\\12Colcloughj\\Documents\\"

def traverse(f):
    fs = os.listdir(f)
    for item in fs:
        if os.path.isdir(f+item):
            print("+", f+item)
            print(traverse(f+item+"\\"))
            print("---", f)
        else:
            print(item)

print(traverse(f))

##filename, extension = os.path.splitext(f)
##if os.path.isdir(f):
##    print("eggg")


#Ben drinks egg whites

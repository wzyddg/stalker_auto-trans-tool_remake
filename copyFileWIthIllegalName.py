from shutil import copyfile
from time import time
import re
import os
import sys
import getopt


startFolder = None
newFolder = None


def handleFolder(folder: str, startFolder: str, newFolder: str):
    newDir = newFolder+folder[len(startFolder):]
    fileList = os.listdir(folder)
    for file in fileList:
        fullPath = os.path.join(folder, file)
        if os.path.isfile(fullPath):
            if len(re.compile(r"[^a-zA-Z0-9_\n.,·~!@#$%^&* \(\);:\\\[\]=+-]").findall(fullPath)) > 0:
                newPath = os.path.join(newDir, file)
                if not os.path.exists(newDir):
                    os.makedirs(newDir)
                print("MotherFucker's Name:"+fullPath)
                copyfile(fullPath, newPath)
        else:
            handleFolder(fullPath, startFolder, newFolder)


def main(argv):

    startFolder = None
    newFolder = None

    opts, args = getopt.getopt(argv[1:], "p:", [
                               "path="])
    print(opts)
    for opt, arg in opts:
        if opt in ("-p", "--path"):
            startFolder = arg
            newFolder = os.path.join(startFolder, "NON-STANDARD")

    handleFolder(startFolder, startFolder, newFolder)


# sourceFolder = r'C:\Users\wzy2\Desktop\stalker_auto-trans-tool_remake\testFile\rusName'

# copyfile(source, target)


if __name__ == "__main__":
    main(sys.argv)

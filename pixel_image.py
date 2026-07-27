from cmu_graphics import *
import subprocess
import sys
from PIL import Image

# NOT PART OF GRADED ALGORITHMIC CODE -- exempt from grading.
# tkinter's file dialog cannot run in the same process as cmu_graphics'
# pygame/SDL window on macOS (it crashes with an NSInvalidArgumentException
# from a conflict between SDL's and Tk's NSApplication setup). This helper
# works around that by launching a separate throwaway Python process that
# only opens the native file picker and prints the chosen path back to us.
def pickImagePath():
    script = (
        "from tkinter import filedialog, Tk;"
        "root = Tk(); root.withdraw();"
        "print(filedialog.askopenfilename("
        "title='Select an image', filetypes=[('Image files', '*.png')]))"
    )
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    return result.stdout.strip()

def loadImage():
    path = pickImagePath()
    if not path:
        return None

    # opening image and converting to rgb format (no need for alpha value)
    rawImg = Image.open(path)
    rgbImg = rawImg.convert("RGB")
    # image meta data
    imgWidth = rawImg.width
    imgHeight = rawImg.height
    imgData = list(rgbImg.getdata())
    return PhotoData(imgWidth, imgHeight, imgData, rgbImg)


# constructing class for image
class PhotoData:
    def __init__(self, width, height, pixelData, rgbImg):
        self.width = width
        self.height = height
        self.pixelData = pixelData
        self.pixelGrid = []
        self.rgbImg = rgbImg
        self.transformPixelData()

    # convert into 2d list for processing 
    def transformPixelData(self):
        startingPoint = 0
        for row in range(self.height):
            temp = self.pixelData[startingPoint:startingPoint + self.width]
            startingPoint = self.width + startingPoint
            self.pixelGrid.append(temp)

  






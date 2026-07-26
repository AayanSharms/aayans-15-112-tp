from cmu_graphics import *
from tkinter import filedialog
from PIL import Image

def loadImage():
    path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image files", "*.png")]
    )

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

  






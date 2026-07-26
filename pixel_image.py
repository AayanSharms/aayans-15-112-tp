from cmu_graphics import *
from PIL import Image


# opening image and converting to rgb format (no need for alpha value)
rawImg = Image.open("/Users/aayansharma/Documents/aayans-15-112-m26-tp/Images:Assets/landscape test image.png")
rgbImg = rawImg.convert("RGB")

# image meta data
imgWidth = rawImg.width
imgHeight = rawImg.height
imgData = list(rgbImg.getdata())


# constructing class for image
class PhotoData:
    def __init__(self, width, height, pixelData):
        self.width = width
        self.height = height
        self.pixelData = pixelData
        self.pixelGrid = []
        self.transformPixelData()

    # convert into 2d list for processing 
    def transformPixelData(self):
        startingPoint = 0
        for row in range(self.height):
            temp = self.pixelData[startingPoint:startingPoint + self.width]
            startingPoint = self.width + startingPoint
            self.pixelGrid.append(temp)


firstImg = PhotoData(imgWidth, imgHeight, imgData)

# puts it into a text file for testing purposes, EXEMPT CODE -- simply for testing purposes
with open("/Users/aayansharma/Documents/aayans-15-112-m26-tp/Outputs/grid_output.txt", "w") as f:
    f.write(str(firstImg.pixelGrid))      






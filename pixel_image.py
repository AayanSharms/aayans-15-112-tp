from cmu_graphics import *
import subprocess
import sys
from PIL import Image
import math
import copy
import convolution

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
        self.pixelData = pixelData #1d list of tuples
        self.pixelGrid = [] #2d list of tuples
        self.rgbImg = rgbImg
        self.transformPixelData()
        self.originalPixelGrid = copy.deepcopy(self.pixelGrid)


    # convert into 2d list for processing 
    def transformPixelData(self):
        startingPoint = 0
        for row in range(self.height):
            temp = self.pixelData[startingPoint:startingPoint + self.width]
            startingPoint = self.width + startingPoint
            self.pixelGrid.append(temp)

# KNOWN LIMITATION - bounding brightness is lossy, reversing a brightness change
# that has been bounded will not restore the original value
# something to keep in mind and possibly try and fix
# LIMITATION FIXED ^^^ Added logic to only edit the original image, not edit the edited image
def applyBrightnessAdjustment(newPixelGrid, originalPixelGrid, amount):
    rows, cols = len(newPixelGrid), len(newPixelGrid[0])
    for row in range(rows):
        for col in range(cols):
            R, G, B = originalPixelGrid[row][col]
            newPixelGrid[row][col] = boundBrightness(R, amount), boundBrightness(G, amount), boundBrightness(B, amount)
    return newPixelGrid

def boundBrightness(val, amount):
    if val + amount < 0:
        val = 0
    elif val + amount > 255:
        val = 255
    else:
        val += amount
    return val


def applyContrast(pixelGrid, originalPixelGrid, alpha): 
    rows, cols = len(pixelGrid), len(pixelGrid[0])
    for row in range(rows):
        for col in range(cols):
            R, G, B = originalPixelGrid[row][col]
            pixelGrid[row][col] = applyContrastToChannel(R, alpha), applyContrastToChannel(G, alpha), applyContrastToChannel(B, alpha)
    return pixelGrid


def applyContrastToChannel(val, alpha):
    updatedVal = (val - 128) * alpha + 128 # 
    return rounded(bound(updatedVal))
    
def applyGaussianBlur(newPixelGrid, originalPixelGrid, size):
    rows, cols = len(newPixelGrid), len(newPixelGrid[0])
    gaussianKernel = convolution.constructGaussianKernel(size)
    for row in range(rows):
        for col in range(cols):
            R, G, B = originalPixelGrid[row][col]
            newPixelGrid[row][col] = (applyBlurToChannel(0, row, col, originalPixelGrid, gaussianKernel), 
                                    applyBlurToChannel(1, row, col, originalPixelGrid, gaussianKernel), 
                                    applyBlurToChannel(2, row, col, originalPixelGrid, gaussianKernel))
    return newPixelGrid

def applyBlurToChannel(channelIndex, row, col, originalPixelGrid, kernel):
    size = len(kernel)
    total = 0
    for ky in range(size):
        for kx in range(size):
            half = size//2
            xOffset, yOffset = kx - half, ky - half
            xPos, yPos = col + xOffset, row+yOffset
            total += kernel[ky][kx] * originalPixelGrid[yPos][xPos][channelIndex]
    return total




def bound(val):
    if val > 255:
        val = 255
    elif val < 0:
        val = 0
    else:
        return val
    return val


# syncs image
def syncImage(photo):
    rows, cols = len(photo.pixelGrid), len(photo.pixelGrid[0])
    flattened = []
    for row in range(rows):
        for col in range(cols):
            flattened.append(photo.pixelGrid[row][col])
    photo.pixelData = flattened
    photo.height = rows
    photo.width = cols
    editedImg = Image.new('RGB', (photo.width, photo.height))
    editedImg.putdata(photo.pixelData)
    photo.rgbImg = editedImg
    return photo.pixelData





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
        "title='Select an image', filetypes=[('Image files', '*.png *.jpg *.jpeg')]))"
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
        self.editHistory = []
        self.checkpoints = [copy.deepcopy(self.pixelGrid)]


        self.proxyScaleFactor = (self.width//2, self.height//2)
        self.proxy = self.rgbImg.resize(self.proxyScaleFactor)
        self.proxyCheckpoints = [proxyImgToGrid(self.proxy)]


    # convert into 2d list for processing 
    def transformPixelData(self):
        startingPoint = 0
        for row in range(self.height):
            temp = self.pixelData[startingPoint:startingPoint + self.width]
            startingPoint = self.width + startingPoint
            self.pixelGrid.append(temp)


def proxyImgToGrid(proxy):
    width, height = proxy.width, proxy.height
    proxyData = list(proxy.convert('RGB').getdata())
    grid = []
    startingPoint = 0
    for row in range(height):
        temp = proxyData[startingPoint:startingPoint + width]
        startingPoint = width + startingPoint
        grid.append(temp)
    return grid

def gridToImage(grid):
    rows, cols = len(grid), len(grid[0])
    flattened = []
    for row in range(rows):
        for col in range(cols):
            flattened.append(grid[row][col])
    img = Image.new('RGB', (cols, rows))
    img.putdata(flattened)
    return img



    
def applyBrightnessAdjustment(destinationGrid, sourceGrid, amount):
    rows, cols = len(destinationGrid), len(destinationGrid[0])
    for row in range(rows):
        for col in range(cols):
            R, G, B = sourceGrid[row][col]
            destinationGrid[row][col] = boundBrightness(R, amount), boundBrightness(G, amount), boundBrightness(B, amount)
    return destinationGrid

def boundBrightness(val, amount):
    if val + amount < 0:
        val = 0
    elif val + amount > 255:
        val = 255
    else:
        val += amount
    return val


def applyContrast(destinationGrid, sourceGrid, alpha): 
    rows, cols = len(destinationGrid), len(destinationGrid[0])
    for row in range(rows):
        for col in range(cols):
            R, G, B = sourceGrid[row][col]
            destinationGrid[row][col] = applyContrastToChannel(R, alpha), applyContrastToChannel(G, alpha), applyContrastToChannel(B, alpha)
    return destinationGrid


def applyContrastToChannel(val, alpha):
    updatedVal = (val - 128) * alpha + 128 # 
    return rounded(bound(updatedVal))

# Saturation

def applySaturation(destinationGrid, sourceGrid, saturationFactor):
    rows, cols = len(destinationGrid), len(destinationGrid[0])
    for row in range(rows):
        for col in range(cols):
            R, G, B = sourceGrid[row][col]
            luma = computeLuma(R, G, B)
            destinationGrid[row][col] = (applySaturationToChannel(R, luma, saturationFactor), 
                                         applySaturationToChannel(G, luma, saturationFactor), 
                                         applySaturationToChannel(B, luma, saturationFactor))
    return destinationGrid

def computeLuma(R, G, B):
    return 0.299*R + 0.587*G+ 0.114*B

def applySaturationToChannel(channel, luma, saturationFactor):
    updatedVal = luma + saturationFactor * (channel-luma) 
    return rounded(bound(updatedVal))

# Temperature
def applyTemperature(destinationGrid, sourceGrid, val):
    rows, cols = len(destinationGrid), len(destinationGrid[0])
    for row in range(rows):
        for col in range(cols):
            R, G, B = sourceGrid[row][col]
            destinationGrid[row][col] = (rounded(bound(R+val)), rounded(bound(G)), rounded(bound(B-val)))
    return destinationGrid






# ----- Exposure -------

def applyExposure(destinationGrid, sourceGrid, EV): 
    rows, cols = len(destinationGrid), len(destinationGrid[0])
    for row in range(rows):
        for col in range(cols):
            R, G, B = sourceGrid[row][col]
            destinationGrid[row][col] = applyExposureToChanenl(R, EV), applyExposureToChanenl(G, EV), applyExposureToChanenl(B, EV)
    return destinationGrid

def applyExposureToChanenl(channel, EV):
    newVal = channel * (2**EV)
    return rounded(bound(newVal))


# ------------- Blurring ---------------------
def applyGaussianBlur(destinationGrid, sourceGrid, size):
    rows, cols = len(destinationGrid), len(destinationGrid[0])
    gaussian1DKernel = convolution.construct1DGaussianKernel(size)
    gaussian2DKernel = convolution.constructGaussianKernel(size)
    horizontalPass = copy.deepcopy(sourceGrid)

    
    for row in range(rows):
        for col in range(cols):

            #seperable 2d convolution
            if size//2<=col<=cols-1-size//2:
                horizontalPass[row][col] = (applyHorizontalBlur(0, row, col, sourceGrid, gaussian1DKernel), 
                                        applyHorizontalBlur(1, row, col, sourceGrid, gaussian1DKernel), 
                                        applyHorizontalBlur(2, row, col, sourceGrid, gaussian1DKernel))

    for row in range(rows):
        for col in range(cols):
            if size//2<=row<=rows-1-size//2 and size//2<=col<=cols-1-size//2:
                destinationGrid[row][col] = (applyVerticalBlur(0, row, col, horizontalPass, gaussian1DKernel),
                                            applyVerticalBlur(1, row, col, horizontalPass, gaussian1DKernel),
                                            applyVerticalBlur(2, row, col, horizontalPass, gaussian1DKernel))

            # Edge Pixels - Normal 2D non-seperable convolution
            else:
                destinationGrid[row][col] = (applyEdgeBlur(0, row, col, horizontalPass, gaussian2DKernel), 
                                        applyEdgeBlur(1, row, col, horizontalPass, gaussian2DKernel), 
                                        applyEdgeBlur(2, row, col, horizontalPass, gaussian2DKernel))


    return destinationGrid


# applies mirroring logic for smooth boundary blur
def applyEdgeBlur(channelIndex, row, col, pixelGrid, kernel):
    rows, cols = len(pixelGrid), len(pixelGrid[0])
    size = len(kernel)
    total = 0
    for ky in range(size):
        for kx in range(size):
            half = size//2
            xOffset, yOffset = kx - half, ky - half
            xPos, yPos = col + xOffset, row+yOffset
            if xPos < 0:
                xPos = -xPos
            elif xPos >= cols:
                overshootX = xPos-(cols-1)
                xPos = (cols-1)-overshootX
            if yPos < 0:
                yPos = -yPos
            elif yPos >= rows:
                overshootY = yPos - (rows-1)
                yPos = (rows-1)-overshootY

            total += kernel[ky][kx] * pixelGrid[yPos][xPos][channelIndex]
    return rounded(bound(total))


def applyHorizontalBlur(channelIndex, row, col, pixelGrid, kernel):
    size = len(kernel)
    total = 0
    for k in range(size):
        offset = k - size//2
        xPos = col + offset
        total += kernel[k] * pixelGrid[row][xPos][channelIndex]
    return rounded(bound(total))

def applyVerticalBlur(channelIndex, row, col, pixelGrid, kernel):
    size = len(kernel)
    total = 0
    for k in range(size):
        offset = k - size//2
        yPos = row + offset
        total += kernel[k] * pixelGrid[yPos][col][channelIndex]
    return rounded(bound(total))
    



def bound(val):
    if val > 255:
        val = 255
    elif val < 0:
        val = 0
    else:
        return val
    return val


# Draw feature

def applyDraw(destinationGrid, points, brushSize, color):
    rows, cols = len(destinationGrid), len(destinationGrid[0])
    radius = rounded(brushSize/2)
    for (cx, cy) in points:
        centerRow, centerCol = rounded(cy), rounded(cx)
        for dRow in range(-radius, radius+1):
            for dCol in range(-radius, radius+1):
                row, col = centerRow + dRow, centerCol + dCol
                if 0<=row<rows and 0<=col<cols and dRow*dRow+dCol*dCol <= radius**2:
                    destinationGrid[row][col]=color
    return destinationGrid


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
    photo.proxy = editedImg.resize(photo.proxyScaleFactor)
    return photo.pixelData

def loadIcon(path):
    img = Image.open(path).convert('RGBA')
    return CMUImage(img)





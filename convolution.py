import math

def constructGaussianKernel(size, sigma=None):
    rows = cols = size
    sum = 0
    centerCol, centerRow = cols//2, rows//2
    completeKernel = []

    if sigma == None:
        sigma = size/6

    # Builds kernel
    for row in range(rows):
        temp = []
        for col in range(cols):
            currX, currY = col - centerCol, row - centerRow
            calculated = gaussianFormula(currX, currY, sigma)
            temp.append(calculated)
            sum += calculated
        completeKernel.append(temp)


    # Normalization
    for row in range(len(completeKernel)):
        for col in range(len(completeKernel[0])):
            completeKernel[row][col] /= sum

              
    return completeKernel

def gaussianFormula(x, y, sigma):
    return  (1/(2*math.pi*(sigma**2))) * math.e** (-(((x)**2 + (y**2))/(2*(sigma**2)) )    )





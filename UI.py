from cmu_graphics import *
import pixel_image
import AdjustmentSidebar
import copy
import os

# NOT PART OF GRADED ALGORITHMIC CODE -- exempt from grading.
# Written by AI: resolves the assets folder relative to this file so icon/image
# paths work on any machine instead of being hardcoded to one developer's home directory.
assetsDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Images:Assets')

actions = {"Brightness": pixel_image.applyBrightnessAdjustment,
           "Contrast": pixel_image.applyContrast,
           "Blur": pixel_image.applyGaussianBlur,
           "Saturation": pixel_image.applySaturation, 
           "Exposure": pixel_image.applyExposure, 
           "Temperature": pixel_image.applyTemperature}

def onAppStart(app):
    app.photo = None
    app.cmuImage = None
    app.startScreen = True
    app.editScreen = False
    app.font = 'montserrat'

    # button attributes
    app.buttonOpacity = 20
    app.buttonX = app.width//2
    app.buttonY = app.height//2
    app.buttonWidth = 250
    app.buttonHeight = 100
    app.folderIcon = pixel_image.loadIcon(os.path.join(assetsDir, 'foldericon.png'))
    app.pointerIcon = pixel_image.loadIcon(os.path.join(assetsDir, 'pointericon.png'))
    app.blurIcon = pixel_image.loadIcon(os.path.join(assetsDir, 'bluricon.png'))

    app.adjustmentSidebar = AdjustmentSidebar.Sidebar(app, "Basic Adjustments")
    app.blurSidebar = AdjustmentSidebar.Sidebar(app, "Blur Adjustments")
    app.activeSidebar = app.adjustmentSidebar

    toolButtonWidth = 50
    toolButtonHeight = 50
    app.selectToolButton = AdjustmentSidebar.Button(app, 70, 150, rgb(100, 100, 100), rgb(60, 60, 60), toolButtonWidth, toolButtonHeight)
    app.blurToolButton = AdjustmentSidebar.Button(app, 70, 215, rgb(100, 100, 100), rgb(60, 60, 60), toolButtonWidth, toolButtonHeight)
    app.selectToolButton.opacity = 100
    app.blurToolButton.opacity = 60


    app.draggingSlider = None
    app.previewProxy = None
    app.previewImage = None

    app.brightness = 0
    app.contrastAlpha = 1
    app.blurSize = 15

    app.undoHistory = []
    app.redoHistory = []
    app.stateBeforeDrag = None


    app.drawingMode = False
    app.drawingPoints = []
    app.brushSize = 10
    app.brushColor = (0, 0, 0)

    app.stepsPerSecond = 100


def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = rgb(30, 30, 30)) # background
    if app.startScreen:
        loadStartScreen(app)
    if app.editScreen:
        loadEditScreen(app)

def drawTitle(app):
    color = rgb(255, 255, 255)
    bW = 2
    drawLabel("PyPhoto Editor", 20, 20, size=25, align='top-left', fill=color, font=app.font, bold=True)

def drawToolButtons(app):
    app.selectToolButton.drawButton(app)
    app.blurToolButton.drawButton(app)
    drawImage(app.pointerIcon, app.selectToolButton.centerX, app.selectToolButton.centerY, align='center', width=24, height=24)
    drawImage(app.blurIcon, app.blurToolButton.centerX, app.blurToolButton.centerY, align='center', width=24, height=24)

def loadStartScreen(app):
    openX = app.buttonX
    openY = app.buttonY
    color = rgb(255, 255, 255)
    bW = 2
    drawRect(openX, openY, app.buttonWidth, app.buttonHeight, align='center', border = 'gray', borderWidth = bW*4, fill = rgb(100, 100, 100), opacity = app.buttonOpacity)
    drawTitle(app)
    drawImage(app.folderIcon, openX-80, openY, align = 'center', width = 40, height =40 )
    drawLabel("Open", openX+10, openY, size=40, fill = color, align='center', font=app.font, bold=True)
    drawLabel("Press u for undo, r for redo, drag sliders to adjust image", openX+10, openY + 90, size = 30, fill = color, align = 'center', font = app.font, bold = True)
    drawLabel("Please pick an image around 500x500 (works too slow otherwise)", openX+10, openY + 140, size = 30, fill = color, align = 'center', font = app.font, bold = True)

def loadEditScreen(app):
    drawTitle(app)
    app.activeSidebar.drawSidebar(app)
    drawToolButtons(app)

    sidebarWidth = app.activeSidebar.width
    margin = 80
    sidebarHeight = app.activeSidebar.height
    availableWidth = app.width - (2*sidebarWidth)- margin
    availableHeight = app.height - margin

    widthRatio = availableWidth/app.photo.width
    heightRatio = availableHeight/app.photo.height
    scaleFactor = min(widthRatio, heightRatio)


    # if there is no slider being dragged and there is no preview image, the image to view is the preview image
    if app.draggingSlider != None and app.previewImage != None: 
        visibleImage = app.previewImage
    else:
        visibleImage = app.cmuImage
    drawImage(visibleImage, app.width//2, app.height//2, align = 'center', width = app.photo.width * scaleFactor, height = app.photo.height*scaleFactor)


    if app.drawingMode:
        radius = (app.brushSize/2) * scaleFactor
        r, g, b = app.brushColor
        imgLeft = app.width//2 - (app.photo.width*scaleFactor)/2 # Scale factor for preview
        imgTop = app.height//2 - (app.photo.height*scaleFactor)/2 # Scale factor for preview
        for (cx, cy) in app.drawingPoints:
            if not (imgLeft <= cx < imgLeft + app.photo.width*scaleFactor and imgTop <= cy < imgTop + app.photo.height*scaleFactor): # bounds check
                continue
            drawCircle(cx, cy, radius, fill=rgb(r, g, b)) #draws circle

def allSliderHistory(app):
    allSliders = app.adjustmentSidebar.sliders + app.blurSidebar.sliders # adding lists together because those are all the sliders
    return allSliders

def undo(app):
    # cannot undo if no edits have been made
    if len(app.undoHistory) == 0:
        return
    photo = app.photo


    # creates slider position list to keep track of slider positions
    sliderPositions = []

    # loops through all sliders and adds their positions to a list
    for otherSlider in allSliderHistory(app):
        sliderPositions.append(otherSlider.cx)

    # add the undo to the redo
    app.redoHistory.append((list(photo.editHistory), list(photo.checkpoints), list(photo.proxyCheckpoints), sliderPositions))


    # pop the value
    editHistory, checkpoints, proxyCheckpoints, sliderPositions = app.undoHistory.pop()

    # reset edit history and checkpoints
    photo.editHistory = editHistory
    photo.checkpoints = checkpoints
    photo.proxyCheckpoints = proxyCheckpoints
    photo.pixelGrid = photo.checkpoints[-1] # set current state of image to most recent state 


    # resets slider positions
    # This piece of code was helped by claude (Lines 139-140)
    for i in range(len(allSliderHistory(app))):
        allSliderHistory(app)[i].cx = sliderPositions[i]

    applyEdits(app)


# opposite of undo
def redo(app):
    if len(app.redoHistory) == 0:
        return
    photo = app.photo

    sliderPositions = []
    for otherSlider in allSliderHistory(app):
        sliderPositions.append(otherSlider.cx)
    app.undoHistory.append((list(photo.editHistory), list(photo.checkpoints), list(photo.proxyCheckpoints), sliderPositions))

    editHistory, checkpoints, proxyCheckpoints, sliderPositions = app.redoHistory.pop()
    photo.editHistory = editHistory
    photo.checkpoints = checkpoints
    photo.proxyCheckpoints = proxyCheckpoints
    photo.pixelGrid = photo.checkpoints[-1]


    # This piece of code was helped by claude (Lines 164-165)
    for i in range(len(allSliderHistory(app))):
        allSliderHistory(app)[i].cx = sliderPositions[i]

    applyEdits(app)


#  ----- Event Handlers -------

def onKeyPress(app, key):
    if key == "u":
        undo(app)
    if key == "r":
        redo(app)
    if key == 'd':
        app.drawingMode = True

def inButton(button, mouseX, mouseY):
    return (button.centerX - button.width/2 <= mouseX <= button.centerX + button.width/2 and
            button.centerY - button.height/2 <= mouseY <= button.centerY + button.height/2)

def onMouseMove(app, mouseX, mouseY):
    if app.startScreen:
        if (app.buttonX - app.buttonWidth/2 <= mouseX <= app.buttonX + app.buttonWidth/2
            and app.buttonY - app.buttonHeight/2 <= mouseY <= app.buttonY + app.buttonHeight/2):
            app.buttonOpacity = 80
        else:
            app.buttonOpacity = 20

    if app.editScreen:
        resetButton = app.activeSidebar.buttons[0]
        if inButton(resetButton, mouseX, mouseY):
            resetButton.opacity = 100
        else:
            resetButton.opacity = 60

        # only change opacity of tool buttons if they arent the active one
        if app.activeSidebar != app.adjustmentSidebar:
            app.selectToolButton.opacity = 100 if inButton(app.selectToolButton, mouseX, mouseY) else 60
        if app.activeSidebar != app.blurSidebar:
            app.blurToolButton.opacity = 100 if inButton(app.blurToolButton, mouseX, mouseY) else 60


def onMousePress(app, mouseX, mouseY):
    if app.startScreen:
        if (app.buttonX - app.buttonWidth/2 <= mouseX <= app.buttonX + app.buttonWidth/2
                and app.buttonY - app.buttonHeight/2 <= mouseY <= app.buttonY + app.buttonHeight/2):
            photo = pixel_image.loadImage()
            if photo is not None:  # None means the user cancelled the file dialog
                app.photo = photo
                app.cmuImage = CMUImage(app.photo.rgbImg)
                app.startScreen = False
                app.editScreen = True

    if app.editScreen:
        if inButton(app.selectToolButton, mouseX, mouseY):
            app.activeSidebar = app.adjustmentSidebar
            app.selectToolButton.opacity = 100
            app.blurToolButton.opacity = 60

        if inButton(app.blurToolButton, mouseX, mouseY):
            app.activeSidebar = app.blurSidebar
            app.blurToolButton.opacity = 100
            app.selectToolButton.opacity = 60

        for slider in app.activeSidebar.sliders:
            if (slider.cx - slider.circleRadius <= mouseX <= slider.cx + slider.circleRadius and
                slider.cy - slider.circleRadius <= mouseY <= slider.cy + slider.circleRadius):
                app.draggingSlider = slider

                # appends the slider positions to the list so undo/redo can access them later
                sliderPositions = []
                for otherSlider in allSliderHistory(app):
                    sliderPositions.append(otherSlider.cx)
                app.stateBeforeDrag = (list(app.photo.editHistory), list(app.photo.checkpoints),
                                       list(app.photo.proxyCheckpoints), sliderPositions)



                history = app.photo.editHistory #(editName, value)
                exisitingIndex = None
                for i in range(len(history)):
                    if history[i][0] == slider.name:
                        exisitingIndex = i
                        break

                # if edit hasnt been made, add it to the end
                if exisitingIndex == None:
                    app.previewProxy = app.photo.proxyCheckpoints[-1]
                # replace existing index
                elif exisitingIndex != None:
                    app.previewProxy = app.photo.proxyCheckpoints[exisitingIndex]


        if app.drawingMode:
            app.drawingPoints = [(mouseX, mouseY)]

        resetButton = app.activeSidebar.buttons[0]
        if inButton(resetButton, mouseX, mouseY):
            photo = app.photo
            photo.editHistory = []
            photo.checkpoints = photo.checkpoints[:1]
            photo.proxyCheckpoints = photo.proxyCheckpoints[:1]
            photo.pixelGrid = photo.checkpoints[-1]
            for slider in allSliderHistory(app):
                if slider.name == "Blur":
                    slider.cx = slider.start # blur only increases, so it resets to the left end
                else:
                    slider.cx = (slider.start + slider.end) / 2
            applyEdits(app)



def onMouseDrag(app, mouseX, mouseY):
    if app.editScreen and app.draggingSlider != None:
        currSlider = app.draggingSlider
        currSlider.cx = max(currSlider.start, min(currSlider.end, mouseX))

        sliderValue = applySliderValue(app, currSlider)


        previewGrid = copy.deepcopy(app.previewProxy) # dont edit the actual preview
        actions[currSlider.name](previewGrid, previewGrid, sliderValue) # applies the edit on top of the image
        previewImg = pixel_image.gridToImage(previewGrid) # turns it into a readable image
        app.previewImage = CMUImage(previewImg)

    if app.editScreen and app.drawingMode and len(app.drawingPoints)>0:
        app.drawingPoints.append((mouseX, mouseY))

       
        

def onMouseRelease(app, mouseX, mouseY):
    currSlider = app.draggingSlider
    if app.draggingSlider != None:
        if currSlider.name in actions:
            sliderValue = applySliderValue(app, currSlider)
            commitEdit(app, currSlider.name, sliderValue)
    if app.drawingMode:
        commitDraw(app, app.drawingPoints, app.brushSize, app.brushColor)
        app.drawingPoints = []
    app.draggingSlider = None


# This function below was helped by claude (Commit draw and commit edit)
# Was used for refining code, structure and algorithm I implemented
def commitDraw(app, points, brushSize, color):
    photo = app.photo

    # has to keep track of slider positions for undo redo
    sliderPositions = []
    for otherSlider in allSliderHistory(app):
        sliderPositions.append(otherSlider.cx)
    app.undoHistory.append((list(photo.editHistory), list(photo.checkpoints), list(photo.proxyCheckpoints), sliderPositions))
    app.redoHistory = []

    # Adds edit to history
    history = photo.editHistory
    history.append(("Draw", (points, brushSize, color)))

    # For preview, checks if brush is within the image
    sidebarWidth = app.adjustmentSidebar.width
    margin = 80
    availableWidth = app.width - (2*sidebarWidth) - margin
    availableHeight = app.height - margin
    scaleFactor = min(availableWidth/photo.width, availableHeight/photo.height)

    # Scale factor was a debug from claude
    imgLeft = app.width//2 - (photo.width*scaleFactor)/2
    imgTop = app.height//2 - (photo.height*scaleFactor)/2
    points = [((cx-imgLeft)/scaleFactor, (cy-imgTop)/scaleFactor) for (cx, cy) in points]
    points = [(cx, cy) for (cx, cy) in points if 0 <= cx < photo.width and 0 <= cy < photo.height]

    # Applies image on top of image
    newGrid = copy.deepcopy(photo.checkpoints[-1])
    pixel_image.applyDraw(newGrid, points, brushSize, color)
    photo.checkpoints.append(newGrid)

    # Same thing for proxy grid, but points are scaled accordingly
    newProxyGrid = copy.deepcopy(photo.proxyCheckpoints[-1])
    scaleRatio = photo.proxyScaleFactor[0]/photo.width
    scaledPoints = [(cx*scaleRatio, cy*scaleRatio) for (cx,cy) in points]
    
    pixel_image.applyDraw(newProxyGrid, scaledPoints, brushSize*scaleRatio, color)
    photo.proxyCheckpoints.append(newProxyGrid)

    # sets current state to edit
    photo.pixelGrid = photo.checkpoints[-1]
    applyEdits(app)

def commitEdit(app, name, value):
    photo = app.photo

    if app.stateBeforeDrag != None: # checks if drag was in progress, either holds none or a 4 tuple snapshot
        app.undoHistory.append(app.stateBeforeDrag) # grabs snapshot before drag
        app.stateBeforeDrag = None # sets it to none
    else:
        # adds all the history of the edit history, checkpoints, and more importantly, slider positions
        sliderPositions = []
        for otherSlider in allSliderHistory(app):
            sliderPositions.append(otherSlider.cx)
        app.undoHistory.append((list(photo.editHistory), list(photo.checkpoints), list(photo.proxyCheckpoints),
                               sliderPositions))
    app.redoHistory = []




    history = photo.editHistory
    exisitingIndex = None

    # go through the edit history and see if that edit was already made
    for i in range(len(history)):
        if history[i][0] == name:
            exisitingIndex = i
            break

    if exisitingIndex == None:
        history.append((name, value)) # add to edit history

        newGrid = copy.deepcopy(photo.checkpoints[-1]) #create a new copy of the image
        newProxyGrid = copy.deepcopy(photo.proxyCheckpoints[-1]) #create a new copy of a proxy

        actions[name](newGrid, newGrid, value) # edit that copy
        actions[name](newProxyGrid, newProxyGrid, value) #edit the proxy

        photo.checkpoints.append(newGrid) # add that copy to the checkpoints
        photo.proxyCheckpoints.append(newProxyGrid) # add that copy to proxy checkpoints

    elif exisitingIndex != None:

        history[exisitingIndex] = (name, value) # edits the value that is already there

        currGrid = copy.deepcopy(photo.checkpoints[exisitingIndex]) # copies that specific index to edit
        currProxyGrid = copy.deepcopy(photo.proxyCheckpoints[exisitingIndex]) # Same thing ^ but for proxy

        photo.checkpoints = photo.checkpoints[:exisitingIndex + 1] # the checkpoints from that value onwards
        photo.proxyCheckpoints = photo.proxyCheckpoints[:exisitingIndex + 1] # the checkpoints from that value onwards

        # applies that edit to every checkpoint after that 
        for i in range(exisitingIndex, len(history)):
            name, value = history[i] #unpacks tuple

            if name != "Draw":
                actions[name](currGrid, currGrid, value)
                actions[name](currProxyGrid, currProxyGrid, value)

            photo.proxyCheckpoints.append(copy.deepcopy(currProxyGrid))
            photo.checkpoints.append(copy.deepcopy(currGrid))

    # makes the last edit the visible one
    photo.pixelGrid = photo.checkpoints[-1]
    applyEdits(app)



# ------ Editing functions -----

def applyBlur(app, size):
    if app.editScreen:
        app.blurSize = size
        pixel_image.applyGaussianBlur(app.photo.pixelGrid, app.photo.originalPixelGrid, app.blurSize)
        applyEdits(app)

def applySliderValue(app, slider):
    percent = (slider.cx - slider.start) / (slider.end - slider.start)
    if slider.name == "Brightness":
        amount = -255 + percent * 510
        return rounded(amount)
    elif slider.name == "Contrast":
        alpha = 0 + percent*2
        return alpha
    elif slider.name == "Saturation":
        saturationFactor = 0+percent*2
        return saturationFactor
    if slider.name == "Brightness":
        val = -255 + percent * 510
        return rounded(val)  
    elif slider.name == "Exposure":
        EV = -2 + percent*4
        return EV
    elif slider.name == "Temperature":
        val = -80 + percent * 160
        return rounded(val)
    elif slider.name == "Blur":
        # equation from claude, snaps percent to odd kernel sizes between 3 and 31
        size = 3 + 2*rounded(percent*14)
        return size

def applyEdits(app):
    pixel_image.syncImage(app.photo)
    app.cmuImage = CMUImage(app.photo.rgbImg)



def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

main()
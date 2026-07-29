from cmu_graphics import *
import pixel_image
import AdjustmentSidebar
import copy

actions = {"Brightness": pixel_image.applyBrightnessAdjustment, 
           "Contrast": pixel_image.applyContrast,
           "Blur": pixel_image.applyGaussianBlur}

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
    app.folderIcon = pixel_image.loadIcon('/Users/aayansharma/Documents/aayans-15-112-m26-tp/Images:Assets/foldericon.png')

    app.adjustmentSidebar = AdjustmentSidebar.Sidebar(app, "Basic Adjustments")
    app.draggingSlider = None
    app.previewProxy = None
    app.previewImage = None

    app.brightness = 0
    app.contrastAlpha = 1
    app.blurSize = 15

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

def loadStartScreen(app):
    openX = app.buttonX
    openY = app.buttonY
    color = rgb(255, 255, 255)
    bW = 2
    drawRect(openX, openY, app.buttonWidth, app.buttonHeight, align='center', border = 'gray', borderWidth = bW*4, fill = rgb(100, 100, 100), opacity = app.buttonOpacity)
    drawTitle(app)
    drawImage(app.folderIcon, openX-80, openY, align = 'center', width = 40, height =40 )
    drawLabel("Open", openX+10, openY, size=40, fill = color, align='center', font=app.font, bold=True)

def loadEditScreen(app):
    drawTitle(app)
    app.adjustmentSidebar.drawSidebar(app)

    sidebarWidth = app.adjustmentSidebar.width
    margin = 80
    sidebarHeight = app.adjustmentSidebar.height
    availableWidth = app.width - (2*sidebarWidth)- margin
    availableHeight = app.height - margin

    widthRatio = availableWidth/app.photo.width
    heightRatio = availableHeight/app.photo.height
    scaleFactor = min(widthRatio, heightRatio)

    if app.draggingSlider != None and app.previewImage != None:
        visibleImage = app.previewImage
    else:
        visibleImage = app.cmuImage
    drawImage(visibleImage, app.width//2, app.height//2, align = 'center', width = app.photo.width * scaleFactor, height = app.photo.height*scaleFactor)


#  ----- Event Handlers -------

def onKeyPress(app, key):
    if key == "b":
        commitEdit(app, "Blur", app.blurSize)
    


def onMouseMove(app, mouseX, mouseY):
    if app.startScreen:
        if (app.buttonX - app.buttonWidth/2 <= mouseX <= app.buttonX + app.buttonWidth/2 
            and app.buttonY - app.buttonHeight/2 <= mouseY <= app.buttonY + app.buttonHeight/2):
            app.buttonOpacity = 80
        else:
            app.buttonOpacity = 20

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
        for slider in app.adjustmentSidebar.sliders:
            if (slider.cx - slider.circleRadius <= mouseX <= slider.cx + slider.circleRadius and 
                slider.cy - slider.circleRadius <= mouseY <= slider.cy + slider.circleRadius):
                app.draggingSlider = slider

                history = app.photo.editHistory
                exisitingIndex = None
                for i in range(len(history)):
                    if history[i][0] == slider.name:
                        exisitingIndex = i
                        break
                if exisitingIndex == None:
                    app.previewProxy = app.photo.proxyCheckpoints[-1]
                elif exisitingIndex != None:
                    app.previewProxy = app.photo.proxyCheckpoints[exisitingIndex]

                

def onMouseDrag(app, mouseX, mouseY):
    if app.editScreen and app.draggingSlider != None:
        currSlider = app.draggingSlider
        currSlider.cx = max(currSlider.start, min(currSlider.end, mouseX))

        sliderValue = applySliderValue(app, currSlider)

        previewGrid = copy.deepcopy(app.previewProxy)
        actions[currSlider.name](previewGrid, previewGrid, sliderValue)
        previewImg = pixel_image.gridToImage(previewGrid)
        app.previewImage = CMUImage(previewImg)

       
        

def onMouseRelease(app, mouseX, mouseY):
    currSlider = app.draggingSlider
    if app.draggingSlider != None:
        if currSlider.name in ("Brightness", "Contrast"):
            sliderValue = applySliderValue(app, currSlider)
            commitEdit(app, currSlider.name, sliderValue)
    app.draggingSlider = None


def commitEdit(app, name, value):
    photo = app.photo
    history = photo.editHistory
    exisitingIndex = None
    for i in range(len(history)):
        if history[i][0] == name:
            exisitingIndex = i
            break
    if exisitingIndex == None:
        history.append((name, value)) # add to edit history

        newGrid = copy.deepcopy(photo.checkpoints[-1]) #create a new copy of the image
        newProxyGrid = copy.deepcopy(photo.proxyCheckpoints[-1])

        actions[name](newGrid, newGrid, value) # edit that copy
        actions[name](newProxyGrid, newProxyGrid, value)

        photo.checkpoints.append(newGrid) # add that copy to the checkpoints
        photo.proxyCheckpoints.append(newProxyGrid)

    elif exisitingIndex != None:
        history[exisitingIndex] = (name, value)

        currGrid = copy.deepcopy(photo.checkpoints[exisitingIndex])
        currProxyGrid = copy.deepcopy(photo.proxyCheckpoints[exisitingIndex])

        photo.checkpoints = photo.checkpoints[:exisitingIndex + 1]
        photo.proxyCheckpoints = photo.proxyCheckpoints[:exisitingIndex + 1]

        for i in range(exisitingIndex, len(history)):
            name, value = history[i]

            actions[name](currGrid, currGrid, value)
            actions[name](currProxyGrid, currProxyGrid, value)

            photo.proxyCheckpoints.append(copy.deepcopy(currProxyGrid))
            photo.checkpoints.append(copy.deepcopy(currGrid))

    photo.pixelGrid = photo.checkpoints[-1]
    applyEdits(app)



# ------ Editing functions -----

def applyBlur(app, size):
    if app.editScreen:
        app.blurSize = size
        pixel_image.applyGaussianBlur(app.photo.pixelGrid, app.photo.originalPixelGrid, app.blurSize)
        applyEdits(app)

def applySliderValue(app, slider):
    if slider.name == "Brightness":
        percent = (slider.cx - slider.start) / (slider.end - slider.start)
        amount = -255 + percent * 510
        return rounded(amount)
    if slider.name == "Contrast":
        percent = (slider.cx - slider.start) / (slider.end - slider.start)
        alpha = 0 + percent*2
        return alpha





def applyEdits(app):
    pixel_image.syncImage(app.photo)
    app.cmuImage = CMUImage(app.photo.rgbImg)



def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

main()
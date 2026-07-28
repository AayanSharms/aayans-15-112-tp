from cmu_graphics import *
import pixel_image
import AdjustmentSidebar


def onAppStart(app):
    app.image = None
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

    app.adjustmentSidebar = AdjustmentSidebar.Sidebar(app, "Basic Adjustments")
    app.draggingSlider = None

    app.brightness = 0
    app.contrastAlpha = 1
    app.blurSize = 25

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = rgb(30, 30, 30)) # background
    if app.startScreen:
        loadStartScreen(app)
    if app.editScreen:
        loadEditScreen(app)

def drawTitle(app):
    color = rgb(255, 255, 255)
    bW = 2
    drawLabel("PyPhoto Editor", 20, 20, size=25, align='top-left', fill=color, font=app.font, bold=True, border = color, borderWidth = bW)

def loadStartScreen(app):
    openX = app.buttonX
    openY = app.buttonY
    color = rgb(255, 255, 255)
    bW = 2
    drawRect(openX, openY, app.buttonWidth, app.buttonHeight, align='center', border = 'gray', borderWidth = bW*4, fill = rgb(100, 100, 100), opacity = app.buttonOpacity)
    drawTitle(app)
    drawLabel("Open", openX, openY, size=40, fill = color, align='center', font=app.font, bold=True, border = color, borderWidth = bW)

def loadEditScreen(app):
    drawTitle(app)
    app.adjustmentSidebar.drawSidebar(app)
    drawImage(app.cmuImage, app.width//2, app.height//2, align = 'center')


#  ----- Event Handlers -------

def onKeyPress(app, key):
    if key == "b":
        applyBlur(app, app.blurSize)


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

                

def onMouseDrag(app, mouseX, mouseY):
    if app.editScreen and app.draggingSlider != None:
        currSlider = app.draggingSlider
        currSlider.cx = max(currSlider.start, min(currSlider.end, mouseX))

        if currSlider.name == "Brightness":
            sliderValue = applySliderValue(app, currSlider)
            applyBrightness(app, sliderValue)
        if currSlider.name == "Contrast":
            sliderValue = applySliderValue(app, currSlider)
            applyContrast(app, sliderValue)

def onMouseRelease(app, mouseX, mouseY):
    app.draggingSlider = None




# ------ Editing functions -----
def applyBrightness(app, amount):
    if app.editScreen:
        pixel_image.applyBrightnessAdjustment(app.photo.pixelGrid, app.photo.originalPixelGrid, amount)
        applyEdits(app)

def applyContrast(app, alpha):
    if app.editScreen:
        app.contrastAlpha = alpha
        pixel_image.applyContrast(app.photo.pixelGrid, app.photo.originalPixelGrid, alpha)
        applyEdits(app)

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
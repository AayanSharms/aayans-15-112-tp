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

    app.brightness = 0
    app.contrastAlpha = 1

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
    if key == "up":
        app.contrastAlpha += 0.2
        applyContrast(app, app.contrastAlpha)
    elif key == 'down':
        app.contrastAlpha -= 0.2
        applyContrast(app, app.contrastAlpha)



def onMouseMove(app, mouseX, mouseY):
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


# ------ Editing functions -----
def applyBrightness(app, amount):
    if app.editScreen:
        pixel_image.applyBrightnessAdjustment(app.photo.pixelGrid, app.photo.originalPixelGrid, amount)
        applyEdits(app)

def applyContrast(app, alpha):
    if app.editScreen:
        alpha = app.contrastAlpha
        pixel_image.applyContrast(app.photo.pixelGrid, app.photo.originalPixelGrid, alpha)
        applyEdits(app)

def applyEdits(app):
    pixel_image.syncImage(app.photo)
    app.cmuImage = CMUImage(app.photo.rgbImg)


def main():
    width = 1280
    height = 720
    runApp(width=width, height=height)

main()
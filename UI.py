from cmu_graphics import *
import pixel_image


def onAppStart(app):
    app.image = None
    app.cmuImage = None
    app.startScreen = True
    app.editScreen = False

    # button attributes
    app.buttonOpacity = 20
    app.buttonX = app.width//2
    app.buttonY = app.height//2
    app.buttonWidth = 250
    app.buttonHeight = 100

    app.contrastK = 0.5

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = rgb(30, 30, 30)) # background
    if app.startScreen:
        loadStartScreen(app)
    if app.editScreen:
        loadEditScreen(app)

def drawTitle(app):
    color = rgb(255, 255, 255)
    bW = 2
    font = 'montserrat'
    drawLabel("PyPhoto Editor", 20, 20, size=25, align='top-left', fill=color, font=font, bold=True, border = color, borderWidth = bW)


def loadStartScreen(app):
    openX = app.buttonX
    openY = app.buttonY
    color = rgb(255, 255, 255)
    bW = 2
    font = 'montserrat'
    drawRect(openX, openY, app.buttonWidth, app.buttonHeight, align='center', border = 'gray', borderWidth = bW*4, fill = rgb(100, 100, 100), opacity = app.buttonOpacity)
    drawTitle(app)
    drawLabel("Open", openX, openY, size=40, fill = color, align='center', font=font, bold=True, border = color, borderWidth = bW)

def loadEditScreen(app):
    drawTitle(app)
    drawImage(app.cmuImage, app.width//2, app.height//2, align = 'center')

def applyBrightness(app, amount):
    if app.editScreen:
        pixel_image.applyBrightnessAdjustment(app.photo.pixelGrid, amount)
        applyEdits(app)

def applyContrast(app):
    if app.editScreen:
        k = app.contrastK
        pixel_image.applyContrast(app.photo.pixelGrid, k)
        applyEdits(app)



def applyEdits(app):
    pixel_image.syncImage(app.photo)
    app.cmuImage = CMUImage(app.photo.rgbImg)

def onKeyPress(app, key):
    if key == "up":
        app.contrastK += 0.2
        applyContrast(app)
    



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


def main():
    width = 1920
    height = 1080
    runApp(width=width, height=height)

main()
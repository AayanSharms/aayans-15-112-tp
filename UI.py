from cmu_graphics import *
import pixel_image

def onAppStart(app):
    app.image = None
    app.startScreen = True
    app.editScreen = False

    # button attributes
    app.buttonOpacity = 20
    app.buttonX = app.width//2
    app.buttonY = app.height//2
    app.buttonWidth = 250
    app.buttonHeight = 100

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill = rgb(30, 30, 30)) # background
    if app.startScreen:
        drawStartScreen(app)
    # if app.editScreen:
        # photo = pixel_image.loadImage()
        # drawImage(photo.rgbImg, app.width/2, app.height/2, align='center')

def drawStartScreen(app):
    openX = app.buttonX
    openY = app.buttonY
    color = rgb(255, 255, 255)
    bW = 2
    font = 'montserrat'
    drawRect(openX, openY, app.buttonWidth, app.buttonHeight, align='center', border = 'gray', borderWidth = bW*4, fill = rgb(100, 100, 100), opacity = app.buttonOpacity)
    drawLabel("PyPhoto Editor", 20, 20, size=25, align='top-left', fill=color, font=font, bold=True, border = color, borderWidth = bW)
    drawLabel("Open", openX, openY, size=40, fill = color, align='center', font=font, bold=True, border = color, borderWidth = bW)

def onMouseMove(app, mouseX, mouseY):
    if (app.buttonX - app.buttonWidth/2 <= mouseX <= app.buttonX + app.buttonWidth/2 
        and app.buttonY - app.buttonHeight/2 <= mouseY <= app.buttonY + app.buttonHeight/2):
        app.buttonOpacity = 80
    else:
        app.buttonOpacity = 20





def main():
    width = 1920
    height = 1080
    runApp(width=width, height=height)

main()
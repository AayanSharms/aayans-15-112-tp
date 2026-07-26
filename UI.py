from cmu_graphics import *
import pixel_image

def onAppStart(app):
    app.image = CMUImage(pixel_image.rgbImg)

def redrawAll(app):
    drawImage(app.image, app.width/2, app.height/2, align='center')
    

def main():
    width = 1920
    height = 1080
    runApp(width=width, height=height)

main()
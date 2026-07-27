from cmu_graphics import *

class Sidebar:
    def __init__(self, app, title):
        self.title = title
        self.updateDimesions(app)
        self.sliders = []
    def updateDimensions(self, app):
        self.width = app.width // 5
        self.height = app.height
        self.left = app.width - self.width
        self.top = 0
    def drawSidebar(self, app):
        self.updateDimensions(app)
        drawRect(self.left, self.top, self.width, self.height, fill = rgb(45, 45, 45), borderWidth = 2)
        drawLabel(self.title, self.width//2, self.height + self.height//20, fill = 'white')


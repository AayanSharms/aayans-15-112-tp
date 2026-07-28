from cmu_graphics import *

class Sidebar:
    def __init__(self, app, title):
        self.title = title
        self.sliders = []
        self.font = 'montserrat'
        self.updateDimensions(app)

        if self.title == "Basic Adjustments":
            self.sliders.append(Slider(app, "Brightness", self.centerX, self.top+150, self.width))
            self.sliders.append(Slider(app, "Contrast", self.centerX, self.top+250, self.width))

    def updateDimensions(self, app):
        self.width = app.width // 5
        self.height = app.height
        self.left = app.width - self.width
        self.centerX = self.left + self.width//2
        self.top = 0
        for slider in self.sliders:
            slider.updateSliderPosition(self.centerX, self.width)

    def drawSidebar(self, app):
        self.updateDimensions(app)
        sideBarColor = rgb(45, 45, 45)
        borderColor = rgb(100, 100, 100)
        drawRect(self.left, self.top, self.width, self.height, fill = sideBarColor, borderWidth = 4, border = borderColor)
        drawLabel(self.title, self.centerX, self.top+50, fill = 'white', font = app.font, bold = True, size = 15, borderWidth = 1, border = 'white')
        for slider in self.sliders:
            slider.drawSlider(app)

class Slider:
    def __init__(self, app, name, x, y, sidebarWidth):
        self.name = name

        self.x = x 
        self.y = y

        self.cx = x
        self.cy = y + 25
        self.circleRadius = 8

        self.lineLength = (sidebarWidth - 70)//2
        self.start = self.x - self.lineLength
        self.end = self.x+self.lineLength
    def updateSliderPosition(self, x, sidebarWidth):
        self.x = x
        self.lineLength = (sidebarWidth - 70)//2
        self.start = self.x - self.lineLength
        self.end = self.x + self.lineLength
    def drawSlider(self, app):
        drawLabel(self.name, self.x, self.y, size = 18, font = app.font, fill = 'white')
        drawLine(self.start, self.y + 25, self.end, self.y + 25, fill = 'white', lineWidth = 2)
        drawCircle(self.cx, self.cy, self.circleRadius, fill = rgb(200, 200, 200))



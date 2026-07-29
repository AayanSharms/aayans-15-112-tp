from cmu_graphics import *

class Sidebar:
    def __init__(self, app, title):
        self.title = title
        self.sliders = []
        self.font = 'montserrat'
        self.update(app)
        self.buttons = []

        if self.title == "Basic Adjustments":
            self.sliders.append(Slider(app, "Brightness", self.centerX, self.top+150, self.width))
            self.sliders.append(Slider(app, "Contrast", self.centerX, self.top+250, self.width))
            self.sliders.append(Slider(app, "Saturation", self.centerX, self.top + 350, self.width))
            self.sliders.append(Slider(app, "Exposure", self.centerX, self.top + 450, self.width))
            self.sliders.append(Slider(app, "Temperature", self.centerX, self.top + 550, self.width))
            self.buttons.append(Button(app, self.centerX, self.height-50, rgb(100, 100, 100), rgb(60, 60, 60), self.width//2.3, 50))

    def update(self, app):
        self.width = app.width // 5
        self.height = app.height
        self.left = app.width - self.width
        self.centerX = self.left + self.width//2
        self.top = 0
        for slider in self.sliders:
            slider.updateSliderPosition(self.centerX, self.width)

    def drawSidebar(self, app):
        self.update(app)
        sideBarColor = rgb(45, 45, 45)
        borderColor = rgb(100, 100, 100)
        drawRect(self.left, self.top, self.width, self.height, fill = sideBarColor, borderWidth = 4, border = borderColor)
        drawLabel(self.title, self.centerX, self.top+50, fill = 'white', font = app.font, bold = True, size = 15, borderWidth = 1, border = 'white')     
        for slider in self.sliders:
            slider.drawSlider(app)
        for button in self.buttons:
            button.drawButton(app)
        drawLabel("Reset", self.centerX, self.height-50, fill = 'white', font = app.font, bold = True, size = 15)

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
        percent = (self.cx-self.start) / (self.end-self.start)
        self.x = x
        self.lineLength = (sidebarWidth - 70)//2
        self.start = self.x - self.lineLength
        self.end = self.x + self.lineLength
        self.cx = self.start + percent * (self.end-self.start)
    def drawSlider(self, app):
        drawLabel(self.name, self.x, self.y, size = 18, font = app.font, fill = 'white')
        drawLine(self.start, self.y + 25, self.end, self.y + 25, fill = 'white', lineWidth = 2)
        drawCircle(self.cx, self.cy, self.circleRadius, fill = rgb(200, 200, 200))

class Button:
    def __init__(self, app, centerX, centerY, border, color, width, height):
        self.centerX = centerX
        self.centerY = centerY
        self.border = border
        self.color = color
        self.width = width
        self.height = height
        self.opacity = 60
    def drawButton(self, app):
        drawRect(self.centerX, self.centerY, self.width, self.height, fill=self.color, border = self.border, borderWidth = 3, align = 'center', opacity = self.opacity)



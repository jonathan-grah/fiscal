# -*- coding: utf-8 -*-

import sys
from PySide2.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView, QScrollArea, QAbstractSlider, QMainWindow, QWidget, QLabel, QDockWidget)
from PySide2.QtCore import *
from PySide2.QtGui import *

countries = {
    "224, 20, 20": "Canada",
    "3, 50, 252": "United States",
    "4, 91, 62": "Mexico"
}

class InteractiveMap(QScrollArea):
    def __init__(self, parent):
        super(InteractiveMap, self).__init__(parent)
        self.setWidgetResizable(False)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # prevents unintended scrolling with middle mouse button
        self.horizontalScrollBar().setEnabled(False)
        self.verticalScrollBar().setEnabled(False)

        # setup properties of class
        self.isMouseMoving = False

        self.displayMap(2500, 2500)

    def displayMap(self, width, height):
        self.map = QImage("world_map.png").scaled(width, height, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        self.label = QLabel()
        self.label.setScaledContents(True)
        self.label.setPixmap(QPixmap.fromImage(self.map))
        self.label.show()

        self.setWidget(self.label)

    def scaleMap(self, zoom):
        # zooming in and out of map
        self.label.resize(
            self.label.width() + zoom,
            self.label.height() + zoom
        )

    def wheelEvent(self, event):
        movement = event.angleDelta().y()
        
        if (movement == 120):
            self.scaleMap(500)
        elif (movement == -120):
            self.scaleMap(-500)

    def findCountry(self, mousePosition):
        color = self.map.pixelColor(mousePosition)
        red = int(color.redF() * 255)
        green = int(color.greenF() * 255)
        blue = int(color.blueF() * 255)
        rgb = "%d, %d, %d" % (red, green, blue)

        # if colour matches to a country
        country = QLabel()
        if (rgb in countries):
            country.setText(countries[rgb])
        else:
            country.setText("Not found")
        country.setAlignment(Qt.AlignCenter)

        self.parent().showCountryDock(country)
        print(countries[rgb])

    def mousePressEvent(self, event):
        self.initialMousePosition = event.pos()
        self.initialSliderPosition = {
            "horizontal": self.horizontalScrollBar().value(),
            "vertical": self.verticalScrollBar().value()
        }

    def mouseMoveEvent(self, event):
        self.isMouseMoving = True

        changeX = self.initialMousePosition.x() - event.x()
        changeY = self.initialMousePosition.y() - event.y()

        self.horizontalScrollBar().setValue(self.initialSliderPosition["horizontal"] + changeX)
        self.verticalScrollBar().setValue(self.initialSliderPosition["vertical"] + changeY)

    def mouseReleaseEvent(self, event):
        if (not(self.isMouseMoving)):
            self.findCountry(event.pos() + QPoint(self.horizontalScrollBar().value(), self.verticalScrollBar().value()))
        self.isMouseMoving = False
    
class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        interactiveMap = InteractiveMap(self)
        self.setCentralWidget(interactiveMap)
        
        self.countryInfo = QDockWidget("Country Information", self)
        self.countryInfo.setFeatures(QDockWidget.DockWidgetClosable)
        self.countryInfo.setFixedWidth(300)

        self.addDockWidget(Qt.RightDockWidgetArea, self.countryInfo)

        self.setWindowTitle("Project Fiscal")
        self.showMaximized()

    def showCountryDock(self, country):
        self.countryInfo.setWidget(country)

app = QApplication(sys.argv)
gui = Window()
gui.show()
sys.exit(app.exec_())
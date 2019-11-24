# -*- coding: utf-8 -*-

import sys
from PySide2.QtWidgets import (QApplication, QGraphicsScene, QGraphicsView, QScrollArea, QAbstractSlider, QMainWindow, QWidget, QLabel)
from PySide2.QtCore import *
from PySide2.QtGui import *

countries = {
    "224, 20, 20": "Canada",
    "3, 50, 252": "United States",
    "4, 91, 62": "Mexico"
}

class InteractiveMap(QScrollArea):
    def __init__(self):
        super(InteractiveMap, self).__init__()
        self.setWidgetResizable(False)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # prevents scrolingscrolling 
        self.horizontalScrollBar().setEnabled(False)
        self.verticalScrollBar().setEnabled(False)

        self.map = QImage("world_map.png")
        
        label = QLabel()
        label.setPixmap(QPixmap.fromImage(self.map))
        label.show()

        self.setWidget(label)

    def mousePressEvent(self, event):
        self.initialMousePosition = event.pos()
        self.initialSliderPosition = {
            "horizontal": self.horizontalScrollBar().value(),
            "vertical": self.verticalScrollBar().value()
        }

        # color = self.map.pixelColor(event.pos())
        # red = int(color.redF() * 255)
        # green = int(color.greenF() * 255)
        # blue = int(color.blueF() * 255)
        # rgb = "%d, %d, %d" % (red, green, blue)

        # country = QLabel()
        # country.setText("helloworld")
        # country.setAlignment(Qt.AlignCenter)
        # country.show()
        # self.setWidget(country)

        # print(countries[rgb])
        

    def mouseMoveEvent(self, event):
        changeX = self.initialMousePosition.x() - event.x()
        changeY = self.initialMousePosition.y() - event.y()

        self.horizontalScrollBar().setValue(self.initialSliderPosition["horizontal"] + changeX)
        self.verticalScrollBar().setValue(self.initialSliderPosition["vertical"] + changeY)
    
class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("Project Fiscal")
        self.showMaximized()
        interactiveMap = InteractiveMap()
        self.setCentralWidget(interactiveMap)

app = QApplication(sys.argv)
gui = Window()
gui.show()
sys.exit(app.exec_())
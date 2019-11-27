# -*- coding: utf-8 -*-

import sys
from PySide2.QtWidgets import (QApplication, QGraphicsItem, QGraphicsScene, QGraphicsView, QScrollArea, QAbstractSlider, QMainWindow, QWidget, QLabel, QDockWidget)
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtSvg import *

class Country(QGraphicsSvgItem):
	def __init__(self, parent, country):
		super(Country, self).__init__()

		self.country = country
		self.parent = parent

		self.setSharedRenderer(parent.renderer)
		self.setElementId(self.country)

	def mouseMoveEvent(self, event):
		print("move")

	def mouseReleaseEvent(self, event):
		print("release")

	def mousePressEvent(self, event):
		print(self.country)
		self.parent.findCountry(self.country)
		self.ungrabMouse()

class InteractiveMap(QGraphicsView):
	def __init__(self, parent):
		super(InteractiveMap, self).__init__()
		
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		# prevents unintended scrolling with middle mouse button
		self.horizontalScrollBar().setEnabled(False)
		self.verticalScrollBar().setEnabled(False)

		self.displayMap()
		self.setScene(self.scene)
		self.scale(2, 2)

		# setup properties of class
		self.isMouseMoving = False

	def displayMap(self):
		self.scene = QGraphicsScene()

		self.renderer = QSvgRenderer("map.svg")

		self.ie = Country(self, "ie")
		self.ie.setPos(1243.335, 223.772)

		self.gb = Country(self, "gb")
		self.gb.setPos(1260.61, 179.859)

		self.es = Country(self, "es")
		self.es.setPos(1169.683, 320.315)

		self.fr = Country(self, "fr")
		self.fr.setPos(834.585, 258.535)

		self.ru = Country(self, "ru")
		self.ru.setPos(1439.66, 32.788)

		self.scene.addItem(self.gb)
		self.scene.addItem(self.ie)
		self.scene.addItem(self.es)
		self.scene.addItem(self.fr)
		self.scene.addItem(self.ru)

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
		self.isMouseMoving = False

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

	def findCountry(self, country):
		text = QLabel()
		if (True):
			text.setText(country)
		else:
			text.setText("Not found")
			text.setAlignment(Qt.AlignCenter)

		self.parent().showCountryDock(text)

class Window(QMainWindow):
	def __init__(self):
		super(Window, self).__init__()

		interactiveMap = InteractiveMap(self)
		self.setCentralWidget(interactiveMap)
		
		self.countryInfo = QDockWidget("Country Information", self)
		self.countryInfo.setFeatures(QDockWidget.DockWidgetClosable)
		self.countryInfo.setFixedWidth(300)
		self.countryInfo.hide()

		self.addDockWidget(Qt.RightDockWidgetArea, self.countryInfo)

		self.setWindowTitle("Project Fiscal")
		self.showMaximized()

	def showCountryDock(self, country):
		if (self.countryInfo.isHidden()):
			self.countryInfo.show()
		self.countryInfo.setWidget(country)

app = QApplication(sys.argv)
gui = Window()
gui.show()
sys.exit(app.exec_())
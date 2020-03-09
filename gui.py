# -*- coding: utf-8 -*-

import sys
import json

from PySide2.QtWidgets import (QApplication, QGraphicsItem, QGraphicsScene, QGraphicsPixmapItem, QGraphicsColorizeEffect, QGraphicsView, QScrollArea, QAbstractSlider, QMainWindow, QWidget, QLabel, QDockWidget)
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtSvg import *

class Country(QGraphicsSvgItem):
	def __init__(self, parent, id, country):
		super(Country, self).__init__()

		print(country["colour"], id)

		self.id = id
		self.country = country
		self.parent = parent

		self.setSharedRenderer(parent.renderer)
		self.setCacheMode(QGraphicsItem.ItemCoordinateCache)

		self.setElementId(self.id)

		self.setPos(self.country["position"]["x"], self.country["position"]["y"])
		self.setColour(self.country["colour"])

	def mousePressEvent(self, event):
		# self.parent.findCountry(self.country)
		print("mousePressEvent on", self.id)
		self.ungrabMouse()

	def setColour(self, colour):
		effect = QGraphicsColorizeEffect()
		effect.setColor(colour)
		self.setGraphicsEffect(effect)

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

		# setup properties of class
		self.isMouseMoving = False

	def displayMap(self):
		self.scene = QGraphicsScene()

		# display image layer for detecting mouse presses

		self.backgroundMapImg = QImage("resources/bg_map.png")

		self.backgroundMap = QGraphicsPixmapItem(QPixmap.fromImage(self.backgroundMapImg))
		self.scene.addItem(self.backgroundMap)

		# display individual countries as SVG elements

		self.renderer = QSvgRenderer("resources/map.svg")

		self.countries = {}
		with open("countries.json") as file:
			countries = json.load(file)
			
			for country in countries:
				self.countries[country] = Country(self, country, countries[country])
				self.scene.addItem(self.countries[country])

		# self.es = Country(self, "es")
		# self.es.setPos(1243.448, 320.3)
		# self.es.setColour("orange")

		# self.fr = Country(self, "fr")
		# self.fr.setPos(1277.77, 258.72)
		# self.fr.setColour("blue")

		# self.ru = Country(self, "ru")
		# self.ru.setPos(1439.66, 32.788)

		# self.scene.addItem(self.gb)
		# self.scene.addItem(self.ie)
		# self.scene.addItem(self.fr)
		# self.scene.addItem(self.ru)
		# self.scene.addItem(self.es)

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
		if (self.isMouseMoving):
			self.isMouseMoving = False
		else:
			# check what country corresponds to colour
			print("Normal click")

			# colour = self.backgroundMapImg.pixel(self.initialMousePosition.x(), self.initialMousePosition.y())
			# print(colour)

	def scaleMap(self, zoom):
		# zooming in and out of map

		zoom = zoom / 500 / 10
		self.scale(1 + zoom, 1 + zoom)

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
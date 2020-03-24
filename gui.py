# -*- coding: utf-8 -*-

import sys
import json

from PySide2.QtWidgets import (QApplication, QStyle, QGraphicsItem, QGraphicsScene, QGraphicsPixmapItem, QGraphicsColorizeEffect, QGraphicsView, QScrollArea, QAbstractSlider, QMainWindow, QWidget, QLabel, QDockWidget)
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtSvg import *


class Country(QGraphicsSvgItem):
	def __init__(self, parent, id, country):
		super(Country, self).__init__()

		self.id = id

		self.country = country

		self.name = country["name"]
		
		self.parent = parent

		self.setSharedRenderer(self.parent.renderer)
		self.setCacheMode(QGraphicsItem.ItemCoordinateCache)

		self.setElementId(self.id)

		self.setPos(self.country["position"]["x"], self.country["position"]["y"])

		# set colour of country
		self.colour = QColor()
		self.colour.setRgb(
			self.country["colour"]["r"],
			self.country["colour"]["g"],
			self.country["colour"]["b"]
		)

		self.setColour(self.colour)

		qDebug("Country initialised: " + self.country["name"])

	def paint(self, painter, option, widget):
		print(self.elementId())

		# partially reimplementing the function
		# https://code.woboq.org/qt5/qtsvg/src/svg/qgraphicssvgitem.cpp.html#_ZN16QGraphicsSvgItem5paintEP8QPainterPK24QStyleOptionGraphicsItemP7QWidget

		rect = self.boundingRect()
		# rect.setSize(QSizeF(rect.width() * self.parent.currentScale, rect.height() * self.parent.currentScale))

		if not(self.parent.renderer.isValid()):
			return
		if not(self.elementId()):
			self.parent.renderer.render(painter, rect)
		else:
			self.parent.renderer.render(painter, self.elementId(), rect)
		
		metrics = QFontMetrics(painter.font())
		x = rect.width() * 1.0 / metrics.width(self.name) - 0.4
		y = rect.height() * 1.0 / metrics.height() - 0.4

		painter.save()
		painter.translate(rect.center())
		painter.scale(min(x, y), min(x, y))
		painter.translate(-rect.center())

		# painter.setPen(Qt.red)
		# probale should change colour of text
		painter.drawText(rect, self.name, Qt.AlignHCenter | Qt.AlignVCenter)

		painter.restore()

	def mousePressEvent(self, event):
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
		self.initialSliderPosition = {
			"horizontal": 0,
			"vertical": 0
		}
		self.initialMousePosition = QPoint()
		self.isMouseMoving = False
		self.currentScale = 1

	def displayMap(self):
		self.scene = QGraphicsScene()

		# display image layer for detecting mouse presses

		self.backgroundMapImg = QImage()
		self.backgroundMapImg.load("resources/bg_map.png", "png")

		self.backgroundMap = QGraphicsPixmapItem(QPixmap.fromImage(self.backgroundMapImg))
		# self.backgroundMap.hide()
		self.scene.addItem(self.backgroundMap)

		# display individual countries as SVG elements

		self.renderer = QSvgRenderer()
		self.renderer.load("resources/uncoloured_map.svg")

		self.countries = {}
		with open("countries.json") as file:
			countries = json.load(file) # need to add error checking
			
			for country in countries:
				self.countries[country] = Country(self, country, countries[country])
				self.scene.addItem(self.countries[country])

	def mousePressEvent(self, event):
		if not(event.buttons() == Qt.RightButton or event.buttons() == Qt.MiddleButton):
			return event.ignore()

		self.initialMousePosition = event.pos()

		self.initialSliderPosition["horizontal"] = self.horizontalScrollBar().value()
		self.initialSliderPosition["vertical"] = self.verticalScrollBar().value()

	def mouseMoveEvent(self, event):
		if not(event.buttons() == Qt.RightButton or event.buttons() == Qt.MiddleButton):
			return event.ignore()

		self.isMouseMoving = True

		changeX = self.initialMousePosition.x() - event.x()
		changeY = self.initialMousePosition.y() - event.y()

		self.horizontalScrollBar().setValue(self.initialSliderPosition["horizontal"] + changeX)
		self.verticalScrollBar().setValue(self.initialSliderPosition["vertical"] + changeY)

	def mouseReleaseEvent(self, event):
		if self.isMouseMoving:
			self.isMouseMoving = False
		else:
			# check what country corresponds to colour
			if event.button() == Qt.LeftButton:
				pixelColour = self.backgroundMapImg.pixelColor((
					event.pos() +
					QPoint(self.horizontalScrollBar().value(), self.verticalScrollBar().value())
				) / self.currentScale)

				# linear search ???
				for country in self.countries:
					if self.countries[country].colour == pixelColour:
						return self.findCountry(self.countries[country].name)

				self.parent().countryInfo.hide()

	# def scaleMap(self, zoom):
	# 	# zooming in and out of map
	# 	qDebug(self.currentScale)
	# 	self.currentScale = 1 + zoom
	# 	qDebug(self.currentScale)

	# 	self.scale(self.currentScale, self.currentScale)

	# def wheelEvent(self, event):
	# 	movement = event.angleDelta().y()

	# 	if (movement == 120):
	# 		self.scaleMap(0.1)
	# 	elif (movement == -120):
	# 		self.scaleMap(-0.2)

	def findCountry(self, country):		
		text = QLabel()
		text.setText(country)

		self.parent().showCountryDock(text)
		
		qDebug("Country clicked: " + country)


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
		if self.countryInfo.isHidden():
			self.countryInfo.show()
		self.countryInfo.setWidget(country)


app = QApplication(sys.argv)
gui = Window()
gui.show()
sys.exit(app.exec_())
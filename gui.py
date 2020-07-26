# -*- coding: utf-8 -*-

import sys
import json

from PySide2.QtWidgets import (QApplication, QGraphicsItem, QGraphicsScene, QGraphicsPixmapItem,
                               QGraphicsColorizeEffect, QGraphicsView,
                               QMainWindow, QLabel, QDockWidget)
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtSvg import *

import db.countries, db.indicators


class Country(QGraphicsSvgItem):
    def __init__(self, parent, id, country):
        super(Country, self).__init__()

        self.id = id

        self.country = country

        self.name = country["name"]

        self.parent = parent

        self.setSharedRenderer(self.parent.renderer)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self.setElementId(self.id)

        self.setPos(self.country["position"]["x"], self.country["position"]["y"])

        # set colour of country
        self.colour = QColor()
        self.colour.setRgb(
            self.country["colour"]["r"],
            self.country["colour"]["g"],
            self.country["colour"]["b"]
        )

        qDebug("Country initialised: " + self.country["name"])

        # country will appear green when selected
        self.selectedEffect = QGraphicsColorizeEffect()
        self.selectedEffect.setColor("green")
        self.setGraphicsEffect(self.selectedEffect)

        # country is not selected by default
        self.deselectCountry()

    def selectCountry(self):
        self.selectedEffect.setEnabled(True)

    def deselectCountry(self):
        self.selectedEffect.setEnabled(False)

    def mousePressEvent(self, event):
        self.ungrabMouse()


class MajorCountry(Country):
    def __init__(self, parent):
        super(MajorCountry, self).__init__()


class InteractiveMap(QGraphicsView):
    def __init__(self, parent):
        super(InteractiveMap, self).__init__()

        # setup properties of class
        self.countries = {}
        self.scene = QGraphicsScene()
        self.backgroundMapImg = QImage()
        self.renderer = QSvgRenderer()
        self.initialSliderPosition = {
            "horizontal": 0,
            "vertical": 0
        }
        self.initialMousePosition = QPoint()
        self.isMouseMoving = False
        self.currentScale = 1.25
        self.currentlySelected = ""

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # prevents unintended scrolling with middle mouse button
        self.horizontalScrollBar().setEnabled(False)
        self.verticalScrollBar().setEnabled(False)

        self.displayMap()
        self.setScene(self.scene)

        self.scale(self.currentScale, self.currentScale)

        # scroll area of map is centered around Europe
        self.horizontalScrollBar().setValue(1500)
        self.verticalScrollBar().setValue(100)

    def displayMap(self):
        # TODO: modulate the gui.py file more

        # set the background behind countries to be blue (representing the sea)
        seaColouredBrush = QBrush(QColor("lightskyblue"))
        self.setBackgroundBrush(seaColouredBrush)

        # display image layer for detecting mouse presses

        self.backgroundMapImg.load("resources/bg_map.png", "png")
        self.backgroundMap = QGraphicsPixmapItem(QPixmap.fromImage(self.backgroundMapImg))
        self.backgroundMap.hide()

        self.scene.addItem(self.backgroundMap)

        # display individual countries as SVG elements

        self.renderer.load("resources/coloured_map_no_text.svg")

        # TODO: Should only occur when the bootstrapping "script" is run

        with open("countries.json") as file:
            countries = json.load(file)
            # TODO: need to add error checking for opening json file

            for country in countries:
                self.countries[country] = Country(self, country, countries[country])

                # country added to the database
                db.countries.add({
                    "iso": countries[country]["iso"],
                    "name": countries[country]["name"],
                    "knoemaKey": countries[country]["datasetIdentifiers"]["knoemaKey"],
                    "knoemaRegionId": countries[country]["datasetIdentifiers"]["knoemaRegionId"]
                })

                self.scene.addItem(self.countries[country])

            # MAKESHIFT BOOTSTRAPPING CODE
            # TODO: A button should trigger this instead and somewhere else

            # db.indicators.createIndicatorTypes()
            # db.countries.grabCountryData()

    def mousePressEvent(self, event):
        if not (event.buttons() == Qt.RightButton or event.buttons() == Qt.MiddleButton):
            return event.ignore()

        self.initialMousePosition = event.pos()

        self.initialSliderPosition["horizontal"] = self.horizontalScrollBar().value()
        self.initialSliderPosition["vertical"] = self.verticalScrollBar().value()

    def mouseMoveEvent(self, event):
        if not (event.buttons() == Qt.RightButton or event.buttons() == Qt.MiddleButton):
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
                # get the colour of the pixel on the background map image that is currently selected by the pointer
                pixelColour = self.backgroundMapImg.pixelColor((
                                                                       event.pos() +
                                                                       QPoint(self.horizontalScrollBar().value(),
                                                                              self.verticalScrollBar().value())
                                                               ) / self.currentScale)

                # if a country is already selected, deselect it
                if self.currentlySelected:
                    self.countries[self.currentlySelected].deselectCountry()

                # linear search ???
                for country in self.countries:
                    if self.countries[country].colour == pixelColour:
                        self.countries[country].selectCountry()
                        self.currentlySelected = country

                        return self.findCountry(self.countries[country].name)

                self.parent().countryInfo.hide()

    def scaleMap(self, movement):
        # zooming in and out of map

        if movement == "in":
            self.scale(1.25, 1.25)
        elif movement == "out":
            self.scale(0.75, 0.75)

        # self.transform.m11() refers to the horizontal scale factor
        # this is updated in order to ensure that mouse presses on countries are still detected when scale is changed
        self.currentScale = self.transform().m11()

    def wheelEvent(self, event):
        movement = event.angleDelta().y()

        if movement == 120:
            self.scaleMap("in")
        elif movement == -120:
            self.scaleMap("out")

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

    def showCountryDock(self, country):
        if self.countryInfo.isHidden():
            self.countryInfo.show()
        self.countryInfo.setWidget(country)


app = QApplication(sys.argv)
gui = Window()
gui.show()
sys.exit(app.exec_())

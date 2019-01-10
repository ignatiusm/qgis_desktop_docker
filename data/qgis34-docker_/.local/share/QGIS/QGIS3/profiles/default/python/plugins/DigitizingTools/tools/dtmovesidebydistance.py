# -*- coding: utf-8 -*-
"""
dtmovesidebydistance
````````````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

* begin                : 2013-08-15
* copyright            : (C) 2013 by Angelos Tzotsos
* email                : tzotsos@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from builtins import object
from qgis.PyQt import QtCore,  QtGui, QtWidgets
from qgis.core import *
from qgis.gui import *

import dt_icons_rc
from dttools import DtSelectSegmentTool
from dtmovesidebydistance_dialog import DtMoveSideByDistance_Dialog

class DtMoveSideByDistance(object):
    '''Automatically move polygon node (along a given side of polygon) in order to achieve a desired polygon area'''
    def __init__(self, iface,  toolBar):
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        self.gui = None
        self.multipolygon_detected = False

        # points of the selected segment
        # p1 is always the left point
        self.p1 = None
        self.p2 = None
        self.rb1 = QgsRubberBand(self.canvas,  False)
        #self.m1 = None
        self.selected_feature = None

        #create action
        self.side_mover = QtWidgets.QAction(QtGui.QIcon(":/ParallelMovePolygonSideByDistance.png"),
            QtWidgets.QApplication.translate("digitizingtools", "Parallel move of polygon side to given distance"),  self.iface.mainWindow())

        self.side_mover.triggered.connect(self.run)
        self.iface.currentLayerChanged.connect(self.enable)
        toolBar.addAction(self.side_mover)
        self.enable()

        self.tool = DtSelectSegmentTool(self.iface)

    def showDialog(self):
        flags = QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        self.gui = DtMoveSideByDistance_Dialog(self.iface.mainWindow(),  flags)
        self.gui.initGui()
        self.gui.show()
        self.gui.unsetTool.connect(self.unsetTool)
        self.gui.moveSide.connect(self.moveSide)

    def enableSegmentTool(self):
        self.canvas.setMapTool(self.tool)
        #Connect to the DtSelectVertexTool
        self.tool.segmentFound.connect(self.storeSegmentPoints)

    def unsetTool(self):
        self.p1 = None
        self.p2 = None
        self.selected_feature = None
        self.canvas.unsetMapTool(self.tool)

    def run(self):
        '''Function that does all the real work'''
        layer = self.iface.activeLayer()
        if(layer.dataProvider().wkbType() == 6):
            self.multipolygon_detected = True
        title = QtWidgets.QApplication.translate("digitizingtools", "Move polygon side by distance")

        if layer.selectedFeatureCount() == 0:
            QtWidgets.QMessageBox.information(None, title,  QtWidgets.QApplication.translate("digitizingtools", "Please select one polygon to edit."))
        elif layer.selectedFeatureCount() > 1:
            QtWidgets.QMessageBox.information(None, title,  QtWidgets.QApplication.translate("digitizingtools", "Please select only one polygon to edit."))
        else:
            #One selected feature
            self.selected_feature = layer.selectedFeatures()[0]
            self.enableSegmentTool()
            self.showDialog()

    def storeSegmentPoints(self,  result):
        if result[0].x() < result[1].x():
            self.p1 = result[0]
            self.p2 = result[1]
        elif result[0].x() == result[1].x():
            self.p1 = result[0]
            self.p2 = result[1]
        else:
            self.p1 = result[1]
            self.p2 = result[0]

    def enable(self):
        '''Enables/disables the corresponding button.'''
        # Disable the Button by default
        self.side_mover.setEnabled(False)
        layer = self.iface.activeLayer()

        if layer != None:
            #Only for vector layers.
            if layer.type() == QgsMapLayer.VectorLayer:
                # only for polygon layers
                if layer.geometryType() == 2:
                    # enable if editable
                    self.side_mover.setEnabled(layer.isEditable())
                    try:
                        layer.editingStarted.disconnect(self.enable) # disconnect, will be reconnected
                    except:
                        pass
                    try:
                        layer.editingStopped.disconnect(self.enable) # when it becomes active layer again
                    except:
                        pass
                    layer.editingStarted.connect(self.enable)
                    layer.editingStopped.connect(self.enable)

    def moveSide(self):
        dist = 0.0
        try:
            dist = float(self.gui.targetDistance.text())
        except:
            pass

        if (dist == 0.0):
            QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate("digitizingtools", "Cancel"), QtWidgets.QApplication.translate("digitizingtools", "Target Distance not valid."))
            return

        if self.p1 == None or self.p2 == None:
            QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate("digitizingtools", "Cancel"), QtWidgets.QApplication.translate("digitizingtools", "Polygon side not selected."))
        else:
            touch_p1_p2 = self.selected_feature.geometry().touches(QgsGeometry.fromPolyline([QgsPoint(self.p1), QgsPoint(self.p2)]))
            if (not touch_p1_p2):
                QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate("digitizingtools", "Cancel"), QtWidgets.QApplication.translate("digitizingtools", "Selected segment should be on the selected polygon."))
            else:
                new_geom = createNewGeometry(self.selected_feature.geometry(), self.p1, self.p2, dist, self.multipolygon_detected)
                fid = self.selected_feature.id()
                layer = self.iface.activeLayer()
                layer.beginEditCommand(QtWidgets.QApplication.translate("editcommand", "Move Side By Distance"))
                layer.changeGeometry(fid,new_geom)
                self.canvas.refresh()
                layer.endEditCommand()


def createNewGeometry(geom, p1, p2, new_distance, multipolygon):

    pointList = []
    if(multipolygon):
        pointList = geom.asMultiPolygon()[0][0][0:-1]
    else:
        pointList = geom.asPolygon()[0][0:-1]
    #Read input polygon geometry as a list of QgsPoints

    #indices
    ind = 0
    ind_max = len(pointList)-1
    p1_indx = -1
    p2_indx = -1

    #find p1 and p2 in the list
    for tmp_point in pointList:
        if (tmp_point == p1):
            p1_indx = ind
        elif (tmp_point == p2):
            p2_indx = ind
        ind += 1

    (p3,p4)=getParallelLinePoints(p1,p2,new_distance)

    pointList[p1_indx] = p3
    pointList[p2_indx] = p4
    new_geom = QgsGeometry.fromPolygonXY( [ pointList ] )

    return new_geom

def getParallelLinePoints(p1,  p2, dist):
    """
    This function is adopted/adapted from 'CadTools Plugin', Copyright (C) Stefan Ziegler
    """
    if dist == 0:
        g = (p1, p2)
        return g

    dn = ( (p1.x()-p2.x())**2 + (p1.y()-p2.y())**2 )**0.5
    x3 = p1.x() + dist*(p1.y()-p2.y()) / dn
    y3 = p1.y() - dist*(p1.x()-p2.x()) / dn
    p3 = QgsPointXY(x3,  y3)

    x4 = p2.x() + dist*(p1.y()-p2.y()) / dn
    y4 = p2.y() - dist*(p1.x()-p2.x()) / dn
    p4 = QgsPointXY(x4,  y4)

    g = (p3,p4)
    return g

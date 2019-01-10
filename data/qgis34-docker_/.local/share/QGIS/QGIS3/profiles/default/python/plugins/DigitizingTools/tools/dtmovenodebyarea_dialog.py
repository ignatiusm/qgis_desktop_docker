# -*- coding: utf-8 -*-
"""
dtmovenodebyarea_dialog
```````````````````````
"""
"""
Part of DigitizingTools, a QGIS plugin that
subsumes different tools neded during digitizing sessions

* begin                : 2013-08-14
* copyright            : (C) 2013 by Angelos Tzotsos
* email                : tzotsos@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

from builtins import str
from qgis.PyQt import QtCore, QtWidgets, uic
import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_dtmovenodebyarea.ui'))

class DtMoveNodeByArea_Dialog(QtWidgets.QDialog, FORM_CLASS):
    unsetTool = QtCore.pyqtSignal()
    moveNode = QtCore.pyqtSignal()

    def __init__(self, parent, flags):
        super().__init__(parent,  flags)
        self.setupUi(self)

    def initGui(self):
        pass

    def writeArea(self, area):
        self.area_label.setText(str(area))
        self.targetArea.setText(str(area))

    @QtCore.pyqtSlot()
    def on_buttonClose_clicked(self):
        self.unsetTool.emit()
        self.close()

    @QtCore.pyqtSlot()
    def on_moveButton_clicked(self):
        self.moveNode.emit()
        pass

import yaml

import gui.GUIbuttons as gb
import os
import sys

from bin.read_yaml import read_yaml
from lib.FitsKeyword import FitsKeyword
from lib.HLSPFile import HLSPFile

try:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *


class UpdateKeywordsGUI(QWidget):

    def __init__(self, parent):
        self.master = parent
        self.product_type = []
        self.standard = []
        for ftype in self.master.hlsp.file_types:
            if ftype["ProductType"] not in self.product_type:
                self.product_type.append(ftype["ProductType"])
            if ftype["Standard"] not in self.standard:
                self.standard.append(ftype["Standard"])
        self.product_type = (self.product_type[0]
                             if len(self.product_type) == 1
                             else None
                             )
        self.standard = (self.standard[0] if len(self.standard) == 1 else None)


# --------------------


class FitsKeywordModel(QAbstractTableModel):
    """
    Create a QAbstractTableModel to display Pandas DataFrame objects in a
    QTableView widget.
    """

    def __init__(self, pdframe, parent=None):
        """
        Upon initialization, move the data into a numpy array (faster) and set
        up variables.
        """

        super().__init__(parent)
        self._data = np.array(pdframe.values)
        self._ind = pdframe.index
        self._cols = pdframe.columns
        self._row_count, self._col_count = np.shape(self._data)
        if self._ind.dtype == "int64":
            self._ind = [str(x) for x in range(1, self._row_count+1)]

    def rowCount(self, parent=None):
        return self._row_count

    def columnCount(self, parent=None):
        return self._col_count

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return self._data[index.row(), index.column()]
        return None

    def headerData(self, p_int, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal and self.columnCount() > 0:
                return self._cols[p_int]
            elif orientation == Qt.Vertical and self.rowCount() > 0:
                return self._ind[p_int]
        return None

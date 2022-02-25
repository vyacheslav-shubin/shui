from PyQt5 import (QtCore, QtWidgets)
from .controls import GCodeActionsControl
import re

class PrinterControlTab(QtWidgets.QWidget):
    rows=[]
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.uartControls=[]
        self.app.onUartRow.connect(self.addRow)
        self.app.onUartMessage.connect(self.addRow)
        self.title = self.app.lang["printer"]
        self.axesControl=GCodeActionsControl(self, self.app)

        self.teConsoleOutput = QtWidgets.QTextEdit(self)
        self.teConsoleOutput.setReadOnly(True)
        self.teConsoleOutput.setStyleSheet("*{background-color: black; color:rgb(0,255,0)}")
        self.leHotendTemp = QtWidgets.QLineEdit(self)
        self.leHotendTemp.setReadOnly(True)
        self.leBedTemp = QtWidgets.QLineEdit(self)
        self.leBedTemp.setReadOnly(True)


        self.mainLayout=QtWidgets.QHBoxLayout()
        self.rightLayout=QtWidgets.QVBoxLayout()
        self.leftLayout=QtWidgets.QVBoxLayout()
        self.leftLayout.addWidget(self.axesControl)
        self.leftLayout.addStretch()
        self.mainLayout.addLayout(self.leftLayout)
        self.mainLayout.addStretch()
        self.mainLayout.addLayout(self.rightLayout)
        self.temperatureViewLayout=QtWidgets.QHBoxLayout()
        self.temperatureViewLayout.addWidget(self.leHotendTemp)
        self.temperatureViewLayout.addWidget(self.leBedTemp)
        self.rightLayout.addLayout(self.temperatureViewLayout)
        self.rightLayout.addWidget(self.teConsoleOutput)
        self.rightLayout.addStretch()

        self.setLayout(self.mainLayout)
        #ok T0:24.00 /0.00 B:84.09 /70.00 T0:24.00 /0.00 T1:116.75 /0.00 @:0 B@:0 @0:0 @1:0
    def filterRow(self, row):
        if row[:5]=='ok T0':
            match = re.search(r'T0\:(\d+\.\d+)\s*\/(\d+\.\d+)\s*B\:(\d+\.\d+)\s*\/(\d+\.\d+)', row)
            if match:
                self.leHotendTemp.setText("T:{0}/{1}".format(match[1], match[2]))
                self.leBedTemp.setText("B:{0}/{1}".format(match[3], match[4]))
            return False
        return True

    def addRow(self, row):
        if self.filterRow(row):
            self.rows.append(row)
            if len(self.rows)>20:
                self.rows.pop(0)
            self.teConsoleOutput.setText("\n".join(self.rows))
            self.teConsoleOutput.verticalScrollBar().setValue(self.teConsoleOutput.verticalScrollBar().maximum())
        pass


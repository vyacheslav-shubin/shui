from PyQt5 import (QtCore, QtWidgets)


class ConsoleTab(QtWidgets.QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.title = self.app.lang["terminal"]
        self.app.onUartRow.connect(self.addRow)
        self.app.onUartMessage.connect(self.addRow)
        self.app.onUartConnect.connect(self.onUartConnect)
        self.rows=[]
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        self.teConsoleOutput = QtWidgets.QTextEdit(self)
        self.teConsoleOutput.setReadOnly(True)

        self.teConsoleOutput.setStyleSheet("*{background-color: black; color:rgb(0,255,0)}")
        self.slGCodeMessage = QtWidgets.QLineEdit(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.slGCodeMessage.sizePolicy().hasHeightForWidth())
        self.slGCodeMessage.setSizePolicy(sizePolicy)
        self.teConsoleOutput.setSizePolicy(sizePolicy)

        self.btSenb = QtWidgets.QPushButton()
        self.btSenb.setMaximumSize(QtCore.QSize(100, 16777215))
        self.btSenb.setMinimumWidth(100)
        self.btSenb.setText("Send")
        self.btSenb.setDisabled(True)


        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.addWidget(self.teConsoleOutput)
        #self.setLayout(self.mainLayout)

        self.sendLayout = QtWidgets.QHBoxLayout()
        self.sendLayout.addWidget(self.slGCodeMessage)
        self.sendLayout.addWidget(self.btSenb)
        self.sendLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addLayout(self.sendLayout)

        self.btSenb.clicked.connect(self.doSend)
        self.addRow(self.app.lang["title"])
        pass

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.doSendKeyPress(event)

    def addRow(self, row):
        self.rows.append(row)
        if len(self.rows)>20:
            self.rows.pop(0)
        self.teConsoleOutput.setText("\n".join(self.rows))
        self.teConsoleOutput.verticalScrollBar().setValue(self.teConsoleOutput.verticalScrollBar().maximum())
        pass

    def onUartConnect(self, state):
        self.btSenb.setDisabled(not state)
        if state:
            self.addRow("Connected")
        else:
            self.addRow("Disconnected")
        pass

    def doSend(self):
        self.addRow(self.slGCodeMessage.text())
        self.app.wifiUart.send(self.slGCodeMessage.text())
        pass

    def doSendKeyPress(self, event):
        if (event.key() == QtCore.Qt.Key_Enter) or (event.key() == QtCore.Qt.Key_Return):
            self.doSend()

from PyQt5 import (QtCore, QtWidgets, QtGui)
from .Core import StartMode

class FileTab(QtWidgets.QWidget):
    parser = None
    locked = False

    def __init__(self, app):
        super().__init__()
        self.app=app
        self.title = self.app.lang["file"]
        self.app.onUploadFinished.connect(self.onFinised)
        self.app.onProgress.connect(self.onProgress)
        self.app.onMessage.connect(self.onMessage)

        mainLayout=QtWidgets.QHBoxLayout()

        self.bigPic = QtWidgets.QLabel()
        self.bigPic.setFixedWidth(200)
        self.bigPic.setFixedHeight(200)

        mainLayout.addWidget(self.bigPic,  alignment=QtCore.Qt.AlignTop)

        rightArea = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(rightArea)

        actions_layout = QtWidgets.QVBoxLayout()
        cb = QtWidgets.QCheckBox(self.app.lang["start-printing"])
        cb.setChecked(True)
        self.cbStartPrinting=cb
        actions_layout.addWidget(cb)

        file_name_layout = QtWidgets.QHBoxLayout()
        file_name_layout.addWidget(QtWidgets.QLabel(self.app.lang["output-name"]), alignment=QtCore.Qt.AlignLeft)
        self.leFileName = QtWidgets.QLineEdit()
        if self.app.outputFileName is not None:
            self.leFileName.setText(self.app.outputFileName)
        self.leFileName.setMaxLength(32)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.leFileName.setSizePolicy(sizePolicy)
        file_name_layout.addWidget(self.leFileName, alignment=QtCore.Qt.AlignLeft)

        progress_layout = QtWidgets.QVBoxLayout()
        progress=QtWidgets.QProgressBar()
        progress_layout.addWidget(progress)
        progress.setMaximum(100)
        progress.setValue(0)
        self.progress = progress

        progress_label=QtWidgets.QLabel()
        progress_layout.addWidget(progress_label)
        self.progress_label=progress_label
        progress_label.setText("---")

        buttons_layout = QtWidgets.QHBoxLayout()
        self.okButton = QtWidgets.QPushButton("OK")
        #self.okButton.setMaximumSize(QtCore.QSize(200, 16777215))
        #self.cancelButton = QtWidgets.QPushButton("Cancel")
        #buttons_layout.addWidget(self.cancelButton)
        buttons_layout.addWidget(self.okButton, alignment=QtCore.Qt.AlignRight)

        rightArea_top=QtWidgets.QVBoxLayout()
        rightArea_bottom=QtWidgets.QVBoxLayout()
        rightArea_bottom.setAlignment(QtCore.Qt.AlignBottom)
        rightArea_top.setAlignment(QtCore.Qt.AlignTop)
        rightArea.addLayout(rightArea_top)
        rightArea.addLayout(rightArea_bottom)

        actions_layout.setAlignment(QtCore.Qt.AlignTop)
        buttons_layout.setAlignment(QtCore.Qt.AlignBottom)
        progress_layout.setAlignment(QtCore.Qt.AlignBottom)
        file_name_layout.setAlignment(QtCore.Qt.AlignLeft)

        rightArea_top.addLayout(actions_layout)
        rightArea_top.addLayout(file_name_layout)
        rightArea_bottom.addLayout(progress_layout)
        rightArea_bottom.addLayout(buttons_layout)

        self.okButton.clicked.connect(self.onOk)

        self.setLayout(mainLayout)
        self.loadSource()
        pass

    def onOk(self, a):
        if self.locked:
            if self.sender is not None and self.sender.reply is not None:
                if self.sender.reply.isRunning():
                    self.sender.reply.abort()
        else:
            menu=QtWidgets.QMenu(self)

            newAct = QtWidgets.QAction(self.app.lang["save-to-file"], menu)
            newAct.triggered.connect(self.onSaveToFile)
            menu.addAction(newAct)

            newAct = QtWidgets.QAction(self.app.lang["send-to-printer"], menu)
            newAct.triggered.connect(self.onSendToWifi)
            menu.addAction(newAct)

            newAct = QtWidgets.QAction(self.app.lang["send-to-yandex"], menu)
            newAct.triggered.connect(self.onSendToYandexDisk)
            menu.addAction(newAct)

            menu.exec_(self.mapToGlobal(self.okButton.pos()))

    def onProgress(self, current, max):
        self.progress.setMaximum(max)
        self.progress.setValue(current)
        pass

    def onMessage(self, message):
        self.progress_label.setText(message)
        pass

    def onSaveToFile(self):
        try:
            self.onProgress(0, 1)
            from .FileSaver import FileSaver
            fileSaver=FileSaver(self.app)
            fileSaver.save(self.parser.getProcessedGcode())
        except Exception as e:
            self.onMessage(str(e))
        pass

    def onSendToYandexDisk(self):
        try:
            self.onProgress(0, 1)
            from .YandexSender import YandexSender
            self.lockUILock(True)
            wifiSender=YandexSender(self.app, self.leFileName.text())
            self.sender=wifiSender
            wifiSender.save(self.parser.getProcessedGcode())
        except Exception as e:
            self.onMessage(str(e))
            self.onFinised(False)
        pass

    def onSendToWifi(self):
        try:
            self.onProgress(0, 1)
            from .WifiSender import WifiSender
            wifiSender=WifiSender(self.app, self.leFileName.text())
            self.lockUILock(True)
            wifiSender.save(self.parser.getProcessedGcode(), start=True)
            self.sender=wifiSender
        except Exception as e:
            self.onMessage(str(e))
            self.onFinised(False)
        pass

    def lockUILock(self, locked):
        if locked:
            self.okButton.setText("Terminate")
        else:
            self.okButton.setText("Ok")
        self.locked=locked
        pass

    def loadSource(self):
        if self.app.startMode==StartMode.PRUSA or self.app.startMode==StartMode.STANDALONE:
            from .PrusaGcodeParser import PrusaGCodeParser
            self.parser=PrusaGCodeParser(self.app.inputFileName)
        elif self.app.startMode==StartMode.CURA:
            from .CuraGCodeParser import CuraGCodeParser
            self.parser=CuraGCodeParser()

        if self.parser is not None:
            self.parser.parse()
            self.bigPic.setPixmap(self.parser.getLargePreview())

    def onFinised(self, state):
        self.lockUILock(False)
        self.sender=None
        pass
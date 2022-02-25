import os
import sys
from sys import argv
import json

from PyQt5 import (QtCore, QtWidgets)
from .utils import (ConnectionThread, Core, ConsoleTab, FileTab, PrinterControlTab)
from PyQt5.QtNetwork import (QNetworkAccessManager, QNetworkProxy)


class App(QtCore.QObject):
    wifiUart=None
    config=None
    selectedPrinter = 0
    startMode = Core.StartMode.UNKNOWN
    outputFileName=None
    inputFileName=None

    onProgress = QtCore.pyqtSignal(object, object)
    onMessage = QtCore.pyqtSignal(object)
    onUploadFinished = QtCore.pyqtSignal(object)
    onUartRow = QtCore.pyqtSignal(object)
    onUartMessage = QtCore.pyqtSignal(object)
    onUartConnect = QtCore.pyqtSignal(object)

    def __init__(self, appStartMode, **kwargs):
        super().__init__()
        self.startMode=appStartMode
        if appStartMode==Core.StartMode.PRUSA:
            self.startMode = Core.StartMode.PRUSA
            self.outputFileName = os.getenv('SLIC3R_PP_OUTPUT_NAME')
            if self.outputFileName is not None:
                self.outputFileName=os.path.basename(self.outputFileName)
            self.inputFileName=sys.argv[1]
        elif appStartMode==Core.StartMode.STANDALONE:
            if len(argv)>1:
                self.inputFileName=sys.argv[1]
            else:
                if os.getenv('START_MODE')=='TEST':
                    self.inputFileName="/home/shubin/electronic/firmware/mks-robin/my/shui-src/bh.gcode"
            pass
        elif appStartMode==Core.StartMode.CURA:
            if "output_file_name" in kwargs:
                self.outputFileName = kwargs["output_file_name"]

        if self.inputFileName is not None and self.outputFileName is None:
            self.outputFileName = os.path.basename(self.inputFileName)
        self.wifiUart = ConnectionThread(self)
        config_file="config_local.json" if os.getenv('USER')=='shubin' else "config.json"
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..", config_file)) as jf:
            self.config=json.load(jf)
            jf.close()

        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"langs.json")) as lf:
            langs_cfg=json.load(lf)
            lf.close()

        selected=self.config["language"]
        self.lang={}
        if "inherited" in langs_cfg[selected]:
            for inh in langs_cfg[selected]["inherited"]:
                self.lang=langs_cfg[inh]["lang"]
        self.lang.update(langs_cfg[selected]["lang"])

        self.proxy=QNetworkProxy()

        if "proxy" in self.config:
            proxy_config=self.config["proxy"]
            if proxy_config["enabled"]:
                if "host" in proxy_config:
                    self.proxy.setHostName(proxy_config["host"])
                if "port" in proxy_config:
                    self.proxy.setPort(proxy_config["port"])
                if "user" in proxy_config:
                    self.proxy.setUser(proxy_config["user"])
                if "password" in proxy_config:
                    self.proxy.setPassword(proxy_config["password"])
                self.proxy.setType(QNetworkProxy.HttpProxy)

        self.networkManager = QNetworkAccessManager()
        self.networkManager.setProxy(self.proxy)

        pass


class MainWidget(QtWidgets.QDialog):
    def __init__(self, app):
        super().__init__()
        self.app=app
        self.setWindowTitle(self.app.lang["title"])
        self.setFixedWidth(500)
        self.setFixedHeight(300)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        self.mainLayout.setContentsMargins(2, 2, 2, 2)
        self.mainLayout.setSpacing(0)
        self.printerSelectLayout = QtWidgets.QHBoxLayout()
        self.cbPrinterSelect = QtWidgets.QComboBox(self)
        pn=[]
        for p in self.app.config["printers"]:
            pn.append(p["name"])
        self.cbPrinterSelect.addItems(pn)
        self.cbPrinterSelect.currentIndexChanged.connect(self.printerChanged)


        self.btConnect = QtWidgets.QPushButton(self)
        self.btConnect.setMaximumSize(QtCore.QSize(100, 16777215))

        self.btClose = QtWidgets.QPushButton(self)
        self.btClose.setMaximumSize(QtCore.QSize(100, 16777215))
        self.btClose.setText(self.app.lang["close"])

        self.printerSelectLayout.addWidget(self.cbPrinterSelect)
        self.printerSelectLayout.addWidget(self.btConnect)
        self.printerSelectLayout.addWidget(self.btClose)

        self.printerSelectLayout.setContentsMargins(2, 2, 2, 2)

        self.tabWidget = QtWidgets.QTabWidget(self)

        self.mainLayout.addLayout(self.printerSelectLayout)
        self.mainLayout.addWidget(self.tabWidget)

        self.makeTabs()

        self.btConnect.clicked.connect(self.doConnect)
        self.btClose.clicked.connect(self.doClose)
        self.app.onUartConnect.connect(self.doOnConnect)
        self.doOnConnect(False)
        pass

    def doClose(self):
        self.close()
        pass

    def makeTabs(self):
        self.tabs = []

        tab = FileTab(self.app)
        self.tabs.append(tab)
        self.tabWidget.addTab(tab, tab.title)

        tab = PrinterControlTab(self.app)
        self.tabs.append(tab)
        self.tabWidget.addTab(tab, tab.title)

        tab = ConsoleTab(self.app)
        self.tabs.append(tab)
        self.tabWidget.addTab(tab, tab.title)

        pass

    def doConnect(self):
        if self.app.wifiUart.connected:
            self.app.wifiUart.disconnect()
        else:
            self.app.wifiUart.connect(self.app.config["printers"][self.app.selectedPrinter]["ip"])
        pass

    def doOnConnect(self, connected):
        if connected:
            self.btConnect.setText(self.app.lang["disconnect"])
        else:
            self.btConnect.setText(self.app.lang["connect"])

    def printerChanged(self, index):
        self.app.selectedPrinter = index
        pass

def makeForm(startMode, **kwargs):
    app=App(startMode, **kwargs)
    form = MainWidget(app)
    form.show()
    return form

def cura_application(**kwargs):
    return makeForm(Core.StartMode.CURA, **kwargs)

def qt_application(startMode):
    import sys
    application = QtWidgets.QApplication(sys.argv)
    form = makeForm(startMode)
    sys.exit(application.exec_())

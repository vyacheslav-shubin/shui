from PyQt5 import QtCore, QtGui, QtWidgets


class ShuiToolButton(QtWidgets.QToolButton):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app=app
        self.setMinimumSize(QtCore.QSize(50, 40))


class ShuiSnippetToolButton(ShuiToolButton):
    onSnippet = QtCore.pyqtSignal(object)
    snippet=None

    def __init__(self, parent, app, snippet):
        super().__init__(parent, app)
        self.snippet=snippet
        self.clicked.connect(lambda: self.onSnippet.emit(self.snippet))



class GCodeActionsControl(QtWidgets.QWidget):
    step=1
    uartControls=[]
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app=app
        self.app.onUartConnect.connect(self.onUartConnect)
        self.gridLayout = QtWidgets.QGridLayout(self)

        self.tbMoveYPlus=ShuiToolButton(self, app)
        self.tbMoveYPlus.setText("Y+")
        self.tbMoveYMinus=ShuiToolButton(self, app)
        self.tbMoveYMinus.setText("Y-")

        self.tbMoveXPlus=ShuiToolButton(self, app)
        self.tbMoveXPlus.setText("X-")
        self.tbMoveXMinus=ShuiToolButton(self, app)
        self.tbMoveXMinus.setText("X-")

        self.tbMoveZMinus=ShuiToolButton(self, app)
        self.tbMoveZMinus.setText("Z-")

        self.tbMoveZPlus=ShuiToolButton(self, app)
        self.tbMoveZPlus.setText("Z+")

        self.tbStep=ShuiToolButton(self, app)
        self.tbStep.setText(str(self.step))


        self.gridLayout.addWidget(self.tbMoveYPlus, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.tbMoveXMinus, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.tbMoveXPlus, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.tbMoveYMinus, 2, 1, 1, 1)

        self.gridLayout.addWidget(self.tbMoveZPlus, 0, 3, 1, 1)
        self.gridLayout.addWidget(self.tbMoveZMinus, 2, 3, 1, 1)


        if "snippets" in self.app.config:
            idx=0
            self.snippet_btns = []
            for s in self.app.config["snippets"]:
                btn=ShuiSnippetToolButton(self, app, self.app.config["snippets"][s])
                btn.setText(s)
                self.gridLayout.addWidget(btn, 3+(idx/4), (idx%4), 1, 1)
                self.snippet_btns.append(btn)
                btn.onSnippet.connect(self.onSnippet)
                idx=idx+1
                if idx==8:
                    break
                print(s)

        self.uartControls=self.uartControls + [self.tbMoveXPlus,self.tbMoveYPlus,self.tbMoveZPlus,self.tbMoveXMinus, self.tbMoveYMinus,self.tbMoveZMinus]+self.snippet_btns

        for c in self.uartControls:
            c.setDisabled(True)

        self.gridLayout.addWidget(self.tbStep, 1, 1, 1, 1)

        self.tbStep.clicked.connect(lambda: self.onStep(1))

        self.tbMoveYPlus.clicked.connect(lambda: self.onMove("Y", 1))
        self.tbMoveYMinus.clicked.connect(lambda: self.onMove("Y", -1))
        self.tbMoveXPlus.clicked.connect(lambda: self.onMove("X", 1))
        self.tbMoveXMinus.clicked.connect(lambda: self.onMove("X", -1))
        self.tbMoveZPlus.clicked.connect(lambda: self.onMove("Z", 1))
        self.tbMoveZMinus.clicked.connect(lambda: self.onMove("Z", -1))

    def onSnippet(self, snippet):
        self.app.onUartMessage.emit(snippet)
        self.app.wifiUart.send(snippet)
        pass

    def onMove(self, axis, direct):
        self.onSnippet("G91|G1{0}{1}F1000|G90".format(axis, str(direct*self.step)))
        pass

    def onStep(self, event):
        if self.step==1:
            self.step=10
        elif self.step==10:
            self.step=50
        elif self.step==50:
            self.step=1
        self.tbStep.setText(str(self.step))

    def onUartConnect(self, state):
        for c in self.uartControls:
            c.setDisabled(not state)
        pass

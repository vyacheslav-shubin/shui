
#from UM.Application import Application
#from UM.Logger import Logger

import sys

language="ru" #ua, en

printers = [
  {'name':'Main', 'ip':'127.0.0.1:8081', "esp32":True},
  {'name':'Dev', 'ip':'192.168.2.192', "esp32":True}
]

default_start_priting=True
default_close_on_complete=True

class Language:
  def __init__(self, lang):
    self.lang_en()
    if language=='ua':
      self.lang_ru()
      self.lang_ua()
    elif language=='ru':
      self.lang_ru()
    else:
      pass

  def lang_en(self):
    self.title='SHUI Cura plugin'
    self.start_printing = "Start printing"
    self.close_on_complete = "Close on complete"
    self.name83 = "8.3 name"
    self.ok = "Ok"
    self.cancel = "Cancel"
    self.printer = "Printer"
    self.success = "Success"
    self.error = "Error"

  def lang_ru(self):
    self.title='SHUI Cura плагин'
    self.start_printing = "Запустить печать"
    self.close_on_complete = "Закрыть по окончании"
    self.name83 = "8.3 имя"
    self.cancel = "Отмена"
    self.printer = "Принтер"
    self.success = "Успешно"
    self.error = "Ошибка"
    pass

  def lang_ua(self):
    pass

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QDialog, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar, QCheckBox, QLineEdit, QComboBox)
from PyQt5.QtGui import (QPixmap, QImage)
from PyQt5.QtNetwork import (QHttpMultiPart, QHttpPart, QNetworkRequest, QNetworkAccessManager, QNetworkReply, QNetworkProxy)
from UM.Application import Application

class NetOutputDialog(QDialog):
  def __init__(self):
    super().__init__()

    self.lang=Language(language)
    self.setWindowTitle('Send to SHUI WiFi')
    self.setFixedWidth(500)
    self.setFixedHeight(222)
    self.reply=None
    self.request=None
    self.postData=None
    self.networkManager=None

    self.setWindowTitle(self.lang.title)
    self.setFixedWidth(500)
    self.setFixedHeight(222)

    mainLayout=QHBoxLayout()
    from cura.Snapshot import Snapshot
    image = Snapshot.snapshot(width = 200, height = 200)
    #image = image.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
    self.bigPic = QLabel()
    self.bigPic.setFixedWidth(200)
    self.bigPic.setFixedHeight(200)
    pix = QPixmap.fromImage(image)
    self.bigPic.setPixmap(pix)

    mainLayout.addWidget(self.bigPic,  alignment=QtCore.Qt.AlignTop)

    rightArea = QVBoxLayout()
    mainLayout.addLayout(rightArea)

    actions_layout = QVBoxLayout()
    cb = QCheckBox(self.lang.start_printing)
    cb.setChecked(default_start_priting)
    self.cbStartPrinting=cb
    actions_layout.addWidget(cb)

    cb = QCheckBox(self.lang.close_on_complete)
    cb.setChecked(default_close_on_complete)
    self.cbCloseOnComplete=cb
    actions_layout.addWidget(cb)

    file_name_layout = QHBoxLayout()
    file_name_layout.addWidget(QLabel(self.lang.name83), alignment=QtCore.Qt.AlignLeft)
    ed83name = QLineEdit()
    ed83name.setText(self.getFileName())
    ed83name.setMaxLength(8)
    file_name_layout.addWidget(ed83name, alignment=QtCore.Qt.AlignLeft)
    self.ed83name=ed83name
    file_name_layout.addWidget(QLabel(".GCO"), alignment=QtCore.Qt.AlignLeft)

    printer_ip_layout=QHBoxLayout()
    printer_ip_layout.addWidget(QLabel(self.lang.printer), alignment=QtCore.Qt.AlignLeft)
    cbPrinterIp=QComboBox()
    pn=[]
    for p in printers:
      pn.append(p["name"])
    cbPrinterIp.addItems(pn)
    cbPrinterIp.currentIndexChanged.connect(self.printerChanged)
    printer_ip_layout.addWidget(cbPrinterIp)
    cb=QCheckBox("ESP32")
    cb.setChecked(printers[0]["esp32"])
    printer_ip_layout.addWidget(cb)
    self.cbEsp32=cb
    self.cbSelectedPrinter=cbPrinterIp

    progress_layout = QVBoxLayout()

    progress=QProgressBar()
    progress_layout.addWidget(progress)
    progress.setMaximum(100)
    progress.setValue(0)
    self.progress = progress

    progress_label=QLabel()
    progress_layout.addWidget(progress_label)
    self.progress_label=progress_label
    progress_label.setText("---")

    buttons_layout = QHBoxLayout()
    okButton = QPushButton(self.lang.ok)
    self.okButton=okButton
    cancelButton = QPushButton(self.lang.cancel)
    buttons_layout.addWidget(cancelButton)
    buttons_layout.addWidget(okButton)

    rightArea_top=QVBoxLayout()
    rightArea_bottom=QVBoxLayout()
    rightArea_bottom.setAlignment(QtCore.Qt.AlignBottom)
    rightArea_top.setAlignment(QtCore.Qt.AlignTop)
    rightArea.addLayout(rightArea_top)
    rightArea.addLayout(rightArea_bottom)

    actions_layout.setAlignment(QtCore.Qt.AlignTop)
    buttons_layout.setAlignment(QtCore.Qt.AlignBottom)
    progress_layout.setAlignment(QtCore.Qt.AlignBottom)
    file_name_layout.setAlignment(QtCore.Qt.AlignLeft)
    printer_ip_layout.setAlignment(QtCore.Qt.AlignLeft)

    rightArea_top.addLayout(actions_layout)
    rightArea_top.addLayout(file_name_layout)
    rightArea_top.addLayout(printer_ip_layout)
    rightArea_bottom.addLayout(progress_layout)
    rightArea_bottom.addLayout(buttons_layout)

    okButton.clicked.connect(self.onOk)
    cancelButton.clicked.connect(self.onCancel)

    self.setLayout(mainLayout)
    pass

  def printerChanged(self, index):
    self.cbEsp32.setChecked(printers[index]["esp32"])
    pass

  def getFileName(self):
    fn=Application.getInstance().getPrintInformation().jobName.strip()
    i=fn.find("_")
    if i!=-1:
      fn=fn[i+1:]
    return fn

  def onOk(self):
    self.disableUI(True)
    scene = Application.getInstance().getController().getScene()
    plate = Application.getInstance().getMultiBuildPlateModel().activeBuildPlate
    gcode_dict = getattr(scene, "gcode_dict", None)
    gcode=(''.join(gcode_dict.get(plate, None))).encode()
    file_name=self.ed83name.text()
    try:
      QNetworkProxy.setApplicationProxy(QNetworkProxy())
      pu = printers[self.cbSelectedPrinter.currentIndex()]["ip"]
      request = QNetworkRequest(QtCore.QUrl("http://%s/upload" % pu))
      request.setRawHeader(b'Connection', b'keep-alive')
      post_data = None
      if self.cbStartPrinting.isChecked():
        request.setRawHeader(b'Start-Printing', b'1')
      if self.cbEsp32.isChecked():
        post_data = gcode
        request.setRawHeader(b'Content-Type', b'application/octet-stream')
        request.setRawHeader(b'File-Name', file_name.encode())
      else:
        post_data = QHttpMultiPart(QHttpMultiPart.FormDataType)
        part = QHttpPart()
        part.setHeader(QNetworkRequest.ContentDispositionHeader,
                       "form-data; name=\"file\"; filename=\"%s\"" % file_name)
        part.setBody(gcode)
        post_data.append(part)
        request.setRawHeader(b'Content-Type', b'multipart/form-data; boundary='+post_data.boundary())
      self.postData=post_data

      if self.networkManager is None:
        self.networkManager = QNetworkAccessManager()
      self.reply = self.networkManager.post(request, post_data)
      self.reply.finished.connect(self.handleResponse)
      self.reply.uploadProgress.connect(self.onUploadProgress)
      self.reply.sslErrors.connect(self.onSslError)
      self.disableUI(True)
    except Exception as e:
      self.progress_label.setText("{0}:{1}".format(self.lang.error, str(e)))
      self.postData=None
      self.reply=None
    pass

  def onCancel(self):
    self.disableUI(False)
    if self.reply is not None:
      if self.reply.isRunning():
        self.reply.abort()
      self.reply=None
    else:
      self.close()
    pass

  def disableUI(self, value):
    self.okButton.setDisabled(value)
    pass

  def handleResponse(self):
    er = self.reply.error()
    if er == QNetworkReply.NoError:
      self.progress_label.setText(self.lang.success)
      if (self.cbCloseOnComplete.isChecked()):
        self.close()
    else:
      self.progress_label.setText("{0} {1}:{2}".format(self.lang.error, er, self.reply.errorString()))

    self.reply=None
    self.postData=None
    self.disableUI(False)
    pass

  def onUploadProgress(self, bytes_sent, bytes_total):
    if bytes_sent==0 and bytes_total==0:
      self.progress.setMaximum(1)
      self.progress.setValue(0)
    else:
      self.progress.setMaximum(bytes_total)
      self.progress.setValue(bytes_sent)
      self.progress_label.setText("{:d}/{:d}".format(bytes_sent, bytes_total))
    pass

  def onSslError(self, reply, sslerror):
    pass

#app = QApplication(sys.argv)
#nod = NetOutputDialog()
#nod.show()
#sys.exit(app.exec_())

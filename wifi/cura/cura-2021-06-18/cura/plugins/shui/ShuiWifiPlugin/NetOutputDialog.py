from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QPushButton, QDesktopWidget, QFileDialog, QLabel, QLineEdit, QProgressBar, QGridLayout, QHBoxLayout, QVBoxLayout, QLayout, QCheckBox
from PyQt5.QtNetwork import QHttpMultiPart, QHttpPart, QNetworkRequest, QNetworkAccessManager, QNetworkReply, QTcpSocket
from UM.Application import Application
from UM.Logger import Logger

import sys


class NetOutputDialog(QDialog):
  def __init__(self):
    super().__init__()
    self.initUI()
    self._manager = QNetworkAccessManager()
    self._manager.finished.connect(self.handleResponse)
    preferences = Application.getInstance().getPreferences()    
    preferences.addPreference("shui/ip", "")
    preferences.addPreference("shui/close_on_success", False)
    preferences.addPreference("shui/esp32", False)

  def initUI(self):
    preferences = Application.getInstance().getPreferences()    
    
    self.setWindowTitle('Send to SHUI WiFi')
    self.resize(400, 40)
    qr = self.frameGeometry()
    qr.moveCenter(QDesktopWidget().availableGeometry().center())
    main_layout=QVBoxLayout()
    self.setLayout(main_layout)

    lAddress = QLabel('Address:')
    
    self._addressEdit = QLineEdit()
    self._addressEdit.setToolTip('Enter printer host name or IP')
    self._addressEdit.setText(preferences.getValue("shui/ip"))
    
    self._bUpload = QPushButton()
    self._bUpload.clicked.connect(self.okClick)

    row_layout=QHBoxLayout()
    main_layout.addLayout(row_layout)
    
    row_layout.addWidget(lAddress) #Qt.AlignRight
    row_layout.addWidget(self._addressEdit)
    row_layout.addWidget(self._bUpload)

    self._edFileName = QLineEdit()
    self._edFileName.setText(self.getFileName())
    self._edFileName.setToolTip('Enter file name 8 symbols only')
    self._edFileName.setMaxLength(8)
    
    row_layout=QHBoxLayout()
    main_layout.addLayout(row_layout)
    
    self._cbPrint = QCheckBox("Print")
    self._cbPrint.setCheckState(Qt.Checked)
    row_layout.addWidget(QLabel('File name (8.3):')) #Qt.AlignRight
    row_layout.addWidget(self._edFileName)
    row_layout.addWidget(QLabel('.gco'))
    row_layout.addWidget(self._cbPrint)


    
    self._progress = QProgressBar()
    self._progress.move(10, 80)
    self._progress.setMaximum(100)
    self._progress.resize(380, 20)
    self._progress.setValue(0)
    
    main_layout.addWidget(self._progress)
    
    row_layout=QHBoxLayout()
    main_layout.addLayout(row_layout)
    self._lStatus =  QLabel(Application.getInstance().getPrintInformation().jobName.strip())
    row_layout.addWidget(self._lStatus)

    row_layout=QHBoxLayout()
    main_layout.addLayout(row_layout)

    self._closeOnSuccess =  QCheckBox("Close on success")
    if preferences.getValue("shui/close_on_success"):
      self._closeOnSuccess.setCheckState(Qt.Checked)
    else:
      self._closeOnSuccess.setCheckState(Qt.Unchecked)

    self._esp32 =  QCheckBox("Esp32")
    if preferences.getValue("shui/esp32"):
      self._esp32.setCheckState(Qt.Checked)
    else:
      self._esp32.setCheckState(Qt.Unchecked)
    row_layout.addWidget(self._esp32)
    row_layout.addWidget(self._closeOnSuccess)

    
    self.uiUploadMode(False)
    self.show()
    pass

  def handleResponse(self, reply):
    er = reply.error()
    if er == QNetworkReply.NoError:
      bytes_string = reply.readAll()
      #Logger.log("w", str(bytes_string, 'utf-8'))
      if self._closeOnSuccess.checkState()==Qt.Checked:
        self.close()
      else:
        self._lStatus.setText("Success")
        self.uiUploadMode(False)
    else:
      #Logger.log("w","Error occured: %d" % er)
      #Logger.log("w", reply.errorString())
      self._lStatus.setText("Error {0}:{1}".format(er, reply.errorString()))
      self.uiUploadMode(False)
    pass
    
  def getFileName(self):
    fn=Application.getInstance().getPrintInformation().jobName.strip()
    i=fn.find("_")
    if i!=-1:
      fn=fn[i+1:]
    return fn

  def uiUploadMode(self, mode):
    if mode:
      self._bUpload.setText("Cancel")
      self._uploading=True
    else:
      self._uploading=False
      self._bUpload.setText("Upload")  
      self._progress.setValue(0)
      self._progress.setMaximum(1)
    pass


  def okClick(self):
    if self._uploading:
      self._reply.abort()
      return
      
    self.uiUploadMode(True)
    preferences = Application.getInstance().getPreferences()    
    preferences.setValue("shui/ip", self._addressEdit.text())
    if self._closeOnSuccess.checkState()==Qt.Checked:
      preferences.setValue("shui/close_on_success", True)
    else:
      preferences.setValue("shui/close_on_success", False)
    if self._esp32.checkState()==Qt.Checked:
      preferences.setValue("shui/esp32", True)
    else:
      preferences.setValue("shui/esp32", False)

    scene = Application.getInstance().getController().getScene()
    plate = Application.getInstance().getMultiBuildPlateModel().activeBuildPlate
    gcode_dict = getattr(scene, "gcode_dict", None)
    gcode=''.join(gcode_dict.get(plate, None))

    request = QNetworkRequest(QUrl("http://%s/upload" % self._addressEdit.text()))
    request.setRawHeader(b'Connection', b'keep-alive')
    if self._cbPrint.checkState()==Qt.Checked:
      request.setRawHeader(b'Start-Printing', b'1')

    if self._esp32.checkState()==Qt.Checked:
      self.post_data = gcode.encode()
      request.setRawHeader(b'Content-Type', b'application/octet-stream')
      request.setRawHeader(b'File-Name', self._edFileName.text().encode())
    else:
      self.post_data = QHttpMultiPart(QHttpMultiPart.FormDataType)
      self.part = QHttpPart()
      self.part.setHeader(QNetworkRequest.ContentDispositionHeader, "form-data; name=\"file\"; filename=\"%s.GCO\"" % self._edFileName.text())
      self.part.setBody(gcode.encode())
      self.post_data.append(self.part)
      request.setRawHeader(b'Content-Type', b'multipart/form-data; boundary='+self.post_data.boundary())


    try:
      self._reply = self._manager.post(request, self.post_data)
      self._reply.uploadProgress.connect(self._onUploadProgress)
      self._reply.sslErrors.connect(self._onSslError)
    except Exception as e:
      self._lStatus.setText("Error:{0}".format(str(e)))
      self.uiUploadMode(False)
    pass
    
  def _onUploadProgress(self, bytes_sent, bytes_total):
    self._progress.setValue(bytes_sent)
    self._progress.setMaximum(bytes_total)
    self._lStatus.setText("Uploading: {0}/{1}".format(bytes_sent, bytes_total))
    pass

  def _onSslError(self, reply, sslerror):
    print("Upload Error")
    
        
#app = QApplication(sys.argv)
#nod = NetOutputDialog()
#sys.exit(app.exec_())

from .FileSaver import NetworkSender
from PyQt5 import (QtCore)
from PyQt5.QtNetwork import (QHttpMultiPart, QHttpPart, QNetworkRequest, QNetworkAccessManager, QNetworkReply, QNetworkProxy)


class WifiSender(NetworkSender):
    reply=None
    request=None
    postData=None

    def save(self, rows, **kwargs):
        self.app.wifiUart.disconnect()
        try:
            rows=self.makeBytes(rows)
            ip = self.app.config["printers"][self.app.selectedPrinter]["ip"]
            esp32 = self.app.config["printers"][self.app.selectedPrinter]["esp32"]
            request = QNetworkRequest(QtCore.QUrl("http://%s/upload" % ip))
            request.setRawHeader(b'Connection', b'keep-alive')
            post_data = None
            if "start" in kwargs:
                if kwargs["start"]:
                    request.setRawHeader(b'Start-Printing', b'1')
            if esp32:
                post_data = rows
                request.setRawHeader(b'Content-Type', b'application/octet-stream')
                request.setRawHeader(b'File-Name', self.fileName.encode())
            else:
                post_data = QHttpMultiPart(QHttpMultiPart.FormDataType)
                part = QHttpPart()
                part.setHeader(QNetworkRequest.ContentDispositionHeader,
                               "form-data; name=\"file\"; filename=\"%s\"" % self.fileName)
                part.setBody(rows)
                post_data.append(part)
                request.setRawHeader(b'Content-Type', b'multipart/form-data; boundary='+post_data.boundary())
            self.postData=post_data

            proxy=QNetworkProxy()
            proxy.setType(QNetworkProxy.NoProxy)
            self.app.networkManager.setProxy(proxy)
            self.reply = self.app.networkManager.post(request, post_data)
            self.reply.finished.connect(self.handleResponse)
            self.reply.uploadProgress.connect(self.onUploadProgress)
            self.reply.sslErrors.connect(self.onSslError)
        except Exception as e:
            self.app.onMessage.emit(str(e))
            print(str(e))
            self.postData=None
            self.reply=None
            self.app.onUploadFinished.emit(True)
        pass

    def handleResponse(self):
        er = self.reply.error()
        if er == QNetworkReply.NoError:
            self.app.onMessage.emit("Success")
        else:
            self.app.onMessage.emit("{0} {1}:{2}".format("Error", er, self.reply.errorString()))

        self.reply=None
        self.postData=None
        self.app.onUploadFinished.emit(True)
        pass

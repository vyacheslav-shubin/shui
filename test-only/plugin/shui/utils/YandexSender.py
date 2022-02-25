from enum import Enum
import json
from .FileSaver import NetworkSender
from PyQt5 import (QtCore)
from PyQt5.QtNetwork import (QHttpMultiPart, QHttpPart, QNetworkRequest, QNetworkAccessManager, QNetworkReply, QNetworkProxy)


class YaPhase(Enum):
    NONE=0
    REQUEST_URL = 0
    UPLOAD = 1


class YandexSender(NetworkSender):
    phase=YaPhase.NONE

    def makeRequest(self, phase, url):
        self.app.networkManager.setProxy(self.app.proxy)
        self.phase=phase
        req=QNetworkRequest(QtCore.QUrl(url))
        req.setRawHeader(b'Accept', b'application/json')
        req.setRawHeader(b'Authorization', ('OAuth '+self.app.config["yandex"]["key"]).encode())
        return req

    def joinReply(self, rep):
        rep.finished.connect(self.handleResponse)
        rep.uploadProgress.connect(self.onUploadProgress)
        rep.sslErrors.connect(self.onSslError)
        pass

    def save(self, rows):
        self.rows = rows
        if self.app.config["yandex"]["override"]:
            ovr="overwrite=true&"
        else:
            ovr=""
        self.request = self.makeRequest(YaPhase.REQUEST_URL, "https://cloud-api.yandex.net/v1/disk/resources/upload?"+ovr+"path=app:/a.html")
        self.reply = self.app.networkManager.get(self.request)
        self.joinReply(self.reply)
        pass

    def upload(self, params):
        self.request = self.makeRequest(YaPhase.UPLOAD, params["href"])
        self.request.setRawHeader(b'Content-Type', b'application/octet-stream')
        self.rows=self.makeBytes(self.rows)
        self.reply = self.app.networkManager.put(self.request, self.rows)
        self.joinReply(self.reply)
        pass

    def doneResponse(self):
        self.reply=None
        self.postData=None

    def handleResponse(self):
        er = self.reply.error()
        if er == QNetworkReply.NoError:
            if self.phase==YaPhase.REQUEST_URL:
                self.app.onMessage.emit("Prepared")
                jresp=json.loads(str(self.reply.readAll(), 'utf-8'))
                self.doneResponse()
                self.upload(jresp)
            elif self.phase==YaPhase.UPLOAD:
                self.app.onMessage.emit("Success")
                self.doneResponse()
                self.app.onUploadFinished.emit(True)
        else:
            if self.reply.rawHeader(b'Content-Type')==b'application/json':
                jresp=json.loads(str(self.reply.readAll(), 'utf-8'))
                self.app.onMessage.emit(jresp["message"])
            else:
                self.app.onMessage.emit("{0} {1}:{2}".format("Error", er, self.reply.errorString()))
            self.doneResponse()
            self.app.onUploadFinished.emit(True)
    pass


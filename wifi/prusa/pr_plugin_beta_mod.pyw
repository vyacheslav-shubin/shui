#Настроки:
#Перечень Ip адресов принтеров. Для прямого подрключения к модулю ShuiWiFi порт указывать не надо
#ip адрес принтера можно узнать в виджете состояния WiFi
printers = [
    {'name':'Sapphire PRO', 'ip':'192.168.1.17', "esp32":True},
    {'name':'PLUS', 'ip':'192.168.1.23', "esp32":True}
]
default_override=True
default_sendWiFi=True
default_start_priting=False
language="ru"   # допустимое значение ru, en, ua

file_prefix="shui_"

import os
import sys
from sys import argv
import re
from PIL import Image
import base64
from io import BytesIO
from os import getenv

if len(argv)>1:
    file_in=sys.argv[1]
else:
    file_in  = "/home/shubin/electronic/firmware/mks-robin/my/shui-src/bh.gcode"   #тестовый файл


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
        self.title='SHUI Prusa plugin'
        self.override_file='Override file'
        self.send_to_wifi='Send to SHUI WiFi'
        self.start_printing = "Start printing"
        self.name83 = "8.3 name"
        self.ok = "Ok"
        self.cancel = "Cancel"
        self.printer = "Printer"
        self.success = "Success"
        self.error = "Error"

    def lang_ru(self):
        self.title='SHUI Prusa плагин'
        self.override_file='Перезаписать файл'
        self.send_to_wifi='Отправить на SHUI WiFi'
        self.start_printing = "Запустить печать"
        self.name83 = "8.3 имя"
        self.cancel = "Отмена"
        self.printer = "Принтер"
        self.success = "Успешно"
        self.error = "Ошибка"
        pass

    def lang_ua(self):
        pass

lang=Language(language)

#file_name = os.path.basename(file_in)
file_name = str(getenv('SLIC3R_PP_OUTPUT_NAME'))

class GCodeParser:
    def __init__(self, fileName):
        self.meta={}
        self.thumbs=[]
        self.fileName=fileName

    def check_key(self, data, key, value_key):
        if (data.startswith(key)):
            self.meta[value_key]=data[len(key):].strip()
            return True
        return False

    def parse(self):
        with open(file_in, "r") as g_file:
            self.gcode=g_file.readlines()
            g_file.close()
        current_thumb=None

        index=0
        for d in self.gcode:
            index+=1
            if current_thumb is None:
                if d.startswith("; thumbnail begin"):
                    current_thumb = {"base64": "", "start_row": index - 1}
                    self.thumbs.append(current_thumb)
                    continue
                if self.check_key(d, "; filament used [mm] = ", "filament used"):
                    continue
                if self.check_key(d, "; estimated printing time (normal mode) = ", "printing time"):
                    continue
                if self.check_key(d, "; layer_height = ", "layer_height"):
                    continue
                if self.check_key(d, ";LAYER_COUNT:", "layer_count"):
                    continue
            if (d.startswith("; thumbnail end")) and (current_thumb is not None):
                current_thumb["end_row"] = index - 1
                current_thumb=None
                continue
            if current_thumb is not None:
                str=d.strip()[2:]
                current_thumb["base64"]+=str

        self.large_preview=None
        self.small_preview=None

        for t in self.thumbs:
            stream=BytesIO(base64.b64decode(t["base64"]))
            image=Image.open(stream).convert("RGB")
            stream.close()
            if image.height == image.width:
                if image.height == 200:
                    self.large_preview=image
                if (image.height == 100) or (image.height == 50):
                    self.small_preview=image

    def dummy_filter(self, idx):
        return True

    def thumb_filter(self, idx):
        for t in self.thumbs:
            if (t["start_row"]<=idx) and (t["end_row"]>=idx):
                return False
        return True

    def generate_preview(self, preview):
        size=preview.width
        res=""
        index=0
        row = bytearray()
        for d in preview.getdata():
            r=d[0]>>3
            g=d[1]>>2
            b=d[2]>>3
            rgb = (r << 11) | (g << 5) | b
            row.append((rgb >> 8) & 0xFF)
            row.append(rgb & 0xFF)
            index+=1
            if (index==size):
                index=0;
                res += ";" + base64.b64encode(row).decode('utf-8') + "\n"
                row = bytearray()
        return res

    def store(self, output_name):
        with open(output_name, "w") as out_file:
            filter_proc=self.dummy_filter
            if (self.large_preview is not None) and (self.small_preview is not None):
                filter_proc=self.thumb_filter
                out_file.write(";SHUI PREVIEW {}x{}\n".format(self.small_preview.width, self.small_preview.width))
                out_file.write(self.generate_preview(self.small_preview))
                out_file.write(self.generate_preview(self.large_preview))
                out_file.write(";POSTPROCESSING SHUI PRUSA PLUGIN\r\n")
                if self.meta["layer_count"] is not None:
                    layer_count=int(self.meta["layer_count"])
                    out_file.write(";LAYER_COUNT: {:}\r\n".format(layer_count))
                if self.meta["filament used"] is not None:
                    f_used=float(self.meta["filament used"])
                    out_file.write(";Filament used: {:1.5f}\r\n".format(f_used/1000))
                if self.meta["layer_height"] is not None:
                    layer_height=float(self.meta["layer_height"])
                    out_file.write(";Layer height: {:1.2f}\r\n".format(layer_height))
                if self.meta["printing time"] is not None:
                    match = re.match('((\d+)d\s)?((\d+)h\s)?((\d+)m\s)?((\d+)s\s*)?', self.meta["printing time"])
                    time=0
                    if match[8] is not None:
                        time+=int(match[8])
                    if match[6] is not None:
                        time+=int(match[6])*60
                    if match[4] is not None:
                        time+=int(match[4])*60*60
                    if match[2] is not None:
                        time+=int(match[2])*60*60*24
                    out_file.write(";TIME:{}\r\n".format(time))
            index=0
            for d in self.gcode:
                if filter_proc(index):
                    out_file.write(d)
                index+=1

        pass


def qt_application():
    from PyQt5 import QtCore
    from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar, QCheckBox, QLineEdit, QComboBox)
    from PyQt5.QtGui import (QPixmap, QImage)
    from PyQt5.QtNetwork import (QHttpMultiPart, QHttpPart, QNetworkRequest, QNetworkAccessManager, QNetworkReply, QNetworkProxy)

    app=QApplication(sys.argv)

    class MainWidget(QWidget):
        def __init__(self):
            super().__init__()
            self.reply=None
            self.request=None
            self.postData=None
            self.networkManager=None

            self.setWindowTitle(lang.title)
            self.setFixedWidth(500)
            self.setFixedHeight(222)
            self.parser = GCodeParser(file_in)
            self.parser.parse()

            mainLayout=QHBoxLayout()
            self.bigPic = QLabel()
            self.bigPic.setFixedWidth(200)
            self.bigPic.setFixedHeight(200)
            mainLayout.addWidget(self.bigPic,  alignment=QtCore.Qt.AlignTop)

            if self.parser.large_preview is not None:
                im = self.parser.large_preview.convert("RGBA")
                data = im.tobytes("raw","RGBA")
                qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)
                pix = QPixmap.fromImage(qim)
                self.bigPic.setPixmap(pix)

            rightArea = QVBoxLayout()
            mainLayout.addLayout(rightArea)

            actions_layout = QVBoxLayout()
            cb = QCheckBox(lang.override_file)
            cb.setChecked(default_override)
            actions_layout.addWidget(cb)
            self.cbOverrideFile=cb
            cb = QCheckBox(lang.send_to_wifi)
            cb.setChecked(default_sendWiFi)
            actions_layout.addWidget(cb)
            self.cbSendToWifi=cb

            cb = QCheckBox(lang.start_printing)
            cb.setChecked(default_start_priting)
            self.cbStartPrinting=cb
            actions_layout.addWidget(cb)

            file_name_layout = QHBoxLayout()
            file_name_layout.addWidget(QLabel(lang.name83), alignment=QtCore.Qt.AlignLeft)
            ed83name = QLineEdit()
            dirname,filename=(os.path.split(file_name))
            filename=(os.path.splitext(filename)[0])
            ed83name.setText(filename)  
            #ed83name.setText(os.path.splitext(file_name)[0])
            ed83name.setMaxLength(8)
            file_name_layout.addWidget(ed83name, alignment=QtCore.Qt.AlignLeft)
            self.ed83name=ed83name
            file_name_layout.addWidget(QLabel(".GCO"), alignment=QtCore.Qt.AlignLeft)

            printer_ip_layout=QHBoxLayout()
            printer_ip_layout.addWidget(QLabel(lang.printer), alignment=QtCore.Qt.AlignLeft)
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
            okButton = QPushButton(lang.ok)
            self.okButton=okButton
            cancelButton = QPushButton(lang.cancel)
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

        def disableUI(self, disabled):
            self.okButton.setDisabled(disabled)
            pass

        def printerChanged(self, index):
            self.cbEsp32.setChecked(printers[index]["esp32"])
            self.cbSendToWifi.setChecked(True)
            pass

        def onOk(self):
            file_out=None
            if self.cbOverrideFile.isChecked():
                file_out=file_in
            else:
                file_out=os.path.join(os.path.dirname(file_in),file_prefix+os.path.basename(file_in))
            self.parser.store(file_out)
            if self.cbSendToWifi.isChecked():
                self.sendToWifi(file_out)
            else:
                self.close()

        def onCancel(self):
            self.disableUI(False)
            if self.reply is not None:
                if self.reply.isRunning():
                    self.reply.abort()
                self.reply=None
            else:
                self.close()
            pass

        def handleResponse(self):
            er = self.reply.error()
            print("HandleResponse: %d" % er)
            if er == QNetworkReply.NoError:
                self.progress_label.setText(lang.success)
                bytes_string = self.reply.readAll()
                self.close()
            else:
                self.progress_label.setText("{0} {1}:{2}".format(lang.error, er, self.reply.errorString()))

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

        def sendToWifi(self, uploaded_file_name):
            gcode=None
            network_file_name=self.ed83name.text()
            if len(network_file_name) == 0:
                network_file_name="SHUIWIFI"

            with open(uploaded_file_name, "rb") as g_file:
                gcode=g_file.read()
            g_file.close()
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
                    request.setRawHeader(b'File-Name', network_file_name.encode())
                else:
                    post_data = QHttpMultiPart(QHttpMultiPart.FormDataType)
                    part = QHttpPart()
                    part.setHeader(QNetworkRequest.ContentDispositionHeader,
                                   "form-data; name=\"file\"; filename=\"%s.GCO\"" % network_file_name)
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
                print("{0}:{1}".format(lang.error, str(e)))
                self.progress_label.setText("{0}:{1}".format(lang.error, str(e)))
                self.postData=None
                self.reply=None
            pass

        def show(self):
            super().show();
            screen = app.primaryScreen()
            #self.move(screen.size().width()/2-self.width()/2, screen.size().height()/2-self.height()/2)
            self.move(int(screen.size().width()/2-self.width()/2), int(screen.size().height()/2-self.height()/2))

    widget=MainWidget()
    widget.show()
    sys.exit(app.exec())


qt_application()
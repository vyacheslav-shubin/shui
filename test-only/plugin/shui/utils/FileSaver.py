from PyQt5 import (QtCore)


class GCodeSaver(QtCore.QObject):
    def __init__(self, app):
        super().__init__()
        self.app=app

    def makeBytes(self, rows):
        d=[]
        for r in rows:
            d+=r.encode()
        return bytearray(d)

class NetworkSender(GCodeSaver):

    def __init__(self, app, file_name):
        super().__init__(app)
        if len(file_name) == 0:
            self.fileName="SHUIWIFI"
        else:
            self.fileName=file_name

    def onUploadProgress(self, bytes_sent, bytes_total):
        if bytes_sent==0 and bytes_total==0:
            self.app.onProgress.emit(0, 1)
        else:
            self.app.onProgress.emit(bytes_sent, bytes_total)
            self.app.onMessage.emit("{:d}/{:d}".format(bytes_sent, bytes_total))
        pass

    def onSslError(self, reply, sslerror):
        pass

class FileSaver(GCodeSaver):

    def save(self, rows):
        from PyQt5 import QtWidgets
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save to file", None, "All Files (*);;GCODE Files (*.gco)", options=options)
        if fileName:
            try:
                i=0
                c=len(rows)/100
                with open(fileName, "w") as out_file:
                    for r in rows:
                        if i%100==0:
                            self.app.onProgress.emit(i/100, c)
                        i=i+1
                        out_file.write(r)
                    self.app.onProgress.emit(1, 1)
                    out_file.close()
            finally:
                self.app.onUploadFinished.emit(True)
            pass

        pass

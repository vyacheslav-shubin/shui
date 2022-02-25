import re
from PIL import Image
import base64
from io import BytesIO
from PyQt5.QtGui import (QPixmap, QImage)
from .Core import GCodeSource

class PrusaGCodeParser(GCodeSource):
    large_preview=None
    small_preview=None

    def __init__(self, fileName):
        super().__init__()
        self.thumbs=[]
        self.fileName=fileName

    def getLargePreview(self):
        if self.large_preview is not None:
            im = self.large_preview.convert("RGBA")
            data = im.tobytes("raw","RGBA")
            qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)
            return QPixmap.fromImage(qim)
        return None

    def parse(self):
        with open(self.fileName, "r") as g_file:
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

    def generate_preview(self, preview, rows):
        size=preview.width
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
                rows.append(";" + base64.b64encode(row).decode('utf-8') + "\n")
                row = bytearray()

    def getProcessedGcode(self):
        rows=[]
        filter_proc=self.dummy_filter
        if (self.large_preview is not None) and (self.small_preview is not None):
            filter_proc=self.thumb_filter
            rows.append(";SHUI PREVIEW {}x{}\n".format(self.small_preview.width, self.small_preview.width))
            self.generate_preview(self.small_preview, rows)
            self.generate_preview(self.large_preview, rows)
        index=0
        for d in self.gcode:
            if filter_proc(index):
                rows.append(d)
            index+=1
        return rows

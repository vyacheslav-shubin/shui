from ..Script import Script
from cura.Snapshot import Snapshot
from PyQt5.QtCore import Qt
import os
import base64

class ShuiPreview(Script):
  def __init__(self):
    super().__init__()
    
  def getSettingDataString(self):
    return """{
              "name": "Generate SHUI Preview",
              "key": "shui_preview",
              "metadata": {},
              "version": 2,
              "settings": {
                  "size": {
                      "label": "Size",
                      "description": "Size of small preview",
                      "type": "enum",
                      "options": {
                        "50": "small",
                        "100": "big",
                        "0": "none"
                      },
                      "default_value": "50"
                  },
                  "format": {
                      "label": "Format",
                      "description": "Format preview code",
                      "type": "enum",
                      "options": {
                        "shui": "SHUI",
                        "mks": "MKS"
                      },
                      "default_value": "shui"
                  }
              }
        }"""

  def addScreenshot(self, img, width, height, img_type):
    result = ""
    b_image = img.scaled(width, height, Qt.KeepAspectRatio)
    img_size = b_image.size()
    result += img_type
    datasize = 0
    for i in range(img_size.height()):
      for j in range(img_size.width()):
        pixel_color = b_image.pixelColor(j, i)
        r = pixel_color.red() >> 3
        g = pixel_color.green() >> 2
        b = pixel_color.blue() >> 3
        rgb = (r << 11) | (g << 5) | b
        strHex = "%x" % rgb
        if len(strHex) == 3:
          strHex = '0' + strHex[0:3]
        elif len(strHex) == 2:
          strHex = '00' + strHex[0:2]
        elif len(strHex) == 1:
          strHex = '000' + strHex[0:1]
        if strHex[2:4] != '':
          result += strHex[2:4]
          datasize += 2
        if strHex[0:2] != '':
          result += strHex[0:2]
          datasize += 2
        if datasize >= 50:
          datasize = 0
      result += '\rM10086 ;'
      if i == img_size.height() - 1:
        result += "\r"
    return result
    
  def generate_mks(self, sz, data):
    image = Snapshot.snapshot(width = 900, height = 900)  
    if sz == "50":
      pv = self.addScreenshot(image, 50, 50, ";simage:")
    else:
      pv = self.addScreenshot(image, 100, 100, ";simage:")
    pv = pv + self.addScreenshot(image, 200, 200, ";;gimage:")
    data.insert(0,  pv)
    return data
    
  def generate_shui(self, sz, data):
    image = Snapshot.snapshot(width = 900, height = 900)
    pv=""
    if sz == "50":
      pv=pv+";SHUI PREVIEW 50x50\n" + self.generate(image, 50)
    else:
      pv=pv+";SHUI PREVIEW 100x100\n" + self.generate(image, 100)
    pv=pv+self.generate(image, 200)
    data.insert(0,  pv)
    return data
        
  def execute(self, data):
    sz=self.getSettingValueByKey("size")
    if sz=="0":
      return data    
    fmt=self.getSettingValueByKey("format")
    if fmt=="shui":
      return self.generate_shui(sz, data)
    if fmt=="mks":
      return self.generate_mks(sz, data)
    return data
    
  def generate(self, img, size):
    result = ""
    b_image = img.scaled(size, size, Qt.KeepAspectRatio)
    img_size = b_image.size()
    datasize = 0
    for i in range(img_size.height()):
      row = bytearray()
      for j in range(img_size.width()):
        pixel_color = b_image.pixelColor(j, i)
        r = pixel_color.red() >> 3
        g = pixel_color.green() >> 2
        b = pixel_color.blue() >> 3
        rgb = (r << 11) | (g << 5) | b
        row.append((rgb >> 8) & 0xFF)
        row.append(rgb & 0xFF)
      result += ";" + base64.b64encode(row).decode('utf-8') + "\n"
    return result

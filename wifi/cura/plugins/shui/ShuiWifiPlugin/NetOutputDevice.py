from UM.Application import Application
from UM.OutputDevice.OutputDevice import OutputDevice
from UM.Logger import Logger
from UM.Preferences import Preferences
from UM.OutputDevice import OutputDeviceError
from UM.FileHandler.WriteFileJob import WriteFileJob

from UM.Message import Message

from . import NetOutputDialog

import sys
import os

from UM.i18n import i18nCatalog
catalog = i18nCatalog("uranium")

class NetOutputDevice(OutputDevice):
    def __init__(self):
        id_str="save_to_network_device"
        descr_str="Send to SHUI WiFi"
        super().__init__(id_str)
        self.setName(id_str)
        self.setPriority(2)
        self._preferences = Application.getInstance().getPreferences()
        self.setShortDescription(catalog.i18nc("@action:button", descr_str))
        self.setDescription(catalog.i18nc("@properties:tooltip", descr_str))
        self.setIconName("save")
        Logger.log("w", "Output device started")
        
    def requestWrite(self, nodes, file_name=None, limit_mimetypes=None, file_handler=None, **kwargs):
        try:
          self.writeStarted.emit(self)
          self.w=NetOutputDialog.NetOutputDialog()
          self.w.show()
        except Exception as e:
          Logger.log("w", "show widget error")
          Logger.log("w", str(e))
        pass


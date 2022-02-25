from UM.Application import Application
from UM.Logger import Logger
from UM.OutputDevice.OutputDevice import OutputDevice
from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin
from UM.i18n import i18nCatalog

from .shui.MainUI import (cura_application)

class NetOutputDevice(OutputDevice):
    def __init__(self):
        catalog = i18nCatalog("uranium")
        id_str="save_to_network_device"
        descr_str="SHUI Uploader"
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
            fn=Application.getInstance().getPrintInformation().jobName.strip()
            i=fn.find("_")
            if i!=-1:
              fn=fn[i+1:]
            self.w=cura_application(output_file_name=fn+".GCO")
            pass
        except Exception as e:
            Logger.log("w", "show widget error")
            Logger.log("w", str(e))
            pass

class ShuiPlugin(OutputDevicePlugin):
    def __init__(self):
        super().__init__()
        self.getOutputDeviceManager().addOutputDevice(NetOutputDevice())

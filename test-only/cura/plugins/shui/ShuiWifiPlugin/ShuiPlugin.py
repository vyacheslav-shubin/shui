from UM.OutputDevice.OutputDevicePlugin import OutputDevicePlugin
from . import NetOutputDevice

class ShuiPlugin(OutputDevicePlugin):
  def __init__(self):
    super().__init__()
    self.getOutputDeviceManager().addOutputDevice(NetOutputDevice.NetOutputDevice())

from .Core import GCodeSource

class CuraGCodeParser(GCodeSource):
    large_preview = None

    def __init__(self):
        super().__init__()

    def parse(self):
        from PyQt5.QtGui import QPixmap
        from cura.Snapshot import Snapshot
        self.large_preview = QPixmap.fromImage(Snapshot.snapshot(width = 200, height = 200))
        pass

    def getLargePreview(self):
        return self.large_preview

    def getProcessedGcode(self):
        from UM.Application import Application
        app_instance=Application.getInstance()
        gcode_dict = getattr(app_instance.getController().getScene(), "gcode_dict", None)
        return gcode_dict.get(app_instance.getMultiBuildPlateModel().activeBuildPlate, None)

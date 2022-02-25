from enum import Enum

class StartMode(Enum):
    UNKNOWN = 0
    CURA = 1
    PRUSA = 2
    STANDALONE = 3


class GCodeSource:
    def __init__(self):
        pass

    def getProcessedGcode(self) -> None: ...

    def parse(self) -> None: ...

    def getLargePreview(self) -> None: ...


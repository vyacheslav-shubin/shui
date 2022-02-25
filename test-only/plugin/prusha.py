import os
from shui.MainUI import qt_application
from shui.utils import StartMode
appStartMode=StartMode.UNKNOWN

if os.getenv('START_MODE')=='TEST':
    appStartMode=StartMode.STANDALONE
else:
    appStartMode=StartMode.PRUSA

qt_application(appStartMode)
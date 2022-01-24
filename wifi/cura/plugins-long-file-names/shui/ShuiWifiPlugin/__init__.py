from . import ShuiPlugin
from UM.i18n import i18nCatalog
from PyQt5.QtQml import qmlRegisterType
catalog = i18nCatalog("cura")

def getMetaData():
	return {}

def register(app):
	return {
		"output_device": ShuiPlugin.ShuiPlugin()
	}

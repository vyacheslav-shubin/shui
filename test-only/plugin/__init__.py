from . import ShuiPlugin


def getMetaData():
	return {}


def register(app):
	return {
		"output_device": ShuiPlugin.ShuiPlugin()
	}

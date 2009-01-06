import os

from picasa import PicasaInfo
from metamonkey import MetaMonkeyInfo
from iptc import IPTCInfo

class Info(object):
	def __init__(self, filename):
		self.filename = filename
		self.picasa = PicasaInfo(filename)
		self.metamonkey = MetaMonkeyInfo(filename)
		self.iptc = IPTCInfo(filename)
		
		self.infos = [selff.filename, self.picasa, self.metamonkey, self.iptc]

class MetaMonkeyAttrs(object):
	def __init__(self, filename):
		self.filename = filename
		self.info = self._load_info()
	
	def items(self):
		return self.info
	
	def _load_info(self):
		#TODO: load file's xattrs
		return {}

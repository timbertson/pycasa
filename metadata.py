import os

class Info(object):
	def __init__(self, filename):
		self.filename = filename
		self.picasa = PicasaInfo(filename)
	
class PicasaIni(object):
	# read in a picasa file from dir, and 
	# populates meta-info for each file
	# contained

	# Currently supported attributes:
	# star (yes/[missing])
	# caption (string)
	# keywords (comma-separated)
	
	# example file:
	#   [DSCN1684.MOV]
	#   star=yes
	#   caption=le cappy!
	#   keywords=a,b,c

	def __init__(self, dirname):
		self.dirname = dirname
		self.fileinfo = self._load_ini()
	
	def __getitem__(self, item):
		return fileinfo.get(item, {})
	
	def _load_ini(self):
		#TODO: load self.dirname/.picasa.ini
		#FIXME: picasa adds metainfo directly to .jpg files, and not to the .ini
		return {}

class PicasaInfo(object):
	ini_files = {}
	def __init__(self, filename):
		self.filename = filename
		self.base = os.path.abspath(os.path.dirname(filename))
		if self.base not in self.ini_files:
			self.ini_files[self.base] = PicasaIni(self.base)
		self.ini = ini_files[self.base]
		self.info = self.ini[self.filename]

class MetaMonkeyAttrs(object):
	def __init__(self, filename):
		self.filename = filename
		self.info = self._load_info()
	
	def items(self):
		return self.info
	
	def _load_info(self):
		#TODO: load file's xattrs
		return {}

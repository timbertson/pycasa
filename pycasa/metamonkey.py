class MetaMonkeyInfo(object):
	def __init__(self, filename):
		self.filename = filename
		self.info = self._load_info()
	
	def items(self):
		return self.info
	
	def _load_info(self):
		#TODO: load file's xattrs
		return {}

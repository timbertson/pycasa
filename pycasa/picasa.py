import re

# attribute constants
TAGS = 'keywords'
CAPTION = 'caption'

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
		item = os.path.getbasename(info)
		return fileinfo.get(item, {})
	
	def _load_ini(self):
		#TODO: load self.dirname/.picasa.ini
		#FIXME: picasa adds metainfo directly to .jpg files, and not to the .ini
		return {}

class PicasaInfo(object):
	ini_files = {}

	iptc_regex = re.compile('\.jpe?g$',re.I)
	iptc_attrs = [TAGS, CAPTION]
	
	def which_info(self, attr):
		if self.iptc_regex.search(self.filename) is not None:
			# it's an iptc-compatible file
			if attr in self.iptc_attrs:
				# and it's an attribute that picasa stores in IPTC:
				return self.iptc_info
		return self.ini_info
		
	def __init__(self, filename):
		self.filename = filename
		self.base = os.path.abspath(os.path.dirname(filename))
		if self.base not in self.ini_files:
			self.ini_files[self.base] = PicasaIni(self.base)
		self.ini = ini_files[self.base]

		self.ini_info = self.ini[self.filename]
		self.file_info = FileInfo(self.filename)
	
	def items(self):
		return self.ini_info.copy().update(self.iptc_info)
		
		
import iptcinfo
class FileInfo(object):
	def __init__(self, filename):
		iptc = iptcinfo.IPTCInfo(filename)
		info_hash = {}
		info_hash[CAPTION] = iptc.get_data()['caption/abstract']
		info_hash[TAGS] = iptc.keywords
		
	def items(self):
		return self.info_hash


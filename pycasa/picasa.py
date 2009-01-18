import os
import re

def dbg(s):
	print(s)

# attribute constants
TAGS = 'keywords'
CAPTION = 'caption'
STAR = 'star'
PICASA_FILENAME = '.picasa.ini'

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
		self.ini_info = self._load_ini()
		self._convert_special_flags()
	
	def __getitem__(self, item):
		item_dirname = os.path.dirname(item)
		if not item_dirname == self.dirname:
			raise ValueError("ini file for %s directory does not have information for files in %s" % (self.dirname, item_dirname))
		item = os.path.basename(item)
		dbg("ini getitem %s, all items = %s" % (item, self.ini_info))
		print self.ini_info.get(item, {})
		return self.ini_info.get(item, {})
	
	newfile = re.compile('^\s*\[(.*)\]\s*$')
	
	def _load_ini(self):
		inifilename = os.path.join(self.dirname, PICASA_FILENAME)
		try:
			f = open(inifilename)
		except IOError:
			dbg("no ini file")
			return {}
		
		info = {}
		current_file = None
		for line in f.readlines():
			if len(line.strip()) == 0:
				continue # blank line
			match = self.newfile.match(line)
			if match:
				current_file = match.group(1)
				if current_file not in info:
					info[current_file] = {}
			else:
				if '=' in line:
					attr, val = [s.strip() for s in line.split('=', 1)]
					if current_file is None:
						dbg("no current file to apply attr: %s" % (line,))
					else:
						print "setting attr %s = %s" % (attr,val)
						info[current_file][attr] = val
				else:
					dbg("doesn't look like an attr to me: %s" % (line, ))
		f.close()
		return info
	
	def _convert_special_flags(self):
		"""
		modifies special flags into their appropriate form. i.e: {'star':'yes'} becomes {'star':True}
		"""
		for file_, attrs in self.ini_info.items():
			if STAR in attrs:
				print "converting"
				attrs[STAR] = (attrs[STAR].lower() == 'yes')
			if TAGS in attrs:
				attrs[TAGS] = [k.strip() for k in attrs[TAGS].split(',')]

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
		self.ini = self.ini_files[self.base]

		self.ini_info = self.ini[self.filename]
		self.file_info = FileInfo(self.filename)
	
	def items(self):
		return self.combined_items.items()
	
	def get_combined_hash(self):
		combined = self.ini_info.copy()
		combined.update(self.file_info.dict())
		return combined
	combined_hash = property(get_combined_hash)
	
	def __getitem__(self, item):
		"""return value for item (or None)"""
		return self.which_info(item).get(item, None)
	
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.combined_hash == other.combined_hash
		else:
			return self.combined_hash == other
	
	def __repr__(self):
		return "<%s for %s: %s>" % (self.__class__.__name__, self.filename, self.combined_hash)
		
import iptcinfo
class FileInfo(object):
	def __init__(self, filename):
		self.info_hash = {}
		try:
			iptc = iptcinfo.IPTCInfo(filename)
		except IOError:
			return

		self.info_hash[CAPTION] = iptc.getData()['caption/abstract']
		self.info_hash[TAGS] = iptc.keywords
		
	def items(self):
		return self.info_hash
	
	def __iter__(self):
		return self.info_hash.__iter__()
	
	def dict(self):
		return self.info_hash


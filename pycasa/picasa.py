import os
import re

def dbg(s):
	print(s)
	
from keys import *

RATING_THRESHOLD = 50
STAR_FLAG = 'yes'
PICASA_FILENAME = '.picasa.ini'

def proxy(attr):
	def decorate(func):
		name = func.__name__
		def fn(self, *args):
			# call the original method before the proxy happens
			func(self, *args)
			delegate = getattr(self, attr)
			return getattr(delegate, name)(*args)
		fn.__name__ = name
		return fn
	return decorate

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
		self.dirname = os.path.abspath(dirname)
		self.ini_filename = os.path.join(self.dirname, PICASA_FILENAME)
		self.ini_info = self._load_ini()
		self._decode_special_flags()
	
	def __getitem__(self, item):
		item_dirname = os.path.dirname(os.path.abspath(item))
		if not item_dirname == self.dirname:
			raise ValueError("ini file for %s directory does not have information for files in %s" % (self.dirname, item_dirname))
		item = os.path.basename(item)
		dbg("ini getitem %s, all items = %s" % (item, self.ini_info))
		print self.ini_info.get(item, {})
		return self.ini_info.get(item, {})
	
	@proxy('ini_info')
	def __delitem__(self, item): pass
	
	newfile = re.compile('^\s*\[(.*)\]\s*$')
	
	def _load_ini(self):
		try:
			f = open(self.ini_filename)
		except IOError:
			dbg("no ini file: %s" % (self.ini_filename))
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
	
	def save(self):
		print "wiriting ini: %s" % (self.ini_info,)
		self._encode_special_flags()
		output = []
		for file_, attrs in self.ini_info.items():
			output.append("[%s]" % (file_,))
			for key, val in attrs.items():
				output.append("%s=%s" % (key, val))
		print '=' * 80 + '\n' + '\n'.join(output) + '\n' + '=' * 80

		f = open(self.ini_filename, 'w')
		f.write('\n'.join(output))
		f.close()
		
		print "DBG: saved file contents are:"
		f = open(self.ini_filename)
		print '\n'.join(f.readlines())
		print "DBG: saved file contents"

		
		self._decode_special_flags()
	
	def _encode_special_flags(self):
		"""
		returns a copy dict with special flags in their on-disk form. i.e: {'star':True} becomes {'star':'yes'}
		"""
		for file_, attrs in self.ini_info.items():
			if STAR in attrs:
				if attrs[STAR]:
					attrs[STAR] = STAR_FLAG
				else:
					del attrs[STAR]
					
			if TAGS in attrs:
				attrs[TAGS] = ','.join(attrs[TAGS])
		
	def _decode_special_flags(self):
		"""
		modifies special flags into their appropriate form. i.e: {'star':'yes'} becomes {'star':True}
		"""
		for file_, attrs in self.ini_info.items():
			if STAR in attrs:
				attrs[STAR] = (attrs[STAR].lower() == STAR_FLAG)
			if TAGS in attrs:
				attrs[TAGS] = [k.strip() for k in attrs[TAGS].split(',')]

class PicasaInfo(object):
	@classmethod
	def _reset(cls):
		"""for use in tests only"""
		cls.ini_files = {}
	ini_files = {}

	iptc_regex = re.compile('\.jpe?g$',re.I)
	iptc_attrs = [TAGS, CAPTION]
	
	def which_info(self, attr):
		if self.file_info and self.iptc_regex.search(self.filename) is not None:
			# it's an iptc-compatible file
			if attr in self.iptc_attrs:
				# and it's an attribute that picasa stores in IPTC:
				return self.file_info
		return self.ini_info
		
	def __init__(self, filename):
		self.filename = filename
		self.base = os.path.abspath(os.path.dirname(filename))
		if self.base not in self.ini_files:
			self.ini_files[self.base] = PicasaIni(self.base)
		self.ini = self.ini_files[self.base]

		self.ini_info = self.ini[self.filename]

		self.file_info = None
		if self.iptc_regex.search(self.filename) is not None and os.path.isfile(self.filename):
			self.file_info = FileInfo(self.filename)
	
	def items(self):
		return self.combined_items.items()
	
	def get_combined_hash(self):
		combined = self.ini_info.copy()
		if self.file_info:
			combined.update(self.file_info.dict())
		return combined
	combined_hash = property(get_combined_hash)
	
	def replace_with(self, new_dict):
		self._clear()
		for (k,v) in new_dict.items():
			self[k] = v
	
	def save(self):
		self.ini.save()
		if self.file_info:
			self.file_info.save()
	
	def __getitem__(self, item):
		"""return value for item (or None)"""
		return self.which_info(item).get(item, None)
	
	def __setitem__(self, item, val):
		self.which_info(item)[item] = val
		if item == RATING:
			self.which_info(STAR)[STAR] = int(val) >= RATING_THRESHOLD
	
	def __delitem__(self, item):
		"""delete from *both* info stores"""
		for store in (self.file_info, self.ini_info):
			if store is not None:
				try:
					del store[item]
				except KeyError: pass
			
	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.combined_hash == other.combined_hash
		else:
			return self.combined_hash == other
	
	def _clear(self):
		for k in self.combined_hash:
			del self[k]
	
	def __repr__(self):
		return "<%s for %s: %s>" % (self.__class__.__name__, self.filename, self.combined_hash)
		
import iptcinfo
class FileInfo(object):
	def __init__(self, filename):
		self.info_hash = {}
		self.iptc = iptcinfo.IPTCInfo(filename)

		self.info_hash[CAPTION] = self.iptc.getData()['caption/abstract']
		self.info_hash[TAGS] = self.iptc.keywords
		
	def items(self):
		return self.info_hash
	
	def __iter__(self):
		return self.info_hash.__iter__()
	
	def dict(self):
		return self.info_hash

	def get(self, item, default):
		return self.info_hash.get(item, default)
	
	# def __setitem__(self, item, val):
	# 	self.info_hash[item] = val
	
	@proxy('info_hash')
	def __setitem__(self, item, val): pass

	@proxy('info_hash')
	def __delitem__(self, item): pass

	def save(self):
		self.iptc.save()

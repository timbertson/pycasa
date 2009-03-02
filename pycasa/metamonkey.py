import xattr

attrNamespace = "user.tk.gfxmonk.MetaMonkey."

from keys import *

def getint(val):
	if val is None:
		return None
	try:
		return int(val)
	except Exception:
		try:
			return int(float(val))
		except Exception:
			return None

def getkeys(val):
 	keys = [x.strip() for x in val.split(",")]
	return None if keys == [] else keys

# keys are picasa key names, values are pars of (xattr key name, conversion function)
mapping = {
	CAPTION: ('comment', str),
	RATING: ('rating', getint),
	TAGS: ('keys', getkeys),
	}
	

class MetaMonkeyInfo(object):
	def __init__(self, filename):
		self.filename = filename
		self.info = self._load_info()
	
	def items(self):
		return self.info
	
	def _load_info(self):
		info = {}
		for key,decode_info in mapping.items():
			xattrkey, extract_value = decode_info
			val = self.getxattr(xattrkey)
			if val is not None:
				val = extract_value(val)
			if val is not None:
				info[key] = val
		return info
	
	def __repr__(self):
		return "<%s for %s: %r>" % (self.__class__.__name__, self.filename, self.info)

	# interaction with xattr
	def getxattr(self, attr, useNamespace = True):
		try:
			return str(xattr.getxattr(self.filename, attrNamespace + attr))
		except Exception,e:
			# xattr raises an exception if a field is not present
			return None

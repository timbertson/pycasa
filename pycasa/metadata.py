import os

from output import dbg
from picasa import PicasaInfo
from metamonkey import MetaMonkeyInfo
try:
	from iptc import IPTCInfo
except ImportError:
	from lib.iptcinfo import IPTCInfo

class Info(object):
	def __init__(self, filename):
		self.filename = filename
		self.picasa = PicasaInfo(filename)
		self.metamonkey = MetaMonkeyInfo(filename)
		
		self.infos = {'picasa':self.picasa, 'metamonkey':self.metamonkey}
		self.master = None
		
	def merge(self, master = None):
		if self.master is not None:
			print "Warning: %s master has already been set"% (self.filename,)
		dbg("merging with master key: %r" % (master,))
		if master is not None:
			if master not in self.infos.keys():
				raise ValueError("%s is not an info key (which are %s)" % (master, self.infos.keys()))
			self.master = self.infos[master]
		else:
			self.master = self._merge(self.infos.values())
		
	def save(self):
		self._update()
		self._save()
	
	def _update(self):
		"""tell self.picasa and self.metamonkey about the new details"""
		for info in self.infos.values():
			if not info is self.master:
				info.replace_with(self.master)
		
	def _save(self):
		for info in self.infos.values():
			if not info is self.master:
				info.save()
		
	def _merge(self, dicts):
		"""merge two (or more) dicts, taking the most "useful" value amongst all dicts for each key"""
		raise NotImplementedError
		
	def items(self):
		for name,info in self.infos.items():
			for k,v in info.items():
				yield k,v
	
	def __len__(self):
		return sum(map(len, self.infos.values()))



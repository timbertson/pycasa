import os

from picasa import PicasaInfo
from metamonkey import MetaMonkeyInfo
from iptc import IPTCInfo

class Info(object):
	def __init__(self, filename):
		self.filename = filename
		self.picasa = PicasaInfo(filename)
		self.metamonkey = MetaMonkeyInfo(filename)
		
		self.infos = {'picasa':self.picasa, 'metamonkey':self.metamonkey}
		self.master = None
		
	def merge(self, master = None):
		if master is not None:
			print "Warning: %s master has already been set"% (self.filename,)
		if master is not None:
			if master not in self.infos:
				raise ValueError("%s is not an info key (which are %s)" % (master, self.infos.keys()))
			self.master = self.infos[master]
		else:
			self.master = _merge(infos.values())
		
	def save(self, master = None):
		self.merge(master)
		self._update()
		self._save()
	
	def _update(self):
		"""tell self.picasa and self.metamonkey about the new details"""
		for info in self.infos.keys():
			info.replace_with(self.master)
		
	def _save(self):
		for info in self.infos.keys():
			info.save()
		
	def _merge(self, dicts):
		"""merge two (or more) dicts, taking the most "useful" value amongst all dicts for each key"""
		raise NotImplementedError



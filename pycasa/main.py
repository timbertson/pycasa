#!/usr/bin/env python
from mandy import Command
import metadata
import os

class Main(Command):
	def configure(self):
		self.opt('src', default='.', desc="source directory (default '.')")
		self.arg('action', default='list', action=self.valid_action, desc="Action: <list|sync|dry-sync>")
		self.opt('recurse', bool, default=False, desc="only scan src and subfolders (default: true)")
	
	def valid_action(self, action):
		if action not in ['list', 'sync','dry-sync']:
			raise RuntimeError("Invalid action")
		if not self.hasattr(action) or super(self.__class__,self).hasattr(action):
			raise RuntimeError("action not yet supported: %s" % (action))
		
	def run(self, opts):
		print repr(opts._dict)
		self.opts = opts
		os.path.walk(opts.src, self.walk_cb, getattr(self, opts.action))
	
	def list(self, info):
		print "** %s" % (info.infos,)
	
	def walk_cb(self, action, dirname, fnames):
		for fname in fnames[:]:
			fullpath = os.path.join(dirname, fname)
			if os.path.isfile(fullpath):
				info = metadata.Info(fname)
				action(info)
			elif not self.opts.recurse:
				fnames.remove(fname)
	

if __name__ == '__main__':
	Main()
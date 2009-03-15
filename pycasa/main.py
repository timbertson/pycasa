#!/usr/bin/env python
from mandy import Command
import metadata
import os
import output

class Main(Command):
	def configure(self):
		self.arg('action', default='list', action=self.valid_action, desc="Action: <list|sync|dry-sync>")
		self.arg('src', desc="source directory (default '.')")
		self.opt('verbose', bool, default=False)
		self.opt('recurse', bool, default=False, desc="only scan src and subfolders (default: true)")
		self.opt('master', default='metamonkey', desc="source of truth: <metamonkey|picasa>")
	
	def valid_master(self, master):
		if master not in ['xattr','picasa']:
			raise RuntimeError("Invalid master: %s" % (master,))
		
	def valid_action(self, action):
		if action not in ['list', 'sync', 'dry-sync']:
			raise RuntimeError("Invalid action: %s" % (action,))
		if not hasattr(self, action) or hasattr(super(self.__class__,self), action):
			raise RuntimeError("action not yet supported: %s" % (action))
		
	def run(self, opts):
		self.opts = opts
		self.count = 0
		if self.opts.verbose:
			output.lvl += 1
		os.path.walk(opts.src, self.walk_cb, getattr(self, opts.action))
		print "Files traversed: %s" % (self.count,)
	
	def list(self, file_path, info):
		if len(info) == 0: return
		print
		print file_path
		print '-' * 80
		for k,v in info.items():
			print "%s=%s" % (k,v)
	
	def sync(self, file_path, info):
		info.merge(self.opts.master)
		info.save()
	
	def walk_cb(self, action, dirname, fnames):
		for fname in fnames[:]:
			fullpath = os.path.join(dirname, fname)
			if os.path.isfile(fullpath):
				info = metadata.Info(fullpath)
				self.count += 1
				action(fullpath, info)
			elif not self.opts.recurse:
				fnames.remove(fname)
	
if __name__ == '__main__':
	Main()
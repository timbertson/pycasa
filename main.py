#!/usr/bin/env python
from mandy import Command

class Main(Command):
	def configure(self):
		self.opt('src', default='.', desc="source directory (default '.')")
		self.arg('action', default='print', desc="Action: <print|sync|dry-sync>")
		self.arg('no-recurse', bool, opposite=False, default=False, desc="only scan src, not its subfolders")
		
	def run(self, opts):
		print repr(opts._dict)
		recurse = not opts['no-recurse']
		if not self.hasattr(opts.action) or super(self.__class__,self).hasattr(opts.action):
			raise RuntimeError("invalid action: %s" % (opts.action))
		self.action(opts)
	
	def list(opts):
		#TODO: walk opts.src
		pass

if __name__ == '__main__':
	Main()
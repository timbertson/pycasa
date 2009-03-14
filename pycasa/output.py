
lvl = 0
def dbg(*args):
	if lvl > 0:
		print '\n'.join(['> %s' % line for line in '\n'.join(args).splitlines()])

def puts(*args): print '\n'.join(args)

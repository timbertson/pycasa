import sys, os

p = os.path
rootpath = p.abspath( p.join(p.dirname(__file__), '..') )
if not rootpath in sys.path:
	sys.path.insert(0,rootpath)


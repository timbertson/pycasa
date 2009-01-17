import os
import sys
sys.path.append('..')

print __file__
print os.getcwd()

import eggloader
from mocktest import *

from pycasa import picasa
print globals().keys()

class PicasaTest(TestCase):
	def setUp(self):
		self.files = []
		
	def tearDown(self):
		for f in self.files:
			os.remove(f)
		# remove cached ini files
		picasa.PicasaInfo.ini_files = {}
	
	def write_ini(self, contents):
		filename = '/tmp/.picasa.ini'
		self.files.append(filename)
		f = open(filename, 'w')
		f.write(contents)
		f.close()
		
	def test_should_load_ini_info_for_multiple_files(self):
		self.write_ini("""
			[a]
			key=val
			key2=val2
			[b]
			foo=bar
		
			""")
		info = picasa.PicasaInfo('/tmp/a')
		self.assertEqual(info, {'key':'val', 'key2':'val2'})
		self.assertEqual(picasa.PicasaInfo('/tmp/b'), {'foo':'bar'})
	
	def test_should_turn_starred_key_into_boolean(self):
		self.write_ini("""[a]
			star=yes
			""")
		info = picasa.PicasaInfo('/tmp/a')
		
		self.assertEqual(info['star'], True)
	
	def test_should_treat_multiple_entries_additively(self):
		self.write_ini("""[a]
				a=b
				[b]
				[a]
				foo=bar
				""")
		info = picasa.PicasaInfo('/tmp/a')
		self.assertEqual(info, {'a':'b', 'foo':'bar'})
		
	def test_should_deal_with_multple_equal_signs(self):
		self.write_ini("""
			[a]
			caption=foo=bar
			""")
		info = picasa.PicasaInfo('/tmp/a')
		self.assertEqual(info['caption'], 'foo=bar')

	def test_should_load_jpeg_info(self):
		import iptcinfo
		iptcinfo.
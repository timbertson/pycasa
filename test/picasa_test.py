import os
import shutil

import eggloader
from mocktest import *

import test_helper
import pycasa
from pycasa import picasa
from pycasa.picasa import iptcinfo

FIXTURE_A = 'DSCN1636.JPG'

from pycasa import output
output.lvl = 1

class AbsPicasaTest(TestCase):
	def setUp(self):
		self.files = []
		
	def tearDown(self):
		for f in self.files:
			os.remove(f)
		# remove cached ini files
		picasa.Info._reset()
	
	def write_ini(self, contents):
		filename = '/tmp/.picasa.ini'
		self.files.append(filename)
		f = open(filename, 'w')
		f.write(contents)
		f.close()

class PicasaTest(AbsPicasaTest):
	def test_should_load_ini_info_for_multiple_files(self):
		self.write_ini("""
			[a]
			key=val
			key2=val2
			[b]
			foo=bar
		
			""")
		info = picasa.Info('/tmp/a')
		self.assertEqual(info, {'key':'val', 'key2':'val2'})
		self.assertEqual(picasa.Info('/tmp/b'), {'foo':'bar'})
	
	def test_should_turn_starred_key_into_boolean(self):
		self.write_ini("""[a]
			star=yes
			""")
		info = picasa.Info('/tmp/a')
		self.assertEqual(info['star'], True)
	
	def test_should_treat_multiple_entries_additively(self):
		self.write_ini("""[a]
				a=b
				[b]
				[a]
				foo=bar
				""")
		info = picasa.Info('/tmp/a')
		self.assertEqual(info, {'a':'b', 'foo':'bar'})
		
	def test_should_deal_with_multple_equal_signs(self):
		self.write_ini("""
			[a]
			caption=foo=bar
			""")
		info = picasa.Info('/tmp/a')
		self.assertEqual(info['caption'], 'foo=bar')
	
	def test_should_split_tags_on_commas(self):
		self.write_ini("""
			[a]
			keywords=a,b, cd
			""")
		info = picasa.Info('/tmp/a')
		self.assertEqual(info['keywords'], ['a','b','cd'])
	
	def test_should_use_empty_dict_if_no_ini_file(self):
		info = picasa.Info('/tmp/a')
		self.assertEqual(info, {})
	
class FixtureTest(AbsPicasaTest):
	def setUp(self):
		super(self.__class__, self).setUp()
		self.fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures')
	
	def fixture_info(self, name):
		return picasa.Info(os.path.join(self.fixtures_path, name))
	
	def test_should_load_jpeg_info(self):
		info = self.fixture_info(FIXTURE_A)
		self.assertEqual(info, {'keywords':['a', 'b'], 'caption':'sunset, woo!', 'star':True})

class IPTCTest(TestCase):
	def test_should_not_fail_on_IPTC_exception(self):
		mock_on(iptcinfo).IPTCInfo.raising(Exception('some stuff went badly'))
		self.assertEqual(picasa.FileInfo('some_path').info_hash, {})
	

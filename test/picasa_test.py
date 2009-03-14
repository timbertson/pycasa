import os
import shutil
import sys
sys.path.append('..')

print __file__
print os.getcwd()

import eggloader
from mocktest import *

from pycasa import picasa
from pycasa.picasa import iptcinfo

FIXTURE_A = 'DSCN1636.JPG'

class AbsPicasaTest(TestCase):
	def setUp(self):
		self.files = []
		
	def tearDown(self):
		for f in self.files:
			os.remove(f)
		# remove cached ini files
		picasa.PicasaInfo._reset()
	
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
	
	def test_should_split_tags_on_commas(self):
		self.write_ini("""
			[a]
			keywords=a,b, cd
			""")
		info = picasa.PicasaInfo('/tmp/a')
		self.assertEqual(info['keywords'], ['a','b','cd'])
	
	def test_should_use_empty_dict_if_no_ini_file(self):
		info = picasa.PicasaInfo('/tmp/a')
		self.assertEqual(info, {})
	
	def test_should_save_ini_info(self):
		self.write_ini("""[a]
			a=b
			""")
		info = picasa.PicasaInfo('/tmp/a')
		info['x'] = 'y'
		info['a'] = 'x'
		info.save()
		lines = list([line.strip() for line in open(self.files[0], 'r').readlines() if len(line.strip()) > 0])
		self.assertEqual(lines[0], '[a]')
		self.assertEqual(sorted(lines[1:]), ['a=x', 'x=y'])
		
	def test_should_get_star_from_rating_if_rating_key_exists(self):
		self.write_ini("""
			[a]
			keywords=a,b, cd
			rating=50
			[b]
			rating=49
			""")
		info_a = picasa.PicasaInfo('/tmp/a')
		info_b = picasa.PicasaInfo('/tmp/b')
		
		# star conversion is done only when replacing the entire dict
		info_a.replace_with(info_a.combined_hash)
		info_b.replace_with(info_b.combined_hash)
		
		self.assertEqual(info_a['star'], True)
		self.assertEqual(info_b['star'], False)

class FixtureTest(AbsPicasaTest):
	def setUp(self):
		super(self.__class__, self).setUp()
		self.fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures')
	
	def fixture_info(self, name):
		return picasa.PicasaInfo(os.path.join(self.fixtures_path, name))
	
	def test_should_load_jpeg_info(self):
		info = self.fixture_info(FIXTURE_A)
		self.assertEqual(info, {'keywords':['a', 'b'], 'caption':'sunset, woo!', 'star':True})
	
	def test_should_replace_info_dict_with_a_new_one(self):
		info = self.fixture_info(FIXTURE_A)
		info.replace_with({'star':True, 'keywords':['foo','bar']})
		self.assertEqual(info, {'star': True, 'keywords':['foo','bar']})
		
		# make sure they ended up in the appropriate dict:
		self.assertEqual(info.ini_info, {'star':True})
		self.assertEqual(info.file_info, {'keywords':['foo','bar']})


class DestructiveFixtureTest(AbsPicasaTest):
	def setUp(self):
		super(self.__class__, self).setUp()
		fixtures_mod_path = os.path.join(os.path.dirname(__file__), 'fixtures_mod')
		fixtures_orig_path = os.path.join(os.path.dirname(__file__), 'fixtures')
		try:
			shutil.rmtree(fixtures_mod_path)
		except:
			pass
		shutil.copytree(fixtures_orig_path, fixtures_mod_path)
		self.fixtures_path = fixtures_mod_path
	
	def tearDown(self):
		super(self.__class__, self).tearDown()
		shutil.rmtree(self.fixtures_path)
		
		
	def test_should_save_jpeg_info(self):
		info = picasa.PicasaInfo(os.path.join(self.fixtures_path, FIXTURE_A))
		self.assertEqual(info, {'keywords':['a', 'b'], 'caption':'sunset, woo!', 'star':True})
		info['keywords'] += 'c'
		info['star'] = False

		# check in-memory version
		self.assertEqual(info, {'keywords':['a', 'b', 'c'], 'caption':'sunset, woo!', 'star':False})

		info.save()
		picasa.PicasaInfo._reset()
		
		# on-disk version
		info = picasa.PicasaInfo(os.path.join(self.fixtures_path, FIXTURE_A))
		self.assertEqual(info, {'keywords':['a', 'b', 'c'], 'caption':'sunset, woo!'})

	@pending
	def test_save_should_create_ini_on_save_if_there_is_none(self):
		ini_path = os.path.join(self.fixtures_path, '.picasa.ini')
		os.remove(ini_path)
		self.assertFalse(os.path.isfile(ini_path))
		info = picasa.PicasaInfo(os.path.join(self.fixtures_path, FIXTURE_A))
		self.assertEqual(info.ini_info, {})
		
		info['star'] = True
		info.save()
		self.assertTrue(os.path.isfile(ini_path))
		
		info = picasa.PicasaInfo(os.path.join(self.fixtures_path, FIXTURE_A))
		self.assertEqual(info.ini_info, {'star':True})
		
class IPTCTest(TestCase):
	def test_should_not_fail_on_IPTC_exception(self):
		mock_on(iptcinfo).IPTCInfo.raising(Exception('some stuff went badly'))
		self.assertEqual(picasa.FileInfo('some_path').info_hash, {})
	

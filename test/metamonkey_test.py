import os

import eggloader
from mocktest import *

import test_helper
from pycasa.metamonkey import MetaMonkeyInfo

FIXTURE_A = 'DSCN1636.JPG'

class MetamonkeyTest(TestCase):
	def test_should_load_xattrs(self):
		info = MetaMonkeyInfo(os.path.join(os.path.dirname(__file__), 'fixtures', FIXTURE_A))
		self.assertEqual(info.info, {'keywords':['foo','bar'], 'rating': 3, 'caption':'commentio'})


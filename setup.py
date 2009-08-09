#!/usr/bin/env python

from setuptools import *

setup(
	name='pycasa-metadata',
	version='0.2',
	description='python library for reading picasa metadata',
	packages=find_packages(exclude=["test"]),
	
	classifiers=[
		"Programming Language :: Python",
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
	],
	keywords='',
	license='BSD',
	install_requires=[
		'setuptools',
		# 'IPTCInfo', # I found this at http://www.fw.hu/gthomas/python/IPTCInfo-1.9.2-rc5.tar.bz2
	],
)

# cocoa bridge
from Foundation import *
from AppKit import *
from ScriptingBridge import SBApplication
from objc import ivar

# standard modules
import xattr
import os

from helpers import log

# namespace for custom xattributes.
attrNamespace = "user.tk.gfxmonk.MetaMonkey."

class FileNode(NSObject):
	"""
	A file node
	"""
	path = ivar("path")
	url = ivar("url")
	name = ivar("name")
	comment = ivar("comment")
	rating = ivar("rating")
	keys = ivar("keys")
	keystr = ivar("keystr")
	
	dirty = False
	
	# initialisation, setting data sources...
	def init(self):
		if self.url is not None:
			self.path = self.url.path()
			self.name = os.path.basename(self.path)
			self.getInfo()
		return self
	
	def initWithPath_(self, path):
		self.url = NSURL.fileURLWithPath_(path)
		return self.init()
	
	def initWithURLStr_(self, urlStr):
		self.url = NSURL.URLWithString_(urlStr)
		return self.init()
	
	def getInfo(self):
		"""
		populates this object with its metadata (using xattr)
		"""
		self.comment = self.getxattr("comment")
		self.updateKeystr()
		rating = 0
		ratingStr = self.getxattr("rating")
		try:
			rating = int(ratingStr)
		except Exception:
			try:
				rating = int(float(ratingStr))
			except Exception:
				pass
		
		self.rating = rating

	# interaction with xattr
	def getxattr(self, attr, useNamespace = True):
		if self.path is None:
			return None
		try:
			if useNamespace:
				attr = attrNamespace + attr
			ret = str(xattr.getxattr(self.path, attr))
			log("xattr:",attr,ret)
			return ret
		except Exception,e:
			# xattr raises an exception if a field is not present
			return None
			
	def setxattr(self, attr, val, useNamespace = True):
		if val is None:
			val = ""
		if self.path is None:
			return False
		
		try:
			if useNamespace:
				attr = attrNamespace + attr
			xattr.setxattr(self.path, attr, val)
			return True
		
		except Exception,e:
			log("setxattr failed :")
			log(e)
			return False
	
	
	def updateKeystr(self):
		self.keystr = self.getxattr("keys")
		if self.keystr is None:
			self.keys = []
		else:
			self.keys = [x.strip() for x in self.keystr.split(",")]
		self.keys = [x for x in self.keys if len(x)>0]

	# objc ivar setters
	def setKeys_(self,val):
		log("setting keys..")
		self.keys = [x for x in val if len(x)>0]
		keystr = ",".join([x.strip() for x in val])
		log(keystr)
		#self.setxattr("keys", keystr)
		self.keystr = keystr
		self.dirty = True
	
	def setKeystr_(self, val):
		self.setxattr("keys", val)
		self.updateKeystr()
		self.dirty = True
		
	def setRating_(self,val):
		self.rating = int(val)
		self.ratingStr = str(self.rating)
		self.dirty = True
		#self.setxattr("rating", self.ratingStr)
		
	def setComment_(self,val):
		self.comment = val
		self.dirty = True
		log("comment updated",self)
		#self.setxattr("comment", val)
	
	# save the internal state to the filesystem
	def save(self):
		if self.dirty:
			log("saving...")
			self.setxattr("comment", self.comment)
			self.setxattr("rating", str(self.rating))
			self.setxattr("keys", self.keystr)
			self.updateSpotlightComment()
			self.dirty = False
		
	def updateSpotlightComment(self):
		"""
		Puts the ratings, keywords and comments into the
		spotlight-indexable comment field.
		
		for a file with:
			rating = 3
			keywords = ("key", "word")
			comment = "yet another sunset"
		the spotlight comment field will become:
		"rating=3 kwd=key# kwd=word#\nyet another sunset"
		
		In theory this should be doable via the xattr library,
		however the keys are stored in some kind of binary plist
		format, so we'll just make applescript do it for us.
		"""
		comment = self.comment if not self.comment is None else ""
		rating = int(self.rating) if not self.rating is None else 0
		keystrs = ["kwd=%s#" % x for x in self.keys] if (not self.keys is None) else ""
		ratingStr = ("rating="+str(rating) + " ") if rating != 0 else ""
		spotlightStr = ratingStr + " ".join(keystrs) + "\n" + comment
		
		log("setting spotlight comment to ", spotlightStr)
		cmd = "osascript -e 'tell application \"Finder\" to set comment of ((\""+self.path+"\" as POSIX file) as alias) to \""+spotlightStr+"\"'"
		os.popen(cmd)


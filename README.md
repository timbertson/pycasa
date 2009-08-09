# Pycasa:

Is a simple python library for reading pycasa metadata.
Currently supported attributes:

 - Caption
 - Keywords (tags)
 - Star

### Example usage:

		import pycasa
		
		info = pycasa.Info('/path/to/some/file.jpg')
		print "keywords: %s" % (info.keywords,))
		print "caption: %s" % (info.caption,))
		print "star: %s" % (info.star,))



import os

_postImportVars = vars().keys()


class _CachedFile(object):
	__slots__ = ('checkedAt', 'fingerprint', 'contents')

	def __init__(self, checkedAt, fingerprint, contents):
		self.checkedAt = checkedAt
		self.fingerprint = fingerprint
		self.contents = contents



def defaultFingerprint(filename):
	s = os.stat(filename)
	return s.st_ino, s.st_size, s.st_mtime, s.st_ctime


def defaultGetContents(filename):
	f = None
	try:
		f = open(filename, 'rb')
		return f.read()
	finally:
		if f:
			f.close()


class FileCache(object):
	"""
	Generic file cache.  Notes about its behavior:

	-	If it's been more than N seconds since the file was last stat,
		it peforms a stat, and if (mod time, creat time, inode, size) are
		different from last time, re-reads the file.

	-	It never forgets files.

	-	It never automatically updates the cache when you're not
		calling it.
	"""

	__slots__ = ('_getTimeCallable', '_recheckDelay', '_cache')

	def __init__(self, getTimeCallable, recheckDelay,
	fingerprintCallable=defaultFingerprint,
	getContentsCallable=defaultGetContents):
		"""
		C{getTimeCallable} is a 0-arg callable that returns the current
			time as a C{float|int|long} in seconds.  This can be any
			clock, as long as it increments by 1 every second.

		C{recheckDelay} is a C{float|int|long}.  If file hasn't been
			stat'ed in this many seconds, it will be stat'ed (at the
			next L{getContent} call).

		C{fingerprintCallable} is a callable that takes a filename and
			returns an __eq__able object.

		C{getContentsCallable} is a callable that takes a filename and
			returns the contents of the file as a C{str}.
		"""
		self._getTimeCallable = getTimeCallable
		self._recheckDelay = recheckDelay
		self._fingerprintCallable = fingerprintCallable
		self._getContentsCallable = getContentsCallable
		# TODO: use securedict
		self._cache = {}


	def getContent(self, filename):
		"""
		C{filename} is a C{str} representing a file name.

		Returns a C{str} or raises an exception.
		"""
		timeNow = self._getTimeCallable()
		cachedFile = self._cache.get(filename)
		if cachedFile:
			if cachedFile.checkedAt > timeNow - self._recheckDelay:
				return cachedFile.contents

			fingerprint = self._fingerprintCallable(filename)
			if fingerprint == cachedFile.fingerprint:
				cachedFile.checkedAt = timeNow
				return cachedFile.contents

		fingerprint = self._fingerprintCallable(filename)
		contents = self._getContentsCallable(filename)
		self._cache[filename] = _CachedFile(timeNow, fingerprint, contents)


from pypycpyo import optimizer
optimizer.bind_all_many(vars(), _postImportVars)

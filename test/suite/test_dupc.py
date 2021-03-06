#!/usr/bin/env python
#
# Copyright (c) 2008-2012 WiredTiger, Inc.
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# test_dupc.py
#	test cursor duplication
#

import os, time
import wiredtiger, wttest
from helper import complex_populate, simple_populate, keyPopulate

# Test session.open_cursor with cursor duplication.
class test_duplicate_cursor(wttest.WiredTigerTestCase):
    name = 'test_dupc'
    nentries = 1000

    config = 'key_format='

    scenarios = [
	('file', dict(uri='file:', fmt='r')),
	('file', dict(uri='file:', fmt='S')),
	('table', dict(uri='table:', fmt='r')),
	('table', dict(uri='table:', fmt='S'))
	]

    # Iterate through an object, duplicate the cursor and checking that it
    # matches the original and is set to the same record.
    def iterate(self, uri):
	cursor = self.session.open_cursor(uri, None, None)
	next = 0
	while True:
	    next += 1
	    nextret = cursor.next()
	    if nextret != 0:
		break
	    self.assertEqual(cursor.get_key(), keyPopulate(self.fmt, next))
	    dupc = self.session.open_cursor(None, cursor, None)
	    self.assertEqual(cursor.equals(dupc), 1)
	    self.assertEqual(dupc.get_key(), keyPopulate(self.fmt, next))
	    cursor.close()
	    cursor = dupc
	self.assertEqual(next, self.nentries)
	self.assertEqual(nextret, wiredtiger.WT_NOTFOUND)
	cursor.close()

    def test_duplicate_cursor(self):
	uri = self.uri + self.name

	# A simple, one-file file or table object.
	simple_populate(self, uri, self.config + self.fmt, self.nentries)
	self.iterate(uri)
	self.session.drop(uri, None)

	# A complex, multi-file table object.
	if self.uri == "table:":
	    complex_populate(self, uri, self.config + self.fmt, self.nentries)
	    self.iterate(uri)
	    self.session.drop(uri, None)

if __name__ == '__main__':
    wttest.run()

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

import os, string
import wiredtiger

# python has a filecmp.cmp function, but different versions of python approach
# file comparison differently.  To make sure we get byte for byte comparison,
# we define it here.
def compare_files(self, filename1, filename2):
    self.pr('compareFiles: ' + filename1 + ', ' + filename2)
    bufsize = 4096
    if os.path.getsize(filename1) != os.path.getsize(filename2):
        print filename1 + ' size = ' + str(os.path.getsize(filename1))
        print filename2 + ' size = ' + str(os.path.getsize(filename2))
        return False
    with open(filename1, "rb") as fp1:
        with open(filename2, "rb") as fp2:
            while True:
                b1 = fp1.read(bufsize)
                b2 = fp2.read(bufsize)
                if b1 != b2:
                    return False
                # files are identical size
                if not b1:
                    return True

# confirm a URI doesn't exist.
def confirm_does_not_exist(self, uri):
    self.pr('confirmDoesNotExist: ' + uri)
    self.assertRaises(wiredtiger.WiredTigerError,
        lambda: self.session.open_cursor(uri, None, None))
    import glob
    self.assertEqual(glob.glob('*' + uri.split(":")[1] + '*'), [],
        'confirmDoesNotExist: URI exists, file name matching \"' +
        uri.split(":")[1] + '\" found')

# confirm a URI exists and is empty.
def confirm_empty(self, uri, to_dup=None, config=None):
    self.pr('confirmEmpty: ' + uri)
    cursor = self.session.open_cursor(uri, to_dup, config)
    self.assertEqual(cursor.next(), wiredtiger.WT_NOTFOUND)
    cursor.close()

# population of a simple object, where the keys are the record number.
#    uri:       object
#    config:    prefix of the session.create configuration string
#    rows:      entries to insert
def simple_populate(self, uri, config, rows,\
        to_dup=None, cursor_config=None):
    self.pr('simplePopulate: ' + uri + ' with ' + str(rows) + ' rows')
    self.session.create(uri, config + ',value_format=S')
    cursor = self.session.open_cursor(uri, to_dup, cursor_config)
    if cursor.key_format == 'i' or cursor.key_format == 'u':
        for i in range(0, rows):
            cursor.set_key(i)
            cursor.set_value(str(i) + ': abcdefghijklmnopqrstuvwxyz')
            cursor.insert()
    elif cursor.key_format == 'S':
        for i in range(0, rows):
            cursor.set_key(str(i))
            cursor.set_value(str(i) + ': abcdefghijklmnopqrstuvwxyz')
            cursor.insert()
    else:
        raise AssertionError(
            'simplePopulate: cursor has unexpected key format: ' +
            cursor.key_format)
    cursor.close()

def simple_populate_check(self, uri, to_dup=None, config=None):
    self.pr('simplePopulateCheck: ' + uri)
    cursor = self.session.open_cursor(uri, to_dup, config)
    next = -1
    if cursor.key_format == 'i' or cursor.key_format == 'u':
        for key,val in cursor:
            next += 1
            self.assertEqual(key, next)
            self.assertEqual(val, str(next) + ': abcdefghijklmnopqrstuvwxyz')
    elif cursor.key_format == 'S':
        for key,val in cursor:
            next += 1
            self.assertEqual(key, str(next))
            self.assertEqual(val, str(next) + ': abcdefghijklmnopqrstuvwxyz')
    else:
        raise AssertionError(
            'simplePopulateCheck: cursor has unexpected key format: ' +
            cursor.key_format)
    cursor.close()

# population of a complex object, where the keys are the record number.
#    uri:       object
#    config:    prefix of the session.create configuration string
#    rows:      entries to insert
def complex_populate(self, uri, config, rows):
    self.session.create(uri,
        config + ',value_format=SiSS,' +
        'columns=(record,column2,column3,column4,column5),' +
        'colgroups=(cgroup1,cgroup2,cgroup3,cgroup4,cgroup5,cgroup6)')
    cgname = 'colgroup:' + uri.split(":")[1]
    self.session.create(cgname + ':cgroup1', 'columns=(column2)')
    self.session.create(cgname + ':cgroup2', 'columns=(column3)')
    self.session.create(cgname + ':cgroup3', 'columns=(column4)')
    self.session.create(cgname + ':cgroup4', 'columns=(column2,column3)')
    self.session.create(cgname + ':cgroup5', 'columns=(column3,column4)')
    self.session.create(cgname + ':cgroup6', 'columns=(column4,column5)')
    cursor = self.session.open_cursor(uri, None, None)
    if cursor.key_format == 'i' or cursor.key_format == 'u':
        for i in range(0, rows):
            cursor.set_key(i)
            cursor.set_value(
                str(i) + ': abcdefghijklmnopqrstuvwxyz'[0:i%26],
                i,
                str(i) + ': abcdefghijklmnopqrstuvwxyz'[0:i%23],
                str(i) + ': abcdefghijklmnopqrstuvwxyz'[0:i%18])
            cursor.insert()
    elif cursor.key_format == 'S':
        for i in range(0, rows):
            cursor.set_key(str(i))
            cursor.set_value(
                str(i) + ': abcdefghijklmnopqrstuvwxyz'[0:i%26],
                i,
                str(i) + ': abcdefghijklmnopqrstuvwxyz'[0:i%23],
                str(i) + ': abcdefghijklmnopqrstuvwxyz'[0:i%18])
            cursor.insert()
    else:
        raise AssertionError(
            'complexPopulate: cursor has unexpected key format: ' +
            cursor.key_format)
    cursor.close()

def complex_populate_check(self, uri):
    self.pr('complexPopulateCheck: ' + uri)
    cursor = self.session.open_cursor(uri, None, None)
    i = -1
    if cursor.key_format == 'i' or cursor.key_format == 'u':
        for key, s1, i2, s3, s4 in cursor:
            i += 1
            self.assertEqual(key, i)
            self.assertEqual(s1,
                str(i) + ': abcdefghijklmnopqrstuvwxyz'[0:i%26])
            self.assertEqual(i2, i)
            self.assertEqual(s3,
                str(i) + ': abcdefghijklmnopqrstuvwxyz'[0:i%23])
            self.assertEqual(s4,
                str(i) + ': abcdefghijklmnopqrstuvwxyz'[0:i%18])
            self.assertEqual(i2, i)
    elif cursor.key_format == 'S':
        for key, s1, i2, s3, s4 in cursor:
            i += 1
            self.assertEqual(key, str(i))
            self.assertEqual(s1,
                str(i) + ': abcdefghijklmnopqrstuvwxyz'[0:i%26])
            self.assertEqual(i2, i)
            self.assertEqual(s3,
                str(i) + ': abcdefghijklmnopqrstuvwxyz'[0:i%23])
            self.assertEqual(s4,
                str(i) + ': abcdefghijklmnopqrstuvwxyz'[0:i%18])
    else:
        raise AssertionError(
            'complexPopulateCheck: cursor has unexpected key format: ' +
            cursor.key_format)
    cursor.close()

import os
import sys
import traceback
import unittest
import wiredtiger
import wttest
from collections import OrderedDict

class SnapShotTest(wttest.WiredTigerTestCase):

    snapshots = {
        "snapshot-1": (100, 120),
        "snapshot-2": (200, 220),
        "snapshot-3": (300, 320),
        "snapshot-4": (400, 420),
        "snapshot-5": (500, 520),
        "snapshot-6": (100, 620),
        "snapshot-7": (200, 720),
        "snapshot-8": (300, 820),
        "snapshot-9": (400, 920),
        #"snapshot-a": (500, 600),
    }
    snapshots = OrderedDict(sorted(snapshots.items(), key=lambda t: t[0]))
    URI = "file:__snap"
    
    #def tearDown(self):
       # for snapshot, sizes in self.snapshots.iteritems():
        #    self.sesssion.drop(self.URL, snapshot)
    def setUpConnectionOpen(self, dir):
        conn = wiredtiger.wiredtiger_open(dir, "create, cache_size=100MB")
        self.pr('conn')
        return conn
    def create_session(self):
        config = "key_format=S, value_format=S, internal_page_max=512, leaf_page_max=512"
        self.session.create(self.URI, config)

    def test_snapshot(self):
        self.create_session()
        self.build_file_with_snapshots() # build set of snapshots
        print 'checking build'
        for snapshot_names, sizes in self.snapshots.iteritems():
            print 'snapshot-name= %s' % snapshot_names
            self.check(snapshot_names)
        #print 'checking cursor_lock...'
        self.cursor_lock()
        print 'checking delete...\n'
        self.drop()

    def build_file_with_snapshots(self):
        for snapshot_name, sizes in self.snapshots.iteritems():
            start, stop = sizes
            self.add_records(start, stop)
            buf = "snapshot=%s" % snapshot_name
            assert 0 == self.session.sync(self.URI, buf)
            assert 0 == self.session.verify(self.URI, None)
    
    def add_records(self, start, stop):
        cursor = self.session.open_cursor(self.URI, None, "overwrite")
        for i in range(start, stop+1):
            kbuf = "%010d KEY------" % i
            cursor.set_key(kbuf)
            vbuf = "%010d VALUE----" % i
            cursor.set_value(vbuf)
            result = cursor.insert()
            if result != 0:
                sys.exit("cursor.insert(): %s" % result)
        cursor.close()

            
    def dump_records(self, snapshot_name,  filename):
        file_to_write = open(filename, 'w')
        for snapshot, sizes in self.snapshots.iteritems():
            sizes = self.snapshots[snapshot]
            start, stop = sizes
            for i in range(start, stop+1):
                    file_to_write.write("%010d KEY------\n%010d VALUE----\n" % (i, i))
            if snapshot == snapshot_name:
                break;
        file_to_write.close()

    def check(self, snapshot_name):
        self.dump_records(snapshot_name, "__dump.1")
        self.dump_snap(snapshot_name, "__dump.2")
        if os.system(\
        "sort -u -o __dump.1 __dump.1 && "
        "sort -u -o __dump.2 __dump.2 && "
        "cmp __dump.1 __dump.2 > /dev/null"
        ):
            sys.exit("Check failed, snapshot results for %s were incorrect" % snapshot_name)

    def dump_snap(self, snapshot_name, filename):
        file_to_write = open(filename, 'w')
        buf = "snapshot=%s" % snapshot_name
        cursor = self.session.open_cursor(self.URI, None, buf)
        while cursor.next() == 0:
            key =  cursor.get_key()
            value = cursor.get_value()
            file_to_write.write( "%s\n%s\n" % (key, value))
            print key, value
            #assert 0 == key
            #assert 0 == value
        cursor.close()
        file_to_write.close()

    def cursor_lock(self):
        buf = 'snapshot=snapshot-1'
        cursor = self.session.open_cursor(self.URI, None, buf)
        #try:
        with self.assertRaises(wiredtiger.WiredTigerError) as cm:
            self.session.drop(self.URI, buf)
        #except:
        #    "WiredTigerError: Device or resource busy" in traceback.format_exc()
        assert 0 == cursor.close()
        cursor1 = self.session.open_cursor(self.URI, None, buf)
        print 'cursor1', cursor1
        assert cursor1 != None
        buf = 'snapshot=snapshot-2' 
        cursor2 = self.session.open_cursor(self.URI, None, buf)
        cursor3 = self.session.open_cursor(self.URI, None, None)
        assert 0 == cursor1.close()
        assert 0 == cursor2.close()
        assert 0 == cursor3.close()

    def drop(self):
        for snapshot_name, sizes in self.snapshots.iteritems():
            start, stop = sizes
            buf = 'snapshot=%s' % snapshot_name
            assert 0 == self.session.drop(self.URI, buf)
            assert 0 == self.session.verify(self.URI, None)

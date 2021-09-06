"""
Tests for Message.
"""

__copyright__ = 'Thinnect Inc. 2021'
__license__ = 'MIT'

from nose.tools import assert_equals

from mistconnection.message import Message


class TestMessage(object):

    def test_mm_conversion(self):
        m = Message()
        m.payload = b'\00'
        mm = m.to_mist_message()
        m2 = Message(mm)

        assert_equals(m, m2)

    def test_mm_string(self):
        m = Message()
        m.source = 1
        m.destination = 2
        m.amid = 0x1234
        m.payload = b"HelloWorld!"

        assert_equals(str(m), "0000000000000001->0000000000000002[1234]: 48656C6C6F576F726C6421")

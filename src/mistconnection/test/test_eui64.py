"""
Tests for EUI64.
"""

__copyright__ = 'Thinnect Inc. 2021'
__license__ = 'MIT'

from nose.tools import assert_equals

from mistconnection.eui64 import EUI64

class TestEUI64(object):

    def test_eui_equality(self):
        val = 0x1122334455667788
        eui1 = EUI64(val)
        eui2 = EUI64(val)

        assert_equals(eui1, eui2)
        assert_equals(eui1, val)

    def test_eui_string(self):
        eui = EUI64(0x1122334455667788)

        assert_equals(str(eui), "1122334455667788")

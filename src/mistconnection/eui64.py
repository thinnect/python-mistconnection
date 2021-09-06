"""
EUI64 type.
"""

__copyright__ = 'Thinnect Inc. 2021'
__license__ = 'MIT'


class EUI64(object):

    def __init__(self, eui):
        self._value : int = eui

    def __int__(self):
        return self._value

    def __str__(self):
        return f"{self._value:016X}"

    def __eq__(self, other):
        if isinstance(other, EUI64):
            if self._value == other._value:
                return True

        if isinstance(other, int):
            if self._value == other:
                return True

        return False

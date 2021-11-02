"""
EUI64 type.
"""

__copyright__ = 'Thinnect Inc. 2021'
__license__ = 'MIT'


class EUI64(object):

    def __init__(self, eui):
        if isinstance(eui, str):
            eui = int(eui, 16)
        elif isinstance(eui, bytes):
            if len(eui) == 16:
                eui = int(eui)
            else:
                eui = int(eui.hex(), 16)
        elif isinstance(eui, EUI64):
            eui = int(eui)
        elif isinstance(eui, int):
            pass
        else:
            raise TypeError(type(eui))

        self._value : int = eui

    def __int__(self):
        return self._value

    def __str__(self):
        return f"{self._value:016X}"

    def __eq__(self, other):
        if isinstance(other, EUI64):
            return self._value == other._value
        if isinstance(other, int):
            return self._value == other
        return False

    def __lt__(self, other):
        if isinstance(other, EUI64):
            return self._value < other._value
        if isinstance(other, int):
            return self._value < other
        return False

    def __gt__(self, other):
        if isinstance(other, EUI64):
            return self._value > other._value
        if isinstance(other, int):
            return self._value > other
        return False

    def __le__(self, other):
        if isinstance(other, EUI64):
            return self._value <= other._value
        if isinstance(other, int):
            return self._value <= other
        return False

    def __ge__(self, other):
        if isinstance(other, EUI64):
            return self._value >= other._value
        if isinstance(other, int):
            return self._value >= other
        return False

    def __ne__(self, other):
        if isinstance(other, EUI64):
            return self._value != other._value
        if isinstance(other, int):
            return self._value != other
        return False

    def __hash__(self):
        return self._value

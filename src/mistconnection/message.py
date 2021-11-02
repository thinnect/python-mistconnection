"""
Mist cloud AMQP message.
"""

__copyright__ = 'Thinnect Inc. 2021'
__license__ = 'MIT'


import time

from .eui64 import EUI64
from .mist_pb2 import MistMessage


class Message(object):

    def __init__(self, mm: MistMessage = None):
        self.source: EUI64 = EUI64(0)
        self.destination: EUI64 = EUI64(0)
        self.gateway: EUI64 = EUI64(0)
        self.amid: int = 0
        self.payload: bytes = b''

        self.rssi: int = -128
        self.lqi: int = 0

        self.group: int = 0
        self.channel: int = 0

        self.timestamp: float = time.time()

        if mm is not None:
            self.from_mist_message(mm)

    def __setattr__(self, attr, val):
        if attr in ("source", "destination", "gateway") and isinstance(val, int):
            val = EUI64(val)
        super().__setattr__(attr, val)

    def __str__(self):
    	return f"{self.source}->{self.destination}[{self.amid:04X}]: {self.payload.hex().upper()}"

    def from_mist_message(self, mm: MistMessage):
        self.source = mm.source
        self.destination = mm.destination
        self.gateway = mm.gateway
        self.amid = mm.amid
        self.payload = bytes(mm.payload)

        self.rssi = mm.rssi
        self.lqi = mm.lqi
        self.group = mm.group
        self.channel = mm.channel

        self.timestamp = mm.timestamp.ToSeconds()

    def to_mist_message(self) -> MistMessage:
        mm = MistMessage()

        mm.destination = int(self.destination)
        mm.source = int(self.source)
        mm.gateway = int(self.gateway)
        mm.amid = self.amid
        mm.payload = self.payload

        mm.rssi = self.rssi
        mm.lqi = self.lqi
        mm.group = self.group
        mm.channel = self.channel

        mm.timestamp.FromMilliseconds(int(self.timestamp * 1000))

        return mm

    def __eq__(self, other):
        if (isinstance(other, Message)):
            return (self.source == other.source
                and self.destination == other.destination
                and self.gateway == other.gateway
                and self.amid == other.amid
                and self.payload == other.payload
                and self.rssi == other.rssi
                and self.lqi == other.lqi
                and self.group == other.group
                and self.channel == other.channel
                and self.timestamp == other.timestamp
                )
        return False

"""
Mist AMQP connection.
"""

__copyright__ = 'Thinnect Inc. 2021'
__license__ = 'MIT'


import threading
import socket
import queue
import pika
import time

from typing import Union
from typing import Callable
from typing import Dict
from .message import Message
from .eui64 import EUI64
from .mist_pb2 import MistMessage

from google.protobuf.message import DecodeError

import logging
log = logging.getLogger(__name__)


# A type hint for the receiver callback - either a function or a queue
type_mm_receiver = Union[Callable[[Message], None], queue.Queue]


class Connection(threading.Thread):
    """The MistConnection class."""

    def __init__(self, amqp : str, exchange: str, eui: Union[EUI64, int], gateway: Union[EUI64, int, None] = None):
        """
        amqp : str
            AMQP connection string amqps://username:password@server/?socket_timeout=123
        exchange : str
            The AMQP exchange to use for messaging, mistx for example.
        eui : EUI64
            The identity of the connection - source of outgoing messages.
        gateway : EUI64, optional
            The gateway through which to communicate. Can be None, in which case any and all are used,
            specific gateways for outgoing messages can always be set in the message.
        """
        super(Connection, self).__init__()

        self._interrupted : bool = False
        self._amqp = amqp
        self._exchange = exchange

        if isinstance(eui, EUI64):
            self._eui64 = eui
        elif isinstance(eui, int):
            self._eui64 = EUI64(eui)
        else:
            raise TypeError(f"The eui must either be an EUI64 or an int, it was {type(eui)}")

        if gateway is None:
            self._gateway = "*"
        elif isinstance(gateway, EUI64):
            self._gateway = str(gateway)
        else:
            self._gateway = f"{gateway:016X}"

        self._name = socket.gethostname()

        self._out = None

        self._connection_backoff = 1

        self._receivers : Dict[int, type_mm_receiver] = {}

    def send(self, message: Message) -> None:
        if self._out is not None:
            self._out.put(message)
        else:
            log.warning("message discarded")

    def register_receiver(self, ptype: int,
                          receiver: type_mm_receiver) -> None:
        self._receivers[ptype] = receiver

    def _deliver(self, mm: MistMessage) -> None:
        m = Message(mm)

        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"RCV: {m}")

        if m.amid in self._receivers:
            receiver = self._receivers[m.amid]
            if callable(receiver):
                receiver(m)
            elif isinstance(receiver, queue.Queue):
                receiver.put(m)
            else:
                log.error(f"AMID {m.amid:016X} bad receiver type '{type(receiver)}'")

    def _send(self, outgoing, m: Message) -> None:

        if m.source == 0:
            m.source = self._eui64

        if m.gateway == 0:
            if self._gateway == "*":
                rgw = "FFFFFFFFFFFFFFFF"
            else:
                rgw = self._gateway
        else:
            rgw = str(m.gateway)

        rkey = f'mist.{rgw}.{m.destination}'
        body = m.to_mist_message().SerializeToString()

        outgoing.basic_publish(exchange=self._exchange, routing_key=rkey, body=body)

        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"{rkey} {body.hex().upper()}")

    def connect(self):
        self.start()

    def close(self):
        self._interrupted = True
        self.join()

    def _backoff(self):
        for _ in range(self._connection_backoff):
            if self._interrupted:
                break
            time.sleep(1)
        if self._connection_backoff < 60:
            self._connection_backoff *= 2

    def run(self):
        log.debug("run")

        while not self._interrupted:
            connection = None
            try:
                cp = pika.URLParameters(self._amqp)
                connection = pika.BlockingConnection(cp)

                incoming = connection.channel()
                outgoing = connection.channel()

                qn = f'cloud-{self._name}-{self._gateway}'

                qdresult = incoming.queue_declare(queue=qn, auto_delete=True)
                qname = qdresult.method.queue

                incoming.queue_bind(queue=qname, exchange=self._exchange,
                                        routing_key=f"cloud.{self._gateway}.{self._eui64}")

                incoming.queue_bind(queue=qname, exchange=self._exchange,
                                        routing_key=f"cloud.{self._gateway}.FFFFFFFFFFFFFFFF")

                log.info("connected")
                self._connection_backoff = 1
                self._out = queue.Queue()

                for method, _, body in incoming.consume(qname, True, True, None, 1.0):

                    if method is not None:
                        mm = MistMessage()
                        try:
                            mm.ParseFromString(body)
                        except DecodeError:
                            log.warning(f'\nERROR PARSING:\n{method.routing_key}\n{body.hex()}\n')
                        self._deliver(mm)

                    while True:
                        try:
                            message = self._out.get(False)
                        except queue.Empty:
                            break
                        self._send(outgoing, message)

                    if self._interrupted:
                        break

            except pika.exceptions.AMQPError as e:
                log.warning("disconnected (%s)", e)
                self._backoff()
            except socket.error as e:
                log.warning("unable to connect (%s)", e)
                self._backoff()

            if connection is not None:
                try:
                    connection.close()
                    log.info("closed")
                except pika.exceptions.ConnectionWrongStateError:
                    pass  # already closed

                connection = None

            if self._out is not None:
                if self._out.qsize() > 0:
                    log.warning("discarded %d old messages", self._out.qsize())
                self._out = None

        log.debug("over")

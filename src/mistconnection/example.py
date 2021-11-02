"""
A really basic example of how to connect, receive and send using the MistConnection.
"""

__copyright__ = 'Thinnect Inc. 2021'
__license__ = 'MIT'


import argparse
import time

from mistconnection.connection import Connection
from mistconnection.message import Message

import logging


# Print any received messages
def receive(message):
    print(message)


if __name__ == '__main__':

    # Enable logging, but disable it for pika, which is very chatty
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("pika").propagate = False

    parser = argparse.ArgumentParser(description='Example setup of a mistconnection.')
    parser.add_argument('--amqp', default='amqps://user:password@server.net',
                        help='The AMQP connection string to use')
    parser.add_argument('--exchange', default='mistx',
                        help='The exchange to use for messaging.')
    args = parser.parse_args()

    conn = Connection(args.amqp, args.exchange, 0x1122334455667788, None)

    # Register a receiver for AMID 0001
    conn.register_receiver(0x0001, receive)

    # Start connecting to the server
    conn.connect()

    # Listen for any messages until interrupted
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    # Send a message when interrupted
    m = Message()
    m.destination = 0x1234567812345678
    m.payload = b"\00\11\22\33"
    conn.send(m)

    # Listen for any responses
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    # Shut it down
    conn.close()

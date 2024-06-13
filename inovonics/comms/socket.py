# -*- encoding: utf-8 -*-
from __future__ import print_function, unicode_literals, division, absolute_import
import logging
import socket

from inovonics.comms.base import CommBase


class Socket(CommBase):
    logger = logging.getLogger('inovonics.comms.Socket')

    def __init__(self, host='', port=10001):
        super(Socket, self).__init__()
        self.host = host
        self.port = port

    def run(self):
        self.logger.info('Socket started')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(5)
        sock.settimeout(0.5)

        while not self._stop_flag.is_set():
            try:
                (client, addr) = sock.accept()
            except socket.timeout:
                continue
            self.logger.debug('Socket "%s" connected' % (addr))
            client.settimeout(0.5)
            while True and not self._stop_flag.is_set():
                try:
                    data = client.recv(2048)
                except socket.timeout:
                    break
                if not data:
                    break
                self._buffer.extend(bytearray(data))
            self.parse()
            client.close()
            self.logger.debug('Socket disconnected')
        sock.close()
        self.logger.info('Socket stopped')

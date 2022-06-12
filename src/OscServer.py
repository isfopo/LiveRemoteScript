import time
from typing import Tuple, Any, Callable
import errno
import socket

from .helpers.values import convertTuple

from .OscMessage import OscMessage
from .OscMessageBuilder import OscMessageBuilder
from .consts import OSC_LISTEN_PORT, OSC_REMOTE_PORT, OUTGOING_MESSAGE_RATE_LIMIT


class OscServer:
    def __init__(self, control_surface, local_addr=('', OSC_LISTEN_PORT), remote_addr=('<broadcast>', OSC_REMOTE_PORT)) -> None:
        self._control_surface = control_surface
        self._local_addr = local_addr
        self._remote_addr = remote_addr

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setblocking(0)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._socket.bind(self._local_addr)

        self._callbacks = {}
        self._outgoing_messages = {}
        self._last_message = None

        self._control_surface.schedule_message(0, self.advertize)

    def advertize(self):
        if self._remote_addr[0] == "<broadcast>":
            self.send("/live/broadcast", [self._control_surface.__version__])
            self._control_surface.show_message("looking for clients")
            self._control_surface.schedule_message(64, self.advertize)
        else:
            self._control_surface.show_message(
                "Connected to: " + self._remote_addr[0])

    def add_handler(self, address: str, handler: Callable):
        self._callbacks[address] = handler

    def send(self, address: str, params: Tuple[Any] = ()) -> None:
        """
        Send an OSC message.
        Args:
            address: The OSC address (e.g. /frequency)
            params: A tuple of zero or more OSC params
        """

        now = time.time()
        locationParams = convertTuple(params[:-1])
        addressAndLocation = address + locationParams

        if addressAndLocation in self._outgoing_messages and now - self._outgoing_messages[addressAndLocation] > OUTGOING_MESSAGE_RATE_LIMIT or not addressAndLocation in self._outgoing_messages:
            if addressAndLocation in self._outgoing_messages:
                self._outgoing_messages.pop(addressAndLocation)
            self._outgoing_messages[addressAndLocation] = now

            msg_builder = OscMessageBuilder(address)
            for param in params:
                msg_builder.add_arg(param)

            try:
                msg = msg_builder.build()

                if msg != self._last_message:
                    self._last_message = msg
                    self._socket.sendto(msg.dgram, self._remote_addr)

            except Exception as e:
                raise e

    def process(self) -> None:
        try:
            while True:
                data, addr = self._socket.recvfrom(65536)

                message = OscMessage(data)

                if message.address == "/live/ping":
                    self.send('/live/ping')

                if message.address == "/live/connect":
                    self._remote_addr = (addr[0], OSC_REMOTE_PORT)
                    self._control_surface.init_api()
                    self._control_surface.show_message(
                        "Connected to: " + addr[0])

                elif message.address == "/live/disconnect":
                    prev_remote_addr = self._remote_addr
                    self._remote_addr = ('<broadcast>', OSC_REMOTE_PORT)

                    # TODO handle shutting down api

                    self._control_surface.show_message(
                        "Disconnected from: " + prev_remote_addr[0])
                    self._control_surface.schedule_message(0, self.advertize)

                elif message.address in self._callbacks:
                    callback = self._callbacks[message.address]
                    response = callback(message.params)

                    if response is not None:
                        self.send(message.address, response)

        except Exception as e:
            if hasattr(e, "errno"):
                if e.errno == errno.EAGAIN:
                    return
            else:
                raise e

    def shutdown(self) -> None:
        self._socket.close()


class ServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        self._control_surface.show_message(
            'Received %r from %s' % (message, addr))

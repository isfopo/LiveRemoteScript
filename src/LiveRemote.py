from __future__ import with_statement

import Live
from _Framework.ControlSurface import ControlSurface
from .helpers.version import get_version
from .handlers.SongHandler import SongHandler
from .handlers.MasterTrackHandler import MasterTrackHandler

from .OscServer import OscServer
from .handlers.TrackHandler import TrackHandler
from .handlers.ReturnTrackHandler import ReturnTrackHandler


class LiveRemote(ControlSurface):
    __module__ = __name__
    __doc__ = "Script to send and receive Osc messages in Live via a remote script"

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self.__version__ = get_version()
        self._live = Live.Application.get_application()
        self.song = self._live.get_document()
        self.handlers = []
        self.api_is_on = False

        self.server = OscServer(self)
        self.schedule_message(0, self.tick)

    def init_api(self):
        if not self.api_is_on:
            self.api_is_on = True
            with self.component_guard():
                self.handlers = [
                    SongHandler(self, "song"),
                    ReturnTrackHandler(self, "return_track"),
                    MasterTrackHandler(self, "master_track"),
                    TrackHandler(self, "track"),
                ]

    def tick(self):
        """
        Called once per "tick".
        """
        try:
            self.server.process()
        except Exception as e:
            self.disconnect()
            raise e

        self.schedule_message(1, self.tick)

    def disconnect(self) -> None:
        """
        Clean up on disconnect
        """
        self.server.shutdown()
        ControlSurface.disconnect(self)
        return None

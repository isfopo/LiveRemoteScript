from .TrackHandler import TrackHandler


class ReturnTrackHandler(TrackHandler):
    def __init__(self, manager, object):
        super().__init__(manager, object)

    methods = [
    ]
    properties_r = [
    ]
    properties_rw = [
        "color",
        "mute",
        "solo",
        "name"
    ]

    mixer_properties_r = [
    ]
    mixer_properties_rw = [
        "volume",
        "panning",
        "crossfade_assign",
        "panning_mode"
    ]

    def set_tracks_listeners(self):
        self.server.send("/live/song/return_tracks",
                         (len(self.song.return_tracks),))
        self._clear_listeners()
        for index, track in enumerate(self.song.return_tracks):
            for prop in self.properties_r + self.properties_rw:
                self._start_listen(track, prop, index)
            for prop in self.mixer_properties_r + self.mixer_properties_rw:
                self._start_listen(track.mixer_device, prop, index)

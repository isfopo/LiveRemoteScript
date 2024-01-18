from .TrackHandler import TrackHandler


class MasterTrackHandler(TrackHandler):
    def __init__(self, manager, object):
        super().__init__(manager, object)

    methods = [
    ]
    properties_r = [
    ]
    properties_rw = [
        "color"
    ]

    mixer_properties_r = [
    ]
    mixer_properties_rw = [
        "volume",
        "panning",
        "panning_mode"
    ]

    def set_tracks_listeners(self):
        self._clear_listeners()
        for prop in self.properties_r + self.properties_rw:
            self._start_listen(self.song.master_track, prop)
        for prop in self.mixer_properties_r + self.mixer_properties_rw:
            self._start_listen(self.song.master_track.mixer_device, prop)

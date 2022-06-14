from functools import partial
from .HandlerBase import HandlerBase


class SongHandler(HandlerBase):
    def __init__(self, manager, object):
        super().__init__(manager, object)

    methods = [
        "start_playing",
        "stop_playing",
        "continue_playing",
        "stop_all_clips",
        "create_audio_track",
        "create_midi_track",
        "create_return_track",
        "create_scene",
        "jump_by"
    ]

    properties_rw = [
        "arrangement_overdub",
        "back_to_arranger",
        "clip_trigger_quantization",
        "current_song_time",
        "groove_amount",
        "loop",
        "loop_length",
        "loop_start",
        "metronome",
        "midi_recording_quantization",
        "nudge_down",
        "nudge_up",
        "punch_in",
        "punch_out",
        "record_mode",
        "tempo",
        "signature_numerator",
        "signature_denominator",
        "session_record"
    ]
    properties_r = [
        "is_playing"
    ]

    def init_api(self):
        for method in self.methods:
            callback = partial(self._call_method, self.song, method)
            self.server.add_handler("/live/song/%s" % method, callback)
        for prop in self.properties_r + self.properties_rw:
            self.server.add_handler(
                "/get/live/song/%s" % prop, partial(self._get, self.song, prop))
            self._start_listen(self.song, prop)
        for prop in self.properties_rw:
            self.server.add_handler(
                "/set/live/song/%s" % prop, partial(self._set, self.song, prop))

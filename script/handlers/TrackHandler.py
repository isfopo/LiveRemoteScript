import Live
from typing import Tuple, Any
from .HandlerBase import HandlerBase


class TrackHandler(HandlerBase):
    def __init__(self, manager, object):
        super().__init__(manager, object)

    methods = [
        "stop_all_clips"
    ]
    properties_r = [
        "output_meter_left",
        "output_meter_right"
    ]
    properties_rw = [
        "color",
        "mute",
        "solo",
        "arm",
        "name"
    ]

    mixer_methods = [
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
        self.server.send("/live/song/tracks", (len(self.song.tracks),))
        self._clear_listeners()
        for index, track in enumerate(self.song.tracks):
            for prop in self.properties_r + self.properties_rw:
                self._start_listen(track, prop, index)
            for prop in self.mixer_properties_r + self.mixer_properties_rw:
                self._start_listen(track.mixer_device, prop, index)

    def set_sends_listeners(self):
        """
            Adds listeners for each send and sends listener for each track.
            Done with a series of callbacks to allocate new memory block for each object.
            Otherwise, all message will contain the last track number and send value allocated.
        """
        def for_send(t_index, s_index, send):
            def send_listener_callback():
                osc_address = "/live/%s/send" % (self.object)
                self.server.send(
                    osc_address, (t_index, s_index, send.value))

            send.add_value_listener(send_listener_callback)

        def for_track(t_index, track):
            track.mixer_device.add_sends_listener(self.set_sends_listeners)
            for s_index, send in enumerate(track.mixer_device.sends):
                for_send(t_index, s_index, send)

        for t_index, track in enumerate(self.song.tracks):
            for_track(t_index, track)

    def init_api(self):
        def create_track_callback(func, *args):
            def track_callback(params: Tuple[Any]):
                track_index = params[0]
                track = self.song.tracks[track_index]
                return func(track, *args, params[1:])

            return track_callback

        def create_track_mixer_device_callback(func, prop):
            def mixer_device_callback(params: Tuple[Any]):
                track_index = params[0]
                mixer_device = self.song.tracks[track_index].mixer_device
                attr = getattr(mixer_device, prop)
                if isinstance(attr, Live.DeviceParameter.DeviceParameter):
                    return func(getattr(mixer_device, prop), "value", params[1:])
                else:
                    return func(mixer_device, prop, params)

            return mixer_device_callback

        for method in self.methods:
            self.server.add_handler("/live/%s/%s" % (self.object, method),
                                    create_track_callback(self._call_method, method))
        for prop in self.properties_r + self.properties_rw:
            self.server.add_handler("/get/live/%s/%s" % (self.object, prop),
                                    create_track_callback(self._get, prop))
        for prop in self.properties_rw:
            self.server.add_handler("/set/live/%s/%s" % (self.object, prop),
                                    create_track_callback(self._set, prop))

        for method in self.mixer_methods:
            self.server.add_handler("/live/%s/%s" % (self.object, method),
                                    create_track_mixer_device_callback(self._call_method, method))
        for prop in self.mixer_properties_r + self.properties_rw:
            self.server.add_handler("/get/live/%s/%s" % (self.object, prop),
                                    create_track_mixer_device_callback(self._get, prop))
        for prop in self.mixer_properties_rw:
            self.server.add_handler("/set/live/%s/%s" % (self.object, prop),
                                    create_track_mixer_device_callback(self._set, prop))

        self.set_tracks_listeners()

        self.song.add_tracks_listener(self.set_tracks_listeners)

        self.set_sends_listeners()

        def track_get_send(track, params: Tuple[Any] = ()):
            return track.mixer_device.sends[params[0]]

        def track_set_send(track, params: Tuple[Any] = ()):
            send_id, value = params
            track.mixer_device.sends[send_id].value = value

        self.server.add_handler(
            "/get/live/%s/send" % self.object, create_track_callback(track_get_send))
        self.server.add_handler(
            "/set/live/%s/send" % self.object, create_track_callback(track_set_send))

        """
        Returns a list of clip properties, or Nil if clip is empty
        """
        if self.object == "track":
            def track_get_clip_names(track, params: Tuple[Any]):
                return tuple(clip_slot.clip.name if clip_slot.clip else None for clip_slot in track.clip_slots)

            def track_get_clip_lengths(track, params: Tuple[Any]):
                return tuple(clip_slot.clip.length if clip_slot.clip else None for clip_slot in track.clip_slots)

            self.server.add_handler(
                "/get/live/%s/clips/name", create_track_callback(track_get_clip_names))
            self.server.add_handler(
                "/get/live/%s/clips/length", create_track_callback(track_get_clip_lengths))

        def track_get_num_devices(track, params: Tuple[Any]):
            return len(track.devices),

        def track_get_device_names(track, params: Tuple[Any]):
            return tuple(device.name for device in track.devices)

        def track_get_device_types(track, params: Tuple[Any]):
            return tuple(device.type for device in track.devices)

        def track_get_device_class_names(track, params: Tuple[Any]):
            return tuple(device.class_name for device in track.devices)

        def track_get_device_can_have_chains(track, params: Tuple[Any]):
            return tuple(device.can_have_chains for device in track.devices)

        """
         - name: the device's human-readable name
         - type: 0 = audio_effect, 1 = instrument, 2 = midi_effect
         - class_name: e.g. Operator, Reverb, AuPluginDevice, PluginDevice, InstrumentGroupDevice
        """
        self.server.add_handler(
            "/get/live/%s/num_devices" % self.object, create_track_callback(track_get_num_devices))
        self.server.add_handler(
            "/get/live/%s/devices/name" % self.object, create_track_callback(track_get_device_names))
        self.server.add_handler(
            "/get/live/%s/devices/type" % self.object, create_track_callback(track_get_device_types))
        self.server.add_handler(
            "/get/live/%s/devices/class_name" % self.object, create_track_callback(track_get_device_class_names))
        self.server.add_handler("/get/live/%s/devices/can_have_chains" % self.object,
                                create_track_callback(track_get_device_can_have_chains))

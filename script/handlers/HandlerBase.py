import Live
from typing import Optional, Tuple, Any


class HandlerBase():
    def __init__(self, manager, object):
        self.manager = manager
        self.server = self.manager.server
        self.song = self.manager.song
        self.object = object
        self.listener_functions = {}
        self.init_api()

    def init_api(self):
        pass

    def clear_api(self):
        self._clear_listeners()

    # --------------------------------------------------------------------------------
    # Generic callbacks
    # --------------------------------------------------------------------------------
    def _call_method(self, target, method, params: Optional[Tuple[Any]] = ()):
        getattr(target, method)(*params)

    def _set(self, target, prop, params: Tuple[Any]) -> None:
        setattr(target, prop, params[0])

    def _get(self, target, prop, params: Optional[Tuple[Any]] = ()) -> Tuple[Any]:
        return getattr(target, prop),

    def _start_listen(self, target, prop, index=None, params: Optional[Tuple[Any]] = ()) -> None:
        if isinstance(getattr(target, prop), Live.DeviceParameter.DeviceParameter):
            parameter = getattr(target, prop)

            def parameter_property_changed_callback():
                osc_address = "/live/%s/%s" % (self.object, prop)
                if index is not None:
                    self.server.send(
                        osc_address, (index, parameter.value,))
                else:
                    self.server.send(osc_address, (parameter.value,))

            if (target, prop) in self.listener_functions:
                parameter.remove_value_listener(self.listener_functions[(target, prop)
                                                                        ])

            parameter.add_value_listener(parameter_property_changed_callback)
            self.listener_functions[(target, prop)
                                    ] = parameter_property_changed_callback

            parameter_property_changed_callback()

        else:
            def property_changed_callback():
                value = getattr(target, prop)
                osc_address = "/live/%s/%s" % (self.object, prop)
                if index is not None:
                    self.server.send(osc_address, (index, value,))
                else:
                    self.server.send(osc_address, (value,))

            add_listener_function_name = "add_%s_listener" % prop
            self._stop_listen(target, prop)

            add_listener_function = getattr(target, add_listener_function_name)
            add_listener_function(property_changed_callback)
            self.listener_functions[(target, prop)] = property_changed_callback

            property_changed_callback()

    def _stop_listen(self, target, prop, params: Optional[Tuple[Any]] = ()) -> None:
        if (target, prop) in self.listener_functions:
            listener_function = self.listener_functions[(target, prop)]
            remove_listener_function_name = "remove_%s_listener" % prop
            remove_listener_function = getattr(
                target, remove_listener_function_name)
            remove_listener_function(listener_function)
            del self.listener_functions[(target, prop)]

    def _clear_listeners(self):
        for listener in self.listener_functions:
            self._stop_listen(listener)

        self.listener_functions = {}

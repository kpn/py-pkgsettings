import functools


class SimpleSettings(object):
    def as_dict(self):
        return self.__dict__


class Settings(object):

    def __init__(self):
        self._chain = [SimpleSettings()]
        self._override_settings = {}

    def __getattr__(self, attr):
        for item in self._chain:
            try:
                return getattr(item, attr)
            except AttributeError:
                pass
        raise AttributeError(attr)

    def as_dict(self):
        result = dict()
        for item in reversed(self._chain):
            result.update(item.as_dict())
        return result

    def configure(self, obj=None, **kwargs):
        """
        Settings that will be used by the time_execution decorator

        Attributes:
            obj (Optional[object]): Class or object with the settings as attributes
            backends (list): List of backends
            hooks (list): List of hooks
            duration_field (string): Name of the field to store the duration value
        """
        if not obj:
            obj = SimpleSettings()
            for key, new_value in kwargs.items():
                setattr(obj, key, new_value)

        self._chain.insert(0, obj)

    def __enter__(self):
        self._override_enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self._override_disable()

    def __call__(self, func=None, *args, **kwargs):
        if func:
            @functools.wraps(func)
            def inner(*args, **kwargs):
                with self:
                    return func(*args, **kwargs)

            return inner
        elif kwargs:
            self._override_settings = kwargs
            return self

    def _override_enable(self):
        obj = SimpleSettings()
        for key, new_value in self._override_settings.items():
            setattr(obj, key, new_value)

        self._chain.insert(0, obj)

    def _override_disable(self):
        self._chain.pop(0)
        self._override_settings = {}

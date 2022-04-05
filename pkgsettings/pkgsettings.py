import functools
import warnings


class DuplicateConfigureWarning(UserWarning):
    pass


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

    def children(self):
        """
        Tries to return a generator of all settings objects in the chain, recursively.
        This might not yield all settings objects, if they include
        other settings objects not by using the children() call.
        :return: generator of settings objects.
        """
        for child in self._chain:
            yield child
            children = getattr(child, "children", None)
            if callable(children):
                for settings in children():
                    yield settings

    def _has_duplicates(self):
        """
        Check if there are duplicates in the chained settings objects.
        :return: True if there are duplicate, False otherwise.
        """
        children = set()
        for settings in self.children():
            if settings in children:
                return True

            children.add(settings)

        return False

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

        if obj is self:
            warnings.warn("Refusing to add ourselves to the chain", DuplicateConfigureWarning)
            return

        self._chain.insert(0, obj)

        if self._has_duplicates():
            warnings.warn("One setting was added multiple times, maybe a loop?", DuplicateConfigureWarning)

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


class PrefixedSettings(object):
    def __init__(self, settings, prefix=None):
        self.settings = settings
        self.prefix = prefix

    def __getattr__(self, attr):
        if self.prefix:
            attr = self.prefix + attr
        return getattr(self.settings, attr)

from __future__ import annotations

import functools
import warnings
from typing import Any, Callable, Dict, Generator, Optional, TypeVar, overload

from typing_extensions import Self

_F = TypeVar("_F", bound=Callable[..., Any])


class DuplicateConfigureWarning(UserWarning):
    pass


class SimpleSettings:
    """
    A single layer of settings.

    Layers get stacked on each other in `Settings`, so allowing to override specific options.
    """

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__


class Settings:
    def __init__(self) -> None:
        self._chain = [SimpleSettings()]
        self._override_settings: Dict[str, Any] = {}

    def __getattr__(self, attr: str) -> Any:
        for item in self._chain:
            try:
                return getattr(item, attr)
            except AttributeError:
                pass
        raise AttributeError(attr)

    def as_dict(self) -> Dict[str, Any]:
        result = {}
        for item in reversed(self._chain):
            result.update(item.as_dict())
        return result

    def children(self) -> Generator[SimpleSettings, None, None]:
        """
        Tries to return a generator of all settings objects in the chain, recursively.
        This might not yield all settings objects, if they include
        other settings objects not by using the `children()` call.

        :return: generator of settings objects.
        """
        for child in self._chain:
            yield child
            children = getattr(child, "children", None)
            if callable(children):
                for settings in children():
                    yield settings

    def _has_duplicates(self) -> bool:
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

    def configure(self, obj: Optional[Any] = None, **kwargs) -> None:
        """
        Settings that will be used by the time_execution decorator

        Args:
            obj: class or object with the settings as attributes
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

    def __enter__(self) -> Self:
        self._override_enable()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._override_disable()

    @overload
    def __call__(self, func: _F) -> _F:
        ...

    @overload
    def __call__(self, **override_settings: Any) -> Self:
        ...

    def __call__(self, func=None, **override_settings: Any):
        """
        Override settings for a decorated function.

        Example:
             >>> settings = Settings()
             >>>
             >>> @settings(option=42)
             >>> def foo():
             >>>     assert settings.option == 42
        """

        if func:

            @functools.wraps(func)
            def inner(*args, **kwargs):
                with self:
                    return func(*args, **kwargs)

            return inner

        elif override_settings:
            self._override_settings = override_settings
            return self

    def _override_enable(self) -> None:
        obj = SimpleSettings()
        for key, new_value in self._override_settings.items():
            setattr(obj, key, new_value)

        self._chain.insert(0, obj)

    def _override_disable(self) -> None:
        self._chain.pop(0)
        self._override_settings = {}


class PrefixedSettings:
    def __init__(self, settings: Any, prefix: Optional[str] = None) -> None:
        self.settings = settings
        self.prefix = prefix

    def __getattr__(self, attr: str) -> Any:
        if self.prefix:
            attr = self.prefix + attr
        return getattr(self.settings, attr)

from __future__ import annotations

from contextlib import suppress
from contextvars import ContextVar, Token
from dataclasses import asdict, dataclass, field, fields
from functools import wraps
from types import TracebackType
from typing import TYPE_CHECKING, Any, Callable, ContextManager, Dict, Generic, Iterable, Optional, Set, Type, TypeVar
from warnings import warn

from typing_extensions import ParamSpec, Self

_P = ParamSpec("_P")
_R = TypeVar("_R")


class DuplicateConfigureWarning(UserWarning):
    pass


@dataclass
class Settings:
    __slots__ = ("__parent__", "__legacy_keys__", "__dataclass_keys__", "__dict__")

    if TYPE_CHECKING:
        __parent__: ContextVar[Self] = field(init=False)
        """
        Possible layer on top of the current settings instance which gets precedence
        in the attribute lookup. If missing – the current instance is the grandparent.

        The better idea would be to keep track of a child.
        However, that would require a mutable grandparent, which in turn would break the backwards compatibility.

        The `ContextVar` here allows thread- and task-safety when used with the context manager.
        If a user tries to call `with settings(…)` in multiple threads or concurrent tasks,
        they would create a «fork» split from the grandparent, so the threads/tasks would be safe.
        """

        __legacy_keys__: Set[str] = field(init=False)
        """
        Settings names that are NOT members of a possible dataclass.

        This is to keep the backwards compatibility for settings not inherited from `Settings`.
        """

        __dataclass_keys__: Set[str] = field(init=False)
        """
        Settings names that ARE members of the dataclass.

        This is to aid keeping track of `__legacy_keys__`.
        """

    def __init__(self, **kwargs) -> None:
        # For backwards compatibility we allow extra arguments:
        for name, value in kwargs.items():
            setattr(self, name, value)
        self._ensure_legacy_keys().update(kwargs.keys() - self._ensure_dataclass_keys())
        self.__post_init__()

    def __post_init__(self) -> None:
        """Do nothing. Exists for compatibility between dataclass-style and legacy-style settings."""

    def __getattribute__(self, name: str) -> Any:
        if name.startswith("_"):
            # Quick path for the internal attributes.
            return object.__getattribute__(self, name)
        try:
            parent = Settings._ensure_parent(self).get()
        except LookupError:
            # `self` is the topmost layer, so we just proceed to get the attribute from `self`.
            pass
        else:
            # There's at least one parent, and so it has the precedence.
            with suppress(AttributeError):
                return Settings.__getattribute__(parent, name)
        # There's no parent or no parent got the attribute, so try and get it from `self`.
        return object.__getattribute__(self, name)

    def as_dict(self) -> Dict[str, Any]:
        dict_ = asdict(self)
        for name in Settings._ensure_legacy_keys(self):
            dict_[name] = getattr(self, name)
        try:
            parent = Settings._ensure_parent(self).get()
        except LookupError:
            pass
        else:
            # The parent takes the precedence.
            dict_.update(Settings.as_dict(parent))
        return dict_

    def children(self) -> Iterable[Settings]:
        """
        Iterate through all the layers, from the bottom to the top
        (through all the children to the grandparent).
        """
        yield self
        try:
            parent = Settings._ensure_parent(self).get()
        except LookupError:
            pass
        else:
            yield from Settings.children(parent)

    def configure(self, obj: Any = None, **kwargs: Any) -> None:
        """
        Update the current settings with the provided values.

        Args:
            obj: optional, additional layer to put on top of the current settings
            kwargs: new values for the current settings instance

        Notes:
            - If you are trying to set defaults, it's better to make a proper dataclass
              inherited from `Settings`.
            - If the current instance is not a topmost layer, the `obj` will replace it.
              This is, however, not a typical not recommended use scenario.
        """

        for name, value in kwargs.items():
            setattr(self, name, value)
        self._ensure_legacy_keys().update(kwargs.keys() - self._ensure_dataclass_keys())

        if obj is not None:
            for other_layer in Settings.children(obj):
                if other_layer is self:
                    warn("attempting to add the layer that makes a loop with `self`", DuplicateConfigureWarning)
                    break
            else:
                self._ensure_parent().set(obj)

    def __call__(self, **kwargs: Any) -> _ContextManager[Self]:
        """
        Create the additional settings layer, which will be added to the top
        upon entering the context manager scope.

        Notes:
            - When applied to a non-topmost layer, this will override all the layers above.
              This is, however, not a typical nor recommended use scenario.
        """
        return _ContextManager[Self](
            parent=Settings(**kwargs),  # the new temporary layer…
            child=Settings._get_grandparent(self),  # …which will be attached on top of the current grandparent
            grandchild=self,  # keep track of the current object for backwards compatibility
        )

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Ensure that setting an attribute on a legacy-style settings keeps track of
        the attribute.
        """
        super().__setattr__(name, value)
        if not name.startswith("_") and name not in Settings._ensure_dataclass_keys(self):
            Settings._ensure_legacy_keys(self).add(name)

    def _ensure_parent(self) -> ContextVar[Self]:
        """
        Get the parent object.

        Legacy-style settings objects are not inherited from `Settings`,
        thus we need to ensure the attribute exists.
        """
        try:
            return self.__parent__
        except AttributeError:
            self.__parent__ = ContextVar("pkgsettings.Settings.__parent__")
            return self.__parent__

    def _ensure_legacy_keys(self) -> Set[str]:
        """Ensure that `__legacy_keys__` exists on the old-style settings object."""
        try:
            legacy_keys = self.__legacy_keys__
        except AttributeError:
            legacy_keys = self.__legacy_keys__ = set()
        return legacy_keys

    def _ensure_dataclass_keys(self) -> Set[str]:
        """Ensure that `__dataclass_keys__` exists on the old-style settings object."""
        try:
            dataclass_keys = self.__dataclass_keys__
        except AttributeError:
            dataclass_keys = self.__dataclass_keys__ = {field.name for field in fields(self)}
        return dataclass_keys

    def _get_grandparent(self) -> Self:
        """Return the grandparent, that is the topmost settings layer."""
        try:
            parent = Settings._ensure_parent(self).get()
        except LookupError:
            # No parent, so the argument IS the grandparent.
            return self
        else:
            return Settings._get_grandparent(parent)


_SettingsT = TypeVar("_SettingsT", bound=Settings)


@dataclass
class _ContextManager(Generic[_SettingsT], ContextManager[_SettingsT]):
    """Manager of an override layer."""

    parent: Any
    """The temporary override layer."""

    child: Any
    """The child, to which the temporary layer will be attached to."""

    grandchild: _SettingsT
    """
    The grandchild to return from the `__enter__`.

    This is only to provide the user the original `settings` object from the context manager
    to keep the backwards compatibility.
    """

    restore_token: Token = field(init=False)
    """Track of a possibly overridden parent."""

    __slots__ = ("parent", "child", "grandchild")

    def __enter__(self) -> _SettingsT:
        self.restore_token = Settings._ensure_parent(self.child).set(self.parent)
        return self.grandchild

    def __exit__(
        self,
        __exc_type: Optional[Type[BaseException]],
        __exc_val: Optional[BaseException],
        __exc_tb: Optional[TracebackType],
    ) -> None:
        self.child.__parent__.reset(self.restore_token)

    def __call__(self, wrapped: Callable[_P, _R]) -> Callable[_P, _R]:
        """Decorate the function to be called with the provided overridden settings."""

        @wraps(wrapped)
        def wrapper(*args, **kwargs):
            with self:
                return wrapped(*args, **kwargs)

        return wrapper


class PrefixedSettings(object):
    def __init__(self, settings, prefix=None):
        self.settings = settings
        self.prefix = prefix

    def __getattr__(self, attr):
        if self.prefix:
            attr = self.prefix + attr
        return getattr(self.settings, attr)

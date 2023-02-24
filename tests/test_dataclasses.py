from dataclasses import dataclass

from pytest import fail, raises, warns

from pkgsettings import DuplicateConfigureWarning, PrefixedSettings, Settings


def test_default_settings():
    @dataclass
    class MySettings(Settings):
        debug = False

    assert not MySettings().debug


def test_context_manager():
    @dataclass
    class MySettings(Settings):
        debug: bool = False
        enabled: bool = False

    settings = MySettings()
    settings.enabled = True

    with settings(debug=True):
        assert settings.debug
        assert settings.enabled

    assert not settings.debug


def test_decorator():
    @dataclass
    class MySettings(Settings):
        debug: bool = False

    settings = MySettings()

    @settings(debug=True)
    def go():
        assert settings.debug

    go()
    assert not settings.debug


def test_decorator_in_class():
    @dataclass
    class MySettings(Settings):
        debug: bool = False

    settings = MySettings()

    class Dummy:
        @settings(debug=True)
        def go(self):
            assert settings.debug

    Dummy().go()
    assert not settings.debug


def test_as_dict():
    @dataclass
    class MySettings(Settings):
        debug: bool = False

    settings = MySettings()

    with settings(debug=True):
        assert settings.as_dict() == {"debug": True}

    assert settings.as_dict() == {"debug": False}


def test_with_object():
    @dataclass
    class MySettings(Settings):
        foo: int = 1

    class OtherSettings:
        def __init__(self):
            self.foo = 2

    settings = MySettings()
    settings.configure(OtherSettings())

    assert settings.foo == 2

    with settings(foo=3):
        assert settings.foo == 3


def test_key_not_found():
    @dataclass
    class MySettings(Settings):
        pass

    with raises(AttributeError):
        getattr(MySettings(), "debug")


def test_warning_when_adding_self():
    @dataclass
    class MySettings(Settings):
        pass

    settings = MySettings()
    with warns(DuplicateConfigureWarning):
        settings.configure(settings)


def test_warning_when_adding_duplicate():
    @dataclass
    class MySettings(Settings):
        pass

    settings_1 = MySettings()
    settings_1.configure()

    settings_2 = MySettings()
    settings_2.configure(settings_1)

    with warns(DuplicateConfigureWarning):
        settings_1.configure(settings_2)


def test_prefixed_no_prefix():
    @dataclass
    class MySettings(Settings):
        a: int = 1
        b: str = "2"

    settings = PrefixedSettings(MySettings())
    assert settings.a == 1
    assert settings.b == "2"


def test_prefixed_with_prefix():
    @dataclass
    class MySettings(Settings):
        MY_a: int = 1
        OTHER_a: int = 2
        a: int = 3
        c: int = 5
        MY_b: str = "2"

    settings = PrefixedSettings(MySettings(), "MY_")

    assert settings.a == 1
    assert settings.b == "2"

    with raises(AttributeError):
        a = settings.c
        fail(a)

    with raises(AttributeError):
        a = settings.MY_a
        fail(a)

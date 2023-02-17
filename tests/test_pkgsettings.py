from pytest import fail, raises, warns

from pkgsettings import DuplicateConfigureWarning, PrefixedSettings, Settings


def test_default_settings():
    settings = Settings()
    settings.configure(debug=False)
    assert not settings.debug


def test_context_manager():
    settings = Settings()
    settings.configure(debug=False)

    with settings(debug=True):
        assert settings.debug
    assert not settings.debug


def test_decorator():
    settings = Settings()
    settings.configure(debug=False)

    @settings(debug=True)
    def go():
        assert settings.debug

    go()
    assert not settings.debug


def test_decorator_in_class():
    settings = Settings()
    settings.configure(debug=False)

    class Dummy(object):
        @settings(debug=True)
        def go(self):
            assert settings.debug

    Dummy().go()
    assert not settings.debug


def test_as_dict():
    settings = Settings()
    settings.configure(debug=False)

    with settings(debug=True):
        assert settings.as_dict() == {"debug": True}

    assert settings.as_dict() == {"debug": False}


def test_with_object():
    class MySettings:
        def __init__(self):
            self.debug = False

    settings = Settings()
    settings.configure(MySettings())

    assert not settings.debug

    with settings(debug=True):
        assert settings.debug


def test_key_not_found():
    settings = Settings()
    settings.configure()

    with raises(AttributeError):
        getattr(settings, "debug")


def test_warning_when_adding_self():
    settings = Settings()
    settings.configure()

    with warns(DuplicateConfigureWarning):
        settings.configure(settings)


def test_warning_when_adding_duplicate():
    settings = Settings()
    settings.configure()

    settings2 = Settings()
    settings2.configure(settings)

    with warns(DuplicateConfigureWarning):
        settings.configure(settings2)


def test_prefixed_no_prefix():
    ss = Settings()
    ss.configure(a=1, b="2")
    settings = PrefixedSettings(ss)
    assert settings.a == 1
    assert settings.b == "2"


def test_prefixed_with_prefix():
    ss = Settings()
    ss.configure(MY_a=1, OTHER_a=2, a=3, c=5, MY_b="2")
    settings = PrefixedSettings(ss, "MY_")

    assert settings.a == 1
    assert settings.b == "2"

    with raises(AttributeError):
        a = settings.c
        fail(a)

    with raises(AttributeError):
        a = settings.MY_a
        fail(a)

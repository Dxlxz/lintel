"""Tests for the `lintel.hub` back-compat namespace shim (WS-G.3).

After a validator is installed as a public `lintel-<name>` package
(importable as `lintel_ai.<name>`), `from lintel.hub import X` must keep
working by falling back to scanning the `lintel_ai.*` namespace, while
emitting a one-time DeprecationWarning.
"""

import sys
import warnings

import pytest

import lintel.hub as hub_module


@pytest.fixture
def fake_namespace_package(tmp_path, monkeypatch):
    """Create an installed `lintel_ai.faketest` namespace package on disk."""
    ns_dir = tmp_path / "lintel_ai" / "faketest"
    ns_dir.mkdir(parents=True)
    # PEP 420 namespace: no lintel_ai/__init__.py
    (ns_dir / "__init__.py").write_text("class FakeValidator:\n    pass\n")
    monkeypatch.syspath_prepend(str(tmp_path))

    # Ensure a clean import + reset the shim's caches/flags.
    for mod in list(sys.modules):
        if mod == "lintel_ai" or mod.startswith("lintel_ai."):
            del sys.modules[mod]
    hub_module._export_map_cache = None
    hub_module._namespace_deprecation_warned = False

    yield

    for mod in list(sys.modules):
        if mod == "lintel_ai" or mod.startswith("lintel_ai."):
            del sys.modules[mod]
    hub_module._export_map_cache = None
    hub_module._namespace_deprecation_warned = False


def test_shim_resolves_from_lintel_ai_namespace(fake_namespace_package):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        resolved = hub_module.__getattr__("FakeValidator")

    assert resolved.__name__ == "FakeValidator"
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_shim_unknown_export_raises_attribute_error(fake_namespace_package):
    with pytest.raises(AttributeError):
        hub_module.__getattr__("DoesNotExistValidator")


def test_shim_returns_none_without_namespace(monkeypatch):
    """If no lintel_ai namespace is installed, lookups raise AttributeError."""
    for mod in list(sys.modules):
        if mod == "lintel_ai" or mod.startswith("lintel_ai."):
            del sys.modules[mod]
    monkeypatch.setitem(sys.modules, "lintel_ai", None)
    hub_module._export_map_cache = None
    with pytest.raises(AttributeError):
        hub_module.__getattr__("AnythingAtAll")

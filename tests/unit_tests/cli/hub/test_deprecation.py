import pytest

from lintel.cli.hub.deprecation import (
    pip_name_for_uri,
    warn_hub_cli_deprecated,
)


@pytest.mark.parametrize(
    ("uri", "expected"),
    [
        ("hub://lintel/detect_pii", "lintel-detect-pii"),
        ("hub://lintel/regex_match", "lintel-regex-match"),
        # cross-namespace hub ids still translate to the lintel-* dist
        ("hub://cartesia/mentions_drugs", "lintel-mentions-drugs"),
    ],
)
def test_pip_name_for_uri(uri, expected):
    assert pip_name_for_uri(uri) == expected


def test_pip_name_for_uri_invalid_returns_none():
    assert pip_name_for_uri("not-a-hub-uri") is None


def test_warn_hub_cli_deprecated_emits_deprecation_warning():
    with pytest.warns(DeprecationWarning, match="deprecated"):
        warn_hub_cli_deprecated(pip_hint="pip install lintel-detect-pii")


def test_install_cli_emits_deprecation_and_translates_to_pip(mocker):
    """`guardrails hub install` warns and points at the public pip command."""
    mock_install_multiple = mocker.patch("lintel.hub.install.install_multiple")
    mocker.patch("lintel.cli.hub.install.version_warnings_if_applicable")
    mock_warn = mocker.patch("lintel.cli.hub.deprecation.warn_hub_cli_deprecated")

    from lintel.cli.hub.install import install_cli

    install_cli(
        ["hub://lintel/detect_pii"],
        local_models=False,
        quiet=True,
        upgrade=False,
    )

    # The deprecation warning fired with the translated pip command.
    assert mock_warn.call_count == 1
    _, kwargs = mock_warn.call_args
    assert kwargs["pip_hint"] == "pip install lintel-detect-pii"
    # Install still proceeds (now from public PyPI).
    mock_install_multiple.assert_called_once()

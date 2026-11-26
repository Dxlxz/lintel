from unittest.mock import mock_open, call

import pytest

from guardrails_hub_types import Manifest
from lintel.cli.hub.uninstall import remove_from_hub_inits

manifest_mock = Manifest.from_dict(
    {
        "id": "lintel/test_package",
        "name": "test_module",
        "author": {"name": "Author Name", "email": "author@example.com"},
        "maintainers": [{"name": "Maintainer Name", "email": "maintainer@example.com"}],
        "repository": {"url": "https://github.com/example/repo"},
        "packageName": "test_package",
        "moduleName": "test_module",
        "namespace": "lintel",
        "description": "Test module",
        "exports": ["Validator", "Helper"],
    }
)


def test_remove_from_hub_inits(mocker):
    mock_remove_line = mocker.patch("lintel.cli.hub.uninstall.remove_line")

    remove_from_hub_inits(manifest_mock, "/site-packages")

    expected_calls = [
        call(
            "/site-packages/lintel/hub/__init__.py",
            "from lintel_ai.test_package import Validator, Helper",
        ),
    ]

    mock_remove_line.assert_has_calls(expected_calls, any_order=True)


def test_uninstall_invalid_uri(mocker):
    with pytest.raises(SystemExit):
        mock_logger_error = mocker.patch("lintel.cli.hub.uninstall.logger.error")
        mocker.patch(
            "lintel.cli.hub.uninstall.get_validator_manifest",
            return_value=manifest_mock,
        )
        mocker.patch(
            "lintel.cli.hub.utils.pip_process",
            return_value={"Location": "/fake/site-packages"},
        )

        m_open = mock_open(read_data="import something")
        mocker.patch("builtins.open", m_open)
        mocker.patch("os.path.exists", return_value=True)

        mocker.patch("subprocess.check_call")
        from lintel.cli.hub.uninstall import uninstall

        uninstall("not a hub uri")

        mock_logger_error.assert_called_once_with("Invalid URI!")

        m_open.assert_called()

        mock_subprocess_check_call = mocker.patch("subprocess.check_call")
        mock_subprocess_check_call.assert_not_called()


def test_uninstall_valid_uri(mocker):
    mocker.patch(
        "lintel.cli.hub.uninstall.get_validator_manifest",
        return_value=manifest_mock,
    )

    mock_uninstall_hub_module = mocker.patch(
        "lintel.cli.hub.uninstall.uninstall_hub_module"
    )
    mocker.patch("lintel.cli.hub.uninstall.console")

    mock_unregister = mocker.patch(
        "lintel.hub.validator_package_service.ValidatorPackageService.unregister_validator"
    )

    from lintel.cli.hub.uninstall import uninstall

    uninstall("hub://lintel/test-validator")

    mock_uninstall_hub_module.assert_called_once_with(manifest_mock)
    mock_unregister.assert_called_once_with("lintel/test-validator")


def test_uninstall_hub_module(mocker):
    mock_pip_process = mocker.patch("lintel.cli.hub.uninstall.pip_process")
    from lintel.cli.hub.uninstall import uninstall_hub_module

    uninstall_hub_module(manifest_mock)

    mock_pip_process.assert_called_once_with(
        "uninstall", "lintel-test-package", flags=["-y"], quiet=True
    )

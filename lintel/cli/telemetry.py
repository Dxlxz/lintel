import platform
from lintel.settings import settings
from lintel.utils.hub_telemetry_utils import HubTelemetry
from lintel.version import LINTEL_VERSION


def trace_if_enabled(command_name: str):
    if settings.rc.enable_metrics is True:
        telemetry = HubTelemetry()
        telemetry._enabled = True
        telemetry.create_new_span(
            f"guardrails-cli/{command_name}",
            [
                ("guardrails-version", LINTEL_VERSION),
                ("python-version", platform.python_version()),
                ("system", platform.system()),
                ("platform", platform.platform()),
                ("arch", platform.architecture()[0]),
                ("machine", platform.machine()),
                ("processor", platform.processor()),
            ],
        )

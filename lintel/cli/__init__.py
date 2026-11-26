import lintel.cli.configure  # noqa
import lintel.cli.start  # noqa
import lintel.cli.validate  # noqa
from lintel.cli.create import create_command  # noqa: F401
from lintel.cli.main import cli as cli
from lintel.cli.hub import hub_command
from lintel.cli.watch import watch_command  # noqa: F401
from lintel.cli.db import db_command


cli.add_typer(
    hub_command, name="hub", help="Manage validators installed from the Lintel Hub."
)

cli.add_typer(db_command, name="db", help="Manage database migrations.")


if __name__ == "__main__":
    cli()

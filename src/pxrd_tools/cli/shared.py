"""
CLI utility functions
"""
# --- Imports

# Standard library
import logging

# External packages
from rich import print
import typer


# --- Constants

LOG_RECORD_FORMAT = "[%(asctime)s]:[%(name)s]:%(message)s"

LOGGER = logging.getLogger("cli")


# --- CLI arguments and options

DATA_FILE_ARG = typer.Argument(
    ...,
    help=(
        "PXRD data file. "
        "The data file is expected to specify a 'count' value for each '2-theta' value."
    ),
)

DEFAULT_QUIET_OPTION = False
QUIET_OPTION = typer.Option("--quiet", "-q", help="Display fewer status messages.")

DEFAULT_LOG_FILE = "pxrd-tools.log"
LOG_FILE_OPTION = typer.Option(
    "--log-file", help=f"Log file. Default: {DEFAULT_LOG_FILE}"
)


# --- Utility functions


def emit_status_message(message: str, quiet: bool = False) -> None:
    """
    Emit status message to appropriate streams.

    Parameters
    ----------
    message: status message

    quiet: set to True if console output should be suppressed; set to False
           otherwise
    """
    LOGGER.info(message)
    if not quiet:
        print(message)

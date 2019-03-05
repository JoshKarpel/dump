import logging
import random
import sys
import os

import click
from halo import Halo
from spinners import Spinners

from . import dump, exceptions

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


SPINNERS = list(name for name in Spinners.__members__ if name.startswith("dots"))


def make_spinner(*args, **kwargs):
    return Halo(*args, spinner=random.choice(SPINNERS), stream=sys.stderr, **kwargs)


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command()
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, resolve_path=True, readable=True
    ),
)
@click.option("--auth", default=None)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Show log messages as the CLI runs.",
)
def cli(files, auth, verbose):
    """Dump command line tool."""
    if verbose:
        _start_logger()
    logger.debug(f'Dump called with arguments "{" ".join(sys.argv[1:])}"')

    auth_token = auth or os.getenv("DROP_AUTH", None)
    if auth_token is None:
        raise exceptions.MissingAuthorization("No auth token provided")

    dbx = dump.get_dropbox(auth_token)
    for path in files:
        dump.upload_file(dbx, path)


def _start_logger():
    """Initialize a basic logger for Dump's CLI."""
    dump_logger = logging.getLogger("dump")
    dump_logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )

    dump_logger.addHandler(handler)

    return handler

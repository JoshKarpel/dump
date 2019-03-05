import logging
import random
import sys
import os
import traceback

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

PREFIX = "\n  "


@click.command()
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, resolve_path=True, readable=True
    ),
)
@click.option(
    "--auth",
    default=None,
    help="Your Dropbox authorization token. Preferred: set environment variable DROP_AUTH",
)
@click.option(
    "--soft",
    is_flag=True,
    default=False,
    help="If passed, continue uploading other files if an upload fails.",
)
@click.option(
    "--report",
    is_flag=True,
    default=False,
    help="If passed, print a plain-text report when done.",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Show log messages as the CLI runs.",
)
def cli(files, auth, soft, report, verbose):
    """Dump command line tool."""
    successes = []
    fails = []

    if verbose:
        _start_logger()
    logger.debug(f'Dump called with arguments "{" ".join(sys.argv[1:])}"')

    auth_token = auth or os.getenv("DROP_AUTH", None)
    if auth_token is None:
        raise exceptions.MissingAuthorization("No auth token provided")

    dbx = dump.get_dropbox(auth_token)

    for path in files:
        with make_spinner(text=f"Uploading {path}") as spinner:
            try:
                for curr, total in dump.upload_file(dbx, path):
                    spinner.text = f"[{curr}/{total}] Uploading {path}"
                spinner.succeed(f"[{total}/{total}] Uploaded {path}")
                successes.append(path)
            except Exception as e:
                spinner.fail(
                    f"Upload for {path} failed:\n{''.join(traceback.format_exception_only(e.__class__, e))}"
                )
                fails.append(path)
                if not soft:
                    click.echo(f"ERR: file upload failed for {path}, aborting")
                    sys.exit(1)

    if report:
        if len(successes) > 0:
            msg = PREFIX + PREFIX.join(successes)
            click.echo(f"Uploaded:{msg}")
        if len(fails) > 0:
            msg = PREFIX + PREFIX.join(fails)
            click.echo(f"Failed to upload:{msg}")


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

import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).parent.parent))

from envman.cli import cli

cli()

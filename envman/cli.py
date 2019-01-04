from pathlib import Path

import click

from .utils import get_env, start_env, list_environs, remove_env, scan_for_file_upwards
from . import db, config

pass_dir = click.make_pass_decorator(Path)


def get_directory(directory=None):
    if directory is None:
        f = scan_for_file_upwards(Path.cwd(), '.envman_default_dir_loc')
        directory = f.read_text().strip() if f is not None else None
    default_directory = (Path.home() / '.envman').resolve()
    return directory if directory is not None else default_directory


@click.group()
@click.option('-d', '--directory', default=None,
              type=click.Path(file_okay=False, writable=True, resolve_path=True),
              required=False, envvar='ENVMAN_DIRECTORY')
@click.pass_context
def cli(ctx, directory):
    directory = get_directory(directory)
    # print(directory)
    ctx.obj = Path(directory).resolve()


@cli.command()
@click.argument('name')
@click.option('-p', '--parent', default=None)
# @click.option('-r/ ', '--relative/--at-root')  # Handle later? Is this even a good idea?
@pass_dir
def create(dir, name, parent):
    # print(dir, name, parent)
    db.Environment.create(name=name, env_root=str(dir), parent=get_env(parent, dir) if parent is not None else None)


@cli.command()
@click.argument('name')
@pass_dir
def start(dir, name):
    start_env(get_env(name, str(dir)))


@cli.command()
@click.argument('name')
@pass_dir
def dir_of(dir, name):
    click.echo(get_env(name, str(dir)).path)


@cli.command()
@click.argument('name')
@pass_dir
def edit(dir, name):
    click.edit(filename=Path(get_env(name, str(dir)).path) / config.startup_file)


@cli.command()
@pass_dir
def list_envs(dir):
    click.echo('Available Environments:')
    for env in list_environs(str(dir)):
        click.echo(env)


@cli.command()
@click.argument('name')
@pass_dir
def rm(dir, name):
    remove_env(str(dir), name)


@cli.command()
@click.option('-l', '--loc', help='Where to save the directory\'s location. Set this to the root directory of the tree '
                                  'you will be working with', type=click.Path(True, False, True, True, True, True),
              default='.')
@pass_dir
def local_dir(dir, loc):
    loc = Path(loc)
    with (loc / '.envman_default_dir_loc').open('w') as f:
        f.write(str(dir))


@cli.command()
@click.argument('dir', default=None)
def dir(directory):
    if directory is None:
        return click.echo(get_directory())
    loc = Path.home()
    with (loc / '.envman_default_dir_loc').open('w') as f:
        f.write(str(dir))

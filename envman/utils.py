import os
import shutil
from pathlib import Path
import sh

from . import config
from . import db

BOX_DRAWING_CHARS = dict(END_LIST='└─ ', MID_LIST_ENTRY='├─ ', MID_LIST_NON_ENTRY='│')


def init_environment_root(env):
    path = Path(env.env_root).resolve()
    # print('INIT ENV_ROOT: %s' % path)
    path.mkdir(parents=True, exist_ok=True)
    global_startup = (path / config.startup_file).resolve()
    if not global_startup.exists():
        with global_startup.open('w') as f:
            f.write(config.global_startup_content)
    (path / config.envs_dir).resolve().mkdir(parents=True, exist_ok=True)
    from . import db
    db.setup(env.env_root)
    db.Base.metadata.create_all()


def create_environment(env):
    path = Path(env.path).resolve()
    sess = db.Session.object_session(env) or db.Session()
    try:
        path.mkdir(parents=True)
        with (path / config.startup_file).open('w') as startup:
            startup.write(config.startup_content.format(**env._todict()))
        sess.add(env)
        sess.commit()
    except BaseException:
        sess.rollback()
        shutil.rmtree(str(path))
        raise


def assemble_exports(environ):
    template = "export {key}='{value}'"
    exports = (template.format(key=key, value=value)
               for key, value in environ.items()
               if 'BASH_FUNC' not in key and '%' not in key)
    return '; '.join(exports)


def get_all_envs(env):
    yield env
    if env.parent is not None:
        yield from get_all_envs(env.parent)


def assemble_setups(base_env):
    env_start = (f'source {str((Path(env.path) / config.startup_file).resolve())}'
                 for env in reversed(list(get_all_envs(base_env))))
    main = str((Path(base_env.env_root) / config.startup_file).resolve())
    return f'source {main}; {"; ".join(env_start)}'


def start_env(env):
    envs = assemble_exports(os.environ)
    setups = assemble_setups(env)
    # print(setups)
    command = f'export ENV={env.name}; export ENV_PATH={env.path}; {envs}; {setups}; bash --norc -i'
    # print('EXECUTING: %s' % command)
    sh.bash(c=command, _fg=True)


def get_env(name, dir):
    db.setup(dir)
    sess = db.Session()
    return sess.query(db.Environment).filter_by(name=name).first()


def recursive_yield_children(all, padding='', ident=2):
    padding += ' ' * ident
    for i, val in enumerate(all):
        is_last = i + 1 == len(all)
        last_char = BOX_DRAWING_CHARS['END_LIST' if is_last else 'MID_LIST_ENTRY']
        yield padding + last_char + val.name
        yield from recursive_yield_children(val.children,
                                            padding + (BOX_DRAWING_CHARS['MID_LIST_NON_ENTRY'] if not is_last else ' '))


def list_environs(dir):
    db.setup(dir)
    envs = db.Session().query(db.Environment).filter_by(parent=None).all()
    return recursive_yield_children(envs)


def remove_env(dir, env_name):
    db.setup(dir)
    env = get_env(env_name, dir)
    shutil.rmtree(str(Path(env.path).resolve()))
    sess = db.Session()
    sess.delete(env)
    sess.commit()


def scan_for_file_upwards(path: Path, filename):
    path = path.resolve()
    if (path / filename).resolve().exists():
        return (path / filename).resolve()
    if path.parent is path:
        return
    return scan_for_file_upwards(path.parent, filename)

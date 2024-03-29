import os
from pathlib import Path

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative.base import _declarative_constructor  # noinspection: protected-member
from sqlalchemy.orm import sessionmaker, relationship, relation

from . import config


def setup(dir=None):
    global engine
    db_engine = None if dir is None else config.db_uri.format(dir)
    engine = create_engine(db_engine)
    Session.configure(bind=engine)
    Base.metadata.bind = engine


Session = sessionmaker()
Base = declarative_base()
Base.__init__ = _declarative_constructor


class Environment(Base):
    def __repr__(self):
        # print(self.name)
        return f'Environment({repr(self.parent)})<{self.path}><{self.name}>'

    __tablename__ = 'environments'

    id = Column(Integer, primary_key=True)

    name = Column(String, unique=True)
    path = Column(String, unique=True)
    env_root = Column(String)
    parent_id = Column(Integer, ForeignKey('environments.id'))
    # parent = relationship(lambda: Environment, primaryjoin='Environment.parent_id==Environment.id',
    #                       remote_side=id, back_populates='children')
    # children = relationship(lambda: Environment, primaryjoin='Environment.id==Environment.parent_id',
    #                         remote_side=parent_id, back_populates='parent')
    # startup_file = Column(String)
    parent = relation('Environment', remote_side=[id], backref='children')

    @classmethod
    def create(cls, *, name, env_root, parent=None):
        location = os.path.join(env_root, config.envs_dir)
        name = '.'.join([parent.name, name.replace('.', '-')]) if parent is not None else name.replace('.', '-')
        # print(name)
        env = Environment(name=name, path=os.path.join(location, name), env_root=env_root, parent=parent)
        # print(repr(env))
        from envman.utils import init_environment_root
        init_environment_root(env)
        # if session is not None:
        #     session.add(env)
        #     session.commit()
        from envman.utils import create_environment
        create_environment(env)
        return env

    def _todict(self):
        # print(self.parent, self.children)
        return dict(name=self.name, path=Path(self.path), env_root=self.env_root,)
        # parent=self.parent._todict() if self.parent is not None else None,
        # children=[x._todict() for x in self.children])

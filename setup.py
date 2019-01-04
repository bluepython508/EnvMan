from setuptools import setup

setup(
        name='EnvManager',
        version='0.0.1',
        packages=['envman'],
        url='',
        license='MIT',
        author='ben',
        author_email='',
        description='A simple environment manager',
        install_requires=['click', 'sqlalchemy', 'sh'],
        entry_points='''
            [console_scripts]
            envman=envman.cli:cli
        '''
)

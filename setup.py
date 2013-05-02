# from distutils.core import setup
from distutils.core import Command
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(
    name='pyscm',
    version='r1',
    # packages=['pyscm'],
    packages=find_packages("src"), 
    package_dir = {'': 'src'},
    test_suite="pyscm.tests",
    tests_require=['pytest'],
    cmdclass = {'test': PyTest},
)

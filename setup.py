from setuptools import setup

setup(name='turbocase',
      version='1.4.2',
      description='Generate an OpenSCAD case template from a KiCAD PCB',
      url='https://git.sr.ht/~martijnbraam/turbocase',
      author='Martijn Braam',
      author_email='martijn@brixit.nl',
      packages=['turbocase', 'turbocase.parts'],
      install_requires=['sexpdata'],
      entry_points={
          'console_scripts': ['turbocase=turbocase.__main__:main'],
      })

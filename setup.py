from setuptools import setup

setup(name='turbocase',
      version='1.8.0',
      description='Generate an OpenSCAD case template from a KiCAD PCB',
      url='https://turbocase.org',
      author='Martijn Braam',
      author_email='martijn@brixit.nl',
      packages=['turbocase', 'turbocase.parts'],
      install_requires=['sexpdata'],
      project_urls={
          'Source': 'https://git.sr.ht/~martijnbraam/turbocase',
          'Tracker': 'https://todo.sr.ht/~martijnbraam/turbocase',
      },
      entry_points={
          'console_scripts': ['turbocase=turbocase.__main__:main'],
      })

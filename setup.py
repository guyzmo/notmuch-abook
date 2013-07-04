from setuptools import setup, find_packages
import os

def read(*names):
    values = dict()
    for name in names:
        if os.path.isfile(name):
            value = open(name).read()
        else:
            value = ''
        values[name] = value
    return values

long_description="""
Notmuch Addressbook Utility

%(README)s

""" % read('README')

setup(name='notmuch_abook',
      version="v1.0",
      description="Notmuch addressbook",
      long_description=long_description,
      classifiers=["Development Status :: 4 - Beta",
                   "Environment :: Console",
                   "License :: Freely Distributable",
                   "Topic :: Communications :: Email :: Address Book"], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='notmuch addressbook vim',
      author='Bernard `Guyzmo` Pratz',
      author_email='guyzmo+notmuch@m0g.net',
      url='https://github.com/guyzmo/notmuch-abook/',
      license='WTFPL',
      package_dir={'notmuch_abook': 'pylibs'},
      data_files=[('plugin', ['plugin/notmuch_abook.vim'])],
      packages=['notmuch_abook'], #find_packages(exclude=['plugin']),
      include_package_data=True,
      namespace_packages = [],
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "pysqlite",
          "docopt"
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      notmuch_abook = notmuch_abook.notmuch_abook:run
      """,
      )

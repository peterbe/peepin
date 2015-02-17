import sys
from os import path
from setuptools import setup

_here = path.dirname(__file__)

# Prevent spurious errors during `python setup.py test`, a la
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html:
try:
    import multiprocessing
    multiprocessing = multiprocessing  # shut up pyflakes
except ImportError:
    pass

install_requires = ['peep']

if sys.version_info >= (2, 6) and sys.version_info <= (2, 7):
    # Python 2.6 is the oldest version we support and it
    # needs some extra stuff
    install_requires.append('argparse')


setup(
    name='peepin',
    version='0.10',
    description='Edits your requirements.txt by peep-hashing them',
    long_description=open(path.join(_here, 'README.rst')).read(),
    author='Peter Bengtsson',
    author_email='mail@peterbe.com',
    license='MIT',
    py_modules=['peepin'],
    entry_points={
        'console_scripts': ['peepin = peepin:main']
        },
    url='https://github.com/peterbe/peepin',
    include_package_data=True,
    install_requires=install_requires,
    tests_require=['nose>=1.3.0,<2.0', 'httpretty'],
    test_suite='nose.collector',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Systems Administration'
        ],
    keywords=['pip', 'peep', 'repeatable', 'deploy', 'deployment', 'hash',
              'install', 'installer']
)

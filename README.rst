======
Peepin
======

.. image:: https://travis-ci.org/peterbe/peepin.svg?branch=master
    :target: https://travis-ci.org/peterbe/peepin

This tool makes it easier to update your strict "peep-ready"
``requirements.txt`` file.

If you want to add a package or edit the version of one you're currently
using you have to do the following steps:

1. Go to pypi for that package
2. Download the .tgz file
3. Possibly download the .whl file
4. Run `peep hash downloadedpackage-1.2.3.tgz`
5. Run `peep hash downloadedpackage-1.2.3.whl`
6. Edit requirements.txt

This script does all those things.
Hackishly wonderfully so.

A Word of Warning!
==================

The whole point of peep is that you vet the packages that you use
on your laptop and that they haven't been tampered with. Then you
can confidently install them on a server.

This tool downloads from PyPI (over HTTPS) and runs ``peep hash``
on the downloaded files.

You still need to check that the packages that are downloaded
are sane.

You might not have time to go through the lines one by one
but you should be aware that the vetting process is your
responsibility.

Installation
============

This is something you only do or ever need in a development
environment. Ie. your laptop::

    pip install peepin

How to use it
=============

Suppose you want to install ``futures``. You can either do this::

    peepin futures

Which will download the latest version tarball (and wheel) and
calculate their peep hash and edit your ``requirements.txt`` file.

Or you can be specific about exactly which version you want::

    peepin "futures==2.1.3"

Suppose you don't have a ``requirements.txt`` right there in the same
directory you can do this::

    peepin "futures==2.1.3" stuff/requirementst/prod.txt

If there's not output. It worked. Check how it edited your
requirements files.

Runnings tests
==============

Simply run:

    python setup.py test


Ode to Erik Rose
================

Just in case you didn't know;
`peep <https://github.com/erikrose/peep>`_ is awesome.
It makes it possible to confidently leave
third-party packages to be installed on the server without needing to
be checked into some sort of "vendor" directory.

Having said that, if you don't care about security or repeatability.
Then Erik is just a dude with a goatee.

Version History
===============

0.8
  * Avoid editing the requirements file if no packages are found, fixed #3

0.7
  * Ability to download binary URLs

0.6
  * Works in python 2.6, 2.7, 3.3 and 3.4

0.5
  * Fix for multi-version packages like Django

0.4
  * Be verbose about downloaded files

0.3
  * Regression

0.2
  * --verbose option

0.1
  * Works

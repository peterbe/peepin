#!/usr/bin/env python
"""
See README :)
"""

import re
import urllib
import tempfile
import os
import sys

import peep


def _download(url):
    return urllib.urlopen(url).read()


def run(spec, file):
    if '==' in spec:
        package, version = spec.split('==')
    else:
        assert '>' not in spec and '<' not in spec
        package, version = spec, None
        # then the latest version is in the breadcrumb
        version = get_latest_version(package)
        assert version
    hashes = get_hashes(package, version)

    requirements = open(file).read()

    def new_lines():
        out = ''
        for h in hashes:
            out += '# sha256: %s\n' % h
        out += '%s==%s\n' % (package, version)
        return out

    # if the package wasn't already there, add it to the bottom
    if '%s==' % package not in requirements:
        # easy peasy
        requirements = requirements.strip() + '\n'
        requirements += new_lines()
    else:
        # need to replace the existing
        prev = []
        for line in requirements.splitlines():
            if '%s==' % package in line:
                prev.append(line)
                combined = '\n'.join(prev + [''])
                requirements = requirements.replace(combined, new_lines())
                break
            elif '==' in line:
                prev = []
            else:
                prev.append(line)

    open(file, 'w').write(requirements)

    return 0


def get_latest_version(package):
    url = 'https://pypi.python.org/pypi/%s' % package
    content = _download(url)
    content = content.split('id="breadcrumb"')[1].split('</div>')[0]
    return re.findall('"/pypi/%s/(.*)"' % package, content)[0]


def get_hashes(package, version):

    url = 'https://pypi.python.org/pypi/%s' % package
    if version:
        url += '/%s' % version

    content = _download(url)
    finds = re.findall('href="((.*)#md5=\w+)"', content)

    for found in finds:
        url = found[0]
        download_dir = tempfile.gettempdir()
        filename = os.path.join(
            download_dir,
            os.path.basename(url.split('#')[0])
        )
        if not os.path.isfile(filename):
            with open(filename, 'wb') as f:
                f.write(urllib.urlopen(url).read())
        yield peep.hash_of_file(filename)


def main():
    def grr():
        print (
            'USAGE: %s "some-package==1.2.3" [/path/to/requirements.txt]'
            % __file__
        )
        sys.exit(1)

    args = sys.argv[1:]
    if not args:
        grr()
    spec = args[0]
    if len(args) > 1:
        requirements_file = args[1]
    else:
        requirements_file = 'requirements.txt'

    return run(spec, requirements_file)

if __name__ == '__main__':
    sys.exit(main())

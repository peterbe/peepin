#!/usr/bin/env python
"""
See README :)
"""

from __future__ import print_function
import re
import urllib
import tempfile
import os
import sys

import peep


def _verbose(*args):
    print('* ' + ' '.join(args))


def _download(url):
    return urllib.urlopen(url).read()


def run(spec, file, verbose=False):
    if '==' in spec:
        package, version = spec.split('==')
    else:
        assert '>' not in spec and '<' not in spec
        package, version = spec, None
        # then the latest version is in the breadcrumb
        version = get_latest_version(package)
        assert version
        if verbose:
            _verbose("Latest version for", version)
    hashes = get_hashes(package, version, verbose=verbose)

    if verbose:
        _verbose("Editing", file)
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

    breadcrumb_content = content.split('id="breadcrumb"')[1].split('</div>')[0]

    def extract_version(html):
        return re.findall(
            '"/pypi/%s/(.*)"' % re.escape(package), html, re.I
        )[0]
    try:
        return extract_version(breadcrumb_content)
    except IndexError:
        assert '<h1>Index of Packages</h1>' in content
        table_content = content.split('<h1>Index of Packages</h1>')[1]
        return extract_version(table_content)


def get_hashes(package, version, verbose=False):

    url = 'https://pypi.python.org/pypi/%s' % package
    if version:
        url += '/%s' % version

    content = _download(url)
    finds = re.findall('href="((.*)#md5=\w+)"', content)

    for found in finds:
        url = found[0]
        if verbose:
            _verbose("Found URL", url)
        download_dir = tempfile.gettempdir()
        filename = os.path.join(
            download_dir,
            os.path.basename(url.split('#')[0])
        )
        if not os.path.isfile(filename):
            if verbose:
                _verbose("  Downloaded to", filename)
            with open(filename, 'wb') as f:
                f.write(urllib.urlopen(url).read())
        elif verbose:
            _verbose("  Re-using", filename)
        hash_ = peep.hash_of_file(filename)
        if verbose:
            _verbose("  Hash", hash_)
        yield hash_


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'package',
        help="package (e.g. some-package==1.2.3 or just some-package)"
    )
    parser.add_argument(
        'requirements_file',
        help="requirements file to write to (default requirementst.txt)",
        default='requirements.txt', nargs='?'
    )
    parser.add_argument(
        "--verbose", help="Verbose output", action="store_true"
    )

    args = parser.parse_args()
    return run(args.package, args.requirements_file, verbose=args.verbose)


if __name__ == '__main__':
    sys.exit(main())

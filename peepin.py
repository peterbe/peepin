#!/usr/bin/env python
"""
See README :)
"""

from __future__ import print_function
import cgi
import re
import tempfile
import os
import sys

if sys.version_info >= (3,):
    from urllib.request import urlopen
else:
    from urllib import urlopen

import peep


class PackageError(Exception):
    pass


def _verbose(*args):
    print('* ' + ' '.join(args))


def _download(url, binary=False):
    r = urlopen(url)
    if binary:
        return r.read()
    _, params = cgi.parse_header(r.headers.get('Content-Type', ''))
    encoding = params.get('charset', 'utf-8')
    return r.read().decode(encoding)


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

    new_lines = ''
    for h in hashes:
        new_lines += '# sha256: %s\n' % h

    if verbose:
        _verbose("Editing", file)
    requirements = open(file).read()
    requirements = amend_requirements_content(
        requirements,
        package,
        new_lines
    )
    open(file, 'w').write(requirements)

    return 0

def amend_requirements_content(requirements, package, new_lines):

    # if the package wasn't already there, add it to the bottom
    if '%s==' % package not in requirements:
        # easy peasy
        requirements = requirements.strip() + '\n'
        requirements += new_lines
    else:
        # need to replace the existing
        prev = []
        for line in requirements.splitlines():
            if '%s==' % package in line:
                prev.append(line)
                combined = '\n'.join(prev + [''])
                requirements = requirements.replace(combined, new_lines)
                break
            elif '==' in line or '://' in line:
                prev = []
            else:
                prev.append(line)

    return requirements


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
    if verbose:
        print(url)
    content = _download(url)
    finds = re.findall('href="((.*)#md5=\w+)"', content)
    yielded = []

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
                f.write(_download(url, binary=True))
        elif verbose:
            _verbose("  Re-using", filename)
        hash_ = peep.hash_of_file(filename)
        if hash_ in yielded:
            continue
        if verbose:
            _verbose("  Hash", hash_)
        yield hash_
        yielded.append(hash_)

    if not yielded:
        raise PackageError(
            "No packages could be found on {0}".format(url)
        )


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

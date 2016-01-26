#!/usr/bin/env python
"""
See README :)
"""

from __future__ import print_function
import cgi
import tempfile
import os
import sys
import json

if sys.version_info >= (3,):
    from urllib.request import urlopen
else:
    from urllib import urlopen

import peep

import pip

pip_version = pip.__version__
major_pip_version = int(pip_version.split('.')[0])
if major_pip_version >= 8:
    import warnings
    warnings.warn(
        "You have pip {0!r} installed.\n"
        "Use hashin instead (pip install hashin).\n"
        "https://pypi.python.org/pypi/hashin".format(pip_version)
    )


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

    data = get_package_data(package, verbose)
    if not version:
        version = get_latest_version(data)
        assert version
        if verbose:
            _verbose("Latest version for", version)

    hashes = get_hashes(data, version, verbose=verbose)

    new_lines = ''
    for h in hashes:
        new_lines += '# sha256: %s\n' % h
    new_lines += '%s==%s\n' % (package, version)

    if verbose:
        _verbose("Editing", file)
    with open(file) as f:
        requirements = f.read()
    requirements = amend_requirements_content(
        requirements,
        package,
        new_lines
    )
    with open(file, 'w') as f:
        f.write(requirements)

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


def get_latest_version(data):
    return data['info']['version']


def get_package_data(package, verbose=False):
    url = 'https://pypi.python.org/pypi/%s/json' % package
    if verbose:
        print(url)
    content = json.loads(_download(url))
    if 'releases' not in content:
        raise PackageError('package JSON is not sane')

    return content


def get_hashes(data, version, verbose=False):
    yielded = []
    try:
        releases = data['releases'][version]
    except KeyError:
        raise PackageError('No data found for version {0}'.format(version))
    for found in releases:
        url = found['url']
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

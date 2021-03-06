import json
import os
from shutil import rmtree
from tempfile import mkdtemp, gettempdir
from contextlib import contextmanager
from unittest import TestCase
from functools import wraps
from glob import glob

import mock

import peepin


@contextmanager
def tmpfile(name='requirements.txt'):
    dir_ = mkdtemp('peepintest')
    try:
        yield os.path.join(dir_, name)
    finally:
        rmtree(dir_)


def cleanup_tmpdir(pattern):

    def decorator(test):
        @wraps(test)
        def inner(self, *args, **kwargs):
            try:
                return test(self, *args, **kwargs)
            finally:
                for each in glob(os.path.join(gettempdir(), pattern)):
                    os.remove(each)
        return inner
    return decorator


class _Response(object):
    def __init__(self, content, status_code=200, headers=None):
        if isinstance(content, dict):
            content = json.dumps(content).encode('utf-8')
        self.content = content
        self.status_code = status_code
        if headers is None:
            headers = {'Content-Type': 'text/html'}
        self.headers = headers

    def read(self):
        return self.content


class Tests(TestCase):

    @mock.patch('peepin.urlopen')
    def test_get_latest_version_simple(self, murlopen):
        version = peepin.get_latest_version({'info': {'version': '0.3'}})
        self.assertEqual(version, '0.3')

    @mock.patch('peepin.urlopen')
    def test_get_hashes_error(self, murlopen):

        def mocked_get(url, **options):
            if url == "https://pypi.python.org/pypi/somepackage/json":
                return _Response({})
            raise NotImplementedError(url)

        murlopen.side_effect = mocked_get

        self.assertRaises(
            peepin.PackageError,
            peepin.run,
            'somepackage==1.2.3',
            'doesntmatter.txt'
        )

    def test_amend_requirements_content_new(self):
        requirements = """
# empty so far
        """.strip() + '\n'
        new_lines = """
# sha256: 6QTt-5DahBKcBiUs06BfkLTuvBu1uF7pblb_bPaUONU
autocompeter==1.2.3
        """.strip()
        result = peepin.amend_requirements_content(
            requirements, 'autocompeter', new_lines
        )
        self.assertEqual(result, requirements + new_lines)

    def test_amend_requirements_content_replacement(self):
        requirements = """
# sha256: hHK_EwLbFb3yxDk6XpGAzb8ps_jtWwbAa_XGuo9DNYg
autocompeter==1.2.2
        """.strip() + '\n'
        new_lines = """
# sha256: 6QTt-5DahBKcBiUs06BfkLTuvBu1uF7pblb_bPaUONU
autocompeter==1.2.3
        """.strip()
        result = peepin.amend_requirements_content(
            requirements, 'autocompeter', new_lines
        )
        self.assertEqual(result, new_lines)

    def test_amend_requirements_content_replacement_2(self):
        requirements = """
# sha256: 3jrATsqwp-CvZO7jCnHnI7pYhrlYIF9zVN1iQ52mA4k
# sha256: hHK_EwLbFb3yxDk6XpGAzb8ps_jtWwbAa_XGuo9DNYg
autocompeter==1.2.2
        """.strip() + '\n'
        new_lines = """
# sha256: 6QTt-5DahBKcBiUs06BfkLTuvBu1uF7pblb_bPaUONU
autocompeter==1.2.3
        """.strip()
        result = peepin.amend_requirements_content(
            requirements, 'autocompeter', new_lines
        )
        self.assertEqual(result, new_lines)

    def test_amend_requirements_content_replacement_amonst_others(self):
        previous = """
# sha256: cHay6ATFKumO3svU3B-8qBMYb-f1_dYlR4OgClWntEI
otherpackage==1.0.0
""".strip() + '\n'
        requirements = previous + """
# sha256: 3jrATsqwp-CvZO7jCnHnI7pYhrlYIF9zVN1iQ52mA4k
# sha256: hHK_EwLbFb3yxDk6XpGAzb8ps_jtWwbAa_XGuo9DNYg
autocompeter==1.2.2
        """.strip() + '\n'
        new_lines = """
# sha256: 6QTt-5DahBKcBiUs06BfkLTuvBu1uF7pblb_bPaUONU
autocompeter==1.2.3
        """.strip()
        result = peepin.amend_requirements_content(
            requirements, 'autocompeter', new_lines
        )
        self.assertEqual(result, previous + new_lines)

    def test_amend_requirements_content_replacement_amonst_others_2(self):
        previous = """
# sha256: 6nj05rvk7z_4OHM6mUIsl7GjE2plb4N3PqnJWaSRRlw
https://github.com/rhelmer/pyinotify/archive/9ff352f.zip#egg=pyinotify
""".strip() + '\n'
        requirements = previous + """
# sha256: 3jrATsqwp-CvZO7jCnHnI7pYhrlYIF9zVN1iQ52mA4k
# sha256: hHK_EwLbFb3yxDk6XpGAzb8ps_jtWwbAa_XGuo9DNYg
autocompeter==1.2.2
        """.strip() + '\n'
        new_lines = """
# sha256: 6QTt-5DahBKcBiUs06BfkLTuvBu1uF7pblb_bPaUONU
autocompeter==1.2.3
        """.strip()
        result = peepin.amend_requirements_content(
            requirements, 'autocompeter', new_lines
        )
        self.assertEqual(result, previous + new_lines)

    @cleanup_tmpdir('peepin*')
    @mock.patch('peepin.urlopen')
    def test_run(self, murlopen):

        def mocked_get(url, **options):
            if url == "https://pypi.python.org/pypi/peepin/json":
                return _Response({
                    'info': {
                        'version': '0.10',
                    },
                    'releases': {
                        '0.10': [
                            {
                                'url': 'https://pypi.python.org/packages/2.7/p/peepin/peepin-0.10-py2-none-any.whl',
                            },
                            {
                                'url': 'https://pypi.python.org/packages/3.3/p/peepin/peepin-0.10-py3-none-any.whl',
                            },
                            {
                                'url': 'https://pypi.python.org/packages/source/p/peepin/peepin-0.10.tar.gz',
                            }
                        ]
                    }
                })
            elif url == "https://pypi.python.org/packages/2.7/p/peepin/peepin-0.10-py2-none-any.whl":
                return _Response(b"Some py2 wheel content\n")
            elif url == "https://pypi.python.org/packages/3.3/p/peepin/peepin-0.10-py3-none-any.whl":
                return _Response(b"Some py3 wheel content\n")
            elif url == "https://pypi.python.org/packages/source/p/peepin/peepin-0.10.tar.gz":
                return _Response(b"Some tarball content\n")

            raise NotImplementedError(url)

        murlopen.side_effect = mocked_get

        with tmpfile() as filename:
            with open(filename, 'w') as f:
                f.write('')
            retcode = peepin.run('peepin==0.10', filename)
            self.assertEqual(retcode, 0)
            with open(filename) as f:
                output = f.read()
            lines = output.splitlines()

            self.assertEqual(lines[0], '')
            self.assertEqual(
                lines[1],
                '# sha256: MRBPjA-YFqbSE120Iyz6JIssdSVZYmMhZXfTzck6PCU'
            )
            self.assertEqual(
                lines[2],
                '# sha256: YftZIx_-lnzmk6IJnP9ZomlebQKsu2sFEDPjsRB9gAg'
            )
            self.assertEqual(
                lines[3],
                '# sha256: svBtPE0Ui2SHaKurUIavrAQU5J60gT4fPEULl1x3zuk'
            )
            self.assertEqual(
                lines[4],
                'peepin==0.10'
            )

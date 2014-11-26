from unittest import TestCase

import httpretty

import peepin


class Tests(TestCase):

    @httpretty.activate
    def test_get_latest_version_simple(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://pypi.python.org/pypi/peepin",
            body="""
            <div id="content">

            <div id="breadcrumb">
              <a href="/pypi">Package Index</a>

                <span class="breadcrumb-separator">&gt;</span>
                <a href="/pypi/peepin">peepin</a>

                <span class="breadcrumb-separator">&gt;</span>
                <a href="/pypi/peepin/0.3">0.3</a>
            </div>
            """,
        )

        version = peepin.get_latest_version('peepin')
        self.assertEqual(version, '0.3')

    @httpretty.activate
    def test_get_latest_version_multiversion(self):
        httpretty.register_uri(
            httpretty.GET,
            "https://pypi.python.org/pypi/django",
            body="""
            <div id="content">
            <div id="breadcrumb">
              <a href="/pypi">Package Index</a>
                <span class="breadcrumb-separator">&gt;</span>
                <a href="/pypi/Django">Django</a>
            </div>
            ...
            <div class="section">
              <h1>Index of Packages</h1>

            <table class="list">
            <tr>
             <th>Package</th>

             <th>Description</th>
            </tr>

            <tr class="odd">
             <td><a href="/pypi/Django/1.7.x">Django&nbsp;1.7.x</a></td>

             <td>A high-level Python Web framework that ...
            </tr>
            <tr class="even">
             <td><a href="/pypi/Django/1.7">Django&nbsp;1.7</a></td>

             <td>A high-level Python Web framework that ...
            </tr>
            <tr class="odd">
             <td><a href="/pypi/Django/1.6.8">Django&nbsp;1.6.8</a></td>

            """,
        )

        version = peepin.get_latest_version('django')
        self.assertEqual(version, '1.7.x')

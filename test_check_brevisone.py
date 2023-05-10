#!/usr/bin/env python3

import unittest
import unittest.mock as mock
import sys

sys.path.append('..')

from check_brevisone import commandline
from check_brevisone import generate_output
from check_brevisone import get_data
from check_brevisone import main

class UtilTesting(unittest.TestCase):

    @mock.patch('builtins.print')
    def test_output(self, mock_print):
        generate_output(status='CRITICAL')
        mock_print.assert_called_with("CRITICAL")

        generate_output(status='OK', lines=['1: 2', '3: 4'], perfdata={'1': '2', '3': 4})
        mock_print.assert_called_with("OK - 1: 2 3: 4|1=2 3=4")

        generate_output(status='CRITICAL', lines=['que: foo', 'foo bar: 1'], perfdata={'que': 'foo', 'foo bar': 1})
        mock_print.assert_called_with("CRITICAL - que: foo foo bar: 1|que=foo foo_bar=1")

class CLITesting(unittest.TestCase):

    def test_commandline(self):
        actual = commandline(['-H', 'localhost'])
        self.assertEqual(actual.hostname, 'localhost')
        self.assertEqual(actual.protocol, 'https')
        self.assertFalse(actual.insecure)
        self.assertEqual(actual.fail, 1)


class URLTesting(unittest.TestCase):

    @mock.patch('urllib.request')
    def test_get_data(self, mock_url):

        m = mock.MagicMock()
        m.getcode.return_value = 200
        m.read.return_value = b'que:foobar'
        mock_url.urlopen.return_value = m

        actual = get_data('http://localhost', 10, True)
        expected = 'que:foobar'

        self.assertEqual(actual, expected)

    @mock.patch('urllib.request')
    def test_get_data_invalid(self, mock_url):

        m = mock.MagicMock()
        m.getcode.return_value = 200
        m.read.return_value = b''
        mock_url.urlopen.return_value = m

        with self.assertRaises(RuntimeError) as context:
            get_data('http://localhost', 10, True)

    @mock.patch('urllib.request')
    def test_get_data_404(self, mock_url):

        m = mock.MagicMock()
        m.getcode.return_value = 404
        m.read.return_value = b''
        mock_url.urlopen.return_value = m

        with self.assertRaises(RuntimeError) as context:
            get_data('http://localhost', 10, True)


class MainTesting(unittest.TestCase):

    @mock.patch('check_brevisone.get_data')
    def test_main_unknown(self, mock_data):
        d = """
        que: foo
        """
        mock_data.return_value = d

        args = commandline(['-H', 'localhost'])
        actual = main(args)
        self.assertEqual(actual, 3)

    @mock.patch('check_brevisone.get_data')
    def test_main_ok(self, mock_data):
        d = """
        que: foo
        failed: 0
        signal_strength: 15 db
        total: 25
        """
        mock_data.return_value = d

        args = commandline(['-H', 'localhost'])
        actual = main(args)
        self.assertEqual(actual, 0)

    @mock.patch('check_brevisone.get_data')
    def test_main_warn(self, mock_data):
        d = """
        que: foo
        failed: 0
        signal_strength: -91 db
        total: 25
        """
        mock_data.return_value = d

        args = commandline(['-H', 'localhost'])
        actual = main(args)
        self.assertEqual(actual, 1)

    @mock.patch('check_brevisone.get_data')
    def test_main_crit(self, mock_data):
        d = """
        que: foo
        failed: 10
        signal_strength: -91 db
        total: 25
        """
        mock_data.return_value = d

        args = commandline(['-H', 'localhost'])
        actual = main(args)
        self.assertEqual(actual, 2)

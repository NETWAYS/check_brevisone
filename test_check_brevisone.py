#!/usr/bin/env python3

import unittest
import unittest.mock as mock
import sys

sys.path.append('..')

from check_brevisone import commandline
from check_brevisone import generate_output
from check_brevisone import determine_status
from check_brevisone import get_data
from check_brevisone import worst_state
from check_brevisone import main

class UtilTesting(unittest.TestCase):

    @mock.patch('builtins.print')
    def test_output(self, mock_print):
        generate_output(status=2)
        mock_print.assert_called_with("[CRITICAL] - Brevis.One SMS Gateway Status\n")

        generate_output(status=0, perfdata={'1': '2', 'foo': 4})
        mock_print.assert_called_with("[OK] - Brevis.One SMS Gateway Status\n|foo=4 ")

        generate_output(status=3, perfdata={'que': '0', 'foo bar': 1})
        mock_print.assert_called_with("[UNKNOWN] - Brevis.One SMS Gateway Status\n|foo_bar=1 ")

    def test_determine_status(self):
        args = commandline(['-H', 'localhost', '--disk-warning', '1500', '--disk-critical', '3000' ])
        data = {"que": 5,"failed": 1, "signal": 0, 'disk': 1400}

        s, o = determine_status(args, data)

        self.assertIn(' \\_[WARNING] Failed sending: 1', o)
        self.assertIn(' \\_[CRITICAL] Queue length: 5', o)
        self.assertIn(' \\_[OK] Signal strength: 0', o)
        self.assertIn(' \\_[OK] Disk usage: 1400', o)

        data = {"que": 0,"failed": 0, "signal": -900, 'disk': 2000}

        s, o = determine_status(args, data)

        self.assertIn(' \\_[OK] Failed sending: 0', o)
        self.assertIn(' \\_[OK] Queue length: 0', o)
        self.assertIn(' \\_[CRITICAL] Signal strength: -900', o)
        self.assertIn(' \\_[WARNING] Disk usage: 2000', o)

        data = {"que": 0,"failed": 0, "signal": -900, 'disk': 4000}

        s, o = determine_status(args, data)

        self.assertIn(' \\_[OK] Failed sending: 0', o)
        self.assertIn(' \\_[OK] Queue length: 0', o)
        self.assertIn(' \\_[CRITICAL] Signal strength: -900', o)
        self.assertIn(' \\_[CRITICAL] Disk usage: 4000', o)

    def test_worst_state(self):

        actual = worst_state()
        expected = 3
        self.assertEqual(actual, expected)

        actual = worst_state(0,1,2)
        expected = 2
        self.assertEqual(actual, expected)

        actual = worst_state(1,2,3,4)
        expected = 3
        self.assertEqual(actual, expected)

        actual = worst_state(0,0,0,0)
        expected = 0
        self.assertEqual(actual, expected)

class CLITesting(unittest.TestCase):

    def test_commandline(self):
        actual = commandline(['-H', 'localhost'])
        self.assertEqual(actual.hostname, 'localhost')
        self.assertEqual(actual.protocol, 'https')
        self.assertFalse(actual.insecure)
        self.assertEqual(actual.failed_warning, 1)


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
    def test_main_data_missing(self, mock_data):
        d = """

        """
        mock_data.return_value = d

        args = commandline(['-H', 'localhost'])
        actual = main(args)
        self.assertEqual(actual, 3)

        d = """
        failed: 0
        """
        mock_data.return_value = d

        actual = main(args)
        self.assertEqual(actual, 3)

    @mock.patch('check_brevisone.get_data')
    def test_main_ok(self, mock_data):
        d = """
        que: 0
        failed: 0
        signal: 15 db
        total: 25
        """
        mock_data.return_value = d

        args = commandline(['-H', 'localhost'])
        actual = main(args)
        self.assertEqual(actual, 0)

    @mock.patch('check_brevisone.get_data')
    def test_main_warn(self, mock_data):
        d = """
        que: 1
        failed: 0
        signal: -91 db
        total: 25
        """
        mock_data.return_value = d

        args = commandline(['-H', 'localhost'])
        actual = main(args)
        self.assertEqual(actual, 1)

    @mock.patch('check_brevisone.get_data')
    def test_main_crit(self, mock_data):
        d = """
        que: 0
        failed: 10
        signal: -91 db
        total: 25
        """
        mock_data.return_value = d

        args = commandline(['-H', 'localhost'])
        actual = main(args)
        self.assertEqual(actual, 2)

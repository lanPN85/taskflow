import unittest

from datetime import timedelta

from taskflow import utils


class UtilsTestCase(unittest.TestCase):
    def test_format_timedelta(self):
        inp = timedelta(seconds=3600)
        expected = "01:00:00"
        output = utils.format_timedelta(inp)
        self.assertEqual(expected, output)

        inp = timedelta(hours=2, minutes=20)
        expected = "02:20:00"
        output = utils.format_timedelta(inp)
        self.assertEqual(expected, output)

        inp = timedelta(hours=5, minutes=17, seconds=22)
        expected = "05:17:22"
        output = utils.format_timedelta(inp)
        self.assertEqual(expected, output)

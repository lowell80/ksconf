#!/usr/bin/env python

# For coverage info, can be run with nose2, like so:
#  nose2 -s . -C

from __future__ import absolute_import, unicode_literals

import os
import sys
import unittest

from io import StringIO

import ksconf.ext.six as six

# Allow interactive execution from CLI,  cd tests; ./test_filterlang.py
if __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from ksconf.conf.filterlang import evaluate_filter
from tests.cli_helper import TestWorkDir, parse_string
from ksconf.conf.parser import DUP_EXCEPTION, DUP_MERGE, DUP_OVERWRITE, \
    DuplicateStanzaException, DuplicateKeyException, parse_conf, write_conf, ConfParserException, \
    PARSECONF_MID, GLOBAL_STANZA



class FilterLangTestCase(unittest.TestCase):
    """ Test the custom conf filtering language"""

    def test_single_stanza_match(self):
        i = parse_string("""
        [stanza1]
        key1 = yes
        key2 = no
        [stanza2]
        key1 = no
        key2 = yes
        empty =
        """)
        o = evaluate_filter("[stanza1]", i)
        self.assertEqual(o["stanza1"]["key1"], "yes")
        self.assertEqual(o["stanza1"]["key2"], "no")
        self.assertNotIn("stanza2", o)
        self.assertNotIn("empty", o["stanza1"])




if __name__ == '__main__':  # pragma: no cover
    unittest.main()

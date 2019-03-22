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



class FilterLangElementalTestCase(unittest.TestCase):
    """ Test core elements of the custom conf filtering language"""

    @property
    def sample1(self):
        return parse_string("""
        [stanza1]
        key1 = yes
        key2 = no
        [stanza2]
        key1 = no
        key2 = yes
        empty =
        """)

    def test_select_stanza_str(self):
        o = evaluate_filter("[stanza1]", self.sample1)
        self.assertEqual(o["stanza1"]["key1"], "yes")
        self.assertEqual(o["stanza1"]["key2"], "no")
        self.assertNotIn("stanza2", o)
        self.assertNotIn("empty", o["stanza1"])

        o = evaluate_filter("[stanza2]", self.sample1)
        self.assertEqual(o["stanza2"]["key1"], "no")
        self.assertEqual(o["stanza2"]["key2"], "yes")
        self.assertEqual(o["stanza2"]["empty"], "")

    # def test_select_stanza_regex(self)
    # def test_select_stanza_wildcard(self)

    def test_select_attr_eq_qstr(self):
        """ Selection: attribute eq quoted string."""
        o = evaluate_filter('key1=="yes"', self.sample1)
        self.assertEqual(o["stanza1"]["key1"], "yes")
        self.assertNotIn("stanzas2", o)

    # Not implemented yet
    #@unittest.expectedFailure
    @unittest.skip
    def test_select_attr_eq_rstr(self):
        """ Selection: attribute eq quoted string."""
        o = evaluate_filter('key1==yes', self.sample1)
        self.assertEqual(o["stanza1"]["key1"], "yes")
        self.assertNotIn("stanzas2", o)

    # def test_select_attr_eq_glob(self):
    # def test_select_attr_eq_regex(self):

    # def test_select_attr_ne_str(self):
    # def test_select_attr_ne_glob(self):
    # def test_select_attr_ne_regex(self):

    def test_project_one_attr_str(self):
        o = evaluate_filter('{key1}', self.sample1)
        self.assertSetEqual(set(o), {"stanza1", "stanza2"})
        o = evaluate_filter('{empty}', self.sample1)
        self.assertSetEqual(set(o), {"stanza2"})

    def test_project_one_attr_qstr(self):
        o = evaluate_filter("{'key1'}", self.sample1)
        self.assertSetEqual(set(o), {"stanza1", "stanza2"})
        o = evaluate_filter("{'empty'}", self.sample1)
        self.assertSetEqual(set(o), {"stanza2"})

    def test_project_multi_attr_qstr(self):
        o = evaluate_filter("{'key1', 'empty'}", self.sample1)
        self.assertSetEqual(set(o), {"stanza1", "stanza2"})

    def test_project_multi_attr_mixed(self):
        o = evaluate_filter("{'key1',empty}", self.sample1)
        self.assertSetEqual(set(o), {"stanza1", "stanza2"})


class FilterLangCombinedTestCase(unittest.TestCase):
    """ Test combination of elements of the custom conf filtering language"""

    @property
    def sample_jungle(self):
        return parse_string("""
        [jungle]
        animal = monkey
        key2 = 01

        [forest]
        animal = wolf

        [mountain]
        animal = snake
        """)

    def test_selattrprojattr(self):
        o = evaluate_filter(
        """
        animal == "monkey" { animal }
        """, self.sample_jungle)
        self.assertDictEqual(o, {"jungle" : { "animal" : "monkey"} })








if __name__ == '__main__':  # pragma: no cover
    unittest.main()

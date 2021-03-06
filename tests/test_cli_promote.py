#!/usr/bin/env python
from __future__ import absolute_import, print_function, unicode_literals

import os
import sys
import unittest

# Allow interactive execution from CLI,  cd tests; ./test_cli.py
if __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ksconf.consts import EXIT_CODE_SUCCESS, EXIT_CODE_FAILED_SAFETY_CHECK
from tests.cli_helper import TestWorkDir, ksconf_cli

dummy_config = {
    "stanza": {"any_content": "will do"}
}


class CliPromoteTest(unittest.TestCase):

    def sample_data01(self):
        twd = TestWorkDir()
        self.conf_default = twd.write_file("default/savedsearches.conf", r"""
        [License usage trend by sourcetype]
        action.email.useNSSubject = 1
        alert.track = 0
        disabled = 0
        enableSched = 0
        dispatch.earliest_time = -30d@d
        dispatch.latest_time = now
        display.general.type = visualizations
        display.page.search.tab = visualizations
        display.statistics.show = 0
        display.visualizations.charting.chart = area
        display.visualizations.charting.chart.stackMode = stacked
        request.ui_dispatch_app = kintyre
        request.ui_dispatch_view = search
        search = | tstats sum(b) as bytes where index=summary_splunkidx by st, _time span=1h | timechart span=1h sum(eval(bytes/1073741824)) as b by st | foreach * [ eval "<<FIELD>>"=round('<<FIELD>>',2) ]
        """)
        self.conf_local = twd.write_file("local/savedsearches.conf", r"""
        [License usage trend by sourcetype]
        alert.track = 1
        display.statistics.show = 1
        request.ui_dispatch_app = kintyre
        search = | tstats sum(b) as bytes where index=summary_splunkidx by st, _time span=1h \
        | timechart span=1h sum(eval(bytes/1073741824)) as b by st \
        | foreach * [ eval "<<FIELD>>"=round('<<FIELD>>',3) ]
        """)
        return twd

    def assert_data01(self, twd):
        d = twd.read_conf("default/savedsearches.conf")
        stanza = d["License usage trend by sourcetype"]
        self.assertEqual(stanza["disabled"], "0")
        self.assertEqual(stanza["alert.track"], "1")
        self.assertTrue(len(stanza["search"].splitlines()) > 2)

    def test_promote_batch_simple_keep(self):
        twd = self.sample_data01()
        with ksconf_cli:
            ksconf_cli("promote", "--batch", "--keep-empty", self.conf_local, self.conf_default)
            self.assertEqual(os.stat(self.conf_local).st_size, 0)  # "Local file should be blanked")
            self.assert_data01(twd)
        del twd

    def test_promote_batch_simple(self):
        twd = self.sample_data01()
        with ksconf_cli:
            ksconf_cli("promote", "--batch", self.conf_local, self.conf_default)
            self.assertFalse(os.path.isfile(self.conf_local))  # "Local file should be blanked")
            self.assert_data01(twd)
        del twd

    def test_promote_to_dir(self):
        twd = self.sample_data01()
        with ksconf_cli:
            ksconf_cli("promote", "--batch", self.conf_local, twd.get_path("default"))
            self.assertTrue(os.path.isfile(self.conf_default), "Default file should be created.")
            self.assertFalse(os.path.isfile(self.conf_local), "Default file should be created.")
            self.assert_data01(twd)

    def test_promote_new_file(self):
        twd = TestWorkDir()
        dummy_local = twd.write_conf("local/dummy.conf", dummy_config)
        dummy_default = twd.get_path("default/dummy.conf")
        twd.makedir("default")
        with ksconf_cli:
            # Expect this to fail
            ko = ksconf_cli("promote", "--batch", dummy_local, dummy_default)
            self.assertEqual(ko.returncode, EXIT_CODE_SUCCESS)
            self.assertRegex(ko.stdout, "Moving source file [^\r\n]+ to the target")

    def test_promote_same_file_abrt(self):
        twd = TestWorkDir()
        dummy = twd.write_conf("dummy.conf", dummy_config)
        with ksconf_cli:
            # Expect this to fail
            ko = ksconf_cli("promote", "--batch", dummy, dummy)
            self.assertEqual(ko.returncode, EXIT_CODE_FAILED_SAFETY_CHECK)
            self.assertRegex(ko.stderr, "same file")

    '''
    def test_promote_simulate_ext_edit(self):
        # Not quite sure how to do this reliably....  May need to try in a loop?
        pass
    '''


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

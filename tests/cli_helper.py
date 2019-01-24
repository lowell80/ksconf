from __future__ import absolute_import, print_function, unicode_literals

import os
import shutil
import stat
import sys
import tempfile
from collections import namedtuple
from io import open, StringIO
from subprocess import list2cmdline
from textwrap import dedent

# Some unittest fixup for various python versions
import tests.compat as _
del _

from ksconf.__main__ import cli
from ksconf.util.file import file_hash
from ksconf.vc.git import git_cmd

from ksconf.conf.parser import parse_conf, write_conf, \
    GLOBAL_STANZA, PARSECONF_MID

# What to export
__all__ = [
    "static_data",
    "ksconf_cli",
    "TestWorkDir",
    "GLOBAL_STANZA",
    "parse_conf",
    "write_conf",
    "_debug_file",
]


def _debug_file(flag, fn):  # pragma: no cover
    """ Dump file contents with a message string to the output.  For quick'n'dirty unittest
    debugging only """
    with open(fn) as fp:
        content = fp.read()
    length = len(content)
    hash = file_hash(fn)
    print("\n{flag} {fn}  len={length} hash={hash} \n{content}".format(**vars()))
    del flag, hash, length


def static_data(path):
    """ Get paths to files under the 'tests/data/*' location """
    # Assume "/" for path separation for simplicity; but ultimately OS independent
    parts = path.split("/")
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "data", *parts))


'''
# Let's try to avoid launching external processes (makes coverage more difficult, and so on)
def ksconf_exec(args):
    args = list(args)
    args.insert(0, "ksconf.py")
    from subprocess import call
    args = list(args)
    if True:    # Coverage enabled
        args = ["coverage", "run", "-a" ] + args
    rc = call(args)
    return KsconfOutput(rc, ...)
'''


class _KsconfCli():
    """
    CLI Wrapper context management class for unit testing;

    USAGE:   Use the ksconf_cli() singleton in a context (with)

    Unfortunately, we have to redirect stdout/stderr while this runs, not
    very clean, but we try to make it as safe as possible.
    tmpfile:    os.tmpfile, or StringIO?
    """

    KsconfOutput = namedtuple("KsconfOutput", ["returncode", "stdout", "stderr"])

    @staticmethod
    def _as_string(stream):
        stream.seek(0)
        return stream.read()

    def __call__(self, *args):
        # In later version of Python (3.4), something like this could be considered:
        # from contextlib import redirect_stdout
        self._last_args = args
        _stdout, _stderr = (sys.stdout, sys.stderr)
        try:
            # Capture all output written to stdout/stderr
            temp_stdout = sys.stdout = StringIO()
            temp_stderr = sys.stderr = StringIO()
            try:
                rc = cli(args, _unittest=True)
            except SystemExit as e:
                if hasattr(e, "code"):  # PY3
                    rc = e.code
                else:
                    rc = e.message
        finally:
            # This next step MUST be done!
            (sys.stdout, sys.stderr) = _stdout, _stderr
        stdout = self._as_string(temp_stdout)
        stderr = self._as_string(temp_stderr)
        output = self.KsconfOutput(rc, stdout, stderr)
        self._last_output = output
        return output

    def __enter__(self):
        self._last_args = None
        self._last_output = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Don't worry with coverage here.  It gets plenty of testing DURING unittest development ;-)
        if exc_type is not None:  # pragma: no cover
            sys.stderr.write("Exception while running: ksconf {0}\n".
                             format(list2cmdline(self._last_args)))
            ko = self._last_output
            if ko:
                if ko.stdout:
                    sys.stderr.write("STDOUT:\n{0}\n".format(ko.stdout))
                if ko.stderr:
                    sys.stderr.write("STDERR:\n{0}\n".format(ko.stderr))
            # Re-raise exception
            return False


ksconf_cli = _KsconfCli()


class TestWorkDir(object):
    """ Create a temporary working directory to create app-like structures and other supporting
    file system artifacts necessary for many CLI tests.  Cleanup is done automatically. """

    encoding = "utf-8"

    def __init__(self, git_repo=False):
        if git_repo:
            self._path = tempfile.mkdtemp("-ksconftest-git")
            self.git("init")
        else:
            self._path = tempfile.mkdtemp("-ksconftest")
        self.git_repo = git_repo

    def __del__(self):
        if "KSCONF_KEEP_TEST_FILES" in os.environ:
            return

        # Remove read-only file handler (e.g. clean .git/objects/xx/* files on Windows)
        def del_rw(action, name, exc):
            # https://stackoverflow.com/a/21263493/315892
            # Not checking for file vs dir, ...
            os.chmod(name, stat.S_IWRITE)
            os.remove(name)
            del action, exc

        shutil.rmtree(self._path, onerror=del_rw)

    def git(self, *args):
        o = git_cmd(args, cwd=self._path)
        if o.returncode != 0:  # pragma: no cover
            # Because, if we're using ksconf_cli, then we may be redirecting these...
            stderr = sys.__stderr__
            stderr.write("Git command 'git {0}' failed with exit code {1}\n{2}\n"
                         .format(" ".join(args), o.returncode, o.stderr))
            raise RuntimeError("Failed git command (return code {0})".format(o.returncode))

    def get_path(self, rel_path):
        # Always using unix/URL style paths internally.  But we want this to be OS agnostic
        rel_parts = rel_path.split("/")
        return os.path.join(self._path, *rel_parts)

    def makedir(self, rel_path, path=None):
        if path is None:
            path = self.get_path(rel_path)
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def write_file(self, rel_path, content):
        path = self.get_path(rel_path)
        self.makedir(None, path=os.path.dirname(path))
        kw = {}
        if isinstance(content, bytes):
            kw["mode"] = "wb"
        else:
            kw["mode"] = "w"
            kw["encoding"] = self.encoding
            content = dedent(content)
        with open(path, **kw) as stream:
            stream.write(content)
        return path

    def read_file(self, rel_path, as_bytes=False):
        path = self.get_path(rel_path)
        kw = {}
        if as_bytes:
            kw["mode"] = "rb"
        else:
            kw["mode"] = "r"
            kw["encoding"] = self.encoding
        with open(path, **kw) as stream:
            content = stream.read()
        return content

    def write_conf(self, rel_path, conf):
        path = self.get_path(rel_path)
        self.makedir(None, path=os.path.dirname(path))
        write_conf(path, conf)
        return path

    def read_conf(self, rel_path, profile=PARSECONF_MID):
        path = self.get_path(rel_path)
        return parse_conf(path, profile=profile)

    def copy_static(self, static, rel_path):
        src = static_data(static)
        with open(src, "rb") as stream:
            content = stream.read()
        return self.write_file(rel_path, content)
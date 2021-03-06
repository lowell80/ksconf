Git tips & tricks
=================

.. _ksconf_pre_commit:

Pre-commit hooks
----------------

Ksconf is setup to work as a `pre-commit`_ plugin.
To use ksconf in this manner, simply configuring the ksconf repo in your pre-commit configuration file.
If you haven't done any of this before, it's not difficult to setup but beyond the scope of this guide.
Go read the pre-commit docs and circle back here when ready to setup the hooks.


Hooks provided by ksconf
~~~~~~~~~~~~~~~~~~~~~~~~~

Two hooks are currently defined by the ksconf repository:


    .. _pchook_ksconf-check:

    ksconf-check
        Runs :ref:`ksconf_cmd_check` to perform basic validation tests against all files
        in your repo that end with ``.conf`` or ``.meta``.
        Any errors will be reported by the UI at commit time and
        you'll be able to correct mistakes before bogus files are committed into your repo.
        If you're not sure why you'd need this, check out :ref:`Why validate my conf files? <why_check>`

    .. _pchook_ksconf-sort:

    ksconf-sort
        Runs :ref:`ksconf_cmd_sort` to normalize any of your ``.conf`` or ``.meta`` files
        which will make diffs more readable and merging more predictable.
        As with any hook, you can customize the filename pattern of which files this applies to.
        For example, to manually organize :file:`props.conf` files, simply add the ``exclude`` setting.
        Example below.


Configuring pre-commit hooks in you repo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add ksconf pre-commit hooks to your repository, add the following content to your
:file:`.pre-commit-config.yaml` file:


..  code-block:: yaml
    :name: .pre-commit-config.yaml

    repos:
    - repo: https://github.com/Kintyre/ksconf
      sha: v0.6.1
      hooks:
        - id: ksconf-check
        - id: ksconf-sort


For general reference, here's a copy of what I frequently use for my own repos.

..  code-block:: yaml

    - repo: https://github.com/pre-commit/pre-commit-hooks
      sha: v2.0.0
      hooks:
        - id: trailing-whitespace
          exclude: README.md
        - id: end-of-file-fixer
          exclude: README.md$
        - id: check-json
        - id: check-xml
        - id: check-ast
        - id: check-added-large-files
          args: [ '--maxkb=50' ]
        - id: check-merge-conflict
        - id: detect-private-key
        - id: mixed-line-ending
          args: [ '--fix=lf' ]
    - repo: https://github.com/Kintyre/ksconf
      sha: v0.6.1
      hooks:
        - id: ksconf-check
        - id: ksconf-sort
          exclude: (props|logging)\.conf

..  tip::

    You may want to update ``sha`` to the most currently released stable version.
    Upgrading this frequently isn't typically necessary since these two operations are pretty basic and stable.
    But it's still a good idea to review the change log to see what (if any) pre-commit functionality was updated.


.. note::

    Sometimes pre-commit can get in the way.
    Instead of disabling it entirely, it's often better to disable just the specific rule that's causing an issue
    using the ``SKIP`` environmental variable.
    So for example, if intentionally adding a file over 50 Kb, a command like this will allow all the *other* rules to still run.

    ..  code-block:: sh

        SKIP=check-added-large-file git commit -m "Refresh lookup files for bogus TA"

    This and other tricks are fully documented in the `pre-commit`_ docs.
    However, this comes up frequently enough that it's worth repeating here.


Should my version of ksconf and pre-commit plugins be the same?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're running both ``ksconf`` locally as well as the ksconf pre-commit plugin then technically you have ksconf installed twice.
That may sound less than ideal, but practically, this isn't a problem.
As long as the version of the ksconf CLI tool is *close* to the ``sha`` listed in :file:`.pre-commit-config.yaml`, then everything should work fine.

My suggestion:

 #. Keep versions in the same `major.minor` release range.  Or bump the version every 6-12 months.
 #. Check the changelog for any pre-commit related changes or compatibility concerns.

While keeping ``ksconf`` CLI versions in sync across your environment is recommended, it doesn't matter as much for the pre-commit plugin.  Why?

 #. The pre-commit plugin offers a small subset of overall ksconf functionality.
 #. The exposed functionality is stable and changes infrequently.
 #. Updating pre-commit too frequently may cause unnecessary delays if you have a large team or high number of git clones throughout your environment, as each one will have to wait and upgrade the next time pre-commit is kicked off.


Git configuration tweaks
-----------------------------


.. _ksconf_ext_diff:

Ksconf as external difftool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use :ref:`ksconf_cmd_diff` as an external *difftool* provider for :command:`git`.
Edit :file:`~/.gitconfig` and add the following entries:

..  code-block:: ini
    :name: ~/.gitconfig`

    [difftool "ksconf"]
        cmd = "ksconf --force-color diff \"$LOCAL\" \"$REMOTE\" | less -R"
    [difftool]
        prompt = false
    [alias]
        ksdiff = "difftool --tool=ksconf"


Now you can run this new ``git`` alias to compare files in your directory using the ``ksconf diff``
feature instead of the default textual diff that git provides.
This is especially helpful if the ``ksconf-sort`` pre-commit hook hasn't been enabled.

..  code-block:: sh

    git ksdiff props.conf


..  tip:: Wonky version of git?

    If you find yourself in the situation where ``git-difftool`` hasn't been fully installed correctly (or the Perl extensions are missing), then here's a workaround option for you.

    ..  code-block:: sh

        ksconf diff <(git show HEAD:./props.conf) props.conf

    Take note of the relative path prefix ``./``.
    In practice, this can get ugly.


Stanza aware textual diffs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make ``git diff`` show the 'stanza' on the ``@@`` output lines.

..  note:: How does git know that?

    Ever wonder how ``git diff`` is able to show you the name of the function or method where changes
    were made?  This works for many programming languages out of the box.  If you've ever spend much
    time looking at diffs that additional context is invaluable.  As it turns out, this is
    customizable by adding a stanza matching regular expression with a file pattern match.

Simply add the following settings to your git configuration:

..  code-block:: ini
    :name: ~/.gitconfig

    [diff "conf"]
        xfuncname = "^(\\[.*\\])$"

Then register this new ability with specific file patterns using git's ``attributes`` feature.
Edit :file:`~/.config/git/attributes` and add:

..  code-block:: none
    :name: ~/.config/git/attributes

    *.conf diff=conf
    *.meta diff=conf

..  note:: Didn't work as expected?

    Be aware that the location for your global-level attributes may be different.
    Use the following command to test if the settings have been applied.

   ..  code-block:: sh

       git check-attr -a -- *.conf

   Test to make sure the ``xfuncname`` attribute was set as expected:

   ..  code-block:: sh

       git config diff.conf.xfuncname




..  include:: common

Concepts
========

..  _configuration-layers:

Configuration layers
--------------------

The idea of configuration layers is shared across multiple actions in ksconf.
Specifically, :ref:`combine <ksconf_cmd_combine>` is used to merge multiple layers, and the
:ref:`unarchive <ksconf_cmd_unarchive>` command can be used to install or upgrade an app in a
layer-aware way.

What's the problem?
~~~~~~~~~~~~~~~~~~~

In a typical enterprise deployment of Splunk, a single app can easily have multiple logical sources
of configuration:

 1. Upstream app developer (typically via Splunkbase)
 2. Local developer app-developer adds organization-specific customizations or fixes
 3. Splunk admin tweaks the inappropriate ``indexes.conf`` settings, and
 4. Custom knowledge objects added by your subject matter experts.

Ideally we'd like to version control these, but doing so is complicated because normally you have to
manage all 4 of these logical layers in one 'default' folder.

.. note:: Isn't that what the **local** folder is for?

    Splunk requires that app settings be located either in :file:`default` or :file:`local`;
    and managing local files with version control leads to merge conflicts;
    so effectively, all version controlled settings need to be in :file:`default`,
    or risk merge conflicts,  However, making changes to the :file:`default` folder causes
    issues when you attempt to upgrade an app upstream.  See how this is a catch-22?

Let's suppose a new upstream version is released.
If you aren't managing layers independently, then you have to manually upgrade the app being careful to preserve all custom configurations.
Compare this to the solution provided by the :ref:`combine <ksconf_cmd_combine>` functionality.
The layered approach provide an advantage because logical sources can be stored separately in their own directories thus allowing them to be modified independently.
Using this approach, changes in the "upstream" layer will only ever be from an official release, and the organizational layer will only ever contain customizations made by your organization.
Practically, this means it's no longer necessary to comb through commit logs identifying which custom changes need to be preserved and reapplied.

While this doesn't completely remove the need for a human to review app upgrades, it does lower the
overhead enough that updates can be pulled in more frequently, thus minimizing divergence.

.. _minimizing_files:

Minimizing files
----------------

**A typical scenario:**

To customize a Splunk app or add-on, many admins simply copy the conf file from default to local and then apply changes to the local one.
That's a common practice, but stopping there complicates future upgrades.
The next step should be to clean up the local file, deleting all the unmodified entries that were copied from default.

**Why does this matter?**

If you've copied a default file into the local folder, this means that local file doesn't contain *just* your settings, it contains all copy of *all* of default settings too.
So in the future, fixes published by the app creator are likely to be masked by your local settings.
A better approach is to reduce the local conf file leaving only the stanzas and settings that you intended to change.
While this is a pain to do by hand, it's quite easily accomplished by :ref:`ksconf_cmd_minimize`.
This make your conf files easier to read and makes upgrades easier, and it's now easy to do.


What does Splunk have to say about this?   (From the docs)

    |   "When you first create this new version of the file, **start with an empty file and add only
        the attributes that you need to change.** Do not start from a copy of the default directory. If you
        copy the entire default file to a location with higher precedence, any changes to the default
        values that occur through future Splunk Enterprise upgrades cannot take effect, because the
        values in the copied file will override the updated values in the default file." -- [SPLKDOC1]_


..  tip::

    It's a good practice to minimize your files right away.
    If you wait, it may not be obvious what specific version of default that local was copied from.
    In other words, if you run the :command:`minimize` command *after* you've upgraded the default folder, you may need to do extra work to manually reconcile upgrade differences.
    Because any changes made between the initial version of the default file and the most recently release of the conf file cannot be automatically addressed in this fashion.

    If your files are all in git, and you know a REF of the previous version of your default file, you can use some commands like this:

    ..  code-block:: sh

        # Review the output of the log, and find the revision of the last change
        git log --oneline -- default/inputs.conf

        # Assuming "e633e6" was identified as the desired baseline ref, based on the 'log' output

        # Compare what's changed in the 'inputs.conf' file between releases (FYI only)
        ksconf diff <(git show e633e6:./default/inputs.conf) default/inputs.conf

        # Now apply the 'minimization' based on the original version of inputs.conf
        ksconf minimize --target=local/inputs.conf <(git show e633e6:./default/inputs.conf)

   As always, be sure to double check the results.



.. [SPLKDOC1] https://docs.splunk.com/Documentation/Splunk/7.2.3/Admin/Configurationfiledirectories

.. include:: common

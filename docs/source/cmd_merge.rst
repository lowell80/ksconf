..  _ksconf_cmd_merge:

ksconf merge
============

..  argparse::
    :module: ksconf.__main__
    :func: build_cli_parser
    :path: merge
    :nodefault:


Examples
---------

Here's a simple, possibly silly, example that merges all ``props.conf`` file from *all* of your technology addons into a single output file:

..  code-block:: sh

    ksconf merge --target=all-ta-props.conf etc/apps/*TA*/{default,local}/props.conf

See an expanded version of this example here: :ref:`example_ta_idx_tier`

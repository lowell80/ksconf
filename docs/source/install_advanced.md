# Advanced Installation Guide

The content in this document was split out from the [Install Guide](install.html) because it became
unruly and the number of possible Python installation combinations and gotchas became very intense.
However, that means that there's lots of truly helpful stuff in here, but becoming a python
packaging expert isn't my goal, so the Splunk app install approach was introduced to alleviate much
of this pain.

A portion of this document is targeted at those who can't install packages as Admin or are forced to
use Splunk's embedded Python.  For everyone else, please start with the one-liner!

**So if you can't easily get `ksconf` installed as a python package, and you have reason to avoid
installing it as a Splunk app, then keep reading, and good luck.**


## Flowchart

(Unfinished; more of a brainstorm at this point...)
 
* Is Python installed?  (OS level)
  * Is the version greater than 2.7?   (Some early 2.7 version have quarks, but typically this is okay)
  * If Python 3.x, is it greater than 3.4?  (I'd like to drop 3.4, but lots of old distros still have it.)
 * Do you have admin access?  (root/Administrator; or can you get it?  How hard?  Will you need it each time you upgrade the ksconf?)
 * Do you already have a large python deployment or dependency?  (If so, you'll probably be fine.  Use `virtualenv`)
 * Do you have any prior Python packaging or administration experience?
 * Are you dealing with some vendor-specific solution?
   * Example:  RedHat Software Collections -- where they realize there software is way too old, so
     they try to make it possible to install newever version of things like Python, but since they
     aren't native or the default, you still end up jumping through a bunch of wonky hoops)
 * Do you have Internet connectivity? (air gap or blocked outbound traffic, or proxy)
 * Do you want to build/deploy your own ksconf extensions?  If so, the python package is a better option.  (But at that point, you can probably already handle any packaging issues yourself.)

## Installation

There are several ways to install ksconf.  Technically all standard python packaging approaches
should work just fine, there's no compiled code or external run-time dependencies so installation
is fairly easy, but for non-python developers there are some gotchas.   Installation options are
listed from the most easy and recommended to more obscure and difficult:


### Install from PyPI with PIP

The preferred installation method is to install via the standard Python package tool 'pip'.  Ksconf
can be installed via the registered `kintyre-splunk-conf` package using the standard python process.

There are 2 popular variations, depending on whether or not you would like to install for all users
or just play around with it locally.


#### Install ksconf into a virtual environment

***Use this option if you don't have admin access***

Installing `ksconf` with [virtualenv][virtualenv] is a great way to test the tool without requiring
admin privileges and has many advantages for a production install too.  Here are the basic steps to
get started.

Please change `venv` to a suitable path for your environment.

    # Install Python virtualenv package (if not already installed)
    pip install virtualenv

    # Create and activte new 'venv' virtual environment
    virtualenv venv
    source venv/bin/activate

    pip install kintyre-splunk-conf

*Windows users:*  The above virtual environment activation should be run as
`venv\Scripts\activate.bat`.


#### Install ksconf system-wide

***Note:  This requires admin access.***

This is the absolute easiest install method where 'ksconf' is available to all users on the system
but it requires root access and `pip` must be installed and up-to-date.

On Mac or Linux, run:

    sudo pip install kintyre-splunk-conf

On Windows, run this commands from an Administrator console.

    pip install kintyre-splunk-conf


### CentOS (RedHat derived) distros

    # Enable the EPEL repo so that `pip` can be installed.
    sudo yum install -y epel-release

    # Install pip
    sudo yum install -y python-pip

    # Install ksconf (globally, for all users)
    sudo pip install kintyre-splunk-conf


#### RedHat Software Collections

The following assumes the `python27` software collection, but other version of Python are supported
too.  The initial setup and deployment of Software Collections is beyond the scope of this doc.

    sudo scl enable python27 python -m pip install kintyre-splunk-conf

(If pip isn't installed, try running `yum install python27-python-pip`)

Unfortunately, the `ksconf` entrypoint script (in the `bin` folder) will not work correctly on it's
own because it doesn't know about the scl environment, nor is it in the default PATH. To solve this
run the following:

    sudo cat > /usr/local/bin/ksconf <<HERE
    #!/bin/sh
    source scl_source enable python27
    exec /opt/rh/python27/root/usr/bin/ksconf "$@"
    HERE
    chmod +x /usr/local/bin/ksconf




## Use the standalone executable

**NOTE:** This option remains for historical reference and will like be disabled in the future.  If
this seems like the best option to you, then please consider install the [KSCONF App for Splunk][ksconfapp] instead.

Ksconf can be installed as a standalone executable zip app.  This approach still requires a python
interpreter to be present either from the OS or the one embedded with Splunk Enterprise.  This works
well for testing or when all other options fail.

From the [GitHub releases][gh-releases] page, grab the file name `ksconf-*.pyz`, download it, copy
it to a `bin` folder in your PATH and rename it `ksconf`.  The default shebang looks for 'python' in
the PATH, but this can be adjusted as needed.  Since installing with Splunk is a common use case, a
second file named `ksconf-*-splunk.pyz` already has the shebang set for the standard `/opt/splunk`
install path.

Typical embedded Splunk install example:

    VER=0.5.0
    curl https://github.com/Kintyre/ksconf/releases/download/v${VER}/ksconf-${VER}-splunk.pyz
    mv ksconf-${VER}-splunk.pyz /opt/splunk/bin/
    cd /opt/splunk/bin
    ln -sf ksconf-${VER}-splunk.pyz ksconf
    chmod +x ksconf
    ksconf --version


Reasons why this is a non-ideal install approach:

 * Lower performance since all python files live in a zip file, and precompiled version's can be
   cached.
 * No standard install pathway (doesn't use pip); user must manually copy the executable into place.
 * Uses a non-standard build process.  (May not be a big deal, but could cause things to break in
  the future.)



### Install the Wheel manually (offline mode)

Download the latest "Wheel" file file from [PyPI][pypi-files], copy it to the destination server
and install with pip.

Offline pip install:

    pip install ~/Downloads/kintyre-splunk-conf-0.4.2-py2.py3-none-any.whl


### Install with Splunk's Python

**NOTE:** Don't do this anymore.  Please use the [KSCONF App for Splunk][ksconfapp] instead.

Splunk Enterprise 6.x and later installs an embedded Python 2.7 environment.
However, Splunk does not provide packing tools (such as `pip` or the `distutils` standard library
which is required to bootstrap install `pip`).  For these reasons, it's typically easier and cleaner
to install `ksconf` with the system provided Python.  However, sometimes the system-provided Python
environment is the wrong version, is missing (like on Windows), or security restrictions prevent the
installation of additional packages.  In such cases, Splunk's embedded Python becomes a beacon of
hope.

#### On Linux or Mac

Download the latest "Wheel" file file from [PyPI][pypi-files].  The path to this download will be
set in the `pkg` variable as shown below.

Setup the shell:

    export SPLUNK_HOME=/opt/splunk
    export pkg=~/Downloads/kintyre_splunk_conf-0.4.9-py2.py3-none-any.whl

Run the following:

    cd $SPLUNK_HOME
    mkdir Kintyre
    cd Kintyre
    # Unzip the 'kconf' folder into SPLUNK_HOME/Kintyre
    unzip "$pkg"

    cat > $SPLUNK_HOME/bin/ksconf <<HERE
    #!/bin/sh
    export PYTHONPATH=$PYTHONPATH:$SPLUNK_HOME/Kintyre
    exec $SPLUNK_HOME/bin/python -m ksconf \$*
    HERE
    chmod +x $SPLUNK_HOME/bin/ksconf

Test the install:

    ksconf --version

#### On Windows

 1. Open a browser and download the latest "Wheel" file file from [PyPI][pypi-files].
 2. Rename the `.whl` extension to `.zip`.  (This may require showing file extensions in Explorer.)
 3. Extract the zip file to a temporary folder.  (This should create a folder named "ksconf")
 4. Create a new folder called "Kintyre" under the Splunk installation path (aka `SPLUNK_HOME`)
    By default this is `C:\Program Files\Splunk`.
 5. Copy the "ksconf" folder to "SPLUNK_HOME\Kintyre".
 6. Create a new batch file called `ksconf.bat` and paste in the following.  Be sure to
    adjust for a non-standard `%SPLUNK_HOME%` value, if necessary.

        @echo off
        SET SPLUNK_HOME=C:\Program Files\Splunk
        SET PYTHONPATH=%SPLUNK_HOME%\bin;%SPLUNK_HOME%\Python-2.7\Lib\site-packages\win32;%SPLUNK_HOME%\Python-2.7\Lib\site-packages;%SPLUNK_HOME%\Python-2.7\Lib
        SET PYTHONPATH=%PYTHONPATH%;%SPLUNK_HOME%\Kintyre
        CALL "%SPLUNK_HOME%\bin\python.exe" -m ksconf %*

 7. Move `ksconf.bat` to the `Splunk\bin` folder.  (This assumes that `%SPLUNK_HOME%/bin` is part of
    your `%PATH%`.  If not, add it, or find an appropriate install location.)
 8. Test this by running `ksconf --version` from the command line.


## Validate the install

Confirm installation with the following command:

    ksconf --help

If this works, it means that `ksconf` installed and is part of your `PATH` and should be useable
everywhere in your system.  Go forth and conquer!

## Offline installation

Installing ksconf to an offline or network restricted computer requires three steps: (1) download
the latest packages from the Internet to a staging location, (2) transfer the staged content (often
as a zip file) to the restricted host, and (3) use pip to install packages from the staged copy.
Fortunately, pip makes offline workflows quite easy to achieve.  Pip can download a python package
with all dependencies stored as wheels files into a single directory, and pip can be told to install
from that directory instead of attempting to talk to the Internet.

The process of transferring these files is very organization-specific.  The example below shows the
creation of a tarball (since `tar` is universally available on Unix systems), but any acceptable
method is fine.  If security is a high concern, this step is frequently where safety checks are
implemented.  For example, antivirus scans, static code analysis, manual inspection, and/or
comparison of cryptographic file hashes.

One additional use-case for this workflow is to ensure the exact same version of all packages are
deployed consistently across all servers and environments.  Often building a `requirements.txt` file
with `pip freeze` is a more appropriate solution.  Or consider using `pipenv lock` for even more
security benefits. 


### Offline installation steps

**NOTE:**  Pip must be installed on the destination server for this process to work.  If pip is NOT
installed see the *Offline installation of pip* section below.


**Step 1**: Use pip to download the latest package and their dependencies.  Be sure to use the same
version of python that is running on destination machine

    # download packages
    python2.7 -m pip download -d ksconf-packages kintyre-splunk-conf

A new directory named 'ksconf-packages' will be created and will contain the necessary `*.whl` files.

**Step 2**: Transfer the directory or archive to the remote computer.  Insert whatever security and
file copy procedures necessary for your organization.

    # Compress directory (on staging computer)
    tar -czvf ksconf-packages.tgz ksconf-packages

    # Copy file using whatever means
    scp ksconf-packages.tgz user@server:/tmp/ksconf-packages.tgz

    # Extract the archive (on destination server)
    tar -xzvf ksconf-packages.tgz

**Step 3**:

    # Install ksconf package with pip
    pip install --no-index --find-links=ksconf-packages kntyre-splunk-conf

    # Test the installation
    ksconf --version

The `ksconf-packages` folder can now safely be removed.


### Offline installation of pip

Use the recommended `pip` install procedures listed elsewhere if possible.  But if a remote
bootstrap of pip is your only option, then here are the steps.  (This process mirrors the steps
above and can be combined, if needed.)


**Step 1**:  Fetch bootstrap script and necessary wheels

    mkdir ksconf-packages
    curl https://bootstrap.pypa.io/get-pip.py -o ksconf-packages/get-pip.py
    python2.7 -m pip download -d /tmp/my_packages pip setuptools wheel

The `ksconf-pacakges` folder should contain 1 script, and 3 wheel (`*.whl`) files.

**Step 2**: Archive and/or copy to offline server

**Step 3**: Bootstrap pip

    sudo python get-pip.py --no-index --find-links=ksconf-packages/

    # Test with
    pip --version


#### Use pip without installing it

If you have a copy of the `pip*.whl` (wheel) file, then it can be executed directly by python.  This
can be used to run `pip` without actually installing it, or for install pip initially (bypassing the
`get-pip.py` script step noted above.)

Here's an example of how this could work:

**Step 1:** Download the pip wheel on a machine where `pip` works, by running:

    pip download pip -d .

This will create a file like `pip-19.0.1-py2.py3-none-any.whl` in the current working directory.

**Step 2:** Copy the pip wheel to another machine (likely where pip isn't installed.)

**Step 3:** Execute the wheel by running:

    python pip-19.0.1-py2.py3-none-any.whl/pip list

Just substitute the `list` command with whatever action you need (like `install` or whatever)


## Frequent gotchas

### PIP Install TLS Error

If `pip` throws an error message like the following:

    There was a problem confirming the ssl certificate: [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version
    ...
    No matching distribution found for setuptools


The problem is likely caused by changes to PyPI website in April 2018 when support for TLS v1.0 and
1.1 were removed.  Downloading new packages requires upgrading to a new version of pip.  Like so:

Upgrade pip as follows:

    curl https://bootstrap.pypa.io/get-pip.py | python

Note:  Use `sudo python` above if not in a virtual environment.

Helpful links:

 * [Not able to install Python packages [SSL: TLSV1_ALERT_PROTOCOL_VERSION]](https://stackoverflow.com/a/49769015/315892)
 * ['pip install' fails for every package ("Could not find a version that satisfies the requirement")](https://stackoverflow.com/a/49748494/315892)


### No module named 'command.install'

If, while trying to install `pip` or run a `pip` command you see the following error:

    ImportError: No module named command.install

Likely this is because you are using a crippled version of Python; like the one that ships with
Splunk.  This won't work.  Either get a pre-package version (the `.pyz` file or install using the
OS-level Python.


## Resources

 * [Python packaging][python-packaging] docs provide a general overview on installing Python
   packages, how to install per-user vs install system-wide.
 * [Install PIP][pip-install] docs explain how to bootstrap or upgrade
   `pip` the Python packaging tool.  Recent versions of Python come with this by default, but
   releases before Python 2.7.9 do not.


[gh-releases]: https://github.com/Kintyre/ksconf/releases/latest
[ksconfapp]:  https://github.com/Kintyre/ksconf/releases/latest
[pip-install]: https://pip.pypa.io/en/stable/installing/
[pypi-files]: https://pypi.org/project/kintyre-splunk-conf/#files
[python-download]: https://www.python.org/downloads/
[python-packaging]: https://docs.python.org/3/installing/index.html
[virtualenv]: https://virtualenv.pypa.io/en/stable/

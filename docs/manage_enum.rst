Manage Enum
============

Command usage:
::

  $ usage: manage_enum.py [-h] [-v] [-y URL] [-d DESCRIPTION] [-s [URL|FILE]]
                          [-t [XLS|ODF|CSV|TAB|GOOGLE]] [-u USERNAME]
                          [-p PASSWORD]
                          bundle name [fields [fields ...]]

    Add / Update / Remove items from an Enum Bundle

    positional arguments:
      bundle
      name
      fields

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -y URL, --youtrack URL
                            URL of YouTrack instance
      -d DESCRIPTION, --desc DESCRIPTION
                            Enum value description. Can be a format string
      -s [URL|FILE], --src [URL|FILE]
                            Path to a file or name of a Google Docs document
      -t [XLS|ODF|CSV|TAB|GOOGLE], --src-type [XLS|ODF|CSV|TAB|GOOGLE]
                            Type of source file.
      -u USERNAME, --username USERNAME
                            Google Docs username
      -p PASSWORD, --password PASSWORD
                            Google Docs password


Examples
-----------

Create a `valueName` value in the `bundleName` bundle in the tracker located
at http://example.org/issues.
::

  $ manage_enum.py -y http://example.org/issues bundleName valueName

Create the value `42` in the `userid` bundle with a description of `Name: Joe`.
::

  $ manage_enum.py -y http://example.org/issues -d 'Name: %(username)' userid 42 username=Joe



API
-----

.. module:: manage_enum
.. autoclass:: EnumBundle
   :members:

# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 John Hampton <pacopablo@pacopablo.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: John Hampton <pacopablo@pacopablo.com>

__author__ = 'John Hampton'

# Std Library Imports
import argparse
import sys

# Local Imports

# Third Party Imports
from youtrack import YouTrackObject
from youtrack.connection import Connection

VERSION = '1.0'
PROG_DESC = """
Add / Update / Remove items from an Enum Bundle
"""[1:]

def main(args):
    """ Add / Update / Remove items from the specified bundle

    """


    cnx = Connection(args.youtrack, username, password)
def do_args(argv):
    """ Parse command line arguments

    Expects the command line minus the script name.  Generally sys.argv[1:]
    """
    parser = argparse.ArgumentParser(description=PROG_DESC, version=VERSION)
    parser.add_argument('bundle')
    parser.add_argument('name')
    parser.add_argument('fields', nargs='*')
    parser.add_argument('-y', '--youtrack', metavar='URL',
                        default='http://localhost',
                        help='URL of YouTrack instance')
    parser.add_argument('-d', '--desc', metavar='DESCRIPTION', default='',
                        help='Enum value description. Can be a format string')
    parser.add_argument('-s', '--src', metavar='[URL|FILE]', default=None,
                        help='Path to a file or name of a Google Docs '
                             'document')
    parser.add_argument('-t', '--src-type', metavar='[XLS|ODF|CSV|TAB|GOOGLE]',
                        default='GOOGLE', help='Type of source file.')
    parser.add_argument('-u', '--username', default=None, help='Google Docs '
                        'username')
    parser.add_argument('-p', '--password', default=None, help='Google Docs '
                        'password')
    args = parser.parse_args(argv)

    # parse out the description data from the extra fields
    args.desc_data = {}
    for v in args.fields:
        tokens = v.split('=')
        args.desc_data.setdefault(tokens[0], '='.join(tokens[1:]))

    # verify presence of login data

    return args


if __name__ == '__main__':
    args = do_args(sys.argv[1:])
    rc = main(args)
    sys.exit(rc)
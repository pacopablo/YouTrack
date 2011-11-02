# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 John Hampton <pacopablo@pacopablo.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: John Hampton <pacopablo@pacopablo.com>
import getpass
import gdata

__author__ = 'John Hampton'

# Std Library Imports
import argparse
import sys
import getpass
import os


# Local Imports

# Third Party Imports
from youtrack import YouTrackObject, YouTrackException
from youtrack.connection import Connection
import gdata.spreadsheet.service
import gdata.docs.service


VERSION = '1.0'
PROG_DESC = """
Add / Update / Remove items from an Enum Bundle
"""[1:]
GOOGLE_DOCS_SOURCE_APP = 'asylumware-trouyack-manage_enum'
SRC_TYPES = ['XLS', 'ODF', 'CSV', 'TAB', 'GOOGLE']

class InvalidSrcType(Exception):
    def __init__(self, src_type='Unknown'):
        Exception.__init__(self)
        self.src_type = src_type


class InvalidSrcPath(Exception):
    def __init__(self, src_path=''):
        Exception.__init__(self)
        self.src_path = src_path


class BundleSyncError(Exception): pass



class EnumValueSrc(object):
    """ Object representing the source of enum bundle value information.

    Usage:

    >>> src = EnumValueSrc(args)
    >>> value_info_pairs = [info_pair for info_pair in src.get_values()]

    """

    def __init__(self, args):
        """ Argparse Parser object containing as return by do_args().
        """
        self.name = args.name
        self.desc_data = args.desc_data
        self.gusername = args.gusername
        self.gpassword = args.gpassword
        self.google = None
        self.src_type = self.set_src_type(args.srctype)
        self.src = self.set_src_path(args.src)

    def _google_login(self):
        """ Log into Google Docs

        TODO: Figure out what happens on failed login so that we can handle
        it gracefully
        """
        self.google = gdata.spreadsheet.service.SpreadsheetsService()
        self.google.email = self.gusername
        self.google.password = self.gpassword
        self.google.source = GOOGLE_DOCS_SOURCE_APP
        self.google.ProgrammaticLogin()

    def _empty(self):
        """ Simply Raise a StopIteration.
        """
        print('calling _empty')
        raise StopIteration

    def _get_GOOGLE_values(self):
        """ Retrieve values from Google doc.

        Retrieves values from all worksheets.  Each worksheet must have a
        'name' column.  Values in the 'name' column are used as the Enum
        values.  The rest of the columns in the row are put into the
        desc_data dictionary for use in the description.
        """

        def is_src(top_row):
            """ Searches the row for a column labeled 'name', case-insensitive.

            Return a dictionary containing the column label with the
            associated column key.
            """
            col_keys = [k.lower() for k in top_row.custom.keys()]
            if 'name' in col_keys:
                return col_keys
            return []

        def extract_values(r, col_keys):
            name = r['name'].text
            desc_data = {}
            for k in col_keys:
                desc_data[k] = r[k].text
                continue
            del desc_data['name']
            return (name, desc_data)

        wsfeed = self.google.GetWorksheetsFeed(self.src)
        for worksheet in wsfeed.entry:
            wskey = worksheet.id.text.rsplit('/', 1)[1]
            rows = self.google.GetListFeed(self.src, wskey)
            if (len(rows.entry) > 0):
                col_keys = is_src(rows.entry[0])
                print(col_keys)
                if col_keys:
                    for row in rows.entry[1:]:
                        yield extract_values(row.custom, col_keys)
                        continue
            continue

    def set_src_type(self, src_type):
        """ Sets the source type.

        Source type may be one of the strings found in SRC_TYPES. An
        InvalidSrcType exception is raised if attempting to set a source not
        found in SRC_TYPES.
        """

        if ((not isinstance(src_type, basestring)) or
           (src_type.upper() not in SRC_TYPES)):
            raise InvalidSrcType(str(src_type))
        else:
            return src_type.upper()

    def set_src_path(self, src_path=None):
        """ Sets the path to the source file.

        src_path may be a path to a file or the name of a Google Doc.
        If src_path is not found on the local file system, it will assume that
        it is a Google Doc and attempt to access it.  If it can not access the
        document, and InvalidSrcPath exception will be raised.
        """
        self.src = src_path
        if ((self.src_type == 'GOOGLE') or
            (not os.path.isfile(os.path.abspath(src_path)))):
            self._google_login()
            doc_query = gdata.docs.service.DocumentQuery()
            doc_query['title'] = src_path
            doc_query['title-exact'] = 'true'
            sfeed = self.google.GetSpreadsheetsFeed(query=doc_query)
            if len(sfeed.entry) < 1:
                raise InvalidSrcPath(src_path)
            else:
                return sfeed.entry[0].id.text.rsplit('/', 1)[1]

    def get_src_values(self):
        """ Yield (name, {data}) tuples from whichever source specified.
        """
        if not self.src:
            yield (self.name, self.desc_data)
        else:
            if self.src_type in SRC_TYPES:
                method_name = '_get_' + self.src_type + '_values'
                print(method_name)
                f = getattr(self, method_name, self._empty)
                for v in f():
                    yield v

class EnumBundle(object):
    """Dict-like object representing an EnumBundle from YouTrack.

    :param str name: Name of the Enum Bundle in YouTrack
    :param str url: URL of YouTrack installation
    :param str username: Username to use when logging into YouTrack
    :param str password: Password to use when logging into YouTrack
    :param dcit proxy_info: (optional) Dictionary mapping protocol to the
                             URL of the proxy.

    Example usage:
    --------------
    >>> bundle = EnumBundle('EnumName', url='http://example.org/youtrack',
                             username='user', password='password')
    >>> bundle.name
    'EnumName'
    >>> bundle['value'] = 'value description'
    >>> bundle['value']
    'value description'
    >>> bundle.save()

    """

    def __init__(self, name, url=None, username=None, password=None,
                 proxy_info=None):
        self.name = name
        self.url = url
        self.password = password
        self.order = []
        self.values = {}
        self.synchronized = False
        self.cnx_error_code = None
        self.cnx_error_msg = ''
        try:
            self.cnx = Connection(url, username, password)
            self._load_enum()
            self.synchronized = True
        except YouTrackException, e:
            # Unable to log into YouTrack site
            self.cnx_error_code = e.response.status_code
            self.cnx_error_msg = e.response.msg
        pass

    def _load_enum(self):
        enum_bundle = self.cnx.getEnumBundle(self.name)

        pass

    def save(self, force=False):
        """ Save the EnumBundle to the corresponding bundle on the server
        """
        if (not self.synchronized) and (not force):
            raise BundleSyncError
        pass

def main(args):
    """ Add / Update / Remove items from the specified bundle

    """

    enum_dest = EnumValueDest
    cnx = Connection(args.youtrack, args.yusername, args.ypassword)
    enum_bundle = cnx.getEnumBundle(args.bundle)
    list_items = {}
    for i in enum_bundle.values:
        list_items[v.element_name] = v.description
    enum_src = EnumValueSrc(args)
    for name, desc_data in enum_src.get_src_values():
        desc = build_desc(args.desc, desc_data)
        if name in list_items.keys():
            if not (desc == list_items[name]):
                pass
            pass
        else:

            print('%s: %s' % (name, str(desc_data)))




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
                        dest='srctype', default='GOOGLE',
                        help='Type of source file.')
    parser.add_argument('-yu', '--youtrack-username', dest='yusername',
                        default=None, help='YouTrack username')
    parser.add_argument('-yp', '--youtrack-password', dest='ypassword',
                        default=None, help='YouTrack password')
    parser.add_argument('-gu', '--google-username', dest='gusername',
                        default=None, help='Google Docs username')
    parser.add_argument('-gp', '--google-password', dest='gpassword',
                        default=None, help='Google Docs password')
    args = parser.parse_args(argv)

    # parse out the description data from the extra fields
    args.desc_data = {}
    for v in args.fields:
        tokens = v.split('=')
        args.desc_data.setdefault(tokens[0], '='.join(tokens[1:]))

    # verify presence of YouTrack login data
    if not args.yusername:
        args.yusername = raw_input("YouTrack Username: ")
    if not args.ypassword:
        args.ypassword = getpass.getpass("YouTrack Password: ")

    # verify presence of Google login data if Google Docs is selected
    if args.srctype.lower() == 'google':
        if not args.gusername:
            args.gusername = raw_input("Google Username: ")
        if not args.gpassword:
            args.gpassword = getpass.getpass('Google Password: ')

    print(args.src)
    print(args.srctype)

    return args


if __name__ == '__main__':
    args = do_args(sys.argv[1:])
    rc = main(args)
    sys.exit(rc)

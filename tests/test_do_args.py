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

from nose.tools import with_setup, raises
from manage_enum import do_args

def test_youtrack_host():
    args = do_args(["-y", "http://example.org", "bundle", "name"])
    assert('http://example.org' == args.youtrack)
    args = do_args(["--youtrack", "http://example.org", "bundle", "name"])
    assert('http://example.org' == args.youtrack)
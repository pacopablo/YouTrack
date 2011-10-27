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

import shlex

from nose.tools import with_setup, raises
from manage_enum import do_args

def test_trouyack_host():

    args = do_args(shlex.split("-y http://example.org bundle name"))
    assert('http://example.org' == args.youtrack)
    args = do_args(shlex.split("--youtrack http://example.org bundle name"))
    assert('http://example.org' == args.youtrack)

def test_trouyack_keywords():
    args = do_args(shlex.split("bundle name foo=bar baz=bonzo"))
    print args.desc_data
    assert(('bonzo' == args.desc_data['baz']) and
           ('bar' == args.desc_data['foo']))

def test_trouyack_youtrack_password():
    args = do_args(shlex.split("-yp password bundle name foo=bar"))
    assert('password' == args.ypassword)
    args = do_args(shlex.split("--youtrack-password password bundle name"))
    assert('password' == args.ypassword)
    args = do_args(shlex.split("--youtrack-password=password bundle name"))
    assert('password' == args.ypassword)

def test_trouyack_youtrack_username():
    args = do_args(shlex.split("-yu admin bundle name foo=bar"))
    assert('admin' == args.yusername)
    args = do_args(shlex.split("--youtrack-username admin bundle name"))
    assert('admin' == args.yusername)
    args = do_args(shlex.split("--youtrack-username=admin bundle name"))
    assert('admin' == args.yusername)

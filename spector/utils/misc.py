# -*- coding: utf-8 -*-
# parts of spector
#
# Copyright (C) 2015 Benoît Bovy
# see license.txt for more details
#

"""
Various utility functions used internally in spector.

"""


def inv_dict(d):
    """Return a dict (val: key) given a dict (key -> val).

    """
    return dict((v, k) for k, v in d.items())

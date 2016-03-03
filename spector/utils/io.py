# -*- coding: utf-8 -*-
# parts of spector
#
# Copyright (C) 2015 Benoît Bovy
# see license.txt for more details
#

"""
Some utility functions for file reading/writing.

"""

import struct
import re


def bytes_2_bits(bytes_list, swap=False):
    """
    Return a list of bits (list of 0 or 1 values)
    from a sequence of bytes.
    """
    bits_list = []
    for byte in bytes_list:
        bits8 = [(byte >> i) & 1 for i in range(8)]
        if swap:
            bits8.reverse()
        bits_list += bits8

    return bits_list


def bits_2_int(bits_list, swap=False):
    """
    Return a int given a sequence
    of bits (list of 0 or 1 values).
    """
    if swap:
        bits_list = reversed(bits_list)
    return int(''.join(str(b) for b in bits_list),
               base=2)


def intdec_2_float(vi, vd):
    """
    Return a float given two 4-byte ints
    `vi` (integer) and `vd` (decimal).
    """
    df = 2.**24
    return vi + vd / df


def read_bin_block(f, ffmt, pos=None, endian="<"):
    """
    Read a formatted binary block/line/record.

    Parameters
    ----------
    f : `file` object
        An opened file.
    ffmt : iterable
        A sequence of (`name`, `format`) tuples
        defining the fields in the binary block.
        `name` is either a string or None and
        `format` is a string used for unpacking
        the field value (see :func:`struct.unpack`).
    pos : int or None
        If not None, start reading the block at that
        position in the file (otherwise it start reading
        at the current position).
    endian : str
        Byte order (see :mod:`struct`).

    Returns
    -------
    fields
        A dictionary of field names and values
        as specified in `tfmt`.

    """
    fmt = endian + ''.join((s for k, s in ffmt))
    nbytes = struct.calcsize(fmt)

    if pos is not None:
        f.seek(pos)

    fkeys = [k for k, s in ffmt if k is not None]
    fvals = struct.unpack(fmt, f.read(nbytes))

    return dict(zip(fkeys, fvals))


def read_str_block(string, regex, ftype=None):
    """
    Read a formatted text block/line/record.

    Parameters
    ----------
    string : str
        The string to parse
    regex : str
        A regular expression used to parse the
        string. It must contain some groups (field
        names)
    ftype : dict or None
        A dictionary (field name: type or callable)
        used for converting the value of the extracted
        fields. If None, no conversion is done.

    Returns
    -------
    fields
        A dictionary of field names and values.

    """
    fields = re.match(regex, string).groupdict()

    if ftype is not None:
        for k, f in ftype.items():
            fields[k] = f(fields[k])

    return fields

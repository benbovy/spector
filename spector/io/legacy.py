# -*- coding: utf-8 -*-
# parts of spector
#
# Copyright (C) 2015 Benoît Bovy
# see license.txt for more details
#

"""
Legacy formats used at GIRPAS.

"""

__all__ = ('read_fts1', 'read_bruker', 'read_spec', 'read_rinsland')


import struct
import math
import datetime

import numpy as np

from . import _iofmt
from . import _iocodes
from ..utils.io import (bytes_2_bits, bits_2_int, intdec_2_float,
                        read_bin_block, read_str_block)
from ..utils.misc import inv_dict


def read_fts1(filename):
    """
    Read a spectrum stored in a FTS1-formatted binary file.

    This is a legacy, custom format used for FTIR spectra
    measured with the hp1000 instrument.

    """
    # --- read header
    with open(filename, 'rb') as f:
        spec = read_bin_block(f, _iofmt.fts1_header_ffmt)

    # -- post-processing header
    # strings
    for k in ('name', 'source', 'ftype'):
        spec[k] = spec[k].decode().strip()

    # dates
    for suffix in ['begin', 'end']:
        datetime_key = '_'.join(['datetime', suffix])
        h_dt_keys = ['_'.join([t, suffix])
                     for t in ('year', 'dayofyear')]
        year, dayofyear = [spec.pop(k) for k in h_dt_keys]
        spec[datetime_key] = (
            datetime.datetime(year, 1, 1)
            + datetime.timedelta(dayofyear - 1)
        )
    dt_delta = spec['datetime_end'] - spec['datetime_begin']
    hour = spec.pop('hour_avg')
    spec['datetime_avg'] = (
        spec['datetime_begin'] + dt_delta / 2
        + datetime.timedelta(seconds=hour * 3600)
    )

    # source string -> source id
    spec['source_id'] = inv_dict(_iocodes.source_id).get(
        spec.pop('source').lower(), 0
    )

    # resolution
    spec['resolution'] = 500. / spec.pop('opd')

    # wavenumber step
    spec['wavenumber_step'] = (
        (spec['wavenumber_end'] - spec['wavenumber_begin'])
        / spec['n_points']
    )

    # TODO: aperture correction
    # TODO: wavenumber correction

    # --- read data
    with open(filename, 'rb') as f:
        f.seek(2048)   # header = 2048 bytes
        data = np.fromfile(f, dtype='f')
        spec['data'] = data[:spec['n_points']]

    return spec


def read_bruker(filename):
    """
    Read a spectrum stored in a Bruker-formatted binary file.

    This format is used for FTIR spectra measured with
    the Bruker instrument at the JungfrauJoch (modified from
    the Bruker's OPUS propiertary format).

    """
    # --- read header
    with open(filename, 'rb') as f:
        spec = read_bin_block(f, _iofmt.bruker_header_ffmt)

    # --- post-processing header
    # string
    spec['name'] = spec['name'].decode().strip()

    # keep `n_points2`
    if spec['n_points'] != spec['n_points2']:
        raise ValueError(
            "number of points mismatch in file {0} ({1}, {2})"
            .format(spec['name'],
                    spec['n_points1'], spec['n_points2'])
        )
    spec['n_points'] = spec.pop('n_points2')

    # date
    dateb = bytes_2_bits(spec.pop('date_block'))
    timeb = bytes_2_bits(spec.pop('time_block'))
    secd, seci = math.modf(
        bits_2_int(timeb[0:12], swap=True) / 10
    )
    spec['datetime_avg'] = datetime.datetime(
        bits_2_int(dateb[12:24], swap=True),
        bits_2_int(dateb[6:12], swap=True),
        bits_2_int(dateb[:6], swap=True),
        bits_2_int(timeb[18:24], swap=True),
        bits_2_int(timeb[12:18], swap=True),
        int(seci),
        int(secd * 1e6)
    )

    # int, dec -> float
    wn_b2 = spec.pop('waven_begin_i'), spec.pop('waven_begin_d')
    spec['wavenumber_begin'] = intdec_2_float(*wn_b2)
    wn_e2 = spec.pop('waven_end_i'), spec.pop('waven_end_d')
    spec['wavenumber_end'] = intdec_2_float(*wn_e2)
    spec['laser_frequency'] = intdec_2_float(spec.pop('laserf_i'),
                                             spec.pop('laserf_d'))
    spec['resolution'] = intdec_2_float(spec.pop('resolution_i'),
                                        spec.pop('resolution_d'))

    # `wavenumber_end` correction (includes last point)
    wn_range = spec['wavenumber_end'] - spec['wavenumber_begin']
    wn_step = wn_range / spec['n_points']
    spec['wavenumber_step'] = wn_step
    spec['wavenumber_end'] -= wn_step

    # scale, type conversion
    spec['resolution'] *= 1e3   # unit ??

    # TODO: wavenumber correction

    # -- read data
    with open(filename, 'rb') as f:
        f.seek(1280)   # header = 1280 bytes
        data = np.fromfile(f, dtype='f')
        spec['data'] = data

    return spec


def read_spec(filename):
    """
    Read a spectra description file ('SPyy' or 'BRyy').

    This is a legacy format used to store metadata about
    the measured spectra of one year (given by the suffix 'yy').
    the prefix 'SP' is relative to older observations at the
    JungfrauJoch station (hp1000 instrument) and the
    prefix 'BR' is relative to the observations made
    with the Bruker instrument.

    """
    # --- read header and records
    records = []
    with open(filename, 'rb') as f:
        header = read_bin_block(f, _iofmt.spec_header_ffmt)

        for r in range(header['n_records']):
            # alternating empty/filled records: issue ?
            empty_record = read_bin_block(f, _iofmt.spec_record_ffmt)
            records.append(read_bin_block(f, _iofmt.spec_record_ffmt))

    # --- post-processing header
    # dates
    for k in header.keys():
        if 'created' in k or 'modified' in k:
            try:
                header[k] = datetime.datetime.strptime(
                    header[k].decode(), '%d %b %Y %H:%M:%S'
                )
            except ValueError:
                header[k] = header[k].decode().strip()

    # --- post-processing records
    for r in records:

        # parse 1-byte integers
        r['relative_humidity'] = bits_2_int(
            bytes_2_bits(r.pop('relative_humidity'))
        )
        r['tropopause_height'] = bits_2_int(
            bytes_2_bits(r.pop('tropopause_height'))
        )

        # check for undefined values
        if r['temperature'] == -9999:
            r['temperature'] = float('nan')
        if r['pressure'] == -9999:
            r['pressure'] = float('nan')
        if r['relative_humidity'] == -99:
            r['relative_humidity'] = float('nan')
        if r['tropopause_height'] == -9:
            r['tropopause_height'] = float('nan')

        # scale, type conversion
        r['n_points_itf'] *= 1000      # Kn -> n
        r['n_points_fft'] *= 1000      # Kn -> n
        r['resistance'] *= 1e3         # KOhms -> Ohms
        r['temperature'] *= 0.1        # deg celsius
        r['pressure'] *= 0.1           # mbar
        r['tropopause_height'] *= 0.1  # km
        r['relative_humidity'] *= 1.   # int to float
        r['wavenumber_step'] *= 1e-3   # 1e-9 m

        # dates
        for suffix in ['avg', 'begin', 'end']:
            datetime_key = '_'.join(['datetime', suffix])
            r_dt_keys = ['_'.join([t, suffix])
                         for t in ('year', 'dayofyear', 'hour')]
            year, dayofyear, hour = [r.pop(k) for k in r_dt_keys]
            r[datetime_key] = (
                datetime.datetime(year, 1, 1)
                + datetime.timedelta(dayofyear - 1)
                + datetime.timedelta(seconds=hour * 3600)
            )

        # strings
        r['name'] = r['name'].decode().strip()

        # decode the composite field `quality`
        qb = bytes_2_bits(r.pop('quality'))
        r['is_bad_spectrum'] = bool(qb[0])
        r['is_mean_spectrum'] = bool(qb[1])
        r['is_bad_zero'] = bool(qb[2])
        r['fringing_level'] = bits_2_int(qb[3:5])
        r['has_bad_sn_ratio'] = bool(qb[5])
        r['has_bad_ils'] = bool(qb[6])
        r['is_sun_centered'] = not bool(qb[7])
        r['has_pollution'] = bool(qb[8])
        r['has_slow_signal_variation'] = bool(qb[9])
        r['has_fast_signal_variation'] = bool(qb[10])
        r['has_technical_problem'] = bool(qb[11])
        r['weather_id'] = bits_2_int(qb[13:])

    return header, records


def read_rinsland(filename):
    """
    Read a spectrum stored in the Rinsland format.

    This is an intermediate, legacy format used to store
    a (subset) spectrum and its some of its metadata
    (ASCII header).

    """
    # --- read ascii header (80c), bin header and data
    with open(filename, 'rb') as f:
        spec = read_str_block(
            struct.unpack('<80s', f.read(80))[0].decode(),
            _iofmt.rinsland_header_regex,
            ftype=_iofmt.rinsland_header_ftype
        )
        spec.update(
            read_bin_block(f, _iofmt.rinsland_datahdr_ffmt)
        )
        spec['data'] = np.frombuffer(f.read(), dtype='f')

    # --- post-process header
    # date
    hour = spec.pop('hour_avg')
    hour_dt = datetime.timedelta(seconds=hour * 3600)
    spec['datetime_avg'] = spec.pop('date') + hour_dt

    return spec

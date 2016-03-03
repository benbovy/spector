# -*- coding: utf-8 -*-
# parts of spector
#
# Copyright (C) 2015 Benoît Bovy
# see license.txt for more details
#

"""
Some - partially defined - formats of
spectra data/metadata.

TODO: provide more explanation.


Attributes
----------
fts1_header_ffmt : ((name, fmt), (name, fmt)...)
    Specification of some fields in the header
    of FTS1 spectra files (binary).
bruker_header_ffmt : ((name, fmt), (name, fmt)...)
    Specification of some fields in the header
    of Bruker spectra files (binary).
spec_header_ffmt : ((name, fmt), (name, fmt)...)
    Definition of the header fields
    of SPEC spectra description files
    ('BRyy' or 'SPyy', binary).
spec_record_ffmt : ((name, fmt), (name, fmt)...)
    Definition of the fields of each record
    in SPEC spectra description files (binary).
rinsland_header_regex : string
    Definition of the text format of the rinsland
    spectra files (regular expression).
rinsland_header_ftype : dict
    Field types (name: type or callable), used
    for converting the field values extracted
    in the rinsland header.
rinsland_datahdr_ffmt : ((name, fmt), (name, fmt)...)
    Fields of the binary header of the rinsland
    files (used to read the data).

"""

from datetime import datetime


fts1_header_ffmt = (
    (None, '14x'),
    ('source', '10s'),
    (None, '12x'),
    ('dayofyear_begin', 'h'),
    ('year_begin', 'h'),
    ('dayofyear_end', 'h'),
    ('year_end', 'h'),
    ('correction_factor', 'f'),
    (None, '222x'),
    ('aperture', 'f'),
    ('nb_scan_backward', 'h'),
    (None, '2x'),
    ('ftype', '12s'),
    (None, '308x'),
    ('n_points', 'i'),
    ('wavenumber_begin', 'd'),
    ('wavenumber_end', 'd'),
    ('opd', 'd'),
    ('sun_elevation', 'f'),
    (None, '10x'),
    ('sn_ratio', 'h'),
    ('secz', 'f'),
    ('hour_avg', 'f'),
    (None, '138x'),
    ('name', '12s'),
    (None, '68x'),
    ('nb_scan_forward', 'h')
)


bruker_header_ffmt = (
    (None, '4x'),
    ('name', '12s'),
    (None, '4x'),
    ('n_points', 'i'),
    (None, '236x'),
    ('n_points2', 'i'),
    ('n_scan_forward', 'i'),
    (None, '4x'),
    ('scale_factor', 'i'),
    ('waven_begin_i', 'i'),
    ('waven_begin_d', 'i'),
    ('waven_end_i', 'i'),
    ('waven_end_d', 'i'),
    ('date_block', '4s'),
    ('time_block', '4s'),
    (None, '16x'),
    ('sn_ratio', 'i'),
    (None, '36x'),
    ('aperture_id', 'i'),
    (None, '12x'),
    ('beamsplitter_id', 'i'),
    (None, '152x'),
    ('laserf_i', 'i'),
    ('laserf_d', 'i'),
    (None, '32x'),
    ('filter_id', 'i'),
    (None, '124x'),
    ('source_id', 'i'),
    (None, '348x'),
    ('resolution_i', 'i'),
    ('resolution_d', 'i'),
    (None, '92x'),
    ('correction_factor', 'f'),
    ('sun_elevation', 'f'),
    (None, '124x')
)


spec_header_ffmt = (
    ('n_records', 'i'),
    ('created_pc', '20s'),
    ('modified_pc', '20s'),
    ('created_hp1000', '20s'),
    ('modified_hp1000', '20s'),
    (None, '44x')
)


spec_record_ffmt = (
    ('name', '12s'),
    ('hour_begin', 'f'),
    ('hour_end', 'f'),
    ('hour_avg', 'f'),
    ('sun_elevation', 'f'),
    ('air_mass', 'f'),
    ('mec_velocity', 'h'),
    ('filter_io_ratio', 'h'),
    ('sampling_frequency', 'i'),
    (None, '2x'),
    ('n_points_itf', 'h'),
    ('n_points_fft', 'h'),
    ('source_id', 'h'),
    ('detector_id', 'h'),
    ('beamsplitter_id', 'h'),
    ('filter_id', 'h'),
    ('n_scan_forward', 'h'),
    ('n_scan_backward', 'h'),
    ('sn_ratio', 'h'),
    ('aperture', 'f'),
    ('detector_potential', 'h'),
    ('resistance', 'h'),
    ('tape_id', 'h'),
    ('max_transmittance', 'f'),
    ('band_id', 'h'),
    ('rms_noise', 'f'),
    ('year_avg', 'h'),
    ('dayofyear_avg', 'h'),
    ('year_begin', 'h'),
    ('dayofyear_begin', 'h'),
    ('year_end', 'h'),
    ('dayofyear_end', 'h'),
    (None, '2x'),
    ('quality', '2s'),
    (None, '2x'),
    ('temperature', 'h'),
    ('pressure', 'h'),
    ('relative_humidity', 'c'),
    ('tropopause_height', 'c'),
    ('wavenumber_begin', 'f'),
    ('wavenumber_end', 'f'),
    ('n_points', 'i'),
    ('resolution', 'f'),
    ('wavenumber_step', 'd')
)


rinsland_header_regex = (
    "(?P<spec_type>[A-Z]{3})-"
    "(?P<name>[\w.]{12}) "
    "(?P<date>[\w ]{11})  "
    "(?P<resolution>[\d.]+)mK "
    "(?P<aperture>[\d.]+) mm "
    "Ap.ZA=(?P<zenith_angle>[\d.]+) "
    "S/N=(?P<sn_ratio>[\d ]+) "
    "h=(?P<hour_avg>[\d.]+)"
)


rinsland_header_ftype = {
    'spec_type': str, 'name': str,
    'date': lambda d: datetime.strptime(d, '%d %b %Y'),
    'resolution': float, 'aperture': float,
    'zenith_angle': float, 'sn_ratio': int,
    'hour_avg': float
}


rinsland_datahdr_ffmt = (
    ('wavenumber_begin', 'd'),
    ('wavenumber_end', 'd'),
    ('wavenumber_step', 'd'),
    ('n_points', 'i')
)

#! /usr/bin/env python2
# coding:UTF-8

#    Copyright 2006 Tibor Csernay

#    This file is part of SuperPatient.

#    SuperPatient is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.

#    SuperPatient is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with SuperPatient; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from .customization import BVR


def bvr_checksum(n):
    s = 0
    for i in str(n):
        s = [0, 9, 4, 6, 8, 2, 7, 1, 3, 5][(s+ord(i)-ord('0')) % 10]
    return (10-s) % 10


def alpha_to_num(char):
    return (ord(char) - ord('A')) % 100


def gen_bvr_ref(cursor, key_one, key_two, date):
    cursor.execute("UPDATE bvr_sequence SET counter = @counter := counter + 1")
    cursor.execute("SELECT @counter")
    bvr_counter, = cursor.fetchone()
    bv_ref = '%06d%010d%02d%02d%02d%04d' % (BVR.prefix, bvr_counter, alpha_to_num(key_one[0]), alpha_to_num(key_two[0]), date.month, date.year)
    return bv_ref + str(bvr_checksum(bv_ref))

#! /usr/bin/env python2
# coding:UTF-8


from bp_custo import bvr


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
    bv_ref = u'%06d%010d%02d%02d%02d%04d' % (bvr.prefix, bvr_counter, alpha_to_num(key_one[0]), alpha_to_num(key_two[0]), date.month, date.year)
    return bv_ref + str(bvr_checksum(bv_ref))

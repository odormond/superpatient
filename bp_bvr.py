#! /usr/bin/env python2
# coding:UTF-8


def bvr_checksum(n):
    s = 0
    for i in str(n):
        s = [0, 9, 4, 6, 8, 2, 7, 1, 3, 5][(s+ord(i)-ord('0')) % 10]
    return (10-s) % 10

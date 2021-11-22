# Copyright (c) 2021 by ERIGrid 2.0. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

def clamp(a, x, b):
    """
    Ensures x lies in the closed interval [a, b]
    :param a:
    :param x:
    :param b:
    :return:
    """
    if x > a:
        if x < b:
            return x
        else:
            return b
    else:
        return a

def log_mean(T_hi, T_lo, exact=False):
    """
    compute the logarithmic mean
    """
    if exact:
        from numpy import log
        return (T_hi-T_lo)/log(T_hi/T_lo)
    else:
        d = T_hi - T_lo
        return T_hi - d/2*(1 + d/6/T_hi*(1 + d/2/T_hi))  # third order taylor expansion


def safediv(a, b, tol=1e-6):
    if b == 0:
        return 0
    else:
        return a/b

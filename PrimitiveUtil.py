#!/usr/bin/python
########################################################################################################################
#
# Copyright (c) 2014, Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################################################################

"""
Utility functions
"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

import numpy as np

# TODO: yaml (refer to GridDB.py), skill, matplotlib export
# TODO: path, label support

#aux functions
def format_float(value, res):
    """
    Format float numbers for pretty printing

    Parameters
    ----------
    value : float
        number to be printed
    res : float
        resolution

    Returns
    -------
    str
    """
    precision = int(np.log10(1 / res)) + 1
    fstr = "%." + str(precision) + "f"
    return fstr % value

def Mt(transform):
    """
    Get transform matrix

    Parameters
    ----------
    transform : str
        transform parameter. possible values are 'R0', 'MX', 'MY', 'MXY', and 'R180'

    Returns
    -------
    np.array([[int, int], [int, int]])
        transform matrix
    """
    if transform=='R0':
        return np.array([[1, 0], [0, 1]])
    if transform=='MX':
        return np.array([[1, 0], [0, -1]])
    if transform=='MY':
        return np.array([[-1, 0], [0, 1]])
    if transform=='MXY': #mirror to y=x line
        return np.array([[0, 1], [1, 0]])
    if transform=='R180':
        return np.array([[-1, 0], [0, -1]])

def Mtinv(transform):
    """
    Get inverse of transform matrix

    Parameters
    ----------
    transform : str
        transform parameter. possible values are 'R0', 'MX', 'MY', 'MXY', and 'R180'

    Returns
    -------
    np.array([[int, int], [int, int]])
        inverse of transform matrix
    """
    if transform=='R0':
        return np.array([[1, 0], [0, 1]])
    if transform=='MX':
        return np.array([[1, 0], [0, -1]])
    if transform=='MY':
        return np.array([[-1, 0], [0, 1]])
    if transform=='MXY': #mirror to y=x line
        return np.array([[0, 1], [1, 0]])
    if transform=='R180':
        return np.array([[-1, 0], [0, -1]])

def Md(direction):
    """
    Get direction/projection matrix

    Parameters
    ----------
    direction : str
        direction/projection parameter. Possible values are 'left', 'right', 'top', 'bottom', 'omni', 'x', 'y'.

    Returns
    -------
    np.array([[int, int], [int, int]])
        directional matrix
    """
    if direction== 'left':
        return np.array([[-1, 0], [0, 0]])
    if direction== 'right':
        return np.array([[1, 0], [0, 0]])
    if direction== 'top':
        return np.array([[0, 0], [0, 1]])
    if direction== 'bottom':
        return np.array([[0, 0], [0, -1]])
    if direction== 'omni':
        return np.array([[1, 0], [0, 1]])
    if direction== 'x':
        return np.array([[1, 0], [0, 0]])
    if direction== 'y':
        return np.array([[0, 0], [0, 1]])

def locate_xy(xy0, xy1, location):
    """
    Find a corresponding xy coordinate from location parameters 

    Parameters
    ----------
    xy0 : np.array([float, float])
        first coordinate
    xy1 : np.array([float, float])
        second coordinate
    location : str
        direction/projection parameter. Possible values are 'lowerLeft', 'upperRight', 'centerCenter', ...

    Returns
    -------
    np.array([float, float])
        resulting coordinate
    """
    if location == 'lowerLeft':
        return np.array(xy0)
    if location == 'lowerRight':
        return np.array([xy1[0], xy0[1]])
    if location == 'upperLeft':
        return np.array([xy0[0], xy1[1]])
    if location == 'upperRight':
        return np.array(xy1)
    if location == 'centerCenter':
        return np.array(0.5*xy0+0.5*xy1)

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
The GridLayoutGenerator2 module implements GridLayoutGenerator2 class, which is an upgraded version of
GridLayoutGenerator, with experimental & improved features. No backward compatibility.

Example
-------
For layout export, type below command in ipython console.

    $ run laygo/labs/lab2_b_gridlayoutgenerator_layoutexercise.py
"""

__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

#from .BaseLayoutGenerator import *
from .GridLayoutGenerator import *
from .TemplateDB import *
from .GridDB import *
from . import PrimitiveUtil as ut
import numpy as np
import logging

#TODO: support path routing

class GridLayoutGenerator2(GridLayoutGenerator):
    """
    The GridLayoutGenerator2 class implements functions and variables for full-custom layout generations on abstract
    grids.

    Parameters
    ----------
    physical_res : float
        physical grid resolution
    config_file : str
        laygo configuration file path
    templates : laygo.TemplateDB.TemplateDB
        template database
    grids : laygo.GridDB.GridDB
        grid database
    layers: dict
        layer dictionary. metal, pin, text, prbnd are used as keys
    """

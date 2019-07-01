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

'''Template Object'''
__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

import numpy as np

class TemplateObject():
    """Layout object class"""
    name = None
    """str: template name"""
    xy = np.array([[0, 0], [0, 0]])
    """np.array([[float, float], [float, float]]): template bBox"""

    @property
    def height(self):
        """float: template height"""
        return abs(self.xy[0][1]-self.xy[1][1])

    @property
    def width(self):
        """float: template width"""
        return abs(self.xy[0][0]-self.xy[1][0])

    @property
    def size(self):
        """np.array([float, float]): template size"""
        return np.array([self.width, self.height])

    def __init__(self, name, xy, pins):
        """
        Constructor

        Parameters
        ----------
        name : str
            object name
        xy : np.ndarray
            coordinate array
        pins : dict()
            pin array
        """
        self.name = name
        self.xy = xy
        self.pins=pins

    def display(self):
        """Display object information"""
        print(" xy:" +str(np.around(self.xy, decimals=10).tolist())+ " pins:" +str(self.pins))

    def export_dict(self):
        """Export object information"""
        export_dict={#'xy':np.around(self.xy, decimals=10).tolist(),
                     'xy0':np.around(self.xy[0,:], decimals=10).tolist(),
                     'xy1':np.around(self.xy[1,:], decimals=10).tolist(),
                     'pins':dict()}
        for pname, p in self.pins.items():
            from copy import deepcopy
            export_dict['pins'][pname]={'netname':p['netname'], 'layer':deepcopy(p['layer']), 'xy0':np.around(p['xy'][0,:], decimals=10).tolist(),
                                                            'xy1':np.around(p['xy'][1,:], decimals=10).tolist(),}
        return export_dict

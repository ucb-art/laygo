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
The LayoutObjectArray module implements array classes for various layout objects.
"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

import numpy as np
#from laygo.LayoutObject import *
#from laygo import PrimitiveUtil as ut
from .LayoutObject import *
from . import PrimitiveUtil as ut


class LayoutObjectArray(np.ndarray):
    """Layout object array class"""
    name = None
    """str: Object name"""

    res = 0.005
    """float: Physical grid resolution"""

    _xy = np.zeros((2), dtype=np.int)
    """np.array([int, int]): Internal variable for xy coordinate (normalized to res)"""
    def get_xy(self): return self._xy * self.res
    def set_xy(self, value): self._xy = np.array(np.round(np.asarray(value) / self.res), dtype=np.int)
    xy = property(get_xy, set_xy)
    """np.array([float, float]): Object xy physical coordinate"""

    def get_shape(self): return np.asarray(super(LayoutObjectArray, self).shape)
    shape = property(get_shape)
    #"""np.array([int, int]): array shape. Overwrites ndarray.shape"""

    def __new__(cls, input_array, name=None):
        """
        Constructor for ndarray subclasses - check NumPy manual for details

        Parameters
        ----------
        input_array : np.ndarray
            Array of LayoutObject.LayoutObject
        name : str
            object name. If None, input_array.item(0).name is used.
        """
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        if name is None:
            obj.name = input_array.item(0).name
        else:
            obj.name = name
        obj.res = input_array.item(0).res
        obj.xy = input_array.item(0).xy
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        """
        Array finalizing function for subclassing ndarray - check NumPy manual for details
        """
        if obj is None: return
        # name
        self.name = getattr(obj, 'name', None)
        self.res = self.item(0).res
        self.xy = self.item(0).xy

    def display(self):
        """Display object information"""
        xystr = "[" + ut.format_float(self.xy[0], self.res) + ", " + ut.format_float(self.xy[1], self.res) + "]"
        print("  " + self.name + " " + self.__class__.__name__ + " xy:" + xystr)

class InstanceArray(LayoutObjectArray):
    """Instance object array class"""
    libname = None
    """str: library name"""

    cellname = None
    """str: cell name"""

    _spacing = np.zeros((2), dtype=np.int)
    """internal variable for spacing"""
    def get_spacing(self): return self._spacing * self.res
    def set_spacing(self, value): self._spacing = np.array(np.round(value / self.res), dtype=np.int)
    spacing = property(get_spacing, set_spacing)
    """Array spacing (actually this is a pitch, but I just followed GDS's notations)"""

    transform = 'R0'
    """str: transform parameter"""
    template = None
    """TemplateObject.TemplateObject: original template object"""
    pins = None
    """dict(): pin dictionary"""
    pointers = dict()
    """dict(): pointer dictionary"""
    #frequenctly used pointers
    left = None
    right = None
    top = None
    bottom = None
    bottom_left = None
    bottom_right = None
    top_left = None
    top_right = None

    @property
    def xy0(self):
        return self.xy
    """np.array([float, float]): Object location"""

    @property
    def xy1(self):
        if self.template is None:
            return self.xy
        else:
            return self.xy + np.dot(self.template.xy[1] * self.shape, ut.Mt(self.transform).T)
    """np.array([float, float]): the opposite corner of xy (or xy0)"""

    @property
    def bbox(self):
        """[[float, float], [float, float]]: instance bounding box in physical coordinate"""
        i = self
        t = self.template
        if t == None:  # no template
            return (np.array([i.xy, i.xy]))
        else:
            if i.transform == 'R0':
                orgn = i.xy + t.xy[0]
                return np.vstack((orgn, orgn + t.size * i.shape))
            if i.transform == 'MX':
                orgn = i.xy + t.xy[0] * np.array([1, -1])
                return np.vstack(
                    (orgn + t.size * np.array([0, -1]) * i.shape, orgn + t.size * np.array([1, 0]) * i.shape))
            if i.transform == 'MY':
                orgn = i.xy + t.xy[0] * np.array([-1, 1])
                return np.vstack(
                    (orgn + t.size * np.array([-1, 0]) * i.shape, orgn + t.size * np.array([0, 1]) * i.shape))
            if i.transform == 'MXY':
                orgn = i.xy + t.xy[0] * np.array([-1, -1])
                return np.vstack(
                    (orgn + t.size * np.array([0, 1]) * i.shape, orgn + t.size * np.array([1, 0]) * i.shape))
            if i.transform == 'R180':
                orgn = i.xy + t.xy[0] * np.array([-1, -1])
                return np.vstack((orgn + t.size * np.array([-1, -1]) * i.shape, orgn))
        return np.array([i.xy, i.xy])

    def __new__(cls, input_array, name=None):
        """
        Constructor

        Parameters
        ----------
        input_array : np.ndarray
            Array of LayoutObject.Instance
        name : str
            object name
        """
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = LayoutObjectArray.__new__(cls, input_array, name).view(cls)
        # add the new attribute to the created instance
        if name is None:
            obj.name = input_array.item(0).name
        else:
            obj.name = name
        obj.res = input_array.item(0).res
        obj.xy = input_array.item(0).xy
        obj.libname = input_array.item(0).libname
        obj.cellname = input_array.item(0).cellname
        if input_array.size > 1:
            obj.spacing = np.asarray(input_array.item(1).xy - input_array.item(0).xy)
        else:
            obj.spacing = np.array([0, 0])
        obj.transform = input_array.item(0).transform
        obj.template = input_array.item(0).template

        #pins and pointers
        if not obj.template is None:
            # crate pointer dictionary
            obj.pointers['left'] = Pointer(name='left', res=obj.res, xy=[0, 0.5], type='boundary', master=obj)
            obj.pointers['right'] = Pointer(name='right', res=obj.res, xy=[1, 0.5], type='boundary', master=obj)
            obj.pointers['bottom'] = Pointer(name='bottom', res=obj.res, xy=[0.5, 0], type='boundary', master=obj)
            obj.pointers['top'] = Pointer(name='top', res=obj.res, xy=[0.5, 1], type='boundary', master=obj)
            obj.pointers['bottom_left'] = Pointer(name='bottom_left', res=obj.res, xy=[0, 0], type='boundary', master=obj)
            obj.pointers['bottom_right'] = Pointer(name='bottom_right', res=obj.res, xy=[1, 0], type='boundary', master=obj)
            obj.pointers['top_left'] = Pointer(name='top_left', res=obj.res, xy=[0, 1], type='boundary', master=obj)
            obj.pointers['top_right'] = Pointer(name='top_right', res=obj.res, xy=[1, 1], type='boundary', master=obj)
            obj.left = obj.pointers['left']
            obj.right = obj.pointers['right']
            obj.bottom = obj.pointers['bottom']
            obj.top = obj.pointers['top']
            obj.bottom_left = obj.pointers['bottom_left']
            obj.bottom_right = obj.pointers['bottom_right']
            obj.top_left = obj.pointers['top_left']
            obj.top_right = obj.pointers['top_right']

            # create pin dictionary
            obj.pins = dict()
            for pn, p in obj.template.pins.items():
                elements = np.empty(obj.shape, dtype=Pin) #copy the shape of obj
                for i, o in np.ndenumerate(obj):
                    _xy = p['xy'] + o.xy - obj.xy
                    pin = Pin(name=pn, res=obj.res, xy=_xy, netname=p['netname'], layer=p['layer'], master=o)
                    elements[i]=pin
                obj.pins[pn] = elements

        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        """
        Array finalizing function for subclassing ndarray - check NumPy manual for details
        """
        #obj = LayoutObjectArray.__array_finalize__(self, obj)

        if obj is None: return
        # name
        self.name = getattr(obj, 'name', None)
        self.res = self.item(0).res
        self.xy = self.item(0).xy
        self.libname = getattr(obj, 'libname', None) #input_array.item(0).libname
        self.cellname = getattr(obj, 'cellname', None) #input_array.item(0).cellname
        if self.size > 1:
            self.spacing = np.asarray(self.item(1).xy - self.item(0).xy)
        else:
            self.spacing = np.array([0, 0])
        self.transform = getattr(obj, 'transform', None)
        self.template = getattr(obj, 'template', None)

        # elements for backward compatibility
        self.elements = self

        # pins and pointers
        if not self.template is None:
            # crate pointer dictionary
            self.pointers['left'] = Pointer(name='left', res=self.res, xy=[0, 0.5], type='boundary', master=self)
            self.pointers['right'] = Pointer(name='right', res=self.res, xy=[1, 0.5], type='boundary', master=self)
            self.pointers['bottom'] = Pointer(name='bottom', res=self.res, xy=[0.5, 0], type='boundary', master=self)
            self.pointers['top'] = Pointer(name='top', res=self.res, xy=[0.5, 1], type='boundary', master=self)
            self.pointers['bottom_left'] = Pointer(name='bottom_left', res=self.res, xy=[0, 0], type='boundary',
                                                  master=self)
            self.pointers['bottom_right'] = Pointer(name='bottom_right', res=self.res, xy=[1, 0], type='boundary',
                                                   master=self)
            self.pointers['top_left'] = Pointer(name='top_left', res=self.res, xy=[0, 1], type='boundary', master=self)
            self.pointers['top_right'] = Pointer(name='top_right', res=self.res, xy=[1, 1], type='boundary', master=self)
            self.left = self.pointers['left']
            self.right = self.pointers['right']
            self.bottom = self.pointers['bottom']
            self.top = self.pointers['top']
            self.bottom_left = self.pointers['bottom_left']
            self.bottom_right = self.pointers['bottom_right']
            self.top_left = self.pointers['top_left']
            self.top_right = self.pointers['top_right']

            # create pin dictionary
            self.pins = dict()
            for pn, p in self.template.pins.items():
                #self.pins[pn] = Pin(name=pn, res=self.res, xy=p['xy'], netname=p['netname'], layer=p['layer'], master=self)
                elements = np.empty(self.shape, dtype=Pin) #copy the shape of self
                for i, o in np.ndenumerate(self):
                    _xy = p['xy'] + o.xy - self.xy
                    pin = Pin(name=pn, res=self.res, xy=_xy, netname=p['netname'], layer=p['layer'], master=o)
                    elements[i] = pin
                self.pins[pn] = elements

    def display(self):
        """Display object information"""
        xystr = "[" + ut.format_float(self.xy[0], self.res) + ", " + ut.format_float(self.xy[1], self.res) + "]"
        spacestr = "[" + ut.format_float(self.spacing[0], self.res) + ", " + ut.format_float(self.spacing[1], self.res) + "]"
        print("  [InstanceArray]" + self.name + " libname:" + self.libname + " cellname:" + self.cellname +
              " xy:" + xystr + " shape:" + str(self.shape.tolist()) +
              " spacing:" + spacestr + " transform:" + str(self.transform))

if __name__ == '__main__':
    #array instance
    inst_list = [Instance(name='I0', res=0.005, xy=[1.5 + 0.5 * i, -2.0], libname='ln', cellname='cn',
                          transform='R0', template=None) for i in range(5)]
    inst_arr = np.atleast_2d(inst_list).T
    obj = InstanceArray(input_array=inst_arr, name='I0')
    obj.display()

    #slicing
    v = obj[1:]
    v.display()

    #single instance
    inst_list = np.array([[Instance(name='I1', res=0.005, xy=[1.5, 0], libname='ln', cellname='cn',
                                    transform='R0', template=None)]])
    inst_arr = np.atleast_2d(inst_list).T
    obj2 = InstanceArray(input_array=inst_arr, name='I1')
    print(obj2, obj2.name, obj2.shape, obj2.res, obj2.xy)
    obj2.display()

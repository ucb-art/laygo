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
The LayoutObject module implements classes for various layout objects.
"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

import numpy as np
from . import PrimitiveUtil as ut

class LayoutObject():
    """Layout object class"""
    name = None
    """str: Object name"""

    res = 0.005
    """float: Physical grid resolution"""

    _xy = np.zeros((2), dtype=np.int)
    """np.array([int, int]): Object xy coordinate (normalized to res)"""

    def get_xy(self): return self._xy * self.res
    def set_xy(self, value): self._xy = np.array(np.round(value / self.res), dtype=np.int)
    xy = property(get_xy, set_xy)
    """np.array([float, float]): Object xy physical coordinate"""

    def __init__(self, name, res, xy):
        """
        Constructor

        Parameters
        ----------
        name : str
            object name
        res : float
            physicial grid resolution
        xy : np.ndarray
            coordinate array
        """
        self.name = name
        self.res = res
        self.xy = np.asarray(xy)

    def display(self):
        """Display object information"""
        print("  " + self.name + " xy:" + str(self.xy.tolist()))


class Rect(LayoutObject):
    """Rect object class"""
    layer = None
    """[str, str]: Rect layer"""

    netname = None
    """str: net name"""

    _xy = np.zeros((2, 2), dtype=np.int)
    """np.array([[int, int], [int, int]]): Object xy coordinate (normalized to res)"""

    def get_xy0(self): return self.xy[0]
    def set_xy0(self, value): self.xy[0] = np.asarray(value)
    xy0 = property(get_xy0, set_xy0)
    """np.array([float, float]): lowerLeft coordinate of Rect"""

    def get_xy1(self): return self.xy[1]
    def set_xy1(self, value): self.xy[1] = np.asarray(value)
    xy1 = property(get_xy1, set_xy1)
    """np.array([float, float]): upperRight coordinate of Rect"""

    @property
    def height(self):
        """float: height of Rect"""
        return abs(self.xy0[1] - self.xy1[1])

    @property
    def width(self):
        """float: width of Rect"""
        return abs(self.xy0[0] - self.xy1[0])

    @property
    def size(self):
        """[float, float]: [width, height] of Rect"""
        return np.hstack((self.width, self.height))

    @property
    def cx(self):
        """float: x-center of Rect"""
        return 0.5 * (self.xy0[0] + self.xy1[0])

    @property
    def cy(self):
        """float: y-center of Rect"""
        return 0.5 * (self.xy0[1] + self.xy1[1])

    @property
    def center(self):
        """[float, float]: center coordinate of Rect"""
        return np.hstack((self.cx, self.cy))

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

    def __init__(self, name, res, xy, layer, netname):
        """
        Constructor

        Parameters
        ----------
        name : str
            object name
        res : float
            grid resolution
        xy : np.array([[x0, y0], [x1, y1]])
            xy coorinates
        layer : [layer, pupose]
            layer name and purpose
        netname : str
            net name
        """
        self.layer = layer
        self.netname = netname
        # crate pointers
        self.pointers['left'] = Pointer(name='left', res=res, xy=[0, 0.5], type='boundary', master=self)
        self.pointers['right'] = Pointer(name='right', res=res, xy=[1, 0.5], type='boundary', master=self)
        self.pointers['bottom'] = Pointer(name='bottom', res=res, xy=[0.5, 0], type='boundary', master=self)
        self.pointers['top'] = Pointer(name='top', res=res, xy=[0.5, 1], type='boundary', master=self)
        self.pointers['bottom_left'] = Pointer(name='bottom_left', res=res, xy=[0, 0], type='boundary', master=self)
        self.pointers['bottom_right'] = Pointer(name='bottom_right', res=res, xy=[1, 0], type='boundary', master=self)
        self.pointers['top_left'] = Pointer(name='top_left', res=res, xy=[0, 1], type='boundary', master=self)
        self.pointers['top_right'] = Pointer(name='top_right', res=res, xy=[1, 1], type='boundary', master=self)
        self.left = self.pointers['left']
        self.right = self.pointers['right']
        self.bottom = self.pointers['bottom']
        self.top = self.pointers['top']
        self.bottom_left = self.pointers['bottom_left']
        self.bottom_right = self.pointers['bottom_right']
        self.top_left = self.pointers['top_left']
        self.top_right = self.pointers['top_right']

        LayoutObject.__init__(self, name, res, xy)

    def display(self):
        """Display object information"""
        print("  [Rect]" + self.name + " layer:" + str(self.layer) +
              " xy:" + str(np.around(self.xy, decimals=10).tolist()) +
              " center:" + str(np.around(self.center, decimals=10).tolist()) +
              " size:" + str(np.around(self.size, decimals=10).tolist()))


class Pin(LayoutObject):
    """Pin object class"""
    layer = None
    """[str, str]: Pin layer"""
    netname = None
    """str: net name"""
    master = None
    """LayoutObject.Instance: master instance, only for instance pins"""
    elements = None
    """np.array([[Pin]]): array elements"""

    _xy = np.zeros((2, 2), dtype=np.int)
    """np.array([[int, int], [int, int]]): Object xy coordinate (normalized to res)"""

    def get_xy0(self): return self.xy[0]
    def set_xy0(self, value): self.xy[0] = np.asarray(value)
    xy0 = property(get_xy0, set_xy0)
    """np.array([float, float]): lowerLeft coordinate of Pin"""

    def get_xy1(self): return self.xy[1]
    def set_xy1(self, value): self.xy[1] = np.asarray(value)
    xy1 = property(get_xy1, set_xy1)
    """np.array([float, float]): upperRight coordinate of Pin"""

    elements = []
    """elements for pins of array instance"""

    pointers = dict()
    """dict(): pointer dictionary"""
    # frequenctly used pointers
    left = None
    right = None
    top = None
    bottom = None
    bottom_left = None
    bottom_right = None
    top_left = None
    top_right = None

    def __init__(self, name, res, xy, netname=None, layer=None, master=None):
        """
        Constructor

        Parameters
        ----------
        name : str
            object name
        res : float
            grid resolution
        xy : np.array([[x0, y0], [x1, y1]]), optional
            xy coorinates
        netname : str, optional
            net name. If None, name is used
        layer : [layer, pupose]
            layer name and purpose
        master : LayoutObject.Instance
            master instance handle
        """
        if netname is None:
            netname = name

        self.netname = netname
        self.layer = layer
        self.master = master
        # crate pointers
        self.pointers['left'] = Pointer(name='left', res=res, xy=[0, 0.5], type='boundary', master=self)
        self.pointers['right'] = Pointer(name='right', res=res, xy=[1, 0.5], type='boundary', master=self)
        self.pointers['bottom'] = Pointer(name='bottom', res=res, xy=[0.5, 0], type='boundary', master=self)
        self.pointers['top'] = Pointer(name='top', res=res, xy=[0.5, 1], type='boundary', master=self)
        self.pointers['bottom_left'] = Pointer(name='bottom_left', res=res, xy=[0, 0], type='boundary', master=self)
        self.pointers['bottom_right'] = Pointer(name='bottom_right', res=res, xy=[1, 0], type='boundary', master=self)
        self.pointers['top_left'] = Pointer(name='top_left', res=res, xy=[0, 1], type='boundary', master=self)
        self.pointers['top_right'] = Pointer(name='top_right', res=res, xy=[1, 1], type='boundary', master=self)
        self.left = self.pointers['left']
        self.right = self.pointers['right']
        self.bottom = self.pointers['bottom']
        self.top = self.pointers['top']
        self.bottom_left = self.pointers['bottom_left']
        self.bottom_right = self.pointers['bottom_right']
        self.top_left = self.pointers['top_left']
        self.top_right = self.pointers['top_right']

        LayoutObject.__init__(self, name, res, xy)

    def display(self):
        """Display object information"""
        print("  [Pin]" + self.name + " layer:" + str(self.layer) + " xy:" + str(self.xy.tolist()))


class Text(LayoutObject):
    """Text object class"""
    layer = None
    """[str, str]: Text layer"""
    text = None
    """str: text body"""

    def __init__(self, name, res, xy, layer, text):
        """
        Constructor

        Parameters
        ----------
        name : str
            object name
        res : float
            grid resolution
        xy : np.array([[x0, y0], [x1, y1]])
            xy coorinates
        layer : [layer, pupose]
            layer name and purpose
        text : str
            text entry
        """
        self.layer = layer
        self.text = text
        LayoutObject.__init__(self, name, res, xy)

    def display(self):
        """Display object information"""
        print("  [Text]" + self.name + " text:" + self.text +
              " layer:" + str(self.layer) + " xy:" + str(np.around(self.xy, decimals=10).tolist()))


class Pointer(LayoutObject):
    """Pointer class attached to other LayoutObjects"""
    master = None
    """LayoutObject.Instance: master instance that the tag is attached"""
    type = 'boundary' #Pointer type
    #boundary : boundary pointer of instances, name will be used for direction in relplace, xy will be used in route

    def __init__(self, name, res, xy, type='direction', master=None):
        """
        Constructor

        Parameters
        ----------
        name : str
            object name
        res : float
            grid resolution
        xy : np.array([x0, y0]), optional
            xy coorinates
        master : LayoutObject.Instance
            master instance handle
        """
        self.master = master
        self.type = type
        LayoutObject.__init__(self, name, res, xy)


class Instance(LayoutObject):
    """Instance object class"""

    libname = None
    """str: library name"""
    cellname = None
    """str: cell name"""
    shape = np.array([1, 1])
    """np.array([int, int]): array shape"""
    size = np.array([0, 0])
    """np.array([float, float]): instance size (valid only if its template is specified)"""
    _spacing = np.zeros((2), dtype=np.int)
    """Array spacing (actually this is a pitch, but I just followed GDS's notations)"""
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
    elements = None
    """np.array([[Instance]]): array elements"""
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
            return self.xy + np.dot(self.template.xy[1], ut.Mt(self.transform).T)
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

    def __init__(self, name, res, xy, libname, cellname, shape=np.array([1, 1]), spacing=np.array([0, 0]),
                 transform='R0', template=None):
        """
        Constructor

        Parameters
        ----------
        name : str
            object name
        res : float
            grid resolution
        xy : np.array([[x0, y0], [x1, y1], ...])
            xy coordinates
        libname : str
            library name
        cellname : str
            cell name
        shape : np.array([col, row])
            array size
        spacing : np.array([xspacing, yspacing])
            spacing between array elements
        transform : str
            transformal parameter
        template: TemplateObject
            template handle (if exist)
        force_elements_2darray: bool
            True if you want to force elements arrays to be 2-diminsional ones. Useful if you are generating a 2d array
            object and either of row and cols can be 1.
        """
        xy = np.asarray(xy)
        shape = np.asarray(shape)
        spacing = np.asarray(spacing)

        LayoutObject.__init__(self, name, res, xy)
        self.libname = libname
        self.cellname = cellname
        self.shape = shape
        self.spacing = spacing
        self.transform = transform
        self.template = template
        self.elements = np.array([])
        # create subelement list
        if not np.all(shape == np.array([1, 1])):
            elements = []
            #construct 2d elements array
            for i in range(shape[0]):
                elements.append([])
                for j in range(shape[1]):
                    _xy = xy + np.dot(spacing * np.array([i, j]), ut.Mt(transform).T)
                    inst = Instance(name=name, res=res, xy=_xy,
                                    libname=libname, cellname=cellname, shape=[1, 1], spacing=[0, 0],
                                    transform=transform, template=template)
                    elements[i].append(inst)
            self.elements = np.array(elements)
        else:
            self.elements = np.array([[self]])
        if not template is None:
            self.size = template.size
            # crate pointers
            self.pointers['left'] = Pointer(name='left', res=res, xy=[0, 0.5], type='boundary', master=self)
            self.pointers['right'] = Pointer(name='right', res=res, xy=[1, 0.5], type='boundary', master=self)
            self.pointers['bottom'] = Pointer(name='bottom', res=res, xy=[0.5, 0], type='boundary', master=self)
            self.pointers['top'] = Pointer(name='top', res=res, xy=[0.5, 1], type='boundary', master=self)
            self.pointers['bottom_left'] = Pointer(name='bottom_left', res=res, xy=[0, 0], type='boundary', master=self)
            self.pointers['bottom_right'] = Pointer(name='bottom_right', res=res, xy=[1, 0], type='boundary', master=self)
            self.pointers['top_left'] = Pointer(name='top_left', res=res, xy=[0, 1], type='boundary', master=self)
            self.pointers['top_right'] = Pointer(name='top_right', res=res, xy=[1, 1], type='boundary', master=self)
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
                self.pins[pn] = Pin(name=pn, res=res, xy=p['xy'], netname=p['netname'], layer=p['layer'], master=self)
                # create subelement lists for pins
                if not np.all(shape == np.array([1, 1])):
                    elements = []
                    for i in range(shape[0]):
                        elements.append([])
                        for j in range(shape[1]):
                            _xy = p['xy'] + np.dot(spacing * np.array([i, j]), ut.Mt(transform).T)
                            pin = Pin(name=pn, res=res, xy=_xy, netname=p['netname'], layer=p['layer'],
                                      master=self.elements[i, j])
                            elements[i].append(pin)
                    self.pins[pn].elements = np.array(elements)
                else:
                    self.pins[pn].elements = np.array([[self.pins[pn].elements]])

    def display(self):
        """Display object information"""
        print("  [Instance]" + self.name + " libname:" + self.libname + " cellname:" + self.cellname +
              " xy:" + str(self.xy.tolist()) + " shape:" + str(self.shape.tolist()) +
              " spacing:" + str(self.spacing.tolist()) + " transform:" + str(self.transform))


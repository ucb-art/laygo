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
The LayoutDB module implements layout database. The core database is constructed in dict (LayoutDB.design), and the
design dict contains all layout objects (instances, rects, pins, ...), instantiated as LayoutObject objects.
"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

from .LayoutObject import *
from .LayoutObjectArray import *
from math import log10
import numpy as np
#import yaml
import logging

class LayoutDB(dict):
    """
    Layout database class
    """
    design = None
    """dict: core database"""
    plib = None
    """str: current library handle"""
    pcell = None
    """str: current cell handle"""
    res = 0.005
    """float: physical grid resolution"""

    @property
    def res_exp(self):
        """int: exponent of laygo.LayoutDB.LayoutDB.res"""
        return int(log10(1/self.res)+1)

    def __init__(self, res=0.005):
        """
        Constructor

        Parameters
        ----------
        res : float
            physical resolution
        """
        #self.design = dict()
        self.design = self
        self.res = res

    # aux functions
    def display(self, libname=None, cellname=None):
        """
        Display the design database

        Parameters
        ----------
        libname : str, optional
            library name. If none, all libraries are displayed.
        cellname : str, optional
            cell name. If none, all cells are displayed.
        """
        if libname == None:
            libstr = ""
        else:
            libstr = "lib:" + libname + ", "
        if cellname == None:
            cellstr = ""
        else:
            cellstr = "cell:" + cellname
        print('Display ' + libstr + cellstr)
        if libname == None:
            liblist=self.keys()
        elif isinstance(libname, list):
            liblist=libname
        else:
            liblist=[libname]

        for ln in liblist:
            l=self[ln]
            print('[Library]' + ln)
            if cellname == None:
                celllist=l.keys()
            elif isinstance(cellname, list):
                celllist=cellname
            else:
                celllist=[cellname]
            for sn in celllist:
                s=l[sn]
                print(' [Cell]' + sn)
                for r in s['rects'].values(): r.display()
                for i in s['instances'].values(): i.display()
                for p in s['pins'].values(): p.display()
                for t in s['texts'].values(): t.display()

    def genid(self, type='instance', pfix='I', sfix='', max_index=100000):
        """
        Generate a unique id (name) for objects

        Parameters
        ----------
        type : str
            object type (instance, rect, path..)
        pfix : str
            prefix of the id
        sfix : str
            surfix of the id
        max_index : int
            maximum index

        Returns
        -------
        str
            unique object id (name)
        """
        n = 0
        trig = 0
        if not type + 's' in self[self.plib][self.pcell]:
            return pfix + str(0) + sfix
        while (n < max_index and trig == 0):
            id = pfix + str(n) + sfix
            if not id in self[self.plib][self.pcell][type + 's']:
                trig = 1
            n = n + 1
        if n == max_index:
            print('laygo.LayoutDB.LayoutDB.genid - overflow')
        return id

    # library and cell related functions
    def add_library(self, name):
        """
        Add a library to the design dictionary

        Parameters
        ----------
        name : str
            library name

        Returns
        -------
        dict
            added library dictionary
        """
        l = dict()
        self[name] = l
        return l

    def add_cell(self, name, libname=None):
        """
        Add a cell to the specified library

        Parameters
        ----------
        name : str
            cell name
        libname :
            library name (if None, self.plib is used)

        Returns
        -------
        dict
            added cell dictionary
        """
        if libname == None: libname = self.plib
        s = {'instances': dict(), 'rects': dict(), 'vias': dict(),
             'paths': dict(), 'pins': dict(), 'texts': dict()}
        self[libname][name] = s
        return s

    def sel_library(self, libname):
        """
        Select a library to work on

        Parameters
        ----------
        libname : str
            library name
        """
        self.plib = libname

    def sel_cell(self, cellname):
        """
        Select a cell to work on

        Parameters
        ----------
        cellname : str
            cellname
        """
        self.pcell = cellname

    # geometry related functions
    def add_rect(self, name, xy, layer, netname=None):
        """
        Add a rect to selected cell

        Parameters
        ----------
        name : str
            rect name
        xy : np.array([[float, float], [float, float]])
            xy coordinate
        layer : [str, str]
            layer name and purpose

        Returns
        -------
        laygo.LayoutObject.Rect
            added rect object
        """
        if name == None: name = self.genid(type='rect', pfix='R')
        xy = np.asarray(xy)
        r = Rect(name=name, res=self.res, xy=xy, layer=layer, netname=netname)
        self[self.plib][self.pcell]['rects'][name] = r
        logging.debug('Rect added - Name:' + r.name + ', layer:' + str(layer) + ', xy:' +
                      str(np.round(r.xy, self.res_exp).tolist()[0]))
        return r

    def add_pin(self, name, netname, xy, layer):
        """
        Add a pin to selected cell

        Parameters
        ----------
        name : str
            pin object name
        netname : str
            net name
        xy : [float, float]
            xy coordinate
        layer : [str, str]
            layer name and purpose

        Returns
        -------
        laygo.LayoutObject.Pin
            generated pin object
        """
        if name == None: name = self.genid(type='pin', pfix='P')
        xy = np.asarray(xy)
        p = Pin(name=name, res=self.res, xy=xy, netname=netname, layer=layer) #how to handle master?
        self[self.plib][self.pcell]['pins'][name] = p
        logging.debug('Pin added - Name:' + p.name + ', layer:' + str(layer) +
                      ', netname:' + p.netname + ', xy:' + str(p.xy.tolist()))
        return p

    def add_text(self, name, text, xy, layer):
        """
        Add a pin to selected cell

        Parameters
        ----------
        name : str
            pin object name
        text : str
            text string
        xy : [float, float]
            xy coordinate
        layer : [str, str]
            layer name and purpose

        Returns
        -------
        laygo.LayoutObject.Text
            generated text object
        """
        if name == None: name = self.genid(type='text', pfix='T')
        xy = np.asarray(xy)
        t = Text(name=name, res=self.res, xy=xy, text=text, layer=layer)
        self[self.plib][self.pcell]['texts'][name] = t
        logging.debug('Text added - Name:' + t.name + ', layer:' + str(layer) +
                      ', text:' + t.text + ', xy:' + str(np.round(t.xy, self.res_exp).tolist()))
        return t

    def add_inst(self, name, libname, cellname, xy=np.array([0, 0]), shape=None, spacing=np.array([0, 0]),
                 transform='R0', template=None, use_array=False):
        """
        Add an instance to the specified library and cell (_plib, _pstr)

        Parameters
        ----------
        name : str
            instance name
        libname : str
            cell library name (not output library)
        cellname : str
            cell name
        xy : np.array([float, float])
            xy coordinate
        shape : np.array([x0, y0])
            array shape parameter
        spacing : np.array([x0, y0])
            array spacing parameter
        transform : str
            transform parameter
        template : laygo.TemplateObject.TemplateObject
            template handle
        use_array : boolean
            temporarily used. If true, InstanceArray is used instead of Instance (introduced for backward compatibility.)

        Returns
        -------
        laygo.LayoutObject.Instance
            instance object
        """
        if name is None: name = self.genid(type='instance', pfix='I')
        xy = np.asarray(xy)
        if shape is None:
            _shape = np.array([1, 1])
        else:
            _shape = np.asarray(shape)
        spacing = np.asarray(spacing)
        if isinstance(xy, list): xy = np.array(xy)
        if (use_array is False) or (shape is None):
            i = Instance(name=name, res=self.res, xy=xy, libname=libname, cellname=cellname, shape=_shape,
                         spacing=spacing, transform=transform, template=template)
        else:
            i_list = []
            for idx_x in range(_shape[0]):
                i_row = []
                for idx_y in range(_shape[1]):
                    #xy = xy + np.dot(spacing * np.array([idx_x, idx_y]), ut.Mt(transform).T)
                    _xy = xy + np.dot(spacing * np.array([idx_x, idx_y]), ut.Mt(transform).T)
                    i_row += [Instance(name=name, res=self.res, xy=_xy, libname=libname, cellname=cellname,
                                       transform=transform, template=template)]
                i_list += [i_row]
            #print(shape, np.array(i_list))
            i = InstanceArray(input_array=np.array(i_list), name=name)
        self[self.plib][self.pcell]['instances'][name] = i
        logging.debug('Instance added - Name:' + name + ', lib:' + libname +
                      ', cell:' + cellname + ', xy:' + str(np.round(i.xy, self.res_exp).tolist()))
        return i

    def get_rect(self, name, libname=None):
        """
        Get rect object

        Parameters
        ----------
        name : str
            rect name
        libname : str
            libname. if None, self.db._plib is used

        Returns
        -------
        laygo.LayoutObject.Rect
        """
        if libname==None: libname=self.plib
        return self[libname][self.pcell]['rects'][name]

    def get_inst(self, name=None, libname=None, index=np.array([0, 0])):
        """
        Get instance object

        Parameters
        ----------
        name : str
            instance name, if none, all instance is returned
        libname : str
            libname. if None, self.db._plib is used

        Returns
        -------
        laygo.LayoutObject.Instancce
        """
        #TODO: implement index handling
        if libname==None: libname=self.plib
        if name==None:
            return self[libname][self.pcell]['instances']
        else:
            return self[libname][self.pcell]['instances'][name]

    def get_pin(self, name, libname=None):
        """
        Get pin object

        Parameters
        ----------
        name : str
            pin name
        libname : str
            libname. if None, self.db._plib is used

        Returns
        -------
        laygo.LayoutObject.Pin
        """
        if libname==None: libname=self.plib
        return self[libname][self.pcell]['pins'][name]

    def merge(self, db):
        """
        Merge a LayoutDB object to self.db

        Parameters
        ----------
        db : laygo.LayoutDB.LayoutDB
            layout database to be merged to self.db
        """
        for ln, l in db.items():
            if not ln in self:
                self.add_library(ln)
            self.sel_library(ln)
            for sn, s in l.items():
                if not sn in self[ln]:
                    self.add_cell(sn, ln)
                self.sel_cell(sn)
                for r in s['rects'].values():
                    #print(r.name,r.xy,r.layer,r.netname)
                    self.add_rect(r.name,r.xy,r.layer,r.netname)
                for i in s['instances'].values():
                    self.add_inst(i.name, i.libname, i.cellname, i.xy, i.shape, i.spacing, i.transform)
                for t in s['texts'].values():
                    self.add_text(t.name, t.text, t.xy, t.layer)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    workinglib = 'laygo_working'
    utemplib = 'laygo_microtemplates'

    metal=[['metal0', 'donotuse'],
           ['metal1', 'drawing'],
           ['metal2', 'drawing'],
           ['metal3', 'drawing'],
           ['metal4', 'drawing'],
           ['metal5', 'drawing']]
    mpin=[['text', 'drawing'],
          ['metal1', 'pin'],
          ['metal2', 'pin'],
          ['metal3', 'pin'],
          ['metal4', 'pin'],
          ['metal5', 'pin']]
    text=['text', 'drawing']

    laydb = LayoutDB()
    laydb._res = 0.005
    laydb.add_library(workinglib)
    laydb.sel_library(workinglib)

    mycell = '_generated_example_1'
    laydb.add_cell(mycell)
    laydb.sel_cell(mycell)
    laydb.add_rect(None, np.array([[0, 0], [0.1, 0.01]]), metal[1])
    laydb.add_rect(None, np.array([[[0, 0], [0.01, 0.1]], [[0.1, 0], [0.11, 0.1]]]), metal[2])
    mycell2 = '_generated_example_2'
    laydb.add_cell(mycell2)
    laydb.sel_cell(mycell2)
    laydb.add_inst(None, workinglib, mycell, xy=np.array([0.2, 0.2]), shape=np.array([0, 0]),
                   spacing=np.array([0, 0]), transform='R0')
    laydb.add_inst(None, workinglib, mycell, xy=np.array([0, 0.2]), shape=np.array([2, 3]),
                   spacing=np.array([0.1, 0.2]), transform='R0')
    laydb.add_inst(None, workinglib, mycell, xy=np.array([[0.8, 0], [0.8, 0.4]]), shape=np.array([0, 0]),
                   spacing=np.array([0.1, 0.2]), transform='R0')
    laydb.add_pin(None, netname='net0', xy=np.array([[0, 0], [0.01, 0.01]]), layer=mpin[1])
    laydb.add_text(None, 'text0', np.array([0.1, 0.1]), text)

    laydb.display()

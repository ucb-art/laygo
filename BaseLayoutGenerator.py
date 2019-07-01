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
The BaseLayoutGenerator module implements classes to generate full-custom layout on physical grid. It allows designers
to describe layout generation scripts in Python language and automate the layout process. BaseLayoutGenerator is not
capable of handling any abstracted grid/template parameters, so all parameters should be given in real numbers

Example
-------
For layout export, type below command in ipython console.

    $ run laygo/labs/lab1_a_baselayoutgenerator_export.py
"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

from . import LayoutIO
from . import PrimitiveUtil
from .LayoutDB import *
import numpy as np

class BaseLayoutGenerator():
    """
    The BaseLayoutGenerator class implements functions and variables for full-custom layout generations on physical
    grids.

    Parameters
    ----------
    res : float
        physical grid resolution
    """

    db = LayoutDB()
    """laygo.LayoutDB.LayoutDB: layout database"""
    use_array = False
    """boolean: True if InstanceArray is used instead of Instance. For GridLayoutGenerator2 only"""

    @property
    def res(self):
        """float: physical resolution"""
        return self.db.res
    
    @res.setter
    def res(self, value):
        """float: physical resolution"""
        self.db.res=value

    def __init__(self, res=0.005):
        """Constructor"""
        self.db=LayoutDB(res=res)

    # auxiliary functions
    def display(self, libname=None, cellname=None):
        """
        Display DB information.

        Parameters
        ----------
        libname : str, optional
            library name
        cellname : str, optional
            cell name
        """
        self.db.display(libname, cellname)

    # library and cell related functions
    def add_library(self, name, select=True):
        """
        Create a library to work on.

        Parameters
        ----------
        name : str
            library name
        select : bool, optional
            if True, automatically select the library to work on after creation
        """
        self.db.add_library(name)
        if select is True:
            self.sel_library(name)

    def add_cell(self, name, libname=None, select=True):
        """
        Create a cell to work on.

        Parameters
        ----------
        name : str
            cellname
        libname : str, optional
            library name. If None, current selected library name is used.
        select : bool, optional
            if True, automatically select the cell to work on after creation.
        """
        self.db.add_cell(name, libname)
        if select is True:
            self.sel_cell(name)

    def sel_library(self, name):
        """
        Select a library to work on.

        Parameters
        ----------
        libname : str
            library name
        """
        self.db.sel_library(name)

    def sel_cell(self, cellname):
        """
        Select a cell to work on.

        Parameters
        ----------
        cellname : str
            cell name
        """
        self.db.sel_cell(cellname)

    # geometry related functions
    def add_rect(self, name, xy, layer, netname=None):
        """
        Add a rect to selected region.

        Parameters
        ----------
        name : str
            rect name
        xy : np.array([[float, float], [float, float]])
            xy coordinates
        layer : [str, str]
            layer name an purpose

        Returns
        -------
        laygo.LayoutObject.Rect
            created Rect object
        """
        return self.db.add_rect(name, xy, layer, netname)

    def add_pin(self, name, netname, xy, layer):
        """
        Add a pin to specified region.

        Parameters
        ----------
        name : str
            pin object name
        netname : str
            net name
        xy : np.array([[float, float], [float, float]])
            xy coordinates
        layer : [str, str]
            layer name and purpose

        Returns
        -------
        laygo.LayoutObject.Pin
            created Pin object
        """
        return self.db.add_pin(name, netname, xy, layer)

    def add_text(self, name, text, xy, layer):
        """
        Add a text to specified coordinate.

        Parameters
        ----------
        name : str
            pin object name
        text : str
            text string
        xy : [float, float]
            xy coordinate
        layer : [layername, purpose]
            layer name an purpose

        Returns
        -------
        laygo.LayoutObject.Text
            created Text object
        """
        return self.db.add_text(name, text, xy, layer)

    def add_inst(self, name, libname, cellname, xy=None, shape=None, spacing=np.array([0, 0]),
                 transform='R0', template=None):
        """
        Add an instance to specified coordinate.

        Parameters
        ----------
        name : str
            instance name
        libname : str
            cell library name (not output library name)
        cellname : str
            cellname
        xy : np.array([float, float])
            xy coordinate
        shape : np.array([x0, y0]) or None
            array shape parameter. If None, the instance is not considered as array
        spacing : np.array([x0, y0])
            array spacing parameter
        transform : str
            transform parameter
        template : laygo.TemplateObject.TemplateObject
            template handle

        Returns
        -------
        laygo.LayoutObject.Instance
            created Instance object
        """
        return self.db.add_inst(name, libname, cellname, xy, shape, spacing, transform, template, use_array=self.use_array)

    # access functions
    def get_rect(self, name, libname=None):
        """
        Get the handle of specified rect object.

        Parameters
        ----------
        name : str
            rect name
        libname : str
            libname. if None, self.db._plib is used

        Returns
        -------
        laygo.LayoutObject.Rect
            Rect object pointer
        """
        return self.db.get_rect(name, libname)

    def get_inst(self, name=None, libname=None, index=np.array([0, 0])):
        """
        Get the handle of specified instance object.

        Parameters
        ----------
        name : str, optional
            instance name, if None, all instances are returned.
        libname : str, optional
            libname. if None, self.db._plib is used.

        Returns
        -------
        laygo.LayoutObject.Instance
            Instance object pointer
        """
        return self.db.get_inst(name, libname, index)

    def get_pin(self, name, libname=None):
        """
        Get the handle of speficied pin object.

        Parameters
        ----------
        name : str
            pin name
        libname : str, optional
            libname. if None, self.db._plib is used.

        Returns
        -------
        laygo.LayoutObject.Pin
            Pin object pointer
        """
        return self.db.get_pin(name, libname)

    # db I/O functions
    def export_GDS(self, filename, libname=None, cellname=None, layermapfile="default.layermap", physical_unit=1e-9,
                   logical_unit=0.001, pin_label_height=0.0001, text_height=0.0001, annotate_layer = ['text', 'drawing'],
                   annotate_height = 0.01):
        """
        Export specified cell(s) to a GDS file.

        Parameters
        ----------
        filename : str
            output filename
        layermapfile : str
            layermap filename
        physical_unit : float
            physical unit for GDS export
        logical_unit : float
            logical unit for GDS export
        pin_label_height : float
            pin label height
        text_height : float
            text height
        """
        if libname==None: libname=self.db.plib
        if cellname==None: cellname=self.db.pcell
        if pin_label_height==None:
            pin_label_height=annotate_height
        if text_height==None:
            text_height=annotate_height
        LayoutIO.export_GDS(self.db, libname, cellname, filename=filename, layermapfile=layermapfile,
                            physical_unit=physical_unit, logical_unit=logical_unit, pin_label_height=pin_label_height,
                            text_height=text_height)

    def export_BAG(self, prj, libname=None, cellname=None, array_delimiter=['[',']'], via_tech='cdsDefTechLib'):
        """
        Export specified cell(s) to BagProject object.

        Parameters
        ----------
        db : laygo.LayoutDB.LayoutDB
            Layout db object
        libname : str
            name of library to be exported
        cellname : list or str
            name of cells to be exported
        prj : BagProject
            bag object to export
        array_delimiter : list or str
            array delimiter for multiple placements.
        via_tech : str
            via technology entry for BagProject. Not being used currently because instances are used for via connections.
        """
        if libname==None: libname=self.db.plib
        if cellname==None: cellname=self.db.pcell
        LayoutIO.export_BAG(self.db, libname, cellname, prj, array_delimiter=array_delimiter, via_tech=via_tech)

    def import_GDS(self, filename, layermapfile="default.layermap", instance_libname=None, append=True):
        """
        Import layout database from gds file.

        Parameters
        ----------
        filename : gds filename
        layermapfile : layermap filename
        instance_libname : library name of instantiated structure

        Returns
        -------
        laygo.LayoutDB.LayoutDB
            Imported layout database
        """
        db=LayoutIO.import_GDS(filename=filename, layermapfile=layermapfile, instance_libname=instance_libname,
                               res=self.res)
        if append==True:
            self.db.merge(db)
        return db

    def import_BAG(self, prj, libname, cellname=None, yamlfile="import_BAG_scratch.yaml", append=True):
        """
        Import layout database from BagProject object.

        Parameters
        ----------
        prj : BagProject
            bag object to export
        libname : str
            name of library to be exported
        cellname : list or str
            name of cells to be exported
        yamlfile : str
            scratch yaml file path

        Returns
        -------
        laygo.LayoutDB.LayoutDB
            Imported layout database
        """
        db=LayoutIO.import_BAG(prj=prj, libname=libname, cellname=cellname, yamlfile=yamlfile, res=self.db.res)
        if append==True:
            self.db.merge(db)
        return db


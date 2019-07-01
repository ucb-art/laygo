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
The GridDB module/class implements grid database management functions for GridBaseLayoutGenerator module.
"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

from .GridObject import *
import numpy as np
import yaml
import logging


class GridDB(dict):
    """
    layout grid database management class
    """
    grids = None
    """dict: grid dictionary"""
    plib = None
    """str: current library handle"""

    def __init__(self):
        """
        Constructor
        """
        #self.grids = dict()
        self.grids = self

    # i/o functions
    def display(self, libname=None, gridname=None):
        """
        Display grid database information

        Parameters
        ----------
        libname : str, optional
            library name. If None, display all libraries.
        gridname : str, optional
            grid name. If None, display all grids.
        """
        if libname == None:
            libstr = ""
        else:
            libstr = "lib:" + libname + ", "
        if gridname == None:
            gridstr = ""
        else:
            gridstr = "grid:" + gridname
        print('Display ' + libstr + gridstr)
        for ln, l in self.items():
            if libname == None or libname == ln:
                print('[Library]' + ln)
                for sn, s in l.items():
                    if gridname == None or gridname == sn:
                        print(' [Grid]' + sn)
                        s.display()

    def export_yaml(self, filename, libname=None):
        """
        Export the grid database to a yaml file. The exported file will be used to generate actual layouts.

        Parameters
        ----------
        filename : str
            filename
        libname : str
            library name
        """
        if libname == None:
            libstr = ""  # empty string
        else:
            libstr = "lib:" + libname + ", "
        # export grid
        export_dict = dict()
        print('Export grid' + libstr)
        for ln, l in self.items():
            export_dict[ln] = dict()
            print('[Library]' + ln)
            for sn, s in l.items():
                print(' [Grid]' + sn)
                export_dict[ln][sn] = s.export_dict()
        with open(filename, 'w') as stream:
            yaml.dump(export_dict, stream)

    def import_yaml(self, filename, libname=None):
        """
        Import grid database from an external file.
        Parameters
        ----------
        filename : str
            file name to be loaded.
        libname : str, optional
            library name to be imported.
        """
        with open(filename, 'r') as stream:
            ydict = yaml.load(stream)
        logging.debug('Import grid')
        for ln, l in ydict.items():
            if libname is None or libname == ln:
                logging.debug('[Library]' + ln)
                if not ln in self:
                    self.add_library(ln)
                self.sel_library(ln)
                for sn, s in l.items():
                    if s['type'] == 'placement':
                        logging.debug(' [PlacementGrid]' + sn)
                        self.add_placement_grid(name=sn, libname=ln, xy=np.array([s['xy0'], s['xy1']]))
                    if s['type'] == 'route':
                        logging.debug(' [RouteGrid]' + sn)
                        vm_dict = dict()
                        for vmn, vm in s['viamap'].items():
                            vm_dict[vmn] = np.array(vm)  # convert to np.array
                        if not 'xlayer' in s: s['xlayer'] = []
                        if not 'ylayer' in s: s['ylayer'] = []
                        self.add_route_grid(name=sn, libname=ln, xy=np.array([s['xy0'], s['xy1']]),
                                            xgrid=np.array(s['xgrid']), ygrid=np.array(s['ygrid']),
                                            xwidth=np.array(s['xwidth']), ywidth=np.array(s['ywidth']),
                                            xlayer=s['xlayer'], ylayer=s['ylayer'],
                                            viamap=vm_dict)

    def merge(self, db):
        """
        Merge a GridDB object to self.db, which is the database GridLayoutGenerator is looking at. Used when importing
        an external file (which could be either written manually or generated from laygo & exported by calling the
        GridDB.export_yaml function.

        Parameters
        ----------
        db : GridDB.GridDB
            Grid database to be merged.
        """
        for ln, l in db.items():
            if not ln in self:
                self.add_library(ln)
            self.sel_library(ln)
            for sn, s in l.items():
                if s.type == 'placement':
                    self.add_placement_grid(name=sn, libname=ln, xy=s.xy)
                if s.type == 'route':
                    self.add_route_grid(name=sn, libname=ln, xy=s.xy, xgrid=s.xgrid, ygrid=s.ygrid, xwidth=s.xwidth,
                                        ywidth=s.ywidth, xlayer=s.xlayer, ylayer=s.ylayer, viamap=s.viamap)

    # library and grid related functions
    def add_library(self, name):
        """
        Add a library to the design dictionary.

        Parameters
        ----------
        name : str
            library name
        """
        l = dict()
        self[name] = l
        return l

    def add_placement_grid(self, name, libname=None, xy=np.array([0, 0])):
        """
        Add a placement grid to the specified library.

        Parameters
        ----------
        name : str
            name of the placement grid.
        libname :
            library name (if None, self.plib is used)
        """
        if libname == None: libname = self.plib
        s = PlacementGrid(name=name, libname=libname, xy=xy)
        self[libname][name] = s
        logging.debug('AddPlacementGrid: name:' + name + ' xy:' + str(xy.tolist()))
        return s

    def add_route_grid(self, name, libname=None, xy=np.array([0, 0]), xgrid=np.array([]), ygrid=np.array([]),
                       xwidth=np.array([]), ywidth=np.array([]), xlayer=[], ylayer=[], viamap=None):
        """
        Add a route grid to the specified library.

        Parameters
        ----------
        name : str
            name of the route grid.
        libname :
            library name (if None, self.plib is used).
        """
        if libname == None: libname = self.plib
        s = RouteGrid(name=name, libname=libname, xy=xy, xgrid=xgrid, ygrid=ygrid, xwidth=xwidth, ywidth=ywidth,
                      xlayer=xlayer, ylayer=ylayer, viamap=viamap)
        self[libname][name] = s
        logging.debug('AddRouteGrid: name:' + name + ' xy:' + str(xy.tolist())
                      + ' xgrid:' + str(xgrid.tolist()) + ' xwidth:' + str(xwidth.tolist()) + ' xlayer:' + str(xlayer)
                      + ' ygrid:' + str(ygrid.tolist()) + ' ywidth:' + str(ywidth.tolist()) + ' ylayer:' + str(ylayer))
        return s

    def sel_library(self, libname):
        """
        Select a library to work on.

        Parameters
        ----------
        libname : str
            library name
        """
        self.plib = libname

    # basic db access functions
    def get_grid(self, gridname):
        """
        Grid object access function

        Parameters
        ----------
        gridname : str
            name of the grid

        Returns
        -------
        GridObject.GridObject
            Grid object handle
        """
        return self[self.plib][gridname]

    # grid coordinate access/conversion functions
    # Note: absgrid_coord notation will be changed to absgrid
    # Note: phygrid_coord notation will be changed to phygrid
    def get_absgrid_coord_x(self, gridname, x):
        """deprecated - use the get_absgrid_x function instead"""
        return self.get_absgrid_x(gridname, x)

    def get_absgrid_x(self, gridname, x):
        """
        convert a x-coordinate value on the physical grid to a corresponding value on the specified grid.
        Parameters
        ----------
        gridname : str
            abstract grid name
        x : float
            x coordinate value to be converted

        Returns
        -------
        int
            x coordinate on gridname
        """
        return self[self.plib][gridname].get_absgrid_x(x)

    def get_absgrid_coord_y(self, gridname, y):
        """deprecated - use the get_absgrid_y function instead"""
        return self.get_absgrid_y(gridname, y)

    def get_absgrid_y(self, gridname, y):
        """
        convert a y-coordinate value on the physical grid to a corresponding value on the specified grid.

        Parameters
        ----------
        gridname : str
            abstract grid name
        y : float
            y coordinate value to be converted

        Returns
        -------
        int
            y coordinate on gridname
        """
        return self[self.plib][gridname].get_absgrid_y(y)

    def get_absgrid_coord_xy(self, gridname, xy):
        """deprecated - use the get_absgrid_xy function instead"""
        return self.get_absgrid_xy(gridname, xy)

    def get_absgrid_xy(self, gridname, xy):
        """
        convert a xy coordinate on the physical grid to a corresponding coordinate on the specified grid.

        Parameters
        ----------
        gridname : str
            abstract grid name
        xy : np.array([float, float])
            xy coordinate value to be converted

        Returns
        -------
        np.array([int, int])
            xy coordinate on gridname
        """
        return self[self.plib][gridname].get_absgrid_xy(xy)

    def get_absgrid_coord_region(self, gridname, xy0, xy1):
        """deprecated - use the get_absgrid_region function instead"""
        return self.get_absgrid_region(gridname, xy0, xy1)

    def get_absgrid_region(self, gridname, xy0, xy1):
        """
        convert a region on the physical grid to a corresponding region on the specified grid.

        Parameters
        ----------
        gridname : str
            abstract grid name
        xy0 : np.array([float, float])
            lower left corner in physical grid
        xy1 : np.array([float, float])
            upper right corner in physical grid

        Returns
        -------
        np.array([[int, int], [int, int]])
            region on the specified grid
        """
        return self[self.plib][gridname].get_absgrid_region(xy0, xy1)

    def get_phygrid_coord_x(self, gridname, x):
        """deprecated - use the get_phygrid_x function instead"""
        return self.get_phygrid_x(gridname, x)

    def get_phygrid_x(self, gridname, x):
        """
        convert a x coordinate on the abstract grid, specified by gridname, to a corresponding value on the physical grid.

        Parameters
        ----------
        gridname : str
            abstract grid name
        x : int
            x coordinate value to be converted

        Returns
        -------
        float
            x coordinate on the physical grid
        """
        return self[self.plib][gridname].get_phygrid_x(x)

    def get_phygrid_coord_y(self, gridname, y):
        """deprecated - use the get_phygrid_y function instead"""
        return self.get_phygrid_y(gridname, y)

    def get_phygrid_y(self, gridname, y):
        """
        convert a y coordinate on the abstract grid, specified by gridname, to a corresponding value on the physical grid.

        Parameters
        ----------
        gridname : str
            abstract grid name
        y : int
            y coordinate value to be converted

        Returns
        -------
        float
            y coordinate on the physical grid
        """
        return self[self.plib][gridname].get_phygrid_y(y)

    def get_phygrid_coord_xy(self, gridname, xy):
        """deprecated - use the get_phygrid_xy function instead"""
        return self.get_phygrid_xy(gridname, xy)

    def get_phygrid_xy(self, gridname, xy):
        """
        convert a xy coordinate on the abstract grid, specified by gridname, to a corresponding coordinate on the physical grid.

        Parameters
        ----------
        gridname : str
            abstract grid name
        xy : np.array([int, int])
            xy coordinate value to be converted

        Returns
        -------
        np.array([float, float])
            xy coordinate on the physical grid
        """
        return self[self.plib][gridname].get_phygrid_xy(xy)

    # route grid function
    def get_route_width_xy(self, gridname, xy):
        """
        return the width of routing wires passing xy on gridname.

        Parameters
        ----------
        gridname : str
            abstract grid name
        xy : np.array([int, int])
            xy coordinate to get the width parameters

        Returns
        -------
        np.array([float, float])
            width parameters on xy (xgrid(vertical), ygrid(horizontal))
        """
        return self[self.plib][gridname].get_route_width_xy(xy)

    def get_route_layer_xy(self, gridname, xy):
        """
        return the layers of routing wires passing xy on gridname.

        Parameters
        ----------
        gridname : str
            abstract grid name
        xy : np.array([int, int])
            xy coordinate to get the layer information

        Returns
        -------
        list([[str, str], [str, str]])
            layer parameters on xy coordinate (xlayer, ylayer)
        """
        return [self.get_route_xlayer_xy(gridname, xy), self.get_route_ylayer_xy(gridname, xy)]

    def get_route_xlayer_xy(self, gridname, xy):
        """
        return the layer of vertical routing wires passing xy on gridname.

        Parameters
        ----------
        gridname : str
            abstract grid name
        xy : np.array([int, int])
            xy coordinate to get the layer information

        Returns
        -------
        list([str, str])
            layer parameters of xgrid on xy coordinate
        """
        return self[self.plib][gridname].get_route_xlayer_xy(xy)

    def get_route_ylayer_xy(self, gridname, xy):
        """
        return the layer of horizontal routing wires passing xy on gridname.

        Parameters
        ----------
        gridname : str
            abstract grid name
        xy : np.array([int, int])
            xy coordinate to get the layer information

        Returns
        -------
        list([str, str])
            layer parameters of ygrid on xy coordinate
        """
        return self[self.plib][gridname].get_route_ylayer_xy(xy)

    # via functions
    def get_vianame(self, gridname, xy):
        """

        Parameters
        ----------
        gridname : str
            abstract grid name
        xy : np.array([int, int])
            xy coordinate to get the layer information

        Returns
        -------
        str
            name of via that can be placed on xy, on abstract grid specified by gridname
        """
        return self[self.plib][gridname].get_vianame(xy)

    def update_viamap(self, gridname, viamap):
        """
        Update viamap of specified grid (used for constructgrid function)
        Parameters
        ----------
        gridname : str
            abstract grid name
        viamap : dict
            dictionary that contains viamap parameters
        """
        self[self.plib][gridname].update_viamap(viamap)

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
The GridObject module and class implements a object that contains grid information for placement and route. It also
provides useful functions for coordinate conversion between physical and abstract grids.
"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

import numpy as np

class GridObject():
    """Layout abstract grid class"""
    type="native"
    """str: type of grid. can be 'native', 'route', 'placement'"""
    name=None
    """str: name of grid"""
    libname=None
    """str: library name of grid"""
    xy = np.array([0, 0]) # Coordinate
    """np.array([float, float]): size of grid"""
    xgrid=np.array([])
    """np.array([float, float, ...]): x coordinates of grid"""
    ygrid=np.array([])
    """np.array([float, float, ...]): y coordinates of grid"""
    max_resolution=10
    """int: maximum resolution to handle floating point numbers"""

    @property
    def height(self):
        """float: height of grid"""
        return abs(self.xy[0][1]-self.xy[1][1])

    @property
    def width(self):
        """float: width of grid"""
        return abs(self.xy[0][0]-self.xy[1][0])

    def __init__(self, name, libname, xy, _xgrid=np.array([0]), _ygrid=np.array([0])):
        """
        Constructor
        """
        self.name = name
        self.libname=libname
        self.xy=xy
        self.xgrid=_xgrid
        self.ygrid=_ygrid

    def display(self):
        """
        Display grid information
        """
        print("  " + self.name + " width:" + str(np.around(self.width, decimals=self.max_resolution))
                               + " height:" + str(np.around(self.height, decimals=self.max_resolution)))

    def export_dict(self):
        """
        Export object information in dict format

        Returns
        -------
        dict
            grid information in dict format
        """
        export_dict={'type':self.type,
                     'xy0':np.around(self.xy[0,:], decimals=self.max_resolution).tolist(),
                     'xy1':np.around(self.xy[1,:], decimals=self.max_resolution).tolist()}
        if not self.xgrid.tolist()==[]:
            export_dict['xgrid']=np.around(self.xgrid, decimals=self.max_resolution).tolist()
        if not self.ygrid.tolist()==[]:
            export_dict['ygrid']=np.around(self.ygrid, decimals=self.max_resolution).tolist()
        return export_dict

    def _add_grid(self, grid, v):
        """
        add a grid coordinate

        Parameters
        ----------
        grid : np.array
            grid array
        v : float
            value

        Returns
        -------
        np.array
            updated grid array
        """
        grid.append(v)
        grid.sort()
        return grid

    def add_xgrid(self, x):
        """
        add a coordinate value to grid in x direction

        Parameters
        ----------
        x : float
            value to be added
        """
        self.xgrid=self._add_grid(self.xgrid, x)

    def add_ygrid(self, y):
        """
        add a coordinate value to grid in y direction

        Parameters
        ----------
        y : float
            value to be added
        """
        self.ygrid=self._add_grid(self.ygrid, y)

    def get_xgrid(self):
        """use laygo.GridObject.GridObject.xgrid instead"""
        return self.xgrid

    def get_ygrid(self):
        """use laygo.GridObject.GridObject.ygrid instead"""
        return self.ygrid

    #abstract to physical conversion functions
    def _get_absgrid_coord(self, v, grid, size, method='ceil'):
        """
        Convert physical value to abstract value on grid. Since physical values are continuous and grid values are
        discrete, boundary conditions are need to be defined for the conversion.
        Default (and only supported in the current version) converting method is ceil, which is described as follows:
        #   physical grid: 0----grid0----grid1----grid2----...----gridN---size
        # abstracted grid: 0  0   0    1   1    2   2           N   N   N+1
        The ceiling method works well with stacked grids. For example, in the example, phyical values ranging from
        (larger than) GridN to (equal to) gridN+1 (grid0 of the second stack) will be converted to N+1.

        Parameters
        ----------
        v : float
            grid value
        grid : np.array
            grid array
        size : float
            grid size
        method : str, optional
            converting method

        Returns
        -------
        int
            abstract grid value
        """
        quo=np.floor(np.divide(v, size))
        mod=v-quo*size #mod=np.mod(v, size) not working well
        mod_ongrid=np.searchsorted(grid+1e-10, mod) #add 1e-10 to handle floating point precision errors
        #print('physical:' + str(v.tolist()) + ' size:'+ str(size) +
        #      ' quo:' + str(quo.tolist()) + ' mod:' + str(mod) +
        #      ' abs:' + str(np.add(np.multiply(quo,grid.shape[0]), mod_ongrid).tolist()))
        return np.add(np.multiply(quo,grid.shape[0]), mod_ongrid)

    def get_absgrid_coord_x(self, x): return self.get_absgrid_x(x)
    def get_absgrid_x(self, x):
        """
        Convert a physical x coordinate to a corresponding value in abstract grid

        Parameters
        ----------
        x : float
            value

        Returns
        -------
        int
            converted value
        """
        return self._get_absgrid_coord(x, self.xgrid, self.width).astype(int)

    def get_absgrid_coord_y(self, y): return self.get_absgrid_y(y)
    def get_absgrid_y(self, y):
        """
        Convert a physical y coordinate to a corresponding value in abstract grid

        Parameters
        ----------
        y : float
            value

        Returns
        -------
        int
            converted value
        """
        return self._get_absgrid_coord(y, self.ygrid, self.height).astype(int)

    def get_absgrid_coord_xy(self, xy): return self.get_absgrid_xy(xy)
    def get_absgrid_xy(self, xy):
        """
        Convert a physical xy coordinate to a corresponding vector in abstract grid

        Parameters
        ----------
        xy : np.array([float, float])

        Returns
        -------
        np.array([int, int])
        """
        _xy=np.vstack((self.get_absgrid_x(xy.T[0]), self.get_absgrid_y(xy.T[1]))).T
        if _xy.shape[0]==1: return _xy[0]
        else: return _xy

    def get_absgrid_coord_region(self, xy0, xy1): return self.get_absgrid_region(xy0, xy1)
    def get_absgrid_region(self, xy0, xy1):
        """
        Convert a physical regin to a corresponding region in abstract grid

        Parameters
        ----------
        xy0 : np.array([float, float])
            first coordinate
        xy1 : np.array([float, float])
            second coordinate

        Returns
        -------
        np.array([[int, int], [int, int]])
            converted coordinate
        """
        _xy0 = np.vstack((self.get_absgrid_coord_x(xy0.T[0]), self.get_absgrid_coord_y(xy0.T[1]))).T
        _xy1 = np.vstack((self.get_absgrid_coord_x(xy1.T[0]), self.get_absgrid_coord_y(xy1.T[1]))).T
        if _xy0.shape[0] == 1: _xy0 = _xy0[0]
        if _xy1.shape[0] == 1: _xy1 = _xy1[0]
        #upper right boundary adjust
        #check by re-converting to physical grid and see if the points are within original [xy0, xy1]
        #xy0_check = self.get_phygrid_coord_xy(_xy0)[0]
        #xy1_check = self.get_phygrid_coord_xy(_xy1)[0]
        xy0_check = self.get_phygrid_xy(_xy0)
        xy1_check = self.get_phygrid_xy(_xy1)
        xy0_check = np.around(xy0_check, decimals=self.max_resolution)
        xy1_check = np.around(xy1_check, decimals=self.max_resolution)
        xy0 = np.around(xy0, decimals=self.max_resolution)
        xy1 = np.around(xy1, decimals=self.max_resolution)
        #print("phy:" + str(xy0) + " " + str(xy1) + " abs:" + str(_xy0) + " " + str(_xy1) + " chk:" + str(xy0_check) + " " + str(xy1_check))
        if xy0_check[0] > xy0[0] and xy0_check[0] > xy1[0]: _xy0[0] -= 1
        if xy1_check[0] > xy0[0] and xy1_check[0] > xy1[0]: _xy1[0] -= 1
        if xy0_check[1] > xy0[1] and xy0_check[1] > xy1[1]: _xy0[1] -= 1
        if xy1_check[1] > xy0[1] and xy1_check[1] > xy1[1]: _xy1[1] -= 1
        #if _xy1[1]==7:
        #    print("phy:"+str(xy0)+" "+str(xy1)+" abs:"+str(_xy0)+" "+str(_xy1)+" chk:"+str(xy0_check)+" "+str(xy1_check))
        #print(xy1)

        return(np.vstack((_xy0, _xy1)))

    # physical to abstract conversion functions
    def _get_phygrid_coord(self, v, grid, size):
        """
        Internal function for abstract to physical coordinate conversions

        Parameters
        ----------
        v : int
            value in abstract coordinate
        grid : np.array
            grid array
        size : float
            grid size

        Returns
        -------
        float
            value in physical coordinate
        """
        quo = np.floor(np.divide(v, grid.shape[0]))
        mod = np.mod(v, grid.shape[0])  # mod = v - quo * grid.shape[0]
        return np.add(np.multiply(quo, size), np.take(grid, mod))

    def get_phygrid_coord_x(self, x): return self.get_phygrid_x(x)
    def get_phygrid_x(self, x):
        """
        Get the physical value of a abstract x coordinate

        Parameters
        ----------
        x : int
            abstract coordinate value

        Returns
        -------
        float
            physical coordinate value
        """
        return self._get_phygrid_coord(x, self.xgrid, self.width)

    def get_phygrid_coord_y(self, y): return self.get_phygrid_y(y)
    def get_phygrid_y(self, y):
        """
        Get the physical value of a abstract y coordinate

        Parameters
        ----------
        y : int
            abstract coordinate value

        Returns
        -------
        float
            physical coordinate value
        """
        return self._get_phygrid_coord(y, self.ygrid, self.height)

    def get_phygrid_coord_xy(self, xy): return self.get_phygrid_xy(xy)
    def get_phygrid_xy(self, xy):
        """
        Get the physical value of a abstract vector

        Parameters
        ----------
        xy : np.array([int, int])
            abstract coordinate vector

        Returns
        -------
        np.array([float, float])
            physical coordinate vector
        """
        if xy.ndim==1: #single coordinate
            return np.vstack((self.get_phygrid_coord_x(xy.T[0]), self.get_phygrid_coord_y(xy.T[1]))).T[0]
        else:
            return np.vstack((self.get_phygrid_coord_x(xy.T[0]), self.get_phygrid_coord_y(xy.T[1]))).T


class PlacementGrid(GridObject):
    """
    Placement grid class
    """
    type = 'placement'


class RouteGrid(GridObject):
    """
    Routing grid class
    """
    type = 'route'
    """str: type of grid. can be 'native', 'route', 'placement'"""
    xwidth = np.array([])
    """np.array: width of xgrid"""
    ywidth = np.array([])
    """np.array: width of ygrid"""
    viamap = dict()
    """dict: via map information"""
    xlayer = None
    """list: layer of xgrid"""
    ylayer = None
    """list: layer of ygrid"""

    def __init__(self, name, libname, xy, xgrid, ygrid, xwidth, ywidth, xlayer=None, ylayer=None, viamap=None):
        """
        Constructor
        """
        self.name = name
        self.libname = libname
        self.xy = xy
        self.xgrid = xgrid
        self.ygrid = ygrid
        self.xwidth = xwidth
        self.ywidth = ywidth
        self.xlayer = xlayer
        self.ylayer = ylayer
        self.viamap = viamap

    def _get_route_width(self, v, _width):
        """
        Get metal width

        Parameters
        ----------
        v : int
            value
        _width : np.array
            width vector

        Returns
        -------
        float
            route width
        """
        #quo=np.floor(np.divide(v, self._width.shape[0]))
        mod=np.mod(v, _width.shape[0])
        #if not isinstance(mod, int):
        #    print(v, _width, mod)
        return _width[int(np.round(mod))]

    def _get_route_layer(self, v, _layer):
        """
        Get metal layer

        Parameters
        ----------
        v : int
            index value
        _layer : list
            layer list

        Returns
        -------
        [str, str]
            route layer
        """
        mod=np.mod(v, len(_layer))
        return _layer[mod]

    #def get_xwidth(self): return self.xwidth
    #def get_ywidth(self): return self.ywidth
    #def get_viamap(self): return self.viamap

    def get_route_width_xy(self, xy):
        """
        Get metal width vector

        Parameters
        ----------
        xy : np.array([int, int])
            coordinate

        Returns
        -------
        np.array([float, float])
            route width vector ([xgrid, ygrid])
        """
        return np.array([self._get_route_width(xy[0], self.xwidth),
                         self._get_route_width(xy[1], self.ywidth)])

    def get_route_xlayer_xy(self, xy):
        """
        Get route layer in xgrid direction (vertical)

        Parameters
        ----------
        xy : np.array([int, int])
            coordinate

        Returns
        -------
        [str, str]
            route layer information
        """
        return self._get_route_layer(xy[0], self.xlayer)

    def get_route_ylayer_xy(self, xy):
        """
        Get route layer in ygrid direction (horizontal)

        Parameters
        ----------
        xy : np.array([int, int])
            coordinate

        Returns
        -------
        [str, str]
            route layer information
        """
        return self._get_route_layer(xy[1], self.ylayer)

    def get_vianame(self, xy):
        """
        Get the name of via on xy

        Parameters
        ----------
        xy : np.array([int, int])
            coordinate

        Returns
        -------
        str
            cellname of via
        """
        mod = np.array([np.mod(xy[0], self.xgrid.shape[0]), np.mod(xy[1], self.ygrid.shape[0])])
        for vianame, viacoord in self.viamap.items():
            if viacoord.ndim==1:
                if np.array_equal(mod, viacoord): return vianame
            else:
                for v in viacoord:
                    if np.array_equal(mod,v):
                        return vianame

    def display(self):
        """
        Display RouteGrid information
        """
        display_str="  " + self.name + " width:" + str(np.around(self.width, decimals=self.max_resolution))\
                    + " height:" + str(np.around(self.height, decimals=self.max_resolution))\
                    + " xgrid:" + str(np.around(self.xgrid, decimals=self.max_resolution))\
                    + " ygrid:" + str(np.around(self.ygrid, decimals=self.max_resolution))\
                    + " xwidth:" + str(np.around(self.xwidth, decimals=self.max_resolution))\
                    + " ywidth:" + str(np.around(self.ywidth, decimals=self.max_resolution))\
                    + " xlayer:" + str(self.xlayer)\
                    + " ylayer:" + str(self.ylayer)\
                    + " viamap:{"
        for vm_name, vm in self.viamap.items():
            display_str+=vm_name + ": " + str(vm.tolist()) + " "
        display_str+="}"
        print(display_str)

    def export_dict(self):
        """
        Export grid information in dict format

        Returns
        -------
        dict
            Grid information
        """
        export_dict=GridObject.export_dict(self)
        export_dict['xwidth'] = np.around(self.xwidth, decimals=self.max_resolution).tolist()
        export_dict['ywidth'] = np.around(self.ywidth, decimals=self.max_resolution).tolist()
        export_dict['xlayer'] = self.xlayer
        export_dict['ylayer'] = self.ylayer
        export_dict['viamap'] = dict()
        for vn, v in self.viamap.items():
            export_dict['viamap'][vn]=[]
            for _v in v:
                export_dict['viamap'][vn].append(_v.tolist())
        return export_dict

    def update_viamap(self, viamap):
        """use laygo.GridObject.RouteGrid.viamap instead"""
        self.viamap=viamap

if __name__ == '__main__':
    lgrid=GridObject()
    print('LayoutGrid test')
    lgrid.xgrid = np.array([0.2, 0.4, 0.6])
    lgrid.ygrid = np.array([0, 0.4, 0.9, 1.2, 2, 3])
    lgrid.width = 1.2
    lgrid.height = 3.2
    phycoord = np.array([[-0.2, -0.2], [0, 2], [4,2.2], [0.5, 1.5], [1.3, 3.6], [8,2.3]])
    print("  xgrid:" + str(lgrid.xgrid) + " width:" + str(lgrid.width))
    print("  ygrid:" + str(lgrid.ygrid) + " height:" + str(lgrid.height))
    print('physical grid to abstract grid')
    print("  input:"+str(phycoord.tolist()))
    abscoord=lgrid.get_absgrid_coord_xy(phycoord)
    print("  output:"+str(abscoord.tolist()))
    print('abstract grid to physical grid')
    phycoord=lgrid.get_phygrid_xy(abscoord).tolist()
    print("  output:"+str(phycoord))

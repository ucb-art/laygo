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
GridLayoutGenerator, with experimental & improved features. No backward compatibility. Not finalized

"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"


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

    #options
    use_array = True
    """boolean: True if InstanceArray is used instead of Instance. For GridLayoutGenerator2 only"""

    def place(self, gridname, cellname, mn=np.array([0, 0]), ref=None, shape=None, transform='R0', name=None,
              libname=None, spacing=None, offset=[0, 0]):
        """
        Place an instance at mn=[m, n] on abstract grid, optionally bound from a reference object.
        If reference object is not specified, origin+offset (in physical grid) is used as the reference point.
        Equation = mn+ref_mn+0.5*(Mt@ref_size+Md@(ref_size+template_size)-Mti@template_size).

        Parameters
        ----------
        gridname : str
            Grid name for the placement. If None, physical grid is used.
        cellname : str
            Template name (cellname) of the instance.
        mn : np.array([int, int]) or [int, int], optional
            Placement coordinate on the grid, specified by gridname. Default value is [0, 0].
        ref : LayoutObject.Instance or LayoutObject.InstanceArray, optional
            Reference instance handle.
        shape : np.array([int, int]) or None, optional
            array shape parameter. If None, the instance is not considered as array. Default is None.
        transform : str ('R0', 'MX', 'MY')
            Transform parameter. 'R0' is used by default.

        Returns
        -------
        laygo.layoutObject.Instance
            generated instance

        Other Parameters
        ----------------
        name : str, optional
            Name of the instance. If None, the instance name is automatically generated.
        libname : str, optional
            Template library name. If not specified, self.templates.plib is used.
        spacing : np.array([int, int]) or [int, int]
            Array spacing parameter for the instance. If none, the size of the instance of is used.
        offset : np.array([float, float]), optional
            Placement offset in physical coordinate.
        """
        return GridLayoutGenerator.relplace(self, name=name, gridname=gridname, xy=mn, offset=offset, shape=shape,
                                            spacing=spacing, transform=transform, refobj=ref, libname=libname,
                                            cellname=cellname)

    def via(self, gridname, mn=[0, 0], ref=None, overlay=None, transform='R0', name=None,
            offset=np.array([0, 0]), overwrite_xy=None):

        """
        Place a via on abstract grid, bound from a reference object. If reference object is not specified,
        [0, 0]+offset is used as the reference point.

        Parameters
        ----------
        gridname : str
            Grid name of the via
        mn : np.array([int, int]) or [int, int]
            xy coordinate of the via. Default value is [0, 0].
        ref : LayoutObject.LayoutObject
            Reference object(Instance/InstanceArray/Pin/Rect) handle.
        overlay : LayoutObject.LayoutObject
            Layout object for via placement at intersections (via will be placed at interaction points of ref and overlay.
        transform : str ('R0', 'MX', 'MY'), optional
            Transform parameter for grid. Transform of ref is used if not specified.

        Returns
        -------
        laygo.layoutObject.Instance
            generated via instance

        Other Parameters
        ----------------
        name : str
            Name of the via
        offset : np.array([float, float]), optional
            Placement offset on the physical grid.
        overwrite_xy : None or np.array([float, float]), optional
            If specified, the final xy (in physical coordinate) is overwritten by the parameter.
        """
        return GridLayoutGenerator.via(self, name=name, xy=mn, gridname=gridname, refobj=ref, offset=offset,
                                       transform=transform, overwrite_xy_phy=overwrite_xy, overlay=overlay)

    def route(self, gridname0, gridname1=None, mn0=np.array([0, 0]), mn1=np.array([0, 0]), ref0=None, ref1=None,
              transform0='R0', transform1=None, via0=None, via1=None, netname=None, direction='omni',
              endstyle0="truncate", endstyle1="truncate", name=None, layer=None, offset0=np.array([0, 0]),
              offset1=None):
        """
        Route on abstract grid, bound from reference objects. If reference objects are not specified,
        [0, 0]+offset is used as reference points.

        Parameters
        ----------
        gridname0 : str
            Grid name0
        gridname1 : str, optional
            Grid name1
        mn0 : np.array([int, int]) or [int, int]
            abstract coordinate of start point.
        mn1 : np.array([int, int]) or [int, int]
            abstract coordinate of end point.
        ref0 : LayoutObject.LayoutObject
            Reference object(Instance/Pin/Rect) handle.
        ref1 : LayoutObject.LayoutObject
            Reference object(Instance/Pin/Rect) handle.
        transform0 : str, optional
            Transform parameter for grid0. Overwritten by transform of ref0 if not specified.
        transform1 : str, optional
            Transform parameter for grid1. Overwritten by transform of ref1 if not specified.
        via0 : None or np.array([int, int]) or np.array([[int, int], [int, int], [int, int], ...]), optional
            Offset coordinates for via placements, bound from xy0
            ex) if mn0 = [1, 2], mn1 = [1, 5], via0 = [0, 2] then a via will be placed at [1, 4]
        via1 : None or np.array([int, int]) or np.array([[int, int], [int, int], [int, int], ...]), optional
            Offset coordinates for via placements, bound from xy1
            ex) if mn0 = [1, 2], mn1 = [1, 5], via1 = [0, 2] then a via will be placed at [1, 7]
        netname : str, optional
            net name of the route
        direction : str, optional
            Routing direction (omni, x, y, ...). It will be used as the input argument of GridLayoutGenerator.Md.
        endstyle0 : str ('extend', 'truncate'), optional
            End style of xy0 (extend the edge by width/2 if endstyle=='extend')
        endstyle1 : str ('extend', 'truncate'), optional
            End style of xy1 (extend the edge by width/2 if endstyle=='extend')

        Returns
        -------
        laygo.layoutObject.Rect
            generated route

        Other Parameters
        ----------------
        name : str
            Route name. If None, the name will be automatically assigned by genid.
        layer : [str, str], optional
            Routing layer [name, purpose]. If None, it figures out the layer from grid and coordinates
        offset0 : np.array([float, float]), optional
            Coordinate offset from xy0, on the physical grid.
        offset1 : np.array([float, float]), optional
            Coordinate offset from xy1, on the physical grid.
        """
        return GridLayoutGenerator.route(self, name=name, layer=layer, xy0=mn0, xy1=mn1, gridname0=gridname0,
                                         gridname1=gridname1, direction=direction, refobj0=ref0, refobj1=ref1,
                                         offset0=offset0, offset1=offset1, transform0=transform0, transform1=transform1,
                                         endstyle0=endstyle0, endstyle1=endstyle1, via0=via0, via1=via1,
                                         netname=netname)

    #pin creation functions
    def pin(self, gridname, name, mn0=np.array([0, 0]), mn1=np.array([0, 0]), ref=None, layer=None, netname=None,
            base_layer=None):
        """
        Pin generation function.
        Parameters
        ----------
        gridname : str
            grid name. If None, physical coordinate is used.
        name : str
            pin name
        mn0 : np.array([[int, int]), optional
            first coordinate
        mn1 : np.array([[int, int]), optional
            second coordinate
        ref : LayoutObject.LayoutObject, optional
            reference object handle
        layer : [str, str], optional
            pin layer, if None, layer of refobj is used (assuming refobj is Rect)
        netname : str, optional
            net name. If None, pin name is used. Used when multiple pin objects are attached to the same net.
        base_layer : [str, str], optional
            base metal layer. If None, corresponding layer in metal dict is used.

        Returns
        -------
        laygo.LayoutObject.Pin
            generated Pin object

        See Also
        --------
        boundary_pin_from_rect : generate a boundary Pin from a Rect
        """
        mn = np.array([mn0, mn1])
        if not ref is None:
            if type(ref).__name__ is 'Rect':
                mn = self.get_mn(obj=ref, gridname=gridname) + mn
                if layer is None:
                    layer=self.layers['pin'][self.layers['metal'].index(ref.layer)]
            elif type(ref).__name__ is 'Pin':
                mn = self.get_mn(obj=ref, gridname=gridname) + mn
                if layer is None:
                    layer=ref.layer
        if netname==None: netname=name
        xy_phy, xy_phy_center=self._route_generate_box_from_abscoord(xy0=mn[0,:], xy1=mn[1,:], gridname0=gridname)
        xy0_phy_center=xy_phy_center[0,:]; xy1_phy_center=xy_phy_center[1,:]
        #layer handling
        if layer is None:
            if int(round(xy0_phy_center[0]/self.res)) == int(round(xy1_phy_center[0]/self.res)):
                _base_layer = self.grids.get_route_xlayer_xy(gridname, mn[0,:])
            else:
                _base_layer = self.grids.get_route_ylayer_xy(gridname, mn[0,:])
            layer=self.layers['pin'][self.layers['metal'].index(_base_layer)]
        #baselayer handling
        if base_layer==None:
            base_layer=self.layers['metal'][self.layers['pin'].index(layer)]
        self.db.add_rect(None, xy=xy_phy, layer=base_layer)
        return self.db.add_pin(name=name, netname=netname, xy=xy_phy, layer=layer)

    #object geometry related functions
    def get_mn(self, obj, gridname=None, sort=False):
        """
            get coordinate values of an object on the specific coordinate
            Parameters
            ----------
            obj : LayoutObject.LayoutObject or TemplateObject.TemplateObject
                Object to get the xy coordinates
            gridname : str, optional
                grid name. If None, physical grid is used
            Returns
            -------
            np.ndarray()
                geometric paramter of the object on gridname
        """
        return self.get_xy(obj=obj, gridname=gridname, sort=sort)

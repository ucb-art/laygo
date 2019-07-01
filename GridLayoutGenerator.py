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
The GridLayoutGenerator module implements classes to generate full-custom layout on 'abstract' grid. It allows designers
to describe layout generation scripts in Python language and automate the layout process, abstracting design rules for
easier implementation and process portability. All numerical parameters are given in integer numbers and they are
converted to physical numbers internally and designers don't need to deal with complex design rules in modern CMOS
process.
Example
-------
For layout export, type below command in ipython console.
    $ run laygo/labs/lab2_b_gridlayoutgenerator_layoutexercise.py
"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

from .BaseLayoutGenerator import *
from .TemplateDB import *
from .GridDB import *
from . import PrimitiveUtil as ut
import numpy as np
import logging

#TODO: support path routing

class GridLayoutGenerator(BaseLayoutGenerator):
    """
    The GridLayoutGenerator class implements functions and variables for full-custom layout generations on abstract
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
    templates = None
    """laygo.TemplateDB.TemplateDB: template database"""
    grids = None
    """laygo.GridDB.GridDB: grid database"""
    use_phantom=False #phantom cell usage
    """bool: true if phantom cells are exported (not real cells)"""
    layers = {'metal':[], 'pin':[], 'text':[], 'prbnd':[]}
    """dict: layer dictionary. Keys are metal, pin, text, prbnd"""

    def __init__(self, physical_res=0.005, config_file=None):
        """
        Constructor
        """
        self.templates = TemplateDB()
        self.grids = GridDB()
        if not config_file==None: #config file exists
            with open(config_file, 'r') as stream:
                techdict = yaml.load(stream)
                self.tech = techdict['tech_lib']
                self.physical_res = techdict['physical_resolution']
                physical_res=self.physical_res
                self.layers['metal'] = techdict['metal_layers']
                self.layers['pin'] = techdict['pin_layers']
                self.layers['text'] = techdict['text_layer']
                self.layers['prbnd'] = techdict['prboundary_layer']
                print(self.tech + " loaded sucessfully")

        BaseLayoutGenerator.__init__(self, res=physical_res)

    #aux functions
    def _bbox_xy(self, xy):
        """
        Find a bbox of xy coordinates. ex) _bbox_xy([[4, 1], [3, 5], [2, 3]])=np.array([[2, 1], [4, 5]])
        Parameters
        ----------
        xy : np.array([[int, int], [int, int]]) or
            point matrix. List can be also used.
        Returns
        -------
        np.array([[int, int], [int, int]])
            bbox matrix
        """
        xy = np.asarray(xy)
        bx = sorted(xy[:, 0].tolist())
        by = sorted(xy[:, 1].tolist())
        ll = np.array([bx[0], by[0]])  # lower-left
        ur = np.array([bx[-1], by[-1]])  # upper-right
        bnd = np.vstack([ll, ur])
        return bnd

    #Placement functions
    def place(self, name, templatename, gridname, xy, template_libname=None, shape=np.array([1, 1]), spacing=None,
              offset=np.array([0, 0]), transform='R0', annotate_text=None, libname=None):
        """
        Place an instance on abstract grid. Use relplace instead
        Parameters
        ----------
        name : str
            Name of the instance.
        templatename : str
            Name of the template for the instance.
        gridname : str
            Grid name for the instance placement.
        xy : np.array([int, int]) or [int, int]
            Placement coordinate on the grid, specified by gridname.
        libname : str, optional
            Template library name. If not specified, self.templates.plib is used.
        shape : np.array([x0, y0]) or None, optional
            array shape parameter. If None, the instance is not considered as array. Default is None
        transform : str ('R0', 'MX', 'MY'), optional
            Transform parameter
        Returns
        -------
        laygo.layoutObject.Instance
            generated instance
        Other Parameters
        ----------------
        template_libname: str, optional, deprecated
            Replaced with libname
        spacing : np.array([int, int]), optional
            Array spacing parameter for the instance. If None, the size of the instance of is used.
        offset : np.array([float, float]), optional
            Offset in physical coordinate.
        annotate_text : str, optional
            text to be annotated. Use None if no annotation is required
        """
        ### preprocessing starts ###
        xy = np.asarray(xy)  # convert to a numpy array
        if shape is None:
            _shape = np.array([1, 1])
        else:
            _shape = np.asarray(shape)
        if not spacing==None: spacing = np.asarray(spacing)
        offset = np.asarray(offset)
        if not libname is None:
            template_libname = libname
        if template_libname is None:
            template_libname = self.templates.plib
        ### preprocessing ends ###
        t=self.templates.get_template(templatename, template_libname)
        xy_phy=self.grids.get_phygrid_xy(gridname, xy)+offset
        # instantiation
        if not isinstance(spacing,np.ndarray): spacing=t.size
        inst = self.add_inst(name=name, libname=template_libname, cellname=t.name, xy=xy_phy, shape=shape,
                             spacing=spacing, transform=transform, template=t)
        if not annotate_text==None: #annotation
            self.add_text(None, text=annotate_text, xy=np.vstack((xy_phy, xy_phy+0.5*np.dot(t.size*_shape,
                          ut.Mt(transform).T))), layer=self.layers['prbnd'])
        if self.use_phantom == True: #phantom cell placement
            self.add_rect(None, xy=np.vstack((xy_phy, xy_phy+np.dot(t.size*_shape, ut.Mt(transform).T))),
                      layer=self.layers['prbnd'])
            for pinname, pin in t.pins.items(): #pin abstract
                for x in range(_shape[0]):
                    for y in range(_shape[1]):
                        self.add_rect(None, xy=np.vstack((xy_phy+np.dot(pin['xy'][0]+t.size*np.array([x, y]), ut.Mt(transform).T),
                                                          xy_phy+np.dot(pin['xy'][1]+t.size*np.array([x, y]), ut.Mt(transform).T))),
                                      layer=self.layers['prbnd'])
                        self.add_text(None, text=pinname+'/'+pin['netname'], xy=xy_phy, layer=self.layers['prbnd'])
            self.add_text(None, text=inst.name+"/"+t.name, xy=xy_phy, layer=self.layers['prbnd'])
        return inst

    def relplace(self, name=None, templatename=None, gridname=None, refinstname=None, direction='right',
                 xy=np.array([0, 0]), offset=np.array([0, 0]), template_libname=None, shape=None,
                 spacing=None, transform='R0', refobj=None, libname=None, cellname=None):
        """
        Place an instance on abstract grid, bound from a reference object. If reference object is not specified,
        [0, 0]+offset is used as the reference point.
        Equation = xy+refobj_xy+0.5*(Mt@refobj_size+Md@(refobj_size+inst_size)-Mti@inst_size).

        Parameters
        ----------
        name : str
            Name of the instance.
        cellname : str
            Template name (cellname) of the instance.
        gridname : str
            Grid name for the placement.
        xy : np.array([x, y]) or [int, int], optional
            Placement coordinate on the grid, specified by gridname. If not specified, [0, 0] is used.
        refobj : LayoutObject.Instance, optional
            Reference instance handle, if None, refinstname is used. Will be extended to support other objects.
        direction : str, optional
            Direction of placement, bound from refobj. For example, if the instance will be place on top of refobj,
            direction='top' is used
        shape : np.array([x0, y0]) or None, optional
            array shape parameter. If None, the instance is not considered as array. Default is None
        transform : str ('R0', 'MX', 'MY')
            Transform parameter. 'R0' is used by default.
        libname : str, optional
            Template library name. If not specified, self.templates.plib is used.

        Returns
        -------
        laygo.layoutObject.Instance
            generated instance

        Other Parameters
        ----------------
        refinstname : str, optional, deprecated
            Reference instance name, if None, [0, 0] is used for the reference point.
        templatename : str, deprecated
            Replaced with cellname
        template_libname: str, optional, deprecated
            Replaced with libname
        spacing : np.array([int, int]) or [int, int]
            Array spacing parameter for the instance. If none, the size of the instance of is used.
        offset : np.array([float, float]), optional
            Placement offset in physical coordinate.

        See Also
        --------
        place : substrate function of relplace
        """
        #TODO: Alignment option, bottom/top-left/right directions
        # cellname handling
        if not cellname is None:
            templatename=cellname
        # check if it's multiple placement
        if isinstance(templatename, list): # multiple placement
            flag_recursive=False #recursive placement flag. If True, next placement refer the current placement
            # preprocessing arguments
            len_inst = len(templatename) #number of instance to be placed (for multiple placements)
            if name is None:
                name = [None] * len_inst #extend Name list to be matched with templatename
            if refinstname is None: #for backward compatibility. Use refobj instead of refinstname if possible
                if refobj is None:
                    flag_recursive=True
                    _refinstname=[None for i in range(len_inst)]
                else:
                    #check if refobj is list. If so, do a recursive placement
                    if isinstance(refobj, list):
                        _refinstname=[i.name for i in refobj]
                    else:
                        flag_recursive=True
                        _refinstname=[refobj.name]+[None for i in range(len_inst-1)]
            else:
                #check if refinstname is list. If so, do a recursive placement
                if isinstance(refinstname, list):
                    _refinstname=refinstname
                else:
                    flag_recursive=True
                    _refinstname=[refinstname]+[None for i in range(len_inst-1)]
            if isinstance(xy[0], (int, np.int64)):
                xy = [xy] * len_inst
            if isinstance(direction, str):
                direction = [direction] * len_inst
            if shape == None:
                shape = [shape] * len_inst
            else:
                if isinstance(shape[0], (int, np.int64)):
                    shape = [shape] * len_inst
            if spacing is None:
                spacing = [None] * len_inst
            elif isinstance(spacing[0], (int, np.int64)):
                spacing = [spacing] * len_inst
            else:
                if not isinstance(spacing, list): spacing = [spacing] * len_inst
            if isinstance(transform, str): transform = [transform] * len_inst
            return_inst_list = []
            for i, nm, _refi_name, _xy, tl, dr, sh, sp, tr in zip(range(len_inst), name, _refinstname, xy, templatename, direction, shape, spacing, transform): #row placement
                refi = GridLayoutGenerator.relplace(self, nm, tl, gridname, refinstname=_refi_name, direction=dr, xy=_xy,
                                   offset=offset, template_libname=template_libname, shape=sh, spacing=sp,
                                   transform=tr)#, refobj=refobj)
                return_inst_list.append(refi)
                if flag_recursive is True:
                    if not i == len_inst-1:
                        _refinstname[i+1] = refi.name
            return return_inst_list
        else: # single placement
            ### preprocessing starts ###
            if shape is None:
                _shape = np.array([1, 1])
            else:
                _shape = np.asarray(shape)
            if not spacing == None: spacing = np.asarray(spacing)
            xy = np.asarray(xy)
            offset = np.asarray(offset)
            if not libname is None:
                template_libname = libname
            if template_libname is None:
                template_libname = self.templates.plib
            ### preprocessing ends ###
            t_size_grid = self.get_template_xy(templatename, gridname, libname=template_libname)
            t_size_grid = t_size_grid*_shape
            #reference instance check
            if (refobj is None) and (refinstname is None):
                ir_xy_grid = np.array([0, t_size_grid[1]/2.0])
                tr_size_grid = np.array([0, 0])
                mtr = ut.Mt('R0')
                mti = ut.Mt('R0')
            else:
                if not refobj is None:
                    if isinstance(refobj, Instance):
                        ir = refobj
                    elif isinstance(refobj, InstanceArray):
                        ir = refobj
                    elif isinstance(refobj, Pointer):
                        ir = refobj.master
                        direction = refobj.name
                else:
                    ir = self.get_inst(refinstname)
                tr = self.templates.get_template(ir.cellname, libname=ir.libname)
                #get abstract grid coordinates
                ir_xy_grid = self.get_absgrid_xy(gridname, ir.xy)
                tr_size_grid = self.get_absgrid_xy(gridname, tr.size+(ir.shape-np.array([1,1]))*ir.spacing)
                mtr = ut.Mt(ir.transform)
                mti = ut.Mt(transform)
            #direction
            md = ut.Md(direction)
            i_xy_grid = ir_xy_grid + 0.5 * (np.dot(tr_size_grid, mtr.T) + np.dot(tr_size_grid + t_size_grid, md.T)
                                            - np.dot(t_size_grid, mti.T))
            return GridLayoutGenerator.place(self, name=name, templatename=templatename, gridname=gridname, xy=i_xy_grid+xy, offset=offset,
                              template_libname=template_libname, shape=shape, spacing=spacing, transform=transform)

    def via(self, name=None, xy=np.array([0, 0]), gridname=None, refobj=None, refobjindex=np.array([0, 0]), offset=np.array([0, 0]), refinstname=None, refinstindex=np.array([0, 0]),
            refpinname=None, transform='R0', overwrite_xy_phy=None, overlay=None):
        """
        Place a via on abstract grid, bound from a reference object. If reference object is not specified,
        [0, 0]+offset is used as the reference point.

        Parameters
        ----------
        name : str
            Name of the via
        xy : np.array([int, int]) or [int, int]
            xy coordinate of the via
        gridname : str
            Grid name of the via
        refobj : LayoutObject.LayoutObject
            Reference object(Instance/Pin/Rect) handle. If None, refinstiname is used.
        overlay : LayoutObject.LayoutObject
            Layout object for via placement at intersection (via will be placed at the overlaid point btn refobj and overlay)
            Use with refobj only. Not compatible with legacy reference parameters (refinstname)
        transform : str ('R0', 'MX', 'MY'), optional
            Transform parameter for grid. Overwritten by transform of refinstname if not specified.

        Returns
        -------
        laygo.layoutObject.Instance
            generated via instance

        Other Parameters
        ----------------
        offset : np.array([float, float]), optional
            Offset on the physical grid, bound from xy
        overwrite_xy_phy : None or np.array([float, float]), optional
            If specified, final xy physical coordinates are overwritten by the argument.
        refobjindex : np.array([int, int]), optional, deprecated
            Index of refobj if it is a mosaic instance.
        refinstname : str, optional, deprecated
            Reference instance name for xy. If None, origin([0,0]) is used as the reference point.
        refinstindex : str, optional, deprecated
            Index of refinstname if it is a mosaic instance
        refpinname : str, optional, deprecated
            Reference pin of refinstname for reference point of xy. If None, the origin of refinstname0 is used.

        """
        if isinstance(refobj, np.ndarray) or isinstance(overlay, np.ndarray): #mutiple placement
            if isinstance(refobj, np.ndarray) and isinstance(overlay, np.ndarray): #both array
                _refobj = refobj.flat
                _overlay = overlay.flat
            elif isinstance(refobj, np.ndarray):
                _refobj = refobj.flat
                _overlay = np.empty(refobj.shape, dtype=overlay.__class__)
                for i, o in np.ndenumerate(_overlay):
                    _overlay[i] = overlay
                _overlay = _overlay.flat
            elif isinstance(overlay, np.ndarray):
                _overlay = overlay.flat
                _refobj = np.empty(overlay.shape, dtype=refobj.__class__)
                for i, o in np.ndenumerate(_refobj):
                    _refobj[i] = refobj
                _refobj = _refobj.flat
            return_via_list = []
            for r0, o0 in zip(_refobj, _overlay):
                refv = GridLayoutGenerator.via(self, name=name, xy=xy, gridname=gridname, refobj=r0, offset=offset, transform=transform,
                                overwrite_xy_phy=overwrite_xy_phy, overlay=o0)
                return_via_list.append(refv)
            return return_via_list
        else:
            ### preprocessing arguments starts ###
            xy = np.asarray(xy)
            offset = np.asarray(offset)
            refinstindex = np.asarray(refinstindex)
            # reading coordinate information from the reference objects
            # this needs to be cleaned up
            refinst = None
            refrect0 = None
            refrect1 = None
            if not refobj is None:
                if isinstance(refobj, Instance):
                    refinst = refobj
                    refinstindex=refobjindex
                elif isinstance(refobj, InstanceArray):
                    refinst = refobj
                    refinstindex=refobjindex
                elif isinstance(refobj, Pin):
                    refinst = refobj.master
                    refinstindex=refobjindex
                    refpinname=refobj.name
                elif isinstance(refobj, Rect):
                    refrect0 = refobj
            else:
                if not refinstname is None:
                    refinst = self.get_inst(refinstname)
            if not overlay is None:
                if isinstance(overlay, Rect):
                    refrect1 = overlay

            ### preprocessing arguments ends ###
            # get physical grid coordinates
            # need to be refactored
            if not refinst is None:
                reftemplate = self.templates.get_template(refinst.cellname, libname=refinst.libname)
                offset = offset + refinst.xy + np.dot(refinst.spacing * refinstindex, ut.Mt(refinst.transform).T)
                if not refpinname == None: #if pin reference is specified
                    pin_xy_phy=reftemplate.pins[refpinname]['xy']
                    bbox=pin_xy_phy
                    if not refrect1 is None: #overlay
                        bbox0=pin_xy_phy
                        bbox1=np.dot(refrect1.xy - refinst.xy, ut.Mtinv(refinst.transform).T)
                        sx=sorted([bbox0[0][0], bbox0[1][0], bbox1[0][0], bbox1[1][0]])
                        sy=sorted([bbox0[0][1], bbox0[1][1], bbox1[0][1], bbox1[1][1]])
                        bbox=np.array([[sx[1], sy[1]], [sx[2], sy[2]]])
                    #pin_xy_abs=self.get_absgrid_region(gridname, pin_xy_phy[0], pin_xy_phy[1])[0,:]
                    pin_xy_abs=self.get_absgrid_region(gridname, bbox[0], bbox[1])[0,:]
                    xy=xy+pin_xy_abs
                transform=refinst.transform #overwrite transform variable
            if not refrect0 is None:
                xy=xy+self.get_absgrid_region(gridname, refrect0.xy0, refrect0.xy1)[0,:]
                if not refrect1 is None:
                    #TODO: implement overlay function using refrect1
                    pass

            vianame = self.grids.get_vianame(gridname, xy)
            if overwrite_xy_phy is None:
                xy_phy=np.dot(self.grids.get_phygrid_xy(gridname, xy), ut.Mt(transform).T)+offset
            else:
                xy_phy=overwrite_xy_phy
            inst=self.add_inst(name=name, libname=self.grids.plib, cellname=vianame, xy=xy_phy, transform=transform)
            if self.use_phantom==True:
                size=self.grids.get_route_width_xy(gridname, xy)
                self.add_rect(None, xy=np.vstack((xy_phy-0.5*size, xy_phy+0.5*size)),
                              layer=self.layers['text'])
                self.add_text(None, text=vianame, xy=xy_phy, layer=self.layers['text'])
            return inst

    # Route functions
    def route(self, name=None, layer=None, xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=None, gridname1=None, direction='omni',
              refobj0=None, refobj1=None, refobjindex0=np.array([0, 0]), refobjindex1=np.array([0, 0]),
              refinstname0=None, refinstname1=None, refinstindex0=np.array([0, 0]), refinstindex1=np.array([0, 0]),
              refpinname0=None, refpinname1=None, offset0=np.array([0,0]), offset1=None,
              transform0='R0', transform1=None, endstyle0="truncate", endstyle1="truncate",
              via0=None, via1=None, netname=None):
        """
        Route on abstract grid, bound from reference objects. If reference objects are not specified,
        [0, 0]+offset is used as reference points.
        This function is a bit messy because originally its main arguments were refinst/refinstindex/refpinname,
        and switched to refobj/refobjindex, and to refobj only. At some point all the codes need to be rewritten.

        Parameters
        ----------
        name : str
            Route name. If None, the name will be automatically assigned by genid.
        layer : [str, str], optional
            Routing layer [name, purpose]. If None, it figures out the layer from grid and coordinates
        xy0 : np.array([int, int]) or [int, int]
            xy coordinate for start point.
        xy1 : np.array([int, int]) or [int, int]
            xy coordinate for end point.
        gridname0 : str
            Grid name0
        gridname1 : str, optional
            Grid name1
        direction : str, optional
            Routing direction (omni, x, y, ...). It will be used as the input argument of GridLayoutGenerator.Md.
        refobj0 : LayoutObject.LayoutObject
            Reference object(Instance/Pin/Rect) handle. If None, refinstiname0 is used.
        refobj1 : LayoutObject.LayoutObject
            Reference object(Instance/Pin/Rect) handle. If None, refinstiname1 is used.
        transform0 : str, optional
            Transform parameter for grid0. Overwritten by transform of refinstname0 if not specified.
        transform1 : str, optional
            Transform parameter for grid1. Overwritten by transform of refinstname1 if not specified.
        endstyle0 : str ('extend', 'truncate'), optional
            End style of xy0 (extend the edge by width/2 if endstyle=='extend')
        endstyle1 : str ('extend', 'truncate'), optional
            End style of xy1 (extend the edge by width/2 if endstyle=='extend')
        via0 : None or np.array([x, y]) or np.array([[x0, y0], [x1, y1], [x2, y2], ...]), optional
            Offset coordinates for via placements, bound from xy0
            ex) if xy0 = [1, 2], xy1 = [1, 5], via0 = [0, 2] then a via will be placed at [1, 4]
        via1 : None or np.array([x, y]) or np.array([[x0, y0], [x1, y1], [x2, y2], ...]), optional
            Offset coordinates for via placements, bound from xy1
            ex) if xy0 = [1, 2], xy1 = [1, 5], via1 = [0, 2] then a via will be placed at [1, 7]
        netname : str, optional
            net name of the route

        Returns
        -------
        laygo.layoutObject.Rect
            generated route

        Other Parameters
        ----------------
        offset0 : np.array([float, float]), optional
            Coordinate offset from xy0, on the physical grid.
        offset1 : np.array([float, float]), optional
            Coordinate offset from xy1, on the physical grid.
        refobjindex0 : np.array([int, int]), optional, deprecated
            Index of refobj0 if it is a mosaic instance.
        refobjindex1 : np.array([int, int]), optional, deprecated
            Index of refobj1 if it is a mosaic instance.
        refinstname0 : str, optional, deprecated
            Reference instance name for start point. If None, origin([0,0]) is used as the reference point.
        refinstname1 : str, optional, deprecated
            Reference instance name for end point. If None, origin([0,0]) is used as the reference point.
        refinstindex0 : np.array([int, int]), optional, deprecated
            Index of refinstname0 if it is a mosaic instance.
        refinstindex1 : np.array([int, int]), optional, deprecated
            Index of refinstname1 if it is a mosaic instance.
        refpinname0 : str, optional, deprecated
            Reference pin of refinstname0 for reference point of xy0. If None, the origin of refinstname0 is used.
        refpinname1 : str, optional, deprecated
            Reference pin of refinstname1 for reference point of xy1. If None, the origin of refinstname1 is used.
        """
        bool_r0 = isinstance(refobj0, np.ndarray) or isinstance(refobj0, InstanceArray)
        bool_r1 = isinstance(refobj1, np.ndarray) or isinstance(refobj1, InstanceArray)
        if bool_r0 or bool_r1: #mutiple placement
            if bool_r0 and bool_r1: #both array
                _refobj0 = refobj0.flat
                _refobj1 = refobj1.flat
            elif bool_r0:
                _refobj0 = refobj0.flat
                _refobj1 = np.empty(refobj0.shape, dtype=refobj1.__class__)
                for i, o in np.ndenumerate(_refobj1):
                    _refobj1[i] = refobj1
                _refobj1 = _refobj1.flat
            elif bool_r1:
                _refobj1 = refobj1.flat
                _refobj0 = np.empty(refobj1.shape, dtype=refobj0.__class__)
                for i, o in np.ndenumerate(_refobj0):
                    _refobj0[i] = refobj0
                _refobj0 = _refobj0.flat
            return_rect_list = []
            for r0, r1 in zip(_refobj0, _refobj1):
                refr = GridLayoutGenerator.route(self, name=name, layer=layer, xy0=xy0, xy1=xy1, gridname0=gridname0,
                                  gridname1=gridname1, direction=direction, refobj0=r0, refobj1=r1,
                                  offset0=offset0, offset1=offset1, transform0=transform0, transform1=transform1,
                                  endstyle0=endstyle0, endstyle1=endstyle1, via0=via0, via1=via1, netname=netname) 
                #Used GridLayoutGenerator for abstracting the function in GridLayoutGenerator2
                return_rect_list.append(refr)
            return return_rect_list
        else:
            # exception handling
            if xy0 is None: raise ValueError('GridLayoutGenerator.route - specify xy0')
            if xy1 is None: raise ValueError('GridLayoutGenerator.route - specify xy1')
            if gridname0 is None: raise ValueError('GridLayoutGenerator.route - specify gridname0')
            ### preprocessing arguments starts ###
            xy0 = np.asarray(xy0)
            xy1 = np.asarray(xy1)
            refinstindex0 = np.asarray(refinstindex0)
            refinstindex1 = np.asarray(refinstindex1)
            refinst0 = None
            refinst1 = None
            offset0 = np.asarray(offset0)
            if not offset1 is None: offset1 = np.asarray(offset1)
            if gridname1 == None: gridname1 = gridname0
            if not isinstance(offset1,np.ndarray): offset1 = offset0
            if transform1 == None: transform1 = transform0
            if not via0 is None:
                if isinstance(via0[0], (int, np.int64)):
                    via0=[via0]
                via0 = np.asarray(via0)
            if not via1 is None:
                if isinstance(via1[0], (int, np.int64)): #convert 1-dim array to 2-dim array
                    via1=[via1]
                via1 = np.asarray(via1)
            ### preprocessing arguments ends ###
            _xy0=xy0
            _xy1=xy1
            _offset0=offset0
            _offset1=offset1
            _xy0_pointer_scale = np.array([0, 0])  # [0, 0] means lower_left
            _xy1_pointer_scale = np.array([0, 0])  # [0, 0] means lower_left
            # reading coordinate information from the reference objects
            # this if routines + refinst stuff needs to be cleaned up, very redunda t
            if not refobj0 is None:
                if isinstance(refobj0, Instance):
                    refinst0=refobj0
                    refinstname0=refobj0.name
                    refinstindex0=refobjindex0
                if isinstance(refobj0, InstanceArray):
                    refinst0=refobj0
                    refinstname0=refobj0.name
                    refinstindex0=refobjindex0
                if isinstance(refobj0, Rect):
                    refinst0=refobj0 #this is hack; we need to completely rewrite the route function at some point
                    refinstname0=refobj0.name
                    refinstindex0=np.array([0, 0])
                    refpinname0=None
                if isinstance(refobj0, Pin):
                    refinst0=refobj0.master
                    refinstname0=refobj0.master.name
                    refinstindex0=refobjindex0
                    refpinname0=refobj0.name
                if isinstance(refobj0, Pointer):
                    if isinstance(refobj0.master, InstanceArray):
                        refinst0 = refobj0.master[0, 0]
                        refinstname0=refobj0.master.name
                        refinstindex0=refobjindex0
                        _xy0_pointer_scale=refobj0.xy
                    elif isinstance(refobj0.master, Instance):
                        refinst0 = refobj0.master
                        refinstname0=refobj0.master.name
                        refinstindex0=refobjindex0
                        _xy0_pointer_scale=refobj0.xy
                    elif isinstance(refobj0.master, Rect):
                        refinst0 = refobj0.master
                        refinstname0=refobj0.master.name
                        refinstindex0=np.array([0, 0])
                        _xy0_pointer_scale=refobj0.xy
                    elif isinstance(refobj0.master, Pin):
                        refinst0 = refobj0.master.master
                        refinstname0 = refobj0.master.master.name
                        refinstindex0 = refobjindex0
                        refpinname0 = refobj0.master.name
                        _xy0_pointer_scale = refobj0.xy
                    else:
                        refinst0 = refobj0.master
                        refinstname0=refobj0.master.name
                        refinstindex0=refobjindex0
                        _xy0_pointer_scale=refobj0.xy
            else:
                if not (refinstname0 is None):
                    refinst0=self.get_inst(refinstname0)
            if not refobj1 is None:
                if isinstance(refobj1, Instance):
                    refinst1=refobj1
                    refinstname1=refobj1.name
                    refinstindex1=refobjindex1
                if isinstance(refobj1, InstanceArray):
                    refinst1=refobj1
                    refinstname1=refobj1.name
                    refinstindex1=refobjindex1
                if isinstance(refobj1, Rect):
                    refinst1=refobj1 #this is hack; we need to completely rewrite the route function at some point
                    refinstname1=refobj1.name
                    refinstindex1=np.array([0, 0])
                    refpinname1=None
                if isinstance(refobj1, Pin):
                    refinst1=refobj1.master
                    refinstname1=refobj1.master.name
                    refinstindex1=refobjindex1
                    refpinname1=refobj1.name
                if isinstance(refobj1, Pointer):
                    if isinstance(refobj1.master, InstanceArray):
                        refinst1 = refobj1.master[0, 0]
                        refinstname1 = refobj1.master.name
                        refinstindex1 = refobjindex1
                        _xy1_pointer_scale = refobj1.xy
                    elif isinstance(refobj1.master, Instance):
                        refinst1 = refobj1.master
                        refinstname1 = refobj1.master.name
                        refinstindex1 = refobjindex1
                        _xy1_pointer_scale = refobj1.xy
                    elif isinstance(refobj1.master, Rect):
                        refinst1 = refobj1.master
                        refinstname1 = refobj1.master.name
                        refinstindex1 = np.array([0, 0])
                        _xy1_pointer_scale = refobj1.xy
                    elif isinstance(refobj1.master, Pin):
                        refinst1 = refobj1.master.master
                        refinstname1 = refobj1.master.master.name
                        refinstindex1 = refobjindex1
                        refpinname1 = refobj1.master.name
                        _xy1_pointer_scale = refobj1.xy
                    else:
                        refinst1 = refobj1.master
                        refinstname1=refobj1.master.name
                        refinstindex1=refobjindex1
                        _xy1_pointer_scale=refobj1.xy
            else:
                if not (refinstname1 is None):
                    refinst1=self.get_inst(refinstname1)

            #compute abstract coordinates
            if not (refinstname0 is None):
                if isinstance(refinst0, Rect): #hack to support Rect objects and Pointer objects of Rect objects
                    _xy_rect0 = self.get_xy(obj=refinst0, gridname=gridname0, sort=False)
                    _xy0 = _xy0 + _xy_rect0[0]
                    # pointer
                    _xy0_pointer_abs = _xy0_pointer_scale * (_xy_rect0[1] - _xy_rect0[0])
                    _xy0_pointer_abs = _xy0_pointer_abs.astype(int)
                    _xy0 = _xy0 + _xy0_pointer_abs
                else: #Instances
                    #instance offset
                    reftemplate0=refinst0.template #self.templates.get_template(refinst0.cellname, libname=refinst0.libname)
                    _offset0=offset0+refinst0.xy+np.dot(refinst0.spacing*refinstindex0, ut.Mt(refinst0.transform).T)
                    #pointer and pin
                    if refpinname0 is None: # not pin
                        # pointer
                        _xy0_pointer_abs = np.dot(
                            _xy0_pointer_scale * self.get_xy(obj=reftemplate0, gridname=gridname0) * refinst0.shape,
                            ut.Mt(refinst0.transform).T)
                        _xy0_pointer_abs = _xy0_pointer_abs.astype(int)
                        _xy0 = _xy0 + _xy0_pointer_abs
                    else: #pin
                        pin_xy_abs = self.get_template_pin_xy(reftemplate0.name, refpinname0, gridname0, libname=refinst0.libname)
                        #pin location
                        pin_xy0_abs = pin_xy_abs[0, :]
                        _xy0 = _xy0 + pin_xy0_abs
                        #pointer
                        pin_size_abs = pin_xy_abs[1, :] - pin_xy_abs[0, :]
                        _xy0_pointer_abs = _xy0_pointer_scale * pin_size_abs #np.dot(_xy0_pointer_scale * pin_size_abs, ut.Mt(refinst0.transform).T)
                        _xy0_pointer_abs = _xy0_pointer_abs.astype(int)
                        _xy0 = _xy0 + _xy0_pointer_abs
                    transform0=refinst0.transform # overwrite transform variable
            if not (refinstname1 is None):
                if isinstance(refinst1, Rect): #hack to support Rect objects and Pointer objects of Rect objects
                    _xy_rect1 = self.get_xy(obj=refinst1, gridname=gridname1, sort=False)
                    _xy1 = _xy1 + _xy_rect1[0]
                    # pointer
                    _xy1_pointer_abs = _xy1_pointer_scale * (_xy_rect1[1] - _xy_rect1[0])
                    _xy1_pointer_abs = _xy1_pointer_abs.astype(int)
                    _xy1 = _xy1 + _xy1_pointer_abs
                else:
                    #instance offset
                    reftemplate1=refinst1.template #self.templates.get_template(refinst1.cellname, libname=refinst1.libname)
                    _offset1=offset1+refinst1.xy+np.dot(refinst1.spacing*refinstindex1, ut.Mt(refinst1.transform).T)
                    #pointer and pin
                    if refpinname1 is None: # not pin
                        # pointer
                        _xy1_pointer_abs = np.dot(
                            _xy1_pointer_scale * self.get_xy(obj=reftemplate1, gridname=gridname1) * refinst1.shape,
                            ut.Mt(refinst1.transform).T)
                        _xy1_pointer_abs = _xy1_pointer_abs.astype(int)
                        _xy1 = _xy1 + _xy1_pointer_abs
                    else:
                        pin_xy_abs = self.get_template_pin_xy(reftemplate1.name, refpinname1, gridname1, libname=refinst1.libname)
                        #pin location
                        pin_xy1_abs = pin_xy_abs[0, :]
                        _xy1 = _xy1 + pin_xy1_abs
                        #pointer
                        pin_size_abs = pin_xy_abs[1, :] - pin_xy_abs[0, :]
                        _xy1_pointer_abs = _xy1_pointer_scale * pin_size_abs #np.dot(_xy1_pointer_scale * pin_size_abs, ut.Mt(refinst1.transform).T)
                        _xy1_pointer_abs = _xy1_pointer_abs.astype(int)
                        _xy1 = _xy1 + _xy1_pointer_abs
                    transform1=refinst1.transform # overwrite transform variable

            # get physical grid coordinates
            xy_phy, xy_phy_center=self._route_generate_box_from_abscoord(xy0=_xy0, xy1=_xy1, gridname0=gridname0, gridname1=gridname1,
                                                          direction=direction, offset0=_offset0, offset1=_offset1,
                                                          transform0=transform0, transform1=transform1,
                                                          endstyle0=endstyle0, endstyle1=endstyle1)
            xy0_phy=xy_phy[0,:]; xy1_phy=xy_phy[1,:]
            xy0_phy_center=xy_phy_center[0,:]; xy1_phy_center=xy_phy_center[1,:]
            # optional via placements
            if not via0 is None:
                for vofst in via0:
                    if isinstance(refinst0, Rect): #hact to support Rect objects and Pointer objects of Rect objects
                        GridLayoutGenerator.via(self, None, _xy0, gridname0, offset=offset0, refobj=None, refobjindex=None,
                                 refpinname=None, transform=transform0)
                    else:
                        GridLayoutGenerator.via(self, None, xy0+vofst, gridname0, offset=offset0, refobj=refinst0, refobjindex=refinstindex0,
                                 refpinname=refpinname0, transform=transform0)
            if not via1 is None:
                for vofst in via1:
                    #overwrite xy coordinate to handle direction matrix (xy1+vofst does not reflect direction matrix in via function)
                    if direction=='omni':
                        if isinstance(refinst1, Rect): #hact to support Rect objects and Pointer objects of Rect objects
                            GridLayoutGenerator.via(self, None, _xy1, gridname1, offset=offset1, refobj=None, refobjindex=None,
                                     refpinname=None, transform=transform1)
                        else:
                            GridLayoutGenerator.via(self, None, xy1 + vofst, gridname1, offset=offset1, refobj=refinst1,
                                     refobjindex=refinstindex1, refpinname=refpinname1, transform=transform1)
                    else:
                        if isinstance(refinst1, Rect): #hact to support Rect objects and Pointer objects of Rect objects
                            GridLayoutGenerator.via(self, None, _xy1, gridname1, offset=offset1, refobj=None, refobjindex=None,
                                     refpinname=None, transform=transform1)
                        else:
                            _xy1=self.get_absgrid_xy(gridname=gridname1, xy=xy1_phy_center, refobj=refinst1,
                                                     refobjindex=refinstindex1, refpinname=refpinname1)
                            GridLayoutGenerator.via(self, None, _xy1, gridname1, offset=offset1, refobj=refinst1, refobjindex=refinstindex1,
                                     refpinname=refpinname1, transform=transform1)
            #layer handling
            if layer is None:
                #if xy0_phy_center[0] == xy1_phy_center[0]: #not accurate sometimes..
                if int(round(xy0_phy_center[0]/self.res)) == int(round(xy1_phy_center[0]/self.res)):
                    layer = self.grids.get_route_xlayer_xy(gridname0, _xy0)
                else:
                    layer = self.grids.get_route_ylayer_xy(gridname0, _xy0)
            return self.add_rect(name, np.vstack((xy0_phy, xy1_phy)), layer, netname)

    def _route_generate_box_from_abscoord(self, xy0, xy1, gridname0, gridname1=None, direction='omni',
                                          offset0=np.array([0, 0]), offset1=None, transform0='R0', transform1=None,
                                          endstyle0="truncate", endstyle1="truncate"):
        """
        Internal function for routing and pinning.
        Generate a rectangular box from 2 points on abstract grid.
        The thickness corresponds to the width parameter of gridname0
        Parameters
        ----------
        name : str
            route name. If None, automatically assigned by genid
        layer : [str, str]
            routing layer [name, purpose]
        xy0 : np.array([int, int])
            xy coordinate for start point
        xy1 : np.array([int, int])
            xy coordinate for end point
        gridname0 : str
            grid name0
        gridname1 : str
            grid name1
        direction : str
            routing direction (omni, x, y, ...) - matrix set by Md
        offset0 : np.array([float, float])
            offset of xy0
        offset1 : np.array([float, float])
            offset of xy1
        transform0 : str
            grid transform information of grid0. Overwritten by transform of refinstname0 if specified
        transform1 : str
            grid transform information of grid1. Overwritten by transform of refinstname1 if specified
        endstyle0 : str (extend, truncate)
            end style of xy0 (extend the edge by width/2 if endstyle="extend")
        endstyle1 : str (extend, truncate)
            end style of xy1 (extend the edge by width/2 if endstyle="extend")
        Returns
        -------
        np.array([[x0, y0], [x1, y1]])
            derived coordinates
        """
        if gridname1 == None: gridname1 = gridname0
        if not isinstance(offset1,np.ndarray): offset1 = offset0
        if transform1 == None: transform1 = transform0
        xy0_phy=np.dot(self.grids.get_phygrid_xy(gridname0, xy0), ut.Mt(transform0).T)+offset0
        xy1_phy=np.dot(self.grids.get_phygrid_xy(gridname1, xy1), ut.Mt(transform1).T)+offset1
        md=ut.Md(direction)
        xy1_phy=np.dot(xy1_phy - xy0_phy, md.T) + xy0_phy #adjust xy1_phy to fix routing direction
        if not (xy0_phy==xy1_phy).all(): #xy0_phy and xy1_phy should not be the same
            #generating a rect object by extending in normal directions by width/2 (grid0 is used for route width)
            vwidth_direction=np.dot((xy1_phy - xy0_phy)/np.linalg.norm(xy1_phy - xy0_phy), ut.Mt('MXY').T)
            vwidth_norm=0.5*self.grids.get_route_width_xy(gridname0, xy0)
            vwidth=vwidth_direction*vwidth_norm
            #endstyles
            vextend0=np.array([0, 0])
            if endstyle0 == "extend":
                vextend_direction = (xy1_phy - xy0_phy) / np.linalg.norm(xy1_phy - xy0_phy)
                vextend_norm = 0.5 * self.grids.get_route_width_xy(gridname0, xy0)
                vextend0=vextend_direction*vextend_norm
            vextend1 = np.array([0, 0])
            if endstyle1 == "extend":
                vextend_direction = (xy1_phy - xy0_phy) / np.linalg.norm(xy1_phy - xy0_phy)
                vextend_norm = 0.5 * self.grids.get_route_width_xy(gridname0, xy0)
                vextend1 = vextend_direction * vextend_norm
            _xy0_phy_center = xy0_phy
            _xy1_phy_center = xy1_phy
            _xy0_phy = xy0_phy - vwidth - vextend0
            _xy1_phy = xy1_phy + vwidth + vextend1
        else: #2 coordinates match (-no routes)
            _xy0_phy = xy0_phy
            _xy1_phy = xy1_phy
            _xy0_phy_center = xy0_phy
            _xy1_phy_center = xy1_phy
        return np.vstack((_xy0_phy, _xy1_phy)), np.vstack((_xy0_phy_center, _xy1_phy_center))

    #advanced route functions
    def route_vh(self, layerv=None, layerh=None, xy0=None, xy1=None, gridname0=None, gridname1=None,
                 refinstname0=None, refinstname1=None, refinstindex0=np.array([0, 0]), refinstindex1=np.array([0, 0]),
                 refpinname0=None, refpinname1=None, endstyle0=['truncate', 'truncate'],
                 endstyle1=['truncate', 'truncate'], via0=None, via1=None, gridname=None):
        """
        Vertical-horizontal route function
        Parameters
        ----------
        layerv : [str, str]
            Vertical route layer name and purpose
        layerh : [str, str]
            Horizontal route layer name and purpose
        xy0 : np.array([int, int])
            First coordinate
        xy1 : np.array([int, int])
            Second coordinate
        gridname : str, optional
            (Obsolete) Grid name. Use gridname0 instead
        gridname0 : str
            Gridname for xy0
        gridname1 : str, optional
            Gridname for xy1. If None, gridname0 is used
        refinstname0 : str, optional
            Reference instance name for xy0
        refinstname1 : str, optional
            Reference instance name for xy1
        refinstindex0 : str, optional
            Reference instance index for xy0
        refinstindex1 : str, optional
            Reference instance index for xy1
        refpinname0 : str, optional
            Reference pin name for xy0
        refpinname1 : str, optional
            Reference pin name for xy1
        via0 : np.array([x0, y0], [x1, y1], ...), optional
            Via attach coordinates. Offsets from xy0
        via1 : np.array([x0, y0], [x1, y1], ...), optional
            Via attach coordinates. Offsets from xy1
        Returns
        -------
        [laygo.layoutObject.Rect, laygo.layoutObject.Rect]
            generated routes (vertical, horizontal)
        """
        #TODO: support refobj instead of refinstname/refpinname
        xy0 = np.asarray(xy0)
        xy1 = np.asarray(xy1)
        xy0 = np.asarray(xy0)
        xy1 = np.asarray(xy1)
        if not gridname is None:
            print("gridname in GridLayoutGenerator.route_vh deprecated. Use gridname0 instead")
            gridname0 = gridname
        if gridname1 is None:
            gridname1 = gridname0
        # Used GridLayoutGenerator for abstracting the function in GridLayoutGenerator2
        rv0 = GridLayoutGenerator.route(self, name=None, layer=layerv, xy0=xy0, xy1=xy1, direction='y', gridname0=gridname0,
                         refinstname0=refinstname0, refinstindex0=refinstindex0, refpinname0=refpinname0,
                         refinstname1=refinstname1, refinstindex1=refinstindex1, refpinname1=refpinname1,
                         endstyle0=endstyle0[0], endstyle1=endstyle1[0], via0=via0, via1=np.array([[0, 0]]))
        rh0 = GridLayoutGenerator.route(self, name=None, layer=layerh, xy0=xy1, xy1=xy0, direction='x', gridname0=gridname1,
                         refinstname0=refinstname1, refinstindex0=refinstindex1, refpinname0=refpinname1,
                         refinstname1=refinstname0, refinstindex1=refinstindex0, refpinname1=refpinname0,
                         endstyle0=endstyle0[1], endstyle1=endstyle1[1], via0=via1)
        return [rv0, rh0]

    def route_hv(self, layerh=None, layerv=None, xy0=None, xy1=None, gridname0=None, gridname1=None,
                 refinstname0=None, refinstname1=None, refinstindex0=np.array([0, 0]), refinstindex1=np.array([0, 0]),
                 refpinname0=None, refpinname1=None, endstyle0=['truncate', 'truncate'],
                 endstyle1=['truncate', 'truncate'], via0=None, via1=None, gridname=None):
        """
        Horizontal-vertical route function
        Parameters
        ----------
        layerh : [str, str]
            Horizontal route layer name and purpose
        layerv : [str, str]
            Vertical route layer name and purpose
        xy0 : np.array([int, int])
            First coordinate
        xy1 : np.array([int, int])
            Second coordinate
        gridname : str
            (Obsolete) Grid name. Use gridname0 instead
        gridname0 : str
            Gridname for xy0
        gridname1 : str, optional
            Gridname for xy1. If None, gridname0 is used
        refinstname0 : str, optional
            Reference instance name for xy0
        refinstname1 : str, optional
            Reference instance name for xy1
        refinstindex0 : str, optional
            Reference instance index for xy0
        refinstindex1 : str, optional
            Reference instance index for xy1
        refpinname0 : str, optional
            Reference pin name for xy0
        refpinname1 : str, optional
            Reference pin name for xy1
        via0 : np.array([x0, y0], [x1, y1], ...), optional
            Via attach coordinates. Offsets from xy0
        via1 : np.array([x0, y0], [x1, y1], ...), optional
            Via attach coordinates. Offsets from xy1
        Returns
        -------
        [laygo.layoutObject.Rect, laygo.layoutObject.Rect]
            generated routes (horizontal, vertical)
        """
        #TODO: support refobj instead of refinstname/refpinname

        xy0=np.asarray(xy0)
        xy1=np.asarray(xy1)
        if not gridname is None:
            print("gridname in GridLayoutGenerator.route_hv deprecated. Use gridname0 instead")
            gridname0 = gridname
        if gridname1 is None:
            gridname1 = gridname0
        # Used GridLayoutGenerator for abstracting the function in GridLayoutGenerator2
        rh0=GridLayoutGenerator.route(self, name=None, layer=layerh, xy0=xy0, xy1=xy1, direction='x', gridname0=gridname0,
                       refinstname0=refinstname0, refinstindex0=refinstindex0, refpinname0=refpinname0,
                       refinstname1=refinstname1, refinstindex1=refinstindex1, refpinname1=refpinname1,
                       endstyle0=endstyle0[0], endstyle1=endstyle1[0], via0=via0, via1=np.array([[0, 0]]))
        rv0=GridLayoutGenerator.route(self, name=None, layer=layerv, xy0=xy1, xy1=xy0, direction='y', gridname0=gridname1,
                       refinstname0=refinstname1, refinstindex0=refinstindex1, refpinname0=refpinname1,
                       refinstname1=refinstname0, refinstindex1=refinstindex0, refpinname1=refpinname0,
                       endstyle0=endstyle0[1], endstyle1=endstyle1[1], via0=via1)
        return [rh0, rv0]

    def route_vhv(self, layerv0=None, layerh=None, xy0=[0, 0], xy1=[0, 0], track_y=0, gridname0=None, layerv1=None, gridname1=None,
                  extendl=0, extendr=0, gridname=None):
        """
        Vertical-horizontal-vertical route function
        Parameters
        ----------
        layerv0 : [str, str]
            First vertical route layer name and purpose
        layerh : [str, str]
            Horizontal route layer name and purpose
        xy0 : np.array([int, int])
            First coordinate
        xy1 : np.array([int, int])
            Second coordinate
        track_y : int
            Y-coordinate for horizontal route
        gridname : str, optional
            (Obsolete) Grid name. Use gridname0 instead
        gridname0 : str
            Gridname for xy0
        layerv1 : [str, str], optional
            Second vertical route layer name and purpose. If None, layer0 is used.
        gridname1 : str, optional
            Gridname for xy1. If None, gridname0 is used
        extendl : int
            Extension parameter in left direction
        extendr : int
            Extension parameter in right direction
        Returns
        -------
        [laygo.layoutObject.Rect, laygo.layoutObject.Rect, laygo.layoutObject.Rect]
            generated routes (vertical, horizontal, vertical)
        """
        #TODO: support refobj
        xy0=np.asarray(xy0)
        xy1=np.asarray(xy1)
        if layerv1==None:
            layerv1=layerv0
        if not gridname is None:
            print("gridname in GridLayoutGenerator.route_vhv deprecated. Use gridname0 instead")
            gridname0 = gridname
        if gridname1 is None:
            gridname1 = gridname0
        if xy0[0]<xy1[0]: #extend horizontal route
            xy0_0 = xy0[0] - extendl
            xy1_0 = xy1[0] + extendr
        else:
            xy0_0 = xy0[0] + extendr
            xy1_0 = xy1[0] - extendl

        #resolve grid mismatch and do horizontal route
        xy1_grid0=self.grids.get_phygrid_xy(gridname0, xy1)
        xy1_grid1=self.grids.get_phygrid_xy(gridname1, xy1)
        # Used GridLayoutGenerator for abstracting the function in GridLayoutGenerator2
        if not xy1_grid0[0]==xy1_grid1[0]: #xy1[0] mismatch
            rh0 = GridLayoutGenerator.route(self, layer=layerh, xy0=np.array([xy0_0, track_y]), xy1=np.array([xy1_0, track_y]),
                             gridname0=gridname0, offset1=np.array([xy1_grid1[0] - xy1_grid0[0], 0]))
        else:
            rh0 = GridLayoutGenerator.route(self, layer=layerh, xy0=np.array([xy0_0, track_y]), xy1=np.array([xy1_0, track_y]),
                             gridname0=gridname0)
        rv0=None;rv1=None
        if gridname==gridname1 and xy0[0]==xy1[0]: #no horozontal route/no via
            via0 = None
        else:
            via0 = [[0, 0]]
        if not track_y == xy0[1]:
            rv0=GridLayoutGenerator.route(self, None, layer=layerv0, xy0=np.array([xy0[0], track_y]), xy1=xy0, gridname0=gridname0, via0=via0)
        else:
            GridLayoutGenerator.via(self, None, xy0, gridname=gridname0)
        if not track_y == xy1[1]:
            rv1=GridLayoutGenerator.route(self, None, layer=layerv1, xy0=np.array([xy1[0], track_y]), xy1=xy1, gridname0=gridname1, via0=via0)
        else:
            GridLayoutGenerator.via(self, None, xy1, gridname=gridname0)
        return [rv0, rh0, rv1]

    def route_hvh(self, layerh0=None, layerv=None, xy0=[0, 0], xy1=[0, 0], track_x=0, gridname0=None, layerh1=None, gridname1=None,
                  extendt=0, extendb=0, gridname=None):
        """
        Horizontal-vertical-horizontal route function
        Parameters
        ----------
        layerh0 : [str, str]
            First horizontal route layer name and purpose
        layerv : [str, str]
            Vertical route layer name and purpose
        xy0 : np.array([int, int])
            First coordinate
        xy1 : np.array([int, int])
            Second coordinate
        track_x : int
            X-coordinate for vertical route
        gridname : str, optional
            (Obsolete) Grid name. Use gridname0 instead
        gridname0 : str
            Gridname for xy0
        layerh1 : [str, str], optional
            Second horizontal route layer name and purpose. If None, layer0 is used.
        gridname1 : str, optional
            Gridname for xy1. If None, gridname0 is used
        extendt : int, optional
            Extension parameter in top direction
        extendb : int, optional
            Extension parameter in bottom direction
        Returns
        -------
        [laygo.layoutObject.Rect, laygo.layoutObject.Rect, laygo.layoutObject.Rect]
            generated routes (horizontal, vertical, horizontal)
        """
        #TODO: support refobj
        xy0=np.asarray(xy0)
        xy1=np.asarray(xy1)
        if layerh1==None:
            layerh1=layerh0
        if not gridname is None:
            print("gridname in GridLayoutGenerator.route_hvh deprecated. Use gridname0 instead")
            gridname0 = gridname
        if gridname1 is None:
            gridname1 = gridname0
        if xy0[0]<xy1[0]: #extend vertical route
            xy0_0 = xy0[0] - extendb
            xy1_0 = xy1[0] + extendt
        else:
            xy0_0 = xy0[0] + extendt
            xy1_0 = xy1[0] - extendb

        rv0 = GridLayoutGenerator.route(self, None, layerv, xy0=np.array([track_x, xy0[1]]), xy1=np.array([track_x, xy1[1]]),
                         gridname0=gridname0)
        rh0 = None;rh1 = None
        if not track_x == xy0[0]:
            rh0 = GridLayoutGenerator.route(self, None, layerh0, xy0=xy0, xy1=np.array([track_x, xy0[1]]), gridname0=gridname0, via1=[[0, 0]])
        else:
            GridLayoutGenerator.via(self, None, xy0, gridname=gridname0)
        if not track_x == xy1[0]:
            rh1 = GridLayoutGenerator.route(self, None, layerh1, xy0=np.array([track_x, xy1[1]]), xy1=xy1, gridname0=gridname1, via0=[[0, 0]])
        else:
            GridLayoutGenerator.via(self, None, xy1, gridname=gridname0)
        return [rh0, rv0, rh1]

    #pin creation functions
    def pin(self, name, layer=None, xy=None, gridname=None, netname=None, base_layer=None, refobj=None,
            xy0=np.array([0, 0]), xy1=np.array([0, 0])):
        """
        Pin generation function.
        Parameters
        ----------
        name : str
            pin name
        layer : [str, str], optional
            pin layer, if None, layer of refobj is used (assuming refobj is Rect)
        xy : np.array([[int, int], [int, int]]), optional, deprecated
            xy coordinate. deprecated. use xy0, xy1 instead
        xy0 : np.array([[int, int]), optional
            first coordinate
        xy1 : np.array([[int, int]), optional
            second coordinate
        gridname : str
            grid name
        netname : str
            net name. If None, pin name is used. Used when multiple pin objects are attached to the same net.
        base_layer : [str, str]
            base metal layer. If None, corresponding layer in metal dict is used.
        refobj : LayoutObject.LayoutObject, optional
            reference object handle
        Returns
        -------
        laygo.LayoutObject.Pin
            generated Pin object
        See Also
        --------
        pin_from_rect : generate a Pin from a Rect
        boundary_pin_from_rect : generate a boundary Pin from a Rect
        """
        if xy is None:
            xy = np.array([xy0, xy1])
        else:
            xy = np.asarray(xy)
        if not refobj is None:
            if type(refobj).__name__ is 'Rect':
                xy = self.get_rect_xy(name=refobj.name, gridname=gridname)
                if layer is None:
                    layer=self.layers['pin'][self.layers['metal'].index(refobj.layer)]
        if netname==None: netname=name
        bx1, bx2 = sorted(xy[:,0].tolist())
        by1, by2 = sorted(xy[:,1].tolist())
        #ll = np.array([bx1, by1])  # lower-left
        #ur = np.array([bx2, by2])  # upper-right
        xy_phy, xy_phy_center=self._route_generate_box_from_abscoord(xy0=xy[0,:], xy1=xy[1,:], gridname0=gridname)
        if base_layer==None:
            base_layer=self.layers['metal'][self.layers['pin'].index(layer)]
            #base_layer=[layer[0], 'drawing']
        self.db.add_rect(None, xy=xy_phy, layer=base_layer)
        return self.db.add_pin(name=name, netname=netname, xy=xy_phy, layer=layer)

    def boundary_pin_from_rect(self, rect, gridname, name, layer, size=4, direction='left', netname=None):
        """
        Generate a boundary Pin object from a reference Rect object
        Parameters
        ----------
        rect : laygo.LayoutObject.Rect
            reference rect object
        gridname : str
            grid name
        name : str
            pin name
        layer : [str, str]
            pin layer
        size : int
            size of boundary pin
        direction : str
            specifies which side the generated Pin is placed. Possible values are 'left', 'right', 'top', 'bottom'
        netname : str, optional
            net name. If None, pin name is used. Used when multiple pin objects are attached to the same net.
        Returns
        -------
        laygo.LayoutObject.Pin
            generated Pin object
        """
        if netname == None: netname = name
        xy=self.get_rect_xy(rect.name, gridname, sort=True)
        if direction=="left":
            xy[1][0] = xy[0][0] + size
        elif direction=="right":
            xy[0][0] = xy[1][0] - size
        elif direction=="bottom":
            xy[1][1] = xy[0][1] + size
        elif direction=="top":
            xy[0][1] = xy[1][1] - size

        return GridLayoutGenerator.pin(self, name=name, layer=layer, xy=xy, gridname=gridname, netname=netname)

    #db access functions
    def sel_template_library(self, libname):
        """
        Select a template library to work on
        Parameters
        ----------
        libname : str
            library name
        """
        self.templates.sel_library(libname)

    def sel_grid_library(self, libname):
        """
        Select a grid library to work on
        Parameters
        ----------
        libname : str
            library name
        """
        self.grids.sel_library(libname)

    #object geometry related functions
    def get_xy(self, obj, gridname=None, sort=False):
        """
            get xy coordinate of an object on the specific coordinate
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
        if isinstance(obj, TemplateObject):
            if gridname is None:
                return obj.size
            else:
                return self.get_absgrid_xy(gridname, obj.size)
        if isinstance(obj, Instance) or isinstance(obj, InstanceArray):
            if gridname == None:
                return obj.xy
            else:
                return self.get_absgrid_xy(gridname, obj.xy)
        if isinstance(obj, Rect):
            xy = self.get_absgrid_region(gridname, obj.xy[0, :], obj.xy[1, :])
            if sort == True: xy = self._bbox_xy(xy)
            return xy
        if isinstance(obj, Pin):
            xy = self.get_absgrid_region(gridname, obj.xy[0, :], obj.xy[1, :])
            if sort == True: xy = self._bbox_xy(xy)
            return xy

    def get_bbox(self, obj, gridname=None):
        """
            get bounding box of an object on the specific coordinate
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
        if isinstance(obj, TemplateObject):
            if gridname is None:
                xy = obj.size
            else:
                xy = self.get_absgrid_xy(gridname, obj.size)
            return np.array([0, 0], xy)
        if isinstance(obj, Instance) or isinstance(obj, InstanceArray):
            if gridname == None:
                xy = obj.bbox
            else:
                xy = self.get_absgrid_xy(gridname, obj.bbox)
            xy = self._bbox_xy(xy)
            return xy
        if isinstance(obj, Rect):
            if gridname == None:
                xy = obj.xy
            else:
                xy = self.get_absgrid_region(gridname, obj.xy[0, :], obj.xy[1, :])
            xy = self._bbox_xy(xy)
            return xy
        if isinstance(obj, Pin):
            if gridname == None:
                xy = obj.xy
            else:
                xy = self.get_absgrid_region(gridname, obj.xy[0, :], obj.xy[1, :])
            xy = self._bbox_xy(xy)
            return xy

    def get_template_size(self, name, gridname=None, libname=None):
        """
            get the size of a template in abstract coordinate. Same with get_template_xy
        """
        return self.get_template_xy(name=name, gridname=gridname, libname=libname)

    #template and grid related functions
    def get_template(self, name, libname=None):
        """
            Get template object handle
            Parameters
            ----------
            name : str
                template name
            libname : str, optional
                library name
            Returns
            -------
            laygo.TemplateObject.TemplateObject
                template object
        """
        return self.templates.get_template(name, libname)

    def get_grid(self, gridname):
        """
        Get grid object handle
        Parameters
        ----------
        gridname : str
            grid name
        Returns
        -------
        laygo.GridObject.GridObject
            grid object
        """
        return self.grids.get_grid(gridname)

    def get_absgrid_xy(self, gridname, xy, refinstname=None, refinstindex=np.array([0, 0]), refpinname=None, refobj=None, refobjindex=None):
        """
        Convert physical coordinate to abstract coordinate
        Parameters
        ----------
        gridname : str
            abstract grid name
        xy : np.array([float, float])
            coordinate
        refinstname : str, optional
            referenence instance name
        refinstname : np.array([int, int]), optional
            referenence instance index
        refpinname : str, optional
            reference pin name
        Returns
        -------
        np.ndarray([int, int])
            abstract coordinate
        """
        if not refinstname is None:
            rinst = self.get_inst(name=refinstname, index=refinstindex)
        elif not refobj is None:
            rinst = refobj
            refinstname = refobj.name
            refinstindex = refobjindex
        if not refinstname is None:
            if not refpinname is None:
                pxy_ongrid = self.get_template_pin_xy(name=rinst.cellname, pinname=refpinname, gridname=gridname)[0]
                pxy = self.grids.get_phygrid_xy(gridname=gridname, xy=pxy_ongrid)
                rxy = rinst.xy + np.dot(ut.Mt(rinst.transform), pxy)
            else:
                rxy = rinst.xy
            _xy = np.dot(np.linalg.inv(ut.Mt(rinst.transform)), xy - rxy)
        else:
            _xy = xy
        return self.grids.get_absgrid_xy(gridname=gridname, xy=_xy)

    def get_absgrid_region(self, gridname, xy0, xy1):
        """
        Get regional coordinates on abstract grid
        Parameters
        ----------
        gridname : str
            grid name
        xy0 : np.array([float, float])
            first xy coordinate on physical grid
        xy1 : np.array([float, float])
            second xy coordinate on physical grid
        refinstname : str, optional
            reference inst name
        refpinname : str, optional
            reference pin name
        Returns
        -------
        np.ndarray([[int, int], [int, int]])
            abstract coordinates
        """
        return self.grids.get_absgrid_region(gridname=gridname, xy0=xy0, xy1=xy1)

    def construct_template_and_grid(self, db, libname, cellname=None,
                                    layer_boundary=['prBoundary', 'boundary'], layer_text=['text', 'drawing'],
                                    routegrid_prefix='route', placementgrid_prefix='placement', append=True):
        """
        Construct TemplateDB and GridDB from LayoutDB. Used when generating a template and grid database
        from layout.
        Parameters
        ----------
        db : laygo.LayoutDB.LayoutDB
            layout database object
        libname : str
            library name
        cellname : str, None, optional
            cell name to be registered as template. If None, all cells(structures) will be registered.
        layer_boundary : [str, str], optional
            layer of placement boundary. Used to find out the size of template/grid.
        layer_text : [str, str], optional
            layer of text objects. Used to find out Pin names (especially when netnames need to be captured).
        routegrid_prefix : str, optioanl
            prefix of routing grids. All layout cells starting with routegrid_prefix will be considered as routing grids.
        placementgrid_prefix : str, optional
            prefix of placement grids. All layout cells starting with placementgrid_prefix will be considered as placement grids.
        append : True, optional
            if True, the loaded template and grid database will be appended to existing database.
        Returns
        -------
        [laygo.TemplateDB.TemplateDB, laygo.GridDB.GridDB]
            constructed template and grid databases
        """
        tdb=TemplateDB()
        gdb=GridDB()
        tdb.add_library(libname)
        gdb.add_library(libname)

        if cellname==None:
            cellname=db.design[libname].keys()
        elif not isinstance(cellname, list):
            cellname=[cellname] # make it to a list
        for sn in cellname:
            s = db.design[libname][sn]
            if sn.startswith(placementgrid_prefix):  # placementgrid
                for r in s['rects'].values():
                    if r.layer==layer_boundary: #boundary layer
                        bx1, bx2 = sorted(r.xy[:,0].tolist()) #need to be changed..
                        by1, by2 = sorted(r.xy[:,1].tolist())
                        ll = np.array([bx1, by1])  # lower-left
                        ur = np.array([bx2, by2])  # upper-right
                        bnd=np.vstack([ll,ur])
                gdb.add_placement_grid(name=sn, libname=libname, xy=bnd)
            elif sn.startswith(routegrid_prefix): #route grid
                xgrid=[]
                xwidth=[]
                xlayer=[]
                ygrid=[]
                ywidth=[]
                ylayer=[]
                for r in s['rects'].values():
                    if r.layer==layer_boundary: #boundary layer
                        bx1, bx2 = sorted(r.xy[:,0].tolist()) #need to be changed..
                        by1, by2 = sorted(r.xy[:,1].tolist())
                        ll = np.array([bx1, by1])  # lower-left
                        ur = np.array([bx2, by2])  # upper-right
                        bnd=np.vstack([ll,ur])
                    else: #route
                        if r.width>r.height: # x-direction
                            ygrid.append(r.cy)
                            ywidth.append(r.height)
                            ylayer.append(r.layer)
                        else: # y-direction
                            xgrid.append(r.cx)
                            xwidth.append(r.width)
                            xlayer.append(r.layer)
                xg = np.vstack((np.array(xgrid), np.array(xwidth)))
                yg = np.vstack((np.array(ygrid), np.array(ywidth)))
                xg = xg.T[xg.T[:, 0].argsort()].T  # sort
                yg = yg.T[yg.T[:, 0].argsort()].T  # sort
                xgrid=xg[0,:];ygrid=yg[0,:]
                xwidth=xg[1,:];ywidth=yg[1,:]
                #print(sn, str(np.around(xg, decimals=10).tolist()), str(np.around(yg, decimals=10).tolist()))
                gdb.add_route_grid(name=sn, libname=libname, xy=bnd, xgrid=xgrid, ygrid=ygrid, xwidth=xwidth,
                                   ywidth=ywidth, xlayer=xlayer, ylayer=ylayer, viamap=None)
                #via load
                viamap=dict()
                gdb.sel_library(libname)
                for i in s['instances'].values(): #via
                    vcoord=gdb.get_absgrid_xy(sn, i.xy)
                    if not i.cellname in viamap: viamap[i.cellname]=vcoord
                    else: viamap[i.cellname]=np.vstack((viamap[i.cellname],vcoord))
                for vm_name, vm_item in viamap.items():  # via map
                    #print(vm_name, vm_item, vm_item.ndim)
                    if not (vm_item.ndim==1):
                        viamap[vm_name]=vm_item[vm_item[:, 1].argsort()]
                gdb.update_viamap(sn, viamap)

            else: #normal template
                #find the boundary
                bnd=np.array(([0.0, 0.0],[0.0, 0.0]))
                for r in s['rects'].values():
                    if r.layer==layer_boundary: #boundary layer
                        bx1, bx2 = sorted(r.xy[:,0].tolist()) #need to be changed..
                        by1, by2 = sorted(r.xy[:,1].tolist())
                        ll = np.array([bx1, by1])  # lower-left
                        ur = np.array([bx2, by2])  # upper-right
                        bnd=np.vstack([ll,ur])
                #find pins
                pindict=dict()
                for t in s['texts'].values():
                    if not t.layer==layer_text: #if text layer (not pin layer), skip
                        #pinname: if a text label is located at the same coordinate, use it as pinname
                        #         otherwise pinname=netname=t.text
                        pinname=t.text
                        for t2 in s['texts'].values():
                            if t2.layer==layer_text:
                                if (t.xy==t2.xy).all():
                                    pinname=t2.text
                        for r in s['rects'].values():
                            if r.layer==t.layer: #boundary layer
                                bx1, bx2 = sorted(r.xy[:,0].tolist()) #need to be changed..
                                by1, by2 = sorted(r.xy[:,1].tolist())
                                ll = np.array([bx1, by1])  # lower-left
                                ur = np.array([bx2, by2])  # upper-right
                                if np.all(np.logical_and(ll <= t.xy, t.xy <= ur))==True:
                                    pindict[pinname]={'netname':t.text, 'layer':r.layer, 'xy':r.xy}
                logging.debug('construct_template: name:' + sn)
                tdb.add_template(name=sn, libname=libname, xy=bnd, pins=pindict)
        if append==True:
            self.templates.merge(tdb)
            self.grids.merge(gdb)
        return tdb, gdb

    def add_template_from_cell(self, libname=None, cellname=None):
        """
        Register selected cell to template database
        Parameters
        ----------
        libname : str, optional
            library name, if None, laygo.GridLayoutGenerator.db.plib is used (set by sel_library)
        cellname : str, optional
            cell name, if None, laygo.GridLayoutGenerator.db.pcell is used (set by sel_cell)
        """
        if libname is None:
            libname=self.db.plib
        if cellname is None:
            cellname=self.db.pcell

        # boundary
        ll = np.array([0.0, 0.0])
        ur = np.array([0.0, 0.0])
        for instname in self.db.design[libname][cellname]['instances'].keys():
            i=self.db.design[libname][cellname]['instances'][instname]
            if i.cellname in self.templates[i.libname].keys():
                t = self.templates.get_template(i.cellname, i.libname)
                if not (t.size[0]==0 and t.size[1]==0): #zero size then waive (no valid prBoundary)
                    xy=self.get_inst(instname).bbox
                    for i in range(xy.shape[0]):
                        if xy[i,:][0] < ll[0]:
                            ll[0]=xy[i,:][0]
                        if xy[i,:][1] < ll[1]:
                            ll[1]=xy[i,:][1]
                        if xy[i,:][0] > ur[0]:
                            ur[0]=xy[i,:][0]
                        if xy[i,:][1] > ur[1]:
                            ur[1]=xy[i,:][1]
        for rectname, r in self.db.design[libname][cellname]['rects'].items():
            if r.layer==self.layers['prbnd']:
                xy=r.xy
                for i in range(xy.shape[0]):
                    if xy[i,:][0] < ll[0]:
                        ll[0]=xy[i,:][0]
                    if xy[i,:][1] < ll[1]:
                        ll[1]=xy[i,:][1]
                    if xy[i,:][0] > ur[0]:
                        ur[0]=xy[i,:][0]
                    if xy[i,:][1] > ur[1]:
                        ur[1]=xy[i,:][1]
        bnd=np.vstack([ll,ur])
        #find pins
        pindict = dict()
        for pinname in self.db.design[libname][cellname]['pins'].keys():
            pin=self.get_pin(pinname)
            pindict[pinname]={'netname':pin.netname, 'layer':pin.layer, 'xy':pin.xy}
        self.templates.add_template(name=cellname, libname=libname, xy=bnd, pins=pindict)

    def save_template(self, filename, libname=None):
        """
        Save templateDB to yaml file
        Parameters
        ----------
        filename : str
        """
        self.templates.export_yaml(filename=filename, libname=libname)

    def load_template(self, filename, libname=None):
        """
        Load templateDB from yaml file
        Parameters
        ----------
        filename : str
        libname : str, optional
        """
        self.templates.import_yaml(filename=filename, libname=libname)

    def save_grid(self, filename):
        """
        Save gridDB to yaml file
        Parameters
        ----------
        filename : str
        """
        self.grids.export_yaml(filename=filename)

    def load_grid(self, filename, libname=None):
        """
        Load gridDB from yaml file
        Parameters
        ----------
        filename : str
        libname : str, optional
        Returns
        -------
        laygo.GridObject.GridObject
            loaded grid object
        """
        self.grids.import_yaml(filename=filename, libname=libname)

    #Deprecated functions. Do not use for future generators
    def pin_from_rect(self, name, layer, rect, gridname, netname=None):
        """
        Generate a Pin object from a Rect object
        Parameters
        ----------
        name : str
            Pin name
        layer : [str, str]
            Pin layer
        rect : laygo.GridObject.Rect
            Rect object
        gridname : str
            Gridname
        netname : str, optional
            net name. If None, pin name is used. Used when multiple pin objects are attached to the same net.
        Returns
        -------
        laygo.LayoutObject.Pin
            generated Pin object
        """
        print("[WARNING] pin_from_rect function will be deprecated. Use pin function with refobj argument instead")
        if netname == None: netname = name
        xy = rect.xy
        xy = self.get_absgrid_region(gridname, xy[0, :], xy[1, :])
        return GridLayoutGenerator.pin(self, name, layer, xy, gridname, netname=netname)

    def get_template_xy(self, name, gridname=None, libname=None):
        """
        get the size of a template in abstract coordinate
        Parameters
        ----------
        name : str
            template name
        gridname : str, optional
            grid name. If None, physical grid is used
        libname : str, optional
            library name. If None, GridLayoutGenerator.TemplateDB.TemplateDB.plib is uesd
        Returns
        -------
        np.ndarray([int, int])
            size of template
        """
        t = self.templates.get_template(name, libname=libname)
        if gridname is None:
            return t.size
        else:
            return self.get_absgrid_xy(gridname, t.size)

    def get_inst_xy(self, name, gridname=None):
        """
        Get xy coordinate values of an Instance object in abstract coordinate
        Parameters
        ----------
        name : str
            instance name
        gridname : str, optional
            grid name. If None, physical grid is used
        Returns
        -------
        np.ndarray([int, int])
            xy coordinate of instance
        """
        i = self.get_inst(name)
        if gridname==None:
            return i.xy
        else:
            return self.get_absgrid_xy(gridname, i.xy)

    def get_rect_xy(self, name, gridname, sort=False):
        """
        get xy coordinate values of a Rect object in abstract coordinate
        Parameters
        ----------
        name : str
            rect name
        gridname : str
            grid name
        sort : bool, optional
            if True, the coordinates are sorted
        Returns
        -------
        np.ndarray([int, int])
            xy coordinates of the Rect object
        """
        r = self.get_rect(name)
        xy=self.get_absgrid_region(gridname, r.xy[0,:], r.xy[1,:])
        if sort==True: xy=self._bbox_xy(xy)
        return xy

    def get_pin_xy(self, name, gridname, sort=False):
        """
        get xy coordinates of a Pin object in abstract coordinate
        Parameters
        ----------
        name : str
            rect name
        gridname : str
            grid name
        sort : bool, optional
            if True, the coordinates are sorted
        Returns
        -------
        np.ndarray([int, int])
            xy coordinates of the Pin object
        """
        r = self.get_rect(name)
        xy=self.get_absgrid_region(gridname, r.xy[0,:], r.xy[1,:])
        if sort==True: xy=self._bbox_xy(xy)
        return xy

    def get_template_pin_xy(self, name, pinname, gridname, libname=None):
        """
        get xy cooridnate of a template pin in abstract coordinate
        Parameters
        ----------
        name : str
            template cellname
        pinname : str
            template pinname
        gridname : str
            grid name
        libname : str, optional
            library name of template
        Returns
        -------
        np.ndarray([[int, int], [int, int]])
            Template pin coordinates
        """
        t = self.templates.get_template(name, libname=libname)
        pin_xy_phy = t.pins[pinname]['xy']
        pin_xy_abs = self.get_absgrid_region(gridname, pin_xy_phy[0], pin_xy_phy[1])
        return pin_xy_abs

    def get_inst_pin_xy(self, name, pinname, gridname, index=np.array([0, 0]), sort=False):
        """
        Get xy coordinates of an instance pin in abstract coordinate
        Parameters
        ----------
        name : str
            instance name
            if None, return all pin coordinates of all instances in dict format
        pinname : str
            template pinname
            if None, return all pin coordinates of specified instance in dict format
        gridname : str
            grid name
        index : np.array([int, int])
        Returns
        -------
        np.ndarray([int, int])
            Instance pin coordinates
        """
        index=np.asarray(index)
        if name == None:
            xy=dict()
            for i in self.get_inst():
                xy[i]=self.get_inst_pin_xy(i, pinname, gridname, index, sort)
            return xy
        else:
            i = self.get_inst(name)
            if not i.cellname in self.templates[i.libname].keys():
                print(i.cellname+" template is not in "+i.libname+'. pin coordinates will not be extracted')
                return dict()
            else:
                t = self.templates.get_template(i.cellname, libname=i.libname)
                if pinname==None:
                    xy=dict()
                    for p in t.pins:
                        xy[p]=self.get_inst_pin_xy(name, p, gridname, index, sort)
                    return xy
                else:
                    xy0 = i.xy + np.dot(t.size * index + t.pins[pinname]['xy'][0, :], ut.Mt(i.transform).T)
                    xy1 = i.xy + np.dot(t.size * index + t.pins[pinname]['xy'][1, :], ut.Mt(i.transform).T)
                    xy=self.get_absgrid_region(gridname, xy0, xy1)
                    if sort == True: xy = self._bbox_xy(xy)
                    return xy

    def get_inst_bbox(self, name, gridname=None, sort=False):
        """
        Get a bounding box of an Instance object, on abstract grid
        Parameters
        ----------
        name : str
            instance name
        gridname : str, optional
            grid name. If None, physical grid is used
        sort : bool, optional
            if True, the return coordinates are sorted
        Returns
        -------
        np.ndarray([[int, int], [int, int]])
            instance bbox in abstract coordinate
        """
        xy = self.get_inst(name).bbox
        if sort == True: xy = self._bbox_xy(xy)
        if gridname is None:
            return xy
        else:
            return self.get_absgrid_region(gridname, xy[0], xy[1])

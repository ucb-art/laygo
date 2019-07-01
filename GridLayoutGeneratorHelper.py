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

"""GridBasedLayoutGenerator utility functions for users"""
__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

#import struct
#import math
#from math import *
import numpy as np
from copy import deepcopy

def generate_boundary(laygen, objectname_pfix, placement_grid,
                      devname_bottom, devname_top, devname_left, devname_right,
                      shape_bottom=None, shape_top=None, shape_left=None, shape_right=None,
                      transform_bottom=None, transform_top=None, transform_left=None, transform_right=None,
                      origin=np.array([0, 0])):
    """generate a boundary structure to resolve boundary design rules"""
    pg = placement_grid
    #parameters
    if shape_bottom == None:
        shape_bottom = [np.array([1, 1]) for d in devname_bottom]
    if shape_top == None:
        shape_top = [np.array([1, 1]) for d in devname_top]
    if shape_left == None:
        shape_left = [np.array([1, 1]) for d in devname_left]
    if shape_right == None:
        shape_right = [np.array([1, 1]) for d in devname_right]
    if transform_bottom == None:
        transform_bottom = ['R0' for d in devname_bottom]
    if transform_top == None:
        transform_top = ['R0' for d in devname_top]
    if transform_left == None:
        transform_left = ['R0' for d in devname_left]
    if transform_right == None:
        transform_right = ['R0' for d in devname_right]

    #bottom
    dev_bottom=[]
    dev_bottom.append(laygen.place("I" + objectname_pfix + 'BNDBTM0', devname_bottom[0], pg, xy=origin,
                      shape=shape_bottom[0], transform=transform_bottom[0]))
    for i, d in enumerate(devname_bottom[1:]):
        dev_bottom.append(laygen.relplace("I" + objectname_pfix + 'BNDBTM'+str(i+1), d, pg, dev_bottom[-1].name,
                                          shape=shape_bottom[i+1], transform=transform_bottom[i+1]))
    dev_left=[]
    dev_left.append(laygen.relplace("I" + objectname_pfix + 'BNDLFT0', devname_left[0], pg, dev_bottom[0].name, direction='top',
                                    shape=shape_left[0], transform=transform_left[0]))
    for i, d in enumerate(devname_left[1:]):
        dev_left.append(laygen.relplace("I" + objectname_pfix + 'BNDLFT'+str(i+1), d, pg, dev_left[-1].name, direction='top',
                                        shape=shape_left[i+1], transform=transform_left[i+1]))
    dev_right=[]
    dev_right.append(laygen.relplace("I" + objectname_pfix + 'BNDRHT0', devname_right[0], pg, dev_bottom[-1].name, direction='top',
                                     shape=shape_right[0], transform=transform_right[0]))
    for i, d in enumerate(devname_right[1:]):
        dev_right.append(laygen.relplace("I" + objectname_pfix + 'BNDRHT'+str(i+1), d, pg, dev_right[-1].name, direction='top',
                                         shape=shape_right[i+1], transform=transform_right[i+1]))
    dev_top=[]
    dev_top.append(laygen.relplace("I" + objectname_pfix + 'BNDTOP0', devname_top[0], pg, dev_left[-1].name, direction='top',
                                   shape=shape_top[0], transform=transform_top[0]))
    for i, d in enumerate(devname_top[1:]):
        dev_top.append(laygen.relplace("I" + objectname_pfix + 'BNDTOP'+str(i+1), d, pg, dev_top[-1].name,
                                       shape=shape_top[i+1], transform=transform_top[i+1]))
    return [dev_bottom, dev_top, dev_left, dev_right]

def generate_power_rails(laygen, routename_tag, layer, gridname, netnames=['VDD', 'VSS'], direction='x', 
                         start_coord=0, end_coord=0, route_index=None, via_index=None, generate_pin=True): 
    """generate power rails"""
    rail_list=[]
    for netidx, netname in enumerate(netnames):
        rail_sub_list=[]
        for rcnt, ridx in enumerate(route_index[netidx]):
            if direction=='x': rxy0=np.array([[start_coord, ridx], [end_coord, ridx]])  
            if direction=='y': rxy0=np.array([[ridx, start_coord], [ridx, end_coord]])  
            if generate_pin == True:
                if netname.endswith(':'): #remove colon from netname
                    pn=netname[:-1] + routename_tag + str(rcnt)
                else:
                    pn=netname + routename_tag + str(rcnt)
                p=laygen.pin(name=pn, layer=layer, xy=rxy0, gridname=gridname, netname=netname)
                rail_sub_list.append(p)
            else:
                r=laygen.route(None, layer, xy0=rxy0[0], xy1=rxy0[1], gridname0=gridname)
                rail_sub_list.append(r)
            if not via_index==None: #via generation
                for vidx in via_index[netidx]:
                    if direction=='x': vxy0=np.array([vidx, ridx])
                    else: vxy0=np.array([ridx, vidx])
                    laygen.via(None, vxy0, gridname=gridname)
        rail_list.append(rail_sub_list)
    return rail_list

def generate_power_rails_from_rails_xy(laygen, routename_tag, layer, gridname, netnames=['VDD', 'VSS'], direction='x', 
                                       input_rails_xy=None, generate_pin=True, 
                                       overwrite_start_coord=None, overwrite_end_coord=None, 
                                       offset_start_coord=None, offset_end_coord=None, 
                                       overwrite_num_routes=None,
                                       overwrite_start_index=None, overwrite_end_index=None,
                                       offset_start_index=0, offset_end_index=0):
    """generate power rails from pre-existing power rails in upper/lower layer. 
       the pre-existing rail information is provided as xy array
    """
    route_index=[]
    via_index=[]
    for netidx, netname in enumerate(netnames):
        sub_via_index=[]
        for i, irxy in enumerate(input_rails_xy[netidx]):   
            if direction == 'x':
                #boundary estimation
                if netidx==0 and i==0: #initialize
                    start_coord=irxy[0][0]
                    end_coord=irxy[0][0]
                    route_index_start=min((irxy[0][1], irxy[1][1]))
                    route_index_end=max((irxy[0][1], irxy[1][1]))
                else:
                    if start_coord > irxy[0][0]: start_coord=irxy[0][0]
                    if end_coord < irxy[0][0]: end_coord=irxy[0][0]
                    rist=min((irxy[0][1], irxy[1][1]))
                    ried=max((irxy[0][1], irxy[1][1]))
                    if route_index_start < rist: route_index_start = rist
                    if route_index_end > ried: route_index_end = ried
                sub_via_index.append(irxy[0][0])
            else:
                #boundary estimation
                if netidx==0 and i==0: #initialize
                    start_coord=irxy[0][1]
                    end_coord=irxy[0][1]
                    route_index_start=min((irxy[0][0], irxy[1][0]))
                    route_index_end=max((irxy[0][0], irxy[1][0]))
                else:
                    if start_coord > irxy[0][1]: start_coord=irxy[0][1]
                    if end_coord < irxy[0][1]: end_coord=irxy[0][1]
                    rist=min((irxy[0][0], irxy[1][0]))
                    ried=max((irxy[0][0], irxy[1][0]))
                    if route_index_start < rist: route_index_start = rist
                    if route_index_end > ried: route_index_end = ried
                sub_via_index.append(irxy[0][1])
        via_index.append(np.array(sub_via_index))
    #offset route index if necessary
    route_index_start+=offset_start_index
    route_index_end+=offset_end_index
    #overwrite route index if necessary
    if not overwrite_start_index==None:
        route_index_start=overwrite_start_index
    if not overwrite_end_index==None:
        route_index_end=overwrite_end_index
    #change number of routes if necessary
    if not overwrite_num_routes==None:
        route_index_end=route_index_start + overwrite_num_routes
    #route index
    for netidx, netname in enumerate(netnames):
        sub_route_index=[]
        for ri in range(int((route_index_end - route_index_start + 1)/len(netnames))):
            sub_route_index += [route_index_start + netidx + len(netnames)*ri]
        route_index.append(np.array(sub_route_index))
    #offset start/end coordinates if necessary
    if not offset_start_coord==None:
        start_coord+=offset_start_coord 
    if not offset_end_coord==None:
        end_coord+=offset_end_coord 
    #overwrite start/end coordinates if necessary
    if not overwrite_start_coord==None:
        start_coord=overwrite_start_coord 
    if not overwrite_end_coord==None:
        end_coord=overwrite_end_coord 
    return generate_power_rails(laygen, routename_tag=routename_tag, layer=layer, gridname=gridname, netnames=netnames, direction=direction, 
                                start_coord=start_coord, end_coord=end_coord, route_index=route_index, via_index=via_index, generate_pin=generate_pin) 

def generate_power_rails_from_rails_rect(laygen, routename_tag, layer, gridname, netnames=['VDD', 'VSS'], direction='x', 
                                         input_rails_rect=None, generate_pin=True, 
                                         overwrite_start_coord=None, overwrite_end_coord=None, overwrite_num_routes=None,
                                         overwrite_start_index=None, overwrite_end_index=None,
                                         offset_start_coord=None, offset_end_coord=None, 
                                         offset_start_index=0, offset_end_index=0):
    """generate power rails from pre-existing power rails in upper/lower layer. 
       the pre-existing rail information is provided as rect
    """
    xy=[]
    for netidx, netname in enumerate(netnames):
        sub_xy=[]
        for i, ir in enumerate(input_rails_rect[netidx]):    
            sub_xy.append(laygen.get_rect_xy(ir.name, gridname))
        xy.append(np.array(sub_xy))
    return generate_power_rails_from_rails_xy(laygen, routename_tag, layer, gridname, netnames=netnames, direction=direction, 
                                              input_rails_xy=xy, generate_pin=generate_pin, 
                                              overwrite_start_coord=overwrite_start_coord, overwrite_end_coord=overwrite_end_coord,
                                              offset_start_coord=offset_start_coord, offset_end_coord=offset_end_coord, 
                                              overwrite_num_routes=overwrite_num_routes,
                                              overwrite_start_index=overwrite_start_index, overwrite_end_index=overwrite_end_index,
                                              offset_start_index=offset_start_index, offset_end_index=offset_end_index)

def generate_power_rails_from_rails_inst(laygen, routename_tag, layer, gridname, netnames=['VDD', 'VSS'], direction='x', 
                                         input_rails_instname=None, input_rails_pin_prefix=['VDD', 'VSS'], generate_pin=True, 
                                         overwrite_start_coord=None, overwrite_end_coord=None, overwrite_num_routes=None,
                                         overwrite_start_index=None, overwrite_end_index=None,
                                         offset_start_coord=None, offset_end_coord=None, 
                                         offset_start_index=0, offset_end_index=0):
    """generate power rails from pre-existing power rails in upper/lower layer. 
       the pre-existing rail information is provided as inst / pin prefix
    """
    xy=[]
    pdict=laygen.get_inst_pin_xy(None, None, gridname)
    #iname=input_rails_instname
    if not isinstance(input_rails_instname, list):
        input_rails_instname=[input_rails_instname]
    for pfix in input_rails_pin_prefix:
        sub_xy=[]
        for iname in input_rails_instname:
            for pn, p in pdict[iname].items():
                if pn.startswith(pfix):
                    sub_xy.append(p)
            xy.append(sub_xy)
    return generate_power_rails_from_rails_xy(laygen, routename_tag, layer, gridname, netnames=netnames, direction=direction, 
                                              input_rails_xy=xy, generate_pin=generate_pin, 
                                              overwrite_start_coord=overwrite_start_coord, overwrite_end_coord=overwrite_end_coord,
                                              overwrite_num_routes=overwrite_num_routes,
                                              overwrite_start_index=overwrite_start_index, overwrite_end_index=overwrite_end_index,
                                              offset_start_coord=offset_start_coord, offset_end_coord=offset_end_coord, 
                                              offset_start_index=offset_start_index, offset_end_index=offset_end_index)

def generate_grids_from_xy(laygen, gridname_input, gridname_output, xy, xy_grid_type=None):
    """generate route grids combining a pre-existing grid and xy-array
    it will create a new array by copying the given grid and update part of entries from xy-lists
    """
    #copy original database
    gi=laygen.get_grid(gridname_input)
    bnd=deepcopy(gi.xy)
    #xgrid = deepcopy(gi.get_xgrid())
    #ygrid = deepcopy(gi.get_ygrid())
    #xwidth = deepcopy(gi.get_xwidth())
    #ywidth = deepcopy(gi.get_ywidth())
    #_viamap = gi.get_viamap()
    xgrid = deepcopy(gi.xgrid)
    ygrid = deepcopy(gi.ygrid)
    xwidth = deepcopy(gi.xwidth)
    ywidth = deepcopy(gi.ywidth)
    _viamap = gi.viamap
    vianame = list(_viamap.keys())[0] #just pickig one via; should be fixed
    #figure out routing direction
    if xy_grid_type==None:
        if abs(xy[0][0][0]-xy[0][1][0]) > abs(xy[0][0][1]-xy[0][1][1]): #aspect ratio
            xy_grid_type = 'ygrid'
        else:
            xy_grid_type = 'xgrid'
    #extract grid information from xy list
    if xy_grid_type== 'xgrid':
        xgrid=[]
        xwidth=[]
        for xy0 in xy:
            #xgrid.append(0.5 * (xy0[0][0] + xy0[1][0]))
            xgrid_new=0.5 * (xy0[0][0] + xy0[1][0])
            if xgrid_new not in xgrid:
                xgrid.append(xgrid_new)
                xwidth.append(abs(xy0[0][0] - xy0[1][0]))
        #sort
        xwidth = [x for (y, x) in sorted(zip(xgrid, xwidth))]
        xgrid.sort()
        xgrid = np.array(xgrid)
        xwidth = np.array(xwidth)
        bnd[1][0] = max(xgrid)+min(xgrid)
    if xy_grid_type== 'ygrid':
        ygrid=[]
        ywidth=[]
        for xy0 in xy:
            #ygrid.append(0.5 * (xy0[0][1] + xy0[1][1]))
            ygrid_new=0.5 * (xy0[0][1] + xy0[1][1])
            if ygrid_new not in ygrid:
                ygrid.append(ygrid_new)
                ywidth.append(abs(xy0[0][1] - xy0[1][1]))
        #sort
        ywidth = [x for (y, x) in sorted(zip(ygrid, ywidth))]
        ygrid.sort()
        ygrid=np.array(ygrid)
        ywidth=np.array(ywidth)
        bnd[1][1]=max(ygrid)+min(ygrid)
    # viamap
    viamap = {vianame: []}
    for x in range(len(xgrid)):
        for y in range(len(ygrid)):
            viamap[vianame].append([x, y])
    viamap[vianame] = np.array(viamap[vianame])
    # add grid information
    laygen.grids.add_route_grid(name=gridname_output, libname=None, xy=bnd, xgrid=xgrid, ygrid=ygrid, xwidth=xwidth,
                                ywidth=ywidth, viamap=viamap)
    #laygen.grids.display()

def generate_grids_from_xy_bnd(laygen, gridname_input, gridname_output, xy, xy_grid_type=None, bnd=None):
    """generate route grids combining a pre-existing grid and xy-array
    it will create a new array by copying the given grid and update part of entries from xy-lists
    """
    #copy original database
    gi=laygen.get_grid(gridname_input)
    if bnd is None:
        _bnd=deepcopy(gi.xy)
    xgrid = deepcopy(gi.xgrid)
    ygrid = deepcopy(gi.ygrid)
    xwidth = deepcopy(gi.xwidth)
    ywidth = deepcopy(gi.ywidth)
    _viamap = gi.viamap
    vianame = list(_viamap.keys())[0] #just pickig one via; should be fixed
    #figure out routing direction
    if xy_grid_type==None:
        if abs(xy[0][0][0]-xy[0][1][0]) > abs(xy[0][0][1]-xy[0][1][1]): #aspect ratio
            xy_grid_type = 'ygrid'
        else:
            xy_grid_type = 'xgrid'
    #extract grid information from xy list
    if xy_grid_type== 'xgrid':
        xgrid=[]
        xwidth=[]
        for xy0 in xy:
            #xgrid.append(0.5 * (xy0[0][0] + xy0[1][0]))
            xgrid_new=0.5 * (xy0[0][0] + xy0[1][0])
            if xgrid_new not in xgrid:
                xgrid.append(xgrid_new)
                xwidth.append(abs(xy0[0][0] - xy0[1][0]))
        #sort
        xwidth = [x for (y, x) in sorted(zip(xgrid, xwidth))]
        xgrid.sort()
        xgrid = np.array(xgrid)
        xwidth = np.array(xwidth)
        if bnd is None:
            _bnd[1][0] = max(xgrid)+min(xgrid)
        else:
            bnd[1][1] = deepcopy(gi.xy)[1][1]
    if xy_grid_type== 'ygrid':
        ygrid=[]
        ywidth=[]
        for xy0 in xy:
            #ygrid.append(0.5 * (xy0[0][1] + xy0[1][1]))
            ygrid_new=0.5 * (xy0[0][1] + xy0[1][1])
            if ygrid_new not in ygrid:
                ygrid.append(ygrid_new)
                ywidth.append(abs(xy0[0][1] - xy0[1][1]))
        #sort
        ywidth = [x for (y, x) in sorted(zip(ygrid, ywidth))]
        ygrid.sort()
        ygrid=np.array(ygrid)
        ywidth=np.array(ywidth)
        if bnd is None:
            _bnd[1][1]=max(ygrid)+min(ygrid)
            bnd=_bnd
        else:
            bnd[1][0] = deepcopy(gi.xy)[1][0]
    # viamap
    viamap = {vianame: []}
    for x in range(len(xgrid)):
        for y in range(len(ygrid)):
            viamap[vianame].append([x, y])
    viamap[vianame] = np.array(viamap[vianame])
    # add grid information
    laygen.grids.add_route_grid(name=gridname_output, libname=None, xy=bnd, xgrid=xgrid, ygrid=ygrid, xwidth=xwidth,
                                ywidth=ywidth, viamap=viamap)

def generate_grids_from_inst(laygen, gridname_input, gridname_output, instname,
                           inst_pin_prefix=['VDD', 'VSS'], xy_grid_type=None):
    """generate route grids combining a pre-existing grid and inst pins
        it will create a new array by copying the given grid and update part of entries from xy coordinates of pins
    """
    if not isinstance(instname, list):
        instname=[instname]
    
    xy = []
    for inn in instname:
        inst = laygen.get_inst(name=inn)
        #inst.display()
        t = laygen.templates.get_template(inst.cellname, libname=inst.libname)
        xy0 = inst.xy
        for p in t.pins:
            for pfix in inst_pin_prefix:
                if p.startswith(pfix):
                    xy_new=xy0 + t.pins[p]['xy']
                    xy.append(xy_new)
        generate_grids_from_xy(laygen, gridname_input, gridname_output, xy, xy_grid_type=xy_grid_type)
    #inst = laygen.get_inst(name=instname)
    #t = laygen.templates.get_template(inst.cellname, libname=template_libname)
    #xy0 = inst.xy
    #xy = []
    #for p in t.pins:
    #    for pfix in inst_pin_prefix:
    #        if p.startswith(pfix):
    #            xy.append(xy0 + t.pins[p]['xy'])
    #generate_grids_from_xy(laygen, gridname_input, gridname_output, xy, xy_grid_type=xy_grid_type)

def generate_grids_from_template(laygen, gridname_input, gridname_output, template_name, template_libname,
                                 template_pin_prefix=['VDD', 'VSS'], xy_grid_type=None, bnd=None, offset=np.array([0, 0])):
    """generate route grids combining a pre-existing grid and template pins
        it will create a new array by copying the given grid and update part of entries from xy coordinates of pins
    """
    t = laygen.templates.get_template(template_name, libname=template_libname)
    xy = []
    for p in t.pins:
        for pfix in template_pin_prefix:
            if p.startswith(pfix):
                xy.append(offset+t.pins[p]['xy'])
    generate_grids_from_xy_bnd(laygen, gridname_input, gridname_output, xy, xy_grid_type=xy_grid_type, bnd=bnd)
    # generate_grids_from_xy(laygen, gridname_input, gridname_output, xy, xy_grid_type=xy_grid_type)

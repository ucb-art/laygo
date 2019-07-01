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

"""Logic layout
"""
import laygo
import numpy as np
import yaml
import os
#import logging;logging.basicConfig(level=logging.DEBUG)

def create_io_pin(laygen, layer, gridname, pinname_list, rect_list, offset_y=np.array([-1, 1])):
    """create digital io pin"""
    rect_xy_list = [laygen.get_rect_xy(name=r.name, gridname=gridname, sort=True) for r in rect_list]
    #align pins
    ry = rect_xy_list[0][:, 1] + offset_y.T
    for i, xy_rect in enumerate(rect_xy_list):
        xy_rect[:, 1]=ry
        laygen.pin(name=pinname_list[i], layer=layer, xy=xy_rect, gridname=gridname)

def create_power_pin(laygen, layer, gridname, rect_vdd, rect_vss, pinname_vdd='VDD', pinname_vss='VSS'):
    """create power pin"""
    rvdd_pin_xy = laygen.get_rect_xy(name = rect_vdd.name, gridname = gridname)
    rvss_pin_xy = laygen.get_rect_xy(name = rect_vss.name, gridname = gridname)
    laygen.pin(name=pinname_vdd, layer=layer, xy=rvdd_pin_xy, gridname=gridname)
    laygen.pin(name=pinname_vss, layer=layer, xy=rvss_pin_xy, gridname=gridname)

def generate_tgate_dn(laygen, objectname_pfix,
                 placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                 devname_nmos_boundary, devname_nmos_body, devname_nmos_space,
                 devname_pmos_boundary, devname_pmos_body, devname_pmos_space,
                 m=1, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m = max(1, int(m / 2))  # using nf=2 devices

    # placement
    in_space = laygen.place("I"+objectname_pfix+'NDMY', devname_nmos_space, pg, shape=np.array([2, 1]), xy=origin)
    in0 = laygen.relplace(name = "I" + objectname_pfix + 'N0', templatename = devname_nmos_boundary, gridname = pg, refinstname = in_space.name)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    in3 = laygen.relplace(name = "I"+objectname_pfix+'N3', templatename = devname_nmos_body, gridname = pg, refinstname = in2.name)
    in4 = laygen.relplace(name = "I"+objectname_pfix+'N4', templatename = devname_nmos_boundary, gridname = pg, refinstname = in3.name)

    ip_space = laygen.relplace(name = "I"+objectname_pfix+'PDMY', templatename = devname_pmos_space, gridname = pg, refinstname = in_space.name, direction='top', transform='MX', shape=np.array([2, 1]))
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip_space.name, transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P1', templatename = devname_pmos_body, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P2', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')
    ip3 = laygen.relplace(name = "I"+objectname_pfix+'P3', templatename = 'pmos4_fast_space', gridname = pg, refinstname = ip2.name, shape=np.array([3,1]), transform='MX')

    # route
    #to vss
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                refinstname0=in3.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                refinstname1=in3.name, refpinname1='S0', refinstindex1=np.array([0, 0]))
    laygen.via(None, np.array([0, 0]), refinstname=in3.name, gridname=rg_m1m2, refinstindex=np.array([0, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                refinstname0=in3.name, refpinname0='S1', refinstindex0=np.array([0, 0]),
                refinstname1=in3.name, refpinname1='S1', refinstindex1=np.array([0, 0]))
    laygen.via(None, np.array([0, 0]), refinstname=in3.name, gridname=rg_m1m2, refinstindex=np.array([1, 0]))

    
    # en, enb
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-3, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-3, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip1.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
    ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-3, 0]), xy1=np.array([-3, 2]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
    laygen.via(None, np.array([-3, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    renb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2, 0]), xy1=np.array([-2, 2]), gridname0=rg_m2m3,
                       refinstname0=ip1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    laygen.via(None, np.array([-2, 0]), refinstname=ip1.name, refpinname='G0', gridname=rg_m2m3)

    in3_g0_xy = laygen.get_inst_pin_xy(in3.name, 'G0', rg_m2m3)    
    ip1_g0_xy = laygen.get_inst_pin_xy(ip1.name, 'G0', rg_m2m3)
    laygen.route_vh(layerv=laygen.layers['metal'][3], layerh=laygen.layers['metal'][2], xy0=in3_g0_xy[0], xy1=ip1_g0_xy[0], gridname0=rg_m2m3)
    laygen.via(None, xy=in3_g0_xy[0], gridname=rg_m2m3)
    in3_g0_xy = laygen.get_inst_pin_xy(in3.name, 'G0', rg_m1m2)
    laygen.via(None, xy=in3_g0_xy[0], gridname=rg_m1m2)

    #input
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S0', refinstindex=np.array([0, 0]), gridname=rg_m2m3)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='S0', refinstindex=np.array([0, 0]), gridname=rg_m2m3)
    ri0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                       refinstname1=ip1.name, refpinname1='S0', refinstindex1=np.array([0, 0]))
    #output
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    #add for in3
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([m-1, 0]),
                 refinstname1=in3.name, refpinname1='D0', refinstindex1=np.array([0, 0]))

    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([m-1, 0]), gridname=rg_m2m3)
    laygen.via(None, np.array([0, 1]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([m-1, 0]), gridname=rg_m2m3)

    #add for in3
    laygen.via(None, np.array([0, 1]), refinstname=in3.name, refpinname='D0', refinstindex=np.array([0, 0]), gridname=rg_m1m2)

    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([m-1, 0]),
                       refinstname1=ip1.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))

    # power and groud rail
    xy = laygen.get_template_xy(name = ip3.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd = laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=ip_space.name, refinstname1=ip3.name, refinstindex1=np.array([2, 0]))
    rvss = laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=in_space.name, refinstname1=in4.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['EN', 'ENB', 'I', 'O'], rect_list=[ren0, renb0, ri0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_space_1x(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2=routing_grid_m1m2

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', 'nmos4_fast_space', pg, xy=origin)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = 'pmos4_fast_space', gridname = pg, refinstname = in0.name, direction='top', transform='MX')

    # power and groud rail
    xy = laygen.get_template_xy(name = in0.cellname, gridname = rg_m1m2) * np.array([1, 0])
    laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)

    # power pin
    if create_pin==True:
        rvdd_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VDD0", gridname = rg_m1m2)
        rvss_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS0", gridname = rg_m1m2)
        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2)

def generate_space_2x(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2=routing_grid_m1m2

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', 'nmos4_fast_space_2x', pg, xy=origin)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = 'pmos4_fast_space_2x', gridname = pg, refinstname = in0.name, direction='top', transform='MX')

    # power and groud rail
    xy = laygen.get_template_xy(name = in0.cellname, gridname = rg_m1m2) * np.array([1, 0])
    laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)

    # power pin
    if create_pin==True:
        rvdd_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VDD0", gridname = rg_m1m2)
        rvss_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS0", gridname = rg_m1m2)
        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2)

def generate_space_4x(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2=routing_grid_m1m2

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', 'nmos4_fast_space_nf4', pg, xy=origin)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = 'pmos4_fast_space_nf4', gridname = pg, refinstname = in0.name, direction='top', transform='MX')

    # power and groud rail
    xy = laygen.get_template_xy(name = in0.cellname, gridname = rg_m1m2) * np.array([1, 0])
    laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)

    # power pin
    if create_pin==True:
        rvdd_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VDD0", gridname = rg_m1m2)
        rvss_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS0", gridname = rg_m1m2)
        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2)

def generate_space_wovdd_1x(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2=routing_grid_m1m2

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', 'nmos4_fast_space', pg, xy=origin)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = 'nmos4_fast_space', gridname = pg, refinstname = in0.name, direction='top', transform='MX')

    # power and groud rail
    xy = laygen.get_template_xy(name = in0.cellname, gridname = rg_m1m2) * np.array([1, 0])
    laygen.route("R"+objectname_pfix+"VSS1", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)

    # power pin
    if create_pin==True:
        rvdd_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS1", gridname = rg_m1m2)
        rvss_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS0", gridname = rg_m1m2)
        laygen.pin(name='VSS1', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2, netname='VSS')
        laygen.pin(name='VSS0', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2, netname='VSS')

def generate_space_wovdd_2x(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2=routing_grid_m1m2

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', 'nmos4_fast_space_2x', pg, xy=origin)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = 'nmos4_fast_space_2x', gridname = pg, refinstname = in0.name, direction='top', transform='MX')

    # power and groud rail
    xy = laygen.get_template_xy(name = in0.cellname, gridname = rg_m1m2) * np.array([1, 0])
    laygen.route("R"+objectname_pfix+"VSS1", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)

    # power pin
    if create_pin==True:
        rvdd_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS1", gridname = rg_m1m2)
        rvss_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS0", gridname = rg_m1m2)
        laygen.pin(name='VSS1', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2, netname='VSS')
        laygen.pin(name='VSS0', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2, netname='VSS')

def generate_space_wovdd_4x(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2=routing_grid_m1m2

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', 'nmos4_fast_space_nf4', pg, xy=origin)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = 'nmos4_fast_space_nf4', gridname = pg, refinstname = in0.name, direction='top', transform='MX')

    # power and groud rail
    xy = laygen.get_template_xy(name = in0.cellname, gridname = rg_m1m2) * np.array([1, 0])
    laygen.route("R"+objectname_pfix+"VSS1", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)

    # power pin
    if create_pin==True:
        rvdd_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS1", gridname = rg_m1m2)
        rvss_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS0", gridname = rg_m1m2)
        laygen.pin(name='VSS1', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2, netname='VSS')
        laygen.pin(name='VSS0', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2, netname='VSS')

def generate_tap(laygen, objectname_pfix, placement_grid, routing_grid_m1m2,
                 devname_nmos_tap, devname_pmos_tap, origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2=routing_grid_m1m2

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_tap, pg, xy=origin)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = devname_pmos_tap, gridname = pg, refinstname = in0.name, direction='top', transform='MX')

    #tap route
    xy_tap0 = laygen.get_template_pin_xy(in0.cellname, 'TAP0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap0 * np.array([1, 0]), xy1=xy_tap0, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap0 * np.array([1, 0])+[0,1], xy1=xy_tap0, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=in0.name)
    laygen.via(None, xy_tap0 * np.array([1, 0]), refinstname=in0.name, gridname=rg_m1m2)
    #laygen.via(None, xy_tap0 * np.array([1, 0]), refinstname=ip0.name, gridname=rg_m1m2)
    xy_tap1 = laygen.get_template_pin_xy(in0.cellname, 'TAP0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap1 * np.array([1, 0]), xy1=xy_tap1, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap1 * np.array([1, 0])+[0,1], xy1=xy_tap1, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=in0.name)
    laygen.via(None, xy_tap1 * np.array([1, 0]), refinstname=in0.name, gridname=rg_m1m2)
    #laygen.via(None, xy_tap1 * np.array([1, 0]), refinstname=ip0.name, gridname=rg_m1m2)

    # power and groud rail
    xy = laygen.get_template_xy(name = in0.cellname, gridname = rg_m1m2) * np.array([1, 0])
    laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)

    # power pin
    if create_pin==True:
        rvdd_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VDD0", gridname = rg_m1m2)
        rvss_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS0", gridname = rg_m1m2)
        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2)

def generate_tap_float(laygen, objectname_pfix, placement_grid, routing_grid_m1m2,
                 devname_nmos_tap, devname_pmos_tap, origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2=routing_grid_m1m2

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_tap, pg, xy=origin)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = devname_pmos_tap, gridname = pg, refinstname = in0.name, direction='top', transform='MX')

    #tap route
    xy_tap0 = laygen.get_template_pin_xy(in0.cellname, 'TAP0', rg_m1m2)[0, :]
    #laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap0 * np.array([1, 0]), xy1=xy_tap0, gridname0=rg_m1m2,
    #             refinstname0=in0.name, refinstname1=in0.name)
    #laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap0 * np.array([1, 0]), xy1=xy_tap0, gridname0=rg_m1m2,
    #             refinstname0=ip0.name, refinstname1=in0.name)
    #laygen.via(None, xy_tap0 * np.array([1, 0]), refinstname=in0.name, gridname=rg_m1m2)
    #laygen.via(None, xy_tap0 * np.array([1, 0]), refinstname=ip0.name, gridname=rg_m1m2)
    xy_tap1 = laygen.get_template_pin_xy(in0.cellname, 'TAP0', rg_m1m2)[0, :]
    #laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap1 * np.array([1, 0]), xy1=xy_tap1, gridname0=rg_m1m2,
    #             refinstname0=in0.name, refinstname1=in0.name)
    #laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap1 * np.array([1, 0]), xy1=xy_tap1, gridname0=rg_m1m2,
    #             refinstname0=ip0.name, refinstname1=in0.name)
    laygen.route(None, laygen.layers['metal'][2], xy0=xy_tap1, xy1=xy_tap1-np.array([2,0]), gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name, via0=np.array([0,0]), via1=np.array([0,0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap1 * np.array([1, 0])-np.array([2,0]), xy1=xy_tap1-np.array([2,0]), gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=ip0.name)
    laygen.via(None, xy_tap1 * np.array([1, 0]) - np.array([2,0]), refinstname=in0.name, gridname=rg_m1m2)
    #laygen.via(None, xy_tap1 * np.array([1, 0]), refinstname=ip0.name, gridname=rg_m1m2)

    # power and groud rail
    xy = laygen.get_template_xy(name = in0.cellname, gridname = rg_m1m2) * np.array([1, 0])
    laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)

    # power pin
    if create_pin==True:
        rvdd_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VDD0", gridname = rg_m1m2)
        rvss_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS0", gridname = rg_m1m2)
        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2)

def generate_tap_wovdd(laygen, objectname_pfix, placement_grid, routing_grid_m1m2,
                 devname_nmos_tap, origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2=routing_grid_m1m2

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_tap, pg, xy=origin)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = devname_nmos_tap, gridname = pg, refinstname = in0.name, direction='top', transform='MX')

    #tap route
    xy_tap0 = laygen.get_template_pin_xy(in0.cellname, 'TAP0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap0 * np.array([1, 0]), xy1=xy_tap0, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap0 * np.array([1, 0]), xy1=xy_tap0, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.via(None, xy_tap0 * np.array([1, 0]), refinstname=in0.name, gridname=rg_m1m2)
    laygen.via(None, xy_tap0 * np.array([1, 0]), refinstname=ip0.name, gridname=rg_m1m2)
    xy_tap1 = laygen.get_template_pin_xy(in0.cellname, 'TAP0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap1 * np.array([1, 0]), xy1=xy_tap1, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap1 * np.array([1, 0]), xy1=xy_tap1, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.via(None, xy_tap1 * np.array([1, 0]), refinstname=in0.name, gridname=rg_m1m2)
    laygen.via(None, xy_tap1 * np.array([1, 0]), refinstname=ip0.name, gridname=rg_m1m2)

    # power and groud rail
    xy = laygen.get_template_xy(name = in0.cellname, gridname = rg_m1m2) * np.array([1, 0])
    laygen.route("R"+objectname_pfix+"VSS1", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)

    # power pin
    if create_pin==True:
        rvdd_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS1", gridname = rg_m1m2)
        rvss_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS0", gridname = rg_m1m2)
        laygen.pin(name='VSS1', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2, netname='VSS')
        laygen.pin(name='VSS0', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2, netname='VSS')

def generate_plugged_tap(laygen, objectname_pfix, placement_grid, routing_grid_m1m2,
                 devname_nmos_tap, devname_pmos_tap, devname_plug, origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2=routing_grid_m1m2

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_tap, pg, xy=origin)
    iplug0 = laygen.place("I"+objectname_pfix + 'PLUG0', devname_plug, pg, xy=origin)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = devname_pmos_tap, gridname = pg, refinstname = in0.name, direction='top', transform='MX')

    #tap route
    xy_tap0 = laygen.get_template_pin_xy(in0.cellname, 'TAP0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap0 * np.array([1, 0]), xy1=xy_tap0, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap0 * np.array([1, 0]), xy1=xy_tap0, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.via(None, xy_tap0 * np.array([1, 0]), refinstname=in0.name, gridname=rg_m1m2)
    laygen.via(None, xy_tap0 * np.array([1, 0]), refinstname=ip0.name, gridname=rg_m1m2)
    xy_tap1 = laygen.get_template_pin_xy(in0.cellname, 'TAP0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap1 * np.array([1, 0]), xy1=xy_tap1, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_tap1 * np.array([1, 0]), xy1=xy_tap1, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.via(None, xy_tap1 * np.array([1, 0]), refinstname=in0.name, gridname=rg_m1m2)
    laygen.via(None, xy_tap1 * np.array([1, 0]), refinstname=ip0.name, gridname=rg_m1m2)

    # power and groud rail
    xy = laygen.get_template_xy(name = in0.cellname, gridname = rg_m1m2) * np.array([1, 0])
    laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)

    # power pin
    if create_pin==True:
        rvdd_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VDD0", gridname = rg_m1m2)
        rvss_pin_xy = laygen.get_rect_xy(name = "R"+objectname_pfix+"VSS0", gridname = rg_m1m2)
        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2)

def generate_tie(laygen, objectname_pfix,
                 placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                 devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_body,
                 m=1, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m=max(1, int(m/2)) #using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix+'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P1', templatename = devname_pmos_body, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P3', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')

    # route
    # horizontal route style
    # input
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refpinname1='D0', refinstindex1=np.array([i, 0]),
                     )
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=ip1.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refpinname1='D0', refinstindex1=np.array([i, 0]),
                     )
    # vdd/vss
    if m==1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]),
                     )
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=ip1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]),
                     )
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=ip1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='S0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S1', refinstindex=np.array([m-1, 0]),
               gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='S1', refinstindex=np.array([m-1, 0]),
               gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S0', refinstindex=np.array([m-1, 0]),
               gridname=rg_m2m3)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='S1', refinstindex=np.array([m-1, 0]),
               gridname=rg_m2m3)

    rvss = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                       refinstname1=ip1.name, refpinname1='S0', refinstindex1=np.array([0, 0]))
    rvdd = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='S1', refinstindex0=np.array([m-1, 0]),
                       refinstname1=ip1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))

    #align output to input pin
    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip2.name)
    laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in2.name)
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,refinstindex=np.array([i, 0]))
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=np.array([m-1, 0]),
                 refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=ip1.name, refinstindex0=np.array([m-1, 0]),
                 refinstname1=ip1.name, refinstindex1=np.array([m-1, 0]))
    laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,refinstindex=np.array([m-1, 0]))
    laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,refinstindex=np.array([m-1, 0]))

    # pin
    rvdd0_pin_xy = laygen.get_rect_xy(name = rvdd.name, gridname = rg_m2m3_pin, sort=True)
    rvss0_pin_xy = laygen.get_rect_xy(name = rvss.name, gridname = rg_m2m3_pin, sort=True)
    rvdd0_pin_xy[0][1] = rvss0_pin_xy[0][1] - 1
    rvdd0_pin_xy[1][1] = rvss0_pin_xy[1][1] + 1
    rvss0_pin_xy[0][1] = rvss0_pin_xy[0][1] - 1
    rvss0_pin_xy[1][1] = rvss0_pin_xy[1][1] + 1

    if create_pin == True:
        laygen.pin(name='TIEVDD', layer=laygen.layers['pin'][3], xy=rvdd0_pin_xy, gridname=rg_m2m3_pin, netname='VDD')
        laygen.pin(name='TIEVSS', layer=laygen.layers['pin'][3], xy=rvss0_pin_xy, gridname=rg_m2m3_pin, netname='VSS')

        # power pin
        rvdd_pin_xy = laygen.get_rect_xy(name = "R" + objectname_pfix + "VDD0", gridname = rg_m1m2)
        rvss_pin_xy = laygen.get_rect_xy(name = "R" + objectname_pfix + "VSS0", gridname = rg_m1m2)
        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2)

def generate_tie_wovdd(laygen, objectname_pfix,
                 placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                 devname_nmos_boundary, devname_nmos_body, 
                 m=1, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m=max(1, int(m/2)) #using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix+'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    in0b = laygen.relplace(name = "I"+objectname_pfix+'N0B', templatename = devname_nmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    in1b = laygen.relplace(name = "I"+objectname_pfix+'N1B', templatename = devname_nmos_body, gridname = pg, refinstname = in0b.name, transform='MX', shape=np.array([m, 1]))
    in2b = laygen.relplace(name = "I"+objectname_pfix+'N2B', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1b.name, transform='MX')

    # route
    # horizontal route style
    # input
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refpinname1='D0', refinstindex1=np.array([i, 0]),
                     )
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in1b.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=in1b.name, refpinname1='D0', refinstindex1=np.array([i, 0]),
                     )
    # vdd/vss
    if m==1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]),
                     )
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=in1b.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1b.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]),
                     )
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=in1b.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1b.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=in1b.name, refpinname='S0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S1', refinstindex=np.array([m-1, 0]),
               gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1b.name, refpinname='S1', refinstindex=np.array([m-1, 0]),
               gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S0', refinstindex=np.array([m-1, 0]),
               gridname=rg_m2m3)
    laygen.via(None, np.array([0, 0]), refinstname=in1b.name, refpinname='S1', refinstindex=np.array([m-1, 0]),
               gridname=rg_m2m3)

    rvss = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                       refinstname1=in1b.name, refpinname1='S0', refinstindex1=np.array([0, 0]))
    rvdd = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='S1', refinstindex0=np.array([m-1, 0]),
                       refinstname1=in1b.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))

    #align output to input pin
    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    laygen.route("R"+objectname_pfix+"VSS1", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0b.name, refinstname1=in2b.name)
    laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in2.name)
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1b.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in1b.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1b.name, gridname=rg_m1m2,refinstindex=np.array([i, 0]))
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=np.array([m-1, 0]),
                 refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=in1b.name, refinstindex0=np.array([m-1, 0]),
                 refinstname1=in1b.name, refinstindex1=np.array([m-1, 0]))
    laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,refinstindex=np.array([m-1, 0]))
    laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in1b.name, gridname=rg_m1m2,refinstindex=np.array([m-1, 0]))

    # pin
    rvdd0_pin_xy = laygen.get_rect_xy(name = rvdd.name, gridname = rg_m2m3_pin, sort=True)
    rvss0_pin_xy = laygen.get_rect_xy(name = rvss.name, gridname = rg_m2m3_pin, sort=True)
    rvdd0_pin_xy[0][1] = rvss0_pin_xy[0][1] - 1
    rvdd0_pin_xy[1][1] = rvss0_pin_xy[1][1] + 1
    rvss0_pin_xy[0][1] = rvss0_pin_xy[0][1] - 1
    rvss0_pin_xy[1][1] = rvss0_pin_xy[1][1] + 1

    if create_pin == True:
        laygen.pin(name='TIEVSS2', layer=laygen.layers['pin'][3], xy=rvdd0_pin_xy, gridname=rg_m2m3_pin, netname='VSS')
        laygen.pin(name='TIEVSS', layer=laygen.layers['pin'][3], xy=rvss0_pin_xy, gridname=rg_m2m3_pin, netname='VSS')

        # power pin
        rvdd_pin_xy = laygen.get_rect_xy(name = "R" + objectname_pfix + "VSS1", gridname = rg_m1m2)
        rvss_pin_xy = laygen.get_rect_xy(name = "R" + objectname_pfix + "VSS0", gridname = rg_m1m2)
        laygen.pin(name='VSS1', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2, netname='VSS')
        laygen.pin(name='VSS0', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2, netname='VSS')

def generate_bcap(laygen, objectname_pfix,
                  placement_grid, routing_grid_m1m2,
                  devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_space,
                  m=2, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2

    m = max(1, int(m / 2))  # using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix+'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_space, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P1', templatename = devname_pmos_space, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m*2, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P3', templatename = devname_pmos_space, gridname = pg, refinstname = ip1.name, transform='MX')

    # route
    #pdict = [laygen.get_inst_pin_xy(None, None, rg_m1m2, index=np.array([i, 0])) for i in range(m)]
    xy_g0 = laygen.get_template_pin_xy(in1.cellname, 'G0', rg_m1m2)[0, :]
    xy_d0 = laygen.get_template_pin_xy(in1.cellname, 'D0', rg_m1m2)[0, :]
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1*np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
    if m > 1:
        #gate
        laygen.route(None, laygen.layers['metal'][2], xy0=xy_g0, xy1=xy_g0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
        for i in range(m):
            laygen.via(None, xy_g0, refinstname=in1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        rg0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                           refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
        #drain
        laygen.route(None, laygen.layers['metal'][2], xy0=xy_d0, xy1=xy_d0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
        for i in range(m):
            laygen.via(None, xy_d0, refinstname=in1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)

    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip2.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in2.name)

    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['I'], rect_list=[rg0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_dcap(laygen, objectname_pfix,
                  placement_grid, routing_grid_m1m2,
                  devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_space, 
                  m=2, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2

    m = max(1, int(m / 2))  # using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix+'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    #ip1 = laygen.relplace(name = "I"+objectname_pfix+'P1', templatename = devname_pmos_space, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m*2, 1]))
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P1', templatename = devname_pmos_space, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m, 1]))
    ip1b = laygen.relplace(name = "I"+objectname_pfix+'P1B', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m*2, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P3', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')

    # route
    #pdict = [laygen.get_inst_pin_xy(None, None, rg_m1m2, index=np.array([i, 0])) for i in range(m)]
    xy_g0 = laygen.get_template_pin_xy(in1.cellname, 'G0', rg_m1m2)[0, :]
    xy_d0 = laygen.get_template_pin_xy(in1.cellname, 'D0', rg_m1m2)[0, :]
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        #laygen.route(None, laygen.layers['metal'][1], xy0=xy_g0*np.array([1, 0]), xy1=xy_g0, gridname0=rg_m1m2,
        #             refinstname0=ip1.name, refinstindex0=np.array([i*2, 0]), via0=[[0, 0]],
        #             refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_g0*np.array([1, 0]), xy1=xy_g0, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1*np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
    if m > 1:
        laygen.route(None, laygen.layers['metal'][2], xy0=xy_d0, xy1=xy_d0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
        for i in range(m):
            laygen.via(None, xy_d0, refinstname=in1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)

    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip2.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in2.name)

    # pin
    if create_pin == True:
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_dcap2(laygen, objectname_pfix,
                   placement_grid, routing_grid_m1m2, routing_grid_m2m3,
                   devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_body, 
                   m=2, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2

    m = max(1, int(m / 2))  # using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix+'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P1', templatename = devname_pmos_body, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P2', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')

    # route
    #pdict = [laygen.get_inst_pin_xy(None, None, rg_m1m2, index=np.array([i, 0])) for i in range(m)]
    xy_g0 = laygen.get_template_pin_xy(in1.cellname, 'G0', rg_m1m2)[0, :]
    xy_d0 = laygen.get_template_pin_xy(in1.cellname, 'D0', rg_m1m2)[0, :]
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    #gate route
    laygen.route(None, laygen.layers['metal'][2], xy0=xy_g0, xy1=xy_g0, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=np.array([0, 0]), 
                 refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=xy_g0, xy1=xy_g0, gridname0=rg_m1m2,
                 refinstname0=ip1.name, refinstindex0=np.array([0, 0]), 
                 refinstname1=ip1.name, refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, xy_g0, refinstname=in1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, xy_g0, refinstname=ip1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #source route
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1*np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1*np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
    #drain route
    if m > 1:
        laygen.route(None, laygen.layers['metal'][2], xy0=xy_d0+np.array([0, 1]), xy1=xy_d0+np.array([0, 1]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
        for i in range(m):
            laygen.via(None, xy_d0+np.array([0, 1]), refinstname=in1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.route(None, laygen.layers['metal'][2], xy0=xy_d0+np.array([0, 1]), xy1=xy_d0+np.array([0, 1]), gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([0, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([m-1, 0]))
        for i in range(m):
            laygen.via(None, xy_d0+np.array([0, 1]), refinstname=ip1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    # vss/vdd vertical route
    laygen.route(None, laygen.layers['metal'][3], xy0=xy_g0*np.array([1, 0]), xy1=xy_g0, gridname0=rg_m2m3,
                 refinstname0=ip1.name, refinstname1=in1.name, 
                 refinstindex0=np.array([0, 0]), refinstindex1=np.array([0, 0]), via0=[[0, 0]], via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][3], xy0=xy_g0*np.array([1, 0]), xy1=xy_g0, gridname0=rg_m2m3,
                 refinstname0=in1.name, refinstname1=ip1.name, 
                 refinstindex0=np.array([m-1, 0]), refinstindex1=np.array([m-1, 0]), via0=[[0, 0]], via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][3], xy0=xy_g0*np.array([1, 0])+np.array([0, 2]), xy1=xy_g0*np.array([1, 0]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refinstname1=in1.name, 
                 refinstindex0=np.array([m-1, 0]), refinstindex1=np.array([m-1, 0]), via0=[[0, 0]], via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][3], xy0=xy_g0*np.array([1, 0])+np.array([0, 2]), xy1=xy_g0*np.array([1, 0]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refinstname1=ip1.name, 
                 refinstindex0=np.array([0, 0]), refinstindex1=np.array([0, 0]), via0=[[0, 0]], via1=[[0, 0]])
    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip2.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in2.name)

    # pin
    if create_pin == True:
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_dcap3(laygen, objectname_pfix,
                  placement_grid, routing_grid_m1m2,
                  devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_space, 
                  m=2, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2

    m = max(1, int(m / 2))  # using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix+'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    #ip1 = laygen.relplace(name = "I"+objectname_pfix+'P1', templatename = devname_pmos_space, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m*2, 1]))
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P1', templatename = devname_pmos_space, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m, 1]))
    ip1b = laygen.relplace(name = "I"+objectname_pfix+'P1B', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m*2, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P3', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')

    # route
    #pdict = [laygen.get_inst_pin_xy(None, None, rg_m1m2, index=np.array([i, 0])) for i in range(m)]
    xy_g0 = laygen.get_template_pin_xy(in1.cellname, 'G0', rg_m1m2)[0, :]
    xy_d0 = laygen.get_template_pin_xy(in1.cellname, 'D0', rg_m1m2)[0, :]
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    #vss
    '''
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1*np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
    '''
    '''
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                 refinstname1=in1.name, refinstindex1=np.array([0, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1*np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=np.array([m-1, 0]), via0=[[0, 0]],
                 refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
    '''
    laygen.route(None, laygen.layers['metal'][2], xy0=xy_d0, xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
    for i in range(m-1):
        laygen.via(None, xy_d0, refinstname=in1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, xy_s1, refinstname=in1.name, refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=xy_s0+np.array([0, 1]), xy1=xy_d0+np.array([0, 1]), 
                 gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
    laygen.via(None, xy_d0+np.array([0, 1]), refinstname=in1.name, refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    laygen.via(None, xy_s0+np.array([0, 1]), refinstname=in1.name, refinstindex=np.array([0, 0]), gridname=rg_m1m2)
    #gate
    laygen.route(None, laygen.layers['metal'][2], xy0=xy_g0, xy1=xy_g0, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, xy_g0, refinstname=in1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_g0, xy1=xy_g0+np.array([0, 2]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstname1=in1.name, via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][2], xy0=xy_g0+np.array([0, 2]), xy1=xy_g0+np.array([3, 2]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstname1=in1.name, via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_g0*np.array([1, 0])+np.array([3, 0]), 
                 xy1=xy_g0+np.array([3, 2]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, via0=[[0, 0]],
                 refinstname1=in1.name)

    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip2.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in2.name)

    # pin
    if create_pin == True:
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_bcap2(laygen, objectname_pfix,
                   placement_grid, routing_grid_m1m2, routing_grid_m2m3,
                   devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_body, 
                   m=2, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2

    m = max(1, int(m / 2))  # using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix+'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P1', templatename = devname_pmos_body, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P2', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')

    # route
    #pdict = [laygen.get_inst_pin_xy(None, None, rg_m1m2, index=np.array([i, 0])) for i in range(m)]
    xy_g0 = laygen.get_template_pin_xy(in1.cellname, 'G0', rg_m1m2)[0, :]
    xy_d0 = laygen.get_template_pin_xy(in1.cellname, 'D0', rg_m1m2)[0, :]
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    #gate route
    laygen.route(None, laygen.layers['metal'][2], xy0=xy_g0, xy1=xy_g0, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=np.array([0, 0]), 
                 refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=xy_g0, xy1=xy_g0, gridname0=rg_m1m2,
                 refinstname0=ip1.name, refinstindex0=np.array([0, 0]), 
                 refinstname1=ip1.name, refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, xy_g0, refinstname=in1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, xy_g0, refinstname=ip1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #source route
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1*np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1*np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
    #drain route
    if m > 1:
        laygen.route(None, laygen.layers['metal'][2], xy0=xy_d0+np.array([0, 1]), xy1=xy_d0+np.array([0, 1]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
        for i in range(m):
            laygen.via(None, xy_d0+np.array([0, 1]), refinstname=in1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.route(None, laygen.layers['metal'][2], xy0=xy_d0+np.array([0, 1]), xy1=xy_d0+np.array([0, 1]), gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([0, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([m-1, 0]))
        for i in range(m):
            laygen.via(None, xy_d0+np.array([0, 1]), refinstname=ip1.name, refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #input route
    rg0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2, 0]), xy1=np.array([2, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0', via0=[[0, 0]], via1=[[0, 0]])
    # vss/vdd vertical route
    #laygen.route(None, laygen.layers['metal'][3], xy0=xy_g0*np.array([1, 0]), xy1=xy_g0, gridname0=rg_m2m3,
    #             refinstname0=ip1.name, refinstname1=in1.name, 
    #             refinstindex0=np.array([0, 0]), refinstindex1=np.array([0, 0]), via0=[[0, 0]], via1=[[0, 0]])
    #laygen.route(None, laygen.layers['metal'][3], xy0=xy_g0*np.array([1, 0]), xy1=xy_g0, gridname0=rg_m2m3,
    #             refinstname0=in1.name, refinstname1=ip1.name, 
    #             refinstindex0=np.array([m-1, 0]), refinstindex1=np.array([m-1, 0]), via0=[[0, 0]], via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][3], xy0=xy_g0*np.array([1, 0])+np.array([0, 2]), xy1=xy_g0*np.array([1, 0]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refinstname1=in1.name, 
                 refinstindex0=np.array([m-1, 0]), refinstindex1=np.array([m-1, 0]), via0=[[0, 0]], via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][3], xy0=xy_g0*np.array([1, 0])+np.array([0, 2]), xy1=xy_g0*np.array([1, 0]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refinstname1=ip1.name, 
                 refinstindex0=np.array([0, 0]), refinstindex1=np.array([0, 0]), via0=[[0, 0]], via1=[[0, 0]])
    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip2.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in2.name)

    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['I'], rect_list=[rg0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_inv(laygen, objectname_pfix,
                 placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                 devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_body,
                 m=1, pin_i_abut='nmos', origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m = max(1, int(m / 2))  # using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix+'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P1', templatename = devname_pmos_body, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P3', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')

    # route
    # horizontal route style
    # input
    if pin_i_abut=="nmos": refinstname_in=in1.name
    else: refinstname_in=ip1.name
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refpinname1='G0', refinstindex1=np.array([i, 0]),
                     )
        laygen.via(None, np.array([0, 0]), refinstname=refinstname_in, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    if m==1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=refinstname_in, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=refinstname_in, refpinname1='G0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
        ri0 = laygen.route("R"+objectname_pfix+"I0", laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                           refinstname0=refinstname_in, refpinname0='G0', refinstname1=refinstname_in, refpinname1='G0')
        laygen.via(None, np.array([-1, 0]), refinstname=refinstname_in, refpinname='G0', gridname=rg_m2m3)
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=refinstname_in, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=refinstname_in, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
        ri0 = laygen.route("R"+objectname_pfix+"I0", laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                           refinstname0=refinstname_in, refpinname0='G0', refinstname1=refinstname_in, refpinname1='G0')
        laygen.via(None, np.array([0, 0]), refinstname=refinstname_in, refpinname='G0', gridname=rg_m2m3)

    # output
    if m==1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([1, 1]), gridname0=rg_m2m3,
                     refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m2m3,
                     refinstname0=ip1.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip1.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                     refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=ip1.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip1.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([m-1, 0]),
               gridname=rg_m2m3)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([m-1, 0]),
               gridname=rg_m2m3)

    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([m-1, 0]),
                       refinstname1=ip1.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))

    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip2.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in2.name)
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,refinstindex=np.array([i, 0]))
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=np.array([m-1, 0]),
                 refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=ip1.name, refinstindex0=np.array([m-1, 0]),
                 refinstname1=ip1.name, refinstindex1=np.array([m-1, 0]))
    laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,refinstindex=np.array([m-1, 0]))
    laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,refinstindex=np.array([m-1, 0]))

    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['I', 'O'], rect_list=[ri0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_inv_1x(laygen, objectname_pfix,
                    placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                    devname_nmos_boundary, devname_nmos_body, devname_nmos_space,
                    devname_pmos_boundary, devname_pmos_body, devname_pmos_space,
                    pin_i_abut='nmos', pin_o_y=0, origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix + 'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name)
    in2 = laygen.relplace(name = "I"+objectname_pfix + 'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    in3 = laygen.relplace(name = "I"+objectname_pfix + 'N3', templatename = devname_nmos_space, gridname = pg, refinstname = in2.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix + 'P1', templatename = devname_pmos_body, gridname = pg, refinstname = ip0.name, transform='MX')
    ip2 = laygen.relplace(name = "I"+objectname_pfix + 'P2', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')
    ip3 = laygen.relplace(name = "I"+objectname_pfix + 'P3', templatename = devname_pmos_space, gridname = pg, refinstname = ip2.name, transform='MX')

    # route
    # input
    if pin_i_abut == "nmos":
        refinstname_in = in1.name
    else:
        refinstname_in = ip1.name
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=refinstname_in, refpinname='G0', gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([2, 0]), gridname0=rg_m1m2,
                 refinstname0=refinstname_in, refpinname0='G0',
                 refinstname1=refinstname_in, refpinname1='G0')
    ri0 = laygen.route("R"+objectname_pfix+"I0", laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                       refinstname0=refinstname_in, refpinname0='G0', refinstname1=refinstname_in, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=refinstname_in, refpinname='G0', gridname=rg_m2m3)
    # output
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, pin_o_y]), xy1=np.array([1, pin_o_y]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0', refinstname1=in1.name, refpinname1='D0',
                 endstyle0='extend', endstyle1='extend')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, pin_o_y]), xy1=np.array([1, pin_o_y]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='D0', refinstname1=ip1.name, refpinname1='D0',
                 endstyle0 = 'extend', endstyle1 = 'extend')
    ro0 = laygen.route("R" + objectname_pfix +"O0", laygen.layers['metal'][3], xy0=np.array([0, pin_o_y]),
                       xy1=np.array([0, pin_o_y]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstname1=ip1.name, refpinname1='D0')
    laygen.via(None, np.array([0, pin_o_y]), refinstname=in1.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, pin_o_y]), refinstname=ip1.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, pin_o_y]), refinstname=in1.name, refpinname='D0', gridname=rg_m2m3)
    laygen.via(None, np.array([0, pin_o_y]), refinstname=ip1.name, refpinname='D0', gridname=rg_m2m3)
    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd = laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=ip0.name, refinstname1=ip3.name)
    rvss = laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=in0.name, refinstname1=in3.name)
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstname1=in1.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=ip1.name, refinstname1=ip1.name)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['I', 'O'], rect_list=[ri0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_tgate(laygen, objectname_pfix,
                 placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                 devname_nmos_boundary, devname_nmos_body, devname_nmos_space,
                 devname_pmos_boundary, devname_pmos_body, devname_pmos_space,
                 m=1, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m = max(1, int(m / 2))  # using nf=2 devices

    # placement
    in_space = laygen.place("I"+objectname_pfix+'NDMY', devname_nmos_space, pg, shape=np.array([2, 1]), xy=origin)
    in0 = laygen.relplace(name = "I" + objectname_pfix + 'N0', templatename = devname_nmos_boundary, gridname = pg, refinstname = in_space.name)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    ip_space = laygen.relplace(name = "I"+objectname_pfix+'PDMY', templatename = devname_pmos_space, gridname = pg, refinstname = in_space.name, direction='top', transform='MX', shape=np.array([2, 1]))
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip_space.name, transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P2', templatename = devname_pmos_body, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P3', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')

    # route
    # en, enb
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-3, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-3, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip1.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
    ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-3, 0]), xy1=np.array([-3, 2]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
    laygen.via(None, np.array([-3, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    renb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2, 0]), xy1=np.array([-2, 2]), gridname0=rg_m2m3,
                       refinstname0=ip1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    laygen.via(None, np.array([-2, 0]), refinstname=ip1.name, refpinname='G0', gridname=rg_m2m3)

    #input
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S0', refinstindex=np.array([0, 0]), gridname=rg_m2m3)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='S0', refinstindex=np.array([0, 0]), gridname=rg_m2m3)
    ri0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                       refinstname1=ip1.name, refpinname1='S0', refinstindex1=np.array([0, 0]))
    #output
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([0, 0]), gridname=rg_m2m3)
    laygen.via(None, np.array([0, 1]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([0, 0]), gridname=rg_m2m3)
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([m-1, 0]),
                       refinstname1=ip1.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))

    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd = laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=ip0.name, refinstname1=ip2.name)
    rvss = laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=in0.name, refinstname1=in2.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['EN', 'ENB', 'I', 'O'], rect_list=[ren0, renb0, ri0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_nsw(laygen, objectname_pfix,
                 placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                 devname_nmos_boundary, devname_nmos_body, devname_nmos_space,
                 devname_pmos_boundary, devname_pmos_body, devname_pmos_space,
                 m=1, origin=np.array([0,0]), create_pin=False):
    #generate an nmos type switch
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m = max(1, int(m / 2))  # using nf=2 devices

    # placement
    in0 = laygen.place("I" + objectname_pfix + 'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_space, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P2', templatename = devname_pmos_space, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m*2, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P3', templatename = devname_pmos_space, gridname = pg, refinstname = ip1.name, transform='MX')
    #ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_space, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    #ip1 = laygen.relplace(name = "I"+objectname_pfix+'P2', templatename = devname_pmos_space, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m*2, 1]))
    #ip2 = laygen.relplace(name = "I"+objectname_pfix+'P3', templatename = devname_pmos_space, gridname = pg, refinstname = ip1.name, transform='MX')

    # route
    # en, enb
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
    ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
    laygen.via(None, np.array([-1, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)

    #input
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1+1, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    ri=[]
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S1', refinstindex=np.array([i, 0]), gridname=rg_m2m3)
        ri0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 4]), gridname0=rg_m2m3,
                           refinstname0=in1.name, refpinname0='S1', refinstindex0=np.array([i, 0]),
                           refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([i, 0]))
        ri.append(ri0)
    #output
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1+1, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]), endstyle0='extend',
                 refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]), endstyle1='extend')
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    ro=[]
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m2m3)
        ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 4]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([i, 0]),
                       refinstname1=in1.name, refpinname1='D0', refinstindex1=np.array([i, 0]))
        ro.append(ro0)

    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd = laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=ip0.name, refinstname1=ip2.name)
    rvss = laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=in0.name, refinstname1=in2.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['EN', 'I', 'O'], rect_list=[ren0, ri[0], ro[0]])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_nsw_wovdd(laygen, objectname_pfix,
                 placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                 devname_nmos_boundary, devname_nmos_body, devname_nmos_space,
                 m=1, origin=np.array([0,0]), create_pin=False):
    #generate an nmos type switch, without vdd rail
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m = max(1, int(m / 2))  # using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix+'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    in0b= laygen.relplace(name = "I"+objectname_pfix+'N0B', templatename = devname_nmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    in1b= laygen.relplace(name = "I"+objectname_pfix+'N2B', templatename = devname_nmos_body, gridname = pg, refinstname = in0b.name, transform='MX', shape=np.array([m, 1]))
    in2b= laygen.relplace(name = "I"+objectname_pfix+'N3B', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1b.name, transform='MX')

    # route
    # en, enb
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
    ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
    laygen.via(None, np.array([-1, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1b.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=in1b.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1b.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
    laygen.via(None, np.array([-1, 0]), refinstname=in1b.name, refpinname='G0', gridname=rg_m2m3)

    #input
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1+1, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    ri=[]
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S1', refinstindex=np.array([i, 0]), gridname=rg_m2m3)
        ri0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 4]), gridname0=rg_m2m3,
                           refinstname0=in1.name, refpinname0='S1', refinstindex0=np.array([i, 0]),
                           refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([i, 0]))
        ri.append(ri0)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1+1, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=in1b.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1b.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1b.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1b.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1b.name, refpinname='S1', refinstindex=np.array([i, 0]), gridname=rg_m2m3)
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 4]), gridname0=rg_m2m3,
                           refinstname0=in1b.name, refpinname0='S1', refinstindex0=np.array([i, 0]),
                           refinstname1=in1b.name, refpinname1='S1', refinstindex1=np.array([i, 0]))

    #output
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1+1, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]), endstyle0='extend',
                 refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]), endstyle1='extend')
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    ro=[]
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m2m3)
        ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 4]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([i, 0]),
                       refinstname1=in1.name, refpinname1='D0', refinstindex1=np.array([i, 0]))
        ro.append(ro0)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1+1, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1b.name, refpinname0='S0', refinstindex0=np.array([0, 0]), endstyle0='extend',
                 refinstname1=in1b.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]), endstyle1='extend')
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1b.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1b.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m2m3)
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 4]), gridname0=rg_m2m3,
                       refinstname0=in1b.name, refpinname0='D0', refinstindex0=np.array([i, 0]),
                       refinstname1=in1b.name, refpinname1='D0', refinstindex1=np.array([i, 0]))

    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvss = laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=in0.name, refinstname1=in2.name)
    rvss2 = laygen.route("R"+objectname_pfix+"VSS1", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=in0b.name, refinstname1=in2b.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['EN', 'I', 'O'], rect_list=[ren0, ri[0], ro[0]])
        rvss_pin_xy = laygen.get_rect_xy(name = rvss.name, gridname = rg_m1m2)
        rvss2_pin_xy = laygen.get_rect_xy(name = rvss2.name, gridname = rg_m1m2)
        laygen.pin(name='VSS0', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2, netname='VSS')
        laygen.pin(name='VSS1', layer=laygen.layers['pin'][2], xy=rvss2_pin_xy, gridname=rg_m1m2, netname='VSS')

def generate_nor(laygen, objectname_pfix,
                 placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                 devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_body,
                 m=1, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m=max(1, int(m/2)) #using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix + 'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I" + objectname_pfix + 'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    in3 = laygen.relplace(name = "I" + objectname_pfix + 'N3', templatename = devname_nmos_boundary, gridname = pg, refinstname = in2.name)
    in4 = laygen.relplace(name = "I"+objectname_pfix + 'N4', templatename = devname_nmos_body, gridname = pg, refinstname = in3.name, shape=np.array([m, 1]))
    in5 = laygen.relplace(name = "I"+objectname_pfix + 'N5', templatename = devname_nmos_boundary, gridname = pg, refinstname = in4.name)

    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix + 'P1', templatename = devname_pmos_body, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix + 'P2', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')
    ip3 = laygen.relplace(name = "I"+objectname_pfix + 'P3', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip2.name, transform='MX')
    ip4 = laygen.relplace(name = "I"+objectname_pfix + 'P4', templatename = devname_pmos_body, gridname = pg, refinstname = ip3.name, transform='MX', shape=np.array([m, 1]))
    ip5 = laygen.relplace(name = "I"+objectname_pfix + 'P5', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip4.name, transform='MX')

    # route
    # b0
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refpinname1='G0', refinstindex1=np.array([i, 0]),
                     )
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    if m == 1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]),
                     endstyle0="extend", endstyle1="extend")
        rb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                           refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0',
                           endstyle0="extend", endstyle1="extend")
        laygen.via(None, np.array([-1, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
        rb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                           refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0',
                           endstyle0="extend", endstyle1="extend")
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    # a0
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in4.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip4.name, refpinname1='G0', refinstindex1=np.array([i, 0]),
                     )
        laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    if m == 1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=ip4.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]),
                     endstyle0="extend", endstyle1="extend")
        ra0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                           refinstname0=ip4.name, refpinname0='G0', refinstname1=ip4.name, refpinname1='G0',
                           endstyle0="extend", endstyle1="extend")
        laygen.via(None, np.array([-1, 0]), refinstname=ip4.name, refpinname='G0', gridname=rg_m2m3)
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=ip4.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
        ra0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                           refinstname0=ip4.name, refpinname0='G0', refinstname1=ip4.name, refpinname1='G0',
                           endstyle0="extend", endstyle1="extend")
        laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='G0', gridname=rg_m2m3)

    # internal connection between mos
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0',
                 refinstname1=in4.name, refpinname1='D0', refinstindex1=np.array([m - 1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='D0',
                 refinstname1=ip4.name, refpinname1='S1', refinstindex1=np.array([m - 1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=in4.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip4.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 1]), refinstname=ip4.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    # output
    if m==1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m2m3,
                     refinstname0=ip4.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip4.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=ip4.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip4.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                       refinstname0=ip4.name, refpinname0='D0', refinstindex0=np.array([m - 1, 0]),
                       refinstname1=in4.name, refpinname1='D0', refinstindex1=np.array([m - 1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='D0', gridname=rg_m2m3, refinstindex=np.array([m - 1, 0]))
    laygen.via(None, np.array([0, 1]), refinstname=in4.name, refpinname='D0', gridname=rg_m2m3, refinstindex=np.array([m - 1, 0]))
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(ip1.cellname, 'S0', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in4.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in4.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in4.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
    xy_s1 = laygen.get_template_pin_xy(ip1.cellname, 'S1', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=in4.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in4.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in4.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
    # power and groud rail
    xy = laygen.get_template_xy(name = ip5.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip5.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in5.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['A', 'B', 'O'], rect_list=[ra0, rb0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_nand(laygen, objectname_pfix,
                     placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                     devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_body,
                     m=1, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m=max(1, int(m/2)) #using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix + 'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I" + objectname_pfix + 'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    in3 = laygen.relplace(name = "I" + objectname_pfix + 'N3', templatename = devname_nmos_boundary, gridname = pg, refinstname = in2.name)
    in4 = laygen.relplace(name = "I"+objectname_pfix + 'N4', templatename = devname_nmos_body, gridname = pg, refinstname = in3.name, shape=np.array([m, 1]))
    in5 = laygen.relplace(name = "I"+objectname_pfix + 'N5', templatename = devname_nmos_boundary, gridname = pg, refinstname = in4.name)

    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix + 'P1', templatename = devname_pmos_body, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix + 'P2', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')
    ip3 = laygen.relplace(name = "I"+objectname_pfix + 'P3', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip2.name, transform='MX')
    ip4 = laygen.relplace(name = "I"+objectname_pfix + 'P4', templatename = devname_pmos_body, gridname = pg, refinstname = ip3.name, transform='MX', shape=np.array([m, 1]))
    ip5 = laygen.relplace(name = "I"+objectname_pfix + 'P5', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip4.name, transform='MX')

    # route
    # b0
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refpinname1='G0', refinstindex1=np.array([i, 0]),
                     )
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    if m == 1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]),
                     endstyle0="extend", endstyle1="extend")
        rb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                           refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0',
                           endstyle0="extend", endstyle1="extend")
        laygen.via(None, np.array([-1, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
        rb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                           refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0',
                           endstyle0="extend", endstyle1="extend")
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    # a0
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in4.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip4.name, refpinname1='G0', refinstindex1=np.array([i, 0]),
                     )
        laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    if m == 1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=ip4.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]),
                     endstyle0="extend", endstyle1="extend")
        ra0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                           refinstname0=ip4.name, refpinname0='G0', refinstname1=ip4.name, refpinname1='G0',
                           endstyle0="extend", endstyle1="extend")
        laygen.via(None, np.array([-1, 0]), refinstname=ip4.name, refpinname='G0', gridname=rg_m2m3)
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=ip4.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
        ra0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                           refinstname0=ip4.name, refpinname0='G0', refinstname1=ip4.name, refpinname1='G0',
                           endstyle0="extend", endstyle1="extend")
        laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='G0', gridname=rg_m2m3)

    # internal connection between mos
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0',
                 refinstname1=in4.name, refpinname1='S1', refinstindex1=np.array([m - 1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='D0',
                 refinstname1=ip4.name, refpinname1='D0', refinstindex1=np.array([m - 1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=in4.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip4.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 1]), refinstname=in4.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    # output
    if m==1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m2m3,
                     refinstname0=in4.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=in4.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=in4.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=in4.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                       refinstname0=in4.name, refpinname0='D0', refinstindex0=np.array([m - 1, 0]),
                       refinstname1=ip4.name, refpinname1='D0', refinstindex1=np.array([m - 1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in4.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #laygen.via(None, np.array([0, 0]), refinstname=in4.name, refpinname='S1', refinstindex=np.array([m - 1, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in4.name, refpinname='D0', gridname=rg_m2m3, refinstindex=np.array([m - 1, 0]))
    laygen.via(None, np.array([0, 1]), refinstname=ip4.name, refpinname='D0', gridname=rg_m2m3, refinstindex=np.array([m - 1, 0]))
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip4.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip4.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip4.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=ip4.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip4.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=ip4.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
    # power and groud rail
    xy = laygen.get_template_xy(name = in5.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip5.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in5.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['A', 'B', 'O'], rect_list=[ra0, rb0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_nand_1x(laygen, objectname_pfix,
                     placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                     devname_nmos_boundary, devname_nmos_body_2stack,
                     devname_pmos_boundary, devname_pmos_body_left, devname_pmos_body_right,
                     pin_o_yindex=0, origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix + 'N1', templatename = devname_nmos_body_2stack, gridname = pg, refinstname = in0.name)
    #in2 = laygen.relplace(name = "I"+objectname_pfix + 'N2', templatename = devname_nmos_body_right, gridname = pg, refinstname = in1.name)
    in2 = laygen.relplace(name = "I"+objectname_pfix + 'N3', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix + 'P1', templatename = devname_pmos_body_left, gridname = pg, refinstname = ip0.name, transform='MX')
    ip2 = laygen.relplace(name = "I"+objectname_pfix + 'P2', templatename = devname_pmos_body_right, gridname = pg, refinstname = ip1.name, transform='MX')
    ip3 = laygen.relplace(name = "I"+objectname_pfix + 'P3', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip2.name, transform='MX')

    # route
    # B
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([2, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0',
                 refinstname1=in1.name, refpinname1='G0', endstyle0="extend", endstyle1="extend")
    rb0 = laygen.route("R"+objectname_pfix+"A0", laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    # A
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G1', refinstname1=ip2.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=ip2.name, refpinname='G0', gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip2.name, refpinname0='G0',
                 refinstname1=ip2.name, refpinname1='G0', endstyle0="extend", endstyle1="extend")
    ra0 = laygen.route("R"+objectname_pfix+"B0", laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G1', refinstname1=in1.name, refpinname1='G1')
    laygen.via(None, np.array([-1, 0]), refinstname=ip2.name, refpinname='G0', gridname=rg_m2m3)

    # output
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, pin_o_yindex]), xy1=np.array([0, pin_o_yindex]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0', refinstname1=in1.name, refpinname1='D0')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, pin_o_yindex]), xy1=np.array([0, pin_o_yindex]), gridname0=rg_m2m3,
                 refinstname0=ip2.name, refpinname0='D0', refinstname1=ip2.name, refpinname1='D0')
    ro0 = laygen.route("R"+objectname_pfix+"O0", laygen.layers['metal'][3], xy0=np.array([0, pin_o_yindex]),
                       xy1=np.array([0, pin_o_yindex]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstname1=ip2.name, refpinname1='D0')
    laygen.via(None, np.array([0, pin_o_yindex]), refinstname=in1.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, pin_o_yindex]), refinstname=ip2.name, refpinname='S0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, pin_o_yindex]), refinstname=in1.name, refpinname='D0', gridname=rg_m2m3)
    laygen.via(None, np.array([0, pin_o_yindex]), refinstname=ip2.name, refpinname='D0', gridname=rg_m2m3)
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstname1=in1.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=ip1.name, refinstname1=ip1.name)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2)
    xy_d0 = laygen.get_template_pin_xy(ip2.cellname, 'D0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_d0*np.array([1, 0]), xy1=xy_d0, gridname0=rg_m1m2,
                 refinstname0=ip2.name, refinstname1=ip2.name)
    laygen.via(None, xy_d0 * np.array([1, 0]), refinstname=ip2.name, gridname=rg_m1m2)

    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd = laygen.route("R" + objectname_pfix + "VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=ip0.name, refinstname1=ip3.name)
    rvss = laygen.route("R" + objectname_pfix + "VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=in0.name, refinstname1=in2.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['A', 'B', 'O'], rect_list=[ra0, rb0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_tinv(laygen, objectname_pfix,
                     placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                     devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_body,
                     m=1, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m=max(1, int(m/2)) #using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix + 'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I" + objectname_pfix + 'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    in3 = laygen.relplace(name = "I" + objectname_pfix + 'N3', templatename = devname_nmos_boundary, gridname = pg, refinstname = in2.name)
    in4 = laygen.relplace(name = "I"+objectname_pfix + 'N4', templatename = devname_nmos_body, gridname = pg, refinstname = in3.name, shape=np.array([m, 1]))
    in5 = laygen.relplace(name = "I"+objectname_pfix + 'N5', templatename = devname_nmos_boundary, gridname = pg, refinstname = in4.name)

    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix + 'P1', templatename = devname_pmos_body, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix + 'P2', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')
    ip3 = laygen.relplace(name = "I"+objectname_pfix + 'P3', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip2.name, transform='MX')
    ip4 = laygen.relplace(name = "I"+objectname_pfix + 'P4', templatename = devname_pmos_body, gridname = pg, refinstname = ip3.name, transform='MX', shape=np.array([m, 1]))
    ip5 = laygen.relplace(name = "I"+objectname_pfix + 'P5', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip4.name, transform='MX')

    # route
    # in0
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refpinname1='G0', refinstindex1=np.array([i, 0]),
                     )
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    if m == 1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([1, 1]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]),
                     endstyle0="extend", endstyle1="extend")
        ri0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                           refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0',
                           endstyle0="extend", endstyle1="extend")
        laygen.via(None, np.array([-1, 1]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
        ri0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                           refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0',
                           endstyle0="extend", endstyle1="extend")
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    # en0
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in4.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    if m==1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=in4.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]),
                     endstyle0="extend", endstyle1="extend")
        ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([1, 0]), xy1=np.array([1, 2]), gridname0=rg_m2m3,
                           refinstname0=in4.name, refpinname0='G0', refinstindex0=np.array([m - 1, 0]),
                           refinstname1=in4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
        laygen.via(None, np.array([1, 0]), refinstname=in4.name, refpinname='G0',
                   refinstindex=np.array([m - 1, 0]), gridname=rg_m2m3)
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=in4.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
        ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([1, 0]), xy1=np.array([1, 2]), gridname0=rg_m2m3,
                           refinstname0=in4.name, refpinname0='G0', refinstindex0=np.array([m - 1, 0]),
                           refinstname1=in4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
        laygen.via(None, np.array([1, 0]), refinstname=in4.name, refpinname='G0',
                   refinstindex=np.array([m - 1, 0]), gridname=rg_m2m3)
    # enb0
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    if m==1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=ip4.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]),
                     endstyle0="extend", endstyle1="extend")
        renb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                           refinstname0=ip4.name, refpinname0='G0', refinstindex0=np.array([m - 1, 0]),
                           refinstname1=ip4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
        laygen.via(None, np.array([-1, 0]), refinstname=ip4.name, refpinname='G0',
                   refinstindex=np.array([m - 1, 0]), gridname=rg_m2m3)
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=ip4.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
        renb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                           refinstname0=ip4.name, refpinname0='G0', refinstindex0=np.array([m - 1, 0]),
                           refinstname1=ip4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
        laygen.via(None, np.array([-1, 0]), refinstname=ip4.name, refpinname='G0',
                   refinstindex=np.array([m - 1, 0]), gridname=rg_m2m3)
    # internal connection between stacked mos
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0',
                 refinstname1=in4.name, refpinname1='S1', refinstindex1=np.array([m - 1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='D0',
                 refinstname1=ip4.name, refpinname1='S1', refinstindex1=np.array([m - 1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=in4.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip4.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    #laygen.via(None, np.array([0, 1]), refinstname=ip1.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 1]), refinstname=in4.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 1]), refinstname=ip4.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    # mux output
    if m==1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m2m3,
                     refinstname0=in4.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=in4.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m2m3,
                     refinstname0=ip4.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip4.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=in4.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=in4.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=ip4.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip4.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in4.name, refpinname0='D0', refinstindex0=np.array([m - 1, 0]),
                       refinstname1=ip4.name, refpinname1='D0', refinstindex1=np.array([m - 1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in4.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in4.name, refpinname='D0', gridname=rg_m2m3, refinstindex=np.array([m - 1, 0]))
    laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='D0', gridname=rg_m2m3, refinstindex=np.array([m - 1, 0]))

    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
    # power and groud rail
    xy = laygen.get_template_xy(name = in5.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd = laygen.route("R" + objectname_pfix + "VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=ip0.name, refinstname1=ip5.name)
    rvss = laygen.route("R" + objectname_pfix + "VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=in0.name, refinstname1=in5.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['I', 'EN', 'ENB', 'O'], rect_list=[ri0, ren0, renb0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_tinv_1x(laygen, objectname_pfix,
                     placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                     devname_nmos_boundary, devname_nmos_body_2stack, devname_nmos_space,
                     devname_pmos_boundary, devname_pmos_body_2stack, devname_pmos_space,
                     pin_i_abut="nmos", origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    # placement
    in0 = laygen.place("I"+objectname_pfix+'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body_2stack, gridname = pg, refinstname = in0.name)
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    in3 = laygen.relplace(name = "I"+objectname_pfix + 'N3', templatename = devname_nmos_space, gridname = pg, refinstname = in2.name)
    in4 = laygen.relplace(name = "I" + objectname_pfix + 'N4', templatename = devname_nmos_space, gridname = pg, refinstname = in3.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P1', templatename = devname_pmos_body_2stack, gridname = pg, refinstname = ip0.name, transform='MX')
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P2', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')
    ip3 = laygen.relplace(name = "I"+objectname_pfix + 'P3', templatename = devname_pmos_space, gridname = pg, refinstname = ip2.name, transform='MX')
    ip4 = laygen.relplace(name = "I" + objectname_pfix + 'P4', templatename = devname_pmos_space, gridname = pg, refinstname = ip3.name, transform='MX')


    # route
    # input
    if pin_i_abut == "nmos":
        refinstname_in = in1.name
        refinstname_en0 = in1.name
        refinstname_en1 = ip1.name
    else:
        refinstname_in = ip1.name
        refinstname_en0 = ip1.name
        refinstname_en1 = in1.name

    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([2, 1]), gridname0=rg_m1m2,
                 refinstname0=refinstname_in, refpinname0='G0', refinstname1=refinstname_in, refpinname1='G0')
    ri0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                       refinstname0=refinstname_in, refpinname0='G0', refinstname1=refinstname_in, refpinname1='G0',
                       endstyle0="extend", endstyle1="extend")
    laygen.via(None, np.array([0, 1]), refinstname=refinstname_in, refpinname='G0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 1]), refinstname=refinstname_in, refpinname='G0', gridname=rg_m2m3)
    # en
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=refinstname_en0, refpinname0='G1', refinstname1=refinstname_en0, refpinname1='G1')
    ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([1, 0]), xy1=np.array([1, 2]), gridname0=rg_m2m3,
                         refinstname0=refinstname_en0, refpinname0='G1', refinstname1=refinstname_en0, refpinname1='G1')
    laygen.via(None, np.array([0, 0]), refinstname=refinstname_en0, refpinname='G1', gridname=rg_m1m2)
    laygen.via(None, np.array([1, 0]), refinstname=in1.name, refpinname='G1', gridname=rg_m2m3)
    # enb
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0+1, 0]), gridname0=rg_m1m2,
                 refinstname0=refinstname_en1, refpinname0='G1', refinstname1=refinstname_en1, refpinname1='G1')
    renb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                         refinstname0=refinstname_en1, refpinname0='G1', refinstname1=refinstname_en1, refpinname1='G1')
    laygen.via(None, np.array([0, 0]), refinstname=refinstname_en1, refpinname='G1', gridname=rg_m1m2)
    laygen.via(None, np.array([-1, 0]), refinstname=ip1.name, refpinname='G1', gridname=rg_m2m3)
    # output
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0', refinstname1=in1.name, refpinname1='D0')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='D0', refinstname1=ip1.name, refpinname1='D0')
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstname1=ip1.name, refpinname1='D0')
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='D0', gridname=rg_m2m3)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='D0', gridname=rg_m2m3)
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='S0', refinstname1=in1.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='S0', refinstname1=ip1.name)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2)
    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd = laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=ip0.name, refinstname1=ip4.name)
    rvss = laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=in0.name, refinstname1=in4.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['I', 'EN', 'ENB', 'O'], rect_list=[ri0, ren0, renb0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_tinv_small_1x(laygen, objectname_pfix,
                           placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                           devname_nmos_boundary, devname_nmos_body_2stack, devname_nmos_space,
                           devname_pmos_boundary, devname_pmos_body_2stack, devname_pmos_space,
                           pin_i_abut="nmos", origin=np.array([0,0]), create_pin=False):
    """small tristate inverter for latches and FFs"""
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    # placement
    in0 = laygen.place("I"+objectname_pfix+'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body_2stack, gridname = pg, refinstname = in0.name)
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    in3 = laygen.relplace(name = "I"+objectname_pfix + 'N3', templatename = devname_nmos_space, gridname = pg, refinstname = in2.name)
    in4 = laygen.relplace(name = "I" + objectname_pfix + 'N4', templatename = devname_nmos_space, gridname = pg, refinstname = in3.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P1', templatename = devname_pmos_body_2stack, gridname = pg, refinstname = ip0.name, transform='MX')
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P2', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')
    ip3 = laygen.relplace(name = "I"+objectname_pfix + 'P3', templatename = devname_pmos_space, gridname = pg, refinstname = ip2.name, transform='MX')
    ip4 = laygen.relplace(name = "I" + objectname_pfix + 'P4', templatename = devname_pmos_space, gridname = pg, refinstname = ip3.name, transform='MX')


    # route
    # input
    if pin_i_abut == "nmos":
        refinstname_in = in1.name
        refinstname_en0 = in1.name
        refinstname_en1 = ip1.name
    else:
        refinstname_in = ip1.name
        refinstname_en0 = ip1.name
        refinstname_en1 = in1.name

    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([2, 1]), gridname0=rg_m1m2,
                 refinstname0=refinstname_in, refpinname0='G0', refinstname1=refinstname_in, refpinname1='G0')
    ri0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                       refinstname0=refinstname_in, refpinname0='G0', refinstname1=refinstname_in, refpinname1='G0',
                       endstyle0="extend", endstyle1="extend")
    laygen.via(None, np.array([0, 1]), refinstname=refinstname_in, refpinname='G0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 1]), refinstname=refinstname_in, refpinname='G0', gridname=rg_m2m3)
    # en
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=refinstname_en0, refpinname0='G1', refinstname1=refinstname_en0, refpinname1='G1')
    ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([1, 0]), xy1=np.array([1, 2]), gridname0=rg_m2m3,
                         refinstname0=refinstname_en0, refpinname0='G1', refinstname1=refinstname_en0, refpinname1='G1')
    laygen.via(None, np.array([0, 0]), refinstname=refinstname_en0, refpinname='G1', gridname=rg_m1m2)
    laygen.via(None, np.array([1, 0]), refinstname=in1.name, refpinname='G1', gridname=rg_m2m3)
    # enb
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0+1, 0]), gridname0=rg_m1m2,
                 refinstname0=refinstname_en1, refpinname0='G1', refinstname1=refinstname_en1, refpinname1='G1')
    renb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                         refinstname0=refinstname_en1, refpinname0='G1', refinstname1=refinstname_en1, refpinname1='G1')
    laygen.via(None, np.array([0, 0]), refinstname=refinstname_en1, refpinname='G1', gridname=rg_m1m2)
    laygen.via(None, np.array([-1, 0]), refinstname=ip1.name, refpinname='G1', gridname=rg_m2m3)
    # output
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0', refinstname1=in1.name, refpinname1='D0')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='D0', refinstname1=ip1.name, refpinname1='D0')
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstname1=ip1.name, refpinname1='D0')
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='D0', gridname=rg_m2m3)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='D0', gridname=rg_m2m3)
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='S0', refinstname1=in1.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='S0', refinstname1=ip1.name)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2)
    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd = laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=ip0.name, refinstname1=ip4.name)
    rvss = laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=in0.name, refinstname1=in4.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['I', 'EN', 'ENB', 'O'], rect_list=[ri0, ren0, renb0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_mux2to1_1x(laygen, objectname_pfix,
                        placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                        devname_nmos_boundary, devname_nmos_body_2stack, #devname_nmos_body_left, devname_nmos_body_right,
                        devname_pmos_boundary, devname_pmos_body_2stack, #devname_pmos_body_left, devname_pmos_body_right,
                        origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_boundary, pg, xy=origin)
    #in1 = laygen.relplace(name = "I"+objectname_pfix + 'N1', templatename = devname_nmos_body_left, gridname = pg, refinstname = in0.name)
    #in2 = laygen.relplace(name = "I"+objectname_pfix + 'N2', templatename = devname_nmos_body_right, gridname = pg, refinstname = in1.name)
    in1 = laygen.relplace(name = "I"+objectname_pfix + 'N1', templatename = devname_nmos_body_2stack, gridname = pg, refinstname = in0.name)
    in3 = laygen.relplace(name = "I"+objectname_pfix + 'N3', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    in4 = laygen.relplace(name = "I"+objectname_pfix + 'N4', templatename = devname_nmos_boundary, gridname = pg, refinstname = in3.name, transform='MY')
    #in5 = laygen.relplace(name = "I"+objectname_pfix + 'N5', templatename = devname_nmos_body_right, gridname = pg, refinstname = in4.name, transform='MY')
    #in6 = laygen.relplace(name = "I"+objectname_pfix + 'N6', templatename = devname_nmos_body_left, gridname = pg, refinstname = in5.name, transform='MY')
    in6 = laygen.relplace(name = "I"+objectname_pfix + 'N6', templatename = devname_nmos_body_2stack, gridname = pg, refinstname = in4.name, transform='MY')
    in7 = laygen.relplace(name = "I"+objectname_pfix + 'N7', templatename = devname_nmos_boundary, gridname = pg, refinstname = in6.name, transform='MY')
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    #ip1 = laygen.relplace(name = "I"+objectname_pfix + 'P1', templatename = devname_pmos_body_left, gridname = pg, refinstname = ip0.name, transform='MX')
    #ip2 = laygen.relplace(name = "I"+objectname_pfix + 'P2', templatename = devname_pmos_body_right, gridname = pg, refinstname = ip1.name, transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix + 'P1', templatename = devname_pmos_body_2stack, gridname = pg, refinstname = ip0.name, transform='MX')
    ip3 = laygen.relplace(name = "I"+objectname_pfix + 'P3', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')
    ip4 = laygen.relplace(name = "I"+objectname_pfix + 'P4', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip3.name, transform='R180')
    #ip5 = laygen.relplace(name = "I"+objectname_pfix + 'P5', templatename = devname_pmos_body_right, gridname = pg, refinstname = ip4.name, transform='R180')
    #ip6 = laygen.relplace(name = "I"+objectname_pfix + 'P6', templatename = devname_pmos_body_left, gridname = pg, refinstname = ip5.name, transform='R180')
    ip6 = laygen.relplace(name = "I"+objectname_pfix + 'P6', templatename = devname_pmos_body_2stack, gridname = pg, refinstname = ip4.name, transform='R180')
    ip7 = laygen.relplace(name = "I"+objectname_pfix + 'P7', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip6.name, transform='R180')
    generate_inv_1x(laygen, objectname_pfix=objectname_pfix+'INV0',
                    placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                    routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                    devname_nmos_boundary='nmos4_fast_boundary',
                    devname_nmos_body='nmos4_fast_center_nf1_left',
                    devname_nmos_space='nmos4_fast_space',
                    devname_pmos_boundary='pmos4_fast_boundary',
                    devname_pmos_body='pmos4_fast_center_nf1_left',
                    devname_pmos_space='pmos4_fast_space',
                    pin_i_abut='pmos', origin=laygen.get_inst_xy(name = in7.name, gridname = pg), pin_o_y=1, create_pin=False)
    # in0
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([2, 1]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
    ri0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0',
                       endstyle0="extend", endstyle1="extend")
    laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='G0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    # in1
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in6.name, refpinname0='G0', refinstname1=ip6.name, refpinname1='G0')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([2, 1]), gridname0=rg_m1m2,
                 refinstname0=in6.name, refpinname0='G0', refinstname1=in6.name, refpinname1='G0')
    ri1 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                       refinstname0=in6.name, refpinname0='G0', refinstname1=in6.name, refpinname1='G0',
                       endstyle0="extend", endstyle1="extend")
    laygen.via(None, np.array([0, 1]), refinstname=in6.name, refpinname='G0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 1]), refinstname=in6.name, refpinname='G0', gridname=rg_m2m3)
    # en0
    #laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
    #             refinstname0=in2.name, refpinname0='G0', refinstname1=in2.name, refpinname1='G0')
    #ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0-1]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
    #                     refinstname0=in2.name, refpinname0='G0', refinstname1=in2.name, refpinname1='G0',
    #                   endstyle0="extend", endstyle1="extend")
    #laygen.via(None, np.array([0, 0]), refinstname=in2.name, refpinname='G0', gridname=rg_m1m2)
    #laygen.via(None, np.array([-1, 0]), refinstname=in2.name, refpinname='G0', gridname=rg_m2m3)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G1', refinstname1=in1.name, refpinname1='G1')
    ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0-1]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                         refinstname0=in1.name, refpinname0='G1', refinstname1=in1.name, refpinname1='G1',
                       endstyle0="extend", endstyle1="extend")
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G1', gridname=rg_m1m2)
    laygen.via(None, np.array([-1, 0]), refinstname=in1.name, refpinname='G1', gridname=rg_m2m3)
    # en1
    #laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
    #             refinstname0=in5.name, refpinname0='G0', refinstname1=in5.name, refpinname1='G0')
    #ren1 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2+1]), gridname0=rg_m2m3,
    #                    refinstname0=in5.name, refpinname0='G0', refinstname1=in5.name, refpinname1='G0',
    #                   endstyle0="extend", endstyle1="extend")
    #laygen.via(None, np.array([0, 0]), refinstname=in5.name, refpinname='G0', gridname=rg_m1m2)
    #laygen.via(None, np.array([-1, 0]), refinstname=in5.name, refpinname='G0', gridname=rg_m2m3)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in6.name, refpinname0='G1', refinstname1=in6.name, refpinname1='G1')
    ren1 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2+1]), gridname0=rg_m2m3,
                        refinstname0=in6.name, refpinname0='G1', refinstname1=in6.name, refpinname1='G1',
                       endstyle0="extend", endstyle1="extend")
    laygen.via(None, np.array([0, 0]), refinstname=in6.name, refpinname='G1', gridname=rg_m1m2)
    laygen.via(None, np.array([-1, 0]), refinstname=in6.name, refpinname='G1', gridname=rg_m2m3)
    # enb0
    #laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
    #             refinstname0=ip2.name, refpinname0='G0', refinstname1=ip2.name, refpinname1='G0')
    #renb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0-1]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
    #                     refinstname0=ip2.name, refpinname0='G0', refinstname1=ip2.name, refpinname1='G0',
    #                   endstyle0="extend", endstyle1="extend")
    #laygen.via(None, np.array([0, 0]), refinstname=ip2.name, refpinname='G0', gridname=rg_m1m2)
    #laygen.via(None, np.array([0, 0]), refinstname=ip2.name, refpinname='G0', gridname=rg_m2m3)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='G1', refinstname1=ip1.name, refpinname1='G1')
    renb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0-1]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                         refinstname0=ip1.name, refpinname0='G1', refinstname1=ip1.name, refpinname1='G1',
                       endstyle0="extend", endstyle1="extend")
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='G1', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='G1', gridname=rg_m2m3)
    # enb1
    #laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
    #             refinstname0=ip5.name, refpinname0='G0', refinstname1=ip5.name, refpinname1='G0')
    #renb1 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2+1]), gridname0=rg_m2m3,
    #                     refinstname0=ip5.name, refpinname0='G0', refinstname1=ip5.name, refpinname1='G0',
    #                   endstyle0="extend", endstyle1="extend")
    #laygen.via(None, np.array([0, 0]), refinstname=ip5.name, refpinname='G0', gridname=rg_m1m2)
    #laygen.via(None, np.array([0, 0]), refinstname=ip5.name, refpinname='G0', gridname=rg_m2m3)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip6.name, refpinname0='G1', refinstname1=ip6.name, refpinname1='G1')
    renb1 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2+1]), gridname0=rg_m2m3,
                         refinstname0=ip6.name, refpinname0='G1', refinstname1=ip6.name, refpinname1='G1',
                       endstyle0="extend", endstyle1="extend")
    laygen.via(None, np.array([0, 0]), refinstname=ip6.name, refpinname='G1', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ip6.name, refpinname='G1', gridname=rg_m2m3)
    # en/enb cross couple
    #laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0-1]), xy1=np.array([0, -1]), gridname0=rg_m2m3,
    #             refinstname0=in2.name, refpinname0='G0', refinstname1=in5.name, refpinname1='G0')
    #laygen.via(None, np.array([-1, -1]), refinstname=in2.name, refpinname='G0', gridname=rg_m2m3)
    #laygen.via(None, np.array([0, -1]), refinstname=in5.name, refpinname='G0', gridname=rg_m2m3)
    #laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0-1]), xy1=np.array([-1, -1]), gridname0=rg_m2m3,
    #             refinstname0=ip2.name, refpinname0='G0', refinstname1=ip5.name, refpinname1='G0')
    #laygen.via(None, np.array([0, -1]), refinstname=ip2.name, refpinname='G0', gridname=rg_m2m3)
    #laygen.via(None, np.array([-1, -1]), refinstname=ip5.name, refpinname='G0', gridname=rg_m2m3)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0-1]), xy1=np.array([0, -1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='G1', refinstname1=in6.name, refpinname1='G1')
    laygen.via(None, np.array([-1, -1]), refinstname=in1.name, refpinname='G1', gridname=rg_m2m3)
    laygen.via(None, np.array([0, -1]), refinstname=in6.name, refpinname='G1', gridname=rg_m2m3)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0-1]), xy1=np.array([-1, -1]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='G1', refinstname1=ip6.name, refpinname1='G1')
    laygen.via(None, np.array([0, -1]), refinstname=ip1.name, refpinname='G1', gridname=rg_m2m3)
    laygen.via(None, np.array([-1, -1]), refinstname=ip6.name, refpinname='G1', gridname=rg_m2m3)
    # output
    #laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
    #             refinstname0=in2.name, refpinname0='D0', refinstname1=in5.name, refpinname1='D0')
    #laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
    #             refinstname0=ip2.name, refpinname0='D0', refinstname1=ip5.name, refpinname1='D0')
    #ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([1, 0]), xy1=np.array([1, 0]), gridname0=rg_m2m3,
    #                   refinstname0=in2.name, refpinname0='D0', refinstname1=ip2.name, refpinname1='D0')
    #laygen.via(None, np.array([0, 0]), refinstname=in2.name, refpinname='D0', gridname=rg_m1m2)
    #laygen.via(None, np.array([0, 0]), refinstname=ip2.name, refpinname='D0', gridname=rg_m1m2)
    #laygen.via(None, np.array([0, 0]), refinstname=in5.name, refpinname='D0', gridname=rg_m1m2)
    #laygen.via(None, np.array([0, 0]), refinstname=ip5.name, refpinname='D0', gridname=rg_m1m2)
    #laygen.via(None, np.array([1, 0]), refinstname=in2.name, refpinname='D0', gridname=rg_m2m3)
    #laygen.via(None, np.array([1, 0]), refinstname=ip2.name, refpinname='D0', gridname=rg_m2m3)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0', refinstname1=in6.name, refpinname1='D0')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='D0', refinstname1=ip6.name, refpinname1='D0')
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([1, 0]), xy1=np.array([1, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstname1=ip6.name, refpinname1='D0')
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in6.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ip6.name, refpinname='D0', gridname=rg_m1m2)
    laygen.via(None, np.array([1, 0]), refinstname=in6.name, refpinname='D0', gridname=rg_m2m3)
    laygen.via(None, np.array([1, 0]), refinstname=ip6.name, refpinname='D0', gridname=rg_m2m3)
    #muxoutput to inverter input
    #laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
    #             refinstname0=in2.name, refpinname0='D0', refinstname1="I"+objectname_pfix+"INV0N1", refpinname1='G0',
    #             direction="x")
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0', refinstname1="I" + objectname_pfix + "INV0N1",
                 refpinname1='G0', direction="x")
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, -2]), gridname0=rg_m2m3,
                 refinstname0="I" + objectname_pfix + "INV0N1", refpinname0='G0',
                 refinstname1="I" + objectname_pfix + "INV0N1", refpinname1='G0')
    laygen.via(None, np.array([0, -2]), refinstname="I" + objectname_pfix + "INV0N1", refpinname='G0', gridname=rg_m2m3)
    #mux output
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                       refinstname0="I" + objectname_pfix + "INV0N1", refpinname0='D0',
                       refinstname1="I" + objectname_pfix + "INV0P1", refpinname1='D0')
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='S0', refinstname1=in1.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='S0', refinstname1=ip1.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=in6.name, refpinname0='S0', refinstname1=in6.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=xy_s0 * np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=ip6.name, refpinname0='S0', refinstname1=ip6.name)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in6.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip6.name, gridname=rg_m1m2)
    # power and groud rail
    rvdd = laygen.route("R" + objectname_pfix +"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]),
                        xy1=np.array([laygen.get_template_xy(name = devname_pmos_boundary, gridname = rg_m1m2)[0], 0]), gridname0=rg_m1m2,
                        refinstname0=ip0.name, refinstname1="I" + objectname_pfix + "INV0P3")
    rvss = laygen.route("R" + objectname_pfix +"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]),
                        xy1=np.array([laygen.get_template_xy(name = devname_pmos_boundary, gridname = rg_m1m2)[0], 0]), gridname0=rg_m1m2,
                        refinstname0=in0.name, refinstname1="I" + objectname_pfix + "INV0N3")
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['I0', 'I1', 'EN0', 'EN1', 'O'], rect_list=[ri0, ri1, ren0, renb0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_mux2to1(laygen, objectname_pfix,
                     placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,
                     routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                     devname_nmos_boundary, devname_nmos_body, devname_nmos_space,
                     devname_pmos_boundary, devname_pmos_body, devname_pmos_space,
                     m=2, origin=np.array([0, 0]), create_pin=False):
    """generate 2:1 mux"""
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m=max(1, int(m/2)) #using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix + 'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in1a = laygen.relplace(name = "I"+objectname_pfix + 'N1A', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    in1b = laygen.relplace(name = "I"+objectname_pfix + 'N1B', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1a.name)
    in2 = laygen.relplace(name = "I"+objectname_pfix + 'N2', templatename = devname_nmos_body, gridname = pg, refinstname = in1b.name, shape=np.array([m, 1]))
    in3 = laygen.relplace(name = "I"+objectname_pfix + 'N3', templatename = devname_nmos_boundary, gridname = pg, refinstname = in2.name)
    in_rte = laygen.relplace(name = "I"+objectname_pfix + 'NRTE', templatename = devname_nmos_space, gridname = pg, refinstname = in3.name, shape=np.array([4, 1]))
    in4 = laygen.relplace(name = "I"+objectname_pfix + 'N4', templatename = devname_nmos_boundary, gridname = pg, refinstname = in_rte.name, transform='MY')
    in5 = laygen.relplace(name = "I"+objectname_pfix + 'N5', templatename = devname_nmos_body, gridname = pg, refinstname = in4.name, transform='MY', shape=np.array([m, 1]))
    in5a = laygen.relplace(name = "I"+objectname_pfix + 'N5A', templatename = devname_nmos_boundary, gridname = pg, refinstname = in5.name, transform='MY')
    in5b = laygen.relplace(name = "I"+objectname_pfix + 'N5B', templatename = devname_nmos_boundary, gridname = pg, refinstname = in5a.name, transform='MY')
    in6 = laygen.relplace(name = "I"+objectname_pfix + 'N6', templatename = devname_nmos_body, gridname = pg, refinstname = in5b.name, transform='MY', shape=np.array([m, 1]))
    in7 = laygen.relplace(name = "I"+objectname_pfix + 'N7', templatename = devname_nmos_boundary, gridname = pg, refinstname = in6.name, transform='MY')
    in8 = laygen.relplace(name = "I"+objectname_pfix + 'N8', templatename = devname_nmos_boundary, gridname = pg, refinstname = in7.name)
    in9 = laygen.relplace(name = "I"+objectname_pfix + 'N9', templatename = devname_nmos_body, gridname = pg, refinstname = in8.name, shape=np.array([m, 1]))
    in10 = laygen.relplace(name = "I"+objectname_pfix + 'N10', templatename = devname_nmos_boundary, gridname = pg, refinstname = in9.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix + 'P1', templatename = devname_pmos_body, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m, 1]))
    ip1a = laygen.relplace(name = "I"+objectname_pfix + 'P1A', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')
    ip1b = laygen.relplace(name = "I"+objectname_pfix + 'P1B', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1a.name, transform='MX')
    ip2 = laygen.relplace(name = "I"+objectname_pfix + 'P2', templatename = devname_pmos_body, gridname = pg, refinstname = ip1b.name, transform='MX', shape=np.array([m, 1]))
    ip3 = laygen.relplace(name = "I"+objectname_pfix + 'P3', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip2.name, transform='MX')
    ip_rte = laygen.relplace(name = "I"+objectname_pfix + 'PRTE', templatename = devname_pmos_space, gridname = pg, refinstname = ip3.name, shape=np.array([4, 1]), transform='MX')
    ip4 = laygen.relplace(name = "I"+objectname_pfix + 'P4', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip_rte.name, transform='R180')
    ip5 = laygen.relplace(name = "I"+objectname_pfix + 'P5', templatename = devname_pmos_body, gridname = pg, refinstname = ip4.name, transform='R180', shape=np.array([m, 1]))
    ip5a = laygen.relplace(name = "I"+objectname_pfix + 'P5A', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip5.name, transform='R180')
    ip5b = laygen.relplace(name = "I"+objectname_pfix + 'P5B', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip5a.name, transform='R180')
    ip6 = laygen.relplace(name = "I"+objectname_pfix + 'P6', templatename = devname_pmos_body, gridname = pg, refinstname = ip5b.name, transform='R180', shape=np.array([m, 1]))
    ip7 = laygen.relplace(name = "I"+objectname_pfix + 'P7', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip6.name, transform='R180')
    ip8 = laygen.relplace(name = "I"+objectname_pfix + 'P8', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip7.name, transform='MX')
    ip9 = laygen.relplace(name = "I"+objectname_pfix + 'P9', templatename = devname_pmos_body, gridname = pg, refinstname = ip8.name, transform='MX', shape=np.array([m, 1]))
    ip10 = laygen.relplace(name = "I"+objectname_pfix + 'P10', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip9.name, transform='MX')

    # in0
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refpinname1='G0', refinstindex1=np.array([i, 0]),
                     )
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    if m==1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([1, 1]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
        ri0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                           refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
        laygen.via(None, np.array([-1, 1]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
        ri0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                           refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    # in1
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in6.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip6.name, refpinname1='G0', refinstindex1=np.array([i, 0]),
                     )
        laygen.via(None, np.array([0, 1]), refinstname=in6.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    if m==1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([1, 1]), gridname0=rg_m1m2,
                     refinstname0=in6.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in6.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
        ri1 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                           refinstname0=in6.name, refpinname0='G0', refinstname1=in6.name, refpinname1='G0')
        laygen.via(None, np.array([-1, 1]), refinstname=in6.name, refpinname='G0', gridname=rg_m2m3)
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                     refinstname0=in6.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in6.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
        ri1 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                           refinstname0=in6.name, refpinname0='G0', refinstname1=in6.name, refpinname1='G0')
        laygen.via(None, np.array([0, 1]), refinstname=in6.name, refpinname='G0', gridname=rg_m2m3)
    # en0
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in2.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    ren0_m2 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([4, 0]), gridname0=rg_m1m2,
                 refinstname0=in2.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=in2.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
    # en1
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in5.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    ren1_m2 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([2, 0]), gridname0=rg_m1m2,
                 refinstname0=in5.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=in5.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
    # enb0
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=ip2.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    renb0_m2 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([2, 0]), gridname0=rg_m1m2,
                 refinstname0=ip2.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip2.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
    # enb1
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=ip5.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    renb1_m2 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([4, 0]), gridname0=rg_m1m2,
                 refinstname0=ip5.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip5.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
    # internal connection between stacked mos
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0',
                 refinstname1=in2.name, refpinname1='D0', refinstindex1=np.array([m - 1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='D0',
                 refinstname1=ip2.name, refpinname1='D0', refinstindex1=np.array([m - 1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in6.name, refpinname0='D0',
                 refinstname1=in5.name, refpinname1='D0', refinstindex1=np.array([m - 1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=ip6.name, refpinname0='D0',
                 refinstname1=ip5.name, refpinname1='D0', refinstindex1=np.array([m - 1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=in2.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip2.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=in5.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip5.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=in6.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip6.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    # mux output
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=in2.name, refpinname0='S0', refinstname1=in5.name, refpinname1='S0')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=ip2.name, refpinname0='S0', refinstname1=ip5.name, refpinname1='S0')
    rmuxo0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in5.name, refpinname0='S0', refinstindex0=np.array([m - 1, 0]),
                       refinstname1=ip5.name, refpinname1='S0', refinstindex1=np.array([m - 1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in2.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip2.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=in5.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip5.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in2.name, refpinname='S1', gridname=rg_m1m2, refinstindex=np.array([m - 1, 0]))
    laygen.via(None, np.array([0, 0]), refinstname=ip2.name, refpinname='S1', gridname=rg_m1m2, refinstindex=np.array([m - 1, 0]))
    laygen.via(None, np.array([0, 0]), refinstname=in5.name, refpinname='S1', gridname=rg_m1m2, refinstindex=np.array([m - 1, 0]))
    laygen.via(None, np.array([0, 0]), refinstname=ip5.name, refpinname='S1', gridname=rg_m1m2, refinstindex=np.array([m - 1, 0]))
    laygen.via(None, np.array([0, 0]), refinstname=in5.name, refpinname='S0', gridname=rg_m2m3, refinstindex=np.array([m - 1, 0]))
    laygen.via(None, np.array([0, 0]), refinstname=ip5.name, refpinname='S0', gridname=rg_m2m3, refinstindex=np.array([m - 1, 0]))
    # inverter input
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in9.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip9.name, refpinname1='G0', refinstindex1=np.array([i, 0]),
                     )
        laygen.via(None, np.array([0, 0]), refinstname=in9.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    if m==1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=in9.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in9.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
        rinvi0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 4]), gridname0=rg_m2m3,
                           refinstname0=in9.name, refpinname0='G0', refinstname1=in9.name, refpinname1='G0')
        laygen.via(None, np.array([-1, 0]), refinstname=in9.name, refpinname='G0', gridname=rg_m2m3)
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in9.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=in9.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
        rinvi0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 4]), gridname0=rg_m2m3,
                           refinstname0=in9.name, refpinname0='G0', refinstname1=in9.name, refpinname1='G0')
        laygen.via(None, np.array([0, 0]), refinstname=in9.name, refpinname='G0', gridname=rg_m2m3)
    #inverter output
    if m==1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([1, 1]), gridname0=rg_m2m3,
                     refinstname0=in9.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=in9.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([1, 1]), gridname0=rg_m2m3,
                     refinstname0=ip9.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip9.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                     refinstname0=in9.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=in9.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                     refinstname0=ip9.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip9.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in9.name, refpinname='D0', refinstindex=np.array([i, 1]),
                   gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip9.name, refpinname='D0', refinstindex=np.array([i, 1]),
                   gridname=rg_m1m2)
    laygen.via(None, np.array([0, 1]), refinstname=in9.name, refpinname='D0', refinstindex=np.array([m-1, 1]),
               gridname=rg_m2m3)
    laygen.via(None, np.array([0, 1]), refinstname=ip9.name, refpinname='D0', refinstindex=np.array([m-1, 1]),
               gridname=rg_m2m3)

    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                       refinstname0=in9.name, refpinname0='D0', refinstindex0=np.array([m-1, 0]),
                       refinstname1=ip9.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))

    # en/enb cross couple
    ren0_m2m3_xy = laygen.get_rect_xy(name = ren0_m2.name, gridname = rg_m2m3, sort=True)
    ren1_m2m3_xy = laygen.get_rect_xy(name = ren1_m2.name, gridname = rg_m2m3, sort=True)
    renb0_m2m3_xy = laygen.get_rect_xy(name = renb0_m2.name, gridname = rg_m2m3, sort=True)
    renb1_m2m3_xy = laygen.get_rect_xy(name = renb1_m2.name, gridname = rg_m2m3, sort=True)
    [rv0, rh0, renb0] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][2], renb0_m2m3_xy[1], ren1_m2m3_xy[0], renb0_m2m3_xy[0][1]+1, rg_m2m3)
    laygen.via(None, xy=np.array(renb0_m2m3_xy[1]), gridname=rg_m2m3)
    laygen.via(None, xy=np.array(ren1_m2m3_xy[0]), gridname=rg_m2m3)
    ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=ren0_m2m3_xy[1], xy1=renb1_m2m3_xy[0], gridname0=rg_m2m3, via0=[[0, 0]], via1=[[0, 0]])

    # muxout to invin
    rmuxo0_m2m3_xy = laygen.get_rect_xy(name = rmuxo0.name, gridname = rg_m2m3, sort=True)
    rinvi0_m2m3_xy = laygen.get_rect_xy(name = rinvi0.name, gridname = rg_m2m3, sort=True)
    laygen.route(None, laygen.layers['metal'][2], xy0=rmuxo0_m2m3_xy[1], xy1=rinvi0_m2m3_xy[1], gridname0=rg_m2m3, via1=[[0, 0]])

    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in6.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in6.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip6.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip6.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in6.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip6.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in9.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in9.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip9.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip9.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in9.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip9.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))

    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=np.array([m - 1, 0]),
                 refinstname1=in1.name, refinstindex1=np.array([m - 1, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=ip1.name, refinstindex0=np.array([m - 1, 0]),
                 refinstname1=ip1.name, refinstindex1=np.array([m - 1, 0]))
    laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,
               refinstindex=np.array([m - 1, 0]))
    laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,
               refinstindex=np.array([m - 1, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=in6.name, refinstindex0=np.array([m - 1, 0]),
                 refinstname1=in6.name, refinstindex1=np.array([m - 1, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=ip6.name, refinstindex0=np.array([m - 1, 0]),
                 refinstname1=ip6.name, refinstindex1=np.array([m - 1, 0]))
    laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in6.name, gridname=rg_m1m2,
               refinstindex=np.array([m - 1, 0]))
    laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=ip6.name, gridname=rg_m1m2,
               refinstindex=np.array([m - 1, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=in9.name, refinstindex0=np.array([m - 1, 0]),
                 refinstname1=in9.name, refinstindex1=np.array([m - 1, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=ip9.name, refinstindex0=np.array([m - 1, 0]),
                 refinstname1=ip9.name, refinstindex1=np.array([m - 1, 0]))
    laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in9.name, gridname=rg_m1m2,
               refinstindex=np.array([m - 1, 0]))
    laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=ip9.name, gridname=rg_m1m2,
               refinstindex=np.array([m - 1, 0]))
    # power and groud rail
    xy = laygen.get_template_xy(name = in10.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd = laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=ip0.name, refinstname1=ip10.name)
    rvss = laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=in0.name, refinstname1=in10.name)
    #pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['I0', 'I1', 'EN0', 'EN1', 'O'], rect_list=[ri0, ri1, ren0, renb0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_latch_2ck(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,origin=np.array([0, 0]),
                   m=4, pin_clk_y=3, pin_clkb_y=2, route_mem_y=4, pin_o_y=5, create_pin=False):
    """generate D latch (complementary clock)"""
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4


    # placement
    i0 = laygen.place("I"+objectname_pfix + 'TINV0', "tinv_"+str(m)+"x", pg, xy=origin)
    #i1 = laygen.relplace(name = "I"+objectname_pfix + 'TINV1', templatename = "tinv_1x_nmosinput", gridname = pg, refinstname = i0.name) #used minimum size
    #i2 = laygen.relplace(name = "I"+objectname_pfix + 'INV0', templatename = "inv_"+str(m)+"x_pmosinput", gridname = pg, refinstname = i1.name)
    i1 = laygen.relplace(name = "I"+objectname_pfix + 'TINV1', templatename = "tinv_small_1x", gridname = pg, refinstname = i0.name) #used minimum size
    i2 = laygen.relplace(name = "I"+objectname_pfix + 'INV0', templatename = "inv_"+str(m)+"x", gridname = pg, refinstname = i1.name)

    # internal pins
    tinv0_i_xy = laygen.get_inst_pin_xy(i0.name, 'I', rg_m3m4)
    tinv0_en_xy = laygen.get_inst_pin_xy(i0.name, 'EN', rg_m3m4)
    tinv0_enb_xy = laygen.get_inst_pin_xy(i0.name, 'ENB', rg_m3m4)
    tinv0_o_xy = laygen.get_inst_pin_xy(i0.name, 'O', rg_m3m4)
    tinv1_i_xy = laygen.get_inst_pin_xy(i1.name, 'I', rg_m3m4)
    tinv1_en_xy = laygen.get_inst_pin_xy(i1.name, 'EN', rg_m3m4)
    tinv1_enb_xy = laygen.get_inst_pin_xy(i1.name, 'ENB', rg_m3m4)
    tinv1_o_xy = laygen.get_inst_pin_xy(i1.name, 'O', rg_m3m4)
    inv0_i_xy = laygen.get_inst_pin_xy(i2.name, 'I', rg_m3m4)
    inv0_o_xy = laygen.get_inst_pin_xy(i2.name, 'O', rg_m3m4)

    #clk
    rclk0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([tinv0_en_xy[0][0], pin_clk_y]), xy1=np.array([tinv1_enb_xy[0][0], pin_clk_y]), gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv0_en_xy[0][0], pin_clk_y]), xy1=tinv0_en_xy[0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv1_enb_xy[0][0], pin_clk_y]), xy1=tinv1_enb_xy[0], gridname0=rg_m3m4)
    laygen.via(None, np.array([tinv0_en_xy[0][0], pin_clk_y]), gridname=rg_m3m4)
    laygen.via(None, np.array([tinv1_enb_xy[0][0], pin_clk_y]), gridname=rg_m3m4)
    #clkb
    rclkb0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([tinv0_enb_xy[0][0], pin_clkb_y]), xy1=np.array([tinv1_en_xy[0][0], pin_clkb_y]), gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv0_enb_xy[0][0], pin_clkb_y]), xy1=tinv0_enb_xy[0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv1_en_xy[0][0], pin_clkb_y]), xy1=tinv1_en_xy[0], gridname0=rg_m3m4)
    laygen.via(None, np.array([tinv0_enb_xy[0][0], pin_clkb_y]), gridname=rg_m3m4)
    laygen.via(None, np.array([tinv1_en_xy[0][0], pin_clkb_y]), gridname=rg_m3m4)
    #storage node
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([tinv0_o_xy[0][0], route_mem_y]), xy1=np.array([inv0_i_xy[0][0], route_mem_y]), gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv0_o_xy[0][0], route_mem_y]), xy1=tinv0_o_xy[0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv1_o_xy[0][0], route_mem_y]), xy1=tinv1_o_xy[0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([inv0_i_xy[0][0], route_mem_y]), xy1=inv0_i_xy[0], gridname0=rg_m3m4)
    laygen.via(None, np.array([tinv0_o_xy[0][0], route_mem_y]), gridname=rg_m3m4)
    laygen.via(None, np.array([tinv1_o_xy[0][0], route_mem_y]), gridname=rg_m3m4)
    laygen.via(None, np.array([inv0_i_xy[0][0], route_mem_y]), gridname=rg_m3m4)
    #inv0 output to tinv1 input
    ro0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([tinv1_i_xy[0][0], pin_o_y]), xy1=np.array([inv0_o_xy[0][0], pin_o_y]), gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv1_i_xy[0][0], pin_o_y]), xy1=tinv1_i_xy[0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([inv0_o_xy[0][0], pin_o_y]), xy1=inv0_o_xy[0], gridname0=rg_m3m4)
    laygen.via(None, np.array([tinv1_i_xy[0][0], pin_o_y]), gridname=rg_m3m4)
    laygen.via(None, np.array([inv0_o_xy[0][0], pin_o_y]), gridname=rg_m3m4)

    #pin
    if create_pin == True:
        ri0_pin_xy=laygen.get_inst_pin_xy(name="I" + objectname_pfix + 'TINV0', pinname='I', gridname=rg_m3m4)

        laygen.pin(name='I', layer=laygen.layers['pin'][3], xy=ri0_pin_xy, gridname=rg_m3m4)
        laygen.pin(name='CLK', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(name = rclk0.name, gridname = rg_m3m4), gridname=rg_m3m4)
        laygen.pin(name='CLKB', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(name = rclkb0.name, gridname = rg_m3m4), gridname=rg_m3m4)
        laygen.pin(name='O', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(name = ro0.name, gridname = rg_m3m4), gridname=rg_m3m4)

        #power pin
        rvdd0_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'TINV0', 'VDD', rg_m2m3)
        rvdd1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'INV0', 'VDD', rg_m2m3)
        rvss0_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'TINV0', 'VSS', rg_m2m3)
        rvss1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'INV0', 'VSS', rg_m2m3)

        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=rg_m1m2)

def generate_latch_2ck_rstbh(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,origin=np.array([0, 0]),
                   m=4, pin_clk_y=3, pin_clkb_y=2, route_mem_y=4, pin_o_y=5, create_pin=False):
    """generate D latch (complementary clock)"""
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4


    # placement
    i0 = laygen.place("I"+objectname_pfix + 'TINV0', "tinv_"+str(m)+"x", pg, xy=origin)
    i1 = laygen.relplace(name = "I"+objectname_pfix + 'TINV1', templatename = "tinv_small_1x", gridname = pg, refinstname = i0.name) #used minimum size
    i2 = laygen.relplace(name = "I"+objectname_pfix + 'ND0', templatename = "nand_"+str(m)+"x", gridname = pg, refinstname = i1.name)

    # internal pins
    tinv0_i_xy = laygen.get_inst_pin_xy(i0.name, 'I', rg_m3m4)
    tinv0_en_xy = laygen.get_inst_pin_xy(i0.name, 'EN', rg_m3m4)
    tinv0_enb_xy = laygen.get_inst_pin_xy(i0.name, 'ENB', rg_m3m4)
    tinv0_o_xy = laygen.get_inst_pin_xy(i0.name, 'O', rg_m3m4)
    tinv1_i_xy = laygen.get_inst_pin_xy(i1.name, 'I', rg_m3m4)
    tinv1_en_xy = laygen.get_inst_pin_xy(i1.name, 'EN', rg_m3m4)
    tinv1_enb_xy = laygen.get_inst_pin_xy(i1.name, 'ENB', rg_m3m4)
    tinv1_o_xy = laygen.get_inst_pin_xy(i1.name, 'O', rg_m3m4)
    nd0_a_xy = laygen.get_inst_pin_xy(i2.name, 'A', rg_m3m4)
    nd0_b_xy = laygen.get_inst_pin_xy(i2.name, 'B', rg_m3m4)
    nd0_o_xy = laygen.get_inst_pin_xy(i2.name, 'O', rg_m3m4)

    #clk
    rclk0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([tinv0_en_xy[0][0], pin_clk_y]), xy1=np.array([tinv1_enb_xy[0][0], pin_clk_y]), gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv0_en_xy[0][0], pin_clk_y]), xy1=tinv0_en_xy[0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv1_enb_xy[0][0], pin_clk_y]), xy1=tinv1_enb_xy[0], gridname0=rg_m3m4)
    laygen.via(None, np.array([tinv0_en_xy[0][0], pin_clk_y]), gridname=rg_m3m4)
    laygen.via(None, np.array([tinv1_enb_xy[0][0], pin_clk_y]), gridname=rg_m3m4)
    #clkb
    rclkb0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([tinv0_enb_xy[0][0], pin_clkb_y]), xy1=np.array([tinv1_en_xy[0][0], pin_clkb_y]), gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv0_enb_xy[0][0], pin_clkb_y]), xy1=tinv0_enb_xy[0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv1_en_xy[0][0], pin_clkb_y]), xy1=tinv1_en_xy[0], gridname0=rg_m3m4)
    laygen.via(None, np.array([tinv0_enb_xy[0][0], pin_clkb_y]), gridname=rg_m3m4)
    laygen.via(None, np.array([tinv1_en_xy[0][0], pin_clkb_y]), gridname=rg_m3m4)
    #storage node
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([tinv0_o_xy[0][0], route_mem_y]), xy1=np.array([nd0_a_xy[0][0], route_mem_y]), gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv0_o_xy[0][0], route_mem_y]), xy1=tinv0_o_xy[0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv1_o_xy[0][0], route_mem_y]), xy1=tinv1_o_xy[0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([nd0_a_xy[0][0], route_mem_y]), xy1=nd0_a_xy[0], gridname0=rg_m3m4)
    laygen.via(None, np.array([tinv0_o_xy[0][0], route_mem_y]), gridname=rg_m3m4)
    laygen.via(None, np.array([tinv1_o_xy[0][0], route_mem_y]), gridname=rg_m3m4)
    laygen.via(None, np.array([nd0_a_xy[0][0], route_mem_y]), gridname=rg_m3m4)
    #nd0 output to tinv1 input
    ro0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([tinv1_i_xy[0][0], pin_o_y]), xy1=np.array([nd0_o_xy[0][0], pin_o_y]), gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([tinv1_i_xy[0][0], pin_o_y]), xy1=tinv1_i_xy[0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([nd0_o_xy[0][0], pin_o_y]), xy1=nd0_o_xy[0], gridname0=rg_m3m4)
    laygen.via(None, np.array([tinv1_i_xy[0][0], pin_o_y]), gridname=rg_m3m4)
    laygen.via(None, np.array([nd0_o_xy[0][0], pin_o_y]), gridname=rg_m3m4)

    #pin
    if create_pin == True:
        ri0_pin_xy=laygen.get_inst_pin_xy(name="I" + objectname_pfix + 'TINV0', pinname='I', gridname=rg_m3m4)

        laygen.pin(name='I', layer=laygen.layers['pin'][3], xy=ri0_pin_xy, gridname=rg_m3m4)
        laygen.pin(name='CLK', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(name = rclk0.name, gridname = rg_m3m4), gridname=rg_m3m4)
        laygen.pin(name='CLKB', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(name = rclkb0.name, gridname = rg_m3m4), gridname=rg_m3m4)
        laygen.pin(name='RSTB', layer=laygen.layers['pin'][3], xy=nd0_b_xy, gridname=rg_m3m4)
        laygen.pin(name='O', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(name = ro0.name, gridname = rg_m3m4), gridname=rg_m3m4)

        #power pin
        rvdd0_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'TINV0', 'VDD', rg_m2m3)
        rvdd1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'ND0', 'VDD', rg_m2m3)
        rvss0_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'TINV0', 'VSS', rg_m2m3)
        rvss1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'ND0', 'VSS', rg_m2m3)

        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=rg_m1m2)

def generate_dff(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,
                 origin=np.array([0, 0]),
                   m=4, create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4

    # placement
    i0 = laygen.place("I" + objectname_pfix + 'INV0', "inv_" + str(m) + "x", pg, xy=origin)
    i1 = laygen.relplace(name = "I" + objectname_pfix + 'INV1', templatename = "inv_" + str(m) + "x", gridname = pg, refinstname = i0.name)
    org=origin+laygen.get_inst_xy(name = 'I'+objectname_pfix+'INV1', gridname = pg)+ laygen.get_template_xy(name = i1.cellname, gridname = pg) * np.array([1, 0])
    generate_latch_2ck(laygen, objectname_pfix+'LCH0', placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,
                       origin=org, m=m, pin_clk_y=3, pin_clkb_y=2, route_mem_y=4, pin_o_y=5, create_pin=False)
    org=origin+laygen.get_inst_xy(name = 'I'+objectname_pfix+'LCH0INV0', gridname = pg)+ laygen.get_template_xy(name = i1.cellname, gridname = pg) * np.array([1, 0])
    generate_latch_2ck(laygen, objectname_pfix+'LCH1', placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,
                       origin=org, m=m, pin_clk_y=2, pin_clkb_y=3, route_mem_y=4, pin_o_y=5, create_pin=False)

    #internal coordinates
    i0_i_xy = laygen.get_inst_pin_xy(i0.name, 'I', rg_m3m4)
    i0_o_xy = laygen.get_inst_pin_xy(i0.name, 'O', rg_m3m4)
    i1_i_xy = laygen.get_inst_pin_xy(i1.name, 'I', rg_m3m4)
    i1_o_xy = laygen.get_inst_pin_xy(i1.name, 'O', rg_m3m4)
    ilch0_i_xy = laygen.get_inst_pin_xy('I'+objectname_pfix+'LCH0TINV0', 'I', rg_m3m4)
    ilch0_o_xy = laygen.get_inst_pin_xy('I'+objectname_pfix+'LCH0INV0', 'O', rg_m3m4)
    ilch1_i_xy = laygen.get_inst_pin_xy('I'+objectname_pfix+'LCH1TINV0', 'I', rg_m3m4)
    ilch1_ck_xy = laygen.get_inst_pin_xy('I'+objectname_pfix+'LCH1TINV0', 'EN', rg_m3m4)
    ilch1_ckb_xy = laygen.get_inst_pin_xy('I'+objectname_pfix+'LCH1TINV0', 'ENB', rg_m3m4)
    ilch1_o_xy = laygen.get_inst_pin_xy('I'+objectname_pfix+'LCH1INV0', 'O', rg_m3m4)

    # iclkb
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i0_o_xy[0], i1_i_xy[0], 3, rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i1_i_xy[0], ilch1_ckb_xy[0], 3, rg_m3m4)
    # iclk
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i1_o_xy[0], ilch1_ck_xy[0], 2, rg_m3m4)
    # intermediate
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ilch0_o_xy[0], ilch1_i_xy[0], 5, rg_m3m4)

    #pin
    if create_pin == True:
        laygen.pin(name='I', layer=laygen.layers['pin'][3], xy=ilch0_i_xy, gridname=rg_m3m4)
        laygen.pin(name='CLK', layer=laygen.layers['pin'][3], xy=i0_i_xy, gridname=rg_m3m4)
        laygen.pin(name='O', layer=laygen.layers['pin'][3], xy=ilch1_o_xy, gridname=rg_m3m4)

        #power pin
        rvdd0_pin_xy = laygen.get_inst_pin_xy(i0.name, 'VDD', rg_m2m3)
        rvdd1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'LCH1INV0', 'VDD', rg_m2m3)
        rvss0_pin_xy = laygen.get_inst_pin_xy(i0.name, 'VSS', rg_m2m3)
        rvss1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'LCH1INV0', 'VSS', rg_m2m3)
        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=rg_m1m2)

def generate_dff_rsth(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,
                 origin=np.array([0, 0]), m=4, create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4

    # placement
    i0 = laygen.place("I" + objectname_pfix + 'INV0', "inv_" + str(m) + "x", pg, xy=origin)
    i1 = laygen.relplace(name = "I" + objectname_pfix + 'INV1', templatename = "inv_" + str(m) + "x", gridname = pg, refinstname = i0.name)
    i2 = laygen.relplace(name = "I" + objectname_pfix + 'INV2', templatename = "inv_" + str(m) + "x", gridname = pg, refinstname = i1.name) #rstb
    org=origin+laygen.get_inst_xy(name = 'I'+objectname_pfix+'INV2', gridname = pg)+ laygen.get_template_xy(name = i1.cellname, gridname = pg) * np.array([1, 0])
    generate_latch_2ck_rstbh(laygen, objectname_pfix+'LCH0', placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,
                       origin=org, m=m, pin_clk_y=3, pin_clkb_y=2, route_mem_y=4, pin_o_y=5, create_pin=False)
    org=origin+laygen.get_inst_xy(name = 'I'+objectname_pfix+'LCH0ND0', gridname = pg)+ \
        laygen.get_template_xy(name = laygen.get_inst('I' + objectname_pfix + 'LCH0ND0').cellname, gridname = pg) * np.array([1, 0])
    generate_latch_2ck_rstbh(laygen, objectname_pfix+'LCH1', placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,
                       origin=org, m=m, pin_clk_y=2, pin_clkb_y=3, route_mem_y=4, pin_o_y=5, create_pin=False)

    #internal coordinates
    i0_i_xy = laygen.get_inst_pin_xy(i0.name, 'I', rg_m3m4)
    i0_o_xy = laygen.get_inst_pin_xy(i0.name, 'O', rg_m3m4)
    i1_i_xy = laygen.get_inst_pin_xy(i1.name, 'I', rg_m3m4)
    i1_o_xy = laygen.get_inst_pin_xy(i1.name, 'O', rg_m3m4)
    i2_i_xy = laygen.get_inst_pin_xy(i2.name, 'I', rg_m3m4)
    i2_o_xy = laygen.get_inst_pin_xy(i2.name, 'O', rg_m3m4)

    ilch0_i_xy = laygen.get_inst_pin_xy('I'+objectname_pfix+'LCH0TINV0', 'I', rg_m3m4)
    ilch0_rstb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0ND0', 'B', rg_m3m4)
    ilch0_o_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0ND0', 'O', rg_m3m4)
    ilch1_i_xy = laygen.get_inst_pin_xy('I'+objectname_pfix+'LCH1TINV0', 'I', rg_m3m4)
    ilch1_ck_xy = laygen.get_inst_pin_xy('I'+objectname_pfix+'LCH1TINV0', 'EN', rg_m3m4)
    ilch1_ckb_xy = laygen.get_inst_pin_xy('I'+objectname_pfix+'LCH1TINV0', 'ENB', rg_m3m4)
    ilch1_rstb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1ND0', 'B', rg_m3m4)
    ilch1_o_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1ND0', 'O', rg_m3m4)

    # iclkb
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i0_o_xy[0], i1_i_xy[0], 3, rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i1_i_xy[0], ilch1_ckb_xy[0], 3, rg_m3m4)
    # iclk
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i1_o_xy[0], ilch1_ck_xy[0], 2, rg_m3m4)
    # intermediate
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ilch0_o_xy[0], ilch1_i_xy[0], 5, rg_m3m4)
    # rstb
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i2_o_xy[0], ilch0_rstb_xy[0], 6, rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i2_o_xy[0], ilch1_rstb_xy[0], 6, rg_m3m4)

    #pin
    if create_pin == True:
        laygen.pin(name='I', layer=laygen.layers['pin'][3], xy=ilch0_i_xy, gridname=rg_m3m4)
        laygen.pin(name='CLK', layer=laygen.layers['pin'][3], xy=i0_i_xy, gridname=rg_m3m4)
        laygen.pin(name='RST', layer=laygen.layers['pin'][3], xy=i2_i_xy, gridname=rg_m3m4)
        laygen.pin(name='O', layer=laygen.layers['pin'][3], xy=ilch1_o_xy, gridname=rg_m3m4)

        #power pin
        rvdd0_pin_xy = laygen.get_inst_pin_xy(i0.name, 'VDD', rg_m1m2)
        rvdd1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'LCH1ND0', 'VDD', rg_m1m2) #(fix this)
        rvss0_pin_xy = laygen.get_inst_pin_xy(i0.name, 'VSS', rg_m1m2)
        rvss1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'LCH1ND0', 'VSS', rg_m1m2)

        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=rg_m1m2)

def generate_oai22_1x(laygen, objectname_pfix,
                      placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                      devname_nmos_boundary, devname_nmos_body_left, devname_nmos_body_right,
                      devname_pmos_boundary, devname_pmos_body_2stack,
                      origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix + 'N1', templatename = devname_nmos_body_left, gridname = pg, refinstname = in0.name)
    in2 = laygen.relplace(name = "I"+objectname_pfix + 'N2', templatename = devname_nmos_body_right, gridname = pg, refinstname = in1.name)
    in3 = laygen.relplace(name = "I"+objectname_pfix + 'N3', templatename = devname_nmos_boundary, gridname = pg, refinstname = in2.name)
    in4 = laygen.relplace(name = "I"+objectname_pfix + 'N4', templatename = devname_nmos_boundary, gridname = pg, refinstname = in3.name)
    in5 = laygen.relplace(name = "I"+objectname_pfix + 'N5', templatename = devname_nmos_body_left, gridname = pg, refinstname = in4.name)
    in6 = laygen.relplace(name = "I"+objectname_pfix + 'N6', templatename = devname_nmos_body_right, gridname = pg, refinstname = in5.name)
    in7 = laygen.relplace(name = "I"+objectname_pfix + 'N7', templatename = devname_nmos_boundary, gridname = pg, refinstname = in6.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix + 'P1', templatename = devname_pmos_body_2stack, gridname = pg, refinstname = ip0.name, transform='MX')
    ip3 = laygen.relplace(name = "I"+objectname_pfix + 'P3', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')
    ip4 = laygen.relplace(name = "I"+objectname_pfix + 'P4', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip3.name, transform='MX')
    ip5 = laygen.relplace(name = "I"+objectname_pfix + 'P5', templatename = devname_pmos_body_2stack, gridname = pg, refinstname = ip4.name, transform='MX')
    ip7 = laygen.relplace(name = "I"+objectname_pfix + 'P7', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip5.name, transform='MX')

    # route
    # A
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([2, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0',
                 refinstname1=in1.name, refpinname1='G0', endstyle0="extend", endstyle1="extend")
    ra0 = laygen.route("R"+objectname_pfix+"A0", laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    # B
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in2.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G1')
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='G1', gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='G1',
                 refinstname1=ip1.name, refpinname1='G1', endstyle0="extend", endstyle1="extend")
    rb0 = laygen.route("R"+objectname_pfix+"B0", laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                       refinstname0=in2.name, refpinname0='G0', refinstname1=in2.name, refpinname1='G0')
    laygen.via(None, np.array([-1, 0]), refinstname=ip1.name, refpinname='G1', gridname=rg_m2m3)
    # C
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in5.name, refpinname0='G0', refinstname1=ip5.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=in5.name, refpinname='G0', gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([2, 0]), gridname0=rg_m1m2,
                 refinstname0=in5.name, refpinname0='G0',
                 refinstname1=in5.name, refpinname1='G0', endstyle0="extend", endstyle1="extend")
    rc0 = laygen.route("R"+objectname_pfix+"C0", laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                       refinstname0=in5.name, refpinname0='G0', refinstname1=in5.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=in5.name, refpinname='G0', gridname=rg_m2m3)
    # D
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in6.name, refpinname0='G0', refinstname1=ip5.name, refpinname1='G1')
    laygen.via(None, np.array([0, 0]), refinstname=ip5.name, refpinname='G1', gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip5.name, refpinname0='G1',
                 refinstname1=ip5.name, refpinname1='G1', endstyle0="extend", endstyle1="extend")
    rd0 = laygen.route("R"+objectname_pfix+"D0", laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                       refinstname0=in6.name, refpinname0='G0', refinstname1=in6.name, refpinname1='G0')
    laygen.via(None, np.array([-1, 0]), refinstname=ip5.name, refpinname='G1', gridname=rg_m2m3)
    # PDN-internal
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='D0', refinstname1=in5.name, refpinname1='D0', via0=[[0, 0]], via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                 refinstname0=in5.name, refpinname0='S0', refinstname1=in6.name, refpinname1='D0', via0=[[0, 0]], via1=[[0, 0]])
    # PUP-internal
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='D0', refinstname1=ip5.name, refpinname1='D0', via0=[[0, 0]], via1=[[0, 0]])


    # output
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                       refinstname0=in6.name, refpinname0='D0', refinstname1=ip5.name, refpinname1='D0', via0=[[0, 0]], via1=[[0, 0]])

    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    xy_d0 = laygen.get_template_pin_xy(in1.cellname, 'D0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstname1=in1.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_d0 * np.array([1, 0]), xy1=xy_d0, gridname0=rg_m1m2,
                 refinstname0=in2.name, refinstname1=in2.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=ip1.name, refinstname1=ip1.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=ip5.name, refinstname1=ip5.name)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2)
    laygen.via(None, xy_d0 * np.array([1, 0]), refinstname=in2.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip5.name, gridname=rg_m1m2)

    # power and groud rail
    xy = laygen.get_template_xy(name = in1.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip7.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in7.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['A', 'B', 'C', 'D', 'O'], rect_list=[ra0, rb0, rc0, rd0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_oai22_skewed_1x(laygen, objectname_pfix,
                      placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                      devname_nmos_boundary, devname_nmos_body_left, devname_nmos_body_right, devname_nmos_space,
                      devname_pmos_boundary, devname_pmos_body_2stack,
                      origin=np.array([0, 0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix + 'N1', templatename = devname_nmos_body_left, gridname = pg, refinstname = in0.name)
    in2 = laygen.relplace(name = "I"+objectname_pfix + 'N2', templatename = devname_nmos_body_right, gridname = pg, refinstname = in1.name)
    in3 = laygen.relplace(name = "I"+objectname_pfix + 'N3', templatename = devname_nmos_boundary, gridname = pg, refinstname = in2.name)
    in4 = laygen.relplace(name = "I"+objectname_pfix + 'N4', templatename = devname_nmos_boundary, gridname = pg, refinstname = in3.name)
    in5 = laygen.relplace(name = "I"+objectname_pfix + 'N5', templatename = devname_nmos_body_left, gridname = pg, refinstname = in4.name)
    in6 = laygen.relplace(name = "I"+objectname_pfix + 'N6', templatename = devname_nmos_body_right, gridname = pg, refinstname = in5.name)
    in7 = laygen.relplace(name = "I"+objectname_pfix + 'N7', templatename = devname_nmos_boundary, gridname = pg, refinstname = in6.name)
    in8 = laygen.relplace(name = "I"+objectname_pfix + 'N8', templatename = devname_nmos_space, gridname = pg, refinstname = in7.name, shape=np.array([4, 1]))
    ip0 = laygen.relplace(name = "I"+objectname_pfix + 'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix + 'P1', templatename = devname_pmos_body_2stack, gridname = pg, refinstname = ip0.name, transform='MX')
    ip3 = laygen.relplace(name = "I"+objectname_pfix + 'P3', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')
    ip4 = laygen.relplace(name = "I"+objectname_pfix + 'P4', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip3.name, transform='MX')
    ip5 = laygen.relplace(name = "I"+objectname_pfix + 'P5', templatename = devname_pmos_body_2stack, gridname = pg, refinstname = ip4.name, transform='MX')
    ip5a = laygen.relplace(name = "I"+objectname_pfix + 'P5a', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip5.name, transform='MX')
    ip5b = laygen.relplace(name = "I"+objectname_pfix + 'P5b', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip5a.name, transform='MX')
    ip6 = laygen.relplace(name = "I"+objectname_pfix + 'P6', templatename = devname_pmos_body_2stack, gridname = pg, refinstname = ip5b.name, transform='MX')
    ip7 = laygen.relplace(name = "I"+objectname_pfix + 'P7', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip6.name, transform='MX')

    # route
    # A
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([2, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0',
                 refinstname1=in1.name, refpinname1='G0', endstyle0="extend", endstyle1="extend")
    ra0 = laygen.route("R"+objectname_pfix+"A0", laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    # B
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in2.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G1')
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='G1', gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='G1',
                 refinstname1=ip1.name, refpinname1='G1', endstyle0="extend", endstyle1="extend")
    rb0 = laygen.route("R"+objectname_pfix+"B0", laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                       refinstname0=in2.name, refpinname0='G0', refinstname1=in2.name, refpinname1='G0')
    laygen.via(None, np.array([-1, 0]), refinstname=ip1.name, refpinname='G1', gridname=rg_m2m3)
    # C
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in5.name, refpinname0='G0', refinstname1=ip5.name, refpinname1='G0')
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([6, 0]), xy1=np.array([6, 0]), gridname0=rg_m1m2,
                 refinstname0=in5.name, refpinname0='G0', refinstname1=ip5.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=in5.name, refpinname='G0', gridname=rg_m1m2)
    laygen.via(None, np.array([6, 0]), refinstname=in5.name, refpinname='G0', gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([6, 0]), gridname0=rg_m1m2,
                 refinstname0=in5.name, refpinname0='G0',
                 refinstname1=in5.name, refpinname1='G0', endstyle0="extend", endstyle1="extend")
    rc0 = laygen.route("R"+objectname_pfix+"C0", laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                       refinstname0=in5.name, refpinname0='G0', refinstname1=in5.name, refpinname1='G0')
    laygen.via(None, np.array([0, 0]), refinstname=in5.name, refpinname='G0', gridname=rg_m2m3)
    # D
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in6.name, refpinname0='G0', refinstname1=ip5.name, refpinname1='G1')
    laygen.via(None, np.array([0, 0]), refinstname=ip5.name, refpinname='G1', gridname=rg_m1m2)
    laygen.via(None, np.array([2, 0]), refinstname=ip5.name, refpinname='G1', gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([2, 0]), gridname0=rg_m1m2,
                 refinstname0=ip5.name, refpinname0='G1',
                 refinstname1=ip5.name, refpinname1='G1', endstyle0="extend", endstyle1="extend")
    rd0 = laygen.route("R"+objectname_pfix+"D0", laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                       refinstname0=in6.name, refpinname0='G0', refinstname1=in6.name, refpinname1='G0')
    laygen.via(None, np.array([-1, 0]), refinstname=ip5.name, refpinname='G1', gridname=rg_m2m3)
    # PDN-internal
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='D0', refinstname1=in5.name, refpinname1='D0', via0=[[0, 0]], via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                 refinstname0=in5.name, refpinname0='S0', refinstname1=in6.name, refpinname1='D0', via0=[[0, 0]], via1=[[0, 0]])
    # PUP-internal
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='D0', refinstname1=ip5.name, refpinname1='D0', via0=[[0, 0]], via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([2, 1]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='D0', refinstname1=ip5.name, refpinname1='D0', via0=[[0, 0]], via1=[[0, 0]])


    # output
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                       refinstname0=in6.name, refpinname0='D0', refinstname1=ip5.name, refpinname1='D0', via0=[[0, 0]], via1=[[0, 0]])

    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    xy_d0 = laygen.get_template_pin_xy(in1.cellname, 'D0', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstname1=in1.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_d0 * np.array([1, 0]), xy1=xy_d0, gridname0=rg_m1m2,
                 refinstname0=in2.name, refinstname1=in2.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=ip1.name, refinstname1=ip1.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                 refinstname0=ip5.name, refinstname1=ip5.name)
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0])+np.array([2,0]), xy1=xy_s0+np.array([2,0]), gridname0=rg_m1m2,
                 refinstname0=ip6.name, refinstname1=ip6.name)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2)
    laygen.via(None, xy_d0 * np.array([1, 0]), refinstname=in2.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip5.name, gridname=rg_m1m2)
    laygen.via(None, xy_s0 * np.array([1, 0])+np.array([2,0]), refinstname=ip6.name, gridname=rg_m1m2)

    # power and groud rail
    xy = laygen.get_template_xy(name = in1.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip7.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in7.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['A', 'B', 'C', 'D', 'O'], rect_list=[ra0, rb0, rc0, rd0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_ndsr(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,
                  origin=np.array([0, 0]), m=2, create_pin=False):
    """generate nand type SR latch"""
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4

    # placement
    i0 = laygen.place("I"+objectname_pfix + 'ND0', "nand_"+str(m)+"x", pg, xy=origin)
    i1 = laygen.relplace(name = "I"+objectname_pfix + 'ND1', templatename = "nand_"+str(m)+"x", gridname = pg, refinstname = i0.name)
    i2 = laygen.relplace(name = "I"+objectname_pfix + 'INV0', templatename = "inv_"+str(m)+"x", gridname = pg, refinstname = i1.name)
    i3 = laygen.relplace(name = "I"+objectname_pfix + 'INV1', templatename = "inv_"+str(m)+"x", gridname = pg, refinstname = i2.name)

    # internal pins
    nd0_a_xy = laygen.get_inst_pin_xy(i0.name, 'A', rg_m3m4)
    nd0_b_xy = laygen.get_inst_pin_xy(i0.name, 'B', rg_m3m4)
    nd0_o_xy = laygen.get_inst_pin_xy(i0.name, 'O', rg_m3m4)
    nd1_a_xy = laygen.get_inst_pin_xy(i1.name, 'A', rg_m3m4)
    nd1_b_xy = laygen.get_inst_pin_xy(i1.name, 'B', rg_m3m4)
    nd1_o_xy = laygen.get_inst_pin_xy(i1.name, 'O', rg_m3m4)
    buf0_i_xy = laygen.get_inst_pin_xy(i2.name, 'I', rg_m3m4)
    buf0_o_xy = laygen.get_inst_pin_xy(i2.name, 'O', rg_m3m4)
    buf1_i_xy = laygen.get_inst_pin_xy(i3.name, 'I', rg_m3m4)
    buf1_o_xy = laygen.get_inst_pin_xy(i3.name, 'O', rg_m3m4)

    #route
    y0=nd0_a_xy[0][1]
    #Q_pre
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], nd0_o_xy[1], buf0_i_xy[0], y0+2, rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], nd0_o_xy[1], nd1_b_xy[0], y0+2, rg_m3m4)
    #Qb_pre
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], nd1_o_xy[1], buf1_i_xy[0], y0+3, rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], nd1_o_xy[1], nd0_b_xy[0], y0+3, rg_m3m4)

    #pin
    if create_pin == True:
        laygen.pin(name='S', layer=laygen.layers['pin'][3], xy=nd0_a_xy, gridname=rg_m3m4)
        laygen.pin(name='R', layer=laygen.layers['pin'][3], xy=nd1_a_xy, gridname=rg_m3m4)
        laygen.pin(name='Q', layer=laygen.layers['pin'][3], xy=buf0_o_xy, gridname=rg_m3m4)
        laygen.pin(name='QB', layer=laygen.layers['pin'][3], xy=buf1_o_xy, gridname=rg_m3m4)

        #power pin
        rvdd0_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'ND0', 'VDD', rg_m2m3)
        rvdd1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'INV1', 'VDD', rg_m2m3)
        rvss0_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'ND0', 'VSS', rg_m2m3)
        rvss1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'INV1', 'VSS', rg_m2m3)

        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=rg_m1m2)

##Add by zhongkai
def generate_tgate_dn(laygen, objectname_pfix,
                 placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                 devname_nmos_boundary, devname_nmos_body, devname_nmos_space,
                 devname_pmos_boundary, devname_pmos_body, devname_pmos_space,
                 m=1, n=1, m_in=3, m_out=3, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m = max(1, int(m / 2))  # passgate size, using nf=2 devices
    n = max(1, int(n / 2))  # pulldown size, using nf=2 devices

    if m_in > m/2:        
        m_in = int(m/2)            #input paths

    if m_out > m/2:
        m_out = int(m/2)           #output_paths

    # placement
    in_space = laygen.place("I"+objectname_pfix+'NDMY', devname_nmos_space, pg, shape=np.array([2, 1]), xy=origin)
    in0 = laygen.relplace(name = "I" + objectname_pfix + 'N0', templatename = devname_nmos_boundary, gridname = pg, refinstname = in_space.name)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name, shape=np.array([2, 1]))
    in3 = laygen.relplace(name = "I"+objectname_pfix+'N3', templatename = devname_nmos_body, gridname = pg, refinstname = in2.name, shape=np.array([n, 1]))
    in4 = laygen.relplace(name = "I"+objectname_pfix+'N4', templatename = devname_nmos_boundary, gridname = pg, refinstname = in3.name)

    ip_space = laygen.relplace(name = "I"+objectname_pfix+'PDMY', templatename = devname_pmos_space, gridname = pg, refinstname = in_space.name, direction='top', transform='MX', shape=np.array([2, 1]))
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip_space.name, transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P1', templatename = devname_pmos_body, gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P2', templatename = devname_pmos_boundary, gridname = pg, refinstname = ip1.name, transform='MX')
    ip3 = laygen.relplace(name = "I"+objectname_pfix+'P3', templatename = 'pmos4_fast_space', gridname = pg, refinstname = ip2.name, shape=np.array([n+4,1]), transform='MX')

    # route
    #to vss
    for i in range(n):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                    refinstname0=in3.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                    refinstname1=in3.name, refpinname1='S0', refinstindex1=np.array([i, 0]))
        laygen.via(None, np.array([0, 0]), refinstname=in3.name, gridname=rg_m1m2, refinstindex=np.array([i, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                refinstname0=in3.name, refpinname0='S0', refinstindex0=np.array([n, 0]),
                refinstname1=in3.name, refpinname1='S0', refinstindex1=np.array([n, 0]))
    laygen.via(None, np.array([0, 0]), refinstname=in3.name, gridname=rg_m1m2, refinstindex=np.array([n, 0]))

    
    # en, enb
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-3, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-3, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip1.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
    ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-3, 0]), xy1=np.array([-3, 2]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
    laygen.via(None, np.array([-3, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    renb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2, 0]), xy1=np.array([-2, 2]), gridname0=rg_m2m3,
                       refinstname0=ip1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0')
    laygen.via(None, np.array([-2, 0]), refinstname=ip1.name, refpinname='G0', gridname=rg_m2m3)

    # gate for pull down
    in3_g0_xy = laygen.get_inst_pin_xy(in3.name, 'G0', rg_m2m3)
    ip1_g0_xy = laygen.get_inst_pin_xy(ip1.name, 'G0', rg_m2m3)
    laygen.route_vh(laygen.layers['metal'][1], laygen.layers['metal'][2], in3_g0_xy[0], ip1_g0_xy[0], rg_m1m2)

    for i in range(n):
        laygen.via(None, np.array([0, 0]), refinstname=in3.name, refpinname='G0', gridname=rg_m1m2, refinstindex=np.array([i, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in3.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=in3.name, refpinname1='G0', refinstindex1=np.array([n-1, 0]))
    
    #input
    #input wire
    for i in range(m_in):
        rix = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                       refinstname1=ip1.name, refpinname1='S0', refinstindex1=np.array([i, 0]))
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m2m3)
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m2m3)

        if create_pin == True:
            laygen.pin(gridname=rg_m2m3, name='I_'+str(i), layer=laygen.layers['pin'][3], refobj=rix, netname='I') 

    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    #connecting source
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='S1', refinstindex=np.array([m-1, 0]), gridname=rg_m1m2)

    
    #output
    #output wire
    for i in range(m_out):
        rox = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([m-1-i, 0]),
                       refinstname1=ip1.name, refpinname1='D0', refinstindex1=np.array([m-1-i, 0]))
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([m-1-i, 0]), gridname=rg_m2m3)
        laygen.via(None, np.array([0, 1]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([m-1-i, 0]), gridname=rg_m2m3)
        if create_pin == True:
            laygen.pin(gridname=rg_m2m3, name='O_'+str(i), layer=laygen.layers['pin'][3], refobj=rox, netname='O') 

    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    #connection for in3
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([m-1, 0]),
                 refinstname1=in3.name, refpinname1='D0', refinstindex1=np.array([n-1, 0]))
    #connecting drain
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    
    #connection for in3
    for i in range(n):
        laygen.via(None, np.array([0, 1]), refinstname=in3.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    
    # power and groud rail
    xy = laygen.get_template_xy(name = ip3.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd = laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=ip_space.name, refinstname1=ip3.name, refinstindex1=np.array([n+3, 0]))
    rvss = laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=in_space.name, refinstname1=in4.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['EN', 'ENB'], rect_list=[ren0, renb0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_cap_sw(laygen, objectname_pfix,
                 placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                 devname_nmos_boundary, devname_nmos_body, devname_nmos_space,
                 devname_pmos_boundary, devname_pmos_body, devname_pmos_space,
                 m=1, origin=np.array([0,0]), create_pin=False):
    #generate an nmos type switch
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m = max(1, int(m / 2))  # using nf=2 devices

    # placement
    in0 = laygen.place("I" + objectname_pfix + 'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace(name = "I"+objectname_pfix+'N1', templatename = devname_nmos_body, gridname = pg, refinstname = in0.name, shape=np.array([m, 1]))
    in2 = laygen.relplace(name = "I"+objectname_pfix+'N2', templatename = devname_nmos_boundary, gridname = pg, refinstname = in1.name)
    ip0 = laygen.relplace(name = "I"+objectname_pfix+'P0', templatename = 'pmos4_fast_space', gridname = pg, refinstname = in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace(name = "I"+objectname_pfix+'P2', templatename = 'pmos4_fast_space', gridname = pg, refinstname = ip0.name, transform='MX', shape=np.array([m*2, 1]))
    ip2 = laygen.relplace(name = "I"+objectname_pfix+'P3', templatename = 'pmos4_fast_space', gridname = pg, refinstname = ip1.name, transform='MX')

    # route
    # to ground
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                    refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                    refinstname1=in1.name, refpinname1='S0', refinstindex1=np.array([i, 0]))
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, gridname=rg_m1m2, refinstindex=np.array([i, 0]))

    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                refinstname0=in1.name, refpinname0='S1', refinstindex0=np.array([m-1, 0]),
                refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, gridname=rg_m1m2, refinstindex=np.array([m, 0]))

    # en, enb
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m-1, 0]))
    ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0')
    laygen.via(None, np.array([-1, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)

    
    #output
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1+1, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='S0', refinstindex0=np.array([0, 0]), endstyle0='extend',
                 refinstname1=in1.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]), endstyle1='extend')
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    ro=[]
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m2m3)
        ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, -1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([i, 0]),
                       refinstname1=in1.name, refpinname1='D0', refinstindex1=np.array([i, 0]))
        ro.append(ro0)

    # power and groud rail
    xy = laygen.get_template_xy(name = in2.cellname, gridname = rg_m1m2) * np.array([1, 0])
    rvdd = laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=ip0.name, refinstname1=ip2.name)
    rvss = laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                        refinstname0=in0.name, refinstname1=in2.name)
    # pin
    if create_pin == True:
        ren0_pin_xy = laygen.get_rect_xy(name = ren0.name, gridname = rg_m3m4)
        laygen.pin(name='EN', layer=laygen.layers['pin'][3], xy=ren0_pin_xy, gridname=rg_m3m4, netname='EN')
        ro0_pin_xy = laygen.get_rect_xy(name = ro[0].name, gridname = rg_m3m4)
        laygen.pin(name='VO', layer=laygen.layers['pin'][3], xy=ro0_pin_xy, gridname=rg_m3m4, netname='VO')
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)


def generate_latch_2ck_strstbh(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,origin=np.array([0, 0]),
                   m=4, pin_clk_y=3, pin_clkb_y=2, route_mem_y=4, route_rstm_y=5, pin_o_y=6, create_pin=False):
    """generate D latch (complementary clock)"""
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4


    # placement
    i0 = laygen.place("I"+objectname_pfix + 'TINV0', "tinv_"+str(m)+"x", pg, xy=origin)
    i2 = laygen.relplace(name = "I"+objectname_pfix + 'TGAT0', templatename = "tgate_2x", gridname = pg, refinstname = i0.name) #used minimum size
    i3 = laygen.relplace(name = "I"+objectname_pfix + 'ND1', templatename = "nand_2x", gridname = pg, refinstname = i2.name) #used minimum size
    i1 = laygen.relplace(name = "I"+objectname_pfix + 'ND0', templatename = "nand_"+str(m)+"x", gridname = pg, refinstname = i3.name)

    # internal pins
    tinv0_i_xy = laygen.get_inst_pin_xy(i0.name, 'I', rg_m3m4)
    tinv0_en_xy = laygen.get_inst_pin_xy(i0.name, 'EN', rg_m3m4)
    tinv0_enb_xy = laygen.get_inst_pin_xy(i0.name, 'ENB', rg_m3m4)
    tinv0_o_xy = laygen.get_inst_pin_xy(i0.name, 'O', rg_m3m4)
    nd0_a_xy = laygen.get_inst_pin_xy(i1.name, 'A', rg_m3m4)
    nd0_b_xy = laygen.get_inst_pin_xy(i1.name, 'B', rg_m3m4)
    nd0_o_xy = laygen.get_inst_pin_xy(i1.name, 'O', rg_m3m4)
    tgate0_i_xy = laygen.get_inst_pin_xy(i2.name, 'I', rg_m3m4)
    tgate0_en_xy = laygen.get_inst_pin_xy(i2.name, 'EN', rg_m3m4)
    tgate0_enb_xy = laygen.get_inst_pin_xy(i2.name, 'ENB', rg_m3m4)
    tgate0_o_xy = laygen.get_inst_pin_xy(i2.name, 'O', rg_m3m4)
    nd1_a_xy = laygen.get_inst_pin_xy(i3.name, 'A', rg_m3m4)
    nd1_b_xy = laygen.get_inst_pin_xy(i3.name, 'B', rg_m3m4)
    nd1_o_xy = laygen.get_inst_pin_xy(i3.name, 'O', rg_m3m4)


    #clk
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], tinv0_en_xy[0], tgate0_enb_xy[0], pin_clk_y, rg_m3m4)
    rclk0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([tinv0_en_xy[0][0], pin_clk_y]), xy1=np.array([tgate0_enb_xy[0][0], pin_clk_y]), gridname0=rg_m3m4)

    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], tinv0_enb_xy[0], tgate0_en_xy[0], pin_clkb_y, rg_m3m4)
    rclkb0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([tinv0_enb_xy[0][0], pin_clkb_y]), xy1=np.array([tgate0_en_xy[0][0], pin_clkb_y]), gridname0=rg_m3m4)

    #storage node
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], np.array([tinv0_o_xy[0][0],route_mem_y]), np.array([tgate0_o_xy[0][0],route_mem_y]), route_mem_y, rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], np.array([tgate0_o_xy[0][0],route_mem_y]), np.array([nd0_a_xy[0][0],route_mem_y]), route_mem_y, rg_m3m4)
    
    #resetm node
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], np.array([nd1_o_xy[0][0],route_rstm_y]), np.array([tgate0_i_xy[0][0],route_rstm_y]), route_rstm_y, rg_m3m4)
    
    #nd0 output to nd1 input
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], np.array([nd0_o_xy[0][0],pin_o_y]), np.array([nd1_a_xy[0][0],pin_o_y]), pin_o_y, rg_m3m4)
    ro0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([nd0_o_xy[0][0], pin_o_y]), xy1=np.array([nd1_a_xy[0][0], pin_o_y]), gridname0=rg_m3m4)
    
    #pin
    if create_pin == True:
        ri0_pin_xy=laygen.get_inst_pin_xy(name="I" + objectname_pfix + 'TINV0', pinname='I', gridname=rg_m3m4)

        laygen.pin(name='I', layer=laygen.layers['pin'][3], xy=ri0_pin_xy, gridname=rg_m3m4)
        laygen.pin(name='CLK', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(name = rclk0.name, gridname = rg_m3m4), gridname=rg_m3m4)
        laygen.pin(name='CLKB', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(name = rclkb0.name, gridname = rg_m3m4), gridname=rg_m3m4)
        laygen.pin(name='STB', layer=laygen.layers['pin'][3], xy=nd0_b_xy, gridname=rg_m3m4)
        laygen.pin(name='RSTB', layer=laygen.layers['pin'][3], xy=nd1_b_xy, gridname=rg_m3m4)
        laygen.pin(name='O', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(name = ro0.name, gridname = rg_m3m4), gridname=rg_m3m4)

        #power pin
           
        rvdd0_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'TINV0', 'VDD', rg_m2m3)
        rvdd1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'ND0', 'VDD', rg_m2m3)
        rvss0_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'TINV0', 'VSS', rg_m2m3)
        rvss1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'ND0', 'VSS', rg_m2m3)

        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=rg_m1m2)


def generate_dff_strsth(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,
                 origin=np.array([0, 0]), m=4, create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4

    # placement
    i8 = laygen.place("I" + objectname_pfix + 'INV8', "inv_" + str(m) + "x", pg, xy=origin)  
    i9 = laygen.relplace(name = "I" + objectname_pfix + 'INV9', templatename = "inv_" + str(m) + "x", gridname = pg, refinstname = i8.name) 
    i10= laygen.relplace(name = "I" + objectname_pfix + 'INV10', templatename = "inv_" + str(m) + "x", gridname = pg, refinstname = i9.name) #stb
    i11= laygen.relplace(name = "I" + objectname_pfix + 'INV11', templatename = "inv_" + str(m) + "x", gridname = pg, refinstname = i10.name) #rstb
    org=origin+laygen.get_inst_xy(name = 'I'+objectname_pfix+'INV11', gridname = pg)+ laygen.get_template_xy(name = i10.cellname, gridname = pg) * np.array([1, 0])
    generate_latch_2ck_strstbh(laygen, objectname_pfix+'LCH0', placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4, 
                       origin=org, m=m, pin_clk_y=3, pin_clkb_y=2, route_mem_y=4, route_rstm_y = 8, pin_o_y=5, create_pin=False)      ##These two lines use different position for clk and clkb
    org=origin+laygen.get_inst_xy(name = 'I'+objectname_pfix+'LCH0ND0', gridname = pg)+ \
        laygen.get_template_xy(name = laygen.get_inst('I' + objectname_pfix + 'LCH0ND0').cellname, gridname = pg) * np.array([1, 0])
    generate_latch_2ck_strstbh(laygen, objectname_pfix+'LCH1', placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,
                       origin=org, m=m, pin_clk_y=2, pin_clkb_y=3, route_mem_y=4, route_rstm_y = 8, pin_o_y=5, create_pin=False)
    
    #inverter coordinates
    i8_i_xy = laygen.get_inst_pin_xy(i8.name, 'I', rg_m3m4)
    i8_o_xy = laygen.get_inst_pin_xy(i8.name, 'O', rg_m3m4)
    i9_i_xy = laygen.get_inst_pin_xy(i9.name, 'I', rg_m3m4)
    i9_o_xy = laygen.get_inst_pin_xy(i9.name, 'O', rg_m3m4)
    i10_i_xy = laygen.get_inst_pin_xy(i10.name, 'I', rg_m3m4)
    i10_o_xy = laygen.get_inst_pin_xy(i10.name, 'O', rg_m3m4)
    i11_i_xy = laygen.get_inst_pin_xy(i11.name, 'I', rg_m3m4)
    i11_o_xy = laygen.get_inst_pin_xy(i11.name, 'O', rg_m3m4)
   
        
    #Latch coordinate
    ilch0_i_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0TINV0', 'I', rg_m3m4)
    ilch0_ck_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0TINV0', 'EN', rg_m3m4)
    ilch0_ckb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0TINV0', 'ENB', rg_m3m4)
    ilch0_stb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0ND0', 'B', rg_m3m4)  #set pin of latch 0
    ilch0_rstb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0ND1', 'B', rg_m3m4) #reset pin of latch 0
    ilch0_o_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0ND0', 'O', rg_m3m4)

    ilch1_i_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1TINV0', 'I', rg_m3m4)
    ilch1_ck_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1TINV0', 'EN', rg_m3m4)
    ilch1_ckb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1TINV0', 'ENB', rg_m3m4)
    ilch1_stb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1ND0', 'B', rg_m3m4)   #set pin of latch 0
    ilch1_rstb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1ND1', 'B', rg_m3m4)  #reset pin of latch 1
    ilch1_o_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1ND0', 'O', rg_m3m4)
    
    # iclkb
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i8_o_xy[0], i9_i_xy[0], 3, rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i9_i_xy[0], ilch1_ckb_xy[0], 3, rg_m3m4)
    # iclk
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i9_o_xy[0], ilch1_ck_xy[0], 2, rg_m3m4)
    # intermediate
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ilch0_o_xy[0], ilch1_i_xy[0], 5, rg_m3m4)
    # stb
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i10_o_xy[0], ilch0_stb_xy[0], 6, rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i10_o_xy[0], ilch1_stb_xy[0], 6, rg_m3m4)
    # rstb
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i11_o_xy[0], ilch0_rstb_xy[0], 7, rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i11_o_xy[0], ilch1_rstb_xy[0], 7, rg_m3m4)

    
    #pin
    if create_pin == True:
        laygen.pin(name='I', layer=laygen.layers['pin'][3], xy=ilch0_i_xy, gridname=rg_m3m4)
        laygen.pin(name='CLK', layer=laygen.layers['pin'][3], xy=i8_i_xy, gridname=rg_m3m4)
        laygen.pin(name='ST', layer=laygen.layers['pin'][3], xy=i10_i_xy, gridname=rg_m3m4)
        laygen.pin(name='RST', layer=laygen.layers['pin'][3], xy=i11_i_xy, gridname=rg_m3m4)
        laygen.pin(name='O', layer=laygen.layers['pin'][3], xy=ilch1_o_xy, gridname=rg_m3m4)

        #power pin
        rvdd0_pin_xy = laygen.get_inst_pin_xy(i8.name, 'VDD', rg_m1m2)
        rvdd1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'LCH1ND0', 'VDD', rg_m1m2) #(fix this)
        rvss0_pin_xy = laygen.get_inst_pin_xy(i8.name, 'VSS', rg_m1m2)
        rvss1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'LCH1ND0', 'VSS', rg_m1m2)

        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=rg_m1m2)


def generate_dff_strsth_ckb(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,
                 origin=np.array([0, 0]), m=4, create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4

    # placement
    i12 = laygen.place("I" + objectname_pfix + 'INV12', "inv_" + str(m) + "x", pg, xy=origin)
    i8 = laygen.relplace(name = "I" + objectname_pfix + 'INV8', templatename = "inv_" + str(m) + "x", gridname = pg, refinstname = i12.name)  #clk buffers -- try to make sure the number is same with schematic
    i9 = laygen.relplace(name = "I" + objectname_pfix + 'INV9', templatename = "inv_" + str(m) + "x", gridname = pg, refinstname = i8.name) #that is why it's not start from '0'
    i10= laygen.relplace(name = "I" + objectname_pfix + 'INV10', templatename = "inv_" + str(m) + "x", gridname = pg, refinstname = i9.name) #stb
    i11= laygen.relplace(name = "I" + objectname_pfix + 'INV11', templatename = "inv_" + str(m) + "x", gridname = pg, refinstname = i10.name) #rstb
    org=origin+laygen.get_inst_xy(name = 'I'+objectname_pfix+'INV11', gridname = pg)+ laygen.get_template_xy(name = i10.cellname, gridname = pg) * np.array([1, 0])
    generate_latch_2ck_strstbh(laygen, objectname_pfix+'LCH0', placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4, #Can we return the object of it as before? -- Zhongkai
                       origin=org, m=m, pin_clk_y=3, pin_clkb_y=2, route_mem_y=4, route_rstm_y = 8, pin_o_y=5, create_pin=False)      ##These two lines use different position for clk and clkb
    org=origin+laygen.get_inst_xy(name = 'I'+objectname_pfix+'LCH0ND0', gridname = pg)+ \
        laygen.get_template_xy(name = laygen.get_inst('I' + objectname_pfix + 'LCH0ND0').cellname, gridname = pg) * np.array([1, 0])
    generate_latch_2ck_strstbh(laygen, objectname_pfix+'LCH1', placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,
                       origin=org, m=m, pin_clk_y=2, pin_clkb_y=3, route_mem_y=4, route_rstm_y = 8, pin_o_y=5, create_pin=False)
    
    #inverter coordinates
    i12_i_xy = laygen.get_inst_pin_xy(i12.name, 'I', rg_m3m4)
    i12_o_xy = laygen.get_inst_pin_xy(i12.name, 'O', rg_m3m4)
    i8_i_xy = laygen.get_inst_pin_xy(i8.name, 'I', rg_m3m4)
    i8_o_xy = laygen.get_inst_pin_xy(i8.name, 'O', rg_m3m4)
    i9_i_xy = laygen.get_inst_pin_xy(i9.name, 'I', rg_m3m4)
    i9_o_xy = laygen.get_inst_pin_xy(i9.name, 'O', rg_m3m4)
    i10_i_xy = laygen.get_inst_pin_xy(i10.name, 'I', rg_m3m4)
    i10_o_xy = laygen.get_inst_pin_xy(i10.name, 'O', rg_m3m4)
    i11_i_xy = laygen.get_inst_pin_xy(i11.name, 'I', rg_m3m4)
    i11_o_xy = laygen.get_inst_pin_xy(i11.name, 'O', rg_m3m4)
    
    #Latch coordinate
    ilch0_i_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0TINV0', 'I', rg_m3m4)
    ilch0_ck_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0TINV0', 'EN', rg_m3m4)
    ilch0_ckb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0TINV0', 'ENB', rg_m3m4)
    ilch0_stb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0ND0', 'B', rg_m3m4)  #set pin of latch 0
    ilch0_rstb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0ND1', 'B', rg_m3m4) #reset pin of latch 0
    ilch0_o_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH0ND0', 'O', rg_m3m4)

    ilch1_i_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1TINV0', 'I', rg_m3m4)
    ilch1_ck_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1TINV0', 'EN', rg_m3m4)
    ilch1_ckb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1TINV0', 'ENB', rg_m3m4)
    ilch1_stb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1ND0', 'B', rg_m3m4)   #set pin of latch 0
    ilch1_rstb_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1ND1', 'B', rg_m3m4)  #reset pin of latch 1
    ilch1_o_xy = laygen.get_inst_pin_xy('I' + objectname_pfix + 'LCH1ND0', 'O', rg_m3m4)
    
    #clk
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i12_o_xy[0], i8_i_xy[0], 5, rg_m3m4)
    # iclkb
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i8_o_xy[0], i9_i_xy[0], 3, rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i9_i_xy[0], ilch1_ckb_xy[0], 3, rg_m3m4)
    # iclk
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i9_o_xy[0], ilch1_ck_xy[0], 2, rg_m3m4)
    # intermediate
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ilch0_o_xy[0], ilch1_i_xy[0], 5, rg_m3m4)
    # stb
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i10_o_xy[0], ilch0_stb_xy[0], 6, rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i10_o_xy[0], ilch1_stb_xy[0], 6, rg_m3m4)
    # rstb
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i11_o_xy[0], ilch0_rstb_xy[0], 7, rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], i11_o_xy[0], ilch1_rstb_xy[0], 7, rg_m3m4)

    
    #pin
    if create_pin == True:
        laygen.pin(name='I', layer=laygen.layers['pin'][3], xy=ilch0_i_xy, gridname=rg_m3m4)
        laygen.pin(name='CLKB', layer=laygen.layers['pin'][3], xy=i12_i_xy, gridname=rg_m3m4)
        laygen.pin(name='ST', layer=laygen.layers['pin'][3], xy=i10_i_xy, gridname=rg_m3m4)
        laygen.pin(name='RST', layer=laygen.layers['pin'][3], xy=i11_i_xy, gridname=rg_m3m4)
        laygen.pin(name='O', layer=laygen.layers['pin'][3], xy=ilch1_o_xy, gridname=rg_m3m4)

        #power pin
        rvdd0_pin_xy = laygen.get_inst_pin_xy(i12.name, 'VDD', rg_m1m2)
        rvdd1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'LCH1ND0', 'VDD', rg_m1m2) #(fix this)
        rvss0_pin_xy = laygen.get_inst_pin_xy(i12.name, 'VSS', rg_m1m2)
        rvss1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'LCH1ND0', 'VSS', rg_m1m2)

        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=rg_m1m2)
    

if __name__ == '__main__':
    laygen = laygo.GridLayoutGenerator(config_file="laygo_config.yaml")

    import imp
    try:
        imp.find_module('bag')
        laygen.use_phantom = False
    except ImportError:
        laygen.use_phantom = True

    tech=laygen.tech
    utemplib = tech+'_microtemplates_dense'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)
    #laygen.templates.display()
    #laygen.grids.display()

    #library generation
    workinglib = tech+'_logic_templates'
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
    if os.path.exists(workinglib+'.yaml'): #generated layout file exists
        laygen.load_template(filename=workinglib+'.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    #grid
    pg = 'placement_basic' #placement grid
    rg_m1m2 = 'route_M1_M2_cmos'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    # cell generation
    laygen.add_cell('space_1x')
    laygen.sel_cell('space_1x')
    generate_space_1x(laygen, objectname_pfix='SPACE0', placement_grid=pg, routing_grid_m1m2=rg_m1m2, create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('space_2x')
    laygen.sel_cell('space_2x')
    generate_space_2x(laygen, objectname_pfix='SPACE0', placement_grid=pg, routing_grid_m1m2=rg_m1m2, create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('space_4x')
    laygen.sel_cell('space_4x')
    generate_space_4x(laygen, objectname_pfix='SPACE0', placement_grid=pg, routing_grid_m1m2=rg_m1m2, create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('space_wovdd_1x')
    laygen.sel_cell('space_wovdd_1x')
    generate_space_wovdd_1x(laygen, objectname_pfix='SPACE0', placement_grid=pg, routing_grid_m1m2=rg_m1m2, create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('space_wovdd_2x')
    laygen.sel_cell('space_wovdd_2x')
    generate_space_wovdd_2x(laygen, objectname_pfix='SPACE0', placement_grid=pg, routing_grid_m1m2=rg_m1m2, create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('space_wovdd_4x')
    laygen.sel_cell('space_wovdd_4x')
    generate_space_wovdd_4x(laygen, objectname_pfix='SPACE0', placement_grid=pg, routing_grid_m1m2=rg_m1m2, create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('tap')
    laygen.sel_cell('tap')
    generate_tap(laygen, objectname_pfix='TAP0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                 devname_nmos_tap='nmos4_fast_tap', devname_pmos_tap='pmos4_fast_tap',
                 origin=np.array([0, 0]), create_pin=True
                 )
    laygen.add_template_from_cell()

    laygen.add_cell('tap_float')
    laygen.sel_cell('tap_float')
    generate_tap_float(laygen, objectname_pfix='TAP0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                 devname_nmos_tap='nmos4_fast_tap', devname_pmos_tap='pmos4_fast_tap',
                 origin=np.array([0, 0]), create_pin=True
                 )
    laygen.add_template_from_cell()

    laygen.add_cell('tap_wovdd')
    laygen.sel_cell('tap_wovdd')
    generate_tap_wovdd(laygen, objectname_pfix='TAP0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                 devname_nmos_tap='nmos4_fast_tap', 
                 origin=np.array([0, 0]), create_pin=True
                 )
    laygen.add_template_from_cell()

    laygen.add_cell('bcap_4x')
    laygen.sel_cell('bcap_4x')
    generate_bcap(laygen, objectname_pfix='DCAP0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                  devname_nmos_boundary='nmos4_fast_boundary',
                  devname_nmos_body='nmos4_fast_center_nf2',
                  devname_pmos_boundary='pmos4_fast_boundary',
                  devname_pmos_space='pmos4_fast_space',
                  m=4, origin=np.array([0,0]), create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('bcap_8x')
    laygen.sel_cell('bcap_8x')
    generate_bcap(laygen, objectname_pfix='DCAP0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                  devname_nmos_boundary='nmos4_fast_boundary',
                  devname_nmos_body='nmos4_fast_center_nf2',
                  devname_pmos_boundary='pmos4_fast_boundary',
                  devname_pmos_space='pmos4_fast_space',
                  m=8, origin=np.array([0,0]), create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('bcap2_8x')
    laygen.sel_cell('bcap2_8x')
    generate_bcap2(laygen, objectname_pfix='BCAP0', placement_grid=pg, 
                  routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                  devname_nmos_boundary='nmos4_fast_boundary',
                  devname_nmos_body='nmos4_fast_center_nf2',
                  devname_pmos_boundary='pmos4_fast_boundary',
                  devname_pmos_body='pmos4_fast_center_nf2',
                  m=8, origin=np.array([0,0]), create_pin=True)
    laygen.add_template_from_cell()


    laygen.add_cell('dcap_2x')
    laygen.sel_cell('dcap_2x')
    generate_dcap(laygen, objectname_pfix='DCAP0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                  devname_nmos_boundary='nmos4_fast_boundary',
                  devname_nmos_body='nmos4_fast_center_nf2',
                  devname_pmos_boundary='pmos4_fast_boundary',
                  devname_pmos_space='pmos4_fast_dmy_nf2',
                  m=2, origin=np.array([0,0]), create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('dcap_4x')
    laygen.sel_cell('dcap_4x')
    generate_dcap(laygen, objectname_pfix='DCAP0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                  devname_nmos_boundary='nmos4_fast_boundary',
                  devname_nmos_body='nmos4_fast_center_nf2',
                  devname_pmos_boundary='pmos4_fast_boundary',
                  devname_pmos_space='pmos4_fast_dmy_nf2',
                  m=4, origin=np.array([0,0]), create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('dcap_8x')
    laygen.sel_cell('dcap_8x')
    generate_dcap(laygen, objectname_pfix='DCAP0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                  devname_nmos_boundary='nmos4_fast_boundary',
                  devname_nmos_body='nmos4_fast_center_nf2',
                  devname_pmos_boundary='pmos4_fast_boundary',
                  devname_pmos_space='pmos4_fast_dmy_nf2',
                  m=8, origin=np.array([0,0]), create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('dcap2_4x')
    laygen.sel_cell('dcap2_4x')
    generate_dcap2(laygen, objectname_pfix='DCAP0', placement_grid=pg, 
                  routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                  devname_nmos_boundary='nmos4_fast_boundary',
                  devname_nmos_body='nmos4_fast_center_nf2',
                  devname_pmos_boundary='pmos4_fast_boundary',
                  devname_pmos_body='pmos4_fast_center_nf2',
                  m=4, origin=np.array([0,0]), create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('dcap2_8x')
    laygen.sel_cell('dcap2_8x')
    generate_dcap2(laygen, objectname_pfix='DCAP0', placement_grid=pg, 
                  routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                  devname_nmos_boundary='nmos4_fast_boundary',
                  devname_nmos_body='nmos4_fast_center_nf2',
                  devname_pmos_boundary='pmos4_fast_boundary',
                  devname_pmos_body='pmos4_fast_center_nf2',
                  m=8, origin=np.array([0,0]), create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('dcap3_8x')
    laygen.sel_cell('dcap3_8x')
    generate_dcap3(laygen, objectname_pfix='DCAP0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                  devname_nmos_boundary='nmos4_fast_boundary',
                  devname_nmos_body='nmos4_fast_center_nf2',
                  devname_pmos_boundary='pmos4_fast_boundary',
                  devname_pmos_space='pmos4_fast_dmy_nf2',
                  m=8, origin=np.array([0,0]), create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('tie_2x')
    laygen.sel_cell('tie_2x')
    generate_tie(laygen, objectname_pfix='TIE0',
                 placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                 routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                 devname_nmos_boundary='nmos4_fast_boundary',
                 devname_nmos_body='nmos4_fast_center_nf2',
                 devname_pmos_boundary='pmos4_fast_boundary',
                 devname_pmos_body='pmos4_fast_center_nf2', m=2, create_pin=True
                 )
    laygen.add_template_from_cell()

    laygen.add_cell('tie_wovdd_2x')
    laygen.sel_cell('tie_wovdd_2x')
    generate_tie_wovdd(laygen, objectname_pfix='TIE0',
                 placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                 routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                 devname_nmos_boundary='nmos4_fast_boundary',
                 devname_nmos_body='nmos4_fast_center_nf2',
                 m=2, create_pin=True
                 )
    laygen.add_template_from_cell()

    laygen.add_cell('inv_1x')
    laygen.sel_cell('inv_1x')
    generate_inv_1x(laygen, objectname_pfix='INV0',
                    placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                    routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                    devname_nmos_boundary='nmos4_fast_boundary',
                    devname_nmos_body='nmos4_fast_center_nf1_left',
                    devname_nmos_space='nmos4_fast_space',
                    devname_pmos_boundary='pmos4_fast_boundary',
                    devname_pmos_body='pmos4_fast_center_nf1_left',
                    devname_pmos_space='pmos4_fast_space',
                    create_pin=True
                    )
    laygen.add_template_from_cell()

    laygen.add_cell('inv_2x')
    laygen.sel_cell('inv_2x')
    generate_inv(laygen, objectname_pfix='INV0',
                 placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                 routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                 devname_nmos_boundary='nmos4_fast_boundary',
                 devname_nmos_body='nmos4_fast_center_nf2',
                 devname_pmos_boundary='pmos4_fast_boundary',
                 devname_pmos_body='pmos4_fast_center_nf2',
                 m=2, create_pin=True
                 )
    laygen.add_template_from_cell()

    laygen.add_cell('inv_4x')
    laygen.sel_cell('inv_4x')
    generate_inv(laygen, objectname_pfix='INV0',
                 placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin,
                 routing_grid_m2m3_pin=rg_m2m3_pin,
                 devname_nmos_boundary='nmos4_fast_boundary',
                 devname_nmos_body='nmos4_fast_center_nf2',
                 devname_pmos_boundary='pmos4_fast_boundary',
                 devname_pmos_body='pmos4_fast_center_nf2',
                 m=4, create_pin=True
                 )
    laygen.add_template_from_cell()

    laygen.add_cell('inv_6x')
    laygen.sel_cell('inv_6x')
    generate_inv(laygen, objectname_pfix='INV0',
                 placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin,
                 routing_grid_m2m3_pin=rg_m2m3_pin,
                 devname_nmos_boundary='nmos4_fast_boundary',
                 devname_nmos_body='nmos4_fast_center_nf2',
                 devname_pmos_boundary='pmos4_fast_boundary',
                 devname_pmos_body='pmos4_fast_center_nf2',
                 m=6, create_pin=True
                 )
    laygen.add_template_from_cell()

    laygen.add_cell('inv_8x')
    laygen.sel_cell('inv_8x')
    generate_inv(laygen, objectname_pfix='INV0',
                 placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin,
                 routing_grid_m2m3_pin=rg_m2m3_pin,
                 devname_nmos_boundary='nmos4_fast_boundary',
                 devname_nmos_body='nmos4_fast_center_nf2',
                 devname_pmos_boundary='pmos4_fast_boundary',
                 devname_pmos_body='pmos4_fast_center_nf2',
                 m=8, create_pin=True
                 )
    laygen.add_template_from_cell()

    laygen.add_cell('inv_10x')
    laygen.sel_cell('inv_10x')
    generate_inv(laygen, objectname_pfix='INV0',
                 placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin,
                 routing_grid_m2m3_pin=rg_m2m3_pin,
                 devname_nmos_boundary='nmos4_fast_boundary',
                 devname_nmos_body='nmos4_fast_center_nf2',
                 devname_pmos_boundary='pmos4_fast_boundary',
                 devname_pmos_body='pmos4_fast_center_nf2',
                 m=10, create_pin=True
                 )
    laygen.add_template_from_cell()

    laygen.add_cell('inv_16x')
    laygen.sel_cell('inv_16x')
    generate_inv(laygen, objectname_pfix='INV0',
                 placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin,
                 routing_grid_m2m3_pin=rg_m2m3_pin,
                 devname_nmos_boundary='nmos4_fast_boundary',
                 devname_nmos_body='nmos4_fast_center_nf2',
                 devname_pmos_boundary='pmos4_fast_boundary',
                 devname_pmos_body='pmos4_fast_center_nf2',
                 m=16, create_pin=True
                 )
    laygen.add_template_from_cell()

    laygen.add_cell('inv_24x')
    laygen.sel_cell('inv_24x')
    generate_inv(laygen, objectname_pfix='INV0',
                 placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin,
                 routing_grid_m2m3_pin=rg_m2m3_pin,
                 devname_nmos_boundary='nmos4_fast_boundary',
                 devname_nmos_body='nmos4_fast_center_nf2',
                 devname_pmos_boundary='pmos4_fast_boundary',
                 devname_pmos_body='pmos4_fast_center_nf2',
                 m=24, create_pin=True
                 )
    laygen.add_template_from_cell()

    laygen.add_cell('inv_32x')
    laygen.sel_cell('inv_32x')
    generate_inv(laygen, objectname_pfix='INV0',
                 placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin,
                 routing_grid_m2m3_pin=rg_m2m3_pin,
                 devname_nmos_boundary='nmos4_fast_boundary',
                 devname_nmos_body='nmos4_fast_center_nf2',
                 devname_pmos_boundary='pmos4_fast_boundary',
                 devname_pmos_body='pmos4_fast_center_nf2',
                 m=32, create_pin=True
                 )
    laygen.add_template_from_cell()

    laygen.add_cell('tgate_2x')
    laygen.sel_cell('tgate_2x')
    generate_tgate(laygen, objectname_pfix='TG0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   devname_pmos_boundary='pmos4_fast_boundary',
                   devname_pmos_body='pmos4_fast_center_nf2',
                   devname_pmos_space='pmos4_fast_space',
                   m=2, create_pin=True
                   )
    laygen.add_template_from_cell()

    laygen.add_cell('tgate_4x')
    laygen.sel_cell('tgate_4x')
    generate_tgate(laygen, objectname_pfix='TG0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   devname_pmos_boundary='pmos4_fast_boundary',
                   devname_pmos_body='pmos4_fast_center_nf2',
                   devname_pmos_space='pmos4_fast_space',
                   m=4, create_pin=True
                   )
    laygen.add_template_from_cell()

    laygen.add_cell('tgate_8x')
    laygen.sel_cell('tgate_8x')
    generate_tgate(laygen, objectname_pfix='TG0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   devname_pmos_boundary='pmos4_fast_boundary',
                   devname_pmos_body='pmos4_fast_center_nf2',
                   devname_pmos_space='pmos4_fast_space',
                   m=8, create_pin=True
                   )
    laygen.add_template_from_cell()

    laygen.add_cell('nsw_2x')
    laygen.sel_cell('nsw_2x')
    generate_nsw(laygen, objectname_pfix='NSW0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   devname_pmos_boundary='pmos4_fast_boundary',
                   devname_pmos_body='pmos4_fast_center_nf2',
                   devname_pmos_space='pmos4_fast_space',
                   m=2, create_pin=True
                   )
    laygen.add_template_from_cell()

    laygen.add_cell('nsw_4x')
    laygen.sel_cell('nsw_4x')
    generate_nsw(laygen, objectname_pfix='NSW0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   devname_pmos_boundary='pmos4_fast_boundary',
                   devname_pmos_body='pmos4_fast_center_nf2',
                   devname_pmos_space='pmos4_fast_space',
                   m=4, create_pin=True
                   )
    laygen.add_template_from_cell()

    laygen.add_cell('nsw_8x')
    laygen.sel_cell('nsw_8x')
    generate_nsw(laygen, objectname_pfix='NSW0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   devname_pmos_boundary='pmos4_fast_boundary',
                   devname_pmos_body='pmos4_fast_center_nf2',
                   devname_pmos_space='pmos4_fast_space',
                   m=8, create_pin=True
                   )
    laygen.add_template_from_cell()

    laygen.add_cell('nsw_12x')
    laygen.sel_cell('nsw_12x')
    generate_nsw(laygen, objectname_pfix='NSW0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   devname_pmos_boundary='pmos4_fast_boundary',
                   devname_pmos_body='pmos4_fast_center_nf2',
                   devname_pmos_space='pmos4_fast_space',
                   m=12, create_pin=True
                   )
    laygen.add_template_from_cell()

    laygen.add_cell('nsw_16x')
    laygen.sel_cell('nsw_16x')
    generate_nsw(laygen, objectname_pfix='NSW0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   devname_pmos_boundary='pmos4_fast_boundary',
                   devname_pmos_body='pmos4_fast_center_nf2',
                   devname_pmos_space='pmos4_fast_space',
                   m=16, create_pin=True
                   )
    laygen.add_template_from_cell()

    laygen.add_cell('nsw_wovdd_2x')
    laygen.sel_cell('nsw_wovdd_2x')
    generate_nsw_wovdd(laygen, objectname_pfix='NSW0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   m=2, create_pin=True
                   )
    laygen.add_template_from_cell()

    laygen.add_cell('nsw_wovdd_4x')
    laygen.sel_cell('nsw_wovdd_4x')
    generate_nsw_wovdd(laygen, objectname_pfix='NSW0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   m=4, create_pin=True
                   )
    laygen.add_template_from_cell()

    laygen.add_cell('nsw_wovdd_8x')
    laygen.sel_cell('nsw_wovdd_8x')
    generate_nsw_wovdd(laygen, objectname_pfix='NSW0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   m=8, create_pin=True
                   )
    laygen.add_template_from_cell()

    laygen.add_cell('nsw_wovdd_12x')
    laygen.sel_cell('nsw_wovdd_12x')
    generate_nsw_wovdd(laygen, objectname_pfix='NSW0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   m=12, create_pin=True
                   )
    laygen.add_template_from_cell()

    laygen.add_cell('nsw_wovdd_16x')
    laygen.sel_cell('nsw_wovdd_16x')
    generate_nsw_wovdd(laygen, objectname_pfix='NSW0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   m=16, create_pin=True
                   )
    laygen.add_template_from_cell()

    laygen.add_cell('nand_1x')
    laygen.sel_cell('nand_1x')
    generate_nand_1x(laygen, objectname_pfix='ND0',
                     placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin,
                     routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body_2stack='nmos4_fast_center_2stack',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body_left='pmos4_fast_center_nf1_left',
                     devname_pmos_body_right='pmos4_fast_center_nf1_right',
                     create_pin=True
                     )
    laygen.add_template_from_cell()

    laygen.add_cell('nor_2x')
    laygen.sel_cell('nor_2x')
    generate_nor(laygen, objectname_pfix='NR0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                  routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                  devname_nmos_boundary='nmos4_fast_boundary',
                  devname_nmos_body='nmos4_fast_center_nf2',
                  devname_pmos_boundary='pmos4_fast_boundary',
                  devname_pmos_body='pmos4_fast_center_nf2',
                  m=2, create_pin=True
                  )
    laygen.add_template_from_cell()

    laygen.add_cell('nor_4x')
    laygen.sel_cell('nor_4x')
    generate_nor(laygen, objectname_pfix='NR0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                  routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                  devname_nmos_boundary='nmos4_fast_boundary',
                  devname_nmos_body='nmos4_fast_center_nf2',
                  devname_pmos_boundary='pmos4_fast_boundary',
                  devname_pmos_body='pmos4_fast_center_nf2',
                  m=4, create_pin=True
                  )
    laygen.add_template_from_cell()

    laygen.add_cell('nor_8x')
    laygen.sel_cell('nor_8x')
    generate_nor(laygen, objectname_pfix='NR0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                     routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body='nmos4_fast_center_nf2',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body='pmos4_fast_center_nf2',
                     m=8, create_pin=True
                     )
    laygen.add_template_from_cell()

    laygen.add_cell('nand_2x')
    laygen.sel_cell('nand_2x')
    generate_nand(laygen, objectname_pfix='ND0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                  routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                  devname_nmos_boundary='nmos4_fast_boundary',
                  devname_nmos_body='nmos4_fast_center_nf2',
                  devname_pmos_boundary='pmos4_fast_boundary',
                  devname_pmos_body='pmos4_fast_center_nf2',
                  m=2, create_pin=True
                  )
    laygen.add_template_from_cell()

    laygen.add_cell('nand_4x')
    laygen.sel_cell('nand_4x')
    generate_nand(laygen, objectname_pfix='ND0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                  routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                  devname_nmos_boundary='nmos4_fast_boundary',
                  devname_nmos_body='nmos4_fast_center_nf2',
                  devname_pmos_boundary='pmos4_fast_boundary',
                  devname_pmos_body='pmos4_fast_center_nf2',
                  m=4, create_pin=True
                  )
    laygen.add_template_from_cell()

    laygen.add_cell('nand_8x')
    laygen.sel_cell('nand_8x')
    generate_nand(laygen, objectname_pfix='ND0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                     routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body='nmos4_fast_center_nf2',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body='pmos4_fast_center_nf2',
                     m=8, create_pin=True
                     )
    laygen.add_template_from_cell()

    laygen.add_cell('nand_16x')
    laygen.sel_cell('nand_16x')
    generate_nand(laygen, objectname_pfix='ND0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                     routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body='nmos4_fast_center_nf2',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body='pmos4_fast_center_nf2',
                     m=16, create_pin=True
                     )
    laygen.add_template_from_cell()

    laygen.add_cell('tinv_1x')
    laygen.sel_cell('tinv_1x')
    generate_tinv_1x(laygen, objectname_pfix='TINV0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                     routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body_2stack='nmos4_fast_center_2stack',
                     devname_nmos_space='nmos4_fast_space',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body_2stack='pmos4_fast_center_2stack',
                     devname_pmos_space='pmos4_fast_space',
                     pin_i_abut='pmos', create_pin=True
                     )
    laygen.add_template_from_cell()

    laygen.add_cell('tinv_small_1x')
    laygen.sel_cell('tinv_small_1x')
    generate_tinv_small_1x(laygen, objectname_pfix='TINV0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                     routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body_2stack='nmos4_fast_center_2stack',
                     devname_nmos_space='nmos4_fast_space',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body_2stack='pmos4_fast_center_2stack',
                     devname_pmos_space='pmos4_fast_space',
                     pin_i_abut='pmos', create_pin=True
                     )
    laygen.add_template_from_cell()

    laygen.add_cell('tinv_2x')
    laygen.sel_cell('tinv_2x')
    generate_tinv(laygen, objectname_pfix='TINV0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                     routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body='nmos4_fast_center_nf2',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body='pmos4_fast_center_nf2',
                     m=2, create_pin=True
                     )
    laygen.add_template_from_cell()

    laygen.add_cell('tinv_4x')
    laygen.sel_cell('tinv_4x')
    generate_tinv(laygen, objectname_pfix='TINV0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                     routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body='nmos4_fast_center_nf2',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body='pmos4_fast_center_nf2',
                     m=4, create_pin=True
                     )
    laygen.add_template_from_cell()

    laygen.add_cell('tinv_8x')
    laygen.sel_cell('tinv_8x')
    generate_tinv(laygen, objectname_pfix='TINV0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                     routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body='nmos4_fast_center_nf2',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body='pmos4_fast_center_nf2',
                     m=8, create_pin=True
                     )
    laygen.add_template_from_cell()

    laygen.add_cell('mux2to1_1x')
    laygen.sel_cell('mux2to1_1x')
    generate_mux2to1_1x(laygen, objectname_pfix='MUX2TO10', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                        routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                        devname_nmos_boundary='nmos4_fast_boundary',
                        devname_nmos_body_2stack='nmos4_fast_center_2stack',
                        #devname_nmos_body_left='nmos4_fast_center_nf1_left',
                        #devname_nmos_body_right='nmos4_fast_center_nf1_right',
                        devname_pmos_boundary='pmos4_fast_boundary',
                        devname_pmos_body_2stack='pmos4_fast_center_2stack',
                        #devname_pmos_body_left='pmos4_fast_center_nf1_left',
                        #devname_pmos_body_right='pmos4_fast_center_nf1_right',
                        create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('mux2to1_2x')
    laygen.sel_cell('mux2to1_2x')
    generate_mux2to1(laygen, objectname_pfix='MUX2TO10', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                     routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                     routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body='nmos4_fast_center_nf2',
                     devname_nmos_space='nmos4_fast_space',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body='pmos4_fast_center_nf2',
                     devname_pmos_space='pmos4_fast_space',
                     m=2, create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('mux2to1_4x')
    laygen.sel_cell('mux2to1_4x')
    generate_mux2to1(laygen, objectname_pfix='TINV0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                     routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                     routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body='nmos4_fast_center_nf2',
                     devname_nmos_space='nmos4_fast_space',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body='pmos4_fast_center_nf2',
                     devname_pmos_space='pmos4_fast_space',
                     m=4, create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('mux2to1_8x')
    laygen.sel_cell('mux2to1_8x')
    generate_mux2to1(laygen, objectname_pfix='TINV0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                     routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                     routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body='nmos4_fast_center_nf2',
                     devname_nmos_space='nmos4_fast_space',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body='pmos4_fast_center_nf2',
                     devname_pmos_space='pmos4_fast_space',
                     m=8, create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('latch_2ck_1x')
    laygen.sel_cell('latch_2ck_1x')
    laygen.templates.sel_library(workinglib)
    generate_latch_2ck(laygen, objectname_pfix='LATCH0', placement_grid=pg,
                   routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                   origin=np.array([0, 0]), m=1, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('latch_2ck_2x')
    laygen.sel_cell('latch_2ck_2x')
    laygen.templates.sel_library(workinglib)
    generate_latch_2ck(laygen, objectname_pfix='LATCH0', placement_grid=pg,
                   routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                   origin=np.array([0, 0]), m=2, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('latch_2ck_4x')
    laygen.sel_cell('latch_2ck_4x')
    laygen.templates.sel_library(workinglib)
    generate_latch_2ck(laygen, objectname_pfix='LATCH0', placement_grid=pg,
                   routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                   origin=np.array([0, 0]), m=4, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('latch_2ck_8x')
    laygen.sel_cell('latch_2ck_8x')
    laygen.templates.sel_library(workinglib)
    generate_latch_2ck(laygen, objectname_pfix='LATCH0', placement_grid=pg,
                   routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                   origin=np.array([0, 0]), m=8, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('latch_2ck_rstbh_2x')
    laygen.sel_cell('latch_2ck_rstbh_2x')
    laygen.templates.sel_library(workinglib)
    generate_latch_2ck_rstbh(laygen, objectname_pfix='LATCH0', placement_grid=pg,
                   routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                   origin=np.array([0, 0]), m=2, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('latch_2ck_rstbh_4x')
    laygen.sel_cell('latch_2ck_rstbh_4x')
    laygen.templates.sel_library(workinglib)
    generate_latch_2ck_rstbh(laygen, objectname_pfix='LATCH0', placement_grid=pg,
                   routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                   origin=np.array([0, 0]), m=4, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('dff_1x')
    laygen.sel_cell('dff_1x')
    laygen.templates.sel_library(workinglib)
    generate_dff(laygen, objectname_pfix='DFF0', placement_grid=pg,
                 routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                 origin=np.array([0, 0]), m=1, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('dff_2x')
    laygen.sel_cell('dff_2x')
    laygen.templates.sel_library(workinglib)
    generate_dff(laygen, objectname_pfix='DFF0', placement_grid=pg,
                 routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                 origin=np.array([0, 0]), m=2, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('dff_4x')
    laygen.sel_cell('dff_4x')
    laygen.templates.sel_library(workinglib)
    generate_dff(laygen, objectname_pfix='DFF0', placement_grid=pg,
                 routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                 origin=np.array([0, 0]), m=4, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('dff_rsth_1x')
    laygen.sel_cell('dff_rsth_1x')
    laygen.templates.sel_library(workinglib)
    generate_dff_rsth(laygen, objectname_pfix='DFF0', placement_grid=pg,
                 routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                 origin=np.array([0, 0]), m=1, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('dff_rsth_2x')
    laygen.sel_cell('dff_rsth_2x')
    laygen.templates.sel_library(workinglib)
    generate_dff_rsth(laygen, objectname_pfix='DFF0', placement_grid=pg,
                 routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                 origin=np.array([0, 0]), m=2, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('dff_rsth_4x')
    laygen.sel_cell('dff_rsth_4x')
    laygen.templates.sel_library(workinglib)
    generate_dff_rsth(laygen, objectname_pfix='DFF0', placement_grid=pg,
                 routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                 origin=np.array([0, 0]), m=4, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('oai22_1x')
    laygen.sel_cell('oai22_1x')
    generate_oai22_1x(laygen, objectname_pfix='OAI0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                      routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                      devname_nmos_boundary='nmos4_fast_boundary',
                      devname_nmos_body_left='nmos4_fast_center_nf1_left',
                      devname_nmos_body_right='nmos4_fast_center_nf1_right',
                      devname_pmos_boundary='pmos4_fast_boundary',
                      devname_pmos_body_2stack='pmos4_fast_center_2stack',
                      origin=np.array([0, 0]), create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('oai22_skewed_1x')
    laygen.sel_cell('oai22_skewed_1x')
    generate_oai22_skewed_1x(laygen, objectname_pfix='OAI0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                      routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                      devname_nmos_boundary='nmos4_fast_boundary',
                      devname_nmos_body_left='nmos4_fast_center_nf1_left',
                      devname_nmos_body_right='nmos4_fast_center_nf1_right',
                      devname_nmos_space='nmos4_fast_space',
                      devname_pmos_boundary='pmos4_fast_boundary',
                      devname_pmos_body_2stack='pmos4_fast_center_2stack',
                      origin=np.array([0, 0]), create_pin=True)
    laygen.add_template_from_cell()

    laygen.add_cell('ndsr_1x')
    laygen.sel_cell('ndsr_1x')
    laygen.templates.sel_library(workinglib)
    generate_ndsr(laygen, objectname_pfix='NDSR0', placement_grid=pg,
                   routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                   origin=np.array([0, 0]), m=1, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('ndsr_2x')
    laygen.sel_cell('ndsr_2x')
    laygen.templates.sel_library(workinglib)
    generate_ndsr(laygen, objectname_pfix='NDSR0', placement_grid=pg,
                   routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                   origin=np.array([0, 0]), m=2, create_pin=True)
    laygen.templates.sel_library(utemplib)
    laygen.add_template_from_cell()


    laygen.save_template(filename=workinglib+'.yaml', libname=workinglib)

    #bag export, if bag does not exist, gds export
    mycell_list=['space_1x', 'space_2x', 'space_4x',
                 'space_wovdd_1x', 'space_wovdd_2x', 'space_wovdd_4x',
                 'tap', 'tap_float', 'tap_wovdd', 'tie_2x', 'tie_wovdd_2x', 
                 'bcap_4x', 'bcap_8x',
                 'dcap_2x', 'dcap_4x', 'dcap_8x',
                 'dcap2_4x', 'dcap2_8x',
                 'dcap3_8x',
                 'bcap2_8x',
                 'inv_1x', 'inv_2x', 'inv_4x', 'inv_6x', 'inv_8x', 'inv_10x', 'inv_16x', 'inv_24x', 'inv_32x',
                 'tgate_2x', 'tgate_4x', 'tgate_8x',
                 'nsw_2x', 'nsw_4x', 'nsw_8x', 'nsw_12x', 'nsw_16x',
                 'nsw_wovdd_2x', 'nsw_wovdd_4x', 'nsw_wovdd_8x', 'nsw_wovdd_12x', 'nsw_wovdd_16x',
                 'tinv_1x', 'tinv_small_1x', 'tinv_2x', 'tinv_4x', 'tinv_8x',
                 'nand_1x', 'nand_2x', 'nand_4x', 'nand_8x', 'nand_16x',
                 'nor_2x', 'nor_4x', 'nor_8x',
                 'latch_2ck_1x', 'latch_2ck_2x', 'latch_2ck_4x', 'latch_2ck_8x',
                 'latch_2ck_rstbh_2x', 'latch_2ck_rstbh_4x',
                 'dff_1x', 'dff_2x', 'dff_4x',
                 'dff_rsth_1x', 'dff_rsth_2x', 'dff_rsth_4x',
                 'oai22_1x', 'oai22_skewed_1x',
                 'ndsr_1x', 'ndsr_2x',
                 'mux2to1_1x', 'mux2to1_2x', 'mux2to1_4x', 'mux2to1_8x',
                 ]

    #Zhongkai's cells
    tgate_dn_size = [2, 4, 8, 16, 18, 24]
    pull_dn_size = 4
    for m in tgate_dn_size:
        laygen.add_cell('tgate_dn_'+str(m)+'x')
        laygen.sel_cell('tgate_dn_'+str(m)+'x')
        generate_tgate_dn(laygen, objectname_pfix='TG0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   devname_pmos_boundary='pmos4_fast_boundary',
                   devname_pmos_body='pmos4_fast_center_nf2',
                   devname_pmos_space='pmos4_fast_space',
                   m=m, n= pull_dn_size, create_pin=True
                   )
        laygen.add_template_from_cell()
        mycell_list.append('tgate_dn_'+str(m)+'x')
    
    #cap_sw
    cap_sw_size = [2, 4, 8, 16, 32]
    for m in cap_sw_size:
        laygen.add_cell('cap_sw_'+str(m)+'x')
        laygen.sel_cell('cap_sw_'+str(m)+'x')
        generate_cap_sw(laygen, objectname_pfix='CSW0',
                   placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
                   routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                   devname_nmos_boundary='nmos4_fast_boundary',
                   devname_nmos_body='nmos4_fast_center_nf2',
                   devname_nmos_space='nmos4_fast_space',
                   devname_pmos_boundary='pmos4_fast_boundary',
                   devname_pmos_body='pmos4_fast_center_nf2',
                   devname_pmos_space='pmos4_fast_space',
                   m=m, create_pin=True
                   )
        laygen.add_template_from_cell()
        mycell_list.append('cap_sw_'+str(m)+'x')  

    inv_size = [6, 8, 36, 40, 50, 64, 100]
    for m in inv_size:
        laygen.add_cell('inv_'+str(m)+'x')
        laygen.sel_cell('inv_'+str(m)+'x')
        generate_inv(laygen, objectname_pfix='INV0',
                 placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin,
                 routing_grid_m2m3_pin=rg_m2m3_pin,
                 devname_nmos_boundary='nmos4_fast_boundary',
                 devname_nmos_body='nmos4_fast_center_nf2',
                 devname_pmos_boundary='pmos4_fast_boundary',
                 devname_pmos_body='pmos4_fast_center_nf2',
                 m=m, create_pin=True
                 )
        laygen.add_template_from_cell()
        mycell_list.append('inv_'+str(m)+'x')  
       
    #latch
    latch_2ck_strstbh_size = [1, 2, 4, 8]
    for m in latch_2ck_strstbh_size:
        laygen.add_cell('latch_2ck_strstbh_'+str(m)+'x')
        laygen.sel_cell('latch_2ck_strstbh_'+str(m)+'x')
        laygen.templates.sel_library(workinglib)
        generate_latch_2ck_strstbh(laygen, objectname_pfix='LATCH0', placement_grid=pg,
                   routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                   origin=np.array([0, 0]), m=m, create_pin=True)
        laygen.templates.sel_library(utemplib)
        laygen.add_template_from_cell()
        mycell_list.append('latch_2ck_strstbh_'+str(m)+'x')


    #dff
    dff_strsth_size = [1, 2, 4, 8]
    for m in dff_strsth_size:
        laygen.add_cell('dff_strsth_'+str(m)+'x')
        laygen.sel_cell('dff_strsth_'+str(m)+'x')
        laygen.templates.sel_library(workinglib)
        generate_dff_strsth(laygen, objectname_pfix='DFF0', placement_grid=pg,
                 routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                 origin=np.array([0, 0]), m=m, create_pin=True)
        laygen.templates.sel_library(utemplib)
        laygen.add_template_from_cell()
        mycell_list.append('dff_strsth_'+str(m)+'x')

    #dff_clkb
    dff_strsth_clkb_size = [1, 2, 4, 8]
    for m in dff_strsth_clkb_size:
        laygen.add_cell('dff_strsth_ckb_'+str(m)+'x')
        laygen.sel_cell('dff_strsth_ckb_'+str(m)+'x')
        laygen.templates.sel_library(workinglib)
        generate_dff_strsth_ckb(laygen, objectname_pfix='DFF0', placement_grid=pg,
                 routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                 origin=np.array([0, 0]), m=m, create_pin=True)
        laygen.templates.sel_library(utemplib)
        laygen.add_template_from_cell()
        mycell_list.append('dff_strsth_ckb_'+str(m)+'x')

    #end Zhongkai's cells

    laygen.save_template(filename=workinglib+'.yaml', libname=workinglib)


    import imp
    try:
        imp.find_module('bag')
        import bag
        prj = bag.BagProject()
        for mycell in mycell_list:
            laygen.sel_cell(mycell)
            laygen.export_BAG(prj, array_delimiter=['[', ']'])
    except ImportError:
        laygen.export_GDS('output.gds', cellname=mycell_list, layermapfile=tech+".layermap")  # change layermapfile





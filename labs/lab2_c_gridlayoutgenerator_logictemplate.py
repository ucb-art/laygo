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

"""Lab2: generate couple of logic templates on abstract grid
   1. Copy this file to working directory
   2. For GDS export, prepare layermap file
"""
import laygo
import numpy as np
#import logging;logging.basicConfig(level=logging.DEBUG)

def create_io_pin(laygen, layer, gridname, pinname_list, rect_list, offset_y=np.array([-1, 1])):
    """create digital io pin"""
    rect_xy_list = [laygen.get_xy(obj =r, gridname=gridname, sort=True) for r in rect_list]
    #align pins
    ry = rect_xy_list[0][:, 1] + offset_y.T
    for i, xy_rect in enumerate(rect_xy_list):
        xy_rect[:, 1]=ry
        laygen.pin(name=pinname_list[i], layer=layer, xy=xy_rect, gridname=gridname)

def create_power_pin(laygen, layer, gridname, rect_vdd, rect_vss, pinname_vdd='VDD', pinname_vss='VSS'):
    """create power pin"""
    laygen.pin(name=pinname_vdd, layer=layer, refobj=rect_vdd, gridname=gridname)
    laygen.pin(name=pinname_vss, layer=layer, refobj=rect_vss, gridname=gridname)

def generate_inv(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m2m3_pin,
                 devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_body, m=2,
                 origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m2m3_pin = routing_grid_m2m3_pin
    m = max(1, int(m / 2))  # using nf=2 devices

    # placement
    in0, in1, in2 = laygen.relplace(name=['I'+objectname_pfix + 'N' + str(i) for i in range(3)],
                           templatename=[devname_nmos_boundary,devname_nmos_body,devname_nmos_boundary],
                           xy=[origin, [0, 0], [0, 0]], shape=[[1, 1], [m, 1], [1, 1]], gridname=pg)
    ip0, ip1, ip2 = laygen.relplace(name=['I'+objectname_pfix + 'P' + str(i) for i in range(3)],
                           templatename=[devname_pmos_boundary,devname_pmos_body,devname_pmos_boundary],
                           shape=[[1, 1], [m, 1], [1, 1]], gridname=pg, refinstname=in0.name,
                           direction=['top','left','left'], transform='MX')
    # route
    # input
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=[i, 0], via0=[[0, 0]],
                     refinstname1=ip1.name, refpinname1='G0', refinstindex1=[i, 0])
    r0, ri0 = laygen.route_hv(layerh=laygen.layers['metal'][2], layerv=laygen.layers['metal'][3], xy0=[1,0], xy1=[-1,2],
                              gridname0=rg_m2m3, refinstname0=in1.name, refinstname1=in1.name, refinstindex0=[m-1, 0],
                              endstyle0=['extend', 'truncate'], endstyle1=['extend', 'truncate'], refpinname0='G0',
                              refpinname1='G0')
    # output
    laygen.route(None, laygen.layers['metal'][2], xy0=[-1, 0], xy1=[1, 0], gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0', refinstindex0=[0, 0], endstyle0="extend",
                 refinstname1=in1.name, refpinname1='D0', refinstindex1=[m-1, 0], endstyle1="extend")
    laygen.route(None, laygen.layers['metal'][2], xy0=[-1, 0], xy1=[1, 0], gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='D0', refinstindex0=[0, 0], endstyle0="extend",
                 refinstname1=ip1.name, refpinname1='D0', refinstindex1=[m-1, 0], endstyle1="extend")
    for i in range(m):
        laygen.via(None, xy=[0, 0], refinstname=in1.name, refpinname='D0', refinstindex=[i, 0], gridname=rg_m1m2)
        laygen.via(None, xy=[0, 0], refinstname=ip1.name, refpinname='D0', refinstindex=[i, 0], gridname=rg_m1m2)
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=[0, 0], xy1=[0, 0], gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstindex0=[m-1, 0], via0=[[0, 0]],
                       refinstname1=ip1.name, refpinname1='D0', refinstindex1=[m-1, 0], via1=[[0, 0]])
    # power and groud rail
    xy = laygen.get_xy(obj = in2.template, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=[0, 0], xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip2.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=[0, 0], xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in2.name)
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=np.array([m-1, 0]), via0=[[0, 0]],
                 refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=ip1.name, refinstindex0=np.array([m-1, 0]), via0=[[0, 0]],
                 refinstname1=ip1.name, refinstindex1=np.array([m-1, 0]))
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin, pinname_list = ['I', 'O'],
                      rect_list=[ri0, ro0])
        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], refobj=rvdd, gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], refobj=rvss, gridname=rg_m1m2)

def generate_tinv(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m2m3_pin,
                  devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_body, m=2,
                  origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m2m3_pin = routing_grid_m2m3_pin
    m = max(1, int(m / 2))  # using nf=2 devices

    # placement
    in0, in1, in2 = laygen.relplace(name=['I'+objectname_pfix + 'N' + str(i) for i in range(3)],
                           templatename=[devname_nmos_boundary, devname_nmos_body, devname_nmos_boundary],
                           xy=[origin, [0, 0], [0, 0], [0, 0]], shape=[[1, 1], [m, 1], [1, 1]], gridname=pg)
    in3, in4, in5 = laygen.relplace(name=['I'+objectname_pfix + 'N' + str(i) for i in range(3, 6)],
                           templatename=[devname_nmos_boundary, devname_nmos_body, devname_nmos_boundary],
                           shape=[[1, 1], [m, 1], [1, 1]], gridname=pg, refinstname=in2.name)
    ip0, ip1, ip2 = laygen.relplace(name=['I'+objectname_pfix + 'P' + str(i) for i in range(3)],
                           templatename=[devname_pmos_boundary, devname_pmos_body, devname_pmos_boundary],
                           shape=[[1, 1], [m, 1], [1, 1]], gridname=pg, refinstname=in0.name,
                           direction=['top','left','left'], transform='MX')
    ip3, ip4, ip5 = laygen.relplace(name=['I'+objectname_pfix + 'P' + str(i) for i in range(3, 6)],
                           templatename=[devname_pmos_boundary, devname_pmos_body, devname_pmos_boundary],
                           shape=[[1, 1], [m, 1], [1, 1]], gridname=pg, refinstname=ip2.name,
                           transform='MX')
    # route
    # input
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=[i, 0], via0=[[0, 0]],
                     refinstname1=ip1.name, refpinname1='G0', refinstindex1=[i, 0])
    r0, ri0 = laygen.route_hv(layerh=laygen.layers['metal'][2], layerv=laygen.layers['metal'][3], xy0=[1,0], xy1=[-1,2],
                              gridname0=rg_m2m3, refinstname0=in1.name, refinstname1=in1.name, refinstindex0=[m-1, 0],
                              endstyle0=['extend', 'truncate'], endstyle1=['extend', 'truncate'], refpinname0='G0',
                              refpinname1='G0')

    # en
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=in4.name, refpinname0='G0',
                 refinstname1=in4.name, refpinname1='G0', refinstindex1=[m-1, 0])
    for i in range(m):
        laygen.via(None, [0, 0], refinstname=in4.name, refpinname='G0', refinstindex=[i, 0], gridname=rg_m1m2)
    ren0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([1, 0]), xy1=np.array([1, 2]), gridname0=rg_m2m3,
                        refinstname0=in4.name, refpinname0='G0', refinstname1=in4.name, refpinname1='G0', via0=[[0, 0]])
    # enb
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                 refinstname0=ip4.name, refpinname0='G0',
                 refinstname1=ip4.name, refpinname1='G0', refinstindex1=[m - 1, 0])
    for i in range(m):
        laygen.via(None, [0, 0], refinstname=ip4.name, refpinname='G0', refinstindex=[i, 0], gridname=rg_m1m2)
    renb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                        refinstname0=ip4.name, refpinname0='G0', refinstname1=ip4.name, refpinname1='G0', via0=[[0, 0]])
    # stack connections
    laygen.route(None, laygen.layers['metal'][2], xy0=[0, 0], xy1=[0, 0], gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0', refinstindex0=[0, 0], endstyle0="extend",
                 refinstname1=in4.name, refpinname1='S1', refinstindex1=[m-1, 0], endstyle1="extend")
    laygen.route(None, laygen.layers['metal'][2], xy0=[0, 0], xy1=[0, 0], gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='D0', refinstindex0=[0, 0], endstyle0="extend",
                 refinstname1=ip4.name, refpinname1='S1', refinstindex1=[m-1, 0], endstyle1="extend")
    for i in range(m):
        laygen.via(None, xy=[0, 0], refinstname=in1.name, refpinname='D0', refinstindex=[i, 0], gridname=rg_m1m2)
        laygen.via(None, xy=[0, 0], refinstname=ip1.name, refpinname='D0', refinstindex=[i, 0], gridname=rg_m1m2)
        laygen.via(None, xy=[0, 0], refinstname=in4.name, refpinname='S0', refinstindex=[i, 0], gridname=rg_m1m2)
        laygen.via(None, xy=[0, 0], refinstname=ip4.name, refpinname='S0', refinstindex=[i, 0], gridname=rg_m1m2)
    laygen.via(None, xy=[0, 0], refinstname=in4.name, refpinname='S1', refinstindex=[m-1, 0], gridname=rg_m1m2)
    laygen.via(None, xy=[0, 0], refinstname=ip4.name, refpinname='S1', refinstindex=[m-1, 0], gridname=rg_m1m2)
    # output
    laygen.route(None, laygen.layers['metal'][2], xy0=[-1, 1], xy1=[1, 1], gridname0=rg_m2m3,
                 refinstname0=in4.name, refpinname0='D0', refinstindex0=[0, 0], endstyle0="extend",
                 refinstname1=in4.name, refpinname1='D0', refinstindex1=[m-1, 0], endstyle1="extend")
    laygen.route(None, laygen.layers['metal'][2], xy0=[-1, 1], xy1=[1, 1], gridname0=rg_m2m3,
                 refinstname0=ip4.name, refpinname0='D0', refinstindex0=[0, 0], endstyle0="extend",
                 refinstname1=ip4.name, refpinname1='D0', refinstindex1=[m-1, 0], endstyle1="extend")
    for i in range(m):
        laygen.via(None, xy=[0, 1], refinstname=in4.name, refpinname='D0', refinstindex=[i, 0], gridname=rg_m1m2)
        laygen.via(None, xy=[0, 1], refinstname=ip4.name, refpinname='D0', refinstindex=[i, 0], gridname=rg_m1m2)
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=[0, 1], xy1=[0, 1], gridname0=rg_m2m3,
                       refinstname0=in4.name, refpinname0='D0', refinstindex0=[m-1, 0], via0=[[0, 0]],
                       refinstname1=ip4.name, refpinname1='D0', refinstindex1=[m-1, 0], via1=[[0, 0]])
    # power and groud rail
    xy = laygen.get_xy(obj = in2.template, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=[0, 0], xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip5.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=[0, 0], xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in5.name)
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=in1.name, refinstindex0=np.array([m-1, 0]), via0=[[0, 0]],
                 refinstname1=in1.name, refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                 refinstname0=ip1.name, refinstindex0=np.array([m-1, 0]), via0=[[0, 0]],
                 refinstname1=ip1.name, refinstindex1=np.array([m-1, 0]))
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['I', 'EN', 'ENB', 'O'], rect_list=[ri0, ren0, renb0, ro0])
        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], refobj=rvdd, gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], refobj=rvss, gridname=rg_m1m2)

def generate_space(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m2m3_pin,
                   devname_nmos_space, devname_pmos_space, m=1, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m2m3_pin = routing_grid_m2m3_pin

    # placement
    in0 = laygen.relplace(name='I' + objectname_pfix + 'N0', templatename=devname_nmos_space, gridname=pg, xy=origin,
                          shape=[m, 1])
    ip0 = laygen.relplace(name='I' + objectname_pfix + 'P0', templatename=devname_pmos_space, gridname=pg,
                          refinstname=in0.name, shape=[m, 1], direction='top', transform='MX')

    # power and groud rail
    xy = laygen.get_xy(obj = in0.template, gridname = rg_m1m2) * np.array([1, 0]) * m
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=[0, 0], xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=[0, 0], xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)
    # pin
    if create_pin == True:
        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], refobj=rvdd, gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], refobj=rvss, gridname=rg_m1m2)

#setup laygo
laygen = laygo.GridLayoutGenerator(config_file='laygo_config.yaml')
if laygen.tech=='laygo10n' or laygen.tech=='laygo_faketech': #fake technology
    laygen.use_phantom = True
utemplib = laygen.tech+'_microtemplates_dense'
laygen.load_template(filename=laygen.tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
laygen.load_grid(filename=laygen.tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
laygen.templates.sel_library(utemplib)
laygen.grids.sel_library(utemplib)

#library generation
workinglib = laygen.tech+'_templates_logic'
laygen.add_library(workinglib); laygen.sel_library(workinglib)

#grid
pg = 'placement_basic' #placement grid
rg_m1m2 = 'route_M1_M2_mos'
rg_m2m3 = 'route_M2_M3_mos'
rg_m1m2_pin = 'route_M1_M2_basic'
rg_m2m3_pin = 'route_M2_M3_basic'

#mycell_list=['inv_1x', 'tinv_1x', 'space_1x']
mycell_list=[]

#inverter generation
cellname='inv_4x'
mycell_list.append(cellname)
laygen.add_cell(cellname); laygen.sel_cell(cellname)
generate_inv(laygen, objectname_pfix='IINV0', placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
             routing_grid_m2m3_pin=rg_m2m3_pin, devname_nmos_boundary='nmos4_fast_boundary',
             devname_nmos_body='nmos4_fast_center_nf2', devname_pmos_boundary='pmos4_fast_boundary',
             devname_pmos_body='pmos4_fast_center_nf2', m=4, create_pin=True)
laygen.add_template_from_cell()
laygen.display()
cellname='tinv_4x'
mycell_list.append(cellname)
laygen.add_cell(cellname); laygen.sel_cell(cellname)
generate_tinv(laygen, objectname_pfix='IINV0', placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
             routing_grid_m2m3_pin=rg_m2m3_pin, devname_nmos_boundary='nmos4_fast_boundary',
             devname_nmos_body='nmos4_fast_center_nf2', devname_pmos_boundary='pmos4_fast_boundary',
             devname_pmos_body='pmos4_fast_center_nf2', m=4, create_pin=True)
laygen.add_template_from_cell()

cellname='space_1x'
mycell_list.append(cellname)
laygen.add_cell(cellname); laygen.sel_cell(cellname)
generate_space(laygen, objectname_pfix='ISP0', placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3,
               routing_grid_m2m3_pin=rg_m2m3_pin, devname_nmos_space='nmos4_fast_space',
               devname_pmos_space='pmos4_fast_space', m=1, create_pin=True)
laygen.add_template_from_cell()

#display
#laygen.display()
#laygen.templates.display()

#save template
laygen.save_template(filename=laygen.tech+'_templates_logic_templates.yaml', libname=workinglib)

#bag export, if bag does not exist, gds export
import imp
try:
    imp.find_module('bag')
    import bag
    prj = bag.BagProject()
    for mycell in mycell_list:
        laygen.sel_cell(mycell)
        laygen.export_BAG(prj, array_delimiter=['[', ']'])
except ImportError:
    laygen.export_GDS('output.gds', cellname=mycell_list, layermapfile=laygen.tech+".layermap")  # change layermapfile

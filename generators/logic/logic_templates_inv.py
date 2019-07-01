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
    rvdd_pin_xy = laygen.get_xy(obj = rect_vdd, gridname = gridname)
    rvss_pin_xy = laygen.get_xy(obj = rect_vss, gridname = gridname)
    laygen.pin(name=pinname_vdd, layer=layer, xy=rvdd_pin_xy, gridname=gridname)
    laygen.pin(name=pinname_vss, layer=layer, xy=rvss_pin_xy, gridname=gridname)

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
    xy = laygen.get_xy(obj = in0.template, gridname = rg_m1m2) * np.array([1, 0])
    laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip0.name)
    laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in0.name)

    # power pin
    if create_pin==True:
        rvdd_pin_xy = laygen.get_xy(obj =laygen.get_rect(name = "R"+objectname_pfix+"VDD0"), gridname = rg_m1m2)
        rvss_pin_xy = laygen.get_xy(obj =laygen.get_rect(name = "R"+objectname_pfix+"VSS0"), gridname = rg_m1m2)
        laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2)
        laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2)

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
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m2m3,
                     refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m2m3,
                     refinstname0=ip1.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip1.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]),
                     endstyle0="extend", endstyle1="extend")
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=in1.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                     refinstname0=ip1.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip1.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([m-1, 0]),
               gridname=rg_m2m3)
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([m-1, 0]),
               gridname=rg_m2m3)

    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([m-1, 0]),
                       refinstname1=ip1.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))

    # power and groud rail
    xy = laygen.get_xy(obj = in2.template, gridname = rg_m1m2) * np.array([1, 0])
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

if __name__ == '__main__':
    laygen = laygo.GridLayoutGenerator(config_file="laygo_config.yaml")

    import imp

    try:
        imp.find_module('bag')
        laygen.use_phantom = False
    except ImportError:
        laygen.use_phantom = True

    tech = laygen.tech
    primitivelib = '_microtemplates_dense'
    utemplib = tech + primitivelib
    laygen.load_template(filename=tech + primitivelib + '_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech + primitivelib + '_grids.yaml', libname=utemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)
    # laygen.templates.display()
    # laygen.grids.display()

    # library generation
    workinglib = 'laygo_working'
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
    if os.path.exists(workinglib + '.yaml'):  # generated layout file exists
        laygen.load_template(filename=workinglib + '.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    # grid
    pg = 'placement_basic'  # placement grid
    rg_m1m2 = 'route_M1_M2_cmos'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    # cell generation

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

    laygen.add_cell('tap')
    laygen.sel_cell('tap')
    generate_tap(laygen, objectname_pfix='TAP0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                           devname_nmos_tap='nmos4_fast_tap', devname_pmos_tap='pmos4_fast_tap',
                           origin=np.array([0, 0]), create_pin=True
                           )
    laygen.add_template_from_cell()

    laygen.save_template(filename=workinglib + '.yaml', libname=workinglib)

    laygen.add_cell('test')
    laygen.sel_cell('test')
    pg = 'placement_basic'

    # placement
    # tap,inv = laygen.relplace(name=['TAPx', 'INVx'], gridname=pg, templatename=['tap','inv_2x'], libname=workinglib,
    #                           xy=[[0,0],[0,0]])
    tap = laygen.relplace(name="TAP0", gridname=pg, templatename='tap', libname=workinglib, xy=[0, 0])
    _inv = laygen.relplace(name="INV0", gridname=pg, templatename='inv_2x', libname=workinglib, refobj=tap)
    laygen.add_template_from_cell()

    mycell_list = ['inv_2x', 'tap', 'test']

    laygen.save_template(filename=workinglib + '.yaml', libname=workinglib)

    import imp

    try:
        imp.find_module('bag')
        import bag

        prj = bag.BagProject()
        for mycell in mycell_list:
            laygen.sel_cell(mycell)
            laygen.export_BAG(prj, array_delimiter=['[', ']'])
    except ImportError:
        laygen.export_GDS('output.gds', cellname=mycell_list, layermapfile=tech + ".layermap")  # change layermapfile

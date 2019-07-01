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

"""SER library
"""
import laygo
import numpy as np
#from logic_layout_generator import *
from math import log
import yaml
import os
#import logging;logging.basicConfig(level=logging.DEBUG)

def generate_boundary(laygen, objectname_pfix, placement_grid,
                      devname_bottom, devname_top, devname_left, devname_right,
                      shape_bottom=None, shape_top=None, shape_left=None, shape_right=None,
                      transform_bottom=None, transform_top=None, transform_left=None, transform_right=None,
                      origin=np.array([0, 0])):
    #generate a boundary structure to resolve boundary design rules
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
        dev_bottom.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDBTM'+str(i+1), templatename = d, gridname = pg, refinstname = dev_bottom[-1].name,
                                          shape=shape_bottom[i+1], transform=transform_bottom[i+1]))
    dev_left=[]
    dev_left.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDLFT0', templatename = devname_left[0], gridname = pg, refinstname = dev_bottom[0].name, direction='top',
                                    shape=shape_left[0], transform=transform_left[0]))
    for i, d in enumerate(devname_left[1:]):
        dev_left.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDLFT'+str(i+1), templatename = d, gridname = pg, refinstname = dev_left[-1].name, direction='top',
                                        shape=shape_left[i+1], transform=transform_left[i+1]))
    dev_right=[]
    dev_right.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDRHT0', templatename = devname_right[0], gridname = pg, refinstname = dev_bottom[-1].name, direction='top',
                                     shape=shape_right[0], transform=transform_right[0]))
    for i, d in enumerate(devname_right[1:]):
        dev_right.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDRHT'+str(i+1), templatename = d, gridname = pg, refinstname = dev_right[-1].name, direction='top',
                                         shape=shape_right[i+1], transform=transform_right[i+1]))
    dev_top=[]
    dev_top.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDTOP0', templatename = devname_top[0], gridname = pg, refinstname = dev_left[-1].name, direction='top',
                                   shape=shape_top[0], transform=transform_top[0]))
    for i, d in enumerate(devname_top[1:]):
        dev_top.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDTOP'+str(i+1), templatename = d, gridname = pg, refinstname = dev_top[-1].name,
                                       shape=shape_top[i+1], transform=transform_top[i+1]))
    dev_right=[]
    return [dev_bottom, dev_top, dev_left, dev_right]

def generate_ser2to1(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m2m3,
                          routing_grid_m4m5, num_ser=8, m_ser=1, origin=np.array([0, 0])):
    """generate 2to1 ser with 1/2 clock array """
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m4m5 = routing_grid_m4m5

    tap_name='tap'
    ff_name = 'dff_'+str(int(m_dff))+'x'
    ff_rst_name = 'dff_strsth_'+str(int(m_dff))+'x'
    latch_sub_name = 'latch_2ck_1x'
    latch_name = 'latch_2ck_'+str(int(m_ser))+'x'
    inv1_name = 'inv_'+str(int(m_cbuf1))+'x'
    inv2_name = 'inv_'+str(int(m_cbuf2))+'x'
    tinv_name = 'tinv_'+str(int(m_mux))+'x'
    outinv_name = 'inv_'+str(int(m_out))+'x'
    sub_ser = int(num_ser/2)

    #Calculate layout size from sub_ser
    ff_size=laygen.get_xy(obj=laygen.get_template(name = ff_name, libname = templib_logic), gridname = pg)
    ff_rst_size=laygen.get_xy(obj=laygen.get_template(name = ff_rst_name, libname = templib_logic), gridname = pg)
    latch_size=laygen.get_xy(obj=laygen.get_template(name = latch_name, libname = templib_logic), gridname = pg)
    inv1_size=laygen.get_xy(obj=laygen.get_template(name = inv1_name, libname = templib_logic), gridname = pg)
    inv2_size=laygen.get_xy(obj=laygen.get_template(name = inv2_name, libname = templib_logic), gridname = pg)
    tinv_size=laygen.get_xy(obj=laygen.get_template(name = tinv_name, libname = templib_logic), gridname = pg)
    outinv_size=laygen.get_xy(obj=laygen.get_template(name = outinv_name, libname = templib_logic), gridname = pg)
    tap_size=laygen.get_xy(obj=laygen.get_template(name = tap_name, libname = templib_logic), gridname = pg)
    x0=ff_size[0]+ff_rst_size[0]+inv1_size[0]+2*inv2_size[0]+tinv_size[0]+2*tap_size[0]
    num_row=1
    #boundaries
    m_bnd = int(x0 / laygen.get_xy(obj=laygen.get_template(name = 'boundary_bottom'), gridname = pg)[0])
    devname_bnd_left = []
    devname_bnd_right = []
    transform_bnd_left = []
    transform_bnd_right = []
    for i in range(num_row):
        if i%2==0:
            devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
    [bnd_bottom, bnd_top, bnd_left, bnd_right] = generate_boundary(laygen, objectname_pfix='BND0',
                                                                   placement_grid=pg,
                                                                   devname_bottom=['boundary_bottomleft',
                                                                                   'boundary_bottom',
                                                                                   'boundary_bottomright'],
                                                                   shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]),
                                                                                 np.array([1, 1])],
                                                                   devname_top=['boundary_topleft', 'boundary_top',
                                                                                'boundary_topright'],
                                                                   shape_top=[np.array([1, 1]), np.array([m_bnd, 1]),
                                                                              np.array([1, 1])],
                                                                   devname_left=devname_bnd_left,
                                                                   transform_left=transform_bnd_left,
                                                                   devname_right=devname_bnd_right,
                                                                   transform_right=transform_bnd_right,
                                                                   origin=np.array([0, 0]))
    #Calculate origins for placement
    tap_origin = origin + laygen.get_xy(obj = bnd_bottom[0], gridname = pg) \
                   + laygen.get_xy(obj = bnd_bottom[0].template, gridname = pg)
    array_origin = origin + laygen.get_xy(obj = bnd_bottom[0], gridname = pg) \
                   + laygen.get_xy(obj = bnd_bottom[0].template, gridname = pg) \
                   + np.array([laygen.get_xy(obj=laygen.get_template(name = tap_name, libname = templib_logic), gridname = pg)[0], 0])
    tapr_origin = tap_origin + m_bnd*np.array([laygen.get_xy(obj=laygen.get_template(name = 'boundary_bottom'), gridname = pg)[0], 0]) \
                   - np.array([laygen.get_xy(obj=laygen.get_template(name = tap_name, libname = templib_logic), gridname = pg)[0], 0])
    # placement
    itapl=[]
    itapr=[]
    itapl.append(laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                                      gridname = pg, xy=tap_origin, transform='R0', shape=np.array([1,1]), template_libname = templib_logic))
    itapr.append(laygen.place(name = "I" + objectname_pfix + 'TAPR0', templatename = tap_name,
                                      gridname = pg, xy=tapr_origin, transform='R0', shape=np.array([1,1]), template_libname = templib_logic))
    #Space placement
    space_name = 'space_1x'
    space4x_name = 'space_4x'
    space_width = laygen.get_xy(obj=laygen.get_template(name = space_name, libname = templib_logic), gridname = pg)[0]
    space4_width = laygen.get_xy(obj=laygen.get_template(name = space4x_name, libname = templib_logic), gridname = pg)[0]
    iclk_size=laygen.get_xy(obj=laygen.get_template(name = "inv_" + str(m_ser) + "x", libname = templib_logic), gridname = pg)
    imux_size=laygen.get_xy(obj=laygen.get_template(name = "mux2to1_" + str(m_ser) + "x", libname = templib_logic), gridname = pg)
    blank1_width = x0 - (2*tap_size + 2*iclk_size + imux_size + latch_size)[0]
    m_space4 = int(blank1_width / space4_width)
    m_space1 = int((blank1_width-m_space4*space4_width)/space_width)
    ispace4=laygen.relplace(name = "I" + objectname_pfix + 'SPACE4', templatename = space4x_name,
                           gridname = pg, refinstname = itapl[0].name, transform="R0", shape=np.array([m_space4-1,1]),
                           template_libname=templib_logic)
    ispace1=laygen.relplace(name = "I" + objectname_pfix + 'SPACE1', templatename = space_name,
                           gridname = pg, refinstname = ispace4.name, transform="R0", shape=np.array([m_space1+4,1]),
                           template_libname=templib_logic)
    #Cell placement
    iclk0 = laygen.relplace(
        name = "I" + objectname_pfix + 'CLKINV0',
        templatename = "inv_" + str(m_ser) + "x",
        gridname = pg, template_libname=templib_logic,
        refinstname = ispace1.name, 
    )
    iclkb0 = laygen.relplace(
        name = "I" + objectname_pfix + 'CLKBINV0',
        templatename = "inv_" + str(m_ser) + "x",
        gridname = pg, template_libname=templib_logic,
        refinstname = iclk0.name
    )
    i0 = laygen.relplace(
        name = "I" + objectname_pfix + 'LATCH0',
        templatename = "latch_2ck_"+str(m_ser)+"x",
        gridname = pg, template_libname=templib_logic,
        refinstname = iclkb0.name
    )
    i1 = laygen.relplace(
        name = "I" + objectname_pfix + 'MUX0',
        templatename = "mux2to1_"+str(m_ser)+"x",
        gridname = pg, template_libname=templib_logic,
        refinstname = i0.name
    )

    # internal pins
    iclk0_i_xy = laygen.get_inst_pin_xy(iclk0.name, 'I', rg_m3m4)
    iclk0_o_xy = laygen.get_inst_pin_xy(iclk0.name, 'O', rg_m3m4)
    iclkb0_i_xy = laygen.get_inst_pin_xy(iclkb0.name, 'I', rg_m3m4)
    iclkb0_o_xy = laygen.get_inst_pin_xy(iclkb0.name, 'O', rg_m3m4)
    i0_i_xy = laygen.get_inst_pin_xy(i0.name, 'I', rg_m3m4)
    i0_clk_xy = laygen.get_inst_pin_xy(i0.name, 'CLK', rg_m3m4)
    i0_clkb_xy = laygen.get_inst_pin_xy(i0.name, 'CLKB', rg_m3m4)
    i0_o_xy = laygen.get_inst_pin_xy(i0.name, 'O', rg_m3m4)
    i1_i0_xy = laygen.get_inst_pin_xy(i1.name, 'I0', rg_m3m4)
    i1_i1_xy = laygen.get_inst_pin_xy(i1.name, 'I1', rg_m3m4)
    i1_en0_xy = laygen.get_inst_pin_xy(i1.name, 'EN0', rg_m3m4)
    i1_en1_xy = laygen.get_inst_pin_xy(i1.name, 'EN1', rg_m3m4)
    i1_o_xy = laygen.get_inst_pin_xy(i1.name, 'O', rg_m3m4)

    # internal route
    laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][3], i0_o_xy[0], i1_i0_xy[0], rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], iclk0_o_xy[0], i1_en1_xy[0], i0_clk_xy[0][1], rg_m3m4)
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], iclkb0_o_xy[0], i1_en0_xy[0], i0_clkb_xy[0][1], rg_m3m4)

    #Pin
    [rv0, rclk] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], 
            iclk0_i_xy[0], np.array([0,iclk0_i_xy[0][1]]), rg_m3m4)
    laygen.boundary_pin_from_rect(rclk, rg_m3m4, "CLK", laygen.layers['pin'][4], size=4, direction='left')
    [rv0, rclkb] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], 
            iclkb0_i_xy[0], np.array([0,iclkb0_i_xy[1][1]]), rg_m3m4)
    laygen.boundary_pin_from_rect(rclkb, rg_m3m4, "CLKB", laygen.layers['pin'][4], size=4, direction='left')
    [rv0, rdatao] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], 
            i1_o_xy[0], i1_o_xy[0]+np.array([5,0]), rg_m3m4)
    laygen.boundary_pin_from_rect(rdatao, rg_m3m4, "O", laygen.layers['pin'][4], size=4, direction='right')
    laygen.pin(name='I<0>', layer=laygen.layers['pin'][3], xy=i0_i_xy, gridname=rg_m3m4)
    laygen.pin(name='I<1>', layer=laygen.layers['pin'][3], xy=i1_i1_xy, gridname=rg_m3m4)
    # power pin
    pwr_dim=laygen.get_xy(obj =itapl[-1].template, gridname=rg_m2m3)
    rvdd = []
    rvss = []
    if num_row%2==0: rp1='VSS'
    else: rp1='VDD'
    print(int(pwr_dim[0]/2))
    for i in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin(name = 'VDD'+str(2*i-2), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSS'+str(2*i-2), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2+1, 0]), xy1=np.array([2*i+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin(name = 'VDD'+str(2*i-1), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSS'+str(2*i-1), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
    
    for i in range(num_row):
        for j in range(0, int(pwr_dim[0]/2)):
            rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                         refinstname0=itapl[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                         refinstname1=itapl[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
            rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                         refinstname0=itapl[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                         refinstname1=itapl[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))
            rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2+1, 0]), xy1=np.array([2*j+2+1, 0]), gridname0=rg_m2m3,
                         refinstname0=itapr[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                         refinstname1=itapr[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
            rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2, 0]), xy1=np.array([2*j+2, 0]), gridname0=rg_m2m3,
                         refinstname0=itapr[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                         refinstname1=itapr[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))

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
    logictemplib = tech+'_logic_templates'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)

    #library load or generation
    workinglib = 'serdes_generated'
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
    if os.path.exists(workinglib+'.yaml'): #generated layout file exists
        laygen.load_template(filename=workinglib+'.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    #grid
    pg = 'placement_basic' #placement grid
    rg_m1m2 = 'route_M1_M2_cmos'
    rg_m1m2_thick = 'route_M1_M2_thick'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'


    #display
    #laygen.display()
    #laygen.templates.display()
    #laygen.save_template(filename=workinglib+'_templates.yaml', libname=workinglib)

    mycell_list = []
    
    #load from preset
    load_from_file=True
    yamlfile_spec="serdes_spec.yaml"
    yamlfile_size="serdes_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        cell_name='ser_2to1_halfrate'
        num_ser=specdict['num_ser']
        m_dff=sizedict['m_dff']
        m_cbuf1=sizedict['m_cbuf1']
        m_cbuf2=sizedict['m_cbuf2']
        m_pbuf1=sizedict['m_pbuf1']
        m_pbuf2=sizedict['m_pbuf2']
        m_mux=sizedict['m_mux']
        m_out=sizedict['m_out']
        m_ser=sizedict['m_ser']

    print(cell_name+" generating")
    mycell_list.append(cell_name)
    laygen.add_cell(cell_name)
    laygen.sel_cell(cell_name)
    generate_ser2to1(laygen, objectname_pfix='SER', templib_logic=logictemplib, 
                          placement_grid=pg, routing_grid_m2m3=rg_m2m3, routing_grid_m4m5=rg_m4m5, num_ser=num_ser,
                          m_ser=m_ser, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    laygen.save_template(filename=workinglib+'.yaml', libname=workinglib)
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
        laygen.export_GDS('output.gds', cellname=mycell_list, layermapfile=tech+".layermap")  # change layermapfile

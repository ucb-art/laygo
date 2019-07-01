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

"""Serdes library
"""
import laygo
import numpy as np
#from logic_templates_layout_generator import *
from math import log
import yaml
#import logging;logging.basicConfig(level=logging.DEBUG)

def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin"""
    rvdd0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VSS', gridname, sort=True)

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=gridname)

def generate_ser2to1_body(laygen, objectname_pfix, placement_grid, routing_grid_m3m4, origin=np.array([0, 0]), m=2):
    """generate a ser2to1 body element"""
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    # placement
    iclk0 = laygen.place(
        name = "I" + objectname_pfix + 'CLKINV0',
        templatename = "inv_" + str(m) + "x",
        gridname = pg,
        xy=origin
    )
    iclkb0 = laygen.relplace(
        name = "I" + objectname_pfix + 'CLKBINV0',
        templatename = "inv_" + str(m) + "x",
        gridname = pg,
        refinstname = iclk0.name
    )
    i0 = laygen.relplace(
        name = "I" + objectname_pfix + 'LATCH0',
        templatename = "latch_2ck_"+str(m)+"x",
        gridname = pg,
        refinstname = iclkb0.name
    )
    i1 = laygen.relplace(
        name = "I" + objectname_pfix + 'MUX0',
        templatename = "mux2to1_"+str(m)+"x",
        gridname = pg,
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

    #pin
    laygen.pin('A', laygen.layers['pin'][3], laygen.get_inst_pin_xy(i1.name, 'I1', rg_m3m4, sort=True), rg_m3m4)
    laygen.pin('B', laygen.layers['pin'][3], laygen.get_inst_pin_xy(i0.name, 'I', rg_m3m4, sort=True), rg_m3m4)
    laygen.pin('O', laygen.layers['pin'][3], laygen.get_inst_pin_xy(i1.name, 'O', rg_m3m4, sort=True), rg_m3m4)
    laygen.pin('CLK', laygen.layers['pin'][3], laygen.get_inst_pin_xy(iclk0.name, 'I', rg_m3m4, sort=True), rg_m3m4)
    laygen.pin('CLKB', laygen.layers['pin'][3], laygen.get_inst_pin_xy(iclkb0.name, 'I', rg_m3m4, sort=True), rg_m3m4)

    create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=iclk0, inst_right=i1)

def generate_ser2to1(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4, devname_serbody,
                     origin=np.array([0, 0]), num_space_left=4, num_space_right=4):
    """generate ser2to1"""
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    # placement
    itap0 = laygen.place(
        name="I" + objectname_pfix + 'TAP0',
        templatename = "tap",
        gridname = pg,
        xy=origin,
        template_libname=templib_logic
    )
    ispace_l0 = laygen.relplace(
        name="I" + objectname_pfix + 'SPL0',
        templatename = "space_1x",
        gridname = pg,
        refinstname = itap0.name,
        shape=np.array([num_space_left, 1]),
        template_libname=templib_logic
    )
    i0 = laygen.relplace(
        name = "I" + objectname_pfix + 'SER0',
        templatename = devname_serbody,
        gridname = pg,
        refinstname = ispace_l0.name
    )
    ispace_r0 = laygen.relplace(
        name = "I" + objectname_pfix + 'SPR0',
        templatename = "space_1x",
        gridname = pg,
        refinstname = i0.name,
        shape=np.array([num_space_right, 1]),
        template_libname=templib_logic,
        transform="MY"
    )
    itap1 = laygen.relplace(
        name = "I" + objectname_pfix + 'TAP1',
        templatename = "tap",
        gridname = pg,
        refinstname = ispace_r0.name,
        template_libname=templib_logic,
        transform = "MY"
    )

    # internal pin coordinates
    i2_a_xy = laygen.get_inst_pin_xy(i0.name, 'A', rg_m3m4)
    i2_b_xy = laygen.get_inst_pin_xy(i0.name, 'B', rg_m3m4)
    i2_clk_xy = laygen.get_inst_pin_xy(i0.name, 'CLK', rg_m3m4)
    i2_clkb_xy = laygen.get_inst_pin_xy(i0.name, 'CLKB', rg_m3m4)
    i2_o_xy = laygen.get_inst_pin_xy(i0.name, 'O', rg_m3m4)

    # reference route coordinates
    y0=i2_clk_xy[0][1]
    x0 = laygen.get_inst_xy(name=ispace_l0.name, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_inst_xy(name=ispace_r0.name, gridname=rg_m3m4)[0] - 1

    # in0 / in1 / clk / clkb route
    rv0, ri0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], i2_a_xy[0], np.array([x0, y0 + 3]), rg_m3m4)
    rv0, ri1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], i2_b_xy[0], np.array([x0, y0 + 2]), rg_m3m4)
    rv0, rclk0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], i2_clk_xy[0], np.array([x0, y0 + 1]), rg_m3m4)
    rv0, rclkb0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], i2_clkb_xy[0], np.array([x0, y0 + 0]), rg_m3m4)

    # output route
    xyo0 = laygen.get_inst_pin_xy(i0.name, 'O', rg_m3m4)[0]
    ro0 = laygen.route(None, laygen.layers['metal'][4], xy0=xyo0, xy1=np.array([x1, xyo0[1]]), gridname0=rg_m3m4)
    laygen.via(None, xyo0, gridname=rg_m3m4)

    # pin creation
    laygen.boundary_pin_from_rect(rclk0, rg_m3m4, "CLK", laygen.layers['pin'][4], size=num_space_left + 6,
                                  direction='left')
    laygen.boundary_pin_from_rect(rclkb0, rg_m3m4, "CLKB", laygen.layers['pin'][4], size=num_space_left + 6,
                                  direction='left')
    laygen.boundary_pin_from_rect(ri0, rg_m3m4, "I<0>", laygen.layers['pin'][4], size=num_space_left + 6,
                                  direction='left')
    laygen.boundary_pin_from_rect(ri1, rg_m3m4, "I<1>", laygen.layers['pin'][4], size=num_space_left + 6,
                                  direction='left')
    laygen.boundary_pin_from_rect(ro0, rg_m3m4, "O", laygen.layers['pin'][4], size=num_space_right + 6,
                                  direction='right')

    #power pin
    create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=itap0, inst_right=itap1)

def generate_ser_vstack(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m4m5, devname_serslice,
                        origin=np.array([0, 0]), num_stages=3, radix=2, num_pwr=4):
    """generate vertically stacked serializer"""

    pg = placement_grid
    rg_m4m5 = routing_grid_m4m5

    input_size = radix ** num_stages
    size_ser2to1 = laygen.get_template_xy(devname_serslice, pg)
    size_ser2to1_rg_m4m5 = laygen.get_template_xy(devname_serslice, rg_m4m5)
    # placement
    iser = []
    y_ser = 0
    for i in range(num_stages):
        if i%2==0:
            transform_list = ['R0', 'MX']
            xoffset=0
        else:
            transform_list = ['MY', 'R180']
            xoffset=size_ser2to1[0]
        for j in range(radix ** (num_stages - i - 1)):
            if j%2==0:
                iser.append(laygen.place("I" + objectname_pfix + 'SER_' + str(i) + '_' + str(j), devname_serslice, pg,
                                         xy=origin + np.array([xoffset, y_ser]), transform=transform_list[0]))
            else:
                iser.append(laygen.place("I" + objectname_pfix + 'SER_' + str(i) + '_' + str(j), devname_serslice, pg,
                                 xy=origin + np.array([xoffset, y_ser+size_ser2to1[1]]), transform=transform_list[1]))
            y_ser += size_ser2to1[1]

    # input
    x0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_0_0', 'I<0>', gridname=rg_m4m5, sort=True)[0][0]
    ri_list=[]
    for j in range(int(input_size/2)):
        xyi0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_0_' + str(j), 'I<0>', gridname=rg_m4m5)[0]
        rh0, ri0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], np.array([x0, xyi0[1]]), np.array([x0+2*j+1, 0]), rg_m4m5)
        ri_list.append(ri0)
        xyi1 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_0_' + str(j), 'I<1>', gridname=rg_m4m5)[0]
        rh1, ri1 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], np.array([x0, xyi1[1]]), np.array([x0+2*j+2, 0]), rg_m4m5)
        ri_list.append(ri1)

    #input pin index calculation
    ri_index_list = []
    for i in range(input_size):
        x = 0
        for j in range(num_stages):
            x += input_size / (2 ** (j + 1)) * (int(i / (2 ** j)) % 2)
        ri_index_list.append(x)

    #input pin creation
    for i in range(input_size):
        laygen.boundary_pin_from_rect(ri_list[i], rg_m4m5, "I<" + str(int(ri_index_list[i])) + ">",
                                      laygen.layers['pin'][5], size=4, direction='bottom')

    # internal datapath route
    for i in range(num_stages-1):
        x0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(i) + '_0', 'O', gridname=rg_m4m5, sort=True)[0][0]
        for j in range(int(radix ** (num_stages - i - 1)/2)):
            xyo0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(i) + '_' + str(2 * j), 'O', gridname=rg_m4m5)[0]
            xyi0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(i + 1) + '_' + str(j), 'I<0>', gridname=rg_m4m5)[0]
            laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], xyo0, xyi0, x0+2*j+1, rg_m4m5)
            xyo1 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(i) + '_' + str(2 * j + 1), 'O', gridname=rg_m4m5)[0]
            xyi1 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(i + 1) + '_' + str(j), 'I<1>', gridname=rg_m4m5)[0]
            laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], xyo1, xyi1, x0+2*j+2, rg_m4m5)

    # internal clock route
    for i in range(num_stages):
        x0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(i) + '_0', 'CLK', gridname=rg_m4m5, sort=True)[0][0]
        for j in range(radix ** (num_stages - i - 1)-1):
            xyclk0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(i) + '_' + str(j), 'CLK', gridname=rg_m4m5, sort=True)[0]
            xyclkb0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(i) + '_' + str(j), 'CLKB', gridname=rg_m4m5, sort=True)[0]
            xyclk1 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(i) + '_' + str(j + 1), 'CLK', gridname=rg_m4m5, sort=True)[0]
            xyclkb1 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(i) + '_' + str(j + 1), 'CLKB', gridname=rg_m4m5, sort=True)[0]
            laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], xyclk0, xyclk1, x0 + (radix) ** (num_stages) + 2*int(i/2) + 2, rg_m4m5)
            laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], xyclkb0, xyclkb1, x0 + (radix) ** (num_stages) + 2*int(i/2) + 2 + 1, rg_m4m5)

    # clock input
    #xoffset0=0
    for i in range(num_stages):
        x0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(i) + '_0', 'CLK', gridname=rg_m4m5, sort=True)[0][0]
        #xoffset0 += radix ** (num_stages - i)
        xyclk0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(i) + '_0', 'CLK', gridname=rg_m4m5, sort=True)[0]
        xyclkb0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(i) + '_0', 'CLKB', gridname=rg_m4m5, sort=True)[0]
        rh0, rclk0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], xyclk0, np.array([x0 + radix ** (num_stages) + 2*int(i/2) + 2, 0]), rg_m4m5)
        rh0, rclkb0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], xyclkb0, np.array([x0 + radix ** (num_stages) + 2*int(i/2) + 2 + 1, 0]), rg_m4m5)

        laygen.boundary_pin_from_rect(rclk0, rg_m4m5, "CLK<" + str(num_stages - i - 1) + ">",
                                      laygen.layers['pin'][5], size=4, direction='bottom')
        laygen.boundary_pin_from_rect(rclkb0, rg_m4m5, "CLKB<" + str(num_stages - i - 1) + ">",
                                      laygen.layers['pin'][5], size=4, direction='bottom')

    # output
    y1 = laygen.get_inst_xy("I" + objectname_pfix + 'SER_' + str(num_stages-1) + '_0', gridname=rg_m4m5)[1]
    y1+=size_ser2to1_rg_m4m5[1]-1
    xyo0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(num_stages - 1) + '_0', 'O', gridname=rg_m4m5)[0]
    ro0 = laygen.route(None, laygen.layers['metal'][5], xy0=xyo0, xy1=np.array([xyo0[0], y1]), gridname0=rg_m4m5, via0=[[0, 0]])
    laygen.boundary_pin_from_rect(ro0, rg_m4m5, "O", laygen.layers['pin'][5], size=4, direction='top')
    
    #power rails
    xypwrl0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_0_0', 'VSS', gridname=rg_m2m3_thick_basic)[0]
    xypwrr0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_0_0', 'VSS', gridname=rg_m2m3_thick_basic)[1]
    xypwrl1 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(num_stages-1) + '_0', 'VDD', gridname=rg_m2m3_thick_basic)[0]
    xypwrr1 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(num_stages-1) + '_0', 'VDD', gridname=rg_m2m3_thick_basic)[1]
    rvddhl=[]
    rvsshl=[]
    rvddhr=[]
    rvsshr=[]
    for i in range(num_pwr):
        rvddhl.append(laygen.route(None, laygen.layers['metal'][3], xy0=xypwrl0+np.array([2*i, 0]), xy1=xypwrl1+np.array([2*i, 0]), gridname0=rg_m2m3_thick_basic))
        rvsshl.append(laygen.route(None, laygen.layers['metal'][3], xy0=xypwrl0+np.array([2*i+1, 0]), xy1=xypwrl1+np.array([2*i+1, 0]), gridname0=rg_m2m3_thick_basic))
        rvddhr.append(laygen.route(None, laygen.layers['metal'][3], xy0=xypwrr0-np.array([2*i, 0]), xy1=xypwrr1-np.array([2*i, 0]), gridname0=rg_m2m3_thick_basic))
        rvsshr.append(laygen.route(None, laygen.layers['metal'][3], xy0=xypwrr0-np.array([2*i+1, 0]), xy1=xypwrr1-np.array([2*i+1, 0]), gridname0=rg_m2m3_thick_basic))
        for j in range(num_stages):
            for k in range(radix ** (num_stages - j - 1)-1):
                xyvddvl0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(j) + '_' + str(k), 
                                                  'VDD', gridname=rg_m2m3_thick_basic)[0]
                xyvddvr0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(j) + '_' + str(k), 
                                                  'VDD', gridname=rg_m2m3_thick_basic)[1]
                xyvssvl0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(j) + '_' + str(k), 
                                                  'VSS', gridname=rg_m2m3_thick_basic)[0]
                xyvssvr0 = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_' + str(j) + '_' + str(k), 
                                                  'VSS', gridname=rg_m2m3_thick_basic)[1]
                if j%2==0:
                    coeff=1
                else:   
                    coeff=-1
                laygen.via(None, xyvddvl0+coeff*np.array([2*i, 0]), gridname=rg_m2m3_thick_basic)
                laygen.via(None, xyvssvl0+coeff*np.array([2*i+1, 0]), gridname=rg_m2m3_thick_basic)
                laygen.via(None, xyvddvr0-coeff*np.array([2*i, 0]), gridname=rg_m2m3_thick_basic)
                laygen.via(None, xyvssvr0-coeff*np.array([2*i+1, 0]), gridname=rg_m2m3_thick_basic)


    #power pin
    rvdd0_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_0_0', 'VDD', rg_m2m3)
    rvdd1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_0_0', 'VDD', rg_m2m3)
    rvss0_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_0_0', 'VSS', rg_m2m3)
    rvss1_pin_xy = laygen.get_inst_pin_xy("I" + objectname_pfix + 'SER_0_0', 'VSS', rg_m2m3)

    laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=rg_m1m2)
    laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=rg_m1m2)

def generate_ser_space_vstack(laygen, objectname_pfix, placement_grid, devname_serspace,
                              origin=np.array([0, 0]), num_stages=3, radix=2):
    """generate spacing elements between vstacked serializers"""
    pg = placement_grid
    size_ser2to1 = laygen.get_template_xy(devname_serspace, pg)

    # placement
    iser = []
    y_ser = 0
    for i in range(num_stages):
        if i%2==0:
            transform_list = ['R0', 'MX']
            xoffset=0
        else:
            transform_list = ['MY', 'R180']
            xoffset=size_ser2to1[0]
        for j in range(radix ** (num_stages - i - 1)):
            if j%2==0:
                iser.append(laygen.place("I" + objectname_pfix + 'SER_' + str(i) + '_' + str(j), devname_serspace, pg,
                                         xy=origin + np.array([xoffset, y_ser]), transform=transform_list[0]))
            else:
                iser.append(laygen.place("I" + objectname_pfix + 'SER_' + str(i) + '_' + str(j), devname_serspace, pg,
                                         xy=origin + np.array([xoffset, y_ser+size_ser2to1[1]]), transform=transform_list[1]))
            y_ser += size_ser2to1[1]

if __name__ == '__main__':
    import os.path
    with open("laygo_config.yaml", 'r') as stream:
        techdict = yaml.load(stream)
        tech = techdict['tech_lib']
        metal = techdict['metal_layers']
        pin = techdict['pin_layers']
        text = techdict['text_layer']
        prbnd = techdict['prboundary_layer']
        res = techdict['physical_resolution']
        print(tech + " loaded sucessfully")

    laygen = laygo.GridLayoutGenerator(physical_res=res)
    laygen.layers['metal'] = metal
    laygen.layers['pin'] = pin
    laygen.layers['prbnd'] = prbnd

    import imp
    try:
        imp.find_module('bag')
        laygen.use_phantom=False
    except ImportError:
        laygen.use_phantom=True

    utemplib = tech+'_microtemplates_dense'
    logictemplib = tech+'_logic_templates'
    laygen.load_template(filename=utemplib+'_templates.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    laygen.load_grid(filename=utemplib+'_grids.yaml', libname=utemplib)
    laygen.templates.sel_library(logictemplib)
    laygen.grids.sel_library(utemplib)

    #library generation
    workinglib = 'serdes_generated'

    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)

    #grid
    pg = 'placement_basic' #placement grid
    rg_m1m2 = 'route_M1_M2_cmos'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m2m3_thick_basic = 'route_M2_M3_thick_basic'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    #phantom_layer=prbnd

    ser_m=4
    ser_num_bits=8
    ser_num_stages=int(log(ser_num_bits, 2))
    # calculate routing track width
    num_route=ser_num_bits*2 # + int(ser_num_stages/2+1)*2 + 1
    num_space=int(laygen.get_grid(pg).width/laygen.get_grid(rg_m3m4).width*(num_route))

    # backend ser
    laygen.add_cell('ser2to1_body')
    laygen.sel_cell('ser2to1_body')
    generate_ser2to1_body(laygen, objectname_pfix='SER2TO1_', placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                        origin=np.array([0, 0]), m=ser_m)
    laygen.add_template_from_cell()

    laygen.add_cell('ser2to1')
    laygen.sel_cell('ser2to1')
    laygen.templates.sel_library(workinglib)
    generate_ser2to1(laygen, objectname_pfix='SER2TO1_', templib_logic=logictemplib, placement_grid=pg,
                     routing_grid_m3m4=rg_m3m4, devname_serbody='ser2to1_body', origin=np.array([0, 0]))
    laygen.templates.sel_library(logictemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('ser' + str(ser_num_bits) + 'to1_ser2to1_body')
    laygen.sel_cell('ser' + str(ser_num_bits) + 'to1_ser2to1_body')
    generate_ser2to1_body(laygen, objectname_pfix='SER2TO1_', placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                        origin=np.array([0, 0]), m=ser_m)
    laygen.add_template_from_cell()

    laygen.add_cell('ser' + str(ser_num_bits) + 'to1_ser2to1')
    laygen.sel_cell('ser' + str(ser_num_bits) + 'to1_ser2to1')
    laygen.templates.sel_library(workinglib)
    generate_ser2to1(laygen, objectname_pfix='SER2TO1_', templib_logic=logictemplib, placement_grid=pg,
                     routing_grid_m3m4=rg_m3m4, origin=np.array([0, 0]),
                     num_space_left=num_space,
                     num_space_right=num_space,
                     devname_serbody='ser'+str(ser_num_bits) + 'to1_ser2to1_body')
    laygen.templates.sel_library(logictemplib)
    laygen.add_template_from_cell()

    laygen.add_cell('ser' + str(ser_num_bits) + 'to1')
    laygen.sel_cell('ser' + str(ser_num_bits) + 'to1')
    laygen.templates.sel_library(workinglib)
    generate_ser_vstack(laygen, objectname_pfix='SER8TO1_', templib_logic=logictemplib, placement_grid=pg,
                        routing_grid_m4m5=rg_m4m5, devname_serslice='ser'+str(ser_num_bits) + 'to1_ser2to1',
                        origin=np.array([0, 0]), num_stages=ser_num_stages, radix=2)
    laygen.templates.sel_library(logictemplib)
    laygen.add_template_from_cell()

    #display
    #laygen.display()
    #laygen.templates.display()
    #laygen.save_template(filename=workinglib+'_templates.yaml', libname=workinglib)

    #bag export, if bag does not exist, gds export
    mycell_list=['ser2to1_body', 'ser2to1',  
                 'ser' + str(ser_num_bits) + 'to1_ser2to1_body',
                 'ser' + str(ser_num_bits) + 'to1_ser2to1',
                 'ser' + str(ser_num_bits) + 'to1',
                ]

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

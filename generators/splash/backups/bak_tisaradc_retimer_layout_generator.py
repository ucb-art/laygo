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

"""ADC library
"""
import laygo
import numpy as np
from math import log
import yaml
import os
import laygo.GridLayoutGeneratorHelper as laygenhelper #utility functions
#import logging;logging.basicConfig(level=logging.DEBUG)

def generate_boundary(laygen, objectname_pfix, placement_grid,
                      devname_bottom, devname_top, devname_left, devname_right,
                      shape_bottom=None, shape_top=None, shape_left=None, shape_right=None,
                      transform_bottom=None, transform_top=None, transform_left=None, transform_right=None,
                      origin=np.array([0, 0])):
    # generate a boundary structure to resolve boundary design rules
    pg = placement_grid
    # parameters
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

    # bottom
    dev_bottom = []
    dev_bottom.append(laygen.place("I" + objectname_pfix + 'BNDBTM0', devname_bottom[0], pg, xy=origin,
                                   shape=shape_bottom[0], transform=transform_bottom[0]))
    for i, d in enumerate(devname_bottom[1:]):
        dev_bottom.append(
            laygen.relplace(name="I" + objectname_pfix + 'BNDBTM' + str(i + 1), templatename=d, gridname=pg,
                            refinstname=dev_bottom[-1].name,
                            shape=shape_bottom[i + 1], transform=transform_bottom[i + 1]))
    dev_left = []
    dev_left.append(laygen.relplace(name="I" + objectname_pfix + 'BNDLFT0', templatename=devname_left[0], gridname=pg,
                                    refinstname=dev_bottom[0].name, direction='top',
                                    shape=shape_left[0], transform=transform_left[0]))
    for i, d in enumerate(devname_left[1:]):
        dev_left.append(laygen.relplace(name="I" + objectname_pfix + 'BNDLFT' + str(i + 1), templatename=d, gridname=pg,
                                        refinstname=dev_left[-1].name, direction='top',
                                        shape=shape_left[i + 1], transform=transform_left[i + 1]))
    dev_right = []
    dev_right.append(laygen.relplace(name="I" + objectname_pfix + 'BNDRHT0', templatename=devname_right[0], gridname=pg,
                                     refinstname=dev_bottom[-1].name, direction='top',
                                     shape=shape_right[0], transform=transform_right[0]))
    for i, d in enumerate(devname_right[1:]):
        dev_right.append(
            laygen.relplace(name="I" + objectname_pfix + 'BNDRHT' + str(i + 1), templatename=d, gridname=pg,
                            refinstname=dev_right[-1].name, direction='top',
                            shape=shape_right[i + 1], transform=transform_right[i + 1]))
    dev_top = []
    dev_top.append(laygen.relplace(name="I" + objectname_pfix + 'BNDTOP0', templatename=devname_top[0], gridname=pg,
                                   refinstname=dev_left[-1].name, direction='top',
                                   shape=shape_top[0], transform=transform_top[0]))
    for i, d in enumerate(devname_top[1:]):
        dev_top.append(laygen.relplace(name="I" + objectname_pfix + 'BNDTOP' + str(i + 1), templatename=d, gridname=pg,
                                       refinstname=dev_top[-1].name,
                                       shape=shape_top[i + 1], transform=transform_top[i + 1]))
    dev_right = []
    return [dev_bottom, dev_top, dev_left, dev_right]


def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin"""
    rvdd0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VSS', gridname, sort=True)

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0], rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0], rvss1_pin_xy[1])), gridname=gridname)


def generate_latch_ckb(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4,
                         m=2, origin=np.array([0, 0])):
    """generate clock delay """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    inv_name = 'inv_1x'
    latch_name = 'latch_2ck_' + str(m) + 'x'

    # placement
    iinv0 = laygen.place(name="I" + objectname_pfix + 'IINV0', templatename=inv_name,
                         gridname=pg, xy=origin, template_libname=templib_logic)
    ilatch0 = laygen.relplace(name="I" + objectname_pfix + 'ILATCH0', templatename=latch_name,
                              gridname=pg, refinstname=iinv0.name, template_libname=templib_logic)

    # internal pins
    pdict = laygen.get_inst_pin_xy(None, None, rg_m3m4)

    # internal routes
    x0 = laygen.get_inst_xy(name=iinv0.name, gridname=rg_m3m4)[0] + 1
    y0 = pdict[iinv0.name]['I'][0][1] + 0

    # route-clk
    rv0, rclk0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv0.name]['O'][0],
                                 pdict[ilatch0.name]['CLK'][0], rg_m3m4)
                                 # np.array([x0, y0 + 3]), rg_m3m4)
    # route-clkb
    rv0, rclkb0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv0.name]['I'][0],
                                 pdict[ilatch0.name]['CLKB'][0], rg_m3m4)
    print('test:', pdict[iinv0.name]['I'][0])
    # pins
    x1 = laygen.get_inst_pin_xy(ilatch0.name, 'O', rg_m3m4)[1][0]
    rh0, rout0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][3], pdict[ilatch0.name]['O'][0],
                                 np.array([x1, y0 + 4]), rg_m3m4)

    laygen.boundary_pin_from_rect(rout0, rg_m3m4, "O", laygen.layers['pin'][3], size=4, direction='top')
    in_xy = laygen.get_inst_pin_xy(ilatch0.name, 'I', rg_m3m4)
    laygen.pin(name='I', layer=laygen.layers['pin'][3], xy=in_xy, gridname=rg_m3m4)
    laygen.pin_from_rect('CLKB', laygen.layers['pin'][4], rclkb0, rg_m3m4)

    # power pin
    create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=iinv0,
                               inst_right=ilatch0)

def generate_retimer_slice(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4,
                           rg_m3m4_basic_thick, rg_m4m5_thick, num_bits=9, origin=np.array([0, 0])):
    """generate clock delay """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4
    tap_name='tap'

    #Calculate layout size
    x0=laygen.templates.get_template('sar_wsamp_bb_doubleSA', workinglib).xy[1][0]

    tap_origin = origin
    array_origin = origin + np.array([laygen.get_template_xy(name=tap_name, gridname=pg, libname=templib_logic)[0], 0])
    tapr_origin = np.array([laygen.get_template_xy(name='sar_wsamp_bb_doubleSA', gridname=pg, libname=workinglib)[0], 0]) \
                  - np.array([laygen.get_template_xy(name=tap_name, gridname=pg, libname=templib_logic)[0], 0])
    #Space calculation
    inv_name = 'inv_1x'
    latch_name = 'latch_ckb'
    space_name = 'space_1x'
    space4x_name = 'space_4x'
    space_width = laygen.get_template_xy(name = space_name, gridname = pg, libname = templib_logic)[0]
    space4_width = laygen.get_template_xy(name = space4x_name, gridname = pg, libname = templib_logic)[0]
    latch_array_width = num_bits*laygen.get_template_xy(name = latch_name, gridname = pg, libname = workinglib)[0]
    blank_width = tapr_origin[0] - array_origin[0] - latch_array_width
    m_space4 = int(blank_width / space4_width)
    m_space1 = int((blank_width-m_space4*space4_width)/space_width)

    # placement: first row
    # iinv0 = laygen.place(name="I" + objectname_pfix + 'IINV0', templatename=inv_name,
    #                      gridname=pg, xy=origin, template_libname=templib_logic)
    itapl2 = laygen.relplace(name="I" + objectname_pfix + 'ITAPL2', templatename=tap_name,
                              gridname=pg, refinstname=None, xy=tap_origin, template_libname=templib_logic)
    itapr2 = laygen.relplace(name="I" + objectname_pfix + 'ITAPR2', templatename=tap_name,
                              gridname = pg, refinstname = None, xy = tapr_origin, template_libname = templib_logic)
    ilatch2 = laygen.relplace(name="I" + objectname_pfix + 'ILATCH2', templatename=latch_name, shape=[num_bits,1],
                              gridname=pg, refinstname=itapl2.name, template_libname=workinglib)
    ispace4x2 = laygen.relplace(name="I" + objectname_pfix + 'ISP4x2', templatename=space4x_name, shape=[m_space4,1],
                              gridname=pg, refinstname=ilatch2.name, template_libname=templib_logic)
    if m_space4 == 0:
        ispace1x2 = laygen.relplace(name="I" + objectname_pfix + 'ISP1x2', templatename=space_name, shape=[m_space1, 1],
                                   gridname=pg, refinstname=ilatch2.name, template_libname=templib_logic)
    else:
        ispace1x2 = laygen.relplace(name="I" + objectname_pfix + 'ISP1x2', templatename=space_name, shape=[m_space1,1],
                              gridname=pg, refinstname=ispace4x2.name, template_libname=templib_logic)
    #second row
    itapl1 = laygen.relplace(name="I" + objectname_pfix + 'ITAPL1', templatename=tap_name, transform='MX',
                             gridname=pg, refinstname=itapl2.name, direction='top', template_libname=templib_logic)
    itapr1 = laygen.relplace(name="I" + objectname_pfix + 'ITAPR1', templatename=tap_name, transform='MX',
                             gridname=pg, refinstname=itapr2.name, direction='top', template_libname=templib_logic)
    ilatch1 = laygen.relplace(name="I" + objectname_pfix + 'ILATCH1', templatename=latch_name, shape=[num_bits, 1], transform='MX',
                              gridname=pg, refinstname=itapl1.name, template_libname=workinglib)
    ispace4x1 = laygen.relplace(name="I" + objectname_pfix + 'ISP4x1', templatename=space4x_name,
                                shape=[m_space4, 1], transform='MX',
                                gridname=pg, refinstname=ilatch1.name, template_libname=templib_logic)
    if m_space4 == 0:
        ispace1x1 = laygen.relplace(name="I" + objectname_pfix + 'ISP1x1', templatename=space_name,
                                    shape=[m_space1, 1], transform='MX',
                                    gridname=pg, refinstname=ilatch1.name, template_libname=templib_logic)
    else:
        ispace1x1 = laygen.relplace(name="I" + objectname_pfix + 'ISP1x1', templatename=space_name,
                                    shape=[m_space1, 1], transform='MX',
                                    gridname=pg, refinstname=ispace4x1.name, template_libname=templib_logic)
    # second row
    itapl0 = laygen.relplace(name="I" + objectname_pfix + 'ITAPL0', templatename=tap_name,
                             gridname=pg, refinstname=itapl1.name, direction='top', template_libname=templib_logic)
    itapr0 = laygen.relplace(name="I" + objectname_pfix + 'ITAPR0', templatename=tap_name,
                             gridname=pg, refinstname=itapr1.name, direction='top', template_libname=templib_logic)
    ilatch0 = laygen.relplace(name="I" + objectname_pfix + 'ILATCH0', templatename=latch_name, shape=[num_bits, 1],
                              gridname=pg, refinstname=itapl0.name, template_libname=workinglib)
    ispace4x0 = laygen.relplace(name="I" + objectname_pfix + 'ISP4x0', templatename=space4x_name,
                                shape=[m_space4, 1],
                                gridname=pg, refinstname=ilatch0.name, template_libname=templib_logic)
    if m_space4 == 0:
        ispace1x0 = laygen.relplace(name="I" + objectname_pfix + 'ISP1x0', templatename=space_name,
                                    shape=[m_space1, 1],
                                    gridname=pg, refinstname=ilatch0.name, template_libname=templib_logic)
    else:
        ispace1x0 = laygen.relplace(name="I" + objectname_pfix + 'ISP1x0', templatename=space_name,
                                    shape=[m_space1, 1],
                                    gridname=pg, refinstname=ispace4x0.name, template_libname=templib_logic)
    # internal pins
    pdict = laygen.get_inst_pin_xy(None, None, rg_m3m4)

    # # internal routes
    # x0 = laygen.get_inst_xy(name=iinv0.name, gridname=rg_m3m4)[0] + 1
    # y0 = pdict[iinv0.name]['I'][0][1] + 0
    #
    # route-clkb
    rclkb0 = laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ilatch0.name, 'CLKB', rg_m3m4, index=[0, 0])[0],
                          xy1=laygen.get_inst_pin_xy(ilatch0.name, 'CLKB', rg_m3m4, index=[num_bits-1, 0])[0], gridname0=rg_m3m4)
    rclkb1 = laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ilatch1.name, 'CLKB', rg_m3m4, index=[0, 0])[0],
                          xy1=laygen.get_inst_pin_xy(ilatch1.name, 'CLKB', rg_m3m4, index=[num_bits-1, 0])[0], gridname0=rg_m3m4)
    rclkb2 = laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ilatch2.name, 'CLKB', rg_m3m4, index=[0, 0])[0],
                          xy1=laygen.get_inst_pin_xy(ilatch2.name, 'CLKB', rg_m3m4, index=[num_bits-1, 0])[0], gridname0=rg_m3m4)

    # route-internal signals
    for i in range(num_bits):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                laygen.get_inst_pin_xy(ilatch0.name, 'O', rg_m3m4, index=[i, 0])[0],
                                laygen.get_inst_pin_xy(ilatch1.name, 'I', rg_m3m4, index=[i, 0])[0],
                                laygen.get_inst_pin_xy(ilatch0.name, 'O', rg_m3m4, index=[i, 0])[0][1] - 4, rg_m3m4)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                laygen.get_inst_pin_xy(ilatch1.name, 'O', rg_m3m4, index=[i, 0])[0],
                                laygen.get_inst_pin_xy(ilatch2.name, 'I', rg_m3m4, index=[i, 0])[0],
                                laygen.get_inst_pin_xy(ilatch1.name, 'O', rg_m3m4, index=[i, 0])[0][1] - 5, rg_m3m4)

    # pins
    laygen.pin_from_rect('clkb0', laygen.layers['pin'][4], rclkb0, rg_m3m4)
    laygen.pin_from_rect('clkb1', laygen.layers['pin'][4], rclkb1, rg_m3m4)
    laygen.pin_from_rect('clkb2', laygen.layers['pin'][4], rclkb2, rg_m3m4)
    for i in range(num_bits):
        in_xy = laygen.get_inst_pin_xy(ilatch0.name, 'I', rg_m3m4, index=[i,0])
        laygen.pin(name='in<%d>'%i, layer=laygen.layers['pin'][3], xy=in_xy, gridname=rg_m3m4)
        out_xy = laygen.get_inst_pin_xy(ilatch2.name, 'O', rg_m3m4, index=[i,0])
        laygen.pin(name='out<%d>'%i, layer=laygen.layers['pin'][3], xy=out_xy, gridname=rg_m3m4)

    # power pin
    pwr_dim=laygen.get_template_xy(name=itapl0.cellname, gridname=rg_m2m3, libname=itapl0.libname)
    rvddl = []
    rvssl = []
    rvddr = []
    rvssr = []
    for i in range(0, int(pwr_dim[0]/2)):
        rvddl.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl2.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl0.name, refpinname1='VDD', refinstindex1=np.array([0, 0])))
        rvssl.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl2.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl0.name, refpinname1='VDD', refinstindex1=np.array([0, 0])))
        laygen.via(None, xy=np.array([2*i+1, 0]), gridname=rg_m2m3, refinstname=itapl0.name, refpinname='VDD')
        laygen.via(None, xy=np.array([2*i+1, 0]), gridname=rg_m2m3, refinstname=itapl1.name, refpinname='VDD')
        laygen.via(None, xy=np.array([2*i+1, 0]), gridname=rg_m2m3, refinstname=itapl2.name, refpinname='VDD')
        laygen.via(None, xy=np.array([2 * i + 2, 0]), gridname=rg_m2m3, refinstname=itapl0.name, refpinname='VSS')
        laygen.via(None, xy=np.array([2 * i + 2, 0]), gridname=rg_m2m3, refinstname=itapl1.name, refpinname='VSS')
        laygen.via(None, xy=np.array([2 * i + 2, 0]), gridname=rg_m2m3, refinstname=itapl2.name, refpinname='VSS')
        laygen.pin(name = 'VDDL'+str(i), layer = laygen.layers['pin'][3], refobj = rvddl[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSSL'+str(i), layer = laygen.layers['pin'][3], refobj = rvssl[-1], gridname=rg_m2m3, netname='VSS')
        rvddr.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr2.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr0.name, refpinname1='VDD', refinstindex1=np.array([0, 0])))
        rvssr.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr2.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr0.name, refpinname1='VDD', refinstindex1=np.array([0, 0])))
        laygen.via(None, xy=np.array([2 * i + 2, 0]), gridname=rg_m2m3, refinstname=itapr0.name, refpinname='VDD')
        laygen.via(None, xy=np.array([2 * i + 2, 0]), gridname=rg_m2m3, refinstname=itapr1.name, refpinname='VDD')
        laygen.via(None, xy=np.array([2 * i + 2, 0]), gridname=rg_m2m3, refinstname=itapr2.name, refpinname='VDD')
        laygen.via(None, xy=np.array([2 * i + 1, 0]), gridname=rg_m2m3, refinstname=itapr0.name, refpinname='VSS')
        laygen.via(None, xy=np.array([2 * i + 1, 0]), gridname=rg_m2m3, refinstname=itapr1.name, refpinname='VSS')
        laygen.via(None, xy=np.array([2 * i + 1, 0]), gridname=rg_m2m3, refinstname=itapr2.name, refpinname='VSS')
        laygen.pin(name = 'VDDR'+str(i), layer = laygen.layers['pin'][3], refobj = rvddr[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSSR'+str(i), layer = laygen.layers['pin'][3], refobj = rvssr[-1], gridname=rg_m2m3, netname='VSS')

    # # VDD/VSS M4
    # rvddl_m4, rvssl_m4 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M4_L', layer=laygen.layers['metal'][4],
    #                             gridname=rg_m3m4_basic_thick, netnames=['VDD', 'VSS'], direction='x',
    #                             input_rails_rect=[rvddl, rvssl], generate_pin=False,
    #                             overwrite_start_coord=0, overwrite_end_coord=None, overwrite_num_routes=None,
    #                             offset_start_index=0, offset_end_index=0)
    # rvddr_m4, rvssr_m4 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M4_R', layer=laygen.layers['metal'][4],
    #                             gridname=rg_m3m4_basic_thick, netnames=['VDD', 'VSS'], direction='x',
    #                             input_rails_rect=[rvddr, rvssr], generate_pin=False, overwrite_start_coord=None,
    #                             overwrite_end_coord=laygen.get_template_xy('sar_wsamp_bb_doubleSA', rg_m3m4_basic_thick, workinglib)[0],
    #                             overwrite_num_routes=None, offset_start_index=0, offset_end_index=0)
    #
    # # VDD/VSS M5
    # rvddl_m5, rvssl_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M5_L', layer=laygen.layers['pin'][5],
    #                             gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y',
    #                             input_rails_rect=[rvddl_m4, rvssl_m4], generate_pin=True,
    #                             overwrite_start_coord=0, overwrite_end_coord=None, overwrite_num_routes=None,
    #                             offset_start_index=0, offset_end_index=0)
    # rvddr_m5, rvssr_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M5_R', layer=laygen.layers['pin'][5],
    #                             gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y',
    #                             input_rails_rect=[rvddr_m4, rvssr_m4], generate_pin=True,
    #                             overwrite_start_coord=0, overwrite_end_coord=None, overwrite_num_routes=None,
    #                             offset_start_index=0, offset_end_index=-2)

def generate_adc_retimer(laygen, objectname_pfix, ret_libname, sar_libname, clkdist_libname, templib_logic,
                                ret_name, sar_name, clkdist_name, space_1x_name, m_ibuf, m_obuf, slice_order,
                                placement_grid,
                                routing_grid_m3m4, routing_grid_m4m5,
                                routing_grid_m4m5_thick, routing_grid_m4m5_basic_thick,
                                routing_grid_m5m6, routing_grid_m5m6_thick, routing_grid_m5m6_thick_basic,
                                routing_grid_m6m7_thick, 
                                num_bits=9, num_slices=8, clkdist_offset=14.4, origin=np.array([0, 0])):
    """generate sar array """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m4m5_thick = routing_grid_m4m5_thick
    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic
    rg_m6m7_thick = routing_grid_m6m7_thick

    #boundaries
    x0=laygen.templates.get_template('sar_wsamp_bb_doubleSA', workinglib).xy[1][0]*num_slices
       # laygen.templates.get_template('boundary_left').xy[1][0]*2
    m_bnd_float = x0 / laygen.templates.get_template('boundary_bottom').xy[1][0]
    m_bnd = int(m_bnd_float)
    if not m_bnd_float == m_bnd:
        m_bnd += 1
    # print('m_bnd:', m_bnd, 'x0:', x0, 'bnd:', m_bnd_float)

    devname_bnd_left = []
    devname_bnd_right = []
    transform_bnd_left = []
    transform_bnd_right = []
    num_row=4
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

    # Define clock phases
    ck_phase_2 = num_slices - 1
    ck_phase_1 = int(num_slices / 2) - 1
    ck_phase_0_0 = int((int(num_slices / 2) + 1) % num_slices)
    ck_phase_0_1 = 1
    ck_phase_out = ck_phase_1
    ck_phase_buf = sorted(set([ck_phase_2, ck_phase_1, ck_phase_0_0, ck_phase_0_1]))

    # Calculate origins for placement
    ret_name = 'adc_retimer_slice'
    ibuf_name = 'inv_'+str(m_ibuf)+'x'
    obuf_name = 'inv_'+str(m_obuf)+'x'
    space_name = 'space_1x'
    space4x_name = 'space_4x'
    tap_name = 'tap'
    space_width = laygen.get_template_xy(name=space_name, gridname=pg, libname=templib_logic)[0]
    space4_width = laygen.get_template_xy(name=space4x_name, gridname=pg, libname=templib_logic)[0]
    tap_width = laygen.get_template_xy(name=tap_name, gridname=pg, libname=templib_logic)[0]
    array_origin = origin + laygen.get_inst_xy(name = bnd_bottom[0].name, gridname = pg) \
                   + laygen.get_template_xy(name = bnd_bottom[0].cellname, gridname = pg)
    ckbuf_2_origin = origin + laygen.get_template_xy(name=bnd_bottom[0].cellname, gridname=pg) \
                    + [0, laygen.get_template_xy(name=ret_name, gridname=pg, libname=workinglib)[1]] \
                    + [0, laygen.get_template_xy(name=ibuf_name, gridname=pg, libname=templib_logic)[1]] \
                    + [laygen.get_template_xy(name=ret_name, gridname=pg, libname=workinglib)[0]*num_slices/2, 0] \
                    - [laygen.get_template_xy(name=ibuf_name, gridname=pg, libname=templib_logic)[0]*6, 0] \
                    - [tap_width, 0]
    ckbuf_1_origin = origin + laygen.get_template_xy(name=bnd_bottom[0].cellname, gridname=pg) \
                     + [0, laygen.get_template_xy(name=ret_name, gridname=pg, libname=workinglib)[1]] \
                     + [0, laygen.get_template_xy(name=ibuf_name, gridname=pg, libname=templib_logic)[1]] \
                     + [laygen.get_template_xy(name=ret_name, gridname=pg, libname=workinglib)[0] * num_slices / 2, 0] \
                     - [laygen.get_template_xy(name=ibuf_name, gridname=pg, libname=templib_logic)[0] * 0, 0] \
                     + [tap_width, 0]
    ckbuf_0_0_origin = origin + laygen.get_template_xy(name=bnd_bottom[0].cellname, gridname=pg) \
                     + [0, laygen.get_template_xy(name=ret_name, gridname=pg, libname=workinglib)[1]] \
                     + [0, laygen.get_template_xy(name=ibuf_name, gridname=pg, libname=templib_logic)[1]] \
                     + [laygen.get_template_xy(name=ret_name, gridname=pg, libname=workinglib)[0] * num_slices / 4, 0] \
                     - [laygen.get_template_xy(name=ibuf_name, gridname=pg, libname=templib_logic)[0] * 6, 0] \
                     - [2 * space4_width, 0]
    ckbuf_0_1_origin = origin + laygen.get_template_xy(name=bnd_bottom[0].cellname, gridname=pg) \
                       + [0, laygen.get_template_xy(name=ret_name, gridname=pg, libname=workinglib)[1]] \
                       + [0, laygen.get_template_xy(name=ibuf_name, gridname=pg, libname=templib_logic)[1]] \
                       + [laygen.get_template_xy(name=ret_name, gridname=pg, libname=workinglib)[0] * num_slices / 4 * 3, 0] \
                       - [laygen.get_template_xy(name=ibuf_name, gridname=pg, libname=templib_logic)[0] * 6, 0] \
                       - [2 * space4_width, 0]

    # Space calculation
    blank0_width = ckbuf_0_0_origin[0] - array_origin[0] - tap_width
    m_space4_0 = int(blank0_width / space4_width)
    m_space1_0 = int((blank0_width - m_space4_0 * space4_width) / space_width)
    blank1_width = ckbuf_2_origin[0] - ckbuf_0_0_origin[0] \
                   - laygen.get_template_xy(name=ibuf_name, gridname=pg, libname=templib_logic)[0] * 6
    m_space4_1 = int(blank1_width / space4_width)
    m_space1_1 = int((blank1_width - m_space4_1 * space4_width) / space_width)
    blank2_width = ckbuf_0_1_origin[0] - ckbuf_1_origin[0] \
                   - laygen.get_template_xy(name=ibuf_name, gridname=pg, libname=templib_logic)[0] * 6 \
                   - laygen.get_template_xy(name=obuf_name, gridname=pg, libname=templib_logic)[0] * 2
    m_space4_2 = int(blank2_width / space4_width)
    m_space1_2 = int((blank2_width - m_space4_2 * space4_width) / space_width)
    blank3_width = laygen.get_inst_xy(name = bnd_bottom[-1].name, gridname = pg)[0] \
                   - ckbuf_0_1_origin[0] \
                   - laygen.get_template_xy(name=ibuf_name, gridname=pg, libname=templib_logic)[0] * 6 \
                   - tap_width
    m_space4_3 = int(blank3_width / space4_width)
    m_space1_3 = int((blank3_width - m_space4_3 * space4_width) / space_width)

    # placement
    iret = laygen.relplace(name="I" + objectname_pfix + 'IRET', templatename=ret_name, shape=[num_slices, 1],
                             gridname=pg, refinstname=None, xy=array_origin, template_libname=workinglib)
    ickbuf_2 = laygen.relplace(name="I" + objectname_pfix + 'ICKBUF2', templatename=ibuf_name, shape=[6, 1],transform='MX',
                             gridname=pg, refinstname=None, xy=ckbuf_2_origin, template_libname=templib_logic)
    ickbuf_1 = laygen.relplace(name="I" + objectname_pfix + 'ICKBUF1', templatename=ibuf_name, shape=[6, 1],
                               transform='MX',
                               gridname=pg, refinstname=None, xy=ckbuf_1_origin, template_libname=templib_logic)
    ickbuf_0_0 = laygen.relplace(name="I" + objectname_pfix + 'ICKBUF0_0', templatename=ibuf_name, shape=[6, 1],
                               transform='MX',
                               gridname=pg, refinstname=None, xy=ckbuf_0_0_origin, template_libname=templib_logic)
    ickbuf_0_1 = laygen.relplace(name="I" + objectname_pfix + 'ICKBUF0_1', templatename=ibuf_name, shape=[6, 1],
                                 transform='MX',
                                 gridname=pg, refinstname=None, xy=ckbuf_0_1_origin, template_libname=templib_logic)
    ickbuf_o = laygen.relplace(name="I" + objectname_pfix + 'ICKOBUF', templatename=obuf_name, shape=[2, 1],
                               transform='MX',
                               gridname=pg, refinstname=ickbuf_1.name, template_libname=templib_logic)
    itapl = laygen.relplace(name="I" + objectname_pfix + 'ITAP0', templatename=tap_name, shape=[1, 1], transform='MX',
                            gridname=pg, refinstname=ickbuf_0_0.name, direction='left', template_libname=templib_logic)
    ispace4x_0 = laygen.relplace(name="I" + objectname_pfix + 'ISP4x0', templatename=space4x_name, shape=[m_space4_0, 1],transform='MX',
                                gridname=pg, refinstname=itapl.name, direction='left', template_libname=templib_logic)
    ispace1x_0 = laygen.relplace(name="I" + objectname_pfix + 'ISP1x0', templatename=space_name, shape=[m_space1_0, 1],transform='MX',
                                gridname=pg, refinstname=ispace4x_0.name, direction='left', template_libname=templib_logic)
    ispace4x_1 = laygen.relplace(name="I" + objectname_pfix + 'ISP4x1', templatename=space4x_name,transform='MX',
                                 shape=[m_space4_1, 1], gridname=pg, refinstname=ickbuf_0_0.name,
                                 template_libname=templib_logic)
    ispace1x_1 = laygen.relplace(name="I" + objectname_pfix + 'ISP1x1', templatename=space_name, shape=[m_space1_1, 1],transform='MX',
                                 gridname=pg, refinstname=ispace4x_1.name, template_libname=templib_logic)
    ispace4x_2 = laygen.relplace(name="I" + objectname_pfix + 'ISP4x2', templatename=space4x_name,transform='MX',
                                 shape=[m_space4_2, 1], gridname=pg, refinstname=ickbuf_o.name,
                                 template_libname=templib_logic)
    ispace1x_2 = laygen.relplace(name="I" + objectname_pfix + 'ISP1x2', templatename=space_name, shape=[m_space1_2, 1],transform='MX',
                                 gridname=pg, refinstname=ispace4x_2.name, template_libname=templib_logic)
    itapr = laygen.relplace(name="I" + objectname_pfix + 'ITAPR', templatename=tap_name, shape=[1, 1], transform='MX',
                            gridname=pg, refinstname=ickbuf_0_1.name, template_libname=templib_logic)
    ispace4x_3 = laygen.relplace(name="I" + objectname_pfix + 'ISP4x3', templatename=space4x_name,transform='MX',
                                 shape=[m_space4_3, 1], gridname=pg, refinstname=itapr.name,
                                 template_libname=templib_logic)
    ispace1x_3 = laygen.relplace(name="I" + objectname_pfix + 'ISP1x3', templatename=space_name, shape=[m_space1_3, 1],transform='MX',
                                 gridname=pg, refinstname=ispace4x_3.name, template_libname=templib_logic)

    itap_mid = laygen.relplace(name="I" + objectname_pfix + 'ITAP_m', templatename=tap_name,transform='MX',
                                 shape=[2, 1], gridname=pg, refinstname=ickbuf_2.name,
                                 template_libname=templib_logic)


    #prboundary
    sar_size = laygen.templates.get_template(sar_name, libname=sar_libname).size
    ret_size = iret.size
    print(ret_size)
    bnd_size = bnd_bottom[0].size
    space_size = laygen.templates.get_template(space_1x_name, libname=templib_logic).size
    laygen.add_rect(None, np.array([origin, 2*bnd_size+[ret_size[0]*num_slices, ret_size[1]+space_size[1]]]), laygen.layers['prbnd'])

    # clk buf route
    for i in range(5):
        rck2 = laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ickbuf_2.name, 'I', rg_m3m4, index=[i, 0])[0],
                          xy1=laygen.get_inst_pin_xy(ickbuf_2.name, 'I', rg_m3m4, index=[i+1, 0])[0],
                          via0=[0,0], via1=[0,0], gridname0=rg_m3m4)
        rck1 = laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ickbuf_1.name, 'I', rg_m3m4, index=[i, 0])[0],
                          xy1=laygen.get_inst_pin_xy(ickbuf_1.name, 'I', rg_m3m4, index=[i+1, 0])[0],
                          via0=[0,0], via1=[0,0], gridname0=rg_m3m4)
        rck0_0 = laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ickbuf_0_0.name, 'I', rg_m3m4, index=[i, 0])[0],
                          xy1=laygen.get_inst_pin_xy(ickbuf_0_0.name, 'I', rg_m3m4, index=[i+1, 0])[0],
                          via0=[0,0], via1=[0,0], gridname0=rg_m3m4)
        rck0_1 = laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ickbuf_0_1.name, 'I', rg_m3m4, index=[i, 0])[0],
                          xy1=laygen.get_inst_pin_xy(ickbuf_0_1.name, 'I', rg_m3m4, index=[i+1, 0])[0],
                          via0=[0,0], via1=[0,0], gridname0=rg_m3m4)
        rckb2 = laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ickbuf_2.name, 'O', rg_m3m4, index=[i, 0])[1],
                          xy1=laygen.get_inst_pin_xy(ickbuf_2.name, 'O', rg_m3m4, index=[i+1, 0])[1],
                          via0=[0,0], via1=[0,0], gridname0=rg_m3m4)
        rckb1 = laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ickbuf_1.name, 'O', rg_m3m4, index=[i, 0])[1],
                          xy1=laygen.get_inst_pin_xy(ickbuf_1.name, 'O', rg_m3m4, index=[i+1, 0])[1],
                          via0=[0,0], via1=[0,0], gridname0=rg_m3m4)
        rckb0_0 = laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ickbuf_0_0.name, 'O', rg_m3m4, index=[i, 0])[1],
                          xy1=laygen.get_inst_pin_xy(ickbuf_0_0.name, 'O', rg_m3m4, index=[i+1, 0])[1],
                          via0=[0,0], via1=[0,0], gridname0=rg_m3m4)
        rckb0_1 = laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ickbuf_0_1.name, 'O', rg_m3m4, index=[i, 0])[1],
                          xy1=laygen.get_inst_pin_xy(ickbuf_0_1.name, 'O', rg_m3m4, index=[i+1, 0])[1],
                          via0=[0,0], via1=[0,0], gridname0=rg_m3m4)
    for i in range(1):
        rcko = laygen.route(None, laygen.layers['metal'][4],
                            xy0=laygen.get_inst_pin_xy(ickbuf_o.name, 'I', rg_m3m4, index=[i, 0])[1],
                            xy1=laygen.get_inst_pin_xy(ickbuf_o.name, 'I', rg_m3m4, index=[i + 1, 0])[1],
                            via0=[0, 0], via1=[0, 0], gridname0=rg_m3m4)
        rckbo = laygen.route(None, laygen.layers['metal'][4],
                            xy0=laygen.get_inst_pin_xy(ickbuf_o.name, 'O', rg_m3m4, index=[i, 0])[0],
                            xy1=laygen.get_inst_pin_xy(ickbuf_o.name, 'O', rg_m3m4, index=[i + 1, 0])[0],
                            via0=[0, 0], via1=[0, 0], gridname0=rg_m3m4)
        rckbo_m5 = laygen.route(None, laygen.layers['metal'][5],
                            xy0=laygen.get_inst_pin_xy(ickbuf_o.name, 'O', rg_m3m4, index=[0, 0])[0],
                            xy1=[laygen.get_inst_pin_xy(ickbuf_o.name, 'O', rg_m3m4, index=[0, 0])[0][0], 0],
                            via0=[0, 0], gridname0=rg_m4m5)
    laygen.route(None, laygen.layers['metal'][4], [0, 0], [0, 0], rg_m3m4, refobj0=rckb1, refobj1=rcko)

    # clkb2 route
    rclkb2_m4 = laygen.route(None, laygen.layers['metal'][4],
                           xy0=laygen.get_inst_pin_xy(iret.name, 'clkb2', rg_m3m4, index=[0, 0])[0],
                           xy1=laygen.get_inst_pin_xy(iret.name, 'clkb2', rg_m3m4, index=[num_slices-1, 0])[1],
                           gridname0=rg_m4m5)
    rh0, rclkb2_m5 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                           xy0=laygen.get_rect_xy(rclkb2_m4.name, rg_m4m5)[0], xy1=laygen.get_rect_xy(rckb2.name, rg_m4m5)[0],
                           via1=[0, 0], gridname0=rg_m4m5)
    # clkb1 route
    rclkb1_m4 = laygen.route(None, laygen.layers['metal'][4],
                           xy0=laygen.get_inst_pin_xy(iret.name, 'clkb1', rg_m3m4, index=[0, 0])[0],
                           xy1=laygen.get_inst_pin_xy(iret.name, 'clkb1', rg_m3m4, index=[num_slices-1, 0])[1],
                           gridname0=rg_m4m5)
    rh0, rclkb1_m5 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                           xy0=laygen.get_rect_xy(rclkb1_m4.name, rg_m4m5)[0], xy1=laygen.get_rect_xy(rckb1.name, rg_m4m5)[0],
                           via1=[0, 0], gridname0=rg_m4m5)
    # clkb0_0 route
    rclkb0_0_m4 = laygen.route(None, laygen.layers['metal'][4],
                           xy0=laygen.get_inst_pin_xy(iret.name, 'clkb0', rg_m3m4, index=[0, 0])[0],
                           xy1=laygen.get_inst_pin_xy(iret.name, 'clkb0', rg_m3m4, index=[int(num_slices/2)-1, 0])[1],
                           gridname0=rg_m4m5)
    rh0, rclkb0_0_m5 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                           xy0=laygen.get_rect_xy(rclkb0_0_m4.name, rg_m4m5)[0], xy1=laygen.get_rect_xy(rckb0_0.name, rg_m4m5)[0],
                           via1=[0, 0], gridname0=rg_m4m5)
    # clkb0_1 route
    rclkb0_1_m4 = laygen.route(None, laygen.layers['metal'][4],
                           xy0=laygen.get_inst_pin_xy(iret.name, 'clkb0', rg_m3m4, index=[int(num_slices/2), 0])[0],
                           xy1=laygen.get_inst_pin_xy(iret.name, 'clkb0', rg_m3m4, index=[num_slices-1, 0])[1],
                           gridname0=rg_m4m5)
    rh0, rclkb0_0_m5 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                           xy0=laygen.get_rect_xy(rclkb0_1_m4.name, rg_m4m5)[0], xy1=laygen.get_rect_xy(rckb0_1.name, rg_m4m5)[0],
                           via1=[0, 0], gridname0=rg_m4m5)

    # Output routing/pins
    for i in range(num_slices):
        for j in range(num_bits):
            rout = laygen.route(None, laygen.layers['metal'][3],
                            xy0=laygen.get_inst_pin_xy(iret.name, 'out<%d>'%j, rg_m3m4, index=[i, 0])[0],
                            xy1=[laygen.get_inst_pin_xy(iret.name, 'out<%d>'%j, rg_m3m4, index=[i, 0])[0][0], 0],
                            gridname0=rg_m3m4)
            # laygen.boundary_pin_from_rect(rout, rg_m3m4, 'out_'+str(i)+'<'+str(j)+'>', laygen.layers['pin'][3], size=4, direction='bottom')
            laygen.boundary_pin_from_rect(rout, rg_m3m4, 'out_'+str(slice_order[i])+'<'+str(j)+'>', laygen.layers['pin'][3], size=4, direction='bottom')

    # Input pins
    for i in range(num_slices):
        for j in range(num_bits):
            pxy = laygen.get_inst_pin_xy(iret.name, 'in<%d>'%j, rg_m3m4, index=[i, 0])
            laygen.pin(name='in_'+str(slice_order[i])+'<'+str(j)+'>', layer=laygen.layers['pin'][3], xy=pxy, gridname=rg_m3m4)

    # Clock pins
    laygen.pin_from_rect('clk'+str(ck_phase_2), laygen.layers['pin'][4], rck2, rg_m3m4)
    laygen.pin_from_rect('clk'+str(ck_phase_1), laygen.layers['pin'][4], rck1, rg_m3m4)
    laygen.pin_from_rect('clk'+str(ck_phase_0_0), laygen.layers['pin'][4], rck0_0, rg_m3m4)
    laygen.pin_from_rect('clk'+str(ck_phase_0_1), laygen.layers['pin'][4], rck0_1, rg_m3m4)
    laygen.boundary_pin_from_rect(rckbo_m5, rg_m4m5, 'ck_out', laygen.layers['pin'][5], size=4, direction='bottom')

    # Power route: M3
    ret_template = laygen.templates.get_template(ret_name, workinglib)
    ret_pins = ret_template.pins
    ret_xy=iret.xy
    y0=laygen.get_inst_pin_xy(ickbuf_2.name, 'VSS', rg_m2m3)[0][1]
    vddlcnt=0
    vsslcnt=0
    vddrcnt = 0
    vssrcnt = 0
    vddl_list=[]
    vssl_list=[]
    vddr_list = []
    vssr_list = []
    for pn, p in ret_pins.items():
        if pn.startswith('VDDL'):
            vddlcnt+=1
            vddl_list.append(pn)
        if pn.startswith('VDDR'):
            vddrcnt += 1
            vddr_list.append(pn)
        if pn.startswith('VSSL'):
            vsslcnt+=1
            vssl_list.append(pn)
        if pn.startswith('VSSR'):
            vssrcnt += 1
            vssr_list.append(pn)
    rvddl_m3=[]
    rvssl_m3=[]
    rvddr_m3 = []
    rvssr_m3 = []
    rvdd_m5 = []
    rvss_m5 = []
    for i in range(num_slices):
        # M3
        for j in range(vddlcnt):
            pxy=laygen.get_inst_pin_xy(iret.name, vddl_list[j], rg_m2m3, index=[i,0])[1]
            rvddl_m3.append(laygen.route(None, laygen.layers['metal'][3], pxy, [pxy[0], y0], rg_m2m3))
        for j in range(vsslcnt):
            pxy = laygen.get_inst_pin_xy(iret.name, vssl_list[j], rg_m2m3, index=[i, 0])[1]
            rvssl_m3.append(laygen.route(None, laygen.layers['metal'][3], pxy, [pxy[0], y0], rg_m2m3, via1=[0, 0]))
        for j in range(vddrcnt):
            pxy=laygen.get_inst_pin_xy(iret.name, vddr_list[j], rg_m2m3, index=[i,0])[1]
            rvddr_m3.append(laygen.route(None, laygen.layers['metal'][3], pxy, [pxy[0], y0], rg_m2m3))
        for j in range(vssrcnt):
            pxy = laygen.get_inst_pin_xy(iret.name, vssr_list[j], rg_m2m3, index=[i, 0])[1]
            rvssr_m3.append(laygen.route(None, laygen.layers['metal'][3], pxy, [pxy[0], y0], rg_m2m3, via1=[0, 0]))
        # M4
        rvddl_m4, rvssl_m4 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M4L',
                                                                               layer=laygen.layers['metal'][4],
                                                                               gridname=rg_m3m4_basic_thick,
                                                                               netnames=['VDD', 'VSS'], direction='x',
                                                                               input_rails_rect=[rvddl_m3, rvssl_m3],
                                                                               generate_pin=False,
                                                                               overwrite_start_coord=None,
                                                                               overwrite_end_coord=None,
                                                                               overwrite_num_routes=None,
                                                                               offset_start_index=0,
                                                                               offset_end_index=0)
        rvddr_m4, rvssr_m4 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M4R',
                                                                             layer=laygen.layers['metal'][4],
                                                                             gridname=rg_m3m4_basic_thick,
                                                                             netnames=['VDD', 'VSS'], direction='x',
                                                                             input_rails_rect=[rvddr_m3, rvssr_m3],
                                                                             generate_pin=False,
                                                                             overwrite_start_coord=None,
                                                                             overwrite_end_coord=None,
                                                                             overwrite_num_routes=None,
                                                                             offset_start_index=0,
                                                                             offset_end_index=0)
        rvddl_m3 = []
        rvssl_m3 = []
        rvddr_m3 = []
        rvssr_m3 = []
        rvddl_m5, rvssl_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M5L',
                                                                               layer=laygen.layers['metal'][5],
                                                                               gridname=rg_m4m5_thick,
                                                                               netnames=['VDD', 'VSS'], direction='y',
                                                                               input_rails_rect=[rvddl_m4, rvssl_m4],
                                                                               generate_pin=False,
                                                                               overwrite_start_coord=0,
                                                                               overwrite_end_coord=None,
                                                                               overwrite_num_routes=None,
                                                                               offset_start_index=0,
                                                                               offset_end_index=0)
        rvddr_m5, rvssr_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M5R',
                                                                               layer=laygen.layers['metal'][5],
                                                                               gridname=rg_m4m5_thick,
                                                                               netnames=['VDD', 'VSS'], direction='y',
                                                                               input_rails_rect=[rvddr_m4, rvssr_m4],
                                                                               generate_pin=False,
                                                                               overwrite_start_coord=0,
                                                                               overwrite_end_coord=None,
                                                                               overwrite_num_routes=None,
                                                                               offset_start_index=0,
                                                                               offset_end_index=0)
        rvdd_m5 += rvddl_m5
        rvdd_m5 += rvddr_m5
        rvss_m5 += rvssl_m5
        rvss_m5 += rvssr_m5
    rvdd_m6, rvss_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M6',
                                                                           layer=laygen.layers['pin'][6],
                                                                           gridname=rg_m5m6_thick,
                                                                           netnames=['VDD', 'VSS'], direction='x',
                                                                           input_rails_rect=[rvdd_m5, rvss_m5],
                                                                           generate_pin=True,
                                                                           overwrite_start_coord=0,
                                                                           overwrite_end_coord=None,
                                                                           overwrite_num_routes=None,
                                                                           offset_start_index=0,
                                                                           offset_end_index=0)


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
    ret_libname = 'adc_retimer_ec'
    clkdist_libname = 'clk_dis_generated'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    # laygen.load_template(filename='adc_retimer.yaml', libname=ret_libname)
    #laygen.load_template(filename=ret_libname+'.yaml', libname=ret_libname)
    laygen.load_template(filename=clkdist_libname+'.yaml', libname=clkdist_libname)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)

    #library load or generation
    workinglib = 'adc_sar_generated'
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
    rg_m3m4_thick = 'route_M3_M4_thick'
    rg_m3m4_basic_thick = 'route_M3_M4_basic_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m4m5_basic_thick = 'route_M4_M5_basic_thick'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m5m6_thick_basic = 'route_M5_M6_thick_basic'
    rg_m5m6_thick2_thick = 'route_M5_M6_thick2_thick'
    rg_m6m7_thick = 'route_M6_M7_thick'
    rg_m6m7_thick2_thick = 'route_M6_M7_thick2_thick'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    mycell_list = []
    num_bits=9
    num_slices=9
    slice_order=[0,2,4,6,1,3,5,7]
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        num_bits=specdict['n_bit']
        num_slices=specdict['n_interleave']
        m_latch=sizedict['retimer']['ret_m_latch']
        m_ibuf=sizedict['retimer']['ret_m_ibuf']
        m_obuf=sizedict['retimer']['ret_m_obuf']
        slice_order=sizedict['slice_order']

    sar_name = 'sar_wsamp_bb_doubleSA_array'
    ret_name = 'adc_retimer'
    clkdist_name = 'clk_dis_viadel_htree'
    #tisar_space_name = 'tisaradc_body_space'
    space_1x_name = 'space_1x'
     
    #latch_ckb
    cellname='latch_ckb'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_latch_ckb(laygen, objectname_pfix='LATCH', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                         m=m_latch, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    # retimer_slice
    cellname = 'adc_retimer_slice'
    print(cellname + " generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_retimer_slice(laygen, objectname_pfix='LATCH', templib_logic=logictemplib, placement_grid=pg,
                       routing_grid_m3m4=rg_m3m4, rg_m3m4_basic_thick=rg_m3m4_basic_thick, rg_m4m5_thick=rg_m4m5_thick,
                       num_bits=num_bits, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    #retimer generation
    cellname = 'adc_retimer'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_adc_retimer(laygen, objectname_pfix='RET',
                 ret_libname=ret_libname, sar_libname=workinglib, clkdist_libname=clkdist_libname, templib_logic=logictemplib,
                 ret_name=ret_name, sar_name=sar_name, clkdist_name=clkdist_name, space_1x_name=space_1x_name,
                 m_ibuf=m_ibuf, m_obuf=m_obuf, slice_order=slice_order,
                 placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5, routing_grid_m4m5_basic_thick=rg_m4m5_basic_thick,
                 routing_grid_m4m5_thick=rg_m4m5_thick, routing_grid_m5m6=rg_m5m6,
                 routing_grid_m5m6_thick=rg_m5m6_thick, 
                 routing_grid_m5m6_thick_basic=rg_m5m6_thick_basic, 
                 routing_grid_m6m7_thick=rg_m6m7_thick, 
                 num_bits=num_bits, num_slices=num_slices, clkdist_offset=21.12, origin=np.array([0, 0]))
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

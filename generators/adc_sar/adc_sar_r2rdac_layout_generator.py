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
    return [dev_bottom, dev_top, dev_left, dev_right]


def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin"""
    rvdd0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VSS', gridname, sort=True)

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0], rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0], rvss1_pin_xy[1])), gridname=gridname)


def generate_r2rdac_unit(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m2m3, routing_grid_m3m4,
                         m=2, m_series=4, origin=np.array([0, 0])):
    """generate clock delay """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    tgate_name = 'tgate_'+str(m)+'x'

    # placement
    itgate = laygen.place(name="I" + objectname_pfix + 'TG0', templatename=tgate_name,
                         gridname=pg, xy=origin, template_libname=templib_logic, shape=np.array([m_series,1]))

    # reference coordinates
    x0 = laygen.get_inst_pin_xy(itgate.name, 'VDD', rg_m2m3, index=[m_series-1, 0])[1][0]
    y0 = laygen.get_inst_pin_xy(itgate.name, 'VDD', rg_m2m3, index=[m_series-1, 0])[1][1]

    # internal routes
    for i in range(m_series-1):
        laygen.route(None, laygen.layers['metal'][4],
                     xy0=laygen.get_inst_pin_xy(itgate.name, 'O', rg_m3m4, index=[i,0])[0] - [0, i%2],
                     xy1=laygen.get_inst_pin_xy(itgate.name, 'I', rg_m3m4, index=[i+1,0])[0] - [0, i%2],
                     gridname0=rg_m3m4, via0=[0,0], via1=[0,0])
    ren = laygen.route(None, laygen.layers['metal'][4],
                 xy0=laygen.get_inst_pin_xy(itgate.name, 'EN', rg_m3m4, index=[0, 0])[0] + [0, 1],
                 xy1=laygen.get_inst_pin_xy(itgate.name, 'EN', rg_m3m4, index=[m_series-1, 0])[0] + [0, 1],
                 gridname0=rg_m3m4)
    renb = laygen.route(None, laygen.layers['metal'][4],
                 xy0=laygen.get_inst_pin_xy(itgate.name, 'ENB', rg_m3m4, index=[0, 0])[0] + [0, 2],
                 xy1=laygen.get_inst_pin_xy(itgate.name, 'ENB', rg_m3m4, index=[m_series-1, 0])[0] + [0, 2],
                 gridname0=rg_m3m4)
    for i in range(m_series):
        laygen.via(None, laygen.get_inst_pin_xy(itgate.name, 'EN', rg_m3m4, index=[i, 0])[0] + [0, 1], rg_m3m4)
        laygen.via(None, laygen.get_inst_pin_xy(itgate.name, 'ENB', rg_m3m4, index=[i, 0])[0] + [0, 2], rg_m3m4)

    # VDD/VSS rails
    rvdd = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, y0]), xy1=np.array([x0, y0]), gridname0=rg_m2m3)
    rvss = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([x0, 0]), gridname0=rg_m2m3)

    # pins
    laygen.pin_from_rect('EN', laygen.layers['pin'][4], ren, rg_m3m4)
    laygen.pin_from_rect('ENB', laygen.layers['pin'][4], renb, rg_m3m4)
    laygen.pin_from_rect('VDD', laygen.layers['pin'][2], rvdd, rg_m2m3)
    laygen.pin_from_rect('VSS', laygen.layers['pin'][2], rvss, rg_m2m3)
    laygen.pin(name='I', layer=laygen.layers['pin'][3],
               xy=laygen.get_inst_pin_xy(itgate.name, 'I', rg_m3m4, index=[0, 0]), gridname=rg_m3m4)
    laygen.pin(name='O', layer=laygen.layers['pin'][3],
               xy=laygen.get_inst_pin_xy(itgate.name, 'O', rg_m3m4, index=[m_series-1, 0]), gridname=rg_m3m4)

def generate_r2r_dac(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m2m3, routing_grid_m3m4,
                           rg_m3m4_basic_thick, rg_m4m5_thick, num_bits=9, origin=np.array([0, 0])):
    """generate r2rdac """
    inv_name='inv_2x'
    tap_name='tap'
    r2r_unit_name='r2r_dac_unit'
    r2r_unit_half_name='r2r_dac_unit_half'
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4
    # rg_m4m5 = routing_grid_m4m5
    # rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    # rg_m4m5_thick = routing_grid_m4m5_thick
    # rg_m5m6 = routing_grid_m5m6
    # rg_m5m6_thick = routing_grid_m5m6_thick
    # rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic
    # rg_m6m7_thick = routing_grid_m6m7_thick

    #boundaries
    x0=laygen.templates.get_template('capdac', workinglib).xy[1][0] - \
           laygen.templates.get_template('boundary_bottomleft').xy[1][0]*2
    m_bnd_float = round(x0 / laygen.templates.get_template('boundary_bottom').xy[1][0])
    m_bnd = int(m_bnd_float)
    if not m_bnd_float == m_bnd:
        m_bnd += 1

    devname_bnd_left = []
    devname_bnd_right = []
    transform_bnd_left = []
    transform_bnd_right = []
    num_row=num_bits*4
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

    #Calculate layout size
    array_origin = origin + laygen.get_template_xy(name='boundary_bottomleft', gridname=pg, libname=utemplib)
    tapr_origin = np.array([laygen.get_template_xy(name='capdac', gridname=pg, libname=workinglib)[0], 0]) \
                  + np.array([0, laygen.get_template_xy(name='boundary_bottomleft', gridname=pg, libname=utemplib)[1]]) \
                  - np.array([laygen.get_template_xy(name='boundary_bottomleft', gridname=pg, libname=utemplib)[0], 0]) \
                  - np.array([laygen.get_template_xy(name=tap_name, gridname=pg, libname=templib_logic)[0], 0])

    # placement
    itapl = []
    for i in range(num_row):
        if i%2 == 0: tf='R0'
        else: tf='MX'
        if i == 0:
            itapl.append(laygen.relplace(name="I" + objectname_pfix + 'ITAPL'+str(i), templatename=tap_name,
                              gridname=pg, refinstname=None, xy=array_origin, template_libname=templib_logic))
        else:
            itapl.append(laygen.relplace(name="I" + objectname_pfix + 'ITAPL'+str(i), templatename=tap_name,
                              gridname=pg, refinstname=itapl[-1].name, template_libname=templib_logic, direction='top', transform=tf))
    itapr = []
    for i in range(num_row):
        if i%2 == 0: tf='R0'
        else: tf='MX'
        if i == 0:
            itapr.append(laygen.relplace(name="I" + objectname_pfix + 'ITAPR'+str(i), templatename=tap_name,
                              gridname=pg, refinstname=None, xy=tapr_origin, template_libname=templib_logic))
        else:
            itapr.append(laygen.relplace(name="I" + objectname_pfix + 'ITAPR'+str(i), templatename=tap_name,
                              gridname=pg, refinstname=itapr[-1].name, template_libname=templib_logic, direction='top', transform=tf))
    i2rvdd = []
    for i in range(num_bits):
        if i == 0:
            i2rvdd.append(laygen.relplace(name="I" + objectname_pfix + 'I2RVDD'+str(i), templatename=r2r_unit_name,
                              gridname=pg, refinstname=itapl[2].name, template_libname=workinglib))
        else:
            i2rvdd.append(laygen.relplace(name="I" + objectname_pfix + 'I2RVDD'+str(i), templatename=r2r_unit_name,
                              xy=np.array([0, 3*laygen.get_template_xy(name=r2r_unit_name, gridname=pg, libname=workinglib)[1]]),
                              gridname=pg, refinstname=i2rvdd[-1].name, template_libname=workinglib, direction='top'))
    ir = []
    for i in range(num_bits):
        if i == 0:
            ir.append(laygen.relplace(name="I" + objectname_pfix + 'IR'+str(i), templatename=r2r_unit_name,
                              gridname=pg, refinstname=itapl[1].name, template_libname=workinglib, transform='MX'))
        # elif i == 0:
        #     ir.append(laygen.relplace(name="I" + objectname_pfix + 'IR'+str(i), templatename=r2r_unit_name,
        #                       gridname=pg, refinstname=itapl[4*(num_bits-1)+1].name, template_libname=workinglib, direction='right', transform='MX'))
        else:
            ir.append(laygen.relplace(name="I" + objectname_pfix + 'IR'+str(i), templatename=r2r_unit_half_name,
                              xy=np.array([0, 0]),
                              gridname=pg, refinstname=itapl[4*i+1].name, template_libname=workinglib, direction='right', transform='MX'))
    i2rvss = []
    for i in range(num_bits):
        if i == 0:
            i2rvss.append(laygen.relplace(name="I" + objectname_pfix + 'I2RVSS'+str(i), templatename=r2r_unit_name,
                              gridname=pg, refinstname=itapl[0].name, template_libname=workinglib))
        else:
            i2rvss.append(laygen.relplace(name="I" + objectname_pfix + 'I2RVSS'+str(i), templatename=r2r_unit_name,
                              xy=np.array([0, 3*laygen.get_template_xy(name=r2r_unit_name, gridname=pg, libname=workinglib)[1]]),
                              gridname=pg, refinstname=i2rvss[-1].name, template_libname=workinglib, direction='top'))
    ibuf0 = []
    ibuf1 = []
    for i in range(num_bits):
        if i == 0:
            ibuf0.append(laygen.relplace(name="I" + objectname_pfix + 'IBUF0'+str(i), templatename=inv_name,
                              gridname=pg, refinstname=itapl[3].name, template_libname=logictemplib, transform='MX'))
        else:
            ibuf0.append(laygen.relplace(name="I" + objectname_pfix + 'IBUF0'+str(i), templatename=inv_name,
                              xy=np.array([0, 3*laygen.get_template_xy(name=inv_name, gridname=pg, libname=logictemplib)[1]]),
                              gridname=pg, refinstname=ibuf0[-1].name, template_libname=logictemplib, direction='top', transform='MX'))
        ibuf1.append(laygen.relplace(name="I" + objectname_pfix + 'IBUF1'+str(i), templatename=inv_name,
                          gridname=pg, refinstname=ibuf0[-1].name, template_libname=logictemplib, transform='MX'))

    # Space calculation
    space_name = 'space_1x'
    space4x_name = 'space_4x'
    space_width = laygen.get_template_xy(name = space_name, gridname = pg, libname = templib_logic)[0]
    space4_width = laygen.get_template_xy(name = space4x_name, gridname = pg, libname = templib_logic)[0]
    blank_2r = laygen.get_inst_xy(itapr[0].name, pg)[0] - laygen.get_inst_bbox(i2rvdd[0].name, pg)[1][0]
    blank_r = laygen.get_inst_xy(itapr[1].name, pg)[0] - laygen.get_inst_bbox(ir[1].name, pg)[1][0]
    blank_buf = laygen.get_inst_xy(itapr[0].name, pg)[0] - laygen.get_inst_bbox(ibuf1[0].name, pg)[1][0]
    m_sp4x_2r = int(blank_2r/space4_width)
    m_sp1x_2r = int(blank_2r/space_width)-4*m_sp4x_2r
    m_sp4x_r = int(blank_r/space4_width)
    m_sp1x_r = int(blank_r/space_width)-4*m_sp4x_r
    m_sp4x_buf = int(blank_buf/space4_width)
    m_sp1x_buf = int(blank_buf/space_width)-4*m_sp4x_buf

    isp_2rvdd_4x = []
    isp_2rvss_4x = []
    isp_r_4x = []
    isp_buf_4x = []
    isp_2rvdd_1x = []
    isp_2rvss_1x = []
    isp_r_1x = []
    isp_buf_1x = []
    for i in range(num_bits):
        isp_2rvdd_4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2RVDD_4x'+str(i), templatename=space4x_name,
                          gridname=pg, refinstname=i2rvdd[i].name, template_libname=logictemplib, shape=[m_sp4x_2r, 1], transform='R0'))
        isp_2rvdd_1x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2RVDD_1x'+str(i), templatename=space_name,
                          gridname=pg, refinstname=isp_2rvdd_4x[i].name, template_libname=logictemplib, shape=[m_sp1x_2r, 1], transform='R0'))
        isp_2rvss_4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2RVSS_4x'+str(i), templatename=space4x_name,
                          gridname=pg, refinstname=i2rvss[i].name, template_libname=logictemplib, shape=[m_sp4x_2r, 1], transform='R0'))
        isp_2rvss_1x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2RVSS_1x'+str(i), templatename=space_name,
                          gridname=pg, refinstname=isp_2rvss_4x[i].name, template_libname=logictemplib, shape=[m_sp1x_2r, 1], transform='R0'))
        if i==0:
            isp_r_4x.append(laygen.relplace(name="I" + objectname_pfix + 'SPR_4x' + str(i), templatename=space4x_name,
                                            gridname=pg, refinstname=ir[i].name, template_libname=logictemplib,
                                            shape=[m_sp4x_2r, 1], transform='MX'))
            isp_r_1x.append(laygen.relplace(name="I" + objectname_pfix + 'SPR_1x' + str(i), templatename=space_name,
                                            gridname=pg, refinstname=isp_r_4x[i].name, template_libname=logictemplib,
                                            shape=[m_sp1x_2r, 1], transform='MX'))
        else:
            isp_r_4x.append(laygen.relplace(name="I" + objectname_pfix + 'SPR_4x'+str(i), templatename=space4x_name,
                              gridname=pg, refinstname=ir[i].name, template_libname=logictemplib, shape=[m_sp4x_r, 1], transform='MX'))
            isp_r_1x.append(laygen.relplace(name="I" + objectname_pfix + 'SPR_1x'+str(i), templatename=space_name,
                              gridname=pg, refinstname=isp_r_4x[i].name, template_libname=logictemplib, shape=[m_sp1x_r, 1], transform='MX'))
        isp_buf_4x.append(laygen.relplace(name="I" + objectname_pfix + 'SPBUF_4x'+str(i), templatename=space4x_name,
                          gridname=pg, refinstname=ibuf1[i].name, template_libname=logictemplib, shape=[m_sp4x_buf, 1], transform='MX'))
        isp_buf_1x.append(laygen.relplace(name="I" + objectname_pfix + 'SPBUF_1x'+str(i), templatename=space_name,
                          gridname=pg, refinstname=isp_buf_4x[i].name, template_libname=logictemplib, shape=[m_sp1x_buf, 1], transform='MX'))

    # internal pins
    pdict = laygen.get_inst_pin_xy(None, None, rg_m3m4)

    # routing
    # 2RVDD to VDD & 2RVSS to VSS
    for i in range(num_bits):
        rh0, rv0 = laygen.route_hv(laygen.layers['metal'][2], laygen.layers['metal'][3],
                                   xy0=laygen.get_inst_pin_xy(i2rvdd[i].name, 'VDD', rg_m2m3)[0],
                                   xy1=laygen.get_inst_pin_xy(i2rvdd[i].name, 'I', rg_m2m3)[0], gridname0=rg_m2m3)
        rh0, rv0 = laygen.route_hv(laygen.layers['metal'][2], laygen.layers['metal'][3],
                                   xy0=laygen.get_inst_pin_xy(i2rvss[i].name, 'VSS', rg_m2m3)[0],
                                   xy1=laygen.get_inst_pin_xy(i2rvss[i].name, 'I', rg_m2m3)[0], gridname0=rg_m2m3)

    x1 = laygen.get_inst_xy(ir[i].name, rg_m3m4)[0]
    for i in range(num_bits):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                laygen.get_inst_pin_xy(i2rvdd[i].name, 'O', rg_m3m4)[0],
                                laygen.get_inst_pin_xy(ir[i].name, 'I', rg_m4m5)[0]+[2,0],
                                laygen.get_inst_pin_xy(ir[i].name, 'EN', rg_m3m4)[0][1] + 6, rg_m3m4,
                                layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
        if i == num_bits-1:
            laygen.pin_from_rect('out', laygen.layers['pin'][4], rh0, rg_m3m4)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                laygen.get_inst_pin_xy(i2rvss[i].name, 'O', rg_m3m4)[0],
                                laygen.get_inst_pin_xy(ir[i].name, 'I', rg_m4m5)[0]+[2,0],
                                laygen.get_inst_pin_xy(ir[i].name, 'EN', rg_m3m4)[0][1] - 6, rg_m3m4,
                                layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
        laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ir[i].name, 'I', rg_m3m4)[0]+[0,2],
                     xy1=laygen.get_inst_pin_xy(ir[i].name, 'I', rg_m4m5)[0]+[2,2], gridname0=rg_m3m4, gridname1=rg_m4m5,via0=[0,0], via1=[0,0])
        y1 = laygen.get_inst_pin_xy(ir[i].name, 'VDD', rg_m3m4)[0][1]+2
        # R path routing
        if not i == 0:
            rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                               laygen.get_inst_pin_xy(ir[i].name, 'O', rg_m3m4)[0],
                                               laygen.get_inst_pin_xy(ir[i-1].name, 'I', rg_m4m5)[0]-[2,-6],
                                               y1, rg_m3m4, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
        else:
            # rh0, rv0 = laygen.route_hv(laygen.layers['metal'][2], laygen.layers['metal'][3],
            #                            xy0=laygen.get_inst_pin_xy(ir[i].name, 'VSS', rg_m2m3)[0],
            #                        xy1=laygen.get_inst_pin_xy(ir[i].name, 'O', rg_m2m3)[0], gridname0=rg_m2m3)
            rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                               laygen.get_inst_pin_xy(ir[i].name, 'O', rg_m3m4)[0],
                                               laygen.get_inst_pin_xy(ir[i].name, 'VSS', rg_m3m4)[1],
                                               laygen.get_inst_pin_xy(ir[i].name, 'O', rg_m3m4)[0][1]-1, rg_m3m4)
            laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ir[i].name, 'O', rg_m3m4)[0]+np.array([0,-1]),
                         xy1=laygen.get_inst_pin_xy(ir[i].name, 'O', rg_m3m4)[0]+np.array([4,-1]), gridname0=rg_m3m4)
            laygen.via(None, xy=laygen.get_inst_pin_xy(ir[i].name, 'VSS', rg_m2m3)[1], gridname=rg_m2m3)
        rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                         laygen.get_inst_pin_xy(ir[i - 1].name, 'I', rg_m3m4)[0],
                                         laygen.get_inst_pin_xy(ir[i - 1].name, 'I', rg_m4m5)[0] - [2, -6],
                                         laygen.get_inst_pin_xy(ir[i - 1].name, 'I', rg_m3m4)[0][1] + 2, rg_m3m4,
                                         layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)

        # R EN/ENB
        rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2],
                                   xy0=laygen.get_inst_pin_xy(ir[i].name, 'EN', rg_m2m3)[1],
                               xy1=laygen.get_inst_pin_xy(ir[i].name, 'VDD', rg_m2m3)[0], gridname0=rg_m2m3)
        rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2],
                                   xy0=laygen.get_inst_pin_xy(ir[i].name, 'ENB', rg_m2m3)[1],
                               xy1=laygen.get_inst_pin_xy(ir[i].name, 'VSS', rg_m2m3)[0], gridname0=rg_m2m3)

        # 2R EN/ENB
        x_en = laygen.get_inst_pin_xy(ibuf1[i].name, 'O', rg_m3m4)[0][0]+6
        x_enb = laygen.get_inst_pin_xy(ibuf1[i].name, 'O', rg_m3m4)[0][0]+4
        rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                         laygen.get_inst_pin_xy(ibuf1[i].name, 'O', rg_m3m4)[0],
                                         np.array([x_en, laygen.get_inst_pin_xy(i2rvdd[i].name, 'EN', rg_m4m5)[0][1]]),
                                         laygen.get_inst_pin_xy(ibuf1[i].name, 'O', rg_m3m4)[1][1], rg_m3m4,
                                         layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
        laygen.via(None, xy=np.array([x_en, laygen.get_inst_pin_xy(i2rvdd[i].name, 'EN', rg_m4m5)[0][1]]), gridname=rg_m4m5)
        rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                         laygen.get_inst_pin_xy(ibuf1[i].name, 'O', rg_m3m4)[0],
                                         np.array([x_en, laygen.get_inst_pin_xy(i2rvss[i].name, 'ENB', rg_m4m5)[0][1]]),
                                         laygen.get_inst_pin_xy(ibuf1[i].name, 'O', rg_m3m4)[1][1], rg_m3m4,
                                         layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
        laygen.via(None, xy=np.array([x_en, laygen.get_inst_pin_xy(i2rvss[i].name, 'ENB', rg_m4m5)[0][1]]), gridname=rg_m4m5)
        rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                         laygen.get_inst_pin_xy(ibuf0[i].name, 'O', rg_m3m4)[0],
                                         np.array([x_enb, laygen.get_inst_pin_xy(i2rvdd[i].name, 'ENB', rg_m4m5)[0][1]]),
                                         laygen.get_inst_pin_xy(ibuf0[i].name, 'O', rg_m3m4)[0][1], rg_m3m4,
                                         layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
        laygen.via(None, xy=np.array([x_enb, laygen.get_inst_pin_xy(i2rvdd[i].name, 'ENB', rg_m4m5)[0][1]]), gridname=rg_m4m5)
        rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                         laygen.get_inst_pin_xy(ibuf0[i].name, 'O', rg_m3m4)[0],
                                         np.array([x_enb, laygen.get_inst_pin_xy(i2rvss[i].name, 'EN', rg_m4m5)[0][1]]),
                                         laygen.get_inst_pin_xy(ibuf0[i].name, 'O', rg_m3m4)[0][1], rg_m3m4,
                                         layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
        laygen.via(None, xy=np.array([x_enb, laygen.get_inst_pin_xy(i2rvss[i].name, 'EN', rg_m4m5)[0][1]]), gridname=rg_m4m5)

        # buffer routing
        laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_inst_pin_xy(ibuf0[i].name, 'O', rg_m3m4)[0],
                     xy1=laygen.get_inst_pin_xy(ibuf1[i].name, 'I', rg_m3m4)[0], gridname0=rg_m3m4, via0=[0,0], via1=[0,0])

        # Sel pins
        rv0, rsel = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                   xy0=laygen.get_inst_pin_xy(ibuf0[i].name, 'I', rg_m3m4)[0],
                               xy1=laygen.get_inst_pin_xy(ibuf0[i].name, 'I', rg_m3m4)[0]+[4,2], gridname0=rg_m3m4)
        laygen.pin_from_rect('SEL<'+str(i)+'>', laygen.layers['pin'][4], rsel, rg_m3m4)

    # # power
    # for i in range(num_row):
    #     laygen.pin(name='VSS'+str(i), layer=laygen.layers['pin'][2], xy=laygen.get_inst_pin_xy(itapl[i].name, 'VSS', rg_m2m3),
    #                gridname=rg_m2m3, netname='VSS:')
    #     laygen.pin(name='VDD'+str(i), layer=laygen.layers['pin'][2], xy=laygen.get_inst_pin_xy(itapl[i].name, 'VDD', rg_m2m3),
    #                gridname=rg_m2m3, netname='VDD:')

    # power pin
    pwr_dim=laygen.get_template_xy(name=itapl[0].cellname, gridname=rg_m2m3, libname=itapl[0].libname)
    rvddl_m3 = []
    rvssl_m3 = []
    rvddr_m3 = []
    rvssr_m3 = []
    for i in range(0, int(pwr_dim[0]/2)):
        rvddl_m3.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+0, 0]), xy1=np.array([2*i+0, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[num_row-1].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvssl_m3.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[num_row-1].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        for j in range(num_row):
            laygen.via(None, xy=np.array([2*i+0, 0]), gridname=rg_m2m3, refinstname=itapl[j].name, refpinname='VDD')
            laygen.via(None, xy=np.array([2 * i + 1, 0]), gridname=rg_m2m3, refinstname=itapl[j].name, refpinname='VSS')
        # laygen.pin(name = 'VDDL'+str(i), layer = laygen.layers['pin'][3], refobj = rvddl_m3[-1], gridname=rg_m2m3, netname='VDD')
        # laygen.pin(name = 'VSSL'+str(i), layer = laygen.layers['pin'][3], refobj = rvssl_m3[-1], gridname=rg_m2m3, netname='VSS')
        rvddr_m3.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+0, 0]), xy1=np.array([2*i+0, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[num_row-1].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvssr_m3.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[num_row-1].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        for j in range(num_row):
            laygen.via(None, xy=np.array([2*i+0, 0]), gridname=rg_m2m3, refinstname=itapr[j].name, refpinname='VDD')
            laygen.via(None, xy=np.array([2 * i + 1, 0]), gridname=rg_m2m3, refinstname=itapr[j].name, refpinname='VSS')
        # laygen.pin(name = 'VDDR'+str(i), layer = laygen.layers['pin'][3], refobj = rvddr_m3[-1], gridname=rg_m2m3, netname='VDD')
        # laygen.pin(name = 'VSSR'+str(i), layer = laygen.layers['pin'][3], refobj = rvssr_m3[-1], gridname=rg_m2m3, netname='VSS')

    #m4
    input_rails_rect = [rvddl_m3, rvssl_m3]
    rvddl_m4, rvssl_m4 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='L_M4_',
                layer=laygen.layers['metal'][4], gridname=rg_m3m4_basic_thick, netnames=['VDD', 'VSS'], direction='x',
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=2, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    x1_phy = laygen.get_xy(obj =bnd_right[0])[0]\
         +laygen.get_xy(obj =bnd_right[0].template)[0]
    x1 = laygen.grids.get_absgrid_x(rg_m3m4_basic_thick, x1_phy)
    input_rails_rect = [rvddr_m3, rvssr_m3]
    rvddr_m4, rvssr_m4 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='R_M4_',
                layer=laygen.layers['metal'][4], gridname=rg_m3m4_basic_thick, netnames=['VDD', 'VSS'], direction='x',
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=x1-2,
                offset_start_index=0, offset_end_index=0)

    #m5
    input_rails_rect = [rvddl_m4, rvssl_m4]
    rvddl_m5, rvssl_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='L_M5_',
                layer=laygen.layers['pin'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y',
                input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    y1_phy = laygen.get_xy(obj =bnd_top[0])[1]\
         +laygen.get_xy(obj =bnd_top[0].template)[1]
    y1 = laygen.grids.get_absgrid_x(rg_m4m5_thick, y1_phy)
    input_rails_rect = [rvddr_m4, rvssr_m4]
    rvddr_m5, rvssr_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='R_M5_',
                layer=laygen.layers['pin'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y',
                input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)

def generate_r2rdac_bcap_unit(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m2m3, routing_grid_m3m4_basic_thick,
                         m=2, origin=np.array([0, 0])):
    pg = placement_grid
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4_basic_thick = routing_grid_m3m4_basic_thick

    bcap_name = 'bcap2_8x'

    # placement
    ibcap = laygen.place(name="I" + objectname_pfix + 'BCAP0', templatename=bcap_name,
                         gridname=pg, xy=origin, template_libname=templib_logic, shape=np.array([m,1]))

    # reference coordinates
    x0 = laygen.get_inst_pin_xy(ibcap.name, 'VDD', rg_m2m3, index=[m-1, 0])[1][0]
    y0 = laygen.get_inst_pin_xy(ibcap.name, 'VDD', rg_m2m3, index=[m-1, 0])[1][1]

    # internal routes
    for i in range(m-1):
        laygen.route(None, laygen.layers['metal'][4],
                     xy0=laygen.get_inst_pin_xy(ibcap.name, 'I', rg_m3m4_basic_thick, index=[i,0])[0],
                     xy1=laygen.get_inst_pin_xy(ibcap.name, 'I', rg_m3m4_basic_thick, index=[i+1,0])[0],
                     gridname0=rg_m3m4_basic_thick, via0=[0,0], via1=[0,0])
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][3],
                     xy0=np.array([laygen.get_inst_pin_xy(ibcap.name, 'I', rg_m2m3, index=[i,0])[0][0], 0]),
                     xy1=np.array([laygen.get_inst_pin_xy(ibcap.name, 'I', rg_m2m3, index=[i,0])[0][0], y0]),
                     gridname0=rg_m2m3)
    rin = laygen.route(None, laygen.layers['metal'][4],
                 xy0=laygen.get_inst_pin_xy(ibcap.name, 'I', rg_m3m4_basic_thick, index=[0, 0])[0],
                 xy1=laygen.get_inst_pin_xy(ibcap.name, 'I', rg_m3m4_basic_thick, index=[m-1, 0])[0],
                 gridname0=rg_m3m4_basic_thick)

    # VDD/VSS rails
    rvdd = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, y0]), xy1=np.array([x0, y0]), gridname0=rg_m2m3)
    rvss = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([x0, 0]), gridname0=rg_m2m3)

    # pins
    laygen.pin_from_rect('I', laygen.layers['pin'][4], rin, rg_m3m4_basic_thick)
    laygen.pin_from_rect('VDD', laygen.layers['pin'][2], rvdd, rg_m2m3)
    laygen.pin_from_rect('VSS', laygen.layers['pin'][2], rvss, rg_m2m3)

def generate_r2r_dac_bcap(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m2m3, routing_grid_m3m4,
                           rg_m3m4_basic_thick, rg_m4m5_thick, num_bits=9, origin=np.array([0, 0])):
    """generate r2rdac """
    inv_name='inv_2x'
    tap_name='tap'
    bcap_unit_name='r2r_dac_bcap_unit'
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4
    # rg_m4m5 = routing_grid_m4m5
    # rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    # rg_m4m5_thick = routing_grid_m4m5_thick
    # rg_m5m6 = routing_grid_m5m6
    # rg_m5m6_thick = routing_grid_m5m6_thick
    # rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic
    # rg_m6m7_thick = routing_grid_m6m7_thick

    #boundaries
    x0=laygen.templates.get_template('r2r_dac_bcap_unit', workinglib).xy[1][0] + \
           laygen.templates.get_template('tap', templib_logic).xy[1][0]*2
    m_bnd_float = round(x0 / laygen.templates.get_template('boundary_bottom').xy[1][0])
    m_bnd = int(m_bnd_float)
    if not m_bnd_float == m_bnd:
        m_bnd += 1

    devname_bnd_left = []
    devname_bnd_right = []
    transform_bnd_left = []
    transform_bnd_right = []
    num_row=num_bits*4
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

    #Calculate layout size
    array_origin = origin + laygen.get_template_xy(name='boundary_bottomleft', gridname=pg, libname=utemplib)
    tapr_origin = np.array([laygen.get_template_xy(name='r2r_dac_bcap_unit', gridname=pg, libname=workinglib)[0], 0]) \
                  + np.array([0, laygen.get_template_xy(name='boundary_bottomleft', gridname=pg, libname=utemplib)[1]]) \
                  + np.array([laygen.get_template_xy(name='boundary_bottomleft', gridname=pg, libname=utemplib)[0], 0]) \
                  + np.array([laygen.get_template_xy(name=tap_name, gridname=pg, libname=templib_logic)[0], 0])

    # placement
    itapl = []
    ibcap = []
    for i in range(num_row):
        if i%2 == 0: tf='R0'
        else: tf='MX'
        if i == 0:
            itapl.append(laygen.relplace(name="I" + objectname_pfix + 'ITAPL'+str(i), templatename=tap_name,
                              gridname=pg, refinstname=None, xy=array_origin, template_libname=templib_logic))
        else:
            itapl.append(laygen.relplace(name="I" + objectname_pfix + 'ITAPL'+str(i), templatename=tap_name,
                              gridname=pg, refinstname=itapl[-1].name, template_libname=templib_logic, direction='top', transform=tf))
        ibcap.append(laygen.relplace(name="I" + objectname_pfix + 'IBCAP'+str(i), templatename=bcap_unit_name,
                          gridname=pg, refinstname=itapl[-1].name, template_libname=workinglib, direction='right', transform=tf))
    itapr = []
    for i in range(num_row):
        if i%2 == 0: tf='R0'
        else: tf='MX'
        if i == 0:
            itapr.append(laygen.relplace(name="I" + objectname_pfix + 'ITAPR'+str(i), templatename=tap_name,
                              gridname=pg, refinstname=None, xy=tapr_origin, template_libname=templib_logic))
        else:
            itapr.append(laygen.relplace(name="I" + objectname_pfix + 'ITAPR'+str(i), templatename=tap_name,
                              gridname=pg, refinstname=itapr[-1].name, template_libname=templib_logic, direction='top', transform=tf))

    # pins
    pdict = laygen.get_inst_pin_xy(None, None, rg_m3m4_basic_thick)
    laygen.pin(name='I', layer=laygen.layers['pin'][4], xy=laygen.get_inst_pin_xy(ibcap[-1].name, 'I', rg_m3m4_basic_thick),
                   gridname=rg_m3m4_basic_thick)

    # power pin
    pwr_dim=laygen.get_template_xy(name=itapl[0].cellname, gridname=rg_m2m3, libname=itapl[0].libname)
    rvddl_m3 = []
    rvssl_m3 = []
    rvddr_m3 = []
    rvssr_m3 = []
    for i in range(0, int(pwr_dim[0]/2)):
        rvddl_m3.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[num_row-1].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvssl_m3.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[num_row-1].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        for j in range(num_row):
            laygen.via(None, xy=np.array([2*i+1, 0]), gridname=rg_m2m3, refinstname=itapl[j].name, refpinname='VDD')
            laygen.via(None, xy=np.array([2 * i + 2, 0]), gridname=rg_m2m3, refinstname=itapl[j].name, refpinname='VSS')
        # laygen.pin(name = 'VDDL'+str(i), layer = laygen.layers['pin'][3], refobj = rvddl_m3[-1], gridname=rg_m2m3, netname='VDD')
        # laygen.pin(name = 'VSSL'+str(i), layer = laygen.layers['pin'][3], refobj = rvssl_m3[-1], gridname=rg_m2m3, netname='VSS')
        rvddr_m3.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[num_row-1].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvssr_m3.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[num_row-1].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        for j in range(num_row):
            laygen.via(None, xy=np.array([2*i+1, 0]), gridname=rg_m2m3, refinstname=itapr[j].name, refpinname='VDD')
            laygen.via(None, xy=np.array([2 * i + 2, 0]), gridname=rg_m2m3, refinstname=itapr[j].name, refpinname='VSS')
        # laygen.pin(name = 'VDDR'+str(i), layer = laygen.layers['pin'][3], refobj = rvddr_m3[-1], gridname=rg_m2m3, netname='VDD')
        # laygen.pin(name = 'VSSR'+str(i), layer = laygen.layers['pin'][3], refobj = rvssr_m3[-1], gridname=rg_m2m3, netname='VSS')

    #m4
    input_rails_rect = [rvddl_m3, rvssl_m3]
    rvddl_m4, rvssl_m4 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='L_M4_',
                layer=laygen.layers['metal'][4], gridname=rg_m3m4_basic_thick, netnames=['VDD', 'VSS'], direction='x',
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=2, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    x1_phy = laygen.get_xy(obj =bnd_right[0])[0]\
         +laygen.get_xy(obj =bnd_right[0].template)[0]
    x1 = laygen.grids.get_absgrid_x(rg_m3m4_basic_thick, x1_phy)
    input_rails_rect = [rvddr_m3, rvssr_m3]
    rvddr_m4, rvssr_m4 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='R_M4_',
                layer=laygen.layers['metal'][4], gridname=rg_m3m4_basic_thick, netnames=['VDD', 'VSS'], direction='x',
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=x1-2,
                offset_start_index=0, offset_end_index=0)

    #m5
    input_rails_rect = [rvddl_m4, rvssl_m4]
    rvddl_m5, rvssl_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='L_M5_',
                layer=laygen.layers['pin'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y',
                input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    y1_phy = laygen.get_xy(obj =bnd_top[0])[1]\
         +laygen.get_xy(obj =bnd_top[0].template)[1]
    y1 = laygen.grids.get_absgrid_x(rg_m4m5_thick, y1_phy)
    input_rails_rect = [rvddr_m4, rvssr_m4]
    rvddr_m5, rvssr_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='R_M5_',
                layer=laygen.layers['pin'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y',
                input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)

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
    rg_m5m6_basic_thick = 'route_M5_M6_basic_thick'
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
        num_bits=sizedict['r2rdac']['num_bits']
        num_slices=specdict['n_interleave']
        m_latch=sizedict['retimer']['ret_m_latch']
        m_ibuf=sizedict['retimer']['ret_m_ibuf']
        m_obuf=sizedict['retimer']['ret_m_obuf']
        m_srbuf=sizedict['retimer']['ret_m_srbuf']
        m_sr=sizedict['retimer']['ret_m_sr']
        slice_order=sizedict['slice_order']
        m=sizedict['r2rdac']['m']
        m_bcap=sizedict['r2rdac']['m_bcap']
        num_series=sizedict['r2rdac']['num_series']

    sar_name = 'sar_wsamp_bb_doubleSA_array'
    ret_name = 'adc_retimer'
    clkdist_name = 'clk_dis_viadel_htree'
    #tisar_space_name = 'tisaradc_body_space'
    space_1x_name = 'space_1x'
     
    #r2r unit
    cellname='r2r_dac_unit'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_r2rdac_unit(laygen, objectname_pfix='R2RUNIT', templib_logic=logictemplib, placement_grid=pg, routing_grid_m2m3=rg_m2m3,
                         routing_grid_m3m4=rg_m3m4, m=m, m_series=num_series, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    #r2r half unit
    cellname='r2r_dac_unit_half'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_r2rdac_unit(laygen, objectname_pfix='R2RUNIT_half', templib_logic=logictemplib, placement_grid=pg, routing_grid_m2m3=rg_m2m3,
                         routing_grid_m3m4=rg_m3m4, m=m, m_series=int(num_series/2), origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    # r2r dac
    cellname = 'r2r_dac'
    print(cellname + " generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_r2r_dac(laygen, objectname_pfix='R2R', templib_logic=logictemplib, placement_grid=pg, routing_grid_m2m3=rg_m2m3,
                       routing_grid_m3m4=rg_m3m4, rg_m3m4_basic_thick=rg_m3m4_basic_thick, rg_m4m5_thick=rg_m4m5_thick,
                       num_bits=num_bits, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    # r2r dac bcap unit
    cellname = 'r2r_dac_bcap_unit'
    print(cellname + " generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_r2rdac_bcap_unit(laygen, objectname_pfix='BCAPUNIT', templib_logic=logictemplib, placement_grid=pg, routing_grid_m2m3=rg_m2m3,
                         routing_grid_m3m4_basic_thick=rg_m3m4_basic_thick, m=m_bcap, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    # r2r dac
    cellname = 'r2r_dac_bcap'
    print(cellname + " generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_r2r_dac_bcap(laygen, objectname_pfix='R2R_bcap', templib_logic=logictemplib, placement_grid=pg, routing_grid_m2m3=rg_m2m3,
                       routing_grid_m3m4=rg_m3m4, rg_m3m4_basic_thick=rg_m3m4_basic_thick, rg_m4m5_thick=rg_m4m5_thick,
                       num_bits=num_bits, origin=np.array([0, 0]))
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

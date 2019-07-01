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
#from logic_layout_generator import *
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
    return [dev_bottom, dev_top, dev_left, dev_right]

def generate_sarabe_dualdelay(laygen, objectname_pfix, workinglib, placement_grid, routing_grid_m2m3, 
                              routing_grid_m3m4_thick, routing_grid_m4m5_thick, routing_grid_m5m6_thick,
                              routing_grid_m4m5, num_bits=9, sarabe_supply_rail_mode=0, clkgen_mode=False,
                              origin=np.array([0, 0])):
    """generate sar backend """
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m3m4_thick = routing_grid_m3m4_thick
    rg_m4m5_thick = routing_grid_m4m5_thick
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m4m5 = routing_grid_m4m5

    #sarfsm_name = 'sarfsm_'+str(num_bits)+'b'
    sarfsm_name = 'sarfsm'#_'+str(num_bits)+'b'
    #sarlogic_name = 'sarlogic_wret_v2_array_'+str(num_bits)+'b'
    sarlogic_name = 'sarlogic_wret_v2_array'#_'+str(num_bits)+'b'
    sarclkgen_name = 'sarclkgen_static'
    #sarret_name = 'sarret_wckbuf_'+str(num_bits)+'b'
    sarret_name = 'sarret_wckbuf'#_'+str(num_bits)+'b'
    #space_name = 'space_dcap_nmos'
    space_name = 'space'

    pin_bot_locx = []

    xy0=laygen.get_xy(obj=laygen.get_template(name=space_name, libname=workinglib), gridname=pg)
    xsp=xy0[0]
    ysp=xy0[1]

    # placement
    core_origin = origin + laygen.get_xy(obj=laygen.get_template(name = 'boundary_bottomleft'), gridname = pg)
    isp=[]
    devname_bnd_left = []
    devname_bnd_right = []
    transform_bnd_left = []
    transform_bnd_right = []
    #additional space for routing area
    isp.append(laygen.place(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                               gridname=pg, xy=core_origin, transform='R0',
                               template_libname=workinglib))
    refi = isp[-1].name
    isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                               gridname=pg, refinstname=refi, direction='top', transform='MX',
                               template_libname=workinglib))
    refi = isp[-1].name
    devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left', 'pmos4_fast_left', 'nmos4_fast_left']
    devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right', 'pmos4_fast_right', 'nmos4_fast_right']
    transform_bnd_left += ['R0', 'MX', 'R0', 'MX']
    transform_bnd_right += ['R0', 'MX', 'R0', 'MX']
    #ret
    iret=laygen.relplace(name="I" + objectname_pfix + 'RET0', templatename=sarret_name,
                         gridname=pg, refinstname=refi, direction='top', template_libname=workinglib)
    refi = iret.name
    yret = int(laygen.get_xy(obj=laygen.get_template(name=sarret_name, libname=workinglib), gridname=pg)[1] / ysp)
    for i in range(yret): #boundary cells
        if i % 2 == 0:
            devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
    # space insertion if number of rows is odd
    if not yret % 2 == 0:
        isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                                   gridname=pg, refinstname=refi, direction='top', transform='MX',
                                   template_libname=workinglib))
        refi = isp[-1].name
        devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
        devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
        transform_bnd_left += ['R0', 'MX']
        transform_bnd_right += ['R0', 'MX']
    #fsm
    ifsm=laygen.relplace(name="I" + objectname_pfix + 'FSM0', templatename=sarfsm_name,
                         gridname=pg, refinstname=refi, direction='top', template_libname=workinglib)
    refi = ifsm.name
    yfsm = int(laygen.get_xy(obj=laygen.get_template(name=sarfsm_name, libname=workinglib), gridname=pg)[1] / ysp)
    for i in range(yfsm): #boundary cells
        if i % 2 == 0:
            devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
    # space insertion if number of rows is odd
    if not yfsm % 2 == 0:
        isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                                   gridname=pg, refinstname=refi, direction='top', transform='MX',
                                   template_libname=workinglib))
        refi = isp[-1].name
        devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
        devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
        transform_bnd_left += ['R0', 'MX']
        transform_bnd_right += ['R0', 'MX']
    # sarlogic
    isl = laygen.relplace(name="I" + objectname_pfix + 'SL0', templatename=sarlogic_name,
                          gridname=pg, refinstname=refi, direction='top', template_libname=workinglib)
    refi = isl.name
    ysl = int(laygen.get_xy(obj=laygen.get_template(name=sarlogic_name, libname=workinglib), gridname=pg)[1] / ysp)
    for i in range(ysl): #boundary cells
        if i % 2 == 0:
            devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
    # space insertion 2 if number of rows is even, 1 if odd
    if ysl % 2 == 0:
        isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                                   gridname=pg, refinstname=refi, direction='top', transform='R0',
                                   template_libname=workinglib))
        refi = isp[-1].name
        devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
        devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
        transform_bnd_left += ['R0', 'MX']
        transform_bnd_right += ['R0', 'MX']
        isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                                   gridname=pg, refinstname=refi, direction='top', transform='MX',
                                   template_libname=workinglib))
        refi = isp[-1].name
        devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
        devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
        transform_bnd_left += ['R0', 'MX']
        transform_bnd_right += ['R0', 'MX']
    else:
        isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                                   gridname=pg, refinstname=refi, direction='top', transform='MX',
                                   template_libname=workinglib))
        refi = isp[-1].name
        devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
        devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
        transform_bnd_left += ['R0', 'MX']
        transform_bnd_right += ['R0', 'MX']
    #clkdelay & clkgen
    ickg = laygen.relplace(name="I" + objectname_pfix + 'CKG0', templatename=sarclkgen_name,
                           gridname=pg, refinstname=refi, direction='top', transform='R0', template_libname=workinglib)
    refi = ickg.name
    yck= laygen.get_xy(obj=laygen.get_template(name=sarclkgen_name, libname=workinglib), gridname=pg)[1] / ysp
    for i in range(int(yck)): #boundary cells
        if i % 2 == 0:
            devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
    # space insertion if number of rows is odd
    if not yck % 2 == 0:
        isp.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(len(isp)), templatename=space_name,
                                   gridname=pg, refinstname=refi, direction='top', transform='MX',
                                   template_libname=workinglib))
        refi = isp[-1].name
        devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
        devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
        transform_bnd_left += ['R0', 'MX']
        transform_bnd_right += ['R0', 'MX']

    #space insertion for routing area, if number of bits exceeds 8
    isp_r=[]
    m4_end_idx = -8
    if num_bits > 6:
        for i in range(int((num_bits-5)/2)):
            isp_r.append(laygen.relplace(name="I" + objectname_pfix + 'SP_route'+str(2*i), templatename=space_name,
                                       gridname=pg, refinstname=refi, direction='top', transform='R0',
                                       template_libname=workinglib))
            refi = isp_r[-1].name
            devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
            isp_r.append(laygen.relplace(name="I" + objectname_pfix + 'SP_route'+str(2*i+1), templatename=space_name,
                                       gridname=pg, refinstname=refi, direction='top', transform='MX',
                                       template_libname=workinglib))
            refi = isp_r[-1].name
            devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
            m4_end_idx += -8
    # if num_bits > 6:
    #     isp_r.append(laygen.relplace(name="I" + objectname_pfix + 'SP_route0', templatename=space_name,
    #                                gridname=pg, refinstname=refi, direction='top', transform='R0',
    #                                template_libname=workinglib))
    #     refi = isp_r[-1].name
    #     devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
    #     devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
    #     transform_bnd_left += ['R0', 'MX']
    #     transform_bnd_right += ['R0', 'MX']
    #     isp_r.append(laygen.relplace(name="I" + objectname_pfix + 'SP_route1', templatename=space_name,
    #                                gridname=pg, refinstname=refi, direction='top', transform='MX',
    #                                template_libname=workinglib))
    #     refi = isp_r[-1].name
    #     devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
    #     devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
    #     transform_bnd_left += ['R0', 'MX']
    #     transform_bnd_right += ['R0', 'MX']
    #     m4_end_idx += -8
    # if num_bits > 8:
    #     isp_r.append(laygen.relplace(name="I" + objectname_pfix + 'SP_route2', templatename=space_name,
    #                                gridname=pg, refinstname=refi, direction='top', transform='R0',
    #                                template_libname=workinglib))
    #     refi = isp_r[-1].name
    #     devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
    #     devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
    #     transform_bnd_left += ['R0', 'MX']
    #     transform_bnd_right += ['R0', 'MX']
    #     isp_r.append(laygen.relplace(name="I" + objectname_pfix + 'SP_route3', templatename=space_name,
    #                                gridname=pg, refinstname=refi, direction='top', transform='MX',
    #                                template_libname=workinglib))
    #     refi = isp_r[-1].name
    #     devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
    #     devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
    #     transform_bnd_left += ['R0', 'MX']
    #     transform_bnd_right += ['R0', 'MX']
    #     m4_end_idx += -8

    # boundaries
    m_bnd = int(xsp / laygen.get_xy(obj=laygen.get_template(name = 'boundary_bottom'), gridname=pg)[0])
    [bnd_bottom, bnd_top, bnd_left, bnd_right] \
        = generate_boundary(laygen, objectname_pfix='BND0', placement_grid=pg,
                            devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
                            shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
                            shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_left=devname_bnd_left,
                            transform_left=transform_bnd_left,
                            devname_right=devname_bnd_right,
                            transform_right=transform_bnd_right,
                            origin=origin)
    #route
    #reference coordinates
    pdict_m3m4 = laygen.get_inst_pin_xy(None, None, rg_m3m4)
    pdict_m4m5 = laygen.get_inst_pin_xy(None, None, rg_m4m5)
    pdict_m5m6 = laygen.get_inst_pin_xy(None, None, rg_m5m6)
    x_right = laygen.get_xy(obj =ifsm, gridname=rg_m5m6)[0]\
             +laygen.get_xy(obj =ifsm.template, gridname=rg_m5m6)[0] - 1
    y_top = laygen.get_xy(obj =ickg, gridname=rg_m5m6)[1]-1
    xysl = laygen.get_xy(obj =isl, gridname=rg_m5m6)
    xyfsm = laygen.get_xy(obj =ifsm, gridname=rg_m5m6)
    xyret = laygen.get_xy(obj =iret, gridname=rg_m5m6)

    # rst signal route
    x0=pdict_m4m5[ickg.name]['EXTSEL_CLK'][0][0]
    # very important because it sets the timing margin
    # ckg to sl
    [rh0, rrst0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m4m5[ickg.name]['RST'][0],
                                           pdict_m4m5[isl.name]['RST'][0],
                                           pdict_m4m5[ickg.name]['RST'][0][0]+2, rg_m4m5)
    [rh0, rrst1, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m4m5[ickg.name]['RST'][0],
                                           pdict_m4m5[isl.name]['RST'][0],
                                           pdict_m4m5[ickg.name]['RST'][0][0]+4, rg_m4m5)
    #[rh0, rrst2, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
    #                                       pdict_m4m5[ickg.name]['RST'][0],
    #                                       pdict_m4m5[isl.name]['RST'][0],
    #                                       pdict_m4m5[ickg.name]['RST'][0][0]+6, rg_m4m5)
    # ckg to fsm
    [rh0, rrst0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m4m5[ickg.name]['RST'][0],
                                           pdict_m4m5[ifsm.name]['RST'][0],
                                           pdict_m4m5[ickg.name]['RST'][0][0]+2, rg_m4m5)
    [rh0, rrst1, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m4m5[ickg.name]['RST'][0],
                                           pdict_m4m5[ifsm.name]['RST'][0],
                                           pdict_m4m5[ickg.name]['RST'][0][0]+4, rg_m4m5)
    #[rh0, rrst2, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
    #                                       pdict_m4m5[ickg.name]['RST'][0],
    #                                       pdict_m4m5[ifsm.name]['RST'][0],
    #                                       pdict_m4m5[ickg.name]['RST'][0][0]+6, rg_m4m5)
    # ckg to ret
    [rh0, rrst0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m4m5[ickg.name]['RST'][0],
                                           pdict_m4m5[iret.name]['CLK'][0],
                                           pdict_m4m5[ickg.name]['RST'][0][0]+2, rg_m4m5)
    [rh0, rrst1, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m4m5[ickg.name]['RST'][0],
                                           pdict_m4m5[iret.name]['CLK'][0],
                                           pdict_m4m5[ickg.name]['RST'][0][0]+4, rg_m4m5)
    #[rh0, rrst2, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
    #                                       pdict_m4m5[ickg.name]['RST'][0],
    #                                       pdict_m4m5[iret.name]['CLK'][0],
    #                                       pdict_m4m5[ickg.name]['RST'][0][0]+6, rg_m4m5)
    # rst output to final retimer
    rrstout0 = laygen.route(None, laygen.layers['metal'][5],
                            xy0=pdict_m5m6[iret.name]['CLKO0'][0],
                            xy1=np.array([pdict_m5m6[iret.name]['CLKO0'][0][0], 0]), gridname0=rg_m5m6)
    laygen.boundary_pin_from_rect(rrstout0, rg_m4m5, 'RSTOUT0', laygen.layers['pin'][5], size=6,
                                  direction='bottom', netname='RSTOUT')
    xy = laygen.get_rect_xy(rrstout0.name, rg_m4m5)
    pin_bot_locx.append(float(laygen._route_generate_box_from_abscoord(xy0=xy[0, :], xy1=xy[1, :], gridname0=rg_m4m5)[1][0][0]))
    rrstout1 = laygen.route(None, laygen.layers['metal'][5],
                            xy0=pdict_m5m6[iret.name]['CLKO1'][0],
                            xy1=np.array([pdict_m5m6[iret.name]['CLKO1'][0][0], 0]), gridname0=rg_m5m6)
    laygen.boundary_pin_from_rect(rrstout1, rg_m4m5, 'RSTOUT1', laygen.layers['pin'][5], size=6,
                                  direction='bottom', netname='RSTOUT')
    xy = laygen.get_rect_xy(rrstout1.name, rg_m4m5)
    pin_bot_locx.append(float(laygen._route_generate_box_from_abscoord(xy0=xy[0, :], xy1=xy[1, :], gridname0=rg_m4m5)[1][0][0]))

    # clk input 
    laygen.boundary_pin_from_rect(rrst0, rg_m5m6, 'RST0', laygen.layers['pin'][5], size=6, direction='top',
                                  netname='RST')
    laygen.boundary_pin_from_rect(rrst1, rg_m5m6, 'RST1', laygen.layers['pin'][5], size=6, direction='top',
                                  netname='RST')
    #laygen.boundary_pin_from_rect(rrst2, rg_m5m6, 'RST2' , laygen.layers['pin'][5], size=6, direction='top', netname='RST')

    # sarclk signal route
    # ckgen to fsm
    ref_x_sarclk = laygen.get_inst_pin_xy(isl.name, 'ZP<'+str(int(num_bits/2)*2-1)+'>', rg_m4m5)[0][0]-5
    rh0, rv0, rh1 = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                     pdict_m4m5[ickg.name]['CLKO'][0], pdict_m4m5[ifsm.name]['CLK'][0], 
                                     ref_x_sarclk, rg_m4m5)
    # ckgen to fsm #2 (to reduce route resistance)
    rh0, rv0, rh1 = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                     pdict_m4m5[ickg.name]['CLKO'][0], pdict_m4m5[ifsm.name]['CLK'][0], 
                                     ref_x_sarclk+2, rg_m4m5)
    ## ckgen to fsm
    #rh0, rv0, rh1 = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
    #                                 pdict_m4m5[ickg.name]['CLKO'][0], pdict_m4m5[ifsm.name]['CLK'][0], 
    #                                 pdict_m4m5[isl.name]['RETO<'+str(num_bits-2)+'>'][1][0]+9-4-1-3, rg_m4m5)
    ## ckgen to fsm #2 (to reduce route resistance)
    #rh0, rv0, rh1 = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
    #                                 pdict_m4m5[ickg.name]['CLKO'][0], pdict_m4m5[ifsm.name]['CLK'][0], 
    #                                 pdict_m4m5[isl.name]['RETO<'+str(num_bits-2)+'>'][1][0]+11-4-1-3, rg_m4m5)

    # ckgen to sl route
    # saopb/saomb
    [rh0, rsaop0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m4m5[ickg.name]['SAOP'][0],
                                           pdict_m4m5[isl.name]['SAOP'][0],
                                           pdict_m4m5[ickg.name]['SAOP'][0][0]+0, rg_m4m5)
    [rh0, rsaom0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                           pdict_m4m5[ickg.name]['SAOM'][0],
                                           pdict_m4m5[isl.name]['SAOM'][0],
                                           pdict_m4m5[ickg.name]['SAOM'][0][0]+1, rg_m4m5)
    #equalize vertical route for pin generation
    rsaop0_xy=laygen.get_xy(obj = rsaop0, gridname = rg_m4m5, sort=True)
    rsaom0_xy=laygen.get_xy(obj = rsaom0, gridname = rg_m4m5, sort=True)
    rsao_y0=min((rsaop0_xy[0][1], rsaom0_xy[0][1]))
    rsao_y1=max((rsaop0_xy[1][1], rsaom0_xy[1][1]))
    rsaop0=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([rsaop0_xy[0][0], rsao_y0]), xy1=np.array([rsaop0_xy[1][0], rsao_y1]), gridname0=rg_m4m5)
    rsaom0=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([rsaom0_xy[0][0], rsao_y0]), xy1=np.array([rsaom0_xy[1][0], rsao_y1]), gridname0=rg_m4m5)
    # fsm to sl route
    # sb
    for i in range(num_bits):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                           pdict_m5m6[ifsm.name]['SB<'+str(i)+'>'][0],
                                           pdict_m5m6[isl.name]['SB<'+str(i)+'>'][0], xysl[1]-i-1, rg_m5m6)
    # zp/zm/zmid
    for i in range(num_bits):
        rzp0 = laygen.route(None, laygen.layers['metal'][5],
                            xy0=pdict_m4m5[isl.name]['ZP<'+str(i)+'>'][0],
                            xy1=pdict_m4m5[isl.name]['ZP<'+str(i)+'>'][0]+np.array([0, 4]), gridname0=rg_m4m5)
        laygen.boundary_pin_from_rect(rzp0, rg_m4m5, 'ZP<' + str(i) + '>', laygen.layers['pin'][5], size=6,
                                      direction='top')
        rzm0 = laygen.route(None, laygen.layers['metal'][5],
                            xy0=pdict_m4m5[isl.name]['ZM<'+str(i)+'>'][0],
                            xy1=pdict_m4m5[isl.name]['ZM<'+str(i)+'>'][0]+np.array([0, 4]), gridname0=rg_m4m5)
        laygen.boundary_pin_from_rect(rzm0, rg_m4m5, 'ZM<' + str(i) + '>', laygen.layers['pin'][5], size=6,
                                      direction='top')
        rzmid0 = laygen.route(None, laygen.layers['metal'][5],
                            xy0=pdict_m4m5[isl.name]['ZMID<'+str(i)+'>'][0],
                            xy1=pdict_m4m5[isl.name]['ZMID<'+str(i)+'>'][0]+np.array([0, 4]), gridname0=rg_m4m5)
        laygen.boundary_pin_from_rect(rzmid0, rg_m4m5, 'ZMID<' + str(i) + '>', laygen.layers['pin'][5], size=6,
                                      direction='top')
    # zmid to short
    #rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
    #                                 pdict_m4m5[ickg.name]['SHORTB'][0],
    #                                 pdict_m4m5[isl.name]['ZMID<5>'][0], rg_m4m5)
    rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                     pdict_m4m5[ickg.name]['SHORTB'][0],
                                     pdict_m4m5[isl.name]['ZMID<'+str(max(0, num_bits-3))+'>'][0], rg_m4m5)
    # ckdsel
    x_ref_ckdsel = laygen.get_inst_bbox(ickg.name, rg_m4m5)[1][0]
    for i in range(2):
        rh0, rclkdsel0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                         pdict_m4m5[ickg.name]['SEL<' + str(i) + '>'][0],
                                         np.array([x_ref_ckdsel-11+i, 0]), rg_m4m5)
        laygen.boundary_pin_from_rect(rclkdsel0, rg_m4m5, 'CKDSEL0<' + str(i) + '>', laygen.layers['pin'][5],
                                      size=6, direction='bottom')
        xy = laygen.get_rect_xy(rclkdsel0.name, rg_m4m5)
        pin_bot_locx.append(float(laygen._route_generate_box_from_abscoord(xy0=xy[0, :], xy1=xy[1, :], gridname0=rg_m4m5)[1][0][0]))
    rh0, rclkdsel1 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                     pdict_m4m5[ickg.name]['SEL<2>'][0],
                                     np.array([x_ref_ckdsel-8, 0]), rg_m4m5)
    laygen.boundary_pin_from_rect(rclkdsel1, rg_m4m5, 'CKDSEL1<0>', laygen.layers['pin'][5], size=6,
                                  direction='bottom')
    xy = laygen.get_rect_xy(rclkdsel1.name, rg_m4m5)
    pin_bot_locx.append(float(laygen._route_generate_box_from_abscoord(xy0=xy[0, :], xy1=xy[1, :], gridname0=rg_m4m5)[1][0][0]))
    #ckdsel dummy
    xy0 = laygen.get_xy(obj =rclkdsel0, gridname=rg_m4m5, sort=True)
    rclkdsel1 = laygen.route(None, laygen.layers['metal'][5], xy0=xy0[0]+np.array([3,0]), xy1=xy0[0]+np.array([3,4]), gridname0=rg_m4m5)
    laygen.boundary_pin_from_rect(rclkdsel1, rg_m4m5, 'CKDSEL1<1>', laygen.layers['pin'][5], size=6,
                                  direction='bottom')
    xy = laygen.get_rect_xy(rclkdsel1.name, rg_m4m5)
    pin_bot_locx.append(float(laygen._route_generate_box_from_abscoord(xy0=xy[0, :], xy1=xy[1, :], gridname0=rg_m4m5)[1][0][0]))

    # SAOP/SAOM
    laygen.boundary_pin_from_rect(rsaop0, rg_m4m5, 'SAOP', laygen.layers['pin'][5], size=6, direction='top')
    laygen.boundary_pin_from_rect(rsaom0, rg_m4m5, 'SAOM', laygen.layers['pin'][5], size=6, direction='top')
    # extclk, extsel_clk
    rh0, rextsel_clk0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                    pdict_m4m5[ickg.name]['EXTSEL_CLK'][0],
                                    np.array([x0-2, 0]), rg_m4m5)
                                    #np.array([x0+13+3, 0]), rg_m4m5)
    laygen.boundary_pin_from_rect(rextsel_clk0, rg_m4m5, 'EXTSEL_CLK', laygen.layers['pin'][5], size=6,
                                  direction='bottom')
    if clkgen_mode:
        rh0, rextsel_clk0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                            pdict_m4m5[ickg.name]['MODESEL'][0],
                                            np.array([x0 - 1, 0]), rg_m4m5)
        laygen.boundary_pin_from_rect(rextsel_clk0, rg_m4m5, 'MODESEL', laygen.layers['pin'][5], size=6,
                                      direction='bottom')

    xy = laygen.get_rect_xy(rextsel_clk0.name, rg_m4m5)
    pin_bot_locx.append(float(laygen._route_generate_box_from_abscoord(xy0=xy[0,:], xy1=xy[1,:], gridname0=rg_m4m5)[1][0][0]))
    # fsm to ret (data)
    for i in range(num_bits):
        if i%2==0: #even channel
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                               pdict_m5m6[isl.name]['RETO<'+str(i)+'>'][0],
                                               pdict_m5m6[iret.name]['IN<'+str(i)+'>'][0], xyfsm[1]-int(i/2)*2+4, rg_m5m6)
        else:
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                               pdict_m5m6[isl.name]['RETO<'+str(i)+'>'][0],
                                               pdict_m5m6[iret.name]['IN<'+str(i)+'>'][0], xyfsm[1]-int(i/2)*2-int(num_bits/2)*2-2, rg_m5m6)
    # adcout
    for i in range(num_bits):
        radco0 = laygen.route(None, laygen.layers['metal'][5],
                             xy0=pdict_m4m5[iret.name]['OUT<'+str(i)+'>'][0],
                             xy1=np.array([pdict_m4m5[iret.name]['OUT<'+str(i)+'>'][0][0], 0]), gridname0=rg_m5m6)
        laygen.boundary_pin_from_rect(radco0, rg_m4m5, 'ADCOUT<' + str(i) + '>', laygen.layers['pin'][5], size=6,
                                      direction='bottom')
        xy = laygen.get_rect_xy(radco0.name, rg_m4m5)
        pin_bot_locx.append(float(laygen._route_generate_box_from_abscoord(xy0=xy[0, :], xy1=xy[1, :], gridname0=rg_m4m5)[1][0][0]))
    # probe outputs
    laygen.pin(name='PHI0', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['PHI0'], gridname=rg_m4m5)
    laygen.pin(name='UP', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['UP'], gridname=rg_m4m5)
    laygen.pin(name='DONE', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['DONE'], gridname=rg_m4m5)
    laygen.pin(name='SARCLK', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['CLKO'], gridname=rg_m4m5)
    laygen.pin(name='SARCLKB', layer=laygen.layers['pin'][4], xy=pdict_m4m5[ickg.name]['CLKOB'], gridname=rg_m4m5)
    for i in range(num_bits):
        laygen.pin(name='SB<' + str(i) + '>', layer=laygen.layers['pin'][5],
                   xy=pdict_m5m6[isl.name]['SB<' + str(i) + '>'], gridname=rg_m5m6)
    # vdd/vss
    # m3
    rvddl_m3=[]
    rvssl_m3=[]
    rvddr_m3=[]
    rvssr_m3=[]
    xret_center = int(laygen.get_xy(obj=laygen.get_template(name=sarret_name, libname=workinglib), gridname=rg_m3m4_thick)[0] / 2)
    for p in pdict_m3m4[iret.name]:
        if p.startswith('VDD'):
            r0=laygen.route(None, laygen.layers['metal'][3], xy0=pdict_m3m4[iret.name][p][0], xy1=pdict_m3m4[isp[-1].name][p][0],
                            gridname0=rg_m3m4)
            if pdict_m3m4[iret.name][p][0][0] < xret_center:
                rvddl_m3.append(r0)
            else:
                rvddr_m3.append(r0)
    for p in pdict_m3m4[iret.name]:
        if p.startswith('VSS'):
            r0=laygen.route(None, laygen.layers['metal'][3], xy0=pdict_m3m4[iret.name][p][0], xy1=pdict_m3m4[isp[-1].name][p][0],
                            gridname0=rg_m3m4)
            if pdict_m3m4[iret.name][p][0][0] < xret_center:
                rvssl_m3.append(r0)
            else:
                rvssr_m3.append(r0)
    #m4
    input_rails_rect = [rvddl_m3, rvssl_m3]
    rvddl_m4, rvssl_m4 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='L_M4_', 
                layer=laygen.layers['metal'][4], gridname=rg_m3m4_thick, netnames=['VDD', 'VSS'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=None,
                offset_start_index=2, offset_end_index=m4_end_idx)
    x1 = laygen.get_xy(obj =bnd_right[0], gridname=rg_m3m4_thick)[0]\
         +laygen.get_xy(obj =bnd_right[0].template, gridname=rg_m3m4_thick)[0]
    input_rails_rect = [rvddr_m3, rvssr_m3]
    rvddr_m4, rvssr_m4 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='R_M4_', 
                layer=laygen.layers['metal'][4], gridname=rg_m3m4_thick, netnames=['VDD', 'VSS'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=x1,
                offset_start_index=2, offset_end_index=m4_end_idx)
    #additional m4 routes
    inst_exclude=[isp[0], isp[1], iret,ifsm,isl,ickg,isp[-1],isp[-2], isp_r[-1], isp_r[-2]]
    # if not len(isp_r)==0:
    #     for i in range (len(isp_r)):
    #         inst_exclude.append(isp_r[i])
    x0 = laygen.get_xy(obj =bnd_left[0], gridname=rg_m3m4_thick)[0]
    y0 = laygen.get_xy(obj =bnd_left[0], gridname=rg_m3m4_thick)[1]
    x1 = laygen.get_xy(obj =bnd_right[0], gridname=rg_m3m4_thick)[0]\
         +laygen.get_xy(obj =bnd_right[0].template, gridname=rg_m3m4_thick)[0]
    y1 = laygen.get_xy(obj =bnd_left[-1], gridname=rg_m3m4_thick)[1]
    for i in range(y1-y0):
        #check if y is not in the exclude area
        trig=0
        for iex in inst_exclude:
            if iex.transform=='MX':
                yex0 = laygen.get_xy(obj =iex, gridname=rg_m3m4_thick)[1]-1\
                       -laygen.get_xy(obj =iex.template, gridname=rg_m3m4_thick)[1]
                yex1 = laygen.get_xy(obj =iex, gridname=rg_m3m4_thick)[1]+1
            else:
                yex0 = laygen.get_xy(obj =iex, gridname=rg_m3m4_thick)[1]-1
                yex1 = laygen.get_xy(obj =iex, gridname=rg_m3m4_thick)[1]+1\
                       +laygen.get_xy(obj =iex.template, gridname=rg_m3m4_thick)[1]
            if y0+i > yex0 and y0+i < yex1: #exclude
                trig=0 
        if trig==1:
            r0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x0, y0+i]), xy1=np.array([x1, y0+i]), 
                            gridname0=rg_m3m4_thick)
    #m5
    y1 = laygen.get_xy(obj =bnd_top[0], gridname=rg_m4m5_thick)[1]\
                            +laygen.get_xy(obj =bnd_top[0].template, gridname=rg_m4m5_thick)[1]
    input_rails_rect = [rvddl_m4, rvssl_m4]
    rvddl_m5, rvssl_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='L_M5_', 
                layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=y1,
                offset_start_index=1, offset_end_index=0) 
    if sarabe_supply_rail_mode == 0:
        input_rails_rect = [rvddr_m4, rvssr_m4]
        rvddr_m5, rvssr_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='R_M5_',
                    layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y',
                    input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=y1,
                    offset_start_index=0, offset_end_index=0)
    else:
        input_rails_rect = [rvssr_m4, rvddr_m4]
        rvssr_m5, rvddr_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='R_M5_',
                    layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VSS', 'VDD'], direction='y',
                    input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=y1,
                    offset_start_index=0, offset_end_index=0)
    #m6
    input_rails_rect = [rvddl_m5, rvssl_m5]
    rvddl_m6, rvssl_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='L_M6_', 
                layer=laygen.layers['metal'][6], gridname=rg_m5m6_thick, netnames=['VDD', 'VSS'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=None,
                offset_start_index=1, offset_end_index=-1)
    # if laygen.grids.get_phygrid_x(rg_m5m6_thick, 1)==laygen.grids.get_phygrid_x(rg_m1m2, 1)*3:
    #     x1 = laygen.get_xy(obj =bnd_right[0], gridname=rg_m5m6_thick)[0]\
    #          +laygen.get_xy(obj =bnd_right[0].template, gridname=rg_m5m6_thick)[0] - 1
    # else:
    #     x1 = laygen.get_xy(obj=bnd_right[0], gridname=rg_m5m6_thick)[0] \
    #          + laygen.get_xy(obj=bnd_right[0].template, gridname=rg_m5m6_thick)[0] - 0
    x1_phy = laygen.get_xy(obj =bnd_right[0])[0]\
         +laygen.get_xy(obj =bnd_right[0].template)[0]
    x1 = laygen.grids.get_absgrid_x(rg_m5m6_thick, x1_phy)
    print(x1_phy, x1)
    input_rails_rect = [rvddr_m5, rvssr_m5]
    rvddr_m6, rvssr_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='R_M6_', 
                layer=laygen.layers['metal'][6], gridname=rg_m5m6_thick, netnames=['VDD', 'VSS'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=x1,
                offset_start_index=1, offset_end_index=-1)
    #trimming
    for r in rvddr_m6:
        r.xy1[0]=x1_phy
    for r in rvssr_m6:
        r.xy1[0]=x1_phy
    #addtional m6 routes 
    rvdd_m6=[]
    rvss_m6=[]
    #inst_reference=[isp[0], isp[1], iret,ifsm,isl]
    inst_reference=[ifsm,isl]
    inst_reference_offset0=[2, 0]
    inst_reference_offset1=[4, 6]
    #num_route=[10,10]
    num_route=[]
    for i, inst in enumerate(inst_reference):
        num_route.append(laygen.get_xy(obj =inst.template, gridname=rg_m5m6_thick)[1] - 2)
    x0 = laygen.get_xy(obj =bnd_left[0], gridname=rg_m5m6_thick)[0]
    n_vdd_m6=0 #number for m6 wires
    n_vss_m6=0 #number for m6 wires
    for i, inst in enumerate(inst_reference):
        for j in range(inst_reference_offset0[i], num_route[i]-inst_reference_offset1[i]):
            y0 = laygen.get_xy(obj =inst, gridname=rg_m5m6_thick)[1]+1
            r0=laygen.route(None, laygen.layers['metal'][6], xy0=np.array([x0, y0+j]), xy1=np.array([x1, y0+j]), 
                            gridname0=rg_m5m6_thick)
            r0.xy1[0]=x1_phy
            if j%2==0: 
                rvdd_m6.append(r0)
                xy0 = laygen.get_xy(obj =r0, gridname=rg_m5m6_thick)
                laygen.pin(name='VDD_M6' + str(n_vdd_m6), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VDD')
                n_vdd_m6+=1
            else: 
                rvss_m6.append(r0)
                xy0 = laygen.get_xy(obj =r0, gridname=rg_m5m6_thick)
                laygen.pin(name='VSS_M6' + str(n_vss_m6), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VSS')
                n_vss_m6+=1

    return sorted(pin_bot_locx)

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
    rg_m3m4_thick = 'route_M3_M4_basic_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    mycell_list = []
    num_bits=9
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
        sarabe_supply_rail_mode=sizedict['sarabe_supply_rail_mode']
        clkgen_mode=sizedict['sarclkgen']['mux_fast']
    #sarabe generation
    cellname='sarabe_dualdelay' #_'+str(num_bits)+'b'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    pin_bot_locx = generate_sarabe_dualdelay(laygen, objectname_pfix='CA0', workinglib=workinglib,
                    placement_grid=pg, routing_grid_m2m3=rg_m2m3, 
                    routing_grid_m3m4_thick=rg_m3m4_thick, routing_grid_m4m5_thick=rg_m4m5_thick, routing_grid_m5m6_thick=rg_m5m6_thick, 
                    routing_grid_m4m5=rg_m4m5, num_bits=num_bits, sarabe_supply_rail_mode=sarabe_supply_rail_mode,
                                             clkgen_mode=clkgen_mode, origin=np.array([0, 0]))
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

    sizedict['adc_width'] = int(laygen.get_template_xy(cellname, libname=workinglib, gridname=rg_m1m2)[0])
    # save x -co-ordinate of bottom pin locations for reserving tracks in power fill of retimer
    sizedict['reserve_tracks'] = pin_bot_locx
    with open(yamlfile_size, 'w') as stream:
        yaml.dump(sizedict, stream)

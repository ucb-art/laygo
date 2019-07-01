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

def generate_serializer(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m2m3,
                          routing_grid_m4m5, m_dff=1, m_cbuf1=2, m_cbuf2=8, m_pbuf1=2, m_pbuf2=8, m_mux=2, m_out=2, num_ser=8, m_ser=1, origin=np.array([0, 0])):
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m4m5 = routing_grid_m4m5

    tap_name='tap'
    ff_name = 'dff_'+str(int(m_dff))+'x'
    ff_rst_name = 'dff_strsth_'+str(int(m_dff))+'x'
    latch_name = 'latch_2ck_1x'
    inv1_name = 'inv_'+str(int(m_cbuf1))+'x'
    inv2_name = 'inv_'+str(int(m_cbuf2))+'x'
    tinv_name = 'tinv_'+str(int(m_mux))+'x'
    outinv_name = 'inv_'+str(int(m_out))+'x'
    sub_ser = int(num_ser/2)

    #Calculate layout size
    ff_size=laygen.get_xy(obj=laygen.get_template(name = ff_name, libname = templib_logic), gridname = pg)
    ff_rst_size=laygen.get_xy(obj=laygen.get_template(name = ff_rst_name, libname = templib_logic), gridname = pg)
    latch_size=laygen.get_xy(obj=laygen.get_template(name = latch_name, libname = templib_logic), gridname = pg)
    inv1_size=laygen.get_xy(obj=laygen.get_template(name = inv1_name, libname = templib_logic), gridname = pg)
    inv2_size=laygen.get_xy(obj=laygen.get_template(name = inv2_name, libname = templib_logic), gridname = pg)
    tinv_size=laygen.get_xy(obj=laygen.get_template(name = tinv_name, libname = templib_logic), gridname = pg)
    outinv_size=laygen.get_xy(obj=laygen.get_template(name = outinv_name, libname = templib_logic), gridname = pg)
    tap_size=laygen.get_xy(obj=laygen.get_template(name = tap_name, libname = templib_logic), gridname = pg)
    x0=ff_size[0]+ff_rst_size[0]+inv1_size[0]+2*inv2_size[0]+tinv_size[0]+2*tap_size[0]
    num_row=int(sub_ser)+1
    print(ff_size)
    print(laygen.get_xy(obj=laygen.get_template(name = ff_name, libname = templib_logic), gridname = None))
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
    FF0_origin = array_origin + np.array([0, laygen.get_xy(obj=laygen.get_template(name = 'inv_1x', libname = templib_logic), gridname = pg)[1]]) + \
                 np.array([0, laygen.get_xy(obj=laygen.get_template(name = ff_name, libname = templib_logic), gridname = pg)[1]])
    # placement
    iffdiv=[]
    ipbuf1=[]
    ipbuf2=[]
    ipbuf3=[]
    iffin=[]
    itinv=[]
    isp1x=[]
    itapl=[]
    itapr=[]
    tf='R0'
    for i in range(num_row):
        if i%2==0: tf='R0'
        else: tf='MX'
        if i==0: #Reference low 
            itapl.append(laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                                      gridname = pg, xy=tap_origin, transform=tf, shape=np.array([1,1]), template_libname = templib_logic))
            itapr.append(laygen.place(name = "I" + objectname_pfix + 'TAPR0', templatename = tap_name,
                                      gridname = pg, xy=tapr_origin, transform=tf, shape=np.array([1,1]), template_libname = templib_logic))
            iffdiv.append(laygen.place(name = "I" + objectname_pfix + 'FFDIV1', templatename = ff_rst_name,
                                      gridname = pg, xy=array_origin, transform=tf, shape=np.array([1,1]), template_libname = templib_logic))
            ipbuf1.append(laygen.relplace(name = "I" + objectname_pfix + 'P1BUF1', templatename = inv1_name,
                                   gridname = pg, refinstname = iffdiv[-1].name, transform=tf, shape=np.array([1,1]),
                                   template_libname=templib_logic))
            ipbuf2.append(laygen.relplace(name = "I" + objectname_pfix + 'P1BUF2', templatename = inv2_name,
                                   gridname = pg, refinstname = ipbuf1[-1].name, transform=tf, shape=np.array([1,1]),
                                   template_libname=templib_logic))
            ipbuf3.append(laygen.relplace(name = "I" + objectname_pfix + 'P1BUF3', templatename = inv2_name,
                                   gridname = pg, refinstname = ipbuf2[-1].name, transform=tf, shape=np.array([1,1]),
                                   template_libname=templib_logic))
            iffin.append(laygen.relplace(name = "I" + objectname_pfix + 'FFIN1', templatename = ff_name,
                                   gridname = pg, refinstname = ipbuf3[-1].name, transform=tf, shape=np.array([1,1]),
                                   template_libname=templib_logic))
            itinv.append(laygen.relplace(name = "I" + objectname_pfix + 'TINV1', templatename = tinv_name,
                                   gridname = pg, refinstname = iffin[-1].name, transform=tf, shape=np.array([1,1]),
                                   template_libname=templib_logic))
        else:
            itapl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPL'+str(i), templatename = tap_name,
                           gridname = pg, refinstname = itapl[-1].name, transform=tf, shape=np.array([1,1]),
                           direction = 'top', template_libname=templib_logic))
            itapr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPR'+str(i), templatename = tap_name,
                           gridname = pg, refinstname = itapr[-1].name, transform=tf, shape=np.array([1,1]),
                           direction = 'top', template_libname=templib_logic))
            if i==num_row-1: #Top row for last bit latch, input clock buffer, and outinv
                iclkbuf1=laygen.relplace(name = "I" + objectname_pfix + 'CLKBUF1', templatename = inv1_name,
                                   gridname = pg, refinstname = iffdiv[-1].name, transform=tf, shape=np.array([1,1]),
                                   xy=np.array([(-ff_rst_size[0]+inv1_size[0])/2,0]), direction = 'top', template_libname=templib_logic)
                iclkbuf2=laygen.relplace(name = "I" + objectname_pfix + 'CLKBUF2', templatename = inv2_name,
                                   gridname = pg, refinstname = iclkbuf1.name, transform=tf, shape=np.array([1,1]),
                                   template_libname=templib_logic)
                ilatch=laygen.relplace(name = "I" + objectname_pfix + 'LATCH0', templatename = latch_name,
                                   gridname = pg, refinstname = iffin[-1].name, transform=tf, shape=np.array([1,1]),
                                   xy=np.array([(ff_size[0]-latch_size[0])/2,0]), direction = 'top', template_libname=templib_logic)
                ioutinv=laygen.relplace(name = "I" + objectname_pfix + 'OUTINV', templatename = inv1_name,
                                   gridname = pg, refinstname = itinv[-1].name, transform=tf, shape=np.array([1,1]),
                                   xy=np.array([(tinv_size[0]-outinv_size[0])/2,0]), direction = 'top', template_libname=templib_logic)
            elif i==num_row-2: #Row for the last bit (p0 row)
                iffdiv.append(laygen.relplace(name = "I" + objectname_pfix + 'FFDIV0', templatename = ff_rst_name,
                                   gridname = pg, refinstname = iffdiv[-1].name, transform=tf, shape=np.array([1,1]),
                                   direction = 'top', template_libname=templib_logic))
                ipbuf1.append(laygen.relplace(name = "I" + objectname_pfix + 'P0BUF1', templatename = inv1_name,
                                   gridname = pg, refinstname = ipbuf1[-1].name, transform=tf, shape=np.array([1,1]),
                                   direction = 'top', template_libname=templib_logic))
                ipbuf2.append(laygen.relplace(name = "I" + objectname_pfix + 'P0BUF2', templatename = inv2_name,
                                   gridname = pg, refinstname = ipbuf2[-1].name, transform=tf, shape=np.array([1,1]),
                                   direction = 'top', template_libname=templib_logic))
                ipbuf3.append(laygen.relplace(name = "I" + objectname_pfix + 'P0BUF3', templatename = inv2_name,
                                   gridname = pg, refinstname = ipbuf3[-1].name, transform=tf, shape=np.array([1,1]),
                                   direction = 'top', template_libname=templib_logic))
                iffin.append(laygen.relplace(name = "I" + objectname_pfix + 'FFIN0', templatename = ff_name,
                                   gridname = pg, refinstname = iffin[-1].name, transform=tf, shape=np.array([1,1]),
                                   direction = 'top', template_libname=templib_logic))
                itinv.append(laygen.relplace(name = "I" + objectname_pfix + 'TINV0', templatename = tinv_name,
                                   gridname = pg, refinstname = itinv[-1].name, transform=tf, shape=np.array([1,1]),
                                   direction = 'top', template_libname=templib_logic))
            else:
                iffdiv.append(laygen.relplace(name = "I" + objectname_pfix + 'FFDIV'+str(i+1), templatename = ff_rst_name,
                                   gridname = pg, refinstname = iffdiv[-1].name, transform=tf, shape=np.array([1,1]),
                                   direction = 'top', template_libname=templib_logic))
                ipbuf1.append(laygen.relplace(name = "I" + objectname_pfix + 'P'+str(i+1)+'BUF1', templatename = inv1_name,
                                   gridname = pg, refinstname = ipbuf1[-1].name, transform=tf, shape=np.array([1,1]),
                                   direction = 'top', template_libname=templib_logic))
                ipbuf2.append(laygen.relplace(name = "I" + objectname_pfix + 'P'+str(i+1)+'BUF2', templatename = inv2_name,
                                   gridname = pg, refinstname = ipbuf2[-1].name, transform=tf, shape=np.array([1,1]),
                                   direction = 'top', template_libname=templib_logic))
                ipbuf3.append(laygen.relplace(name = "I" + objectname_pfix + 'P'+str(i+1)+'BUF3', templatename = inv2_name,
                                   gridname = pg, refinstname = ipbuf3[-1].name, transform=tf, shape=np.array([1,1]),
                                   direction = 'top', template_libname=templib_logic))
                iffin.append(laygen.relplace(name = "I" + objectname_pfix + 'FFIN'+str(i+1), templatename = ff_name,
                                   gridname = pg, refinstname = iffin[-1].name, transform=tf, shape=np.array([1,1]),
                                   direction = 'top', template_libname=templib_logic))
                itinv.append(laygen.relplace(name = "I" + objectname_pfix + 'TINV'+str(i+1), templatename = tinv_name,
                                   gridname = pg, refinstname = itinv[-1].name, transform=tf, shape=np.array([1,1]),
                                   direction = 'top', template_libname=templib_logic))
    #Space placement at the last row
    space_name = 'space_1x'
    space4x_name = 'space_4x'
    space_width = laygen.get_xy(obj=laygen.get_template(name = space_name, libname = templib_logic), gridname = pg)[0]
    space4_width = laygen.get_xy(obj=laygen.get_template(name = space4x_name, libname = templib_logic), gridname = pg)[0]
    blank1_width = x0 - (2*tap_size + inv1_size + inv2_size + tinv_size + latch_size)[0]
    blank2_width = (tinv_size - inv1_size)[0]
    m_space4 = int(blank1_width / space4_width)
    m_space1 = int((blank1_width-m_space4*space4_width)/space_width)
    #m_space1 = int(blank1_width / space_width)
    m_space2 = int(blank2_width / space_width)
    if num_row%2==0: tf_s='MX'
    else: tf_s='R0'
    ispace4=laygen.relplace(name = "I" + objectname_pfix + 'SPACE4', templatename = space4x_name,
                           gridname = pg, refinstname = iclkbuf2.name, transform=tf_s, shape=np.array([m_space4-1,1]),
                           template_libname=templib_logic)
    ispace1=laygen.relplace(name = "I" + objectname_pfix + 'SPACE1', templatename = space_name,
                           gridname = pg, refinstname = ispace4.name, transform=tf_s, shape=np.array([m_space1+4,1]),
                           template_libname=templib_logic)
    #ispace1=laygen.relplace(name = "I" + objectname_pfix + 'SPACE1', templatename = space_name,
                           #gridname = pg, refinstname = iclkbuf2.name, transform=tf_s, shape=np.array([m_space1,1]),
                           #template_libname=templib_logic)
    ispace2=laygen.relplace(name = "I" + objectname_pfix + 'SPACE2', templatename = space_name,
                           gridname = pg, refinstname = ilatch.name, transform=tf_s, shape=np.array([m_space2,1]),
                           template_libname=templib_logic)

    #Internal Pins
    ffin_in_xy=[]
    ffin_in_xy45=[]
    ffin_out_xy=[]
    ffin_clk_xy=[]
    ffdiv_in_xy=[]
    ffdiv_out_xy45=[]
    ffdiv_out_xy=[]
    ffdiv_clk_xy=[]
    ffdiv_rst_xy=[]
    ffdiv_st_xy=[]
    ffdiv_st_xy45=[]
    pbuf1_in_xy=[]
    pbuf1_out_xy=[]
    pbuf2_in_xy=[]
    pbuf2_out_xy=[]
    pbuf3_in_xy=[]
    pbuf3_out_xy=[]
    tinv_in_xy=[]
    tinv_out_xy=[]
    tinv_en_xy=[]
    tinv_enb_xy=[]
    for i in range(sub_ser):
        ffin_in_xy.append(laygen.get_inst_pin_xy(iffin[i].name, 'I', rg_m3m4))
        ffin_out_xy.append(laygen.get_inst_pin_xy(iffin[i].name, 'O', rg_m3m4))
        ffin_clk_xy.append(laygen.get_inst_pin_xy(iffin[i].name, 'CLK', rg_m3m4))
        ffdiv_in_xy.append(laygen.get_inst_pin_xy(iffdiv[i].name, 'I', rg_m3m4))
        ffdiv_out_xy.append(laygen.get_inst_pin_xy(iffdiv[i].name, 'O', rg_m3m4))
        ffdiv_clk_xy.append(laygen.get_inst_pin_xy(iffdiv[i].name, 'CLK', rg_m3m4))
        ffdiv_rst_xy.append(laygen.get_inst_pin_xy(iffdiv[i].name, 'RST', rg_m3m4))
        ffdiv_st_xy.append(laygen.get_inst_pin_xy(iffdiv[i].name, 'ST', rg_m3m4))
        ffdiv_st_xy45.append(laygen.get_inst_pin_xy(iffdiv[i].name, 'ST', rg_m4m5))
        ffin_in_xy45.append(laygen.get_inst_pin_xy(iffin[i].name, 'I', rg_m4m5))
        ffdiv_out_xy45.append(laygen.get_inst_pin_xy(iffdiv[i].name, 'O', rg_m4m5))
        pbuf1_in_xy.append(laygen.get_inst_pin_xy(ipbuf1[i].name, 'I', rg_m3m4))
        pbuf1_out_xy.append(laygen.get_inst_pin_xy(ipbuf1[i].name, 'O', rg_m3m4))
        pbuf2_in_xy.append(laygen.get_inst_pin_xy(ipbuf2[i].name, 'I', rg_m3m4))
        pbuf2_out_xy.append(laygen.get_inst_pin_xy(ipbuf2[i].name, 'O', rg_m3m4))
        pbuf3_in_xy.append(laygen.get_inst_pin_xy(ipbuf3[i].name, 'I', rg_m3m4))
        pbuf3_out_xy.append(laygen.get_inst_pin_xy(ipbuf3[i].name, 'O', rg_m3m4))
        tinv_in_xy.append(laygen.get_inst_pin_xy(itinv[i].name, 'I', rg_m3m4))
        tinv_out_xy.append(laygen.get_inst_pin_xy(itinv[i].name, 'O', rg_m3m4))
        tinv_en_xy.append(laygen.get_inst_pin_xy(itinv[i].name, 'EN', rg_m3m4))
        tinv_enb_xy.append(laygen.get_inst_pin_xy(itinv[i].name, 'ENB', rg_m3m4))

    # Route
    for i in range(sub_ser):
        if iffdiv[i].transform=='MX': offset=6
        if iffdiv[i].transform=='R0': offset=8
        if iffin[i].transform=='MX': offset_p=-5
        if iffin[i].transform=='R0': offset_p=5
        if not i==sub_ser-1:
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], #DIVFF 
                    ffdiv_in_xy[i][0], ffdiv_out_xy[i+1][0], ffdiv_in_xy[i][0][1]+offset, rg_m3m4)
            rclk=laygen.route(None, laygen.layers['metal'][3], xy0=ffdiv_clk_xy[i][0], xy1=ffdiv_clk_xy[i+1][0], gridname0=rg_m3m4) #CLK
            rp0buf=laygen.route(None, laygen.layers['metal'][3], xy0=ffin_clk_xy[i][0], xy1=ffin_clk_xy[i+1][0], gridname0=rg_m3m4) #P0BUF
            [rh0, rv0] = laygen.route_hv(laygen.layers['metal'][2], laygen.layers['metal'][3],  #ST to VSS
                        laygen.get_inst_pin_xy(iffdiv[i].name, 'VSS', rg_m2m3)[0], laygen.get_inst_pin_xy(iffdiv[i].name, 'ST', rg_m2m3)[0], rg_m2m3)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], #FFin to tinv
                        ffin_out_xy[i][0], tinv_in_xy[i][1], ffin_out_xy[i][0][1], rg_m3m4)
            if not i==sub_ser-2: #RST routing
                rrst=laygen.route(None, laygen.layers['metal'][3], xy0=ffdiv_rst_xy[i][0], xy1=ffdiv_rst_xy[i+1][0], gridname0=rg_m3m4)
            else: #RST-ST crossing
                [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                        ffdiv_rst_xy[i][0], ffdiv_st_xy45[i+1][0]-np.array([4,0]), ffdiv_rst_xy[i][0][1], rg_m3m4,
                        layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
                [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                        ffdiv_st_xy[i+1][0], ffdiv_st_xy45[i+1][0]-np.array([4,1]), ffdiv_st_xy[i+1][0][1], rg_m3m4,
                        layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
        else: #p0 row
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], #DIV feedback path
                    ffdiv_in_xy[i][0], ffdiv_out_xy45[0][0]+np.array([4,0]), ffdiv_in_xy[i][0][1]+offset, rg_m3m4,
                    layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], #M3-to-M5
                    ffdiv_out_xy[0][0], ffdiv_out_xy45[0][0]+np.array([4,1]), ffdiv_out_xy[0][0][1], rg_m3m4, 
                    layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],  #Clock
                    ffdiv_clk_xy[i][0], laygen.get_inst_pin_xy(iclkbuf2.name, 'O', rg_m3m4)[0], ffdiv_clk_xy[i][0][1] + offset + 1, rg_m3m4)
            [rh0, rv0] = laygen.route_hv(laygen.layers['metal'][2], laygen.layers['metal'][3],  #RST
                        laygen.get_inst_pin_xy(iffdiv[i].name, 'VSS', rg_m2m3)[0], laygen.get_inst_pin_xy(iffdiv[i].name, 'RST', rg_m2m3)[0], rg_m2m3)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], #p0buf to FFin
                        pbuf2_out_xy[i][0], ffin_clk_xy[i][0], pbuf2_out_xy[i][0][1]+offset_p, rg_m3m4)
            #Latch connections
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],  #Input
                    laygen.get_inst_pin_xy(ilatch.name, 'I', rg_m3m4)[0], ffin_out_xy[i][0],
                                               laygen.get_inst_pin_xy(ilatch.name, 'I', rg_m3m4)[0][1] - offset, rg_m3m4)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],  #p0buf
                    pbuf2_out_xy[i][0], laygen.get_inst_pin_xy(ilatch.name, 'CLKB', rg_m3m4)[0] - np.array([2, 0]), ffin_out_xy[i][0][1] + offset_p, rg_m3m4)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],  #p0buf
                    laygen.get_inst_pin_xy(ilatch.name, 'CLKB', rg_m3m4)[0], laygen.get_inst_pin_xy(ilatch.name, 'CLKB', rg_m3m4)[0] - np.array([2, 0]),
                                               laygen.get_inst_pin_xy(ilatch.name, 'CLKB', rg_m3m4)[0][1], rg_m3m4)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],  #p0bufb
                    pbuf3_out_xy[i][0], laygen.get_inst_pin_xy(ilatch.name, 'CLK', rg_m3m4)[0] + np.array([2, 0]),
                                               pbuf3_out_xy[i][0][1] + offset_p - (-1) ** (i%2), rg_m3m4)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],  #p0bufb
                    laygen.get_inst_pin_xy(ilatch.name, 'CLK', rg_m3m4)[0], laygen.get_inst_pin_xy(ilatch.name, 'CLK', rg_m3m4)[0] + np.array([2, 0]),
                                               laygen.get_inst_pin_xy(ilatch.name, 'CLK', rg_m3m4)[0][1], rg_m3m4)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],  #tinv
                    laygen.get_inst_pin_xy(ilatch.name, 'O', rg_m3m4)[0], tinv_in_xy[i][0],
                                               laygen.get_inst_pin_xy(ilatch.name, 'O', rg_m3m4)[0][1], rg_m3m4)
        #Multiphase buffer
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                ffdiv_out_xy[i][0]+np.array([0,0]), pbuf1_in_xy[i][0], ffdiv_out_xy[i][0][1], rg_m3m4, extendr=2)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                pbuf1_out_xy[i][1], pbuf2_in_xy[i][0], pbuf1_out_xy[i][1][1], rg_m3m4)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                pbuf2_out_xy[i][1], pbuf3_in_xy[i][0], pbuf2_out_xy[i][1][1], rg_m3m4)
        #Multiphase to TINV
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                pbuf2_out_xy[i][0], tinv_en_xy[i][0], pbuf2_out_xy[i][0][1]+offset_p, rg_m3m4)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                pbuf3_out_xy[i][0], tinv_enb_xy[i][0], pbuf3_out_xy[i][0][1]+offset_p-(-1)**(i%2), rg_m3m4)
        #MUX
        if not i==sub_ser-1:
            routb=laygen.route(None, laygen.layers['metal'][3], xy0=tinv_out_xy[i][0], xy1=tinv_out_xy[i+1][0], gridname0=rg_m3m4) #OUTB
        else:
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],  #OUTINV
                        tinv_out_xy[i][0], laygen.get_inst_pin_xy(ioutinv.name, 'I', rg_m3m4)[1] - np.array([2, 0]),
                                               tinv_out_xy[i][0][1], rg_m3m4)
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],  #OUTINV
                        laygen.get_inst_pin_xy(ioutinv.name, 'I', rg_m3m4)[1], laygen.get_inst_pin_xy(ioutinv.name, 'I', rg_m3m4)[1] - np.array([2, 0]),
                                               laygen.get_inst_pin_xy(ioutinv.name, 'I', rg_m3m4)[1][1], rg_m3m4, extendr=2)
    #CLKIN buffer
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                       laygen.get_inst_pin_xy(iclkbuf1.name, 'O', rg_m3m4)[0], laygen.get_inst_pin_xy(iclkbuf2.name, 'I', rg_m3m4)[0],
                                       laygen.get_inst_pin_xy(iclkbuf1.name, 'O', rg_m3m4)[0][1], rg_m3m4)

    #Pin
    clkin_xy=laygen.get_inst_pin_xy(iclkbuf1.name, 'I', rg_m3m4)[1]
    [rv0, rclkin] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], 
            clkin_xy, np.array([0,clkin_xy[1]]), rg_m3m4)
    laygen.boundary_pin_from_rect(rclkin, rg_m3m4, "clk_in", laygen.layers['pin'][4], size=4, direction='left')
    for i in range(sub_ser):
        if iffin[i].transform=='MX': offset_din=4
        if iffin[i].transform=='R0': offset_din=6
        din_xy34=laygen.get_inst_pin_xy(iffin[i].name, 'I', rg_m3m4)
        [rv0, rh0] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                din_xy34[1], np.array([0,din_xy34[0][1]+offset_din]), rg_m3m4)
        if not i==sub_ser-1:
            laygen.boundary_pin_from_rect(rh0, rg_m3m4, "in<" + str(i + 1) + ">", laygen.layers['pin'][4],
                                          size=4, direction='left')
        else:
            laygen.boundary_pin_from_rect(rh0, rg_m3m4, "in<0>", laygen.layers['pin'][4], size=4,
                                          direction='left')
    datao_xy=laygen.get_inst_pin_xy(ioutinv.name, 'O', rg_m3m4)
    laygen.pin(name='out', layer=laygen.layers['pin'][3], xy=datao_xy, gridname=rg_m3m4)
    #[rv0, rdatao] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], 
    #        datao_xy[0], datao_xy+np.array([5,0]), rg_m3m4)
    #laygen.boundary_pin_from_rect(rdatao, rg_m3m4, "out", laygen.layers['pin'][4], size=4, direction='right')
    laygen.pin(name='p1buf', layer=laygen.layers['pin'][3], xy=pbuf2_out_xy[0], gridname=rg_m3m4)
    rrst=laygen.route(None, laygen.layers['metal'][3], xy0=ffdiv_rst_xy[0][0], xy1=np.array([ffdiv_rst_xy[0][0][0],0]), gridname0=rg_m3m4)
    laygen.boundary_pin_from_rect(rrst, rg_m3m4, "RST", laygen.layers['pin'][3], size=4, direction='bottom')

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
        cell_name='ser_'+str(int(specdict['num_ser']/2))+'to1'
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
    generate_serializer(laygen, objectname_pfix='SER', templib_logic=logictemplib, 
                          placement_grid=pg, routing_grid_m2m3=rg_m2m3, routing_grid_m4m5=rg_m4m5, num_ser=num_ser,
                          m_dff=m_dff, m_cbuf1=m_cbuf1, m_cbuf2=m_cbuf2, m_pbuf1=m_pbuf1, m_pbuf2=m_pbuf2, m_mux=m_mux, m_out=m_out, m_ser=m_ser, origin=np.array([0, 0]))
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

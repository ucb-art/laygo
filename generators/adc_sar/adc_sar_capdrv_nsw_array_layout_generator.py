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
from math import log, ceil
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

def generate_capdrv_array(laygen, objectname_pfix, templib_logic, cdrv_name_list, placement_grid, routing_grid_m2m3,
                          routing_grid_m4m5, num_bits=8, num_bits_row=4, num_output_routes=2, origin=np.array([0, 0])):
    """generate cap driver array """
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m4m5 = routing_grid_m4m5
    num_row=ceil(num_bits/num_bits_row)

    tap_name='tap_wovdd'
    cdrv_name='capdrv_nsw_8x'
    #cdac_name='capdac_'+str(num_bits)+'b'
    cdac_name='capdac'
    space_1x_name = 'space_wovdd_1x'
    space_2x_name = 'space_wovdd_2x'
    space_4x_name = 'space_wovdd_4x'

    #space cell insertion
    #1. making it fit to DAC-DAC dimension
    x0 = laygen.templates.get_template(cdac_name, libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2 \
         - laygen.templates.get_template(cdrv_name_list[0], libname=workinglib).xy[1][0] * num_bits_row \
         - laygen.templates.get_template(tap_name, libname=templib_logic).xy[1][0] * 3
    m_space = int(round(x0 / laygen.templates.get_template(space_1x_name, libname=templib_logic).xy[1][0]))
    m_space = max(0, m_space)
    m_space_4x = 0
    m_space_2x = 0
    m_space_1x = m_space
    #print(laygen.templates.get_template(cdac_name, libname=workinglib).xy[1][0])
    #print(laygen.templates.get_template(cdrv_name_list[0], libname=workinglib).xy[1][0])
    x0 = laygen.templates.get_template(tap_name, libname=templib_logic).xy[1][0] * 3 \
         + laygen.templates.get_template(cdrv_name_list[0], libname=workinglib).xy[1][0] * num_bits_row \
         + laygen.templates.get_template(space_1x_name, libname=templib_logic).xy[1][0] * m_space_1x \
         + laygen.templates.get_template(space_2x_name, libname=templib_logic).xy[1][0] * m_space_2x
    print(x0, m_space)
    m_space_4x = int(m_space / 4)
    m_space_2x = int((m_space - m_space_4x * 4) / 2)
    m_space_1x = int(m_space - m_space_4x * 4 - m_space_2x * 2)
    #print(m_space, m_space_4x, m_space_2x)


    #boundaries
    m_bnd = int(round(x0 / laygen.templates.get_template('boundary_bottom').xy[1][0]))
    devname_bnd_left = []
    devname_bnd_right = []
    transform_bnd_left = []
    transform_bnd_right = []
    for i in range(num_row):
        if i%2==0:
            devname_bnd_left += ['nmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            devname_bnd_left += ['nmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'nmos4_fast_right']
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
    array_origin = origin + laygen.get_xy(obj = bnd_bottom[0], gridname = pg) \
                   + laygen.get_xy(obj = bnd_bottom[0].template, gridname = pg)
    # placement
    itapl=[]
    icdrv=[]
    itapr=[]
    isp4x=[]
    isp2x=[]
    isp1x=[]
    ispfill=[]
    for i in range(num_row):
        if i==0: 
            itapl.append(laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                                      gridname = pg, xy=array_origin, shape=np.array([2,1]), template_libname = templib_logic))
            tf='R0'
        else:
            if i%2==0: tf='R0'
            else: tf='MX'
            itapl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPL'+str(i), templatename = tap_name,
                                   gridname = pg, refinstname = itapl[-1].name, transform=tf, shape=np.array([2,1]),
                                   direction = 'top', template_libname=templib_logic))
        refi = itapl[-1].name
        for j in range(num_bits_row): #main driver
            if num_bits_row*i+j < num_bits:
                cdrv_name=cdrv_name_list[i*num_bits_row+j]
                icdrv.append(laygen.relplace(name = "I" + objectname_pfix + 'CDRV'+str(i)+'_'+str(j), templatename = cdrv_name,
                                       gridname = pg, refinstname = refi, transform=tf, 
                                       template_libname=workinglib))
                refi = icdrv[-1].name
            else: #cell filler
                xfill0 = laygen.templates.get_template(cdrv_name_list[0], libname=workinglib).xy[1][0]
                m_space_fill = int(round(xfill0 / laygen.templates.get_template(space_1x_name, libname=templib_logic).xy[1][0]))
                m_space_fill_4x = int(m_space_fill / 4)
                m_space_fill_2x = int((m_space_fill - m_space_fill_4x * 4) / 2)
                m_space_fill_1x = int(m_space_fill - m_space_fill_4x * 4 - m_space_fill_2x * 2)
                if not m_space_fill_4x==0:
                    ispfill.append(laygen.relplace(name=None, templatename=space_4x_name,
                                 shape = np.array([m_space_fill_4x, 1]), transform=tf, gridname=pg,
                                 refinstname=refi, template_libname=templib_logic))
                    refi = ispfill[-1].name
                if not m_space_fill_2x==0:
                    ispfill.append(laygen.relplace(name=None, templatename=space_2x_name,
                                 shape = np.array([m_space_fill_2x, 1]), transform=tf, gridname=pg,
                                 refinstname=refi, template_libname=templib_logic))
                    refi = ispfill[-1].name
                if not m_space_fill_1x==0:
                    ispfill.append(laygen.relplace(name=None, templatename=space_1x_name,
                                 shape=np.array([m_space_fill_1x, 1]), transform=tf, gridname=pg,
                                 refinstname=refi, template_libname=templib_logic))
                    refi = ispfill[-1].name
        #row filler
        if not m_space_4x==0:
            isp4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP4X'+str(i), templatename=space_4x_name,
                         shape = np.array([m_space_4x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp4x[-1].name
        if not m_space_2x==0:
            isp2x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2X'+str(i), templatename=space_2x_name,
                         shape = np.array([m_space_2x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp2x[-1].name
        if not m_space_1x==0:
            isp1x.append(laygen.relplace(name="I" + objectname_pfix + 'SP1X'+str(i), templatename=space_1x_name,
                         shape=np.array([m_space_1x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp1x[-1].name
        itapr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPR'+str(i), templatename = tap_name,
                               gridname = pg, refinstname = refi, transform=tf, template_libname = templib_logic))

    # internal pins
    icdrv_en0_xy=[]
    icdrv_en1_xy=[]
    icdrv_en2_xy=[]
    icdrv_vref0_xy=[]
    icdrv_vref1_xy=[]
    icdrv_vref2_xy=[]
    icdrv_vo_xy=[]
    for i in range(num_row):
        for j in range(num_bits_row):
            if num_bits_row*i+j < num_bits:
                icdrv_en0_xy.append(laygen.get_inst_pin_xy(icdrv[i * num_bits_row + j].name, 'EN<0>', rg_m4m5))
                icdrv_en1_xy.append(laygen.get_inst_pin_xy(icdrv[i * num_bits_row + j].name, 'EN<1>', rg_m4m5))
                icdrv_en2_xy.append(laygen.get_inst_pin_xy(icdrv[i * num_bits_row + j].name, 'EN<2>', rg_m4m5))
                icdrv_vref0_xy.append(laygen.get_inst_pin_xy(icdrv[i * num_bits_row + j].name, 'VREF<0>', rg_m4m5))
                icdrv_vref1_xy.append(laygen.get_inst_pin_xy(icdrv[i * num_bits_row + j].name, 'VREF<1>', rg_m4m5))
                icdrv_vref2_xy.append(laygen.get_inst_pin_xy(icdrv[i * num_bits_row + j].name, 'VREF<2>', rg_m4m5))
                icdrv_vo_xy.append(laygen.get_inst_pin_xy(icdrv[i * num_bits_row + j].name, 'VO', rg_m4m5))

    # reference route coordinate
    x0 = icdrv_en0_xy[0][0][0]
    y0 = laygen.get_xy(obj =icdrv[0], gridname=rg_m4m5)[1]
    y1 = laygen.get_xy(obj =icdrv[-1], gridname=rg_m4m5)[1]
    if num_row%2==1:
        y1 += laygen.get_xy(obj =icdrv[-1].template, gridname=rg_m4m5)[1]
    # vref route
    rvref0=[]
    rvref1=[]
    rvref2=[]
    for i in range(num_row):
        rvref0.append(laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m4m5,
                              refinstname0=icdrv[i*num_bits_row].name, refpinname0='VREF<0>', refinstindex0=np.array([0, 0]),
                              refinstname1=icdrv[i*num_bits_row].name, refpinname1='VREF<0>', refinstindex1=np.array([num_bits_row-1, 0])))
        rvref1.append(laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m4m5,
                              refinstname0=icdrv[i*num_bits_row].name, refpinname0='VREF<1>', refinstindex0=np.array([0, 0]),
                              refinstname1=icdrv[i*num_bits_row].name, refpinname1='VREF<1>', refinstindex1=np.array([num_bits_row-1, 0])))
        rvref2.append(laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m4m5,
                              refinstname0=icdrv[i*num_bits_row].name, refpinname0='VREF<2>', refinstindex0=np.array([0, 0]),
                              refinstname1=icdrv[i*num_bits_row].name, refpinname1='VREF<2>', refinstindex1=np.array([num_bits_row-1, 0])))
    # vref vertical route
    if not num_row==0:
        for i in range(1, num_row):
            [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], icdrv_vref0_xy[0][0], icdrv_vref0_xy[i*num_bits_row][0], x0-12, rg_m4m5)
            [rh0, rv1, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], icdrv_vref1_xy[0][0], icdrv_vref1_xy[i*num_bits_row][0], x0-8, rg_m4m5)
            [rh0, rv2, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], icdrv_vref2_xy[0][0], icdrv_vref2_xy[i*num_bits_row][0], x0-10, rg_m4m5)
            #equalize vertical route for pin generation
            rv0_xy=laygen.get_xy(obj = rv0, gridname = rg_m4m5, sort=True)
            rv1_xy=laygen.get_xy(obj = rv1, gridname = rg_m4m5, sort=True)
            rv2_xy=laygen.get_xy(obj = rv2, gridname = rg_m4m5, sort=True)
            rv_y0=min((2, rv0_xy[0][1], rv1_xy[0][1], rv2_xy[0][1]))
            rv_y1=max((rv0_xy[1][1], rv1_xy[1][1], rv2_xy[1][1]))
            rvref0v=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([rv0_xy[0][0], rv_y0]), xy1=np.array([rv0_xy[1][0], rv_y1]), gridname0=rg_m4m5)
            rvref1v=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([rv1_xy[0][0], rv_y0]), xy1=np.array([rv1_xy[1][0], rv_y1]), gridname0=rg_m4m5)
            rvref2v=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([rv2_xy[0][0], rv_y0]), xy1=np.array([rv2_xy[1][0], rv_y1]), gridname0=rg_m4m5)
            #additional routes for better integrity
            [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], icdrv_vref0_xy[0][0], icdrv_vref0_xy[i*num_bits_row][0], x0-6, rg_m4m5)
            [rh0, rv1, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], icdrv_vref1_xy[0][0], icdrv_vref1_xy[i*num_bits_row][0], x0-2, rg_m4m5)
            [rh0, rv2, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], icdrv_vref2_xy[0][0], icdrv_vref2_xy[i*num_bits_row][0], x0-4, rg_m4m5)
            #equalize vertical route for pin generation
            rv0_xy=laygen.get_xy(obj = rv0, gridname = rg_m4m5, sort=True)
            rv1_xy=laygen.get_xy(obj = rv1, gridname = rg_m4m5, sort=True)
            rv2_xy=laygen.get_xy(obj = rv2, gridname = rg_m4m5, sort=True)
            rv_y0=min((2, rv0_xy[0][1], rv1_xy[0][1], rv2_xy[0][1]))
            rv_y1=max((rv0_xy[1][1], rv1_xy[1][1], rv2_xy[1][1]))
            rvref0v2=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([rv0_xy[0][0], rv_y0]), xy1=np.array([rv0_xy[1][0], rv_y1]), gridname0=rg_m4m5)
            rvref1v2=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([rv1_xy[0][0], rv_y0]), xy1=np.array([rv1_xy[1][0], rv_y1]), gridname0=rg_m4m5)
            rvref2v2=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([rv2_xy[0][0], rv_y0]), xy1=np.array([rv2_xy[1][0], rv_y1]), gridname0=rg_m4m5)
            
            
    # en route
    x0 = laygen.get_template_pin_xy(cdac_name, 'I<' + str(num_bits - num_bits_h) + '>', rg_m4m5, libname=workinglib)[0][0]
    x1 = laygen.get_template_size(cdrv_name_list[0], gridname=rg_m4m5, libname=workinglib)[0]
    ren0 = []
    ren1 = []
    ren2 = []
    for i in range(num_row):
        for j in range(num_bits_row):
            if num_bits_row*i+j < num_bits:
                rh0, _ren0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                             icdrv_en0_xy[num_bits_row * i + j][0],
                                             # np.array([x0 - num_row * 2 - i - j * x1, y0]), rg_m4m5)
                                             np.array([x0 - 1 + num_row * 0 + num_output_routes*num_row + i + j * x1, y0]), rg_m4m5)
                                             # np.array([icdrv_en0_xy[num_bits_row * i + j][0][0] + i*3 + 3 + 12, y0]), rg_m4m5)
                ren0.append(_ren0)
                rh0, _ren1 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                             icdrv_en1_xy[num_bits_row * i + j][0],
                                             # np.array([x0 - num_row * 1 - i - j * x1, y0]), rg_m4m5)
                                             np.array([x0 - 1 + num_row * 1 + num_output_routes*num_row + i + j * x1, y0]), rg_m4m5)
                                             # np.array([icdrv_en1_xy[num_bits_row * i + j][0][0] + i*3 + 4 + 12, y0]), rg_m4m5)
                ren1.append(_ren1)
                rh0, _ren2 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                             icdrv_en2_xy[num_bits_row * i + j][0],
                                             # np.array([x0 - num_row* 0 - i - j * x1, y0]), rg_m4m5)
                                             np.array([x0 - 1 + num_row * 2 + num_output_routes*num_row + i + j * x1, y0]), rg_m4m5)
                                             # np.array([icdrv_en2_xy[num_bits_row * i + j][0][0] + i*3 + 5 + 12, y0]), rg_m4m5)
                ren2.append(_ren2)
    # vc0 route
    rh0, rvc0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                 icdrv_vref1_xy[0][0],
                                 np.array([x0+1, y1]), rg_m4m5)
                                 # np.array([icdrv_en0_xy[0][0][0] + num_row*3 + 4 + 12, y1]), rg_m4m5)
    # vo route
    rvo = []
    for k in range(num_output_routes):
        for i in range(num_row):
            for j in range(num_bits_row):
                if num_bits_row*i+j < num_bits:
                    rh0, _rvo = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                                icdrv_vo_xy[num_bits_row * i + j][0],
                                                np.array([x0 + 2 + i + k*num_row + j * x1, y1]), rg_m4m5)
                                                # np.array([icdrv_en0_xy[num_bits_row * i + j][0][0] + num_row*3 + 6 + i + 12 + k*num_row, y1]), rg_m4m5)
                    rvo.append(_rvo)
                    #output_pin
                    laygen.boundary_pin_from_rect(_rvo, rg_m4m5,
                                                         "VO" + str(k) + "<" + str(i * num_bits_row + j) + ">",
                                                  laygen.layers['pin'][5], size=6, direction='top',
                                                  netname="VO<" + str(i * num_bits_row + j) + ">")
    #pins
    laygen.boundary_pin_from_rect(rvref0[0], rg_m4m5, "VREF<0>", laygen.layers['pin'][4], size=4,
                                  direction='left')
    laygen.boundary_pin_from_rect(rvref1[0], rg_m4m5, "VREF<1>", laygen.layers['pin'][4], size=4,
                                  direction='left')
    laygen.boundary_pin_from_rect(rvref2[0], rg_m4m5, "VREF<2>", laygen.layers['pin'][4], size=4,
                                  direction='left')
    laygen.pin(name='VREF_M5<0>', layer=laygen.layers['pin'][5], xy=laygen.get_xy(obj = rvref0v, gridname=rg_m4m5), gridname=rg_m4m5, netname='VREF<0>')
    laygen.pin(name='VREF_M5<1>', layer=laygen.layers['pin'][5], xy=laygen.get_xy(obj = rvref1v, gridname=rg_m4m5), gridname=rg_m4m5, netname='VREF<1>')
    laygen.pin(name='VREF_M5<2>', layer=laygen.layers['pin'][5], xy=laygen.get_xy(obj = rvref2v, gridname=rg_m4m5), gridname=rg_m4m5, netname='VREF<2>')
    laygen.pin(name='VREF_M5_2<0>', layer=laygen.layers['pin'][5], xy=laygen.get_xy(obj = rvref0v2, gridname=rg_m4m5), gridname=rg_m4m5, netname='VREF<0>')
    laygen.pin(name='VREF_M5_2<1>', layer=laygen.layers['pin'][5], xy=laygen.get_xy(obj = rvref1v2, gridname=rg_m4m5), gridname=rg_m4m5, netname='VREF<1>')
    laygen.pin(name='VREF_M5_2<2>', layer=laygen.layers['pin'][5], xy=laygen.get_xy(obj = rvref2v2, gridname=rg_m4m5), gridname=rg_m4m5, netname='VREF<2>')
    
    for i, _ren0 in enumerate(ren0):
        laygen.boundary_pin_from_rect(_ren0, rg_m4m5, "EN" + str(i) + "<0>", laygen.layers['pin'][5], size=6,
                                      direction='bottom')
    for i, _ren1 in enumerate(ren1):
        laygen.boundary_pin_from_rect(_ren1, rg_m4m5, "EN" + str(i) + "<1>", laygen.layers['pin'][5], size=6,
                                      direction='bottom')
    for i, _ren2 in enumerate(ren2):
        laygen.boundary_pin_from_rect(_ren2, rg_m4m5, "EN" + str(i) + "<2>", laygen.layers['pin'][5], size=6,
                                      direction='bottom')
    laygen.boundary_pin_from_rect(rvc0, rg_m4m5, "VO_C0", laygen.layers['pin'][5], size=6, direction='top',
                                  netname="VREF<1>")

    # power pin
    pwr_dim_left=laygen.get_xy(obj =itapl[-1].template, gridname=rg_m2m3)[0]
    pwr_dim_right=pwr_dim_left
    if m_space_4x>1:
        pwr_dim_right+= laygen.get_xy(obj =isp4x[0].template, gridname=rg_m2m3)[0] * (m_space_4x - 1)
    pwr_dim_right = min(pwr_dim_right, 10) # max number of tracks for avoiding short
    pwr_dim_delta=pwr_dim_right-pwr_dim_left
    rvdd = []
    rvss = []
    if num_row%2==0: rp1='VSS0'
    else: rp1='VSS1'
    #for i in range(1, int(pwr_dim_left/2)):
    for i in range(1, int(pwr_dim_left)):
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS0', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin(name = 'VSSL'+str(i-1), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
    for i in range(1, int(pwr_dim_right/2)):
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i-pwr_dim_delta, 0]), xy1=np.array([2*i-pwr_dim_delta, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS0', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin(name = 'VSSR'+str(i-1), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
    for i in range(num_row):
        for j in range(1, int(pwr_dim_left/2)):
            rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0='route_M2_M3_mos',
                         refinstname0=itapl[i].name, refpinname0='VSS1', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                         refinstname1=itapl[i].name, refpinname1='VSS0', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))
        for j in range(1, int(pwr_dim_right/2)):
            rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j-pwr_dim_delta, 0]), xy1=np.array([2*j-pwr_dim_delta, 0]), gridname0='route_M2_M3_mos',
                         refinstname0=itapr[i].name, refpinname0='VSS1', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                         refinstname1=itapr[i].name, refpinname1='VSS0', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))

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
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'


    #display
    #laygen.display()
    #laygen.templates.display()
    #laygen.save_template(filename=workinglib+'_templates.yaml', libname=workinglib)

    mycell_list = []
    #capdrv generation
    cell_name='capdrv_nsw_array'
    cdrv_name_list=[
        'capdrv_nsw_2x',
        'capdrv_nsw_2x',
        'capdrv_nsw_2x',
        'capdrv_nsw_2x',
        'capdrv_nsw_2x',
        'capdrv_nsw_2x',
        'capdrv_nsw_4x',
        'capdrv_nsw_8x',
        ]
    m_list=[2, 2, 2, 2, 2, 2, 2, 2]

    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        num_bits=specdict['n_bit']-1
        num_bits_h=sizedict['capdac']['num_bits_horizontal']
        m_list=sizedict['capdrv']['m_list']
        cdrv_name_list=[]
        for i, m in enumerate(m_list):
            cdrv_name_list.append('capdrv_nsw_'+str(m)+'x')

    print(cell_name+" generating")
    mycell_list.append(cell_name)
    laygen.add_cell(cell_name)
    laygen.sel_cell(cell_name)
    generate_capdrv_array(laygen, objectname_pfix='CA0', templib_logic=logictemplib, cdrv_name_list=cdrv_name_list,
                          placement_grid=pg, routing_grid_m2m3=rg_m2m3, routing_grid_m4m5=rg_m4m5, 
                          num_bits=num_bits, num_bits_row=2, num_output_routes=2, origin=np.array([0, 0]))
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

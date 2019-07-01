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

"""DES library
"""
import laygo
import numpy as np
#from logic_layout_generator import *
from math import log
import yaml
import os
#import logging;logging.basicConfig(level=logging.DEBUG)

def add_to_export_ports(export_ports, pins):
    if type(pins) != list:
        pins = [pins]

    for pin in pins:
        netname = pin.netname
        bbox_float = pin.xy.reshape((1,4))[0]
        for ind in range(len(bbox_float)): # keeping only 3 decimal places
            bbox_float[ind] = float('%.3f' % bbox_float[ind])
        port_entry = dict(layer=int(pin.layer[0][1]), bbox=bbox_float.tolist())
        if netname in export_ports.keys():
            export_ports[netname].append(port_entry)
        else:
            export_ports[netname] = [port_entry]

    return export_ports

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

def generate_deserializer(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m2m3,
                          routing_grid_m4m5, num_des=8, num_flop=1, m_des_dff=1, origin=np.array([0, 0])):
    """generate deserializer """
    export_dict = {'boundaries': {'lib_name': 'ge_tech_logic_templates',
                                  'lr_width': 8,
                                  'tb_height': 0.5},
                   'cells': {cell_name: {'cell_name': cell_name,
                                                 'lib_name': workinglib,
                                                 'size': [40, 1]}},
                   'spaces': [{'cell_name': 'space_4x',
                               'lib_name': 'ge_tech_logic_templates',
                               'num_col': 4},
                              {'cell_name': 'space_2x',
                               'lib_name': 'ge_tech_logic_templates',
                               'num_col': 2}],
                   'tech_params': {'col_pitch': 0.09,
                                   'directions': ['x', 'y', 'x', 'y'],
                                   'height': 0.96,
                                   'layers': [2, 3, 4, 5],
                                   'spaces': [0.064, 0.05, 0.05, 0.05],
                                   'widths': [0.032, 0.04, 0.04, 0.04]}}
    export_ports = dict()
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m4m5 = routing_grid_m4m5

    tap_name='tap'
    #ff_name = 'dff_1x'
    #ff_rst_name = 'dff_strsth_1x'
    ff_name = 'dff_'+str(m_des_dff)+'x'
    ff_rst_name = 'dff_strsth_'+str(m_des_dff)+'x'

    #Calculate layout size
    x0=num_flop * (2*laygen.templates.get_template(ff_name, templib_logic).xy[1][0] + laygen.templates.get_template(ff_rst_name, templib_logic).xy[1][0]) \
            + 2*laygen.templates.get_template(tap_name, templib_logic).xy[1][0]
    num_row=int((num_des/num_flop + 0.99))+1
    size_x=x0 + 2*laygen.templates.get_template('boundary_bottomleft').xy[1][0]
    size_y=num_row*laygen.templates.get_template(ff_name, templib_logic).xy[1][1] + 2*laygen.templates.get_template('boundary_bottom').xy[1][1]
    #boundaries
    m_bnd = int(x0 / laygen.templates.get_template('boundary_bottom').xy[1][0])
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
    tap_origin = origin + laygen.get_inst_xy(name = bnd_bottom[0].name, gridname = pg) \
                   + laygen.get_template_xy(name = bnd_bottom[0].cellname, gridname = pg)
    array_origin = origin + laygen.get_inst_xy(name = bnd_bottom[0].name, gridname = pg) \
                   + laygen.get_template_xy(name = bnd_bottom[0].cellname, gridname = pg) \
                   + np.array([laygen.get_template_xy(name = tap_name, gridname = pg, libname = templib_logic)[0], 0])
    tapr_origin = tap_origin + m_bnd*np.array([laygen.get_template_xy(name = 'boundary_bottom', gridname = pg)[0], 0]) \
                   - np.array([laygen.get_template_xy(name = tap_name, gridname = pg, libname = templib_logic)[0], 0])
    FF0_origin = array_origin + np.array([0, laygen.get_template_xy(name = 'inv_1x', gridname = pg, libname = templib_logic)[1]]) + \
                 np.array([0, laygen.get_template_xy(name = ff_name, gridname = pg, libname = templib_logic)[1]])
    # placement
    iffout=[]
    iffin=[]
    iffdiv=[]
    iclkbuf=[]
    idivbuf=[]
    isp1x=[]
    itapl=[]
    itapr=[]
    clkbuf_name_list=[]
    divbuf_name_list=[]
    tf='R0'
    for i, m in enumerate(clkbuf_list):
        clkbuf_name_list.append('inv_'+str(m)+'x')
    for i, m in enumerate(divbuf_list):
        divbuf_name_list.append('inv_'+str(m)+'x')
    if num_flop == 1: #Layout height reduction factor, no reduction
        for i in range(num_row):
            if i%2==0: tf='R0'
            else: tf='MX'
            if i==0: #Row for clock buffers 
                itapl.append(laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                                          gridname = pg, xy=tap_origin, transform=tf, shape=np.array([1,1]), template_libname = templib_logic))
                itapr.append(laygen.place(name = "I" + objectname_pfix + 'TAPR0', templatename = tap_name,
                                          gridname = pg, xy=tapr_origin, transform=tf, shape=np.array([1,1]), template_libname = templib_logic))
                for j in range(len(divbuf_list)):
                    if j==0:
                        idivbuf.append(laygen.place(name = "I" + objectname_pfix + 'DIVBUF'+str(j), templatename = divbuf_name_list[len(divbuf_list)-j-1],
                                          gridname = pg, xy=array_origin, transform=tf, shape=np.array([1,1]), template_libname = templib_logic))
                    else:
                        idivbuf.append(laygen.relplace(name = "I" + objectname_pfix + 'DIVBUF'+str(j), templatename = divbuf_name_list[len(divbuf_list)-j-1],
                                       gridname = pg, refinstname = idivbuf[-1].name, transform=tf, shape=np.array([1,1]),
                                       template_libname=templib_logic))
                    print(idivbuf[j].name)
                for k in range(len(clkbuf_list)):
                    if k==0:
                        iclkbuf.append(laygen.relplace(name = "I" + objectname_pfix + 'CLKBUF'+str(k), templatename = clkbuf_name_list[k],
                                          gridname = pg, refinstname = idivbuf[len(divbuf_list)-1].name, transform=tf, shape=np.array([1,1]), xy=np.array([0,0]), template_libname = templib_logic))
                    else:
                        iclkbuf.append(laygen.relplace(name = "I" + objectname_pfix + 'CLKBUF'+str(k), templatename = clkbuf_name_list[k],
                                       gridname = pg, refinstname = iclkbuf[-1].name, transform=tf, shape=np.array([1,1]),
                                       template_libname=templib_logic))
            else:
                itapl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPL'+str(i), templatename = tap_name,
                               gridname = pg, refinstname = itapl[-1].name, transform=tf, shape=np.array([1,1]),
                               direction = 'top', template_libname=templib_logic))
                itapr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPR'+str(i), templatename = tap_name,
                               gridname = pg, refinstname = itapr[-1].name, transform=tf, shape=np.array([1,1]),
                               direction = 'top', template_libname=templib_logic))
                if i==1: #Reference FF: FFOUT1
                    iffout.append(laygen.place(name = "I" + objectname_pfix + 'FFOUT1', templatename = ff_name,
                                          gridname = pg, xy=FF0_origin, transform=tf, shape=np.array([1,1]), template_libname = templib_logic))
                else:
                    iffout.append(laygen.relplace(name = "I" + objectname_pfix + 'FFOUT'+str(i), templatename = ff_name,
                                       gridname = pg, refinstname = iffout[-1].name, transform=tf, shape=np.array([1,1]),
                                       direction = 'top', template_libname=templib_logic))
                refi = iffout[-1].name
                iffin.append(laygen.relplace(name = "I" + objectname_pfix + 'FFIN'+str(i), templatename = ff_name,
                                       gridname = pg, refinstname = refi, transform=tf, shape=np.array([1,1]),
                                       template_libname=templib_logic))
                refi2 = iffin[-1].name
                iffdiv.append(laygen.relplace(name = "I" + objectname_pfix + 'FFDIV'+str(i), templatename = ff_rst_name,
                                       gridname = pg, refinstname = refi2, transform=tf, shape=np.array([1,1]),
                                       template_libname=templib_logic))
    if num_flop == 2: #Layout height reduced by half
        for i in range(num_row):
            if i%2==0: tf='R0'
            else: tf='MX'
            if i==0: #Low for clock buffers 
                itapl.append(laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                                          gridname = pg, xy=tap_origin, transform=tf, shape=np.array([1,1]), template_libname = templib_logic))
                itapr.append(laygen.place(name = "I" + objectname_pfix + 'TAPR0', templatename = tap_name,
                                          gridname = pg, xy=tapr_origin, transform=tf, shape=np.array([1,1]), template_libname = templib_logic))
                idivbuf.append(laygen.place(name = "I" + objectname_pfix + 'DIVBUF32x', templatename = 'inv_32x',
                                          gridname = pg, xy=array_origin, transform=tf, shape=np.array([1,1]), template_libname = templib_logic))
                idivbuf.append(laygen.relplace(name = "I" + objectname_pfix + 'DIVBUF8x', templatename = 'inv_8x',
                                       gridname = pg, refinstname = idivbuf[-1].name, transform=tf, shape=np.array([1,1]),
                                       template_libname=templib_logic))
                idivbuf.append(laygen.relplace(name = "I" + objectname_pfix + 'DIVBUF2x', templatename = 'inv_2x',
                                       gridname = pg, refinstname = idivbuf[-1].name, transform=tf, shape=np.array([1,1]),
                                       template_libname=templib_logic))
                idivbuf.append(laygen.relplace(name = "I" + objectname_pfix + 'DIVBUF1x', templatename = 'inv_1x',
                                       gridname = pg, refinstname = idivbuf[-1].name, transform=tf, shape=np.array([1,1]),
                                       template_libname=templib_logic))
                iclkbuf.append(laygen.relplace(name = "I" + objectname_pfix + 'CLKBUF1x', templatename = 'inv_1x',
                                       gridname = pg, refinstname = idivbuf[3].name, transform=tf, shape=np.array([1,1]), xy=np.array([0,0]),
                                       template_libname=templib_logic))
                iclkbuf.append(laygen.relplace(name = "I" + objectname_pfix + 'CLKBUF2x', templatename = 'inv_2x',
                                       gridname = pg, refinstname = iclkbuf[-1].name, transform=tf, shape=np.array([1,1]),
                                       template_libname=templib_logic))
                iclkbuf.append(laygen.relplace(name = "I" + objectname_pfix + 'CLKBUF8x', templatename = 'inv_8x',
                                       gridname = pg, refinstname = iclkbuf[-1].name, transform=tf, shape=np.array([1,1]),
                                       template_libname=templib_logic))
                iclkbuf.append(laygen.relplace(name = "I" + objectname_pfix + 'CLKBUF32x', templatename = 'inv_32x',
                                       gridname = pg, refinstname = iclkbuf[-1].name, transform=tf, shape=np.array([1,1]),
                                       template_libname=templib_logic))
            else:
                itapl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPL'+str(i), templatename = tap_name,
                               gridname = pg, refinstname = itapl[-1].name, transform=tf, shape=np.array([1,1]),
                               direction = 'top', template_libname=templib_logic))
                itapr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPR'+str(i), templatename = tap_name,
                               gridname = pg, refinstname = itapr[-1].name, transform=tf, shape=np.array([1,1]),
                               direction = 'top', template_libname=templib_logic))
                if i==1: #Reference FF: FFOUT1 and FFOUT2
                    iffout.append(laygen.place(name = "I" + objectname_pfix + 'FFOUT1', templatename = ff_name,
                                          gridname = pg, xy=FF0_origin, transform=tf, shape=np.array([1,1]), template_libname = templib_logic))
                    iffout.append(laygen.relplace(name = "I" + objectname_pfix + 'FFOUT2', templatename = ff_name,
                                       gridname = pg, refinstname = iffout[0].name, transform=tf, shape=np.array([1,1]),
                                       direction = 'right', template_libname=templib_logic))
                elif i==(num_row-1): #The last low depending on num_des: even or odd
                    iffout.append(laygen.relplace(name = "I" + objectname_pfix + 'FFOUT'+str(2*i-1), templatename = ff_name,
                                       gridname = pg, refinstname = iffout[-2].name, transform=tf, shape=np.array([1,1]),
                                       direction = 'top', template_libname=templib_logic))
                    if num_des%2==0: #If not, space should be placed rather than FF
                        iffout.append(laygen.relplace(name = "I" + objectname_pfix + 'FFOUT'+str(2*i), templatename = ff_name,
                                       gridname = pg, refinstname = iffout[-1].name, transform=tf, shape=np.array([1,1]),
                                       direction = 'right', template_libname=templib_logic))
                else: #FFOUTs will be the reference for FFIN and FFDIV
                    iffout.append(laygen.relplace(name = "I" + objectname_pfix + 'FFOUT'+str(2*i-1), templatename = ff_name,
                                       gridname = pg, refinstname = iffout[-2].name, transform=tf, shape=np.array([1,1]),
                                       direction = 'top', template_libname=templib_logic))
                    iffout.append(laygen.relplace(name = "I" + objectname_pfix + 'FFOUT'+str(2*i), templatename = ff_name,
                                       gridname = pg, refinstname = iffout[-1].name, transform=tf, shape=np.array([1,1]),
                                       direction = 'right', template_libname=templib_logic))
        for j in range(num_des): #Relplace of FFIN and the left side of FFDIV
            if iffout[j].transform=='MX': tf='MX'
            else: tf='R0'
            iffin.append(laygen.relplace(name = "I" + objectname_pfix + 'FFIN'+str(j+1), templatename = ff_name,
                                         gridname = pg, refinstname = iffout[j].name, transform=tf, shape=np.array([1,1]),
                                         xy=np.array([laygen.get_template_xy(name = ff_name, gridname = pg, libname = templib_logic)[0], 0]), template_libname=templib_logic))
            if j%2==0:
                iffdiv.append(laygen.relplace(name = "I" + objectname_pfix + 'FFDIV'+str(int(j/2+1)), templatename = ff_rst_name,
                                              gridname = pg, refinstname = iffin[j].name, transform=tf, shape=np.array([1,1]),
                                              xy=np.array([laygen.get_template_xy(name = ff_name, gridname = pg, libname = templib_logic)[0], 0]), template_libname=templib_logic))
        for i in range(num_row, num_des+1): #Right side of FFDIV
            if num_des%2==1:
                if i%2==0: tf='R0'
                else: tf='MX'
            if num_des%2==0:
                if i%2==0: tf='MX'
                else: tf='R0'
            if i==num_row: #Even: relplaced by top FFDIV, odd: relplaced by second FFDIV from top
                iffdiv.append(laygen.relplace(name = "I" + objectname_pfix + 'FFDIV'+str(i), templatename = ff_rst_name,
                               gridname = pg, refinstname = iffdiv[int(num_des/2)-1].name, transform=tf, shape=np.array([1,1]),
                               direction = 'right', template_libname=templib_logic))
            else:
                iffdiv.append(laygen.relplace(name = "I" + objectname_pfix + 'FFDIV'+str(i), templatename = ff_rst_name,
                               gridname = pg, refinstname = iffdiv[-1].name, transform=tf, shape=np.array([1,1]),
                               direction = 'bottom', template_libname=templib_logic))

    #Space placement at the first row
    space_name = 'space_1x'
    space4x_name = 'space_4x'
    space_width = laygen.get_template_xy(name = space_name, gridname = pg, libname = templib_logic)[0]
    space4_width = laygen.get_template_xy(name = space4x_name, gridname = pg, libname = templib_logic)[0]
    inv_width_div=0
    for i, m in enumerate(divbuf_list):
        inv_width_div=inv_width_div+laygen.get_template_xy(name = 'inv_' + str(m) + 'x', gridname = pg, libname = templib_logic)[0]
    inv_width_clk=0
    for i, m in enumerate(clkbuf_list):
        inv_width_clk=inv_width_clk+laygen.get_template_xy(name = 'inv_' + str(m) + 'x', gridname = pg, libname = templib_logic)[0]
    blank_width = tapr_origin[0] - array_origin[0] - inv_width_div - inv_width_clk
    m_space4 = int(blank_width / space4_width)
    m_space1 = int((blank_width-m_space4*space4_width)/space_width)
    ispace4=laygen.relplace(name = "I" + objectname_pfix + 'SPACE4', templatename = space4x_name,
                           gridname = pg, refinstname = iclkbuf[3].name, transform='R0', shape=np.array([m_space4-1,1]),
                           template_libname=templib_logic)
    ispace1=laygen.relplace(name = "I" + objectname_pfix + 'SPACE1', templatename = space_name,
                           gridname = pg, refinstname = ispace4.name, transform='R0', shape=np.array([m_space1+4,1]),
                           template_libname=templib_logic)
    #Space placement at the last row for odd num_des
    m_ff_space = int(laygen.get_template_xy(name = ff_name, gridname = pg, libname = templib_logic)[0] / space_width)
    m_ffrst_space = int(laygen.get_template_xy(name = ff_rst_name, gridname = pg, libname = templib_logic)[0] / space_width)
    if (num_des%2)==1:
        if num_flop==2:
            ispace_out=laygen.relplace(name = "I" + objectname_pfix + 'SPACEOUT', templatename = space_name,
                           gridname = pg, refinstname = iffout[num_des-1].name, transform=iffout[num_des-1].transform, shape=np.array([m_ff_space,1]),
                           template_libname=templib_logic)
            ispace_in=laygen.relplace(name = "I" + objectname_pfix + 'SPACEIN', templatename = space_name,
                           gridname = pg, refinstname = iffin[num_des-1].name, transform=iffin[num_des-1].transform, shape=np.array([m_ff_space,1]),
                           template_libname=templib_logic)
            ispace_div=laygen.relplace(name = "I" + objectname_pfix + 'SPACEDIV', templatename = space_name,
                           gridname = pg, refinstname = iffdiv[int(num_des/2)].name, transform=iffdiv[int(num_des/2)].transform, shape=np.array([m_ffrst_space,1]),
                           template_libname=templib_logic)
        
    #Internal Pins
    ffin_in_xy=[]
    ffin_in_xy45=[]
    ffin_out_xy=[]
    ffout_in_xy=[]
    ffout_out_xy=[]
    ffdiv_in_xy=[]
    ffdiv_in_xy45=[]
    ffdiv_out_xy=[]
    ffdiv_rst_xy=[]
    ffdiv_st_xy=[]
    for i in range(num_des):
        ffin_in_xy.append(laygen.get_inst_pin_xy(iffin[i].name, 'I', rg_m3m4))
        ffin_out_xy.append(laygen.get_inst_pin_xy(iffin[i].name, 'O', rg_m3m4))
        ffout_in_xy.append(laygen.get_inst_pin_xy(iffout[i].name, 'I', rg_m3m4))
        ffout_out_xy.append(laygen.get_inst_pin_xy(iffout[i].name, 'O', rg_m3m4))
        ffdiv_in_xy.append(laygen.get_inst_pin_xy(iffdiv[i].name, 'I', rg_m3m4))
        ffdiv_out_xy.append(laygen.get_inst_pin_xy(iffdiv[i].name, 'O', rg_m3m4))
        ffdiv_rst_xy.append(laygen.get_inst_pin_xy(iffdiv[i].name, 'RST', rg_m3m4))
        ffdiv_st_xy.append(laygen.get_inst_pin_xy(iffdiv[i].name, 'ST', rg_m3m4))
        ffin_in_xy45.append(laygen.get_inst_pin_xy(iffin[i].name, 'I', rg_m4m5))
        ffdiv_in_xy45.append(laygen.get_inst_pin_xy(iffdiv[i].name, 'I', rg_m4m5))
    # Route
    for i in range(num_des):
        if num_flop==1: #Routing offset selection for rows in R0 and MX
            if iffin[i].transform=='MX': offset=1
            if iffin[i].transform=='R0': offset=4
            if iffdiv[i].transform=='MX': offset_div=1
            if iffdiv[i].transform=='R0': offset_div=3
        if num_flop==2: #Offset_div would be different because of different placement
            if i in range(int((num_des+1)/2)):
                if iffin[i].transform=='MX': 
                    if i%2==1:
                        offset=1
                    else:
                        offset=8
                if iffin[i].transform=='R0': offset=3+i%2
                if iffdiv[i].transform=='MX': offset_div=1
                if iffdiv[i].transform=='R0': offset_div=3
            else:
                if iffin[i].transform=='MX':
                    if i%2==1:
                        offset=1
                    else:
                        offset=8
                if iffin[i].transform=='R0': offset=3+i%2
                if iffdiv[i].transform=='MX': offset_div=10
                if iffdiv[i].transform=='R0': offset_div=13
        if i in range(num_des-1):
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], #in-to-in
                        ffin_out_xy[i][0], ffin_in_xy[i+1][0], ffin_out_xy[i][1][1]+7-offset, rg_m3m4)  
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], #div-to-div 
                        ffdiv_out_xy[i][0], ffdiv_in_xy[i+1][0]-np.array([0,0]), ffdiv_out_xy[i][1][1]+7-offset_div, rg_m3m4)
                #[rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                #        ffdiv_in_xy[i+1][0], ffdiv_in_xy[i+1][0]-np.array([0,0]), ffdiv_in_xy[i+1][0][1], rg_m3m4)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], #in-to-out
                    ffin_out_xy[i][0], ffout_in_xy[i][0], ffin_out_xy[i][1][1]+7-offset, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], #div feedback
                ffdiv_out_xy[num_des-1][0], ffdiv_in_xy45[0][0]+np.array([4,0]), ffdiv_out_xy[num_des-1][1][1]+7-offset_div, 
                rg_m3m4, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], #M3-to-M5
                ffdiv_in_xy[0][0], ffdiv_in_xy45[0][1]+np.array([4,0]), ffdiv_in_xy[0][0][1], rg_m3m4, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
    if ext_clk==True:
        for i in range(num_des):
            [rh0, rv1] = laygen.route_hv(laygen.layers['metal'][2], laygen.layers['metal'][3],
                                           laygen.get_inst_pin_xy(iffdiv[i].name, 'VSS', rg_m2m3)[0], laygen.get_inst_pin_xy(iffdiv[i].name, 'I', rg_m2m3)[0],
                                           rg_m2m3)
            
    #CLK Buffer
    for i in range(3):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                           laygen.get_inst_pin_xy(iclkbuf[i].name, 'O', rg_m3m4)[0], laygen.get_inst_pin_xy(iclkbuf[i + 1].name, 'I', rg_m3m4)[0],
                                           laygen.get_inst_pin_xy(iclkbuf[i].name, 'O', rg_m3m4)[0][1] + i % 2, rg_m3m4)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                           laygen.get_inst_pin_xy(idivbuf[3 - i].name, 'O', rg_m3m4)[0], laygen.get_inst_pin_xy(idivbuf[2 - i].name, 'I', rg_m3m4)[0],
                                           laygen.get_inst_pin_xy(idivbuf[3 - i].name, 'O', rg_m3m4)[0][1] + i % 2, rg_m3m4)

    #DIVCLK Route
    if ext_clk==False:
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                       laygen.get_inst_pin_xy(idivbuf[3].name, 'I', rg_m3m4)[0], laygen.get_inst_pin_xy(iffdiv[0].name, 'I', rg_m3m4)[0],
                                       laygen.get_inst_pin_xy(idivbuf[3].name, 'I', rg_m3m4)[0][1] + 3, rg_m3m4)
    for i in range(num_des):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                           laygen.get_inst_pin_xy(idivbuf[0].name, 'O', rg_m3m4)[0], laygen.get_inst_pin_xy(iffout[i].name, 'CLK', rg_m3m4)[0],
                                           laygen.get_inst_pin_xy(idivbuf[0].name, 'O', rg_m3m4)[0][1] + 5, rg_m3m4)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                           laygen.get_inst_pin_xy(iclkbuf[3].name, 'O', rg_m3m4)[0], laygen.get_inst_pin_xy(iffin[i].name, 'CLK', rg_m3m4)[0],
                                           laygen.get_inst_pin_xy(iclkbuf[3].name, 'O', rg_m3m4)[0][1] + 6, rg_m3m4)
        if ext_clk == False:
            [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                           laygen.get_inst_pin_xy(iclkbuf[3].name, 'O', rg_m3m4)[0], laygen.get_inst_pin_xy(iffdiv[i].name, 'CLK', rg_m3m4)[0],
                                           laygen.get_inst_pin_xy(iclkbuf[3].name, 'O', rg_m3m4)[0][1] + 6, rg_m3m4)
        else:
            [rh0, rv1] = laygen.route_hv(laygen.layers['metal'][2], laygen.layers['metal'][3],
                                           laygen.get_inst_pin_xy(iffdiv[i].name, 'VSS', rg_m2m3)[0], laygen.get_inst_pin_xy(iffdiv[i].name, 'CLK', rg_m2m3)[0],
                                           rg_m2m3)
    #RST Route
    for i in range(num_des):
        if i in range(int((num_des+1)/2)): #First half of FFDIVs
            if not i==int((num_des+1)/2)-1:
                rrst=laygen.route(None, laygen.layers['metal'][3], xy0=ffdiv_rst_xy[i][0], xy1=ffdiv_rst_xy[i+1][0], gridname0=rg_m3m4)
                rst=laygen.route(None, laygen.layers['metal'][3], xy0=ffdiv_st_xy[i][0], xy1=ffdiv_st_xy[i+1][0], gridname0=rg_m3m4)
                #[rrstv, rrsth] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                #        ffdiv_rst_xy[i][0], ffdiv_rst_xy[i+1][0], rg_m3m4)
                #[rstv, rsth] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                #        ffdiv_st_xy[i][0], ffdiv_st_xy[i+1][0], rg_m3m4)
            else:
                [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                        ffdiv_rst_xy[i][0], ffdiv_st_xy[i+1][0], ffdiv_rst_xy[i][1][1]+7, rg_m3m4)
        else: #Second half of FFDIVs
            if not i==num_des-1:
                rst=laygen.route(None, laygen.layers['metal'][3], xy0=ffdiv_st_xy[i][0], xy1=ffdiv_st_xy[i+1][0], gridname0=rg_m3m4)
                rrst=laygen.route(None, laygen.layers['metal'][3], xy0=ffdiv_rst_xy[i][0], xy1=ffdiv_rst_xy[i+1][0], gridname0=rg_m3m4)
                #[rrstv, rrsth] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                #        ffdiv_rst_xy[i][0], ffdiv_rst_xy[i+1][0], rg_m3m4)
                #[rstv, rsth] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                #        ffdiv_st_xy[i][0], ffdiv_st_xy[i+1][0], rg_m3m4)
    [rh0, rv0] = laygen.route_hv(laygen.layers['metal'][2], laygen.layers['metal'][3],
                                 laygen.get_inst_pin_xy(iffdiv[0].name, 'VSS', rg_m2m3)[0], laygen.get_inst_pin_xy(iffdiv[0].name, 'ST', rg_m2m3)[0], rg_m2m3)
    [rh0, rv0] = laygen.route_hv(laygen.layers['metal'][2], laygen.layers['metal'][3],
                                 laygen.get_inst_pin_xy(iffdiv[num_des - 1].name, 'VSS', rg_m2m3)[0], laygen.get_inst_pin_xy(iffdiv[num_des - 1].name, 'RST', rg_m2m3)[0], rg_m2m3)
                        
    #Pin
    clkin_xy=laygen.get_inst_pin_xy(iclkbuf[0].name, 'I', rg_m3m4)
    rclkin=laygen.route(None, laygen.layers['metal'][3], xy0=clkin_xy[0], xy1=np.array([clkin_xy[0][0],0]), gridname0=rg_m3m4)
    CLK_pin=laygen.boundary_pin_from_rect(rclkin, rg_m3m4, "clk", laygen.layers['pin'][3], size=0, direction='left')
    export_ports = add_to_export_ports(export_ports, CLK_pin)
    #if ext_clk==True:
    divin_xy=laygen.get_inst_pin_xy(idivbuf[len(divbuf_list)-1].name, 'I', rg_m3m4)
    rdivin=laygen.route(None, laygen.layers['metal'][3], xy0=divin_xy[0], xy1=np.array([divin_xy[0][0],0]), gridname0=rg_m3m4)
    div_pin=laygen.boundary_pin_from_rect(rdivin, rg_m3m4, "div<0>", laygen.layers['pin'][3], size=0, direction='left')
    export_ports = add_to_export_ports(export_ports, div_pin)
    din_xy34=laygen.get_inst_pin_xy(iffin[0].name, 'I', rg_m3m4)
    din_xy45=laygen.get_inst_pin_xy(iffin[0].name, 'I', rg_m4m5)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
            din_xy34[0], np.array([din_xy45[0][0]-2,0]), din_xy34[0][1], 
            rg_m3m4, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
    [rv2, rh3, rv4] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][4], 
            np.array([din_xy45[0][0]-2,0]), np.array([din_xy34[0][0]+4,0]), 4, 
            rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4)
    rdummy = laygen.route(None, laygen.layers['metal'][4], xy0=din_xy34[0], xy1=din_xy34[0]+np.array([2,0]), gridname0=rg_m3m4)
    in_pin=laygen.boundary_pin_from_rect(rv4, rg_m3m4, "in", laygen.layers['pin'][3], size=4, direction='bottom')
    export_ports = add_to_export_ports(export_ports, in_pin)
    for i in range(num_des):
        datao_xy = laygen.get_inst_pin_xy(iffout[i].name, 'O', rg_m3m4)
        rdatao=laygen.route(None, laygen.layers['metal'][3], xy0=datao_xy[0], xy1=datao_xy[1], gridname0=rg_m3m4)
        datao_pin=laygen.boundary_pin_from_rect(rdatao, rg_m3m4, 'dout<'+str(i)+'>', laygen.layers['pin'][3], size=0, direction='left')
        #datao_pin=laygen.pin(name='dout<'+str(i)+'>', layer=laygen.layers['pin'][3], xy=datao_xy, gridname=rg_m3m4)
        export_ports = add_to_export_ports(export_ports, datao_pin)
    clkdiv_xy = laygen.get_inst_pin_xy(iffout[-1].name, 'CLK', rg_m3m4)
    clkdiv_pin=laygen.pin(name='clk_div', layer=laygen.layers['pin'][3], xy=clkdiv_xy, gridname=rg_m3m4)
    export_ports = add_to_export_ports(export_ports, clkdiv_pin)
    rst_xy34=laygen.get_inst_pin_xy(iffdiv[0].name, 'RST', rg_m3m4)
    rst_xy45=laygen.get_inst_pin_xy(iffdiv[0].name, 'RST', rg_m4m5)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
            rst_xy34[0], np.array([rst_xy45[0][0]-2,0]), rst_xy34[0][1], 
            rg_m3m4, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
    [rv2, rh2, rv3] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][4], 
            np.array([rst_xy45[0][0]-2,0]), np.array([rst_xy34[0][0]+4,0]), 4, 
            rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4)
    rdummy = laygen.route(None, laygen.layers['metal'][4], xy0=rst_xy34[0], xy1=rst_xy34[0]+np.array([2,0]), gridname0=rg_m3m4)
    rst_pin=laygen.boundary_pin_from_rect(rv3, rg_m3m4, "RST", laygen.layers['pin'][3], size=4, direction='bottom')
    export_ports = add_to_export_ports(export_ports, rst_pin)

    # power pin
    pwr_dim=laygen.get_template_xy(name=itapl[-1].cellname, gridname=rg_m2m3, libname=itapl[-1].libname)
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
        vdd_pin=laygen.pin(name = 'VDD'+str(2*i-2), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        vss_pin=laygen.pin(name = 'VSS'+str(2*i-2), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
        export_ports = add_to_export_ports(export_ports, vdd_pin)
        export_ports = add_to_export_ports(export_ports, vss_pin)
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2+1, 0]), xy1=np.array([2*i+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        vdd_pin=laygen.pin(name = 'VDD'+str(2*i-1), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        vss_pin=laygen.pin(name = 'VSS'+str(2*i-1), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
        export_ports = add_to_export_ports(export_ports, vdd_pin)
        export_ports = add_to_export_ports(export_ports, vss_pin)
    
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
    
    # export_dict will be written to a yaml file for using with StdCellBase

    export_dict['cells'][cell_name]['ports'] = export_ports
    export_dict['cells'][cell_name]['size_um'] = [float(int(size_x*1e3))/1e3, float(int(size_y*1e3))/1e3]
    #export_dict['cells']['clk_dis_N_units']['num_ways'] = num_ways
    # print('export_dict:')
    # pprint(export_dict)
    # save_path = path.dirname(path.dirname(path.realpath(__file__))) + '/dsn_scripts/'
    save_path = workinglib 
    #if path.isdir(save_path) == False:
    #    mkdir(save_path)
    with open(save_path + '_int.yaml', 'w') as f:
        yaml.dump(export_dict, f, default_flow_style=False)

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
        cell_name='des_1to'+str(specdict['num_des'])
        num_des=specdict['num_des']
        num_flop=specdict['num_flop']
        ext_clk=specdict['ext_clk']
        m_des_dff=sizedict['m_des_dff']
        clkbuf_list=sizedict['des_clkbuf_list']
        divbuf_list=sizedict['des_divbuf_list']

    print(cell_name+" generating")
    mycell_list.append(cell_name)
    laygen.add_cell(cell_name)
    laygen.sel_cell(cell_name)
    generate_deserializer(laygen, objectname_pfix='DES', templib_logic=logictemplib, 
                          placement_grid=pg, routing_grid_m2m3=rg_m2m3, routing_grid_m4m5=rg_m4m5, num_des=num_des,
                          num_flop=num_flop, m_des_dff=m_des_dff, origin=np.array([0, 0]))
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

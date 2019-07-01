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
import os
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
        dev_bottom.append(laygen.relplace("I" + objectname_pfix + 'BNDBTM'+str(i+1), d, pg, dev_bottom[-1].name,
                                          shape=shape_bottom[i+1], transform=transform_bottom[i+1]))
    dev_left=[]
    dev_left.append(laygen.relplace("I" + objectname_pfix + 'BNDLFT0', devname_left[0], pg, dev_bottom[0].name, direction='top',
                                    shape=shape_left[0], transform=transform_left[0]))
    for i, d in enumerate(devname_left[1:]):
        dev_left.append(laygen.relplace("I" + objectname_pfix + 'BNDLFT'+str(i+1), d, pg, dev_left[-1].name, direction='top',
                                        shape=shape_left[i+1], transform=transform_left[i+1]))
    dev_right=[]
    dev_right.append(laygen.relplace("I" + objectname_pfix + 'BNDRHT0', devname_right[0], pg, dev_bottom[-1].name, direction='top',
                                     shape=shape_right[0], transform=transform_right[0]))
    for i, d in enumerate(devname_right[1:]):
        dev_right.append(laygen.relplace("I" + objectname_pfix + 'BNDRHT'+str(i+1), d, pg, dev_right[-1].name, direction='top',
                                         shape=shape_right[i+1], transform=transform_right[i+1]))
    dev_top=[]
    dev_top.append(laygen.relplace("I" + objectname_pfix + 'BNDTOP0', devname_top[0], pg, dev_left[-1].name, direction='top',
                                   shape=shape_top[0], transform=transform_top[0]))
    for i, d in enumerate(devname_top[1:]):
        dev_top.append(laygen.relplace("I" + objectname_pfix + 'BNDTOP'+str(i+1), d, pg, dev_top[-1].name,
                                       shape=shape_top[i+1], transform=transform_top[i+1]))
    dev_right=[]
    return [dev_bottom, dev_top, dev_left, dev_right]

def generate_tap(laygen, objectname_pfix, placement_grid, routing_grid_m1m2_thick, devname_tap_boundary, devname_tap_body,
                 m=1, origin=np.array([0,0]), double_rail=False, transform='R0'):
    """generate a tap primitive"""
    pg = placement_grid
    rg12t = routing_grid_m1m2_thick

    # placement
    taprow = laygen.relplace(name=[None, None, None], 
                             templatename=[devname_tap_boundary, devname_tap_body, devname_tap_boundary],
                             gridname=pg, xy=[origin, [0, 0], [0, 0]], shape=[[1, 1], [m, 1], [1, 1]], 
                             transform=transform)
    itapbl0, itap0, itapbr0 = taprow

    #power route
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12t,
                 refobj0=itap0.elements[0, 0].pins['TAP0'], refobj1=itap0.elements[m-1, 0].pins['TAP1'])
    for i in range(0, m, 1):
        laygen.via(name=None, xy=[0, 0], refobj=itap0.elements[i, 0].pins['TAP1'], gridname=rg12t)
    if double_rail==False: #location of track
        laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12t,
                     refobj0=itap0.elements[0, 0].pins['TAP0'], refobj1=itap0.elements[m - 1, 0].pins['TAP1'])
        for i in range(0, m, 1):
            laygen.via(name=None, xy=[0, 1], refobj=itap0.elements[i, 0].pins['TAP0'], gridname=rg12t)
        if m % 2 == 0:
            laygen.via(name=None, xy=[0, 1], refobj=itap0.elements[m - 1, 0].pins['TAP1'], gridname=rg12t)
    if double_rail==True: #location of track
        laygen.route(name=None, xy0=[0, -1], xy1=[0, -1], gridname0=rg12t,
                     refobj0=itap0.elements[0, 0].pins['TAP0'], refobj1=itap0.elements[m-1, 0].pins['TAP1'])
        for i in range(0, m, 1):
            laygen.route(None, xy0=np.array([0, -1]), xy1=np.array([0, 1]), gridname0=rg12t,
                         refobj0=itap0.elements[i, 0].pins['TAP0'], refobj1=itap0.elements[i, 0].pins['TAP0'])
            laygen.via(None, np.array([0, -1]), refobj=itap0.elements[i, 0].pins['TAP0'], gridname=rg12t)
        if m%2==0:
            laygen.route(None, xy0=np.array([0, -1]), xy1=np.array([0, 1]), gridname0=rg12t,
                         refobj0=itap0.elements[m-1, 0].pins['TAP1'], refobj1=itap0.elements[m-1, 0].pins['TAP1'])
            laygen.via(name=None, xy=[0, -1], refobj=itap0.elements[m-1, 0].pins['TAP1'], gridname=rg12t)
    return [itapbl0, itap0, itapbr0]

def generate_mos(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, devname_mos_boundary, devname_mos_body,
                 devname_mos_dmy, m=1, m_dmy=0, origin=np.array([0,0])):
    """generate a analog mos primitive with dummies"""
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2

    # placement
    if not m_dmy==0:
        imbl0 = laygen.place("I" + objectname_pfix + 'BL0', devname_mos_boundary, pg, xy=origin)
        imdmyl0 = laygen.relplace("I" + objectname_pfix + 'DMYL0', devname_mos_dmy, pg, imbl0.name, shape=np.array([m_dmy, 1]))
        im0 = laygen.relplace("I" + objectname_pfix + '0', devname_mos_body, pg, imdmyl0.name, shape=np.array([m, 1]))
        imdmyr0 = laygen.relplace("I" + objectname_pfix + 'DMYR0', devname_mos_dmy, pg, im0.name, shape=np.array([m_dmy, 1]))
        imbr0 = laygen.relplace("I" + objectname_pfix + 'BR0', devname_mos_boundary, pg, imdmyr0.name)
    else:
        imbl0 = laygen.place("I" + objectname_pfix + 'BL0', devname_mos_boundary, pg, xy=origin)
        imdmyl0 = None
        im0 = laygen.relplace("I" + objectname_pfix + '0', devname_mos_body, pg, imbl0.name, shape=np.array([m, 1]))
        imdmyr0 = None
        imbr0 = laygen.relplace("I" + objectname_pfix + 'BR0', devname_mos_boundary, pg, im0.name)
    #route
    #gate
    rg0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=im0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                      refinstname1=im0.name, refpinname1='G0', refinstindex1=np.array([m-1, 0])
                      )
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=im0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #drain
    rdl0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                      refinstname0=im0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                      refinstname1=im0.name, refpinname1='D0', refinstindex1=np.array([m-1, 0])
                      )
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=im0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #source
    rs0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=im0.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                      refinstname1=im0.name, refpinname1='S1', refinstindex1=np.array([m-1, 0])
                      )
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=im0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=im0.name, refpinname='S1', refinstindex=np.array([m - 1, 0]), gridname=rg_m1m2)
    #dmy
    if m_dmy>=2:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                      refinstname0=imdmyl0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                      refinstname1=imdmyl0.name, refpinname1='D0', refinstindex1=np.array([m_dmy-1, 0])
                      )
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                      refinstname0=imdmyr0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                      refinstname1=imdmyr0.name, refpinname1='D0', refinstindex1=np.array([m_dmy-1, 0])
                      )
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imdmyl0.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                      refinstname1=imdmyl0.name, refpinname1='S0', refinstindex1=np.array([m_dmy-1, 0])
                      )
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imdmyr0.name, refpinname0='S1', refinstindex0=np.array([0, 0]),
                      refinstname1=imdmyr0.name, refpinname1='S1', refinstindex1=np.array([m_dmy-1, 0])
                      )
        for i in range(m_dmy):
            laygen.via(None, np.array([0, 1]), refinstname=imdmyl0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
            laygen.via(None, np.array([0, 1]), refinstname=imdmyr0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
            laygen.via(None, np.array([0, 0]), refinstname=imdmyl0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
            laygen.via(None, np.array([0, 0]), refinstname=imdmyr0.name, refpinname='S1', refinstindex=np.array([i, 0]), gridname=rg_m1m2)

    return [imbl0, imdmyl0, im0, imdmyr0, imbr0]

def generate_mos_mirror_ofst(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, devname_mos_boundary, devname_mos_body,
                             devname_mos_dmy, devname_tap_boundary, devname_tap_body,
                             devname_mos_space_4x, devname_mos_space_2x, devname_mos_space_1x,
                             devname_tap_space_4x, devname_tap_space_2x, devname_tap_space_1x,
                             m_mir=2, m_bias=2, m_in=2, m_ofst=2, m_bias_dum=2, m_in_dum=2, origin=np.array([0,0])):
    """generate an analog differential mos structure with dummmies """
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    # placement
    # generate boundary
    x0=laygen.get_template_size('sar', gridname=pg, libname=workinglib)[0]
    x1=laygen.get_template_size('boundary_bottomleft', gridname=pg, libname=utemplib)[0]
    m_bnd=int((x0-x1*2)/laygen.get_template_size('boundary_bottom', gridname=pg, libname=utemplib)[0])
    [bnd_bottom, bnd_top, bnd_left, bnd_right]=generate_boundary(laygen, objectname_pfix='BND0',
        placement_grid=pg,
        devname_bottom = ['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
        shape_bottom = [np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
        devname_top = ['boundary_topleft', 'boundary_top', 'boundary_topright'],
        shape_top = [np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
        devname_left = ['ptap_fast_left', 'nmos4_fast_left', 'nmos4_fast_left', 'ptap_fast_left'],
        transform_left=['MX', 'R0', 'MX', 'R0'],
        devname_right=['ptap_fast_right', 'nmos4_fast_right', 'nmos4_fast_right','ptap_fast_right'],
        transform_right = ['MX', 'R0', 'MX', 'R0'],
        origin=np.array([0, 0]))

    # generate the first tap row
    tap_origin = laygen.get_inst_xy(bnd_left[0].name, pg) + laygen.get_template_size('ptap_fast_left', pg)[0]*np.array([1,0])
    m_tap = max((m_bias_dum*5+m_ofst+int(m_mir/2)*2+m_bias), (m_in_dum*2+m_in))
    [itapbl0, itap0, itapbr0] = generate_tap(laygen, objectname_pfix=objectname_pfix+'PTAP0', placement_grid=pg,
                                             routing_grid_m1m2_thick=rg_m1m2_thick,
                                             devname_tap_boundary=devname_tap_boundary, devname_tap_body=devname_tap_body,
                                             m=m_tap, double_rail=False, origin=tap_origin, transform='MX')

    # generate the second current mirror & bias devices row
    if m_bias_dum * 5 + m_ofst + int(m_mir / 2) * 2 + m_bias > m_in_dum * 2 + m_in:
        m_bias_dum_r = m_bias_dum
    else:
        m_bias_dum_r = (m_in_dum*2+m_in) - (m_bias_dum*4+m_ofst+int(m_mir/2)*2+m_bias)
    imbl0 = laygen.relplace("I" + objectname_pfix + 'BL0', devname_mos_boundary, pg, itapbl0.name, direction='top')
    imdmyl0 = laygen.relplace("I" + objectname_pfix + 'DMYL0', devname_mos_dmy, pg, imbl0.name, shape=np.array([m_bias_dum, 1]))
    imofst0 = laygen.relplace("I" + objectname_pfix + 'OFST0', devname_mos_body, pg, imdmyl0.name, shape=np.array([m_ofst, 1]))
    imdmyl1 = laygen.relplace("I" + objectname_pfix + 'DMYL1', devname_mos_dmy, pg, imofst0.name, shape=np.array([m_bias_dum, 1]))
    immirl = laygen.relplace("I" + objectname_pfix + 'MIRL0', devname_mos_body, pg, imdmyl1.name, shape=np.array([int(m_mir/2), 1]))
    imdmyl2 = laygen.relplace("I" + objectname_pfix + 'DMYL2', devname_mos_dmy, pg, immirl.name, shape=np.array([m_bias_dum, 1]))
    imbias0 = laygen.relplace("I" + objectname_pfix + 'BIAS0', devname_mos_body, pg, imdmyl2.name, shape=np.array([m_bias, 1]))
    imdmyr0 = laygen.relplace("I" + objectname_pfix + 'DMYR0', devname_mos_dmy, pg, imbias0.name, shape=np.array([m_bias_dum, 1]), transform='MY')
    immirr = laygen.relplace("I" + objectname_pfix + 'MIRR0', devname_mos_body, pg, imdmyr0.name, shape=np.array([int(m_mir/2), 1]), transform='MY')
    imdmyr1 = laygen.relplace("I" + objectname_pfix + 'DMYR1', devname_mos_dmy, pg, immirr.name, shape=np.array([m_bias_dum_r, 1]), transform='MY')
    imbr0 = laygen.relplace("I" + objectname_pfix + 'BR0', devname_mos_boundary, pg, imdmyr1.name, transform='MY')

    # generate the third input device row
    if m_bias_dum * 5 + m_ofst + int(m_mir / 2) * 2 + m_bias < m_in_dum * 2 + m_in:
        m_in_dum_r = m_in_dum
    else:
        m_in_dum_r = (m_bias_dum * 5 + m_ofst + int(m_mir / 2) * 2 + m_bias) - (m_in_dum * 1 + m_in)
    imbl_in0 = laygen.relplace("I" + objectname_pfix + 'BLin0', devname_mos_boundary, pg, imbl0.name, direction='top', transform='MX')
    imdmyl_in0 = laygen.relplace("I" + objectname_pfix + 'DMYLin0', devname_mos_body, pg, imbl_in0.name, shape=np.array([m_in_dum, 1]), transform='MX')
    imin0 = laygen.relplace("I" + objectname_pfix + 'IN0', devname_mos_body, pg, imdmyl_in0.name, shape=np.array([m_in, 1]), transform='MX')
    imdmyr_in0 = laygen.relplace("I" + objectname_pfix + 'DMYRin0', devname_mos_body, pg, imin0.name, shape=np.array([m_in_dum_r, 1]), transform='R180')
    imbr_in0 = laygen.relplace("I" + objectname_pfix + 'BRin0', devname_mos_boundary, pg, imdmyr_in0.name, transform='R180')

    # generate the fourth tap row
    tap_origin = laygen.get_inst_xy(bnd_left[3].name, pg) + laygen.get_template_size('ptap_fast_left', pg)[0]*np.array([1,0])
    m_tap = max((m_bias_dum * 5 + m_ofst + int(m_mir / 2) * 2 + m_bias), (m_in_dum * 2 + m_in))
    [itapbl1, itap1, itapbr1] = generate_tap(laygen, objectname_pfix=objectname_pfix+'PTAP0', placement_grid=pg,
                                             routing_grid_m1m2_thick=rg_m1m2_thick,
                                             devname_tap_boundary=devname_tap_boundary, devname_tap_body=devname_tap_body,
                                             m=m_tap, double_rail=False, origin=tap_origin)
    # generate space
    x_sp4 = laygen.get_template_size('nmos4_fast_space_nf4', gridname=pg, libname=utemplib)
    x_sp2 = laygen.get_template_size('nmos4_fast_space_nf2', gridname=pg, libname=utemplib)
    x_sp1 = laygen.get_template_size('nmos4_fast_space', gridname=pg, libname=utemplib)[0]
    x_sp = x0 - x1 - laygen.get_inst_bbox(itapbr0.name, gridname=pg)[1][0]
    m_sp4x = int(x_sp/x_sp1/4)
    m_sp1x = int(x_sp/x_sp1) - 4*int(x_sp/x_sp1/4)
    isp0_4x = laygen.relplace("I" + objectname_pfix + 'sp0_4x', devname_tap_space_4x, pg, itapbr0.name, shape=[m_sp4x,1], transform='MX')
    isp0_1x = laygen.relplace("I" + objectname_pfix + 'sp0_1x', devname_tap_space_1x, pg, isp0_4x.name, shape=[m_sp1x,1], transform='MX')
    isp1_4x = laygen.relplace("I" + objectname_pfix + 'sp1_4x', devname_mos_space_4x, pg, imbr0.name,
                              shape=[m_sp4x, 1])
    isp1_1x = laygen.relplace("I" + objectname_pfix + 'sp1_1x', devname_mos_space_1x, pg, isp1_4x.name,
                              shape=[m_sp1x, 1])
    isp2_4x = laygen.relplace("I" + objectname_pfix + 'sp2_4x', devname_mos_space_4x, pg, imbr_in0.name,
                              shape=[m_sp4x, 1], transform='MX')
    isp2_1x = laygen.relplace("I" + objectname_pfix + 'sp2_1x', devname_mos_space_1x, pg, isp2_4x.name,
                              shape=[m_sp1x, 1], transform='MX')
    isp3_4x = laygen.relplace("I" + objectname_pfix + 'sp3_4x', devname_tap_space_4x, pg, itapbr1.name, shape=[m_sp4x,1])
    isp3_1x = laygen.relplace("I" + objectname_pfix + 'sp3_1x', devname_tap_space_1x, pg, isp3_4x.name, shape=[m_sp1x,1])

    # route
    # VBIAS
    for i in range(m_bias-1):
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imbias0.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=imbias0.name, refpinname1='G0', refinstindex1=np.array([i+1, 0]),
                     via0=[0,0], via1=[0,0])
        rvb = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([1, 0]), xy1=np.array([1, -6]), gridname0=rg_m2m3,
                     refinstname0=imbias0.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=imbias0.name, refpinname1='G0', refinstindex1=np.array([i, 0]), via0=[0,0])
        laygen.boundary_pin_from_rect(rvb, rg_m2m3, 'VBIAS'+str(i), laygen.layers['pin'][3], size=4, direction='bottom', netname='VBIAS')

    if int(m_mir/2)-1>0:
        for i in range(int(m_mir/2)-1):
            laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=immirl.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=immirl.name, refpinname1='G0', refinstindex1=np.array([i+1, 0]),
                     via0=[0,0], via1=[0,0])
            laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=immirr.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=immirr.name, refpinname1='G0', refinstindex1=np.array([i + 1, 0]),
                     via0=[0, 0], via1=[0, 0])
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=immirl.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=immirl.name, refpinname1='G0', refinstindex1=np.array([1, 0]),
                     via0=[0, 0])
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=immirr.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=immirr.name, refpinname1='G0', refinstindex1=np.array([1, 0]),
                     via0=[0, 0])

    for i in range(int(m_mir / 2)): #diode connected
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=immirl.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=immirl.name, refpinname1='D0', refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=immirr.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=immirr.name, refpinname1='D0', refinstindex1=np.array([i, 0]))

    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=imbias0.name, refpinname0='G0', refinstindex0=np.array([m_bias-1, 0]),
                 refinstname1=immirr.name, refpinname1='G0', refinstindex1=np.array([0, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=immirl.name, refpinname0='G0', refinstindex0=np.array([int(m_mir/2)-1, 0]),
                 refinstname1=imbias0.name, refpinname1='G0', refinstindex1=np.array([0, 0]))

    # IBIAS/IMIR VSS connection
    for i in range(m_tap):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -3]), gridname0=rg_m1m2,
                     refinstname0=itap0.name, refpinname0='TAP0', refinstindex0=np.array([i, 0]),
                     refinstname1=itap0.name, refpinname1='TAP0', refinstindex1=np.array([i, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -3]), gridname0=rg_m1m2,
                 refinstname0=itap0.name, refpinname0='TAP2', refinstindex0=np.array([m_tap-1, 0]),
                 refinstname1=itap0.name, refpinname1='TAP2', refinstindex1=np.array([m_tap-1, 0]))
    # IBIAS/IMIR Dummy VSS connection
    idmy_list = [imdmyl0, imdmyl1, imdmyl2, imdmyr0]
    for i in range(len(idmy_list)):
        for j in range(m_bias_dum):
            laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -3]), gridname0=rg_m1m2,
                         refinstname0=idmy_list[i].name, refpinname0='D0', refinstindex0=np.array([j, 0]),
                         refinstname1=idmy_list[i].name, refpinname1='D0', refinstindex1=np.array([j, 0]))
    for i in range(m_bias_dum_r):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -3]), gridname0=rg_m1m2,
                     refinstname0=imdmyr1.name, refpinname0='D0', refinstindex0=np.array([i, 0]),
                     refinstname1=imdmyr1.name, refpinname1='D0', refinstindex1=np.array([i, 0]))
    # Output
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                 refinstname0=imdmyl_in0.name, refpinname0='S0', refinstindex0=np.array([m_in_dum - 1, 0]),
                 refinstname1=imdmyr_in0.name, refpinname1='S0', refinstindex1=np.array([0, 0]))
    for i in range(m_in):
        laygen.via(None, np.array([0, 1]), rg_m1m2, refinstname=imin0.name, refpinname='D0',refinstindex=np.array([i, 0]))
        ro_v0, ro_h0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]),
                        gridname0=rg_m2m3, refinstname0=imin0.name, refpinname0='D0', refinstindex0=np.array([i, 0]),
                        refinstname1 = imbias0.name, refpinname1 = 'D0', refinstindex1 = np.array([0, 0]), via0=[0,0])
        laygen.boundary_pin_from_rect(ro_v0, rg_m2m3, 'out'+str(i), laygen.layers['pin'][3], size=4, direction='top', netname='out')

    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                 refinstname0=imdmyl0.name, refpinname0='S0', refinstindex0=np.array([m_bias_dum - 1, 0]),
                 refinstname1=imdmyr1.name, refpinname1='S0', refinstindex1=np.array([0, 0]))
    for i in range(m_bias):
        laygen.via(None, np.array([0, 1]), rg_m1m2, refinstname=imbias0.name, refpinname='D0',refinstindex=np.array([i, 0]))
        ro_v0, ro_h0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], xy0=np.array([0, 1]),
                                   xy1=np.array([0, 1]), gridname0=rg_m2m3, refinstname0=imbias0.name, refpinname0='D0',
                                   refinstindex0=np.array([i, 0]), refinstname1=imin0.name, refpinname1='D0',
                                   refinstindex1=np.array([0, 0]), via0=[0, 0])
        laygen.boundary_pin_from_rect(ro_v0, rg_m2m3, 'out' + str(m_in+i), laygen.layers['pin'][3], size=4, direction='top',
                                  netname='out')
    for i in range(m_ofst):
        laygen.via(None, np.array([0, 1]), rg_m1m2, refinstname=imofst0.name, refpinname='D0',refinstindex=np.array([i, 0]))

    # Input
    for i in range(m_in-1):
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imin0.name, refpinname0='G0', refinstindex0=np.array([i, 0]), via0=[0,0],
                     refinstname1=imin0.name, refpinname1='G0', refinstindex1=np.array([i+1, 0]), via1=[0,0])
    rin = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([1, 0]), xy1=np.array([1, -6]), gridname0=rg_m2m3,
                 refinstname0=imin0.name, refpinname0='G0', refinstindex0=np.array([0, 0]), via0=[0, 0],
                 refinstname1=imin0.name, refpinname1='G0', refinstindex1=np.array([0, 0]))
    laygen.boundary_pin_from_rect(rin, rg_m2m3, 'in', laygen.layers['pin'][3], size=4, direction='top')

    # Input dummy
    for i in range(m_in_dum-1):
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imdmyl_in0.name, refpinname0='G0', refinstindex0=np.array([i, 0]), via0=[0,0],
                     refinstname1=imdmyl_in0.name, refpinname1='G0', refinstindex1=np.array([i+1, 0]), via1=[0,0])
    for i in range(m_in_dum):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imdmyl_in0.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=imdmyl_in0.name, refpinname1='D0', refinstindex1=np.array([i, 0]))
    laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], xy0=np.array([0, 0]),
                   xy1=np.array([0, 0]), gridname0=rg_m2m3, gridname1=rg_m2m3_thick,
                    refinstname0=imdmyl_in0.name, refpinname0='G0',
                   refinstindex0=np.array([0, 0]), refinstname1=itap1.name, refpinname1='TAP0',
                   refinstindex1=np.array([0, 0]), via0=[0, 0]) #gate to VSS
    for i in range(m_in_dum_r-1):
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imdmyr_in0.name, refpinname0='G0', refinstindex0=np.array([i, 0]), via0=[0,0],
                     refinstname1=imdmyr_in0.name, refpinname1='G0', refinstindex1=np.array([i+1, 0]), via1=[0,0])
    for i in range(m_in_dum_r):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imdmyr_in0.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=imdmyr_in0.name, refpinname1='D0', refinstindex1=np.array([i, 0]))
    laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], xy0=np.array([0, 0]),
                   xy1=np.array([0, 0]), gridname0=rg_m2m3, gridname1=rg_m2m3_thick,
                    refinstname0=imdmyr_in0.name, refpinname0='G0',
                   refinstindex0=np.array([1, 0]), refinstname1=itap1.name, refpinname1='TAP0',
                   refinstindex1=np.array([0, 0]), via0=[0, 0]) #gate to VSS

    # Voff
    for i in range(m_ofst):
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imofst0.name, refpinname0='G0', refinstindex0=np.array([i, 0]), via0=[0,0],
                     refinstname1=imofst0.name, refpinname1='G0', refinstindex1=np.array([i+1, 0]))
    roff = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([1, 0]), xy1=np.array([1, -6]), gridname0=rg_m2m3,
                 refinstname0=imofst0.name, refpinname0='G0', refinstindex0=np.array([0, 0]), via0=[0, 0],
                 refinstname1=imofst0.name, refpinname1='G0', refinstindex1=np.array([0, 0]))
    laygen.boundary_pin_from_rect(roff, rg_m2m3, 'Voff', laygen.layers['pin'][3], size=4, direction='bottom')


    # Input device VDD connection
    for i in range(m_in):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imin0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imin0.name, refpinname1='S0', refinstindex1=np.array([i, 0]), via1=[0,0])
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imin0.name, refpinname0='S1', refinstindex0=np.array([i, 0]),
                     refinstname1=imin0.name, refpinname1='S1', refinstindex1=np.array([i, 0]), via1=[0,0])
    # Input dummy L VDD connection
    for i in range(m_in_dum):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imdmyl_in0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imdmyl_in0.name, refpinname1='S0', refinstindex1=np.array([i, 0]), via1=[0, 0])
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]),
                     gridname0=rg_m1m2,
                     refinstname0=imdmyl_in0.name, refpinname0='S1', refinstindex0=np.array([i, 0]),
                     refinstname1=imdmyl_in0.name, refpinname1='S1', refinstindex1=np.array([i, 0]), via1=[0, 0])
    # Input dummy L VDD connection
    for i in range(m_in_dum_r):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imdmyr_in0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imdmyr_in0.name, refpinname1='S0', refinstindex1=np.array([i, 0]), via1=[0, 0])
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imdmyr_in0.name, refpinname0='S1', refinstindex0=np.array([i, 0]),
                     refinstname1=imdmyr_in0.name, refpinname1='S1', refinstindex1=np.array([i, 0]), via1=[0, 0])

    # VSS/VDD
    num_vert_pwr_l = 3
    num_vert_pwr_r = 1 + m_sp4x*2
    # M2 VSS rails
    rvss0 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr_l, 0]), xy1=np.array([2*num_vert_pwr_r, 0]), gridname0=rg_m2m3_thick,
                        refinstname0=itap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=itap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0]))
    rvss0_0 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr_l, 1]), xy1=np.array([2*num_vert_pwr_r, 1]), gridname0=rg_m2m3_thick,
                        refinstname0=itap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=itap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0]))
    rvss1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr_l, 0]), xy1=np.array([2*num_vert_pwr_r, 0]), gridname0=rg_m2m3_thick,
                        refinstname0=itap1.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=itap1.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0]))
    rvss1_0 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr_l, 1]), xy1=np.array([2*num_vert_pwr_r, 1]), gridname0=rg_m2m3_thick,
                        refinstname0=itap1.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=itap1.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0]))
    # M2 VDD rail
    rvdd = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr_l, -1]), xy1=np.array([-2*num_vert_pwr_r, -1]), gridname0=rg_m2m3,
                 refinstname0=imdmyl_in0.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=imdmyr_in0.name, refpinname1='S0', refinstindex1=np.array([0, 0]))
    #
    # rvss0_pin_xy = laygen.get_rect_xy(rvss0.name, rg_m1m2_thick)
    # rvss0_0_pin_xy = laygen.get_rect_xy(rvss0_0.name, rg_m1m2_thick)
    # rvss1_pin_xy = laygen.get_rect_xy(rvss1.name, rg_m1m2_thick)
    # rvss1_0_pin_xy = laygen.get_rect_xy(rvss1_0.name, rg_m1m2_thick)
    # rvdd_pin_xy = laygen.get_rect_xy(rvdd.name, rg_m2m3)
    #
    # laygen.pin(name='VSS0', layer=laygen.layers['pin'][2], xy=rvss0_pin_xy, gridname=rg_m1m2_thick, netname='VSS:')
    # laygen.pin(name='VSS0_0', layer=laygen.layers['pin'][2], xy=rvss0_0_pin_xy, gridname=rg_m1m2_thick, netname='VSS:')
    # laygen.pin(name='VSS1', layer=laygen.layers['pin'][2], xy=rvss1_pin_xy, gridname=rg_m1m2_thick, netname='VSS:')
    # laygen.pin(name='VSS1_0', layer=laygen.layers['pin'][2], xy=rvss1_0_pin_xy, gridname=rg_m1m2_thick, netname='VSS:')
    # laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m2m3, netname='VDD')

    # M3 VDD/VSS vertical
    for i in range(num_vert_pwr_l):
        rvvss_l = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2*i-1, 1]), xy1=np.array([-2*i-1, 1]), gridname0=rg_m2m3_thick,
                               refinstname0=itap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                               refinstname1=itap1.name, refpinname1='TAP0', refinstindex1=np.array([0, 0]))
        rvvdd_l = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2*i-2, 1]), xy1=np.array([-2*i-2, 1]), gridname0=rg_m2m3_thick,
                               refinstname0=itap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                               refinstname1=itap1.name, refpinname1='TAP0', refinstindex1=np.array([0, 0]))
        laygen.via(None, np.array([-2*i-1, 1]), refinstname=itap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2*i-1, 0]), refinstname=itap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2 * i - 1, 1]), refinstname=itap1.name, refpinname='TAP0',
                   refinstindex=np.array([0, 0]), gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2*i-1, 0]), refinstname=itap1.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2*i-2, -1]), refinstname=imdmyl_in0.name, refpinname='S0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3)
        laygen.pin(name='VSS'+str(i), layer=laygen.layers['pin'][3], xy=laygen.get_rect_xy(rvvss_l.name, rg_m2m3_thick),
                   gridname=rg_m2m3_thick, netname='VSS')
        laygen.pin(name='VDD'+str(i), layer=laygen.layers['pin'][3], xy=laygen.get_rect_xy(rvvdd_l.name, rg_m2m3_thick),
                   gridname=rg_m2m3_thick, netname='VDD')
    for i in range(num_vert_pwr_r):
        rvvss_r = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2 * i + 1, 1]),
                               xy1=np.array([2 * i + 1, 1]), gridname0=rg_m2m3_thick,
                               refinstname0=itap0.name, refpinname0='TAP2', refinstindex0=np.array([m_tap-1, 0]),
                               refinstname1=itap1.name, refpinname1='TAP2', refinstindex1=np.array([m_tap-1, 0]))
        rvvdd_r = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2 * i + 2, 1]),
                               xy1=np.array([2 * i + 2, 1]), gridname0=rg_m2m3_thick,
                               refinstname0=itap0.name, refpinname0='TAP2', refinstindex0=np.array([m_tap-1, 0]),
                               refinstname1=itap1.name, refpinname1='TAP2', refinstindex1=np.array([m_tap-1, 0]))
        laygen.via(None, np.array([2 * i + 1, 1]), refinstname=itap0.name, refpinname='TAP2',
                   refinstindex=np.array([m_tap-1, 0]), gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2 * i + 1, 0]), refinstname=itap0.name, refpinname='TAP2',
                   refinstindex=np.array([m_tap-1, 0]), gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2 * i + 1, 1]), refinstname=itap1.name, refpinname='TAP2',
                   refinstindex=np.array([m_tap-1, 0]), gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2 * i + 1, 0]), refinstname=itap1.name, refpinname='TAP2',
                   refinstindex=np.array([m_tap-1, 0]), gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2 * i - 2, -1]), refinstname=imdmyr_in0.name, refpinname='S0',
                   refinstindex=np.array([0, 0]), gridname=rg_m2m3)
        laygen.pin(name='VSS' + str(num_vert_pwr_l+i), layer=laygen.layers['pin'][3], xy=laygen.get_rect_xy(rvvss_r.name, rg_m2m3_thick),
                   gridname=rg_m2m3_thick, netname='VSS')
        laygen.pin(name='VDD' + str(num_vert_pwr_l+i), layer=laygen.layers['pin'][3], xy=laygen.get_rect_xy(rvvdd_r.name, rg_m2m3_thick),
                   gridname=rg_m2m3_thick, netname='VDD')
        # rvvss_r = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, -1]), xy1=np.array([2*i+1, -1]), gridname0=rg_m2m3_thick,
        #                        refinstname0=imaintap0.name, refpinname0='TAP1', refinstindex0=np.array([m_tap-1, 0]),
        #                        refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
        #                        )
        # laygen.via(None, np.array([-2*i-via_offset, 0]), refinstname=irgntap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
        #                gridname=rg_m2m3_thick)
        # laygen.via(None, np.array([2*i+via_offset, 0]), refinstname=irgntap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
        #                gridname=rg_m2m3_thick)
        # laygen.via(None, np.array([-2*i-via_offset, -1]), refinstname=irgntap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
        #                gridname=rg_m2m3_thick)
        # laygen.via(None, np.array([2*i+via_offset, -1]), refinstname=irgntap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
        #                gridname=rg_m2m3_thick)
        # laygen.pin(name='VSSL'+str(i), layer=laygen.layers['pin'][3],
        #            xy=laygen.get_rect_xy(rvvss_l.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VSS')
        # laygen.pin(name='VSSR'+str(i), layer=laygen.layers['pin'][3],
        #            xy=laygen.get_rect_xy(rvvss_r.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VSS')
        #
        #
        # rvvdd_r = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, -1]), xy1=np.array([2*i+2, -1]), gridname0=rg_m2m3_thick,
        #                        refinstname0=imaintap0.name, refpinname0='TAP1', refinstindex0=np.array([m_tap-1, 0]),
        #                        refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
        #                )
        # laygen.via(None, np.array([-2*i-1, 1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
        #                gridname=rg_m2m3_thick)
        # laygen.via(None, np.array([2*i+1, 1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
        #                gridname=rg_m2m3_thick)
        # laygen.via(None, np.array([-2*i-1, 1]), refinstname=irgntapn0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
        #                gridname=rg_m2m3_thick)
        # laygen.via(None, np.array([2*i+1, 1]), refinstname=irgntapn0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
        #                gridname=rg_m2m3_thick)
        # laygen.via(None, np.array([-2*i-1, -1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
        #                gridname=rg_m2m3_thick)
        # laygen.via(None, np.array([2*i+1, -1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
        #                gridname=rg_m2m3_thick)
        # #laygen.via(None, np.array([-2*i-2, 0]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 1]),
        # #               gridname=rg_m2m3)
        # #laygen.via(None, np.array([2*i+2, 0]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 1]),
        # #               gridname=rg_m2m3)
        # laygen.via(None, np.array([-2*i-2, -1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 5]),
        #                gridname=rg_m2m3)
        # laygen.via(None, np.array([2*i+2, -1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 5]),
        #                gridname=rg_m2m3)
        #
        # laygen.pin(name='VDDL'+str(i), layer=laygen.layers['pin'][3],
        #            xy=laygen.get_rect_xy(rvvdd_l.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VDD')
        # laygen.pin(name='VDDR'+str(i), layer=laygen.layers['pin'][3],
        #            xy=laygen.get_rect_xy(rvvdd_r.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VDD')

#
#     #VDD/VSS
#     #num_vert_pwr = 20
#     if pmos_body == 'VSS':
#         rvss1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 1]), xy1=np.array([2*num_vert_pwr, 1]), gridname0=rg_m1m2_thick,
#                             refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
#                             refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
#                            )
#         rvss1b = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, -1]), xy1=np.array([2*num_vert_pwr, -1]), gridname0=rg_m1m2_thick,
#                             refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
#                             refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
#                            )
#         rvss2 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 1]), xy1=np.array([2*num_vert_pwr, 1]), gridname0=rg_m1m2_thick,
#                             refinstname0=irgntapn0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
#                             refinstname1=irgntapn0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
#                            )
#         rvss = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 0]), xy1=np.array([2*num_vert_pwr, 0]), gridname0=rg_m1m2_thick,
#                             refinstname0=irgntap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
#                             refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
#                            )
#         rvssb = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, -1]), xy1=np.array([2*num_vert_pwr, -1]), gridname0=rg_m1m2_thick,
#                             refinstname0=irgntap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
#                             refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
#                            )
#         rvdd1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, -1]), xy1=np.array([2*num_vert_pwr, -1]), gridname0=rg_m1m2,
#                             refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 5]),
#                             refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 5])
#                            )
#         rvss1_pin_xy = laygen.get_rect_xy(rvss1.name, rg_m1m2_thick)
#         rvss2_pin_xy = laygen.get_rect_xy(rvss2.name, rg_m1m2_thick)
#         rvss_pin_xy = laygen.get_rect_xy(rvss.name, rg_m1m2_thick)
#
#         laygen.pin(name='VSS2', layer=laygen.layers['pin'][2], xy=rvss1_pin_xy, gridname=rg_m1m2_thick, netname='VSS')
#         laygen.pin(name='VSS1', layer=laygen.layers['pin'][2], xy=rvss2_pin_xy, gridname=rg_m1m2_thick, netname='VSS')
#         laygen.pin(name='VSS0', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2_thick, netname='VSS')
#
#         via_offset = 1
#
#     elif pmos_body == 'VDD':
#         rvss1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2 * num_vert_pwr, 1]),
#                              xy1=np.array([2 * num_vert_pwr, 1]), gridname0=rg_m1m2_thick,
#                              refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
#                              refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap - 1, 0])
#                              )
#         rvss1b = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2 * num_vert_pwr, -1]),
#                               xy1=np.array([2 * num_vert_pwr, -1]), gridname0=rg_m1m2_thick,
#                               refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
#                               refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap - 1, 0])
#                               )
#         rvss2 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2 * num_vert_pwr, 1]),
#                              xy1=np.array([2 * num_vert_pwr, 1]), gridname0=rg_m1m2_thick,
#                              refinstname0=irgntapn0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
#                              refinstname1=irgntapn0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap - 1, 0])
#                              )
#         rvdd = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2 * num_vert_pwr, 0]),
#                             xy1=np.array([2 * num_vert_pwr, 0]), gridname0=rg_m1m2_thick,
#                             refinstname0=irgntap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
#                             refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap - 1, 0])
#                             )
#         rvssb = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2 * num_vert_pwr, -1]),
#                              xy1=np.array([2 * num_vert_pwr, -1]), gridname0=rg_m1m2_thick,
#                              refinstname0=irgntap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
#                              refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap - 1, 0])
#                              )
#         '''
#         rvdd0 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 0]), xy1=np.array([2*num_vert_pwr, 0]), gridname0=rg_m1m2,
#                             refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 1]),
#                             refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 1])
#                            )
#         '''
#         rvdd1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2 * num_vert_pwr, -1]),
#                              xy1=np.array([2 * num_vert_pwr, -1]), gridname0=rg_m1m2,
#                              refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 5]),
#                              refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap - 1, 5])
#                              )
#         # rvdd_pin_xy = laygen.get_rect_xy(rvdd.name, rg_m1m2_thick)
#         rvss1_pin_xy = laygen.get_rect_xy(rvss1.name, rg_m1m2_thick)
#         rvss2_pin_xy = laygen.get_rect_xy(rvss2.name, rg_m1m2_thick)
#         rvdd_pin_xy = laygen.get_rect_xy(rvdd.name, rg_m1m2_thick)
#
#         # laygen.pin(name='VDD0', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2_thick, netname='VDD')
#         laygen.pin(name='VSS2', layer=laygen.layers['pin'][2], xy=rvss1_pin_xy, gridname=rg_m1m2_thick, netname='VSS')
#         laygen.pin(name='VSS1', layer=laygen.layers['pin'][2], xy=rvss2_pin_xy, gridname=rg_m1m2_thick, netname='VSS')
#         laygen.pin(name='VDD0', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2_thick, netname='VDD')
#
#         via_offset = 2
#
#     #vdd/vss vertical
#     i=0
#     for i in range(num_vert_pwr):
#         rvvss_l = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2*i-1, -1]), xy1=np.array([-2*i-1, -1]), gridname0=rg_m2m3_thick,
#                                refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
#                                refinstname1=irgntap0.name, refpinname1='TAP0', refinstindex1=np.array([0, 0])
#                                )
#         rvvss_r = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, -1]), xy1=np.array([2*i+1, -1]), gridname0=rg_m2m3_thick,
#                                refinstname0=imaintap0.name, refpinname0='TAP1', refinstindex0=np.array([m_tap-1, 0]),
#                                refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
#                                )
#         laygen.via(None, np.array([-2*i-via_offset, 0]), refinstname=irgntap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
#                        gridname=rg_m2m3_thick)
#         laygen.via(None, np.array([2*i+via_offset, 0]), refinstname=irgntap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
#                        gridname=rg_m2m3_thick)
#         laygen.via(None, np.array([-2*i-via_offset, -1]), refinstname=irgntap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
#                        gridname=rg_m2m3_thick)
#         laygen.via(None, np.array([2*i+via_offset, -1]), refinstname=irgntap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
#                        gridname=rg_m2m3_thick)
#         laygen.pin(name='VSSL'+str(i), layer=laygen.layers['pin'][3],
#                    xy=laygen.get_rect_xy(rvvss_l.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VSS')
#         laygen.pin(name='VSSR'+str(i), layer=laygen.layers['pin'][3],
#                    xy=laygen.get_rect_xy(rvvss_r.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VSS')
#
#         rvvdd_l = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2*i-2, -1]), xy1=np.array([-2*i-2, -1]), gridname0=rg_m2m3_thick,
#                                refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
#                                refinstname1=irgntap0.name, refpinname1='TAP0', refinstindex1=np.array([0, 0])
#                        )
#         rvvdd_r = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, -1]), xy1=np.array([2*i+2, -1]), gridname0=rg_m2m3_thick,
#                                refinstname0=imaintap0.name, refpinname0='TAP1', refinstindex0=np.array([m_tap-1, 0]),
#                                refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
#                        )
#         laygen.via(None, np.array([-2*i-1, 1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
#                        gridname=rg_m2m3_thick)
#         laygen.via(None, np.array([2*i+1, 1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
#                        gridname=rg_m2m3_thick)
#         laygen.via(None, np.array([-2*i-1, 1]), refinstname=irgntapn0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
#                        gridname=rg_m2m3_thick)
#         laygen.via(None, np.array([2*i+1, 1]), refinstname=irgntapn0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
#                        gridname=rg_m2m3_thick)
#         laygen.via(None, np.array([-2*i-1, -1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
#                        gridname=rg_m2m3_thick)
#         laygen.via(None, np.array([2*i+1, -1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
#                        gridname=rg_m2m3_thick)
#         #laygen.via(None, np.array([-2*i-2, 0]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 1]),
#         #               gridname=rg_m2m3)
#         #laygen.via(None, np.array([2*i+2, 0]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 1]),
#         #               gridname=rg_m2m3)
#         laygen.via(None, np.array([-2*i-2, -1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 5]),
#                        gridname=rg_m2m3)
#         laygen.via(None, np.array([2*i+2, -1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 5]),
#                        gridname=rg_m2m3)
#
#         laygen.pin(name='VDDL'+str(i), layer=laygen.layers['pin'][3],
#                    xy=laygen.get_rect_xy(rvvdd_l.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VDD')
#         laygen.pin(name='VDDR'+str(i), layer=laygen.layers['pin'][3],
#                    xy=laygen.get_rect_xy(rvvdd_r.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VDD')
#
# def generate_salatch_pmos_fitdim(laygen, objectname_pfix, placement_grid, routing_grid_m1m2,
#                                  routing_grid_m1m2_thick, routing_grid_m2m3, routing_grid_m2m3_thick, routing_grid_m3m4, routing_grid_m4m5,
#                                  devname_ptap_boundary, devname_ptap_body,
#                                  devname_nmos_boundary, devname_nmos_body, devname_nmos_dmy,
#                                  devname_pmos_boundary, devname_pmos_body, devname_pmos_dmy,
#                                  devname_ntap_boundary, devname_ntap_body,
#                                  m_in=4, m_ofst=2, m_clkh=2, m_rgnn=2, m_rstn=1, m_buf=1,
#                                  m_space_4x=0, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0])):
#     """generate a salatch & fit to CDAC dim"""
#
#     cdac_name = 'capdac'
#     cdrva_name = 'capdrv_array_7b'
#
#     m_tot = max(m_in, m_clkh, m_rgnn + 2*m_rstn + m_buf) + 1  # at least one dummy
#
#     #grids
#     pg = placement_grid
#     rg_m1m2 = routing_grid_m1m2
#     rg_m1m2_thick = routing_grid_m1m2_thick
#     rg_m2m3 = routing_grid_m2m3
#     rg_m2m3_thick = routing_grid_m2m3_thick
#     rg_m3m4 = routing_grid_m3m4
#     rg_m4m5 = routing_grid_m4m5
#
#     #spacing calculation
#     devname_space_1x = ['ptap_fast_space', 'nmos4_fast_space', 'ptap_fast_space',
#                         'nmos4_fast_space', 'pmos4_fast_space', 'ntap_fast_space']
#     devname_space_2x = ['ptap_fast_space_nf2', 'nmos4_fast_space_nf2', 'ptap_fast_space_nf2',
#                         'nmos4_fast_space_nf2', 'pmos4_fast_space_nf2', 'ntap_fast_space_nf2']
#     devname_space_4x = ['ptap_fast_space_nf4', 'nmos4_fast_space_nf4', 'ptap_fast_space_nf4',
#                         'nmos4_fast_space_nf4', 'pmos4_fast_space_nf4', 'ntap_fast_space_nf4']
#     transform_space = ['R0', 'R0', 'R0', 'R0', 'R0', 'MX']
#     m_space=m_space_4x*4+m_space_2x*2+m_space_1x*1
#     #boundary generation
#     m_bnd=m_tot*2*2+m_space*2+2 #2 for diff, 2 for nf, 2 for mos boundary
#     [bnd_bottom, bnd_top, bnd_left, bnd_right]=generate_boundary(laygen, objectname_pfix='BND0',
#         placement_grid=pg,
#         devname_bottom = ['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
#         shape_bottom = [np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
#         devname_top = ['boundary_topleft', 'boundary_top', 'boundary_topright'],
#         shape_top = [np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
#         devname_left = ['ptap_fast_left', 'nmos4_fast_left', 'ptap_fast_left',
#                         'nmos4_fast_left', 'pmos4_fast_left', 'ntap_fast_left'],
#         transform_left=['R0', 'R0', 'R0', 'R0', 'R0', 'MX'],
#         devname_right=['ptap_fast_right', 'nmos4_fast_right', 'ptap_fast_right',
#                        'nmos4_fast_right','pmos4_fast_right', 'ntap_fast_right'],
#         transform_right = ['R0', 'R0', 'R0', 'R0', 'R0', 'MX'],
#         origin=np.array([0, 0]))
#     #space generation
#     spl_origin = laygen.get_inst_xy(bnd_bottom[0].name, pg) + laygen.get_template_size(bnd_bottom[0].cellname, pg)
#     ispl4x=[]
#     ispl2x=[]
#     ispl1x=[]
#     for i, d in enumerate(devname_space_4x):
#         if i==0:
#             if not m_space_1x==0:
#                 ispl1x.append(laygen.place(name="ISA0SPL1X0", templatename=devname_space_1x[i], gridname=pg, shape=np.array([m_space_1x, 1]),
#                                            xy=spl_origin, transform=transform_space[i]))
#                 refi=ispl1x[-1].name
#                 if not m_space_2x==0:
#                     ispl2x.append(laygen.relplace(name="ISA0SPL2X0", templatename=devname_space_2x[i], gridname=pg, refinstname=refi,
#                                               shape=np.array([m_space_2x, 1]),
#                                               transform=transform_space[i]))
#                     refi=ispl2x[-1].name
#             else:
#                 if not m_space_2x==0:
#                     ispl2x.append(laygen.place(name="ISA0SPL2X0", templatename=devname_space_2x[i], gridname=pg, shape=np.array([m_space_2x, 1]),
#                                            xy=spl_origin, transform=transform_space[i]))
#                     refi=ispl2x[-1].name
#                 #ispl2x.append(laygen.relplace(name="ISA0SPL2X0", templatename=devname_space_2x[i], gridname=pg, refinstname=refi,
#                 #                              shape=np.array([m_space_2x, 1]),
#                 #                              transform=transform_space[i]))
#                 #refi=ispl2x[-1].name
#             if m_space_1x==0 and m_space_2x==0:
#                 ispl4x.append(laygen.place(name="ISA0SPL4X0", templatename=d, gridname=pg, xy=spl_origin,
#                                           shape=np.array([m_space_4x, 1]), transform=transform_space[i]))
#                 refi=ispl4x[-1].name
#             else:
#                 ispl4x.append(laygen.relplace(name="ISA0SPL4X0", templatename=d, gridname=pg, refinstname=refi,
#                                           shape=np.array([m_space_4x, 1]), transform=transform_space[i]))
#         else:
#             if not m_space_1x==0:
#                 ispl1x.append(laygen.relplace(name="ISA0SPL1X" + str(i), templatename=devname_space_1x[i], gridname=pg,
#                                               refinstname=ispl1x[-1].name, shape=np.array([m_space_1x, 1]),
#                                               direction='top', transform=transform_space[i]))
#             if not m_space_2x==0:
#                 ispl2x.append(laygen.relplace(name="ISA0SPL2X" + str(i), templatename=devname_space_2x[i], gridname=pg,
#                                               refinstname=ispl2x[-1].name, shape=np.array([m_space_2x, 1]),
#                                               direction='top', transform=transform_space[i]))
#             ispl4x.append(laygen.relplace(name="ISA0SPL4X"+str(i), templatename=d, gridname=pg, refinstname=ispl4x[-1].name,
#                                         shape=np.array([m_space_4x, 1]), direction='top', transform=transform_space[i]))
#     spr_origin = laygen.get_inst_xy(bnd_bottom[-1].name, pg) \
#                  + laygen.get_template_size(bnd_bottom[-1].cellname, pg) * np.array([0, 1]) \
#                  - laygen.get_template_size('nmos4_fast_space', pg) * np.array([m_space, 0])
#     ispr4x=[]
#     ispr2x=[]
#     ispr1x=[]
#     for i, d in enumerate(devname_space_4x):
#         if i==0:
#             ispr4x.append(laygen.place(name="ISA0SPR4X0", templatename=d, gridname=pg, shape=np.array([m_space_4x, 1]),
#                                      xy=spr_origin, transform=transform_space[i]))
#             refi=ispr4x[-1].name
#             if not m_space_2x==0:
#                 ispr2x.append(laygen.relplace(name="ISA0SPR2X0", templatename=devname_space_2x[i], gridname=pg, refinstname=refi,
#                                               shape=np.array([m_space_2x, 1]),
#                                               transform=transform_space[i]))
#                 refi=ispr2x[-1].name
#             if not m_space_1x==0:
#                 ispr1x.append(laygen.relplace(name="ISA0SPR1X0", templatename=devname_space_1x[i], gridname=pg, refinstname=refi,
#                                               shape=np.array([m_space_1x, 1]),
#                                               transform=transform_space[i]))
#         else:
#             ispr4x.append(laygen.relplace(name="ISA0SPR4X"+str(i), templatename=d, gridname=pg, refinstname=ispr4x[-1].name,
#                                         shape=np.array([m_space_4x, 1]), direction='top', transform=transform_space[i]))
#             if not m_space_2x==0:
#                 ispr2x.append(laygen.relplace(name="ISA0SPR2X" + str(i), templatename=devname_space_2x[i], gridname=pg,
#                                               refinstname=ispr2x[-1].name, shape=np.array([m_space_2x, 1]),
#                                               direction='top', transform=transform_space[i]))
#             if not m_space_1x==0:
#                 ispr1x.append(laygen.relplace(name="ISA0SPR1X" + str(i), templatename=devname_space_1x[i], gridname=pg,
#                                               refinstname=ispr1x[-1].name, shape=np.array([m_space_1x, 1]),
#                                               direction='top', transform=transform_space[i]))
#
#     #salatch
#     sa_origin = origin+laygen.get_inst_xy(bnd_bottom[0].name, pg)+laygen.get_template_size(bnd_bottom[0].cellname, pg)\
#                 +laygen.get_template_size('nmos4_fast_space', pg)*m_space*np.array([1, 0])
#
#     #sa_origin=origin
#     generate_salatch_pmos(laygen, objectname_pfix=objectname_pfix,
#                      placement_grid=placement_grid, routing_grid_m1m2=routing_grid_m1m2,
#                      routing_grid_m1m2_thick=routing_grid_m1m2_thick,
#                      routing_grid_m2m3=routing_grid_m2m3, routing_grid_m2m3_thick=routing_grid_m2m3_thick,
#                      routing_grid_m3m4=routing_grid_m3m4, routing_grid_m4m5=routing_grid_m4m5,
#                      devname_ptap_boundary=devname_ptap_boundary, devname_ptap_body=devname_ptap_body,
#                      devname_nmos_boundary=devname_nmos_boundary, devname_nmos_body=devname_nmos_body,
#                      devname_nmos_dmy=devname_nmos_dmy,
#                      devname_pmos_boundary=devname_pmos_boundary, devname_pmos_body=devname_pmos_body,
#                      devname_pmos_dmy=devname_pmos_dmy,
#                      devname_ntap_boundary=devname_ntap_boundary, devname_ntap_body=devname_ntap_body,
#                      m_in=m_in, m_ofst=m_ofst, m_clkh=m_clkh, m_rgnn=m_rgnn, m_rstn=m_rstn, m_buf=m_buf,
#                      num_vert_pwr = m_space_4x * 2, origin=sa_origin)


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
    rg_m1m2_thick = 'route_M1_M2_basic_thick'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m2m3_thick = 'route_M2_M3_thick_basic'
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
    #salatch generation (wboundary)
    #cellname = 'salatch'
    cellname = 'sourceFollower'
    print(cellname+" generating")
    mycell_list.append(cellname)
    m_sa=8
    m_rst_sa=8
    m_rgnn_sa=2
    m_buf_sa=8
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        m_mir=sizedict['sourceFollower']['m_mirror']
        m_bias=sizedict['sourceFollower']['m_bias']
        m_in=sizedict['sourceFollower']['m_in']
        m_ofst=sizedict['sourceFollower']['m_off']
        m_in_dum=sizedict['sourceFollower']['m_in_dum']
        m_bias_dum=sizedict['sourceFollower']['m_bias_dum']

    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)

    sf_origin=np.array([0, 0])

    #salatch body
    # 1. generate without spacing
    generate_mos_mirror_ofst(laygen, objectname_pfix='SF0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                             devname_mos_boundary='nmos4_fast_boundary', devname_mos_body='nmos4_fast_center_nf2',
                             devname_mos_dmy='nmos4_fast_dmy_nf2', devname_tap_boundary='ptap_fast_boundary', devname_tap_body='ptap_fast_center_nf2',
                             devname_mos_space_4x='nmos4_fast_space_nf4', devname_mos_space_2x='nmos4_fast_space_nf2', devname_mos_space_1x='nmos4_fast_space',
                             devname_tap_space_4x='ptap_fast_space_nf4', devname_tap_space_2x='ptap_fast_space_nf2', devname_tap_space_1x='ptap_fast_space',
                             m_mir=m_mir, m_bias=m_bias, m_in=m_in,
                             m_ofst=m_ofst, m_bias_dum=m_bias_dum, m_in_dum=m_in_dum,
                             origin=sf_origin)
    # generate_mos_mirror_ofst(laygen, objectname_pfix='SA0',
    #                             placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick,
    #                             routing_grid_m2m3=rg_m2m3, routing_grid_m2m3_thick=rg_m2m3_thick, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5,
    #                             devname_ptap_boundary='ptap_fast_boundary', devname_ptap_body='ptap_fast_center_nf1',
    #                             devname_nmos_boundary='nmos4_fast_boundary', devname_nmos_body='nmos4_fast_center_nf2',
    #                             devname_nmos_dmy='nmos4_fast_dmy_nf2',
    #                             devname_pmos_boundary='pmos4_fast_boundary', devname_pmos_body='pmos4_fast_center_nf2',
    #                             devname_pmos_dmy='pmos4_fast_dmy_nf2',
    #                             devname_ntap_boundary='ntap_fast_boundary', devname_ntap_body='ntap_fast_center_nf1',
    #                             m_in=m_in, m_ofst=m_ofst, m_clkh=m_clkh, m_rgnn=m_rgnn, m_rstn=m_rstn, m_buf=m_buf,
    #                             m_space_4x=10, m_space_2x=0, m_space_1x=0, origin=sa_origin)
    laygen.add_template_from_cell()
    # # 2. calculate spacing param and regenerate
    # x0 = 2*laygen.templates.get_template('capdac', libname=workinglib).xy[1][0] \
    #      - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0]
    # m_space = int(round(x0 / 2 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    # m_space_4x = int(m_space / 4)
    # m_space_2x = int((m_space - m_space_4x * 4) / 2)
    # m_space_1x = int(m_space - m_space_4x * 4 - m_space_2x * 2)
    # #print("debug", x0, laygen.templates.get_template('capdrv_array_7b', libname=workinglib).xy[1][0] \
    # #        , laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
    # #        , laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0], m_space, m_space_4x, m_space_2x, m_space_1x)
    #
    # laygen.add_cell(cellname)
    # laygen.sel_cell(cellname)
    # generate_salatch_pmos_fitdim(laygen, objectname_pfix='SA0',
    #                             placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick,
    #                             routing_grid_m2m3=rg_m2m3, routing_grid_m2m3_thick=rg_m2m3_thick, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5,
    #                             devname_ptap_boundary='ptap_fast_boundary', devname_ptap_body='ptap_fast_center_nf1',
    #                             devname_nmos_boundary='nmos4_fast_boundary', devname_nmos_body='nmos4_fast_center_nf2',
    #                             devname_nmos_dmy='nmos4_fast_dmy_nf2',
    #                             devname_pmos_boundary='pmos4_fast_boundary', devname_pmos_body='pmos4_fast_center_nf2',
    #                             devname_pmos_dmy='pmos4_fast_dmy_nf2',
    #                             devname_ntap_boundary='ntap_fast_boundary', devname_ntap_body='ntap_fast_center_nf1',
    #                             m_in=m_in, m_ofst=m_ofst, m_clkh=m_clkh, m_rgnn=m_rgnn, m_rstn=m_rstn, m_buf=m_buf,
    #                             m_space_4x=10+m_space_4x, m_space_2x=m_space_2x, m_space_1x=m_space_1x, origin=sa_origin)
    # laygen.add_template_from_cell()
    

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

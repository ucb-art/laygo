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
            laygen.via(name=None, xy=[0, 1], refobj=itap0.elements[m - 1, 0].pins['TAP2'], gridname=rg12t)
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

def generate_source_follower(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, devname_mos_boundary, devname_mos_body,
                             devname_mos_dmy, devname_tap_boundary, devname_tap_body,
                             devname_mos_space_4x, devname_mos_space_2x, devname_mos_space_1x,
                             devname_tap_space_4x, devname_tap_space_2x, devname_tap_space_1x,
                             m_mir=2, m_bias=2, m_in=2, m_ofst=2, m_bias_dum=2, m_in_dum=2, m_byp=2, m_byp_bias=2, bias_current=True, origin=np.array([0,0])):
    """generate an analog differential mos structure with dummmies """
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    # placement
    # generate boundary
    x0=laygen.get_template_size('capdac', gridname=pg, libname=workinglib)[0]*2
    x1=laygen.get_template_size('boundary_bottomleft', gridname=pg, libname=utemplib)[0]
    m_bnd=int((x0-x1*2)/laygen.get_template_size('boundary_bottom', gridname=pg, libname=utemplib)[0])
    [bnd_bottom, bnd_top, bnd_left, bnd_right]=generate_boundary(laygen, objectname_pfix='BND0',
        placement_grid=pg,
        devname_bottom = ['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
        shape_bottom = [np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
        devname_top = ['boundary_topleft', 'boundary_top', 'boundary_topright'],
        shape_top = [np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
        devname_left = ['ptap_fast_left', 'nmos4_fast_left', 'ptap_fast_left', 'ptap_fast_left', 'nmos4_fast_left', 'ptap_fast_left'],
        transform_left=['MX', 'R0', 'MX', 'R0', 'MX', 'R0'],
        devname_right=['ptap_fast_right', 'nmos4_fast_right','ptap_fast_right','ptap_fast_right', 'nmos4_fast_right','ptap_fast_right'],
        transform_right = ['MX', 'R0', 'MX', 'R0', 'MX', 'R0'],
        origin=np.array([0, 0]))

    # generate the first tap row
    m_tap = max((m_bias_dum*6+m_ofst+int(m_mir/2)*2+m_bias+m_byp_bias), (m_in_dum*3+m_in+m_byp+2))+4
    tap_origin = laygen.get_inst_xy(bnd_left[0].name, pg) + laygen.get_template_size('ptap_fast_left', pg)[0]*np.array([1,0])
    [itapbl0, itap0, itapbr0] = generate_tap(laygen, objectname_pfix=objectname_pfix+'PTAP0', placement_grid=pg,
                                             routing_grid_m1m2_thick=rg_m1m2_thick,
                                             devname_tap_boundary=devname_tap_boundary, devname_tap_body=devname_tap_body,
                                             m=m_tap, double_rail=False, origin=tap_origin, transform='MX')

    # generate the second current mirror & bias devices row
    if m_bias_dum * 6 + m_ofst + int(m_mir / 2) * 2 + m_bias + m_byp_bias > m_in_dum * 3 + m_in + m_byp + 2:
        m_bias_dum_r = m_bias_dum
    else:
        m_bias_dum_r = (m_in_dum*3+m_in+m_byp+2) - (m_bias_dum*5+m_ofst+int(m_mir/2)*2+m_bias+m_byp_bias)
    imspl0 = laygen.relplace("I" + objectname_pfix + 'SPL0', devname_mos_space_4x, pg, bnd_left[1].name, shape=np.array([2, 1]))
    imbl0 = laygen.relplace("I" + objectname_pfix + 'BL0', devname_mos_boundary, pg, imspl0.name)
    imdmyl0 = laygen.relplace("I" + objectname_pfix + 'DMYL0', devname_mos_dmy, pg, imbl0.name, shape=np.array([m_bias_dum, 1]))
    imofst0 = laygen.relplace("I" + objectname_pfix + 'OFST0', devname_mos_body, pg, imdmyl0.name, shape=np.array([m_ofst, 1]))
    imdmyl1 = laygen.relplace("I" + objectname_pfix + 'DMYL1', devname_mos_dmy, pg, imofst0.name, shape=np.array([m_bias_dum, 1]))
    if bias_current == True:
        immirl = laygen.relplace("I" + objectname_pfix + 'MIRL0', devname_mos_body, pg, imdmyl1.name, shape=np.array([int(m_mir/2), 1]))
    else:
        # immirl = laygen.relplace("I" + objectname_pfix + 'MIRL0', devname_mos_space_2x, pg, imdmyl1.name, shape=np.array([int(m_mir/2), 1]))
        immirl = laygen.relplace("I" + objectname_pfix + 'MIRL0', devname_mos_boundary, pg, imdmyl1.name, shape=np.array([int(m_mir), 1]))
    imdmyl2 = laygen.relplace("I" + objectname_pfix + 'DMYL2', devname_mos_dmy, pg, immirl.name, shape=np.array([m_bias_dum, 1]))
    imbias0 = laygen.relplace("I" + objectname_pfix + 'BIAS0', devname_mos_body, pg, imdmyl2.name, shape=np.array([m_bias, 1]))
    imdmyr0 = laygen.relplace("I" + objectname_pfix + 'DMYR0', devname_mos_dmy, pg, imbias0.name, shape=np.array([m_bias_dum, 1]), transform='MY')
    if bias_current == True:
        immirr = laygen.relplace("I" + objectname_pfix + 'MIRR0', devname_mos_body, pg, imdmyr0.name, shape=np.array([int(m_mir/2), 1]), transform='MY')
    else:
        # immirr = laygen.relplace("I" + objectname_pfix + 'MIRR0', devname_mos_space_2x, pg, imdmyr0.name, shape=np.array([int(m_mir/2), 1]), transform='MY')
        immirr = laygen.relplace("I" + objectname_pfix + 'MIRR0', devname_mos_boundary, pg, imdmyr0.name, shape=np.array([int(m_mir), 1]), transform='MY')
    imdmyr0_1 = laygen.relplace("I" + objectname_pfix + 'DMYR0_1', devname_mos_dmy, pg, immirr.name, shape=np.array([m_bias_dum, 1]), transform='MY')
    imbyp_bias = laygen.relplace("I" + objectname_pfix + 'BYPBIAS', devname_mos_body, pg, imdmyr0_1.name, shape=np.array([m_byp_bias, 1]), transform='MY')
    imdmyr1 = laygen.relplace("I" + objectname_pfix + 'DMYR1', devname_mos_dmy, pg, imbyp_bias.name, shape=np.array([m_bias_dum_r, 1]), transform='MY')
    imbr0 = laygen.relplace("I" + objectname_pfix + 'BR0', devname_mos_boundary, pg, imdmyr1.name, transform='MY')

    # generate the third tap row
    tap_origin = laygen.get_inst_xy(bnd_left[2].name, pg) + laygen.get_template_size('ptap_fast_left', pg)[0]*np.array([1,0])
    [itapbl2, itap2, itapbr2] = generate_tap(laygen, objectname_pfix=objectname_pfix+'PTAP1', placement_grid=pg,
                                             routing_grid_m1m2_thick=rg_m1m2_thick,
                                             devname_tap_boundary=devname_tap_boundary, devname_tap_body=devname_tap_body,
                                             m=m_tap, double_rail=False, origin=tap_origin, transform='MX')

    # generate the fourth tap row
    tap_origin = laygen.get_inst_xy(bnd_left[3].name, pg) + laygen.get_template_size('ptap_fast_left', pg)[0]*np.array([1,0])
    [itapbl3, itap3, itapbr3] = generate_tap(laygen, objectname_pfix=objectname_pfix+'PTAP2', placement_grid=pg,
                                             routing_grid_m1m2_thick=rg_m1m2_thick,
                                             devname_tap_boundary=devname_tap_boundary, devname_tap_body=devname_tap_body,
                                             m=m_tap, double_rail=False, origin=tap_origin, transform='R0')

    # generate the fifth input device row
    if m_bias_dum * 6 + m_ofst + int(m_mir / 2) * 2 + m_bias + m_byp_bias < m_in_dum * 3 + m_in + m_byp + 2:
        m_in_dum_r = m_in_dum
    else:
        m_in_dum_r = (m_bias_dum * 6 + m_ofst + int(m_mir / 2) * 2 + m_bias) - (m_in_dum * 2 + m_in)
    imspl_in0 = laygen.relplace("I" + objectname_pfix + 'SPLin0', devname_mos_space_4x, pg, bnd_left[4].name, shape=np.array([2, 1]), transform='MX')
    imbl_in0 = laygen.relplace("I" + objectname_pfix + 'BLin0', devname_mos_boundary, pg, imspl_in0.name, transform='MX')
    imdmyl_in0 = laygen.relplace("I" + objectname_pfix + 'DMYLin0', devname_mos_body, pg, imbl_in0.name, shape=np.array([m_in_dum, 1]), transform='MX')
    imin0 = laygen.relplace("I" + objectname_pfix + 'IN0', devname_mos_body, pg, imdmyl_in0.name, shape=np.array([m_in, 1]), transform='MX')
    imdmyr_in0_0 = laygen.relplace("I" + objectname_pfix + 'DMYRin0_0', devname_mos_body, pg, imin0.name, shape=np.array([m_in_dum, 1]), transform='MX')
    imbyp_bnl = laygen.relplace("I" + objectname_pfix + 'BYP_BNL', devname_mos_boundary, pg, imdmyr_in0_0.name, shape=np.array([2, 1]), transform='MX')
    imbyp = laygen.relplace("I" + objectname_pfix + 'BYP', devname_mos_body, pg, imbyp_bnl.name, shape=np.array([m_byp, 1]), transform='MX')
    imdmyr_bnr = laygen.relplace("I" + objectname_pfix + 'BYP_BNR', devname_mos_boundary, pg, imbyp.name, shape=np.array([2, 1]), transform='R180')
    imdmyr_in0 = laygen.relplace("I" + objectname_pfix + 'DMYRin0', devname_mos_body, pg, imdmyr_bnr.name, shape=np.array([m_in_dum_r, 1]), transform='R180')
    imbr_in0 = laygen.relplace("I" + objectname_pfix + 'BRin0', devname_mos_boundary, pg, imdmyr_in0.name, transform='R180')

    # generate the sixth tap row
    tap_origin = laygen.get_inst_xy(bnd_left[5].name, pg) + laygen.get_template_size('ptap_fast_left', pg)[0]*np.array([1,0])
    [itapbl1, itap1, itapbr1] = generate_tap(laygen, objectname_pfix=objectname_pfix+'PTAP3', placement_grid=pg,
                                             routing_grid_m1m2_thick=rg_m1m2_thick,
                                             devname_tap_boundary=devname_tap_boundary, devname_tap_body=devname_tap_body,
                                             m=m_tap, double_rail=False, origin=tap_origin)
    # generate space
    x_sp4 = laygen.get_template_size('nmos4_fast_space_nf4', gridname=pg, libname=utemplib)[0]
    x_sp2 = laygen.get_template_size('nmos4_fast_space_nf2', gridname=pg, libname=utemplib)[0]
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
    isp2_4x = laygen.relplace("I" + objectname_pfix + 'sp2_4x', devname_tap_space_4x, pg, itapbr2.name,
                              shape=[m_sp4x, 1], transform='MX')
    isp2_1x = laygen.relplace("I" + objectname_pfix + 'sp2_1x', devname_tap_space_1x, pg, isp2_4x.name,
                              shape=[m_sp1x, 1], transform='MX')
    isp3_4x = laygen.relplace("I" + objectname_pfix + 'sp3_4x', devname_tap_space_4x, pg, itapbr3.name,
                              shape=[m_sp4x, 1])
    isp3_1x = laygen.relplace("I" + objectname_pfix + 'sp3_1x', devname_tap_space_1x, pg, isp3_4x.name,
                              shape=[m_sp1x, 1])
    isp4_4x = laygen.relplace("I" + objectname_pfix + 'sp4_4x', devname_mos_space_4x, pg, imbr_in0.name,
                              shape=[m_sp4x, 1], transform='MX')
    isp4_1x = laygen.relplace("I" + objectname_pfix + 'sp4_1x', devname_mos_space_1x, pg, isp4_4x.name,
                              shape=[m_sp1x, 1], transform='MX')
    isp5_4x = laygen.relplace("I" + objectname_pfix + 'sp5_4x', devname_tap_space_4x, pg, itapbr1.name, shape=[m_sp4x,1])
    isp5_1x = laygen.relplace("I" + objectname_pfix + 'sp5_1x', devname_tap_space_1x, pg, isp5_4x.name, shape=[m_sp1x,1])

    # route
    # VBIAS
    for i in range(m_bias-1):
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imbias0.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=imbias0.name, refpinname1='G0', refinstindex1=np.array([i+1, 0]),
                     via0=[0,0], via1=[0,0])
        rvb = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([1, 0]), xy1=np.array([1, -10]), gridname0=rg_m2m3,
                     refinstname0=imbias0.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=imbias0.name, refpinname1='G0', refinstindex1=np.array([i, 0]), via0=[0,0])
        laygen.boundary_pin_from_rect(rvb, rg_m2m3, 'VBIAS'+str(i), laygen.layers['pin'][3], size=4, direction='bottom', netname='VBIAS')

    if bias_current == True:
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

    # IBYP_BIAS routing
    for i in range(m_byp_bias-1):
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imbyp_bias.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=imbyp_bias.name, refpinname1='G0', refinstindex1=np.array([i+1, 0]),
                     via0=[0,0], via1=[0,0])
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imbyp_bias.name, refpinname0='D0', refinstindex0=np.array([i, 0]),
                     refinstname1=imbyp_bias.name, refpinname1='D0', refinstindex1=np.array([i+1, 0]),
                     via0=[0,0], via1=[0,0])
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=imbyp_bias.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbias0.name, refpinname1='D0', refinstindex1=np.array([0, 0]))
    for i in range(m_bias-1):
        laygen.via(None, np.array([0, 0]), rg_m2m3, refinstname=imbias0.name, refpinname='S1', refinstindex=np.array([i, 0]))

    # IBIAS/IMIR/IBYP_BIAS VSS connection
    for i in range(m_tap):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -3]), gridname0=rg_m1m2,
                     refinstname0=itap0.name, refpinname0='TAP0', refinstindex0=np.array([i, 0]),
                     refinstname1=itap0.name, refpinname1='TAP0', refinstindex1=np.array([i, 0]))
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -3]), gridname0=rg_m1m2,
                 refinstname0=itap0.name, refpinname0='TAP2', refinstindex0=np.array([m_tap-1, 0]),
                 refinstname1=itap0.name, refpinname1='TAP2', refinstindex1=np.array([m_tap-1, 0]))
    # IBIAS/IMIR Dummy VSS connection
    idmy_list = [imdmyl0, imdmyl1, imdmyl2, imdmyr0, imdmyr0_1]
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
                 refinstname1=imdmyr_in0_0.name, refpinname1='S0', refinstindex1=np.array([m_in_dum - 1, 0]))
    for i in range(m_in):
        laygen.via(None, np.array([0, 1]), rg_m1m2, refinstname=imin0.name, refpinname='D0',refinstindex=np.array([i, 0]))
        ro_v0, ro_h0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]),
                        gridname0=rg_m2m3, refinstname0=imin0.name, refpinname0='D0', refinstindex0=np.array([i, 0]),
                        refinstname1 = imbias0.name, refpinname1 = 'D0', refinstindex1 = np.array([0, 0]), via0=[0,0])
        # laygen.boundary_pin_from_rect(ro_v0, rg_m2m3, 'out'+str(i), laygen.layers['pin'][3], size=4, direction='top', netname='out')

    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                 refinstname0=imdmyl0.name, refpinname0='S0', refinstindex0=np.array([m_bias_dum - 1, 0]),
                 refinstname1=imdmyr1.name, refpinname1='S0', refinstindex1=np.array([0, 0]))
    for i in range(m_bias):
        laygen.via(None, np.array([0, 1]), rg_m1m2, refinstname=imbias0.name, refpinname='D0',refinstindex=np.array([i, 0]))
        ro_v0, ro_h0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], xy0=np.array([0, 1]),
                                   xy1=np.array([0, 1]), gridname0=rg_m2m3, refinstname0=imbias0.name, refpinname0='D0',
                                   refinstindex0=np.array([i, 0]), refinstname1=imin0.name, refpinname1='D0',
                                   refinstindex1=np.array([0, 0]), via0=[0, 0])
        laygen.via(None, np.array([0, 0]), rg_m3m4_thick, refinstname=imbias0.name, refpinname='D0',refinstindex=np.array([i, 0]))
        # laygen.boundary_pin_from_rect(ro_v0, rg_m2m3, 'out' + str(m_in+i), laygen.layers['pin'][3], size=4, direction='top',
        #                           netname='out')
    ro_m4=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4_thick,
                 refinstname0=imbias0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbias0.name, refpinname1='D0', refinstindex1=np.array([m_bias-1, 0]))
    laygen.pin(name='out', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(ro_m4.name, rg_m3m4_thick), gridname=rg_m3m4_thick)

    for i in range(m_ofst):
        laygen.via(None, np.array([0, 1]), rg_m1m2, refinstname=imofst0.name, refpinname='D0',refinstindex=np.array([i, 0]))

    # Input
    for i in range(m_in-1):
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imin0.name, refpinname0='G0', refinstindex0=np.array([i, 0]), via0=[0,0],
                     refinstname1=imin0.name, refpinname1='G0', refinstindex1=np.array([i+1, 0]), via1=[0,0])
    rin_m3 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([1, 0]), xy1=np.array([1, 3]), gridname0=rg_m2m3,
                 refinstname0=imin0.name, refpinname0='G0', refinstindex0=np.array([0, 0]), via0=[0, 0],
                 refinstname1=imin0.name, refpinname1='G0', refinstindex1=np.array([0, 0]))
    rin_m4 = laygen.route(None, laygen.layers['metal'][4], xy0=laygen.get_rect_xy(rin_m3.name, rg_m3m4)[0],
                          xy1=laygen.get_rect_xy(rin_m3.name, rg_m3m4)[0]-np.array([3, 0]), gridname0=rg_m3m4,
                          via0=[0, 0])
    rin = laygen.route(None, laygen.layers['metal'][5], xy0=laygen.get_rect_xy(rin_m4.name, rg_m4m5_basic_thick)[1],
                          xy1=laygen.get_rect_xy(rin_m4.name, rg_m4m5_basic_thick)[1]+np.array([0, 6]), gridname0=rg_m4m5_basic_thick,
                          via0=[0, 0])
    # rin_m4, rin = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], xy0=np.array([1, 3]),
    #                 xy1=np.array([4, -4]), gridname0=rg_m3m4, gridname1=rg_m4m5_basic_thick,
    #                               refinstname0=imin0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
    #                 refinstname1=imin0.name, refpinname1='G0', refinstindex1=np.array([0, 0]))
    laygen.pin_from_rect('in', laygen.layers['pin'][5], rin, rg_m4m5_basic_thick)

    # In-Out bypass
    for i in range(m_byp):
        if not i == m_byp-1:
            laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                         refinstname0=imbyp.name, refpinname0='G0', refinstindex0=np.array([i, 0]), via0=[0,0],
                         refinstname1=imbyp.name, refpinname1='G0', refinstindex1=np.array([i+1, 0]), via1=[0,0])
            laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                         refinstname0=imbyp.name, refpinname0='D0', refinstindex0=np.array([i, 0]), via0=[0, 0],
                         refinstname1=imbyp.name, refpinname1='D0', refinstindex1=np.array([i + 1, 0]), via1=[0, 0])
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imbyp.name, refpinname0='S0', refinstindex0=np.array([i, 0]), via0=[0, 0],
                     refinstname1=imbyp.name, refpinname1='S0', refinstindex1=np.array([i + 1, 0]), via1=[0, 0])
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                 refinstname0=imbyp.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=imin0.name, refpinname1='D0', refinstindex1=np.array([0, 0]))
    # laygen.route_hv(laygen.layers['metal'][2], laygen.layers['metal'][3], xy0=np.array([0, 0]),
    #                 xy1=np.array([1, 0]), gridname0=rg_m2m3,
    #                 refinstname0=imbyp.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
    #                 refinstname1=imin0.name, refpinname1='G0', refinstindex1=np.array([0, 0]))
    laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], xy1=np.array([0, 0]),
                    xy0=np.array([1, 0]), gridname0=rg_m2m3,
                    refinstname1=imbyp.name, refpinname1='S0', refinstindex1=np.array([0, 0]),
                    refinstname0=imin0.name, refpinname0='G0', refinstindex0=np.array([0, 0]))

    # Input dummy
    idmy_in_list = [imdmyl_in0, imdmyr_in0_0]
    for j in range(len(idmy_in_list)):
        for i in range(m_in_dum-1):
            laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                         refinstname0=idmy_in_list[j].name, refpinname0='G0', refinstindex0=np.array([i, 0]), via0=[0,0],
                         refinstname1=idmy_in_list[j].name, refpinname1='G0', refinstindex1=np.array([i+1, 0]), via1=[0,0])
        for i in range(m_in_dum):
            laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                         refinstname0=idmy_in_list[j].name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                         refinstname1=idmy_in_list[j].name, refpinname1='D0', refinstindex1=np.array([i, 0]))
        # laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], xy0=np.array([0, 0]),
        #                xy1=np.array([0, 0]), gridname0=rg_m2m3, gridname1=rg_m2m3_thick,
        #                 refinstname0=idmy_in_list[j].name, refpinname0='G0',
        #                refinstindex0=np.array([0, 0]), refinstname1=itap1.name, refpinname1='TAP0',
        #                refinstindex1=np.array([0, 0]), via0=[0, 0]) #gate to VSS
        laygen.route_hv(laygen.layers['metal'][2], laygen.layers['metal'][3], xy0=np.array([0, 0]),
                       xy1=np.array([0, 0]), gridname0=rg_m2m3_thick, gridname1=rg_m2m3,
                        refinstname0=itap1.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=idmy_in_list[j].name, refpinname1='G0', refinstindex1=np.array([0, 0]), via1=[0, 0]
                        ) #gate to VSS
    for i in range(m_in_dum_r-1):
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imdmyr_in0.name, refpinname0='G0', refinstindex0=np.array([i, 0]), via0=[0,0],
                     refinstname1=imdmyr_in0.name, refpinname1='G0', refinstindex1=np.array([i+1, 0]), via1=[0,0])
    for i in range(m_in_dum_r):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imdmyr_in0.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=imdmyr_in0.name, refpinname1='D0', refinstindex1=np.array([i, 0]))
        # laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
        #              refinstname0=imdmyr_in0.name, refpinname0='S0', refinstindex0=np.array([i, 0]), via0=[0,0],
        #              refinstname1=imdmyr_in0.name, refpinname1='S0', refinstindex1=np.array([i+1, 0]), via1=[0,0])
    # laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], xy0=np.array([0, 0]),
    #                xy1=np.array([0, 0]), gridname0=rg_m2m3, gridname1=rg_m2m3_thick,
    #                 refinstname0=imdmyr_in0.name, refpinname0='G0',
    #                refinstindex0=np.array([1, 0]), refinstname1=itap1.name, refpinname1='TAP0',
    #                refinstindex1=np.array([0, 0]), via0=[0, 0]) #gate to VSS
    laygen.route_hv(laygen.layers['metal'][2], laygen.layers['metal'][3], xy0=np.array([0, 0]),
                    xy1=np.array([0, 0]), gridname0=rg_m2m3_thick, gridname1=rg_m2m3,
                    refinstname0=itap1.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                    refinstname1=imdmyr_in0.name, refpinname1='G0', refinstindex1=np.array([0, 0]), via1=[0, 0]
                    )  # gate to VSS

    # Voff
    for i in range(m_ofst):
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imofst0.name, refpinname0='G0', refinstindex0=np.array([i, 0]), via0=[0,0],
                     refinstname1=imofst0.name, refpinname1='G0', refinstindex1=np.array([i+1, 0]))
    roff = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([1, 0]), xy1=np.array([1, -10]), gridname0=rg_m2m3,
                 refinstname0=imofst0.name, refpinname0='G0', refinstindex0=np.array([0, 0]), via0=[0, 0],
                 refinstname1=imofst0.name, refpinname1='G0', refinstindex1=np.array([0, 0]))
    laygen.boundary_pin_from_rect(roff, rg_m2m3, 'Voff', laygen.layers['pin'][3], size=4, direction='bottom')

    # Bypass signal
    # rbyp, rv = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
    #              refinstname0=imbyp.name, refpinname0='G0', refinstindex0=np.array([0, 0]), via0=[0, 0],
    #              refinstname1=imbyp_bias.name, refpinname1='G0', refinstindex1=np.array([0, 0]), via1=[0, 0])
    rbyp, rv = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], xy0=np.array([0, 0]),
                   xy1=np.array([0, 0]), gridname0=rg_m2m3, refinstname0=imbyp.name, refpinname0='G0',
                   refinstindex0=np.array([0, 0]), refinstname1=imbyp_bias.name, refpinname1='G0',
                   refinstindex1=np.array([0, 0]), via0=[0, 0]) #gate to VSS
    laygen.boundary_pin_from_rect(rbyp, rg_m2m3, 'bypass', laygen.layers['pin'][3], size=4, direction='bottom')

    # Input device VDD connection
    for i in range(m_in):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imin0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imin0.name, refpinname1='S0', refinstindex1=np.array([i, 0]), via1=[0,0])
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imin0.name, refpinname0='S1', refinstindex0=np.array([i, 0]),
                     refinstname1=imin0.name, refpinname1='S1', refinstindex1=np.array([i, 0]), via1=[0,0])
    # Input dummy VDD connection
    for j in range(len(idmy_in_list)):
        for i in range(m_in_dum):
            laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                         refinstname0=idmy_in_list[j].name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                         refinstname1=idmy_in_list[j].name, refpinname1='S0', refinstindex1=np.array([i, 0]), via1=[0, 0])
            laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]),
                         gridname0=rg_m1m2,
                         refinstname0=idmy_in_list[j].name, refpinname0='S1', refinstindex0=np.array([i, 0]),
                         refinstname1=idmy_in_list[j].name, refpinname1='S1', refinstindex1=np.array([i, 0]), via1=[0, 0])
    # Input dummy R VDD connection
    for i in range(m_in_dum_r):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imdmyr_in0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imdmyr_in0.name, refpinname1='S0', refinstindex1=np.array([i, 0]), via1=[0, 0])
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imdmyr_in0.name, refpinname0='S1', refinstindex0=np.array([i, 0]),
                     refinstname1=imdmyr_in0.name, refpinname1='S1', refinstindex1=np.array([i, 0]), via1=[0, 0])

    # VSS/VDD
    num_vert_pwr_l = 3
    num_vert_pwr_r = 3
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
    rvss2 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr_l, 0]), xy1=np.array([2*num_vert_pwr_r, 0]), gridname0=rg_m2m3_thick,
                        refinstname0=itap2.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=itap2.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0]))
    rvss2_0 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr_l, 1]), xy1=np.array([2*num_vert_pwr_r, 1]), gridname0=rg_m2m3_thick,
                        refinstname0=itap2.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=itap2.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0]))
    rvss3 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr_l, 0]), xy1=np.array([2*num_vert_pwr_r, 0]), gridname0=rg_m2m3_thick,
                        refinstname0=itap3.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=itap3.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0]))
    rvss3_0 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr_l, 1]), xy1=np.array([2*num_vert_pwr_r, 1]), gridname0=rg_m2m3_thick,
                        refinstname0=itap3.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=itap3.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0]))
    # M2 VDD rail
    rvdd = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr_l-8, -1]), xy1=np.array([-2*num_vert_pwr_r, -1]), gridname0=rg_m2m3,
                 refinstname0=imdmyl_in0.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=imdmyr_in0.name, refpinname1='S0', refinstindex1=np.array([0, 0]))

    # M3 VDD/VSS vertical
    for i in range(num_vert_pwr_l):
        rvvss_l = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 1]), xy1=np.array([2*i+1, 1]), gridname0=rg_m2m3_thick,
                               refinstname0=itap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                               refinstname1=itap1.name, refpinname1='TAP0', refinstindex1=np.array([0, 0]))
        rvvdd_l = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+0, 1]), xy1=np.array([2*i+0, 1]), gridname0=rg_m2m3_thick,
                               refinstname0=itap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                               refinstname1=itap1.name, refpinname1='TAP0', refinstindex1=np.array([0, 0]))
        laygen.via(None, np.array([2*i+1, 1]), refinstname=itap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, 0]), refinstname=itap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, 1]), refinstname=itap1.name, refpinname='TAP0',
                   refinstindex=np.array([0, 0]), gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, 0]), refinstname=itap1.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, 1]), refinstname=itap2.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, 0]), refinstname=itap2.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, 1]), refinstname=itap3.name, refpinname='TAP0',
                   refinstindex=np.array([0, 0]), gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, 0]), refinstname=itap3.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+0-8, -1]), refinstname=imdmyl_in0.name, refpinname='S0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3)
        laygen.pin(name='VSS'+str(i), layer=laygen.layers['pin'][3], xy=laygen.get_rect_xy(rvvss_l.name, rg_m2m3_thick),
                   gridname=rg_m2m3_thick, netname='VSS')
        laygen.pin(name='VDD'+str(i), layer=laygen.layers['pin'][3], xy=laygen.get_rect_xy(rvvdd_l.name, rg_m2m3_thick),
                   gridname=rg_m2m3_thick, netname='VDD')
    for i in range(num_vert_pwr_r):
        rvvss_r = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2 * i + 1, 1]),
                               xy1=np.array([2 * i + 1, 1]), gridname0=rg_m2m3_thick,
                               refinstname0=isp0_4x.name, refinstindex0=np.array([m_sp4x-1, 0]),
                               refinstname1=isp5_4x.name, refinstindex1=np.array([m_sp4x-1, 0]))
        rvvdd_r = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2 * i + 2, 1]),
                               xy1=np.array([2 * i + 2, 1]), gridname0=rg_m2m3_thick,
                               refinstname0=isp0_4x.name, refinstindex0=np.array([m_sp4x-1, 0]),
                               refinstname1=isp5_4x.name, refinstindex1=np.array([m_sp4x-1, 0]))
        # laygen.via(None, np.array([2 * i + 1, 1]), refinstname=isp0_4x.name, refinstindex=np.array([m_sp4x-1, 0]), gridname=rg_m2m3_thick)
        # laygen.via(None, np.array([2 * i + 1, 0]), refinstname=isp0_4x.name, refinstindex=np.array([m_sp4x-1, 0]), gridname=rg_m2m3_thick)
        # laygen.via(None, np.array([2 * i + 1, 1]), refinstname=isp5_4x.name, refinstindex=np.array([m_sp4x-1, 0]), gridname=rg_m2m3_thick)
        # laygen.via(None, np.array([2 * i + 1, 0]), refinstname=isp5_4x.name, refinstindex=np.array([m_sp4x-1, 0]), gridname=rg_m2m3_thick)
        # laygen.via(None, np.array([-2 * i - 2, -1]), refinstname=imdmyr_in0.name, refpinname='S0',
        #            refinstindex=np.array([0, 0]), gridname=rg_m2m3)
        laygen.pin(name='VSS' + str(num_vert_pwr_l+i), layer=laygen.layers['pin'][3], xy=laygen.get_rect_xy(rvvss_r.name, rg_m2m3_thick),
                   gridname=rg_m2m3_thick, netname='VSS')
        laygen.pin(name='VDD' + str(num_vert_pwr_l+i), layer=laygen.layers['pin'][3], xy=laygen.get_rect_xy(rvvdd_r.name, rg_m2m3_thick),
                   gridname=rg_m2m3_thick, netname='VDD')

def generate_source_follower_vref(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, devname_mos_boundary, devname_mos_body,
                             devname_mos_dmy, devname_tap_boundary, devname_tap_body,
                             devname_mos_space_4x, devname_mos_space_2x, devname_mos_space_1x,
                             devname_tap_space_4x, devname_tap_space_2x, devname_tap_space_1x,
                             m_mir=2, m_bias=2, m_in=2, m_ofst=2, m_bias_dum=2, m_in_dum=2, m_byp=2, m_byp_bias=2, origin=np.array([0,0])):
    """generate an analog differential mos structure with dummmies """
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    # placement
    # generate boundary
    x_off = laygen.get_template_size('sourceFollower_vref_unit', gridname=pg, libname=workinglib)[0]
    isf0 = laygen.relplace("I" + objectname_pfix + 'SF0', 'sourceFollower_vref_unit', pg, xy=origin+np.array([0, 0]), transform='R0', template_libname=workinglib)
    isf1 = laygen.relplace("I" + objectname_pfix + 'SF1', 'sourceFollower_vref_unit', pg, isf0.name, direction='top', transform='R0', template_libname=workinglib)
    isf2 = laygen.relplace("I" + objectname_pfix + 'SF2', 'sourceFollower_vref_unit', pg, isf1.name, direction='top', transform='R0', template_libname=workinglib)
    isf_list = [isf0, isf1, isf2]
    isf_suffix_list = ['<0>', '<1>', '<2>']

    # pins
    sf_template = laygen.templates.get_template('sourceFollower_vref_unit', workinglib)
    sf_pins=sf_template.pins
    sf0_xy=isf0.xy
    sf1_xy=isf1.xy
    sf2_xy=isf2.xy
    pdict_m3m4=laygen.get_inst_pin_xy(None, None, rg_m3m4)
    pdict_m3m4_thick=laygen.get_inst_pin_xy(None, None, rg_m3m4_basic_thick)
    pdict_m4m5_basic_thick=laygen.get_inst_pin_xy(None, None, rg_m4m5_basic_thick)
    pdict_m4m5_thick=laygen.get_inst_pin_xy(None, None, rg_m4m5_thick)

    outcnt = [0, 0, 0]
    incnt = [0, 0, 0]
    vbiascnt = [0, 0, 0]
    voffcnt = [0, 0, 0]
    for pn, p in sf_pins.items():
        # output pins
        if pn.startswith('out'):
            for i in range(len(isf_list)):
                # pn='out'
                pn_out='out'+isf_suffix_list[i]
                laygen.pin(name=pn_out, layer=sf_pins[pn]['layer'], netname='out'+isf_suffix_list[i],
                           xy=pdict_m3m4_thick[isf_list[i].name][pn], gridname=rg_m3m4_basic_thick)
                outcnt[i]+=1

    pn = 'in'
    for i in range(len(isf_list)):
        pn_out = 'in' + isf_suffix_list[i]
        laygen.pin(name=pn_out, layer=sf_pins[pn]['layer'], netname='in' + isf_suffix_list[i],
                   xy=pdict_m4m5_basic_thick[isf_list[i].name][pn], gridname=rg_m4m5_basic_thick)
    # vbias pins
    pdict_m3m4_bt=laygen.get_inst_pin_xy(None, None, rg_m3m4_basic_thick)
    for i in range(len(isf_list)):
        vbias_xy = []
        for pn, p in sf_pins.items():
            if pn.startswith('VBIAS'):
                vbias_xy.append(pdict_m3m4_thick[isf_list[i].name][pn][0])
                # laygen.pin(name=pn_out, layer=sf_pins[pn]['layer'], netname='VBIAS' + isf_suffix_list[i],
                #            xy=pdict_m3m4[isf_list[i].name][pn], gridname=rg_m3m4)
                # vbiascnt[i] += 1
        for j in range(len(vbias_xy)-1):
            laygen.route(None, laygen.layers['metal'][4], xy0=vbias_xy[j], xy1=vbias_xy[j+1], gridname0=rg_m3m4_basic_thick,
                         via0=[0, 0], via1=[0, 0])
        # rvb = laygen.route(None, laygen.layers['metal'][5], xy0=pdict_m4m5_thick[isf_list[i].name]['VBIAS0'][0],
        #              xy1=pdict_m4m5_thick[isf_list[i].name]['VBIAS0'][0]+np.array([0, 4]),
        #              gridname0=rg_m4m5_thick, via0=[0, 0])
        rvb = laygen.route(None, laygen.layers['metal'][4],
                           xy0=pdict_m4m5_thick[isf_list[i].name]['VBIAS0'][0]+np.array([1,0]),
                           xy1=np.array([pdict_m4m5_thick[isf_list[i].name]['in'][0][0] + 1,
                                         pdict_m4m5_thick[isf_list[i].name]['VBIAS0'][0][1]]),
                           gridname0=rg_m4m5_thick, via1=[0,0])
        ref_y = pdict_m3m4_bt[isf_list[i].name]['VSS0'][0][1]
        rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                   xy0=pdict_m3m4_thick[isf_list[i].name]['Voff'][0],
                                   xy1=np.array([0, ref_y]), gridname0=rg_m3m4_basic_thick)
        # pn_out = 'VBIAS' + isf_suffix_list[i]
        # laygen.boundary_pin_from_rect(rvb, rg_m4m5_thick, pn_out, laygen.layers['pin'][5], size=4, direction='top')
        # pn_out = 'Voff' + isf_suffix_list[i]
        # laygen.boundary_pin_from_rect(rvoff, rg_m4m5_thick, pn_out, laygen.layers['pin'][5], size=4, direction='top')

    rvb = laygen.route(None, laygen.layers['metal'][5],
                       xy0=np.array([pdict_m4m5_thick[isf_list[i].name]['in'][0][0]+1, pdict_m4m5_thick[isf_list[0].name]['VBIAS0'][0][1]]),
                       xy1=np.array([pdict_m4m5_thick[isf_list[i].name]['in'][0][0]+1, pdict_m4m5_thick[isf_list[-1].name]['VBIAS0'][0][1]]),
                       gridname0=rg_m4m5_thick)
    laygen.boundary_pin_from_rect(rvb, rg_m4m5_thick, 'VBIAS', laygen.layers['pin'][5], size=4, direction='top')

    # bypass route
    rbyp = laygen.route(None, layer=laygen.layers['metal'][3], xy0=pdict_m3m4[isf0.name]['bypass'][0],
                     xy1=pdict_m3m4[isf2.name]['bypass'][0], gridname0=rg_m3m4)
    print(laygen.get_xy(rbyp, rg_m3m4))
    laygen.pin(name='bypass', layer=laygen.layers['pin'][3], xy=laygen.get_xy(rbyp, rg_m3m4), gridname=rg_m3m4)

    # M3 VSS/VDD rails
    for pn, p in sf_pins.items():
        if pn.startswith('VSS'):
            pxy0 = pdict_m3m4_bt[isf0.name][pn][0]
            pxy1 = pdict_m3m4_bt[isf2.name][pn][0]
            rvss = laygen.route(None, laygen.layers['metal'][3], xy0=pxy0, xy1=pxy1,
                                 gridname0=rg_m3m4_basic_thick)
        if pn.startswith('VDD'):
            pxy0 = pdict_m3m4_bt[isf0.name][pn][0]
            pxy1 = pdict_m3m4_bt[isf2.name][pn][0]
            rvdd = laygen.route(None, laygen.layers['metal'][3], xy0=pxy0, xy1=pxy1,
                                 gridname0=rg_m3m4_basic_thick)
    # M4 VSS/VDD rails
    for i in range(len(isf_list)):
        ref_y = pdict_m3m4_bt[isf_list[i].name]['VSS0'][0][1]
        x0 = laygen.get_template_size('sourceFollower_vref_unit', rg_m3m4_basic_thick, libname=workinglib)[0]
        rvss0 = laygen.route(None, laygen.layers['metal'][4], xy0=[0, ref_y], xy1=[x0, ref_y], gridname0=rg_m3m4_basic_thick)
        rvdd0 = laygen.route(None, laygen.layers['metal'][4], xy0=[0, ref_y+1], xy1=[x0, ref_y+1], gridname0=rg_m3m4_basic_thick)
        laygen.pin(name='VSS'+str(2*i), layer=laygen.layers['pin'][4], xy=laygen.get_xy(rvss0, rg_m3m4_basic_thick),
                   netname='VSS', gridname=rg_m3m4_basic_thick)
        laygen.pin(name='VDD'+str(2*i), layer=laygen.layers['pin'][4], xy=laygen.get_xy(rvdd0, rg_m3m4_basic_thick),
                   netname='VDD', gridname=rg_m3m4_basic_thick)
        for pn, p in sf_pins.items():
            if pn.startswith('VSS'):
                pxyl=pdict_m3m4_bt[isf_list[i].name][pn]
                laygen.via(None, np.array([pxyl[0][0], ref_y]), gridname=rg_m3m4_basic_thick)
            if pn.startswith('VDD'):
                pxyl=pdict_m3m4_bt[isf_list[i].name][pn]
                laygen.via(None, np.array([pxyl[0][0], ref_y+1]), gridname=rg_m3m4_basic_thick)

        ref_y = pdict_m3m4_bt[isf_list[i].name]['VSS0'][1][1]
        rvss1 = laygen.route(None, laygen.layers['metal'][4], xy0=[0, ref_y-1], xy1=[x0, ref_y-1], gridname0=rg_m3m4_basic_thick)
        rvdd1 = laygen.route(None, laygen.layers['metal'][4], xy0=[0, ref_y], xy1=[x0, ref_y], gridname0=rg_m3m4_basic_thick)
        laygen.pin(name='VSS'+str(2*i+1), layer=laygen.layers['pin'][4], xy=laygen.get_xy(rvss1, rg_m3m4_basic_thick),
                   netname='VSS', gridname=rg_m3m4_basic_thick)
        laygen.pin(name='VDD'+str(2*i+1), layer=laygen.layers['pin'][4], xy=laygen.get_xy(rvdd1, rg_m3m4_basic_thick),
                   netname='VDD', gridname=rg_m3m4_basic_thick)
        for pn, p in sf_pins.items():
            if pn.startswith('VSS'):
                pxyl=pdict_m3m4_bt[isf_list[i].name][pn]
                laygen.via(None, np.array([pxyl[0][0], ref_y-1]), gridname=rg_m3m4_basic_thick)
            if pn.startswith('VDD'):
                pxyl=pdict_m3m4_bt[isf_list[i].name][pn]
                laygen.via(None, np.array([pxyl[0][0], ref_y]), gridname=rg_m3m4_basic_thick)

    # # M4 VSS/VDD upper rails
    # ref_y = pdict_m3m4_bt[isfl.name]['VSS0'][1][1]
    # rvss1 = laygen.route(None, laygen.layers['metal'][4], xy0=[0, ref_y-1], xy1=[x0, ref_y-1], gridname0=rg_m3m4_basic_thick)
    # rvdd1 = laygen.route(None, laygen.layers['metal'][4], xy0=[0, ref_y], xy1=[x0, ref_y], gridname0=rg_m3m4_basic_thick)
    # laygen.pin(name='VSS1', layer=laygen.layers['pin'][4], xy=laygen.get_xy(rvss1, rg_m3m4_basic_thick),
    #            netname='VSS', gridname=rg_m3m4_basic_thick)
    # laygen.pin(name='VDD1', layer=laygen.layers['pin'][4], xy=laygen.get_xy(rvdd1, rg_m3m4_basic_thick),
    #            netname='VDD', gridname=rg_m3m4_basic_thick)
    # for pn, p in sf_pins.items():
    #     if pn.startswith('VSS'):
    #         pxyl=pdict_m3m4_bt[isfl.name][pn]
    #         pxyr=pdict_m3m4_bt[isfr.name][pn]
    #         laygen.via(None, np.array([pxyl[0][0], ref_y-1]), gridname=rg_m3m4_basic_thick)
    #         laygen.via(None, np.array([pxyr[0][0], ref_y-1]), gridname=rg_m3m4_basic_thick)
    #     if pn.startswith('VDD'):
    #         pxyl=pdict_m3m4_bt[isfl.name][pn]
    #         pxyr=pdict_m3m4_bt[isfr.name][pn]
    #         laygen.via(None, np.array([pxyl[0][0], ref_y]), gridname=rg_m3m4_basic_thick)
    #         laygen.via(None, np.array([pxyr[0][0], ref_y]), gridname=rg_m3m4_basic_thick)

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
    rg_m3m4_thick = 'route_M3_M4_basic_thick'
    rg_m3m4_basic_thick = 'route_M3_M4_basic_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m4m5_basic_thick = 'route_M4_M5_basic_thick'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    mycell_list = []
    #salatch generation (wboundary)
    cellname = 'sourceFollower_vref_unit'
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
        m_mir=sizedict['sourceFollower_vref']['m_mirror']
        m_bias=sizedict['sourceFollower_vref']['m_bias']
        m_in=sizedict['sourceFollower_vref']['m_in']
        m_ofst=sizedict['sourceFollower_vref']['m_off']
        m_in_dum=sizedict['sourceFollower_vref']['m_in_dum']
        m_bias_dum=sizedict['sourceFollower_vref']['m_bias_dum']
        m_byp=sizedict['sourceFollower_vref']['m_byp']
        m_byp_bias=sizedict['sourceFollower_vref']['m_byp_bias']
        bias_current=sizedict['sourceFollower_vref']['bias_current']

    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)

    sf_origin=np.array([0, 0])

    #source follwer generation
    generate_source_follower(laygen, objectname_pfix='SF0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                             devname_mos_boundary='nmos4_fast_boundary', devname_mos_body='nmos4_fast_center_nf2',
                             devname_mos_dmy='nmos4_fast_dmy_nf2', devname_tap_boundary='ptap_fast_boundary', devname_tap_body='ptap_fast_center_nf2',
                             devname_mos_space_4x='nmos4_fast_space_nf4', devname_mos_space_2x='nmos4_fast_space_nf2', devname_mos_space_1x='nmos4_fast_space',
                             devname_tap_space_4x='ptap_fast_space_nf4', devname_tap_space_2x='ptap_fast_space_nf2', devname_tap_space_1x='ptap_fast_space',
                             m_mir=m_mir, m_bias=m_bias, m_in=m_in,
                             m_ofst=m_ofst, m_bias_dum=m_bias_dum, m_in_dum=m_in_dum, m_byp=m_byp, m_byp_bias=m_byp_bias,
                             bias_current=bias_current, origin=sf_origin)
    laygen.add_template_from_cell()

    laygen.save_template(filename=workinglib+'.yaml', libname=workinglib)

    #SF_vref generation
    cellname = 'sourceFollower_vref'
    print(cellname+" generating")
    mycell_list.append(cellname)

    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)

    sf_origin=np.array([0, 0])

    #source follwer generation
    generate_source_follower_vref(laygen, objectname_pfix='SF0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                             devname_mos_boundary='nmos4_fast_boundary', devname_mos_body='nmos4_fast_center_nf2',
                             devname_mos_dmy='nmos4_fast_dmy_nf2', devname_tap_boundary='ptap_fast_boundary', devname_tap_body='ptap_fast_center_nf2',
                             devname_mos_space_4x='nmos4_fast_space_nf4', devname_mos_space_2x='nmos4_fast_space_nf2', devname_mos_space_1x='nmos4_fast_space',
                             devname_tap_space_4x='ptap_fast_space_nf4', devname_tap_space_2x='ptap_fast_space_nf2', devname_tap_space_1x='ptap_fast_space',
                             m_mir=m_mir, m_bias=m_bias, m_in=m_in,
                             m_ofst=m_ofst, m_bias_dum=m_bias_dum, m_in_dum=m_in_dum, m_byp=m_byp, m_byp_bias=m_byp_bias,
                             origin=sf_origin)
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

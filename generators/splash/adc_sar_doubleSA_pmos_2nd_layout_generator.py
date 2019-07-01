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
    laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12t,
                 refobj0=itap0.elements[0, 0].pins['TAP0'], refobj1=itap0.elements[m-1, 0].pins['TAP1'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12t,
                 refobj0=itap0.elements[0, 0].pins['TAP0'], refobj1=itap0.elements[m-1, 0].pins['TAP1'])
    for i in range(0, m, 2):
        laygen.via(name=None, xy=[0, 1], refobj=itap0.elements[i, 0].pins['TAP0'], gridname=rg12t)
        laygen.via(name=None, xy=[0, 0], refobj=itap0.elements[i, 0].pins['TAP1'], gridname=rg12t)
    if m%2==0:
        laygen.via(name=None, xy=[0, 1], refobj=itap0.elements[m-1, 0].pins['TAP1'], gridname=rg12t)
    if double_rail==True: #make 2-track rail
        laygen.route(name=None, xy0=[0, -1], xy1=[0, -1], gridname0=rg12t,
                     refobj0=itap0.elements[0, 0].pins['TAP0'], refobj1=itap0.elements[m-1, 0].pins['TAP1'])
        for i in range(0, m, 2):
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

def generate_diff_mos_ofst(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, devname_mos_boundary, devname_mos_body,
                      devname_mos_dmy, m=1, m_ofst=2, m_dmy=0, origin=np.array([0,0])):
    """generate an analog differential mos structure with dummmies """
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    # placement
    if not m_dmy==0:
        imbl0 = laygen.place("I" + objectname_pfix + 'BL0', devname_mos_boundary, pg, xy=origin)
        imdmyl0 = laygen.relplace("I" + objectname_pfix + 'DMYL0', devname_mos_body, pg, imbl0.name, shape=np.array([m_dmy, 1]))
        imofstl0 = laygen.relplace("I" + objectname_pfix + 'OFST0', devname_mos_body, pg, imdmyl0.name, shape=np.array([m_ofst, 1]))
        iml0 = laygen.relplace("I" + objectname_pfix + '0', devname_mos_body, pg, imofstl0.name, shape=np.array([m, 1]))
        imr0 = laygen.relplace("I" + objectname_pfix + '1', devname_mos_body, pg, iml0.name, shape=np.array([m, 1]), transform='MY')
        imofstr0 = laygen.relplace("I" + objectname_pfix + 'OFST1', devname_mos_body, pg, imr0.name, shape=np.array([m_ofst, 1]), transform='MY')
        imdmyr0 = laygen.relplace("I" + objectname_pfix + 'DMYR0', devname_mos_body, pg, imofstr0.name, shape=np.array([m_dmy, 1]), transform='MY')
        imbr0 = laygen.relplace("I" + objectname_pfix + 'BR0', devname_mos_boundary, pg, imdmyr0.name, transform='MY')
    else:
        imbl0 = laygen.place("I" + objectname_pfix + 'BL0', devname_mos_boundary, pg, xy=origin)
        imdmyl0 = None
        imofstl0 = laygen.relplace("I" + objectname_pfix + '0', devname_mos_body, pg, imbl0.name, shape=np.array([m_ofst, 1]))
        iml0 = laygen.relplace("I" + objectname_pfix + '0', devname_mos_body, pg, imofstl0.name, shape=np.array([m, 1]))
        imr0 = laygen.relplace("I" + objectname_pfix + '1', devname_mos_body, pg, iml0.name, shape=np.array([m, 1]), transform='MY')
        imofstr0 = laygen.relplace("I" + objectname_pfix + '1', devname_mos_body, pg, imr0.name, shape=np.array([m_ofst, 1]), transform='MY')
        imdmyr0 = None
        imbr0 = laygen.relplace("I" + objectname_pfix + 'BR0', devname_mos_boundary, pg, imofstr0.name, transform='MY')

    #route
    #gate
    rgl0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=iml0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                      refinstname1=iml0.name, refpinname1='G0', refinstindex1=np.array([m-1, 0])
                      )
    rgr0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imr0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                      refinstname1=imr0.name, refpinname1='G0', refinstindex1=np.array([m-1, 0])
                      )
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=iml0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=imr0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #gate_ofst
    '''
    rgofstl0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imofstl0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                      refinstname1=imofstl0.name, refpinname1='G0', refinstindex1=np.array([m_ofst-1, 0])
                      )
    rgofstr0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imofstr0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                      refinstname1=imofstr0.name, refpinname1='G0', refinstindex1=np.array([m_ofst-1, 0])
                      )
    for i in range(m_ofst):
        laygen.via(None, np.array([0, 0]), refinstname=imofstl0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=imofstr0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    '''
    #drain
    rdl0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                      refinstname0=imofstl0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                      refinstname1=iml0.name, refpinname1='D0', refinstindex1=np.array([m-1, 0])
                      )
    rdr0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                      refinstname0=imr0.name, refpinname0='D0', refinstindex0=np.array([m-1, 0]),
                      refinstname1=imofstr0.name, refpinname1='D0', refinstindex1=np.array([0, 0])
                      )
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=iml0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=imr0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    '''
    for i in range(m_ofst):
        laygen.via(None, np.array([0, 1]), refinstname=imofstl0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=imofstr0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    '''
    #source
    rs0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imofstl0.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                      refinstname1=imofstr0.name, refpinname1='S0', refinstindex1=np.array([0, 0])
                      )
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=iml0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=imr0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=iml0.name, refpinname='S1', refinstindex=np.array([m - 1, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=imr0.name, refpinname='S1', refinstindex=np.array([m - 1, 0]), gridname=rg_m1m2)
    '''
    for i in range(m_ofst):
        laygen.via(None, np.array([0, 0]), refinstname=imofstl0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=imofstr0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=imofstl0.name, refpinname='S1', refinstindex=np.array([m_ofst - 1, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=imofstr0.name, refpinname='S1', refinstindex=np.array([m_ofst - 1, 0]), gridname=rg_m1m2)
    '''
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
                      refinstname0=imdmyr0.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                      refinstname1=imdmyr0.name, refpinname1='S0', refinstindex1=np.array([m_dmy-1, 0])
                      )
        for i in range(m_dmy):
            laygen.via(None, np.array([0, 1]), refinstname=imdmyl0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
            laygen.via(None, np.array([0, 1]), refinstname=imdmyr0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
            laygen.via(None, np.array([0, 0]), refinstname=imdmyl0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
            laygen.via(None, np.array([0, 0]), refinstname=imdmyr0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)

    return [imbl0, imdmyl0, imofstl0, iml0, imr0, imofstr0, imdmyr0, imbr0]

def generate_clkdiffpair_ofst(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m1m2_thick, routing_grid_m2m3,
                         devname_mos_boundary, devname_mos_body, devname_mos_dmy, devname_tap_boundary, devname_tap_body,
                         m_in=2, m_ofst=2, m_in_dmy=1, m_clkh=2, m_clkh_dmy=1, m_tap=12, origin=np.array([0, 0])):
    """generate a clocked differential pair with offset"""
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m1m2_thick = routing_grid_m1m2_thick
    rg_m2m3 = routing_grid_m2m3

    m_clk=m_clkh*2
    [itapbl0, itap0, itapbr0] = generate_tap(laygen, objectname_pfix=objectname_pfix+'NTAP0', placement_grid=pg,
                                             routing_grid_m1m2_thick=rg_m1m2_thick,
                                             devname_tap_boundary=devname_tap_boundary, devname_tap_body=devname_tap_body,
                                             m=m_tap, double_rail=True, origin=origin)
    diffpair_origin = laygen.get_inst_xy(itapbl0.name, pg) + laygen.get_template_size(itapbl0.cellname, pg) * np.array([0, 1])
    #[ickbl0, ickdmyl0, ick0, ickdmyr0, ickbr0]=generate_mos(laygen, objectname_pfix +'CK0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
    #                                    devname_mos_boundary=devname_mos_boundary, devname_mos_body=devname_mos_body,
    #                                    devname_mos_dmy=devname_mos_dmy, m=m_clkh*2, m_dmy=m_clkh_dmy, origin=diffpair_origin)
    #in_origin=laygen.get_inst_xy(ickbl0.name, pg)+laygen.get_template_size(ickbl0.cellname, pg)*np.array([0,1])
    [iinbl0, iindmyl0, iofstl0, iinl0, iinr0, iofstr0, iindmyr0, iinbr0] = \
        generate_diff_mos_ofst(laygen, objectname_pfix+'IN0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                          devname_mos_boundary=devname_mos_boundary, devname_mos_body=devname_mos_body,
                          devname_mos_dmy=devname_mos_dmy, m=m_in, m_ofst=m_ofst, m_dmy=m_in_dmy, origin=diffpair_origin)
    #tap to cs
    for i in range(m_in*2):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=iinl0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=itap0.name, refpinname1='TAP0', refinstindex1=np.array([0, 0]),
                     direction='y'
                     )
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=iinl0.name, refpinname0='S1', refinstindex0=np.array([m_in*2-1, 0]),
                     refinstname1=itap0.name, refpinname1='TAP0', refinstindex1=np.array([0, 0]),
                     direction='y'
                     )
    #cs to in (tail)
    '''
    for i in range(min(m_clkh-1, m_in-1)):
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                     refinstname0=iinl0.name, refpinname0='D0', refinstindex0=np.array([m_in-i-1, 0]),
                     refinstname1=ick0.name, refpinname1='D0', refinstindex1=np.array([m_clkh-i-1, 0]),
                     via0=[[0, 0]], via1=[[0, 0]],
                     )
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                     refinstname0=iinr0.name, refpinname0='D0', refinstindex0=np.array([m_in-i-1, 0]),
                     refinstname1=ick0.name, refpinname1='D0', refinstindex1=np.array([m_clkh+i, 0]),
                     via0=[[0, 0]], via1=[[0, 0]],
                     )
    '''
    #biascap
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0+0, 0]), gridname0=rg_m1m2,
                 refinstname0=iindmyl0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=iindmyl0.name, refpinname1='G0', refinstindex1=np.array([m_in_dmy-1, 0])
                 )
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0+0, 0]), gridname0=rg_m1m2,
                 refinstname0=iindmyr0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=iindmyr0.name, refpinname1='G0', refinstindex1=np.array([m_in_dmy-1, 0])
                 )
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=iindmyl0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=iindmyl0.name, refpinname1='D0', refinstindex1=np.array([0, 0])
                 )
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=iindmyl0.name, refpinname0='G0', refinstindex0=np.array([m_in_dmy-1, 0]),
                 refinstname1=iindmyl0.name, refpinname1='D0', refinstindex1=np.array([m_in_dmy-1, 0])
                 )
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=iindmyr0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=iindmyr0.name, refpinname1='D0', refinstindex1=np.array([0, 0])
                 )
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=iindmyr0.name, refpinname0='G0', refinstindex0=np.array([m_in_dmy-1, 0]),
                 refinstname1=iindmyr0.name, refpinname1='D0', refinstindex1=np.array([m_in_dmy-1, 0])
                 )
    for i in range(0, m_in_dmy-0):
        laygen.via(None, np.array([0, 0]), refinstname=iindmyl0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=iindmyr0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #clock
    #dmy route
    #for i in range(min(m_clkh_dmy, m_in_dmy)):
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=iindmyl0.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=itap0.name, refpinname1='TAP0', refinstindex1=np.array([0, 0])
                 )
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=iindmyl0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=itap0.name, refpinname1='TAP0', refinstindex1=np.array([1, 0])
                 )
    '''
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 2]), xy1=np.array([-1, 2]), gridname0=rg_m1m2,
                 refinstname0=ickdmyl0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=ickdmyl0.name, refpinname1='D0', refinstindex1=np.array([0, 0])
                 )
    '''
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=iindmyr0.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                 refinstname1=itap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                 )
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=iindmyr0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=itap0.name, refpinname1='TAP0', refinstindex1=np.array([m_tap-1, 0])
                 )
    '''
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 2]), xy1=np.array([1, 2]), gridname0=rg_m1m2,
                 refinstname0=ickdmyr0.name, refpinname0='D0', refinstindex0=np.array([m_clkh_dmy-1, 0]),
                 refinstname1=ickdmyr0.name, refpinname1='D0', refinstindex1=np.array([m_clkh_dmy-1, 0])
                 )
    laygen.via(None, np.array([0, 0]), refinstname=ickdmyl0.name, refpinname='S0', refinstindex=np.array([0, 0]), gridname=rg_m1m2)
    #laygen.via(None, np.array([0, 0]), refinstname=ickdmyl0.name, refpinname='D0', refinstindex=np.array([0, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=ickdmyr0.name, refpinname='S1', refinstindex=np.array([0, 0]), gridname=rg_m1m2)
    #laygen.via(None, np.array([0, 0]), refinstname=ickdmyr0.name, refpinname='D0', refinstindex=np.array([0, 0]), gridname=rg_m1m2)
    '''
    #return [itapbl0, itap0, itapbr0, ickbl0, ick0, ickbr0, iinbl0, iindmyl0, iofstl0, iinl0, iinr0, iofstr0, iindmyr0, iinbr0]
    return [itapbl0, itap0, itapbr0, iinbl0, iindmyl0, iofstl0, iinl0, iinr0, iofstr0, iindmyr0, iinbr0]

def generate_salatch_regen(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m1m2_thick,
                   routing_grid_m2m3, routing_grid_m3m4,
                   devname_nmos_boundary, devname_nmos_body, devname_nmos_dmy,
                   devname_pmos_boundary, devname_pmos_body, devname_pmos_dmy,
                   devname_ptap_boundary, devname_ptap_body, devname_ntap_boundary, devname_ntap_body,
                   m_rgnp=2, m_rgnp_dmy=1, m_rstp=1, m_tap=12, m_buf=1, origin=np.array([0, 0])):
    """generate regenerative stage of SAlatch"""
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m1m2_thick = routing_grid_m1m2_thick
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4

    #m_rgnn = m_rgnp - 2 * m_rstp + 1
    m_rgnn = m_rgnp + 2 * m_rstp - 1
    m_rgnn_dmy = m_rgnp_dmy

    #tap
    [itapbln0, itapn0, itapbrn0] = generate_tap(laygen, objectname_pfix=objectname_pfix+'NTAP0', placement_grid=pg,
                                             routing_grid_m1m2_thick=rg_m1m2_thick,
                                             devname_tap_boundary=devname_ptap_boundary, devname_tap_body=devname_ptap_body,
                                             m=m_tap, origin=origin)
    rgnbody_origin = laygen.get_inst_xy(itapbln0.name, pg) + laygen.get_template_size(itapbln0.cellname, pg) * np.array([0, 1])
    #nmos row
    if not m_rgnn_dmy==0:
        imbln0 = laygen.place("I" + objectname_pfix + 'BLN0', devname_nmos_boundary, pg, xy=rgnbody_origin)
        imbufln0 = laygen.relplace("I" + objectname_pfix + 'BUFLN0', devname_nmos_body, pg, imbln0.name, shape=np.array([m_buf, 1]))
        imdmyln0 = laygen.relplace("I" + objectname_pfix + 'DMYLN0', devname_nmos_dmy, pg, imbufln0.name, shape=np.array([m_rgnn_dmy, 1]))
        imln0 = laygen.relplace("I" + objectname_pfix + 'LN0', devname_nmos_body, pg, imdmyln0.name, shape=np.array([m_rgnn, 1]))
        imln1 = laygen.relplace("I" + objectname_pfix + 'LN1', devname_nmos_dmy, pg, imln0.name)
        imrn1 = laygen.relplace("I" + objectname_pfix + 'RN1', devname_nmos_dmy, pg, imln1.name, transform='MY')
        imrn0 = laygen.relplace("I" + objectname_pfix + 'RN0', devname_nmos_body, pg, imrn1.name, shape=np.array([m_rgnn, 1]), transform='MY')
        imdmyrn0 = laygen.relplace("I" + objectname_pfix + 'DMYRN0', devname_nmos_dmy, pg, imrn0.name, shape=np.array([m_rgnn_dmy, 1]), transform='MY')
        imbufrn0 = laygen.relplace("I" + objectname_pfix + 'BUFRN0', devname_nmos_body, pg, imdmyrn0.name, shape=np.array([m_buf, 1]), transform='MY')
        imbrn0 = laygen.relplace("I" + objectname_pfix + 'BRN0', devname_nmos_boundary, pg, imbufrn0.name, transform='MY')
    else:
        imbln0 = laygen.place("I" + objectname_pfix + 'BLN0', devname_nmos_boundary, pg, xy=origin)
        imbufln0 = laygen.relplace("I" + objectname_pfix + 'BUFLN0', devname_nmos_body, pg, imbln0.name, shape=np.array([m_buf, 1]))
        imdmyln0 = None
        imln0 = laygen.relplace("I" + objectname_pfix + 'LN0', devname_nmos_body, pg, imbufln0.name, shape=np.array([m_rgnn, 1]))
        imln1 = laygen.relplace("I" + objectname_pfix + 'LN1', devname_nmos_dmy, pg, imln0.name)
        imrn1 = laygen.relplace("I" + objectname_pfix + 'RN1', devname_nmos_dmy, pg, imln1.name, transform='MY')
        imrn0 = laygen.relplace("I" + objectname_pfix + 'RN0', devname_nmos_body, pg, imrn1.name, shape=np.array([m_rgnn, 1]), transform='MY')
        imdmyrn0 = None
        imbufrn0 = laygen.relplace("I" + objectname_pfix + 'BUFRN0', devname_nmos_body, pg, imrn0.name, shape=np.array([m_buf, 1]), transform='MY')
        imbrn0 = laygen.relplace("I" + objectname_pfix + 'BRN0', devname_nmos_boundary, pg, imbufrn0.name, transform='MY')
    #pmos row
    if not m_rgnp_dmy==0:
        imblp0 = laygen.relplace("I" + objectname_pfix + 'BLP0', devname_pmos_boundary, pg, imbln0.name, direction='top', transform='MX')
        imbuflp0 = laygen.relplace("I" + objectname_pfix + 'BUFLP0', devname_pmos_body, pg, imblp0.name, shape=np.array([m_buf, 1]), transform='MX')
        imdmylp0 = laygen.relplace("I" + objectname_pfix + 'DMYLP0', devname_pmos_body, pg, imbuflp0.name, shape=np.array([m_rgnp_dmy, 1]), transform='MX')
        imlp0 = laygen.relplace("I" + objectname_pfix + 'LP0', devname_pmos_body, pg, imdmylp0.name, shape=np.array([m_rgnp, 1]), transform='MX')
        imrstlp0 = laygen.relplace("I" + objectname_pfix + 'RSTLP0', devname_pmos_body, pg, imlp0.name, shape=np.array([m_rstp, 1]), transform='MX')
        imrstlp1 = laygen.relplace("I" + objectname_pfix + 'RSTLP1', devname_pmos_body, pg, imrstlp0.name, shape=np.array([m_rstp, 1]), transform='MX')
        imrstrp1 = laygen.relplace("I" + objectname_pfix + 'RSTRP1', devname_pmos_body, pg, imrstlp1.name, shape=np.array([m_rstp, 1]), transform='R180')
        imrstrp0 = laygen.relplace("I" + objectname_pfix + 'RSTRP0', devname_pmos_body, pg, imrstrp1.name, shape=np.array([m_rstp, 1]), transform='R180')
        imrp0 = laygen.relplace("I" + objectname_pfix + 'RP0', devname_pmos_body, pg, imrstrp0.name, shape=np.array([m_rgnp, 1]), transform='R180')
        imdmyrp0 = laygen.relplace("I" + objectname_pfix + 'DMYRP0', devname_pmos_body, pg, imrp0.name, shape=np.array([m_rgnp_dmy, 1]), transform='R180')
        imbufrp0 = laygen.relplace("I" + objectname_pfix + 'BUFRP0', devname_pmos_body, pg, imdmyrp0.name, shape=np.array([m_buf, 1]), transform='R180')
        imbrp0 = laygen.relplace("I" + objectname_pfix + 'BRP0', devname_pmos_boundary, pg, imbufrp0.name, transform='R180')
    else:
        imblp0 = laygen.relplace("I" + objectname_pfix + 'BLP0', devname_pmos_boundary, pg, imbln0.name, direction='top', transform='MX')
        imbuflp0 = laygen.relplace("I" + objectname_pfix + 'BUFLP0', devname_pmos_body, pg, imblp0.name, shape=np.array([m_buf, 1]), transform='MX')
        imdmylp0 = None
        imlp0 = laygen.relplace("I" + objectname_pfix + 'LP0', devname_pmos_body, pg, imbuflp0.name, shape=np.array([m_rgnp, 1]), transform='MX')
        imrstlp0 = laygen.relplace("I" + objectname_pfix + 'RSTLP0', devname_pmos_body, pg, imlp0.name, shape=np.array([m_rstp, 1]), transform='MX')
        imrstlp1 = laygen.relplace("I" + objectname_pfix + 'RSTLP1', devname_pmos_body, pg, imrstlp0.name, shape=np.array([m_rstp, 1]), transform='MX')
        imrstrp1 = laygen.relplace("I" + objectname_pfix + 'RSTRP1', devname_pmos_body, pg, imrstlp1.name, shape=np.array([m_rstp, 1]), transform='R180')
        imrstrp0 = laygen.relplace("I" + objectname_pfix + 'RSTRP0', devname_pmos_body, pg, imrstrp1.name, shape=np.array([m_rstp, 1]), transform='R180')
        imrp0 = laygen.relplace("I" + objectname_pfix + 'RP0', devname_pmos_body, pg, imrstrp0.name, shape=np.array([m_rgnp, 1]), transform='R180')
        imdmyrp0 = None
        imbufrp0 = laygen.relplace("I" + objectname_pfix + 'BUFRP0', devname_pmos_body, pg, imrp0.name, shape=np.array([m_buf, 1]), transform='R180')
        imbrp0 = laygen.relplace("I" + objectname_pfix + 'BRP0', devname_pmos_boundary, pg, imbufrp0.name, transform='R180')
    tap_origin = laygen.get_inst_xy(imblp0.name, pg) + laygen.get_template_size(devname_ntap_boundary, pg) * np.array([0, 1])
    [itapbl0, itap0, itapbr0] = generate_tap(laygen, objectname_pfix=objectname_pfix+'PTAP0', placement_grid=pg, routing_grid_m1m2_thick=rg_m1m2_thick,
                                             devname_tap_boundary=devname_ntap_boundary, devname_tap_body=devname_ntap_body,
                                             m=m_tap, double_rail=True, origin=tap_origin, transform='MX')
    #tap to pmos
    for i in range(m_rgnp+1):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imlp0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imlp0.name, refpinname1='S0', refinstindex1=np.array([i, 0]),
                     direction='y'
                     )
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imrp0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imrp0.name, refpinname1='S0', refinstindex1=np.array([i, 0]),
                     direction='y'
                     )
        laygen.via(None, np.array([0, -1]), refinstname=imlp0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, -1]), refinstname=imrp0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    for i in range(m_rstp+1):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imrstlp0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imrstlp0.name, refpinname1='S0', refinstindex1=np.array([i, 0]),
                     direction='y'
                     )
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imrstlp1.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imrstlp1.name, refpinname1='S0', refinstindex1=np.array([i, 0]),
                     direction='y'
                     )
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imrstrp1.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imrstrp1.name, refpinname1='S0', refinstindex1=np.array([i, 0]),
                     direction='y'
                     )
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imrstrp0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imrstrp0.name, refpinname1='S0', refinstindex1=np.array([i, 0]),
                     direction='y'
                     )
        laygen.via(None, np.array([0, -1]), refinstname=imrstlp0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, -1]), refinstname=imrstrp0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, -1]), refinstname=imrstlp1.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, -1]), refinstname=imrstrp1.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #gate-n
    rgln0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imln0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                      refinstname1=imln0.name, refpinname1='G0', refinstindex1=np.array([m_rgnn-1, 0])
                      )
    for i in range(m_rgnn):
        laygen.via(None, np.array([0, 0]), refinstname=imln0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    rgrn0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imrn0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                      refinstname1=imrn0.name, refpinname1='G0', refinstindex1=np.array([m_rgnn-1, 0])
                      )
    for i in range(m_rgnn):
        laygen.via(None, np.array([0, 0]), refinstname=imrn0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)

    #gate-p
    rglp0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imlp0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                      refinstname1=imlp0.name, refpinname1='G0', refinstindex1=np.array([m_rgnp-1, 0])
                      )
    for i in range(m_rgnp):
        laygen.via(None, np.array([0, 0]), refinstname=imlp0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    rgrp0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imrp0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                      refinstname1=imrp0.name, refpinname1='G0', refinstindex1=np.array([m_rgnp-1, 0])
                      )
    for i in range(m_rgnp):
        laygen.via(None, np.array([0, 0]), refinstname=imrp0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #gate-pn vertical
    rglv0=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 0]), gridname0=rg_m2m3,
                      refinstname0=imlp0.name, refpinname0='G0', refinstindex0=np.array([m_rgnp-1, 0]), via0=[[0, 0]],
                      refinstname1=imln0.name, refpinname1='G0', refinstindex1=np.array([m_rgnp-1, 0]), via1=[[0, 0]]
                      )
    rgrv0=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 0]), gridname0=rg_m2m3,
                      refinstname0=imrp0.name, refpinname0='G0', refinstindex0=np.array([m_rgnp-1, 0]), via0=[[0, 0]],
                      refinstname1=imrn0.name, refpinname1='G0', refinstindex1=np.array([m_rgnp-1, 0]), via1=[[0, 0]],
                      )

    #drain-pn vertical
    rdlv0=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                      refinstname0=imlp0.name, refpinname0='D0', refinstindex0=np.array([-1, 0]), via0=[[0, 0]],
                      refinstname1=imln0.name, refpinname1='D0', refinstindex1=np.array([-1, 0]), via1=[[0, 0]],
                      )
    rdrv0=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                      refinstname0=imrp0.name, refpinname0='D0', refinstindex0=np.array([-1, 0]), via0=[[0, 0]],
                      refinstname1=imrn0.name, refpinname1='D0', refinstindex1=np.array([-1, 0]), via1=[[0, 0]],
                      )
    for i in range(m_rgnp):
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                    refobj0=imlp0, refpinname0='D0', refobjindex0=np.array([i, 0]), via0=[[0, 0]],
                    refobj1=imln0, refpinname1='D0', refobjindex1=np.array([i, 0]), via1=[[0, 0]],
                    )
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                    refobj0=imrp0, refpinname0='D0', refobjindex0=np.array([i, 0]), via0=[[0, 0]],
                    refobj1=imrn0, refpinname1='D0', refobjindex1=np.array([i, 0]), via1=[[0, 0]],
                    )
    for i in range(m_rstp):
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                    refobj0=imrstlp0, refpinname0='D0', refobjindex0=np.array([i, 0]), via0=[[0, 0]],
                    refobj1=imln0, refpinname1='D0', refobjindex1=np.array([i+m_rgnp, 0]), via1=[[0, 0]],
                    )
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                    refobj0=imrstrp0, refpinname0='D0', refobjindex0=np.array([i, 0]), via0=[[0, 0]],
                    refobj1=imrn0, refpinname1='D0', refobjindex1=np.array([i+m_rgnp, 0]), via1=[[0, 0]],
                    )

    #gate-rst
    rgrstopp0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imrstlp0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                      refinstname1=imrstlp0.name, refpinname1='G0', refinstindex1=np.array([m_rstp-1, 0])
                      )
    rgrstintpp0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imrstlp1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                      refinstname1=imrstlp1.name, refpinname1='G0', refinstindex1=np.array([m_rstp-1, 0])
                      )
    rgrstomp0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imrstrp0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                      refinstname1=imrstrp0.name, refpinname1='G0', refinstindex1=np.array([m_rstp-1, 0])
                      )
    rgrstintmp0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imrstrp1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                      refinstname1=imrstrp1.name, refpinname1='G0', refinstindex1=np.array([m_rstp-1, 0])
                      )
    #laygen.boundary_pin_from_rect(rgrstintpp0, gridname=rg_m2m3, name='INTP', layer=laygen.layers['pin'][2], size=2, direction='left')
    #laygen.boundary_pin_from_rect(rgrstintmp0, gridname=rg_m2m3, name='INTM', layer=laygen.layers['pin'][2], size=2, direction='left')
    laygen.boundary_pin_from_rect(rgrstopp0, gridname=rg_m2m3, name='OP', layer=laygen.layers['pin'][2], size=2, direction='left')
    laygen.boundary_pin_from_rect(rgrstomp0, gridname=rg_m2m3, name='OM', layer=laygen.layers['pin'][2], size=2, direction='right')
    for i in range(m_rstp):
        laygen.via(None, np.array([0, 0]), refinstname=imrstlp0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=imrstlp1.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=imrstrp1.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=imrstrp0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #drain-p
    rdlp0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imlp0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                      refinstname1=imlp0.name, refpinname1='D0', refinstindex1=np.array([m_rgnp+m_rstp-1, 0])
                      )
    for i in range(m_rgnp):
        laygen.via(None, np.array([0, 0]), refinstname=imlp0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    for i in range(m_rstp):
        laygen.via(None, np.array([0, 0]), refinstname=imrstlp0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    rdrp0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imrp0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                      refinstname1=imrp0.name, refpinname1='D0', refinstindex1=np.array([m_rgnp+m_rstp-1, 0])
                      )
    for i in range(m_rgnp):
        laygen.via(None, np.array([0, 0]), refinstname=imrp0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    for i in range(m_rstp):
        laygen.via(None, np.array([0, 0]), refinstname=imrstrp0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #cross-coupled route and via
    xyg0=laygen.get_rect_xy(rglv0.name, rg_m3m4, sort=True)[0]
    xyd0=laygen.get_rect_xy(rdlv0.name, rg_m3m4, sort=True)[0]
    xyg1=laygen.get_rect_xy(rgrv0.name, rg_m3m4, sort=True)[0]
    xyd1=laygen.get_rect_xy(rdrv0.name, rg_m3m4, sort=True)[0]
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xyd0[0], xyg0[1]]), xy1=np.array([xyd1[0], xyg0[1]]), gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xyd0[0], xyg0[1]+1]), xy1=np.array([xyd1[0], xyg0[1]+1]), gridname0=rg_m3m4)
    laygen.via(None, np.array([xyg0[0], xyg0[1]]), gridname=rg_m3m4)
    laygen.via(None, np.array([xyd1[0], xyg0[1]]), gridname=rg_m3m4)
    laygen.via(None, np.array([xyd0[0], xyg0[1]+1]), gridname=rg_m3m4)
    laygen.via(None, np.array([xyg1[0], xyg0[1]+1]), gridname=rg_m3m4)
    #source/drain-n
    rdln0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                      refinstname0=imln0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                      refinstname1=imln0.name, refpinname1='D0', refinstindex1=np.array([m_rgnn-1, 0])
                      )
    for i in range(m_rgnn):
        laygen.via(None, np.array([0, 1]), refinstname=imln0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    rdrn0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2, 1]), xy1=np.array([0, 1]), gridname0=rg_m1m2,
                      refinstname0=imrn0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                      refinstname1=imrn0.name, refpinname1='D0', refinstindex1=np.array([m_rgnn-1, 0])
                      )
    for i in range(m_rgnn):
        laygen.via(None, np.array([0, 1]), refinstname=imrn0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    rsln0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imln0.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                      refinstname1=imln1.name, refpinname1='S0', refinstindex1=np.array([0, 0])
                      )
    for i in range(m_rgnn):
        laygen.via(None, np.array([0, 0]), refinstname=imln0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=imln1.name, refpinname='S0', refinstindex=np.array([0, 0]), gridname=rg_m1m2)
    rsrn0=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                      refinstname0=imrn0.name, refpinname0='S0', refinstindex0=np.array([0, 0]),
                      refinstname1=imrn1.name, refpinname1='S0', refinstindex1=np.array([0, 0])
                      )
    for i in range(m_rgnn):
        laygen.via(None, np.array([0, 0]), refinstname=imrn0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.via(None, np.array([0, 0]), refinstname=imrn1.name, refpinname='S0', refinstindex=np.array([0, 0]), gridname=rg_m1m2)
    #tap to rgnn
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2, #gridname1=rg_m1m2_pin,
                     refinstname0=imln1.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=itapn0.name, refpinname1='TAP0', refinstindex1=np.array([0, 0]),
                     direction='y'
                     )
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2, #gridname1=rg_m1m2_pin,
                     refinstname0=imln1.name, refpinname0='S1', refinstindex0=np.array([0, 0]),
                     refinstname1=itapn0.name, refpinname1='TAP0', refinstindex1=np.array([0, 0]),
                     direction='y'
                     )
    laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2, #gridname1=rg_m1m2_pin,
                     refinstname0=imrn1.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                     refinstname1=itapn0.name, refpinname1='TAP0', refinstindex1=np.array([0, 0]),
                     direction='y'
                     )
    #laygen.via(None, np.array([0, -1]), refinstname=imln1.name, refpinname='D0', refinstindex=np.array([0, 0]), gridname=rg_m1m2_pin)
    #laygen.via(None, np.array([0, -1]), refinstname=imln1.name, refpinname='S1', refinstindex=np.array([0, 0]), gridname=rg_m1m2_pin)
    #laygen.via(None, np.array([0, -1]), refinstname=imrn1.name, refpinname='D0', refinstindex=np.array([0, 0]), gridname=rg_m1m2_pin)
    #buf tap to rgnn
    for i in range(m_buf):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2, 
                     refinstname0=imbufln0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=itapn0.name, refpinname1='TAP0', refinstindex1=np.array([i, 0]), direction='y')
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2, 
                     refinstname0=imbufrn0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=itapn0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-i, 0]), direction='y')
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imbuflp0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imbuflp0.name, refpinname1='S0', refinstindex1=np.array([i, 0]), direction='y')
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imbufrp0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imbufrp0.name, refpinname1='S0', refinstindex1=np.array([i, 0]), direction='y')
    for i in range(m_buf):
        laygen.via(None, np.array([0, -1]), refinstname=imbuflp0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, -1]), refinstname=imbufrp0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #buf-gate
    for i in range(m_buf):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imbufln0.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=imbuflp0.name, refpinname1='G0', refinstindex1=np.array([i, 0]), direction='y')
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=imbufrn0.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=imbufrp0.name, refpinname1='G0', refinstindex1=np.array([i, 0]), direction='y')
    #buf-gate(horizontal)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([2*m_rgnn_dmy, 0]), gridname0=rg_m2m3,
                 refinstname0=imbufln0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbufln0.name, refpinname1='G0', refinstindex1=np.array([m_buf-1, 0]), via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([2*m_rgnn_dmy, 0]), gridname0=rg_m2m3,
                 refinstname0=imbufrn0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbufrn0.name, refpinname1='G0', refinstindex1=np.array([m_buf-1, 0]), via1=[[0, 0]])
    for i in range(m_buf):
        laygen.via(None, np.array([0, 0]), refinstname=imbufln0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=imbufrn0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #buf-drain
    for i in range(m_buf):
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                     refinstname0=imbufln0.name, refpinname0='D0', refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=imbuflp0.name, refpinname1='D0', refinstindex1=np.array([i, 0]), via1=[[0, 0]])
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                     refinstname0=imbufrn0.name, refpinname0='D0', refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=imbufrp0.name, refpinname1='D0', refinstindex1=np.array([i, 0]), via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=imbufln0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbufln0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]),
                 endstyle0="extend", endstyle1="extend")
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                 refinstname0=imbufrn0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbufrn0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]),
                 endstyle0="extend", endstyle1="extend")
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=imbuflp0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbuflp0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=imbufrp0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbufrp0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]))
    for i in range(m_buf):
        laygen.via(None, np.array([0, 0]), refinstname=imbufln0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=imbuflp0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=imbufrn0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=imbufrp0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #dmy-p
    for i in range(m_rgnp_dmy):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imdmylp0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imdmylp0.name, refpinname1='S0', refinstindex1=np.array([i, 0]),
                     direction='y'
                     )
        laygen.via(None, np.array([0, 0]), refinstname=imdmylp0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=imdmylp0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, -1]), gridname0=rg_m1m2,
                     refinstname0=imdmyrp0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=imdmyrp0.name, refpinname1='S0', refinstindex1=np.array([i, 0]),
                     direction='y'
                     )
        laygen.via(None, np.array([0, 0]), refinstname=imdmyrp0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=imdmyrp0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)

        laygen.via(None, np.array([0, -1]), refinstname=imdmylp0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, -1]), refinstname=imdmyrp0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #dmy-n
    for i in range(m_rgnn_dmy):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2, #gridname1=rg_m1m2_pin,
                     refinstname0=imdmyln0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=itapn0.name, refpinname1='TAP0', refinstindex1=np.array([i, 0]),
                     direction='y'
                     )
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2, #gridname1=rg_m1m2_pin,
                     refinstname0=imdmyln0.name, refpinname0='D0', refinstindex0=np.array([i, 0]),
                     refinstname1=itapn0.name, refpinname1='TAP0', refinstindex1=np.array([i+1, 0]),
                     direction='y'
                     )
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2, #gridname1=rg_m1m2_pin,
                     refinstname0=imdmyrn0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=itapn0.name, refpinname1='TAP0', refinstindex1=np.array([m_tap-i, 0]),
                     direction='y'
                     )
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2, #gridname1=rg_m1m2_pin,
                     refinstname0=imdmyrn0.name, refpinname0='D0', refinstindex0=np.array([i, 0]),
                     refinstname1=itapn0.name, refpinname1='TAP0', refinstindex1=np.array([m_tap-i, 0]),
                     direction='y'
                     )
        #laygen.via(None, np.array([0, -1]), refinstname=imdmyln0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2_pin)
        #laygen.via(None, np.array([0, -1]), refinstname=imdmyln0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2_pin)
        #laygen.via(None, np.array([0, -1]), refinstname=imdmyrn0.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2_pin)
        #laygen.via(None, np.array([0, -1]), refinstname=imdmyrn0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2_pin)
    return [itapbln0, itapn0, itapbrn0, imbln0, imbufln0, imdmyln0, imln0, imln1, imrn1, imrn0, imdmyrn0, imbufrn0, imbrn0,
            imblp0, imbuflp0, imdmylp0, imlp0, imrstlp0, imrstlp1, imrstrp1, imrstrp0, imrp0, imdmyrp0, imbufrp0, imbrp0,
            itapbl0, itap0, itapbr0]

def generate_salatch_pmos(laygen, objectname_pfix, placement_grid,
                          routing_grid_m1m2, routing_grid_m1m2_thick, routing_grid_m2m3,
                          routing_grid_m2m3_thick, routing_grid_m3m4, routing_grid_m4m5,
                          devname_ntap_boundary, devname_ntap_body,
                          devname_pmos_boundary, devname_pmos_body, devname_pmos_dmy,
                          devname_nmos_boundary, devname_nmos_body, devname_nmos_dmy,
                          devname_ptap_boundary, devname_ptap_body,
                          m_in=4, m_ofst=2, m_clkh=2, m_rgnn=2, m_rstn=1, m_buf=1, num_vert_pwr=20, origin=np.array([0, 0])):
    """generate strongarm latch"""
    #internal parameters
    #m_tot= max(m_in, m_clkh, m_rgnn + 2*m_rstn + m_buf*(1+4)) + 1 #at least one dummy
    m_tot= max(m_in, m_clkh, m_rgnn + 2*m_rstn + m_buf) + 1 #at least one dummy
    m_tap=m_tot*2*2 #2 for diff, 2 for nf=2
    m_in_dmy = m_tot - m_in
    m_clkh_dmy = m_tot - m_clkh
    #m_rgnn_dmy = m_tot - m_rgnn - m_rstn * 2 - m_buf * (1+4)
    m_rgnn_dmy = m_tot - m_rgnn - m_rstn * 2 - m_buf
    l_clkb_m4=4 #clkb output wire length

    #grids
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m1m2_thick = routing_grid_m1m2_thick
    rg_m2m3 = routing_grid_m2m3
    rg_m2m3_thick = routing_grid_m2m3_thick
    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5

    #offset pair
    [iofsttapbl0, iofsttap0, iofsttapbr0, iofstckbl0, iofstck0, iofstckbr0,
     iofstinbl0, iofstindmyl0, iofstinl0, iofstinr0, iofstindmyr0, iofstinbr0]=\
    [None, None, None, None, None, None,
     None, None, None, None, None, None]
    #generate_clkdiffpair(laygen, objectname_pfix=objectname_pfix+'OFST0', placement_grid=pg,
    #                     routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick, routing_grid_m2m3=rg_m2m3,
    #                     devname_mos_boundary=devname_pmos_boundary, devname_mos_body=devname_pmos_body, devname_mos_dmy=devname_pmos_dmy,
    #                     devname_tap_boundary=devname_ntap_boundary, devname_tap_body=devname_ntap_body,
    #                     m_in=m_in, m_in_dmy=m_in_dmy, m_clkh=m_clkh, m_clkh_dmy=m_clkh_dmy, m_tap=m_tap, origin=origin)

    #main pair
    #mainpair_origin = laygen.get_inst_xy(iofstinbl0.name, pg) + laygen.get_template_size(iofstinbl0.cellname, pg) * np.array([0, 1])
    mainpair_origin = origin
    '''
    [imaintapbl0, imaintap0, imaintapbr0, imainckbl0, imainck0, imainckbr0,
     imaininbl0, imainindmyl0, iofstinl0, imaininl0, imaininr0, iofstinr0, imainindmyr0, imaininbr0]=\
    generate_clkdiffpair_ofst(laygen, objectname_pfix=objectname_pfix+'MAIN0', placement_grid=pg,
                         routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick, routing_grid_m2m3=rg_m2m3,
                         devname_mos_boundary=devname_pmos_boundary, devname_mos_body=devname_pmos_body, devname_mos_dmy=devname_pmos_dmy,
                         devname_tap_boundary=devname_ntap_boundary, devname_tap_body=devname_ntap_body,
                         m_in=m_in, m_ofst=m_ofst, m_in_dmy=m_in_dmy-m_ofst, m_clkh=m_clkh, m_clkh_dmy=m_clkh_dmy, m_tap=m_tap, origin=mainpair_origin)
    '''
    [imaintapbl0, imaintap0, imaintapbr0, 
     imaininbl0, imainindmyl0, iofstinl0, imaininl0, imaininr0, iofstinr0, imainindmyr0, imaininbr0]=\
    generate_clkdiffpair_ofst(laygen, objectname_pfix=objectname_pfix+'MAIN0', placement_grid=pg,
                         routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick, routing_grid_m2m3=rg_m2m3,
                         devname_mos_boundary=devname_nmos_boundary, devname_mos_body=devname_nmos_body, devname_mos_dmy=devname_nmos_dmy,
                         devname_tap_boundary=devname_ptap_boundary, devname_tap_body=devname_ptap_body,
                         m_in=m_in, m_ofst=m_ofst, m_in_dmy=m_in_dmy-m_ofst, m_clkh=m_clkh, m_clkh_dmy=m_clkh_dmy, m_tap=m_tap, origin=mainpair_origin)
    #regen
    regen_origin = laygen.get_inst_xy(imaininbl0.name, pg) + laygen.get_template_size(imaininbl0.cellname, pg) * np.array([0, 1])

    [irgntapbln0, irgntapn0, irgntapbrn0,
     irgnbln0, irgnbufln0, irgndmyln0, irgnln0, irgnln1, irgnrn1, irgnrn0, irgndmyrn0, irgnbufrn0, irgnbrn0,
     irgnblp0, irgnbuflp0, irgndmylp0, irgnlp0, irgnrstlp0, irgnrstlp1, irgnrstrp1, irgnrstrp0, irgnrp0, irgndmyrp0, irgnbufrp0, irgnbrp0,
     irgntapbl0, irgntap0, irgntapbr0]=\
    generate_salatch_regen(laygen, objectname_pfix=objectname_pfix+'RGN0', placement_grid=pg,
                           routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                           devname_nmos_boundary=devname_nmos_boundary, devname_nmos_body=devname_nmos_body, devname_nmos_dmy=devname_nmos_dmy,
                           devname_pmos_boundary=devname_pmos_boundary, devname_pmos_body=devname_pmos_body, devname_pmos_dmy=devname_pmos_dmy,
                           devname_ptap_boundary=devname_ptap_boundary, devname_ptap_body=devname_ptap_body,
                           devname_ntap_boundary=devname_ntap_boundary, devname_ntap_body=devname_ntap_body,
                           m_rgnp=m_rgnn, m_rgnp_dmy=m_rgnn_dmy, m_rstp=m_rstn, m_tap=m_tap, m_buf=m_buf, origin=regen_origin)
    #irgnbuflp1
    #regen-diff pair connections
    for i in range(m_rstn):
        rintm=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                           refinstname0=irgnln1.name, refpinname0='S0', refinstindex0=np.array([-i, 0]), via0=[[0, 0]],
                           refinstname1=irgnrstlp1.name, refpinname1='S0', refinstindex1=np.array([m_rstn-1-i, 0]), via1=[[0, 0]])
        rintp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                           refinstname0=irgnrn1.name, refpinname0='S0', refinstindex0=np.array([-i, 0]), via0=[[0, 0]],
                           refinstname1=irgnrstrp1.name, refpinname1='S0', refinstindex1=np.array([m_rstn-1-i, 0]), via1=[[0, 0]])
    for i in range(min(m_in, m_rgnn+m_rstn)-1):
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2, 1]), xy1=np.array([-2, 0]), gridname0=rg_m2m3,
                     refinstname0=imaininl0.name, refpinname0='S0', refinstindex0=np.array([m_in - 1 - i + 1, 0]), via0=[[0, 0]],
                     refinstname1=irgnln1.name, refpinname1='S0', refinstindex1=np.array([-i + 1, 0]), via1=[[0, 0]])
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2, 1]), xy1=np.array([-2, 0]), gridname0=rg_m2m3,
                     refinstname0=imaininr0.name, refpinname0='S0', refinstindex0=np.array([m_in - 1 - i + 1, 0]), via0=[[0, 0]],
                     refinstname1=irgnrn1.name, refpinname1='S0', refinstindex1=np.array([-i + 1, 0]), via1=[[0, 0]])
    #laygen.boundary_pin_from_rect(rintp, gridname=rg_m2m3, name='INTP', layer=laygen.layers['pin'][3], size=2, direction='top')
    #laygen.boundary_pin_from_rect(rintm, gridname=rg_m2m3, name='INTM', layer=laygen.layers['pin'][3], size=2, direction='top')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refobj0=irgnrstlp1, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refobj1=irgnrstlp1, refpinname1='D0', refinstindex1=np.array([m_rstn-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refobj0=irgnrstrp1, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refobj1=irgnrstrp1, refpinname1='D0', refinstindex1=np.array([m_rstn-1, 0]))
    
    laygen.via(None, np.array([0, 1]), refinstname=imaininl0.name, refpinname='S0', refinstindex=np.array([m_in-1, 0]), gridname=rg_m2m3)
    laygen.via(None, np.array([0, 1]), refinstname=imaininr0.name, refpinname='S0', refinstindex=np.array([m_in-1, 0]), gridname=rg_m2m3)
    for i in range(m_rstn):
        laygen.via(None, np.array([0, 1]), refinstname=irgnrstlp1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=irgnrstrp1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #clk connection
    '''
    xy0=laygen.get_inst_pin_xy(imainck0.name, pinname='G0', gridname=rg_m2m3, index=np.array([m_clkh - 1, 0]), sort=True)[0]
    y0=laygen.get_inst_xy(imaintap0.name, rg_m3m4)[1]-1
    xy1=laygen.get_inst_pin_xy(irgnrstlp1.name, pinname='G0', gridname=rg_m2m3, index=np.array([m_clkh - 1, 0]), sort=True)[0]
    rclk=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0]+1, y0]), xy1=np.array([1, 0-4-1]), gridname0=rg_m2m3,
                      refinstname1=irgnrstlp1.name, refpinname1='G0', refinstindex1=np.array([m_rstn-1, 0])
                      )
    xy0=laygen.get_rect_xy(rclk.name, rg_m3m4, sort=True)
    #laygen.route(None, laygen.layers['metal'][4], xy0=xy0[1]+np.array([-2*m_rstn, 0]), xy1=xy0[1]+np.array([0, 0]), gridname0=rg_m3m4, via1=[[0, 0]])
    #rclk2 = laygen.route(None, laygen.layers['metal'][4], xy0=xy0[1]+np.array([0, 0]), xy1=xy0[1]+np.array([2*m_rstn, 0]), gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][4], xy0=xy0[1]+np.array([-1*l_clkb_m4, 0]), xy1=xy0[1]+np.array([0, 0]), gridname0=rg_m3m4, via1=[[0, 0]])
    rclk2 = laygen.route(None, laygen.layers['metal'][4], xy0=xy0[1]+np.array([0, 0]), xy1=xy0[1]+np.array([l_clkb_m4, 0]), gridname0=rg_m3m4)
    xy0=laygen.get_rect_xy(rclk2.name, rg_m4m5, sort=True)
    rclk3 = laygen.route(None, laygen.layers['metal'][5], xy0=xy0[0]+np.array([l_clkb_m4, 0]), xy1=xy0[0]+np.array([l_clkb_m4, 5]), gridname0=rg_m4m5, via0=[[0, 0]])
    laygen.boundary_pin_from_rect(rclk3, gridname=rg_m4m5, name='CLKB', layer=laygen.layers['pin'][5], size=4, direction='top')
    laygen.via(None, np.array([1, 0]), refinstname=imainck0.name, refpinname='G0', refinstindex=np.array([m_clkh-1, 0]), gridname=rg_m2m3)
    laygen.via(None, np.array([1, 0]), refinstname=irgnrstlp1.name, refpinname='G0', refinstindex=np.array([m_rstn-1, 0]), gridname=rg_m2m3)
    '''
    #input connection
    y0=laygen.get_inst_xy(imaintap0.name, rg_m3m4)[1]
    y1=laygen.get_inst_xy(irgntap0.name, rg_m2m3)[1]
    xy0=laygen.get_inst_pin_xy(imaininl0.name, pinname='G0', gridname=rg_m2m3, index=np.array([0, 0]), sort=True)[0]
    rinp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0]+1-1, y0]), xy1=np.array([1-1, 0]), gridname0=rg_m2m3,
                      refinstname1=imaininl0.name, refpinname1='G0', refinstindex1=np.array([0, 0]))
    laygen.boundary_pin_from_rect(rinp, gridname=rg_m3m4, name='INTP', layer=laygen.layers['pin'][3], size=4, direction='bottom')
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                      refinstname0=imaininl0.name, refpinname0='G0', refinstindex0=np.array([m_in - 1, 0]), via0=[[0, 0]],
                      refinstname1=irgnrstlp1.name, refpinname1='G0', refinstindex1=np.array([m_rstn - 1, 0]), via1=[[0, 0]])

    laygen.via(None, np.array([1-1, 0]), refinstname=imaininl0.name, refpinname='G0', refinstindex=np.array([0, 0]), gridname=rg_m2m3)
    xy0=laygen.get_inst_pin_xy(imaininr0.name, pinname='G0', gridname=rg_m2m3, index=np.array([0, 0]), sort=True)[0]
    rinm=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0]-1+1, y0]), xy1=np.array([1-1, 0]), gridname0=rg_m2m3,
                      refinstname1=imaininr0.name, refpinname1='G0', refinstindex1=np.array([0, 0]))
    laygen.boundary_pin_from_rect(rinm, gridname=rg_m3m4, name='INTM', layer=laygen.layers['pin'][3], size=4, direction='bottom')
    laygen.via(None, np.array([1-1, 0]), refinstname=imaininr0.name, refpinname='G0', refinstindex=np.array([0, 0]), gridname=rg_m2m3)
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
                      refinstname0=imaininr0.name, refpinname0='G0', refinstindex0=np.array([m_in - 1, 0]), via0=[[0, 0]],
                      refinstname1=irgnrstrp1.name, refpinname1='G0', refinstindex1=np.array([m_rstn - 1, 0]), via1=[[0, 0]])

    #output connection (outp)
    #x_center=laygen.get_rect_xy(rclk.name, rg_m3m4, sort=True)[0][0]
    x_center=(laygen.get_rect_xy(rinp.name, rg_m3m4, sort=True)[0][0]+laygen.get_rect_xy(rinm.name, rg_m3m4, sort=True)[0][0])/2
    y1=laygen.get_inst_xy(irgntap0.name, rg_m3m4)[1]-4
    xy0=laygen.get_inst_pin_xy(irgnbuflp0.name, pinname='D0', gridname=rg_m3m4, index=np.array([m_buf-1, 0]), sort=True)[0]
    routp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0], y1+4]), xy1=np.array([0, 1]), gridname0=rg_m3m4,
                      refinstname1=irgnbuflp0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]),
                      direction='top')
    routp2=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xy0[0], y1]), xy1=np.array([x_center-l_clkb_m4-2, y1]),
                        gridname0=rg_m3m4, via0=[[0, 0]])
    routp2b=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xy0[0], y1+2]), xy1=np.array([x_center-l_clkb_m4-2, y1+2]),
                        gridname0=rg_m3m4, via0=[[0, 0]])
    xy1=laygen.get_rect_xy(routp2.name, rg_m4m5, sort=True)
    routp3 = laygen.route(None, laygen.layers['metal'][5], xy0=xy1[1], xy1=xy1[1]+np.array([0, 6]), gridname0=rg_m4m5, via0=[[0, 0]])
    routp3b = laygen.route(None, laygen.layers['metal'][5], xy0=xy1[1]+np.array([0, 2]), xy1=xy1[1]+np.array([0, 6]), gridname0=rg_m4m5, via0=[[0, 0]])
    laygen.boundary_pin_from_rect(routp3, gridname=rg_m4m5, name='OUTP', layer=laygen.layers['pin'][5], size=4, direction='top')
    #output connection (outm)
    y1=laygen.get_inst_xy(irgntap0.name, rg_m3m4)[1]-4
    xy0=laygen.get_inst_pin_xy(irgnbufrp0.name, pinname='D0', gridname=rg_m3m4, index=np.array([m_buf-1, 0]), sort=True)[0]
    routm=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0], y1+4]), xy1=np.array([0, 1]), gridname0=rg_m3m4,
                      refinstname1=irgnbufrp0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]),
                      direction='top')
    routm2=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xy0[0], y1]), xy1=np.array([x_center+l_clkb_m4+2, y1]),
                        gridname0=rg_m3m4, via0=[[0, 0]])
    routm2b=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xy0[0], y1+2]), xy1=np.array([x_center+l_clkb_m4+2, y1+2]),
                        gridname0=rg_m3m4, via0=[[0, 0]])
    xy1=laygen.get_rect_xy(routm2.name, rg_m4m5, sort=True)
    routm3 = laygen.route(None, laygen.layers['metal'][5], xy0=xy1[0]+np.array([0, 0]), xy1=xy1[0]+np.array([0, 6]), gridname0=rg_m4m5, via0=[[0, 0]])
    routm3b = laygen.route(None, laygen.layers['metal'][5], xy0=xy1[0]+np.array([0, 2]), xy1=xy1[0]+np.array([0, 6]), gridname0=rg_m4m5, via0=[[0, 0]])
    laygen.boundary_pin_from_rect(routm3, gridname=rg_m4m5, name='OUTM', layer=laygen.layers['pin'][5], size=4, direction='top')
    #offset input connection
    y1=laygen.get_inst_xy(irgntap0.name, rg_m2m3)[1]
    xy0=laygen.get_inst_pin_xy(iofstinl0.name, pinname='G0', gridname=rg_m2m3, index=np.array([0, 0]), sort=True)[0]
    xy1=laygen.get_rect_xy(routp.name, rg_m2m3, sort=True)[0]
    #rosp=laygen.route(None, laygen.layers['metal'][3], xy0=[xy1[0]+3, y1], xy1=[0, 0], gridname0=rg_m2m3, 
    #                  refobj1=iofstinl0, refpinname1='G0', direction='y', via1=[[0, 0]])
    #laygen.boundary_pin_from_rect(rosp, gridname=rg_m3m4, name='OSP', layer=laygen.layers['pin'][3], size=4, direction='top')
    xy0=laygen.get_inst_pin_xy(iofstinr0.name, pinname='G0', gridname=rg_m2m3, index=np.array([0, 0]), sort=True)[0]
    xy1=laygen.get_rect_xy(routm.name, rg_m2m3, sort=True)[0]
    #rosm=laygen.route(None, laygen.layers['metal'][3], xy0=[xy1[0]-3, y1], xy1=[xy1[0]-3, xy0[1]], gridname0=rg_m2m3, via1=[[0, 0]])
    #rosm=laygen.route(None, laygen.layers['metal'][3], xy0=[xy1[0]-3, y1], xy1=[0, 0], gridname0=rg_m2m3, 
    #                  refobj1=iofstinr0, refpinname1='G0', direction='y', via1=[[0, 0]])
    #laygen.route(None, laygen.layers['metal'][2], xy0=[0, 0], xy1=[xy1[0]-3, xy0[1]], gridname0=rg_m2m3,
    #             refinstname0=iofstinr0.name, refpinname0='G0', refinstindex0=np.array([0, 0]))
    #laygen.boundary_pin_from_rect(rosm, gridname=rg_m3m4, name='OSM', layer=laygen.layers['pin'][3], size=4, direction='top')

    #VDD/VSS
    #num_vert_pwr = 20
    rvss1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 1]), xy1=np.array([2*num_vert_pwr, 1]), gridname0=rg_m1m2_thick,
                        refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
    rvss1b = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, -1]), xy1=np.array([2*num_vert_pwr, -1]), gridname0=rg_m1m2_thick,
                        refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
    rvss2 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 1]), xy1=np.array([2*num_vert_pwr, 1]), gridname0=rg_m1m2_thick,
                        refinstname0=irgntapn0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=irgntapn0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
    rvss = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 1]), xy1=np.array([2*num_vert_pwr, 1]), gridname0=rg_m1m2_thick,
                        refinstname0=irgntap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
    rvssb = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, -1]), xy1=np.array([2*num_vert_pwr, -1]), gridname0=rg_m1m2_thick,
                        refinstname0=irgntap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
    '''
    rvdd0 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 0]), xy1=np.array([2*num_vert_pwr, 0]), gridname0=rg_m1m2,
                        refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 1]),
                        refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 1])
                       )
    '''
    rvdd1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, -1]), xy1=np.array([2*num_vert_pwr, -1]), gridname0=rg_m1m2,
                        refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 5]),
                        refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 5])
                       )
    #rvdd_pin_xy = laygen.get_rect_xy(rvdd.name, rg_m1m2_thick)
    rvss1_pin_xy = laygen.get_rect_xy(rvss1.name, rg_m1m2_thick)
    rvss2_pin_xy = laygen.get_rect_xy(rvss2.name, rg_m1m2_thick)
    rvss_pin_xy = laygen.get_rect_xy(rvss.name, rg_m1m2_thick)

    #laygen.pin(name='VDD0', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2_thick, netname='VDD')
    laygen.pin(name='VSS2', layer=laygen.layers['pin'][2], xy=rvss1_pin_xy, gridname=rg_m1m2_thick, netname='VSS')
    laygen.pin(name='VSS1', layer=laygen.layers['pin'][2], xy=rvss2_pin_xy, gridname=rg_m1m2_thick, netname='VSS')
    laygen.pin(name='VSS0', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2_thick, netname='VSS')

    #vdd/vss vertical
    i=0
    for i in range(num_vert_pwr):
        rvvss_l = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2*i-1, -1]), xy1=np.array([-2*i-1, -1]), gridname0=rg_m2m3_thick,
                               refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                               refinstname1=irgntap0.name, refpinname1='TAP0', refinstindex1=np.array([0, 0])
                               )
        rvvss_r = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, -1]), xy1=np.array([2*i+1, -1]), gridname0=rg_m2m3_thick,
                               refinstname0=imaintap0.name, refpinname0='TAP1', refinstindex0=np.array([m_tap-1, 0]),
                               refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                               )
        laygen.via(None, np.array([-2*i-1, 1]), refinstname=irgntap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, 1]), refinstname=irgntap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2*i-1, -1]), refinstname=irgntap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, -1]), refinstname=irgntap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
                       gridname=rg_m2m3_thick)
        laygen.pin(name='VSSL'+str(i), layer=laygen.layers['pin'][3],
                   xy=laygen.get_rect_xy(rvvss_l.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VSS')
        laygen.pin(name='VSSR'+str(i), layer=laygen.layers['pin'][3],
                   xy=laygen.get_rect_xy(rvvss_r.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VSS')

        rvvdd_l = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2*i-2, -1]), xy1=np.array([-2*i-2, -1]), gridname0=rg_m2m3_thick,
                               refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                               refinstname1=irgntap0.name, refpinname1='TAP0', refinstindex1=np.array([0, 0])
                       )
        rvvdd_r = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, -1]), xy1=np.array([2*i+2, -1]), gridname0=rg_m2m3_thick,
                               refinstname0=imaintap0.name, refpinname0='TAP1', refinstindex0=np.array([m_tap-1, 0]),
                               refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
        laygen.via(None, np.array([-2*i-1, 1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, 1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2*i-1, 1]), refinstname=irgntapn0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, 1]), refinstname=irgntapn0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2*i-1, -1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, -1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
                       gridname=rg_m2m3_thick)
        #laygen.via(None, np.array([-2*i-2, 0]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 1]),
        #               gridname=rg_m2m3)
        #laygen.via(None, np.array([2*i+2, 0]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 1]),
        #               gridname=rg_m2m3)
        laygen.via(None, np.array([-2*i-2, -1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 5]),
                       gridname=rg_m2m3)
        laygen.via(None, np.array([2*i+2, -1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 5]),
                       gridname=rg_m2m3)

        laygen.pin(name='VDDL'+str(i), layer=laygen.layers['pin'][3],
                   xy=laygen.get_rect_xy(rvvdd_l.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VDD')
        laygen.pin(name='VDDR'+str(i), layer=laygen.layers['pin'][3],
                   xy=laygen.get_rect_xy(rvvdd_r.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VDD')

def generate_salatch_pmos_fitdim(laygen, objectname_pfix, placement_grid, routing_grid_m1m2,
                                 routing_grid_m1m2_thick, routing_grid_m2m3, routing_grid_m2m3_thick, routing_grid_m3m4, routing_grid_m4m5,
                                 devname_ptap_boundary, devname_ptap_body,
                                 devname_nmos_boundary, devname_nmos_body, devname_nmos_dmy,
                                 devname_pmos_boundary, devname_pmos_body, devname_pmos_dmy,
                                 devname_ntap_boundary, devname_ntap_body,
                                 m_in=4, m_ofst=2, m_clkh=2, m_rgnn=2, m_rstn=1, m_buf=1,
                                 m_space_4x=0, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0])):
    """generate a salatch & fit to CDAC dim"""

    cdac_name = 'capdac'
    cdrva_name = 'capdrv_array_7b'

    m_tot = max(m_in, m_clkh, m_rgnn + 2*m_rstn + m_buf) + 1  # at least one dummy
    
    #grids
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m1m2_thick = routing_grid_m1m2_thick
    rg_m2m3 = routing_grid_m2m3
    rg_m2m3_thick = routing_grid_m2m3_thick
    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5

    #spacing calculation
    devname_space_1x = ['ptap_fast_space', 'nmos4_fast_space', 'ptap_fast_space',
                        'nmos4_fast_space', 'pmos4_fast_space', 'ntap_fast_space']
    devname_space_2x = ['ptap_fast_space_nf2', 'nmos4_fast_space_nf2', 'ptap_fast_space_nf2',
                        'nmos4_fast_space_nf2', 'pmos4_fast_space_nf2', 'ntap_fast_space_nf2']
    devname_space_4x = ['ptap_fast_space_nf4', 'nmos4_fast_space_nf4', 'ptap_fast_space_nf4',
                        'nmos4_fast_space_nf4', 'pmos4_fast_space_nf4', 'ntap_fast_space_nf4']
    transform_space = ['R0', 'R0', 'R0', 'R0', 'R0', 'MX']
    m_space=m_space_4x*4+m_space_2x*2+m_space_1x*1
    #boundary generation
    m_bnd=m_tot*2*2+m_space*2+2 #2 for diff, 2 for nf, 2 for mos boundary
    [bnd_bottom, bnd_top, bnd_left, bnd_right]=generate_boundary(laygen, objectname_pfix='BND0',
        placement_grid=pg,
        devname_bottom = ['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
        shape_bottom = [np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
        devname_top = ['boundary_topleft', 'boundary_top', 'boundary_topright'],
        shape_top = [np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
        devname_left = ['ptap_fast_left', 'nmos4_fast_left', 'ptap_fast_left',
                        'nmos4_fast_left', 'pmos4_fast_left', 'ntap_fast_left'],
        transform_left=['R0', 'R0', 'R0', 'R0', 'R0', 'MX'],
        devname_right=['ptap_fast_right', 'nmos4_fast_right', 'ptap_fast_right',
                       'nmos4_fast_right','pmos4_fast_right', 'ntap_fast_right'],
        transform_right = ['R0', 'R0', 'R0', 'R0', 'R0', 'MX'],
        origin=np.array([0, 0]))
    #space generation
    spl_origin = laygen.get_inst_xy(bnd_bottom[0].name, pg) + laygen.get_template_size(bnd_bottom[0].cellname, pg)
    ispl4x=[]
    ispl2x=[]
    ispl1x=[]
    for i, d in enumerate(devname_space_4x):
        if i==0:
            if not m_space_1x==0:
                ispl1x.append(laygen.place(name="ISA0SPL1X0", templatename=devname_space_1x[i], gridname=pg, shape=np.array([m_space_1x, 1]),
                                           xy=spl_origin, transform=transform_space[i]))
                refi=ispl1x[-1].name
                if not m_space_2x==0:
                    ispl2x.append(laygen.relplace(name="ISA0SPL2X0", templatename=devname_space_2x[i], gridname=pg, refinstname=refi,
                                              shape=np.array([m_space_2x, 1]),
                                              transform=transform_space[i]))
                    refi=ispl2x[-1].name
            else:
                if not m_space_2x==0:
                    ispl2x.append(laygen.place(name="ISA0SPL2X0", templatename=devname_space_2x[i], gridname=pg, shape=np.array([m_space_2x, 1]),
                                           xy=spl_origin, transform=transform_space[i]))
                    refi=ispl2x[-1].name
                #ispl2x.append(laygen.relplace(name="ISA0SPL2X0", templatename=devname_space_2x[i], gridname=pg, refinstname=refi,
                #                              shape=np.array([m_space_2x, 1]),
                #                              transform=transform_space[i]))
                #refi=ispl2x[-1].name
            if m_space_1x==0 and m_space_2x==0:
                ispl4x.append(laygen.place(name="ISA0SPL4X0", templatename=d, gridname=pg, xy=spl_origin,
                                          shape=np.array([m_space_4x, 1]), transform=transform_space[i]))
                refi=ispl4x[-1].name
            else:
                ispl4x.append(laygen.relplace(name="ISA0SPL4X0", templatename=d, gridname=pg, refinstname=refi,
                                          shape=np.array([m_space_4x, 1]), transform=transform_space[i]))
        else:
            if not m_space_1x==0:
                ispl1x.append(laygen.relplace(name="ISA0SPL1X" + str(i), templatename=devname_space_1x[i], gridname=pg,
                                              refinstname=ispl1x[-1].name, shape=np.array([m_space_1x, 1]),
                                              direction='top', transform=transform_space[i]))
            if not m_space_2x==0:
                ispl2x.append(laygen.relplace(name="ISA0SPL2X" + str(i), templatename=devname_space_2x[i], gridname=pg,
                                              refinstname=ispl2x[-1].name, shape=np.array([m_space_2x, 1]),
                                              direction='top', transform=transform_space[i]))
            ispl4x.append(laygen.relplace(name="ISA0SPL4X"+str(i), templatename=d, gridname=pg, refinstname=ispl4x[-1].name,
                                        shape=np.array([m_space_4x, 1]), direction='top', transform=transform_space[i]))
    spr_origin = laygen.get_inst_xy(bnd_bottom[-1].name, pg) \
                 + laygen.get_template_size(bnd_bottom[-1].cellname, pg) * np.array([0, 1]) \
                 - laygen.get_template_size('nmos4_fast_space', pg) * np.array([m_space, 0])
    ispr4x=[]
    ispr2x=[]
    ispr1x=[]
    for i, d in enumerate(devname_space_4x):
        if i==0:
            ispr4x.append(laygen.place(name="ISA0SPR4X0", templatename=d, gridname=pg, shape=np.array([m_space_4x, 1]),
                                     xy=spr_origin, transform=transform_space[i]))
            refi=ispr4x[-1].name
            if not m_space_2x==0:
                ispr2x.append(laygen.relplace(name="ISA0SPR2X0", templatename=devname_space_2x[i], gridname=pg, refinstname=refi,
                                              shape=np.array([m_space_2x, 1]),
                                              transform=transform_space[i]))
                refi=ispr2x[-1].name
            if not m_space_1x==0:
                ispr1x.append(laygen.relplace(name="ISA0SPR1X0", templatename=devname_space_1x[i], gridname=pg, refinstname=refi,
                                              shape=np.array([m_space_1x, 1]),
                                              transform=transform_space[i]))
        else:
            ispr4x.append(laygen.relplace(name="ISA0SPR4X"+str(i), templatename=d, gridname=pg, refinstname=ispr4x[-1].name,
                                        shape=np.array([m_space_4x, 1]), direction='top', transform=transform_space[i]))
            if not m_space_2x==0:
                ispr2x.append(laygen.relplace(name="ISA0SPR2X" + str(i), templatename=devname_space_2x[i], gridname=pg,
                                              refinstname=ispr2x[-1].name, shape=np.array([m_space_2x, 1]),
                                              direction='top', transform=transform_space[i]))
            if not m_space_1x==0:
                ispr1x.append(laygen.relplace(name="ISA0SPR1X" + str(i), templatename=devname_space_1x[i], gridname=pg,
                                              refinstname=ispr1x[-1].name, shape=np.array([m_space_1x, 1]),
                                              direction='top', transform=transform_space[i]))

    #salatch
    sa_origin = origin+laygen.get_inst_xy(bnd_bottom[0].name, pg)+laygen.get_template_size(bnd_bottom[0].cellname, pg)\
                +laygen.get_template_size('nmos4_fast_space', pg)*m_space*np.array([1, 0])

    #sa_origin=origin
    generate_salatch_pmos(laygen, objectname_pfix=objectname_pfix,
                     placement_grid=placement_grid, routing_grid_m1m2=routing_grid_m1m2,
                     routing_grid_m1m2_thick=routing_grid_m1m2_thick,
                     routing_grid_m2m3=routing_grid_m2m3, routing_grid_m2m3_thick=routing_grid_m2m3_thick,
                     routing_grid_m3m4=routing_grid_m3m4, routing_grid_m4m5=routing_grid_m4m5,
                     devname_ptap_boundary=devname_ptap_boundary, devname_ptap_body=devname_ptap_body,
                     devname_nmos_boundary=devname_nmos_boundary, devname_nmos_body=devname_nmos_body,
                     devname_nmos_dmy=devname_nmos_dmy,
                     devname_pmos_boundary=devname_pmos_boundary, devname_pmos_body=devname_pmos_body,
                     devname_pmos_dmy=devname_pmos_dmy,
                     devname_ntap_boundary=devname_ntap_boundary, devname_ntap_body=devname_ntap_body,
                     m_in=m_in, m_ofst=m_ofst, m_clkh=m_clkh, m_rgnn=m_rgnn, m_rstn=m_rstn, m_buf=m_buf, 
                     num_vert_pwr = m_space_4x * 2, origin=sa_origin)


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
    cellname = 'doubleSA_pmos_2nd'
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
        m_sa=sizedict['salatch']['m_d']
        m_rst_sa=sizedict['salatch']['m_rst_d']
        m_rgnn_sa=sizedict['salatch']['m_rgnp_d']
        m_buf_sa=sizedict['salatch']['m_buf']
        #m_sa=sizedict['salatch_m']
        #m_rst_sa=sizedict['salatch_m_rst']
        #m_rgnn_sa=sizedict['salatch_m_rgnn']
        #m_buf_sa=sizedict['salatch_m_buf']
    m_in=int(m_sa/2)            #4
    m_clkh=m_in #max(1, m_in)                 #4
    m_rstn=int(m_rst_sa/2)                    #1
    m_buf=int(m_buf_sa/2)
    m_rgnn=int(m_rgnn_sa/2) 
    m_ofst=0

    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)

    sa_origin=np.array([0, 0])

    #salatch body
    # 1. generate without spacing
    generate_salatch_pmos_fitdim(laygen, objectname_pfix='SA0',
                                placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick,
                                routing_grid_m2m3=rg_m2m3, routing_grid_m2m3_thick=rg_m2m3_thick, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5,
                                devname_ptap_boundary='ptap_fast_boundary', devname_ptap_body='ptap_fast_center_nf1',
                                devname_nmos_boundary='nmos4_fast_boundary', devname_nmos_body='nmos4_fast_center_nf2',
                                devname_nmos_dmy='nmos4_fast_dmy_nf2',
                                devname_pmos_boundary='pmos4_fast_boundary', devname_pmos_body='pmos4_fast_center_nf2',
                                devname_pmos_dmy='pmos4_fast_dmy_nf2',
                                devname_ntap_boundary='ntap_fast_boundary', devname_ntap_body='ntap_fast_center_nf1',
                                m_in=m_in, m_ofst=m_ofst, m_clkh=m_clkh, m_rgnn=m_rgnn, m_rstn=m_rstn, m_buf=m_buf,
                                m_space_4x=10, m_space_2x=0, m_space_1x=0, origin=sa_origin)
    laygen.add_template_from_cell()
    # 2. calculate spacing param and regenerate
    x0 = 2*laygen.templates.get_template('capdac', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0]
    m_space = int(round(x0 / 2 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_space_4x = int(m_space / 4)
    m_space_2x = int((m_space - m_space_4x * 4) / 2)
    m_space_1x = int(m_space - m_space_4x * 4 - m_space_2x * 2)
    #print("debug", x0, laygen.templates.get_template('capdrv_array_7b', libname=workinglib).xy[1][0] \
    #        , laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
    #        , laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0], m_space, m_space_4x, m_space_2x, m_space_1x)
    
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_salatch_pmos_fitdim(laygen, objectname_pfix='SA0',
                                placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick,
                                routing_grid_m2m3=rg_m2m3, routing_grid_m2m3_thick=rg_m2m3_thick, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5,
                                devname_ptap_boundary='ptap_fast_boundary', devname_ptap_body='ptap_fast_center_nf1',
                                devname_nmos_boundary='nmos4_fast_boundary', devname_nmos_body='nmos4_fast_center_nf2',
                                devname_nmos_dmy='nmos4_fast_dmy_nf2',
                                devname_pmos_boundary='pmos4_fast_boundary', devname_pmos_body='pmos4_fast_center_nf2',
                                devname_pmos_dmy='pmos4_fast_dmy_nf2',
                                devname_ntap_boundary='ntap_fast_boundary', devname_ntap_body='ntap_fast_center_nf1',
                                m_in=m_in, m_ofst=m_ofst, m_clkh=m_clkh, m_rgnn=m_rgnn, m_rstn=m_rstn, m_buf=m_buf,
                                m_space_4x=10+m_space_4x, m_space_2x=m_space_2x, m_space_1x=m_space_1x, origin=sa_origin)
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

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

def generate_tap(laygen, objectname_pfix, placement_grid, routing_grid_m1m2_thick, devname_tap_boundary, devname_tap_body,
                 m=1, origin=np.array([0,0]), extend_rail=False, transform='R0'):
    """generate a tap primitive"""
    pg = placement_grid
    rg12t = routing_grid_m1m2_thick

    # placement
    taprow = laygen.relplace(name=[None, None, None], 
                             templatename=[devname_tap_boundary, devname_tap_body, devname_tap_boundary],
                             gridname=pg, xy=[origin, [0, 0], [0, 0]], shape=[[1, 1], [m, 1], [1, 1]], 
                             transform=transform)
    itapbl0, itap0, itapbr0 = taprow
    td=itap0.elements[:, 0]

    #power route
    laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12t,
                 refobj0=td[0].pins['TAP0'], refobj1=td[-1].pins['TAP1'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12t,
                 refobj0=td[0].pins['TAP0'], refobj1=td[-1].pins['TAP1'])
    key=1
    for _td in td:
        laygen.via(name=None, xy=[0, key], refobj=_td.pins['TAP0'], gridname=rg12t)
        key=1-key
    laygen.via(name=None, xy=[0, key], refobj=td[-1].pins['TAP1'], gridname=rg12t)
    if extend_rail==True: #extend rail for better power integrity
        laygen.route(name=None, xy0=[0, -1], xy1=[0, -1], gridname0=rg12t,
                     refobj0=td[0].pins['TAP0'], refobj1=td[-1].pins['TAP1'])
        for _td in td[::2]:
            laygen.route(None, xy0=[0, -1], xy1=[0, 1], gridname0=rg12t, refobj0=_td.pins['TAP0'], refobj1=_td.pins['TAP0'])
            laygen.via(None, [0, -1], refobj=_td.pins['TAP0'], gridname=rg12t)
        laygen.route(None, xy0=[0, -1], xy1=[0, 1], gridname0=rg12t, refobj0=td[-1].pins['TAP1'], refobj1=td[-1].pins['TAP1'])
        laygen.via(None, [0, -1], refobj=td[-1].pins['TAP1'], gridname=rg12t)
    return [itapbl0, itap0, itapbr0]

def generate_mos(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, devname_mos_boundary, devname_mos_body,
                 devname_mos_dmy, m=1, m_dmy=0, origin=np.array([0,0])):
    """generate a analog mos primitive with dummies"""
    pg = placement_grid
    rg12 = routing_grid_m1m2
    pfix = objectname_pfix

    # placement
    imbl0 = laygen.relplace(name="I" + pfix + 'BL0', templatename=devname_mos_boundary, gridname=pg, xy=origin)
    refi=imbl0
    if not m_dmy==0:
        imdmyl0 = laygen.relplace(name="I" + pfix + 'DMYL0', templatename=devname_mos_dmy, gridname=pg, refobj=refi, shape=[m_dmy, 1])
        refi=imdmyl0
    else:
        imdmyl0 = None
    im0 = laygen.relplace(name="I" + pfix + '0', templatename=devname_mos_body, gridname=pg, refobj=refi, shape=[m, 1])
    refi=im0
    if not m_dmy==0:
        imdmyr0 = laygen.relplace(name="I" + pfix + 'DMYR0', templatename=devname_mos_dmy, gridname=pg, refobj=refi, shape=[m_dmy, 1])
        refi=imdmyr0
    else:
        imdmyr0 = None
    imbr0 = laygen.relplace(name="I" + pfix + 'BR0', templatename=devname_mos_boundary, gridname=pg, refobj=imdmyr0)
    md=im0.elements[:, 0]
    #route
    #gate
    rg0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=md[0].pins['G0'], refobj1=md[-1].pins['G0'])
    for _md in md:
        laygen.via(name=None, xy=[0, 0], refobj=_md.pins['G0'], gridname=rg12)
    #drain
    rdl0=laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12, refobj0=md[0].pins['D0'], refobj1=md[-1].pins['D0'])
    for _md in md:
        laygen.via(name=None, xy=[0, 1], refobj=_md.pins['D0'], gridname=rg12)
    #source
    rs0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=md[0].pins['S0'], refobj1=md[-1].pins['S1'])
    for _md in md:
        laygen.via(name=None, xy=[0, 0], refobj=_md.pins['S0'], gridname=rg12)
    laygen.via(name=None, xy=[0, 0], refobj=md[-1].pins['S1'], gridname=rg12)
    #dmy
    if m_dmy>=2:
        mdmyl=imdmyl0.elements[:, 0]
        mdmyr=imdmyr0.elements[:, 0]
        laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12, refobj0=mdmyl[0].pins['D0'], refobj1=mdmyl[-1].pins['D0'])
        laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12, refobj0=mdmyr[0].pins['D0'], refobj1=mdmyr[-1].pins['D0'])
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=mdmyl[0].pins['S0'], refobj1=mdmyl[-1].pins['S1'])
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=mdmyr[0].pins['S0'], refobj1=mdmyr[-1].pins['S1'])
        for _mdmyl in mdmyl:
            laygen.via(name=None, xy=[0, 1], refobj=_mdmyl.pins['D0'], gridname=rg12)
            laygen.via(name=None, xy=[0, 0], refobj=_mdmyl.pins['S0'], gridname=rg12)
        for _mdmyr in mdmyr:
            laygen.via(name=None, xy=[0, 1], refobj=_mdmyr.pins['D0'], gridname=rg12)
            laygen.via(name=None, xy=[0, 0], refobj=_mdmyr.pins['S1'], gridname=rg12)
    return [imbl0, imdmyl0, im0, imdmyr0, imbr0]

def generate_diff_mos_ofst(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, devname_mos_boundary, devname_mos_body,
                      devname_mos_dmy, m=1, m_ofst=2, m_dmy=0, origin=np.array([0,0])):
    """generate an analog differential mos structure with dummmies """
    pg = placement_grid
    rg12 = routing_grid_m1m2
    pfix = objectname_pfix

    # placement
    imbl0 = laygen.relplace(name="I" + pfix + 'BL0', templatename=devname_mos_boundary, gridname=pg, xy=origin)
    refi=imbl0
    if not m_dmy==0:
        imdmyl0 = laygen.relplace(name="I" + pfix + 'DMYL0', templatename=devname_mos_body, gridname=pg, refobj=refi, shape=[m_dmy, 1])
        refi=imdmyl0
    else:
        imdmyl0=None
    imofstl0 = laygen.relplace(name="I" + pfix + 'OFST0', templatename=devname_mos_body, gridname=pg, refobj=refi, shape=[m_ofst, 1])
    iml0 = laygen.relplace(name="I" + pfix + '0', templatename=devname_mos_body, gridname=pg, refobj=imofstl0, shape=[m, 1])
    imr0 = laygen.relplace(name="I" + pfix + '1', templatename=devname_mos_body, gridname=pg, refobj=iml0, shape=[m, 1], transform='MY')
    imofstr0 = laygen.relplace(name="I" + pfix + 'OFST1', templatename=devname_mos_body, gridname=pg, refobj=imr0, shape=[m_ofst, 1], transform='MY')
    refi=imofstr0
    if not m_dmy==0:
        imdmyr0 = laygen.relplace(name="I" + pfix + 'DMYR0', templatename=devname_mos_body, gridname=pg, refobj=imofstr0, shape=[m_dmy, 1], transform='MY')
        refi=imdmyr0
    else:
        imdmyr0=None
    imbr0 = laygen.relplace(name="I" + pfix + 'BR0', templatename=devname_mos_boundary, gridname=pg, refobj=refi, transform='MY')
    mdl=iml0.elements[:, 0]
    mdr=imr0.elements[:, 0]
    mdol=imofstl0.elements[:, 0]
    mdor=imofstr0.elements[:, 0]

    #route
    #gate
    rgl0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=mdl[0].pins['G0'], refobj1=mdl[-1].pins['G0'])
    rgr0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=mdr[0].pins['G0'], refobj1=mdr[-1].pins['G0'])
    for _mdl, _mdr in zip(mdl, mdr):
        laygen.via(name=None, xy=[0, 0], refobj=_mdl.pins['G0'], gridname=rg12)
        laygen.via(name=None, xy=[0, 0], refobj=_mdr.pins['G0'], gridname=rg12)
    #gate_ofst
    rgofstl0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=mdol[0].pins['G0'], refobj1=mdol[-1].pins['G0'])
    rgofstr0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=mdor[0].pins['G0'], refobj1=mdor[-1].pins['G0'])
    for _mdol, _mdor in zip(mdol, mdor):
        laygen.via(name=None, xy=[0, 0], refobj=_mdol.pins['G0'], gridname=rg12)
        laygen.via(name=None, xy=[0, 0], refobj=_mdor.pins['G0'], gridname=rg12)
    #drain
    rdl0=laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12, refobj0=mdol[0].pins['D0'], refobj1=mdl[-1].pins['D0'])
    rdr0=laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12, refobj0=mdr[-1].pins['D0'], refobj1=mdor[0].pins['D0'])
    for _mdl, _mdr in zip(mdl, mdr):
        laygen.via(name=None, xy=[0, 1], refobj=_mdl.pins['D0'], gridname=rg12)
        laygen.via(name=None, xy=[0, 1], refobj=_mdr.pins['D0'], gridname=rg12)
    for _mdol, _mdor in zip(mdol, mdor):
        laygen.via(name=None, xy=[0, 1], refobj=_mdol.pins['D0'], gridname=rg12)
        laygen.via(name=None, xy=[0, 1], refobj=_mdor.pins['D0'], gridname=rg12)
    #source
    rs0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=mdol[0].pins['S0'], refobj1=mdor[0].pins['S0'])
    for _mdl, _mdr in zip(mdl, mdr):
        laygen.via(name=None, xy=[0, 0], refobj=_mdl.pins['S0'], gridname=rg12)
        laygen.via(name=None, xy=[0, 0], refobj=_mdr.pins['S0'], gridname=rg12)
    laygen.via(name=None, xy=[0, 0], refobj=mdl[-1].pins['S1'], gridname=rg12)
    laygen.via(name=None, xy=[0, 0], refobj=mdr[-1].pins['S1'], gridname=rg12)
    for _mdol, _mdor in zip(mdol, mdor):
        laygen.via(name=None, xy=[0, 0], refobj=_mdol.pins['S0'], gridname=rg12)
        laygen.via(name=None, xy=[0, 0], refobj=_mdor.pins['S0'], gridname=rg12)
    laygen.via(name=None, xy=[0, 0], refobj=mdol[-1].pins['S1'], gridname=rg12)
    laygen.via(name=None, xy=[0, 0], refobj=mdor[-1].pins['S1'], gridname=rg12)
    #dmy
    if m_dmy>=2:
        mdmyl=imdmyl0.elements[:, 0]
        mdmyr=imdmyr0.elements[:, 0]
        laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12, refobj0=mdmyl[0].pins['D0'], refobj1=mdmyl[-1].pins['D0'])
        laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12, refobj0=mdmyr[0].pins['D0'], refobj1=mdmyr[-1].pins['D0'])
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=mdmyl[0].pins['S0'], refobj1=mdmyl[-1].pins['S0'])
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=mdmyr[0].pins['S0'], refobj1=mdmyr[-1].pins['S0'])
        for _mdmyl, _mdmyr in zip(mdmyl, mdmyr):
            laygen.via(name=None, xy=[0, 1], refobj=_mdmyl.pins['D0'], gridname=rg12)
            laygen.via(name=None, xy=[0, 1], refobj=_mdmyr.pins['D0'], gridname=rg12)
            laygen.via(name=None, xy=[0, 0], refobj=_mdmyl.pins['S0'], gridname=rg12)
            laygen.via(name=None, xy=[0, 0], refobj=_mdmyr.pins['S0'], gridname=rg12)
    return [imbl0, imdmyl0, imofstl0, iml0, imr0, imofstr0, imdmyr0, imbr0]

def generate_clkdiffpair_ofst(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m1m2_thick, routing_grid_m2m3,
                              devname_mos_boundary, devname_mos_body, devname_mos_dmy, devname_tap_boundary, devname_tap_body,
                              m_in=2, m_ofst=2, m_in_dmy=1, m_clkh=2, m_clkh_dmy=1, m_tap=12, origin=np.array([0, 0])):
    """generate a clocked differential pair with offset"""
    pg = placement_grid
    rg12 = routing_grid_m1m2
    rg12t = routing_grid_m1m2_thick
    rg23 = routing_grid_m2m3
    m_clk=m_clkh*2

    #placement
    tap_origin=origin
    [itapbl0, itap0, itapbr0] = generate_tap(laygen, objectname_pfix=objectname_pfix+'NTAP0', placement_grid=pg,
                                             routing_grid_m1m2_thick=rg12t,
                                             devname_tap_boundary=devname_tap_boundary, devname_tap_body=devname_tap_body,
                                             m=m_tap, extend_rail=True, origin=tap_origin)
    diffpair_origin = laygen.get_xy(obj = itapbl0, gridname = pg) + laygen.get_xy(obj = itapbl0.template, gridname = pg) * np.array([0, 1])
    [ickbl0, ickdmyl0, ick0, ickdmyr0, ickbr0]=generate_mos(laygen, objectname_pfix +'CK0', placement_grid=pg, routing_grid_m1m2=rg12,
                                        devname_mos_boundary=devname_mos_boundary, devname_mos_body=devname_mos_body,
                                        devname_mos_dmy=devname_mos_dmy, m=m_clkh*2, m_dmy=m_clkh_dmy, origin=diffpair_origin)
    in_origin=laygen.get_xy(obj = ickbl0, gridname = pg)+ laygen.get_xy(obj = ickbl0.template, gridname = pg) * np.array([0, 1])
    [iinbl0, iindmyl0, iofstl0, iinl0, iinr0, iofstr0, iindmyr0, iinbr0] = \
        generate_diff_mos_ofst(laygen, objectname_pfix+'IN0', placement_grid=pg, routing_grid_m1m2=rg12,
                          devname_mos_boundary=devname_mos_boundary, devname_mos_body=devname_mos_body,
                          devname_mos_dmy=devname_mos_dmy, m=m_in, m_ofst=m_ofst, m_dmy=m_in_dmy, origin=in_origin)

    #route
    #tap to cs
    for _ick0 in ick0.elements[:, 0]:
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=_ick0.pins['S0'], refobj1=itap0.pins['TAP0'], direction='y')
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=ick0.elements[-1, 0].pins['S1'], refobj1=itap0.pins['TAP0'], direction='y')
    #cs to in (tail)
    for i in range(min(m_clkh-1, m_in-1)):
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 1], gridname0=rg23,
                     refobj0=iinl0.elements[m_in-i-1, 0].pins['D0'], via0=[0, 0],
                     refobj1=ick0.elements[m_clkh-i-1, 0].pins['D0'], via1=[0, 0])
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 1], gridname0=rg23,
                     refobj0=iinr0.elements[m_in-i-1, 0].pins['D0'], via0=[0, 0],
                     refobj1=ick0.elements[m_clkh+i, 0].pins['D0'], via1=[0, 0])
    #biascap for ofst
    laygen.route(name=None, xy0=[0, 0], xy1=[2, 0], gridname0=rg12, 
                 refobj0=iindmyl0.elements[1, 0].pins['G0'], refobj1=iindmyl0.elements[-1, 0].pins['G0'])
    laygen.route(name=None, xy0=[0, 0], xy1=[2, 0], gridname0=rg12,
                 refobj0=iindmyr0.elements[1, 0].pins['G0'], refobj1=iindmyr0.elements[-1, 0].pins['G0'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, 
                 refobj0=iindmyl0.elements[0, 0].pins['G0'], refobj1=iindmyl0.elements[0, 0].pins['D0'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=iindmyl0.elements[-1, 0].pins['G0'], refobj1=iindmyl0.elements[-1, 0].pins['D0'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=iindmyr0.elements[0, 0].pins['G0'], refobj1=iindmyr0.elements[0, 0].pins['D0'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=iindmyr0.elements[-1, 0].pins['G0'], refobj1=iindmyr0.elements[-1, 0].pins['D0'])
    for _dmyl, _dmyr in zip(iindmyl0.elements[1:-1, 0], iindmyr0.elements[1:-1, 0]):
        laygen.via(name=None, xy=[0, 0], refobj=_dmyl.pins['G0'], gridname=rg12)
        laygen.via(name=None, xy=[0, 0], refobj=_dmyr.pins['G0'], gridname=rg12)
    #dmy route
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, 
                 refobj0=iindmyl0.elements[0, 0].pins['S0'], refobj1=itap0.elements[0, 0].pins['TAP0'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=iindmyl0.elements[0, 0].pins['D0'], refobj1=itap0.elements[1, 0].pins['TAP0'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=iindmyr0.elements[0, 0].pins['S0'], refobj1=itap0.elements[-1, 0].pins['TAP1'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=iindmyr0.elements[0, 0].pins['D0'], refobj1=itap0.elements[-1, 0].pins['TAP0'])
    return [itapbl0, itap0, itapbr0, ickbl0, ick0, ickbr0, iinbl0, iindmyl0, iofstl0, iinl0, iinr0, iofstr0, iindmyr0, iinbr0]

def generate_salatch_regen(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m1m2_thick,
                   routing_grid_m2m3, routing_grid_m3m4,
                   devname_nmos_boundary, devname_nmos_body, devname_nmos_dmy,
                   devname_pmos_boundary, devname_pmos_body, devname_pmos_dmy,
                   devname_ptap_boundary, devname_ptap_body, devname_ntap_boundary, devname_ntap_body,
                   m_rgnp=2, m_rgnp_dmy=1, m_rstp=1, m_tap=12, m_buf=1, num_row_ptap=1, origin=np.array([0, 0])):
    """generate regenerative stage of SAlatch. N/P flipped for pmos type"""
    pg = placement_grid
    rg12 = routing_grid_m1m2
    rg12t = routing_grid_m1m2_thick
    rg23 = routing_grid_m2m3
    rg34 = routing_grid_m3m4
    pfix = objectname_pfix

    m_rgnn = m_rgnp + 2 * m_rstp - 1
    m_rgnn_dmy = m_rgnp_dmy

    #placement
    #tap
    [itapbln0, itapn0, itapbrn0] = generate_tap(laygen, objectname_pfix=pfix+'NTAP0', 
                                                placement_grid=pg, routing_grid_m1m2_thick=rg12t,
                                                devname_tap_boundary=devname_ptap_boundary, devname_tap_body=devname_ptap_body,
                                                m=m_tap, origin=origin)
    rgnbody_origin = laygen.get_xy(obj = itapbln0, gridname = pg) + laygen.get_xy(obj = itapbln0.template, gridname = pg) * np.array([0, 1])
    #nmos row
    imbln0 = laygen.relplace(name="I" + pfix + 'BLN0', templatename=devname_nmos_boundary, gridname=pg, xy=rgnbody_origin)
    imbufln0 = laygen.relplace(name="I" + pfix + 'BUFLN0', templatename=devname_nmos_body, gridname=pg, refobj=imbln0, shape=[m_buf, 1])
    refi=imbufln0
    if not m_rgnn_dmy==0:
        imdmyln0 = laygen.relplace(name="I" + pfix + 'DMYLN0', templatename=devname_nmos_dmy, gridname=pg, refobj=imbufln0, shape=[m_rgnn_dmy, 1])
        refi=imdmyln0
    else:
        imdmyln0=None
    imln0 = laygen.relplace(name="I" + pfix + 'LN0', templatename=devname_nmos_body, gridname=pg, refobj=refi, shape=[m_rgnn, 1])
    imln1 = laygen.relplace(name="I" + pfix + 'LN1', templatename=devname_nmos_dmy, gridname=pg, refobj=imln0)
    imrn1 = laygen.relplace(name="I" + pfix + 'RN1', templatename=devname_nmos_dmy, gridname=pg, refobj=imln1, transform='MY')
    imrn0 = laygen.relplace(name="I" + pfix + 'RN0', templatename=devname_nmos_body, gridname=pg, refobj=imrn1, shape=[m_rgnn, 1], transform='MY')
    refi=imrn0
    if not m_rgnn_dmy==0:
        imdmyrn0 = laygen.relplace(name="I" + pfix + 'DMYRN0', templatename=devname_nmos_dmy, gridname=pg, refobj=imrn0, shape=[m_rgnn_dmy, 1], transform='MY')
        refi=imdmyrn0
    imbufrn0 = laygen.relplace(name="I" + pfix + 'BUFRN0', templatename=devname_nmos_body, gridname=pg, refobj=refi, shape=[m_buf, 1], transform='MY')
    imbrn0 = laygen.relplace(name="I" + pfix + 'BRN0', templatename=devname_nmos_boundary, gridname=pg, refobj=imbufrn0, transform='MY')
    #pmos row
    imblp0 = laygen.relplace(name="I" + pfix + 'BLP0', templatename=devname_pmos_boundary, gridname=pg, refobj=imbln0, direction='top', transform='MX')
    imbuflp0 = laygen.relplace(name="I" + pfix + 'BUFLP0', templatename=devname_pmos_body, gridname=pg, refobj=imblp0, shape=[m_buf, 1], transform='MX')
    refi=imbufln0
    if not m_rgnp_dmy==0:
        imdmylp0 = laygen.relplace(name="I" + pfix + 'DMYLP0', templatename=devname_pmos_body, gridname=pg, refobj=imbuflp0, shape=[m_rgnp_dmy, 1], transform='MX')
        refi=imdmylp0
    else:
        imdmylp0=None
    imlp0 = laygen.relplace(name="I" + pfix + 'LP0', templatename=devname_pmos_body, gridname=pg, refobj=imdmylp0, shape=[m_rgnp, 1], transform='MX')
    imrstlp0 = laygen.relplace(name="I" + pfix + 'RSTLP0', templatename=devname_pmos_body, gridname=pg, refobj=imlp0, shape=[m_rstp, 1], transform='MX')
    imrstlp1 = laygen.relplace(name="I" + pfix + 'RSTLP1', templatename=devname_pmos_body, gridname=pg, refobj=imrstlp0, shape=[m_rstp, 1], transform='MX')
    imrstrp1 = laygen.relplace(name="I" + pfix + 'RSTRP1', templatename=devname_pmos_body, gridname=pg, refobj=imrstlp1, shape=[m_rstp, 1], transform='R180')
    imrstrp0 = laygen.relplace(name="I" + pfix + 'RSTRP0', templatename=devname_pmos_body, gridname=pg, refobj=imrstrp1, shape=[m_rstp, 1], transform='R180')
    imrp0 = laygen.relplace(name="I" + pfix + 'RP0', templatename=devname_pmos_body, gridname=pg, refobj=imrstrp0, shape=[m_rgnp, 1], transform='R180')
    refi=imrp0
    if not m_rgnp_dmy==0:
        imdmyrp0 = laygen.relplace(name="I" + pfix + 'DMYRP0', templatename=devname_pmos_body, gridname=pg, refobj=imrp0, shape=[m_rgnp_dmy, 1], transform='R180')
        refi = imdmyrp0
    else:
        imdmyrp0 = None
    imbufrp0 = laygen.relplace(name="I" + pfix + 'BUFRP0', templatename=devname_pmos_body, gridname=pg, refobj=imdmyrp0, shape=[m_buf, 1], transform='R180')
    imbrp0 = laygen.relplace(name="I" + pfix + 'BRP0', templatename=devname_pmos_boundary, gridname=pg, refobj=imbufrp0, transform='R180')
    #tap
    for i in range(num_row_ptap):
        tap_origin = laygen.get_xy(obj = imblp0, gridname = pg) + laygen.get_xy(obj=laygen.get_template(name = devname_ntap_boundary), gridname = pg) * np.array([0, 1]) * (i + 1)
        [itapbl0, itap0, itapbr0] = generate_tap(laygen, objectname_pfix=pfix+'PTAP0', placement_grid=pg, routing_grid_m1m2_thick=rg12t,
                                                 devname_tap_boundary=devname_ntap_boundary, devname_tap_body=devname_ntap_body,
                                                 m=m_tap, extend_rail=True, origin=tap_origin, transform='MX')

    #route
    #tap to pmos
    for i in range(m_rgnp):
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imlp0.elements[i, 0].pins['S0'], refobj1=itap0.pins['TAP0'], direction='y')
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imrp0.elements[i, 0].pins['S0'], refobj1=itap0.pins['TAP0'], direction='y')
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=imlp0.elements[-1, 0].pins['S1'], refobj1=itap0.pins['TAP0'], direction='y')
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=imrp0.elements[-1, 0].pins['S1'], refobj1=itap0.pins['TAP0'], direction='y')
    for i in range(m_rstp):
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imrstlp0.elements[i, 0].pins['S0'], refobj1=itap0.pins['TAP0'], direction='y')
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imrstlp1.elements[i, 0].pins['S0'], refobj1=itap0.pins['TAP0'], direction='y')
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imrstrp1.elements[i, 0].pins['S0'], refobj1=itap0.pins['TAP0'], direction='y')
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imrstrp0.elements[i, 0].pins['S0'], refobj1=itap0.pins['TAP0'], direction='y')
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=imrstlp0.elements[-1, 0].pins['S1'], refobj1=itap0.pins['TAP0'], direction='y')
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=imrstlp1.elements[-1, 0].pins['S1'], refobj1=itap0.pins['TAP0'], direction='y')
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=imrstrp1.elements[-1, 0].pins['S1'], refobj1=itap0.pins['TAP0'], direction='y')
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=imrstrp0.elements[-1, 0].pins['S1'], refobj1=itap0.pins['TAP0'], direction='y')
    #gate-n
    rgln0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                       refobj0=imln0.elements[0, 0].pins['G0'], refobj1=imln0.elements[-1, 0].pins['G0'])
    for _mln in imln0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_mln.pins['G0'], gridname=rg12)
    rgrn0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                       refobj0=imrn0.elements[0, 0].pins['G0'], refobj1=imrn0.elements[-1, 0].pins['G0'])
    for _mrn in imrn0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_mrn.pins['G0'], gridname=rg12)

    #gate-p
    rglp0=laygen.route(None, xy0=[-2, 0], xy1=[0, 0], gridname0=rg12,
                       refobj0=imlp0.elements[0, 0].pins['G0'], refobj1=imlp0.elements[-1, 0].pins['G0'])
    for _mlp in imlp0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_mlp.pins['G0'], gridname=rg12)
    rgrp0=laygen.route(None, xy0=[-2, 0], xy1=[0, 0], gridname0=rg12,
                       refobj0=imrp0.elements[0, 0].pins['G0'], refobj1=imrp0.elements[-1, 0].pins['G0'])
    for _mrp in imrp0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_mrp.pins['G0'], gridname=rg12)
    #gate-pn vertical
    rglv0=laygen.route(name=None, xy0=[-1, 0], xy1=[-1, 0], gridname0=rg23,
                       refobj0=imlp0.elements[-1, 0].pins['G0'], via0=[0, 0], refobj1=imln0.elements[m_rgnp-1, 0].pins['G0'], via1=[0, 0])
    rgrv0=laygen.route(name=None, xy0=[-1, 0], xy1=[-1, 0], gridname0=rg23,
                       refobj0=imrp0.elements[-1, 0].pins['G0'], via0=[0, 0], refobj1=imrn0.elements[m_rgnp-1, 0].pins['G0'], via1=[0, 0])

    #drain-pn vertical
    rdlv0=laygen.route(name=None, xy0=[-2, 0], xy1=[-2, 1], gridname0=rg23,
                       refobj0=imlp0.elements[0, 0].pins['D0'], via0=[0, 0], refobj1=imln0.elements[0, 0].pins['D0'], via1=[0, 0])
    rdrv0=laygen.route(name=None, xy0=[-2, 0], xy1=[-2, 1], gridname0=rg23,
                       refobj0=imrp0.elements[0, 0].pins['D0'], via0=[0, 0], refobj1=imrn0.elements[0, 0].pins['D0'], via1=[0, 0])
    for _mlp, _mln in zip(imlp0.elements[:, 0], imln0.elements[:, 0]):
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 1], gridname0=rg23,
                     refobj0=_mlp.pins['D0'], via0=[0, 0], refobj1=_mln.pins['D0'], via1=[0, 0])
    for _mrp, _mrn in zip(imrp0.elements[:, 0], imrn0.elements[:, 0]):
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 1], gridname0=rg23,
                     refobj0=_mrp.pins['D0'], via0=[0, 0], refobj1=_mrn.pins['D0'], via1=[0, 0])
    for i in range(m_rstp):
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 1], gridname0=rg23,
                    refobj0=imrstlp0.elements[i, 0].pins['D0'], via0=[0, 0],
                    refobj1=imln0.elements[i+m_rgnp, 0].pins['D0'], via1=[0, 0])
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 1], gridname0=rg23,
                    refobj0=imrstrp0.elements[i, 0].pins['D0'], via0=[0, 0],
                    refobj1=imrn0.elements[i+m_rgnp, 0].pins['D0'], via1=[0, 0])
    #gate-clkp
    rgrstp0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, 
                         refobj0=imrstlp0.pins['G0'], refobj1=imrstrp0.pins['G0'])
    for i in range(m_rstp):
        laygen.via(name=None, xy=[0, 0], refobj=imrstlp0.elements[i, 0].pins['G0'], gridname=rg12)
        laygen.via(name=None, xy=[0, 0], refobj=imrstlp1.elements[i, 0].pins['G0'], gridname=rg12)
        laygen.via(name=None, xy=[0, 0], refobj=imrstrp1.elements[i, 0].pins['G0'], gridname=rg12)
        laygen.via(name=None, xy=[0, 0], refobj=imrstrp0.elements[i, 0].pins['G0'], gridname=rg12)
    #drain-p
    rdlp0=laygen.route(name=None, xy0=[-2, 0], xy1=[0, 0], gridname0=rg12,
                       refobj0=imlp0.elements[0, 0].pins['D0'], refobj1=imrstlp0.elements[-1, 0].pins['D0'])
    for _m in imlp0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_m.pins['D0'], gridname=rg12)
    for _m in imrstlp0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_m.pins['D0'], gridname=rg12)
    rdrp0=laygen.route(name=None, xy0=[-2, 0], xy1=[0, 0], gridname0=rg12,
                       refobj0=imrp0.elements[0, 0].pins['D0'], refobj1=imrstrp0.elements[-1, 0].pins['D0'])
    for _m in imrp0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_m.pins['D0'], gridname=rg12)
    for _m in imrstrp0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_m.pins['D0'], gridname=rg12)
    #cross-coupled route and via
    xyg0=laygen.get_xy(obj = rglv0, gridname = rg34, sort=True)[0]
    xyd0=laygen.get_xy(obj = rdlv0, gridname = rg34, sort=True)[0]
    xyg1=laygen.get_xy(obj = rgrv0, gridname = rg34, sort=True)[0]
    xyd1=laygen.get_xy(obj = rdrv0, gridname = rg34, sort=True)[0]
    laygen.route(name=None, xy0=[xyd0[0], xyg0[1]], xy1=[xyd1[0], xyg0[1]], gridname0=rg34)
    laygen.route(name=None, xy0=[xyd0[0], xyg0[1]+1], xy1=[xyd1[0], xyg0[1]+1], gridname0=rg34)
    laygen.via(name=None, xy=[xyg0[0], xyg0[1]], gridname=rg34)
    laygen.via(name=None, xy=[xyd1[0], xyg0[1]], gridname=rg34)
    laygen.via(name=None, xy=[xyd0[0], xyg0[1]+1], gridname=rg34)
    laygen.via(name=None, xy=[xyg1[0], xyg0[1]+1], gridname=rg34)
    #source/drain-n
    rdln0=laygen.route(name=None, xy0=[-2, 1], xy1=[0, 1], gridname0=rg12,
                       refobj0=imln0.elements[0, 0].pins['D0'], refobj1=imln0.elements[-1, 0].pins['D0'])
    for _m in imln0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 1], refobj=_m.pins['D0'], gridname=rg12)
    rdrn0=laygen.route(name=None, xy0=[-2, 1], xy1=[0, 1], gridname0=rg12,
                       refobj0=imrn0.elements[0, 0].pins['D0'], refobj1=imrn0.elements[-1, 0].pins['D0'])
    for _m in imrn0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 1], refobj=_m.pins['D0'], gridname=rg12)
    rsln0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                       refobj0=imln0.elements[0, 0].pins['S0'], refobj1=imln1.elements[0, 0].pins['S0'])
    for _m in imln0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_m.pins['S0'], gridname=rg12)
    laygen.via(name=None, xy=[0, 0], refobj=imln1.elements[0, 0].pins['S0'], gridname=rg12)
    rsrn0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                      refobj0=imrn0.elements[0, 0].pins['S0'],
                      refobj1=imrn1.elements[0, 0].pins['S0'])
    for _m in imrn0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_m.pins['S0'], gridname=rg12)
    laygen.via(name=None, xy=[0, 0], refobj=imrn1.elements[0, 0].pins['S0'], gridname=rg12)
    #tap to rgnn
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=imln1.elements[0, 0].pins['D0'], refobj1=itapn0.elements[0, 0].pins['TAP0'], direction='y')
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=imln1.elements[0, 0].pins['S1'], refobj1=itapn0.elements[0, 0].pins['TAP0'], direction='y')
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=imrn1.elements[0, 0].pins['D0'], refobj1=itapn0.elements[0, 0].pins['TAP0'], direction='y')
    #buf tap to rgnn
    for i in range(m_buf):
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imbufln0.elements[i, 0].pins['S0'], refobj1=itapn0.elements[i, 0].pins['TAP0'], direction='y')
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imbufrn0.elements[i, 0].pins['S0'], refobj1=itapn0.elements[m_tap-i-1, 0].pins['TAP1'], direction='y')
        laygen.route(name=None, xy0=[0, 0], xy1=np.array([0, 0]), gridname0=rg12,
                     refobj0=imbuflp0.elements[i, 0].pins['S0'], refobj1=itap0.elements[i, 0].pins['TAP0'], direction='y')
        laygen.route(name=None, xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg12,
                     refobj0=imbufrp0.elements[i, 0].pins['S0'], refobj1=itap0.elements[m_tap-i-1, 0].pins['TAP1'], direction='y')
    #buf-gate
    for i in range(m_buf):
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imbufln0.elements[i, 0].pins['G0'], refobj1=imbuflp0.elements[i, 0].pins['G0'], direction='y')
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imbufrn0.elements[i, 0].pins['G0'], refobj1=imbufrp0.elements[i, 0].pins['G0'], direction='y')
    #buf-gate(horizontal)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([2*m_rgnn_dmy, 0]), gridname0=rg23,
                 refinstname0=imbufln0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbufln0.name, refpinname1='G0', refinstindex1=np.array([m_buf-1, 0]), via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([2*m_rgnn_dmy, 0]), gridname0=rg23,
                 refinstname0=imbufrn0.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbufrn0.name, refpinname1='G0', refinstindex1=np.array([m_buf-1, 0]), via1=[[0, 0]])
    for i in range(m_buf):
        laygen.via(None, np.array([0, 0]), refinstname=imbufln0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg12)
        laygen.via(None, np.array([0, 0]), refinstname=imbufrn0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg12)
    #buf-drain
    for i in range(m_buf):
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg23,
                     refinstname0=imbufln0.name, refpinname0='D0', refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=imbuflp0.name, refpinname1='D0', refinstindex1=np.array([i, 0]), via1=[[0, 0]])
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg23,
                     refinstname0=imbufrn0.name, refpinname0='D0', refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=imbufrp0.name, refpinname1='D0', refinstindex1=np.array([i, 0]), via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg23,
                 refinstname0=imbufln0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbufln0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]),
                 endstyle0="extend", endstyle1="extend")
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg23,
                 refinstname0=imbufrn0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbufrn0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]),
                 endstyle0="extend", endstyle1="extend")
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg23,
                 refinstname0=imbuflp0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbuflp0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg23,
                 refinstname0=imbufrp0.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=imbufrp0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]))
    for i in range(m_buf):
        laygen.via(None, np.array([0, 0]), refinstname=imbufln0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg12)
        laygen.via(None, np.array([0, 1]), refinstname=imbuflp0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg12)
        laygen.via(None, np.array([0, 0]), refinstname=imbufrn0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg12)
        laygen.via(None, np.array([0, 1]), refinstname=imbufrp0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg12)
    #dmy-p
    for i in range(m_rgnp_dmy):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg12,
                     refinstname0=imdmylp0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=itap0.name, refpinname1='TAP0', refinstindex1=np.array([i, 0]),
                     direction='y'
                     )
        laygen.via(None, np.array([0, 0]), refinstname=imdmylp0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg12)
        laygen.via(None, np.array([0, 0]), refinstname=imdmylp0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg12)
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg12,
                     refinstname0=imdmyrp0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=itap0.name, refpinname1='TAP0', refinstindex1=np.array([m_tap-i, 0]),
                     direction='y'
                     )
        laygen.via(None, np.array([0, 0]), refinstname=imdmyrp0.name, refpinname='G0', refinstindex=np.array([i, 0]), gridname=rg12)
        laygen.via(None, np.array([0, 0]), refinstname=imdmyrp0.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg12)
    #dmy-n
    for i in range(m_rgnn_dmy):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg12,
                     refinstname0=imdmyln0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=itapn0.name, refpinname1='TAP0', refinstindex1=np.array([i, 0]),
                     direction='y'
                     )
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg12,
                     refinstname0=imdmyln0.name, refpinname0='D0', refinstindex0=np.array([i, 0]),
                     refinstname1=itapn0.name, refpinname1='TAP0', refinstindex1=np.array([i+1, 0]),
                     direction='y'
                     )
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg12,
                     refinstname0=imdmyrn0.name, refpinname0='S0', refinstindex0=np.array([i, 0]),
                     refinstname1=itapn0.name, refpinname1='TAP0', refinstindex1=np.array([m_tap-i, 0]),
                     direction='y'
                     )
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg12,
                     refinstname0=imdmyrn0.name, refpinname0='D0', refinstindex0=np.array([i, 0]),
                     refinstname1=itapn0.name, refpinname1='TAP0', refinstindex1=np.array([m_tap-i-1, 0]),
                     direction='y'
                     )
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
                          m_in=4, m_ofst=2, m_clkh=2, m_rgnn=2, m_rstn=1, m_buf=1, num_vert_pwr=20, num_row_ptap=1, origin=np.array([0, 0])):
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
    #mainpair_origin = laygen.get_xy(obj = iofstinbl0, gridname = pg) + laygen.get_xy(obj = iofstinbl0.template, gridname = pg) * np.array([0, 1])
    mainpair_origin = origin
    [imaintapbl0, imaintap0, imaintapbr0, imainckbl0, imainck0, imainckbr0,
     imaininbl0, imainindmyl0, iofstinl0, imaininl0, imaininr0, iofstinr0, imainindmyr0, imaininbr0]=\
    generate_clkdiffpair_ofst(laygen, objectname_pfix=objectname_pfix+'MAIN0', placement_grid=pg,
                         routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick, routing_grid_m2m3=rg_m2m3,
                         devname_mos_boundary=devname_pmos_boundary, devname_mos_body=devname_pmos_body, devname_mos_dmy=devname_pmos_dmy,
                         devname_tap_boundary=devname_ntap_boundary, devname_tap_body=devname_ntap_body,
                         m_in=m_in, m_ofst=m_ofst, m_in_dmy=m_in_dmy-m_ofst, m_clkh=m_clkh, m_clkh_dmy=m_clkh_dmy, m_tap=m_tap, 
                         origin=mainpair_origin)
    #regen
    regen_origin = laygen.get_xy(obj = imaininbl0, gridname = pg) + laygen.get_xy(obj = imaininbl0.template, gridname = pg) * np.array([0, 1])

    [irgntapbln0, irgntapn0, irgntapbrn0,
     irgnbln0, irgnbufln0, irgndmyln0, irgnln0, irgnln1, irgnrn1, irgnrn0, irgndmyrn0, irgnbufrn0, irgnbrn0,
     irgnblp0, irgnbuflp0, irgndmylp0, irgnlp0, irgnrstlp0, irgnrstlp1, irgnrstrp1, irgnrstrp0, irgnrp0, irgndmyrp0, irgnbufrp0, irgnbrp0,
     irgntapbl0, irgntap0, irgntapbr0]=\
    generate_salatch_regen(laygen, objectname_pfix=objectname_pfix+'RGN0', placement_grid=pg,
                           routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                           devname_nmos_boundary=devname_pmos_boundary, devname_nmos_body=devname_pmos_body, devname_nmos_dmy=devname_pmos_dmy,
                           devname_pmos_boundary=devname_nmos_boundary, devname_pmos_body=devname_nmos_body, devname_pmos_dmy=devname_nmos_dmy,
                           devname_ptap_boundary=devname_ntap_boundary, devname_ptap_body=devname_ntap_body,
                           devname_ntap_boundary=devname_ptap_boundary, devname_ntap_body=devname_ptap_body,
                           m_rgnp=m_rgnn, m_rgnp_dmy=m_rgnn_dmy, m_rstp=m_rstn, m_tap=m_tap, m_buf=m_buf, num_row_ptap=num_row_ptap, origin=regen_origin)
    #irgnbuflp1
    #regen-diff pair connections
    for i in range(m_rstn):
        rintm=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                           refinstname0=irgnln1.name, refpinname0='S0', refinstindex0=np.array([-i, 0]), via0=[[0, 0]],
                           refinstname1=irgnrstlp1.name, refpinname1='S0', refinstindex1=np.array([m_rstn-1-i, 0]), via1=[[0, 0]])
        rintp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                           refinstname0=irgnrn1.name, refpinname0='S0', refinstindex0=np.array([-i, 0]), via0=[[0, 0]],
                           refinstname1=irgnrstrp1.name, refpinname1='S0', refinstindex1=np.array([m_rstn-1-i, 0]), via1=[[0, 0]])
    for i in range(min(m_in, m_rgnn+m_rstn)):
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2, 1]), xy1=np.array([-2, 0]), gridname0=rg_m2m3,
                     refinstname0=imaininl0.name, refpinname0='S0', refinstindex0=np.array([m_in - 1 - i + 1, 0]), via0=[[0, 0]],
                     refinstname1=irgnln1.name, refpinname1='S0', refinstindex1=np.array([-i + 1, 0]), via1=[[0, 0]])
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2, 1]), xy1=np.array([-2, 0]), gridname0=rg_m2m3,
                     refinstname0=imaininr0.name, refpinname0='S0', refinstindex0=np.array([m_in - 1 - i + 1, 0]), via0=[[0, 0]],
                     refinstname1=irgnrn1.name, refpinname1='S0', refinstindex1=np.array([-i + 1, 0]), via1=[[0, 0]])
    laygen.boundary_pin_from_rect(rintp, gridname=rg_m2m3, name='INTP', layer=laygen.layers['pin'][3], size=2,
                                  direction='top')
    laygen.boundary_pin_from_rect(rintm, gridname=rg_m2m3, name='INTM', layer=laygen.layers['pin'][3], size=2,
                                  direction='top')
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
    xy0=laygen.get_inst_pin_xy(imainck0.name, pinname='G0', gridname=rg_m2m3, index=np.array([m_clkh - 1, 0]), sort=True)[0]
    y0=laygen.get_xy(obj = imaintap0, gridname = rg_m3m4)[1]-1
    xy1=laygen.get_inst_pin_xy(irgnrstlp1.name, pinname='G0', gridname=rg_m2m3, index=np.array([m_clkh - 1, 0]), sort=True)[0]
    rclk=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0]+1, y0]), xy1=np.array([1, 0-4-1]), gridname0=rg_m2m3,
                      refinstname1=irgnrstlp1.name, refpinname1='G0', refinstindex1=np.array([m_rstn-1, 0])
                      )
    xy0=laygen.get_xy(obj = rclk, gridname = rg_m3m4, sort=True)
    #laygen.route(None, laygen.layers['metal'][4], xy0=xy0[1]+np.array([-2*m_rstn, 0]), xy1=xy0[1]+np.array([0, 0]), gridname0=rg_m3m4, via1=[[0, 0]])
    #rclk2 = laygen.route(None, laygen.layers['metal'][4], xy0=xy0[1]+np.array([0, 0]), xy1=xy0[1]+np.array([2*m_rstn, 0]), gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][4], xy0=xy0[1]+np.array([-1*l_clkb_m4, 0]), xy1=xy0[1]+np.array([0, 0]), gridname0=rg_m3m4, via1=[[0, 0]])
    rclk2 = laygen.route(None, laygen.layers['metal'][4], xy0=xy0[1]+np.array([0, 0]), xy1=xy0[1]+np.array([l_clkb_m4, 0]), gridname0=rg_m3m4)
    xy0=laygen.get_xy(obj = rclk2, gridname = rg_m4m5, sort=True)
    rclk3 = laygen.route(None, laygen.layers['metal'][5], xy0=xy0[0]+np.array([l_clkb_m4, 0]), xy1=xy0[0]+np.array([l_clkb_m4, 5]), gridname0=rg_m4m5, via0=[[0, 0]])
    laygen.boundary_pin_from_rect(rclk3, gridname=rg_m4m5, name='CLKB', layer=laygen.layers['pin'][5], size=4,
                                  direction='top')
    laygen.via(None, np.array([1, 0]), refinstname=imainck0.name, refpinname='G0', refinstindex=np.array([m_clkh-1, 0]), gridname=rg_m2m3)
    laygen.via(None, np.array([1, 0]), refinstname=irgnrstlp1.name, refpinname='G0', refinstindex=np.array([m_rstn-1, 0]), gridname=rg_m2m3)
    #input connection
    y0=laygen.get_xy(obj = imaintap0, gridname = rg_m3m4)[1]
    y1=laygen.get_xy(obj = irgntap0, gridname = rg_m2m3)[1]
    xy0=laygen.get_inst_pin_xy(imaininl0.name, pinname='G0', gridname=rg_m2m3, index=np.array([0, 0]), sort=True)[0]
    rinp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0]+1-1, y0]), xy1=np.array([1-1, 0]), gridname0=rg_m2m3,
                      refinstname1=imaininl0.name, refpinname1='G0', refinstindex1=np.array([0, 0]))
    laygen.boundary_pin_from_rect(rinp, gridname=rg_m3m4, name='INP', layer=laygen.layers['pin'][3], size=4,
                                  direction='bottom')
    laygen.via(None, np.array([1-1, 0]), refinstname=imaininl0.name, refpinname='G0', refinstindex=np.array([0, 0]), gridname=rg_m2m3)
    xy0=laygen.get_inst_pin_xy(imaininr0.name, pinname='G0', gridname=rg_m2m3, index=np.array([0, 0]), sort=True)[0]
    rinm=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0]-1+1, y0]), xy1=np.array([1-1, 0]), gridname0=rg_m2m3,
                      refinstname1=imaininr0.name, refpinname1='G0', refinstindex1=np.array([0, 0]))
    laygen.boundary_pin_from_rect(rinm, gridname=rg_m3m4, name='INM', layer=laygen.layers['pin'][3], size=4,
                                  direction='bottom')
    laygen.via(None, np.array([1-1, 0]), refinstname=imaininr0.name, refpinname='G0', refinstindex=np.array([0, 0]), gridname=rg_m2m3)
    #output connection (outp)
    x_center=laygen.get_xy(obj = rclk, gridname = rg_m3m4, sort=True)[0][0]
    y1=laygen.get_xy(obj = irgntap0, gridname = rg_m3m4)[1]-4
    xy0=laygen.get_inst_pin_xy(irgnbuflp0.name, pinname='D0', gridname=rg_m3m4, index=np.array([m_buf - 1, 0]), sort=True)[0]
    routp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0], y1+4]), xy1=np.array([0, 1]), gridname0=rg_m3m4,
                      refinstname1=irgnbuflp0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]),
                      direction='top')
    routp2=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xy0[0], y1]), xy1=np.array([x_center-l_clkb_m4-2, y1]),
                        gridname0=rg_m3m4, via0=[[0, 0]])
    routp2b=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xy0[0], y1+2]), xy1=np.array([x_center-l_clkb_m4-2, y1+2]),
                        gridname0=rg_m3m4, via0=[[0, 0]])
    xy1=laygen.get_xy(obj = routp2, gridname = rg_m4m5, sort=True)
    routp3 = laygen.route(None, laygen.layers['metal'][5], xy0=xy1[1], xy1=xy1[1]+np.array([0, 6]), gridname0=rg_m4m5, via0=[[0, 0]])
    routp3b = laygen.route(None, laygen.layers['metal'][5], xy0=xy1[1]+np.array([0, 2]), xy1=xy1[1]+np.array([0, 6]), gridname0=rg_m4m5, via0=[[0, 0]])
    laygen.boundary_pin_from_rect(routp3, gridname=rg_m4m5, name='OUTP', layer=laygen.layers['pin'][5], size=4,
                                  direction='top')
    #output connection (outm)
    y1=laygen.get_xy(obj = irgntap0, gridname = rg_m3m4)[1]-4
    xy0=laygen.get_inst_pin_xy(irgnbufrp0.name, pinname='D0', gridname=rg_m3m4, index=np.array([m_buf - 1, 0]), sort=True)[0]
    routm=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0], y1+4]), xy1=np.array([0, 1]), gridname0=rg_m3m4,
                      refinstname1=irgnbufrp0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]),
                      direction='top')
    routm2=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xy0[0], y1]), xy1=np.array([x_center+l_clkb_m4+2, y1]),
                        gridname0=rg_m3m4, via0=[[0, 0]])
    routm2b=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xy0[0], y1+2]), xy1=np.array([x_center+l_clkb_m4+2, y1+2]),
                        gridname0=rg_m3m4, via0=[[0, 0]])
    xy1=laygen.get_xy(obj = routm2, gridname = rg_m4m5, sort=True)
    routm3 = laygen.route(None, laygen.layers['metal'][5], xy0=xy1[0]+np.array([0, 0]), xy1=xy1[0]+np.array([0, 6]), gridname0=rg_m4m5, via0=[[0, 0]])
    routm3b = laygen.route(None, laygen.layers['metal'][5], xy0=xy1[0]+np.array([0, 2]), xy1=xy1[0]+np.array([0, 6]), gridname0=rg_m4m5, via0=[[0, 0]])
    laygen.boundary_pin_from_rect(routm3, gridname=rg_m4m5, name='OUTM', layer=laygen.layers['pin'][5], size=4,
                                  direction='top')
    #offset input connection
    y1=laygen.get_xy(obj = irgntap0, gridname = rg_m2m3)[1]
    xy0=laygen.get_inst_pin_xy(iofstinl0.name, pinname='G0', gridname=rg_m2m3, index=np.array([0, 0]), sort=True)[0]
    xy1=laygen.get_xy(obj = routp, gridname = rg_m2m3, sort=True)[0]
    rosp=laygen.route(None, laygen.layers['metal'][3], xy0=[xy1[0]+3, y1], xy1=[0, 0], gridname0=rg_m2m3, 
                      refobj1=iofstinl0, refpinname1='G0', direction='y', via1=[[0, 0]])
    laygen.boundary_pin_from_rect(rosp, gridname=rg_m3m4, name='OSP', layer=laygen.layers['pin'][3], size=4,
                                  direction='top')
    xy0=laygen.get_inst_pin_xy(iofstinr0.name, pinname='G0', gridname=rg_m2m3, index=np.array([0, 0]), sort=True)[0]
    xy1=laygen.get_xy(obj = routm, gridname = rg_m2m3, sort=True)[0]
    #rosm=laygen.route(None, laygen.layers['metal'][3], xy0=[xy1[0]-3, y1], xy1=[xy1[0]-3, xy0[1]], gridname0=rg_m2m3, via1=[[0, 0]])
    rosm=laygen.route(None, laygen.layers['metal'][3], xy0=[xy1[0]-3, y1], xy1=[0, 0], gridname0=rg_m2m3, 
                      refobj1=iofstinr0, refpinname1='G0', direction='y', via1=[[0, 0]])
    #laygen.route(None, laygen.layers['metal'][2], xy0=[0, 0], xy1=[xy1[0]-3, xy0[1]], gridname0=rg_m2m3,
    #             refinstname0=iofstinr0.name, refpinname0='G0', refinstindex0=np.array([0, 0]))
    laygen.boundary_pin_from_rect(rosm, gridname=rg_m3m4, name='OSM', layer=laygen.layers['pin'][3], size=4,
                                  direction='top')

    #VDD/VSS
    #num_vert_pwr = 20
    rvdd1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 1]), xy1=np.array([2*num_vert_pwr, 1]), gridname0=rg_m1m2_thick,
                        refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
    rvdd1b = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, -1]), xy1=np.array([2*num_vert_pwr, -1]), gridname0=rg_m1m2_thick,
                        refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
    rvdd2 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 1]), xy1=np.array([2*num_vert_pwr, 1]), gridname0=rg_m1m2_thick,
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
    #rvdd_pin_xy = laygen.get_xy(obj = rvdd, gridname = rg_m1m2_thick)
    rvdd1_pin_xy = laygen.get_xy(obj = rvdd1, gridname = rg_m1m2_thick)
    rvdd2_pin_xy = laygen.get_xy(obj = rvdd2, gridname = rg_m1m2_thick)
    rvss_pin_xy = laygen.get_xy(obj = rvss, gridname = rg_m1m2_thick)

    #laygen.pin(name='VDD0', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2_thick, netname='VDD')
    laygen.pin(name='VDD0', layer=laygen.layers['pin'][2], xy=rvdd1_pin_xy, gridname=rg_m1m2_thick, netname='VDD')
    laygen.pin(name='VDD1', layer=laygen.layers['pin'][2], xy=rvdd2_pin_xy, gridname=rg_m1m2_thick, netname='VDD')
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
                   xy=laygen.get_xy(obj = rvvss_l, gridname = rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VSS')
        laygen.pin(name='VSSR'+str(i), layer=laygen.layers['pin'][3],
                   xy=laygen.get_xy(obj = rvvss_r, gridname = rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VSS')

        rvvdd_l = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2*i-2, -1]), xy1=np.array([-2*i-2, -1]), gridname0=rg_m2m3_thick,
                               refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                               refinstname1=irgntap0.name, refpinname1='TAP0', refinstindex1=np.array([0, 0])
                       )
        rvvdd_r = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, -1]), xy1=np.array([2*i+2, -1]), gridname0=rg_m2m3_thick,
                               refinstname0=imaintap0.name, refpinname0='TAP1', refinstindex0=np.array([m_tap-1, 0]),
                               refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
        laygen.via(None, np.array([-2*i-2, 1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+2, 1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2*i-2, 1]), refinstname=irgntapn0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+2, 1]), refinstname=irgntapn0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2*i-2, -1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+2, -1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
                       gridname=rg_m2m3_thick)

        laygen.pin(name='VDDL'+str(i), layer=laygen.layers['pin'][3],
                   xy=laygen.get_xy(obj = rvvdd_l, gridname = rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VDD')
        laygen.pin(name='VDDR'+str(i), layer=laygen.layers['pin'][3],
                   xy=laygen.get_xy(obj = rvvdd_r, gridname = rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VDD')

def generate_salatch_pmos_wbnd(laygen, objectname_pfix, placement_grid, routing_grid_m1m2,
                                 routing_grid_m1m2_thick, routing_grid_m2m3, routing_grid_m2m3_thick, routing_grid_m3m4, routing_grid_m4m5,
                                 devname_ptap_boundary, devname_ptap_body,
                                 devname_nmos_boundary, devname_nmos_body, devname_nmos_dmy,
                                 devname_pmos_boundary, devname_pmos_body, devname_pmos_dmy,
                                 devname_ntap_boundary, devname_ntap_body,
                                 m_in=4, m_ofst=2, m_clkh=2, m_rgnn=2, m_rstn=1, m_buf=1,
                                 m_space_4x=0, m_space_2x=0, m_space_1x=0, num_row_ptap=1, origin=np.array([0, 0])):
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

    #spacing cells
    devname_space_1x = ['ntap_fast_space', 'pmos4_fast_space', 'pmos4_fast_space',
                        'ntap_fast_space', 'pmos4_fast_space', 'nmos4_fast_space'] + ['ptap_fast_space']*num_row_ptap
    devname_space_2x = ['ntap_fast_space_nf2', 'pmos4_fast_space_nf2', 'pmos4_fast_space_nf2',
                        'ntap_fast_space_nf2', 'pmos4_fast_space_nf2', 'nmos4_fast_space_nf2'] + ['ptap_fast_space_nf2']*num_row_ptap
    devname_space_4x = ['ntap_fast_space_nf4', 'pmos4_fast_space_nf4', 'pmos4_fast_space_nf4',
                        'ntap_fast_space_nf4', 'pmos4_fast_space_nf4', 'nmos4_fast_space_nf4'] + ['ptap_fast_space_nf4']*num_row_ptap
    transform_space = ['R0', 'R0', 'R0', 'R0', 'R0', 'MX'] + ['MX']*num_row_ptap
    m_space=m_space_4x*4+m_space_2x*2+m_space_1x*1
    #boundary generation
    m_bnd=m_tot*2*2+m_space*2+2 #2 for diff, 2 for nf, 2 for mos boundary
    [bnd_bottom, bnd_top, bnd_left, bnd_right]=generate_boundary(laygen, objectname_pfix='BND0',
        placement_grid=pg,
        devname_bottom = ['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
        shape_bottom = [np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
        devname_top = ['boundary_topleft', 'boundary_top', 'boundary_topright'],
        shape_top = [np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
        devname_left = ['ntap_fast_left', 'pmos4_fast_left', 'pmos4_fast_left',
                        'ntap_fast_left', 'pmos4_fast_left', 'nmos4_fast_left'] + ['ptap_fast_left']*num_row_ptap,
        transform_left=['R0', 'R0', 'R0', 'R0', 'R0', 'MX'] + ['MX']*num_row_ptap,
        devname_right=['ntap_fast_right', 'pmos4_fast_right', 'pmos4_fast_right',
                       'ntap_fast_right','pmos4_fast_right','nmos4_fast_right']+['ptap_fast_right']*num_row_ptap,
        transform_right = ['R0', 'R0', 'R0', 'R0', 'R0', 'MX']+['MX']*num_row_ptap,
        origin=np.array([0, 0]))
    #space generation
    spl_origin = laygen.get_xy(obj = bnd_bottom[0], gridname = pg) + laygen.get_xy(obj = bnd_bottom[0].template, gridname = pg)
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
            if m_space_1x==0 and m_space_2x==0:
                ispl4x.append(laygen.place(name="ISA0SPL4X0", templatename=d, gridname=pg, xy=spl_origin,
                                          shape=np.array([m_space_4x, 1]), transform=transform_space[i]))
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
    spr_origin = laygen.get_xy(obj = bnd_bottom[-1], gridname = pg) \
                 + laygen.get_xy(obj = bnd_bottom[-1].template, gridname = pg) * np.array([0, 1]) \
                 - laygen.get_xy(obj=laygen.get_template(name = 'nmos4_fast_space'), gridname = pg) * np.array([m_space, 0])
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
    sa_origin = origin+laygen.get_xy(obj = bnd_bottom[0], gridname = pg)+laygen.get_xy(obj = bnd_bottom[0].template, gridname = pg)\
                + laygen.get_xy(obj=laygen.get_template(name = 'nmos4_fast_space'), gridname = pg) * m_space * np.array([1, 0])

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
                     num_vert_pwr = m_space_4x * 2, num_row_ptap=num_row_ptap, origin=sa_origin)


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
    cellname = 'salatch_pmos'
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
        m_sa=sizedict['salatch']['m']
        m_rst_sa=sizedict['salatch']['m_rst']
        m_rgnn_sa=sizedict['salatch']['m_rgnn']
        m_buf_sa=sizedict['salatch']['m_buf']
        if 'num_row_ptap' in sizedict['salatch']:
            num_row_ptap=sizedict['salatch']['num_row_ptap']
    m_in=int(m_sa/2)            #4
    m_clkh=m_in #max(1, m_in)                 #4
    m_rstn=int(m_rst_sa/2)                    #1
    m_buf=int(m_buf_sa/2)
    m_rgnn=int(m_rgnn_sa/2) 
    m_ofst=1
    num_rot_ptap=1 #increase if you need to insert additional taps for grid alignment

    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)

    sa_origin=np.array([0, 0])

    #salatch body
    # 1. generate without spacing
    generate_salatch_pmos_wbnd(laygen, objectname_pfix='SA0',
                                placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick,
                                routing_grid_m2m3=rg_m2m3, routing_grid_m2m3_thick=rg_m2m3_thick, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5,
                                devname_ptap_boundary='ptap_fast_boundary', devname_ptap_body='ptap_fast_center_nf1',
                                devname_nmos_boundary='nmos4_fast_boundary', devname_nmos_body='nmos4_fast_center_nf2',
                                devname_nmos_dmy='nmos4_fast_dmy_nf2',
                                devname_pmos_boundary='pmos4_fast_boundary', devname_pmos_body='pmos4_fast_center_nf2',
                                devname_pmos_dmy='pmos4_fast_dmy_nf2',
                                devname_ntap_boundary='ntap_fast_boundary', devname_ntap_body='ntap_fast_center_nf1',
                                m_in=m_in, m_ofst=m_ofst, m_clkh=m_clkh, m_rgnn=m_rgnn, m_rstn=m_rstn, m_buf=m_buf,
                                m_space_4x=10, m_space_2x=0, m_space_1x=0, num_row_ptap=num_row_ptap, origin=sa_origin)
    laygen.add_template_from_cell()
    # 2. calculate spacing param and regenerate
    x0 = 2*laygen.templates.get_template('capdac', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0]
    m_space = int(round(x0 / 2 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))+10*4
    m_space_4x = int(m_space / 4)
    m_space_2x = int((m_space - m_space_4x * 4) / 2)
    m_space_1x = int(m_space - m_space_4x * 4 - m_space_2x * 2)
    #print("debug", x0, laygen.templates.get_template('capdac', libname=workinglib).xy[1][0] \
    #        , laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
    #        , laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0], m_space, m_space_4x, m_space_2x, m_space_1x)
    
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_salatch_pmos_wbnd(laygen, objectname_pfix='SA0',
                                placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick,
                                routing_grid_m2m3=rg_m2m3, routing_grid_m2m3_thick=rg_m2m3_thick, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5,
                                devname_ptap_boundary='ptap_fast_boundary', devname_ptap_body='ptap_fast_center_nf1',
                                devname_nmos_boundary='nmos4_fast_boundary', devname_nmos_body='nmos4_fast_center_nf2',
                                devname_nmos_dmy='nmos4_fast_dmy_nf2',
                                devname_pmos_boundary='pmos4_fast_boundary', devname_pmos_body='pmos4_fast_center_nf2',
                                devname_pmos_dmy='pmos4_fast_dmy_nf2',
                                devname_ntap_boundary='ntap_fast_boundary', devname_ntap_body='ntap_fast_center_nf1',
                                m_in=m_in, m_ofst=m_ofst, m_clkh=m_clkh, m_rgnn=m_rgnn, m_rstn=m_rstn, m_buf=m_buf,
                                m_space_4x=m_space_4x, m_space_2x=m_space_2x, m_space_1x=m_space_1x, num_row_ptap=num_row_ptap, origin=sa_origin)
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

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

"""
    Strong-Arm layout generator (new version), Using GridLayoutGenerator2
"""
import laygo
import numpy as np
import yaml
import os
#import logging;logging.basicConfig(level=logging.DEBUG)

def create_ana_nmos(laygen, place_grid, route_grid_m1m2, nf, nf_dmy, mn=np.array([0, 0]), ref=None, transform='R0'):
    #grids
    pg = place_grid
    rg12 = route_grid_m1m2
    #device names and internal parameters
    dnbl = 'nmos4_fast_boundary'
    if nf == 1:
        dnc = 'nmos4_fast_center_nf1_left'
        m = 1
    else:
        dnc = 'nmos4_fast_center_nf2'
        m = int(nf / 2)
    dnbr = 'nmos4_fast_boundary'
    dnsp = 'nmos4_fast_space'
    if nf_dmy == 1:
        dnd = 'nmos4_fast_dmy_nf1'
        m_dmy = 1
    else:
        dnd = 'nmos4_fast_dmy_nf2'
        m_dmy = int(nf / 2)

    dev_bl0 = laygen.place(gridname=pg, cellname=dnbl, mn=mn, ref=ref, shape=[1, 1], transform=transform)
    ref = dev_bl0.right
    if m_dmy == 0:
        dev_dl0 = None
        dev_core0 = laygen.place(gridname=pg, cellname=dnd, ref=ref, shape=[m_dmy, 1], transform=transform)
        ref = dev_dl0.right
    else:
        dev_dl0 = None
    dev_core0 = laygen.place(gridname=pg, cellname=dnc, ref=ref, shape=[m, 1], transform=transform)
    dev_br0 = laygen.place(gridname=pg, cellname=dnbr, ref=dev_core0.right, shape=[1, 1], transform=transform)
    if nf == 1:
        dev_br0 = laygen.place(gridname=pg, cellname=dnsp, ref=dev_br0.right, shape=[1, 1], transform=transform)
    return {'dev': [dev_bl0, dev_core0, dev_br0], 'core': dev_core0}

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
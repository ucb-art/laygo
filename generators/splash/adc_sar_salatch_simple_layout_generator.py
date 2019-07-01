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

"""Simple nmos type salatch layout generator
"""
import laygo
import numpy as np
import os
import yaml

def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin"""
    rvdd0_pin_xy = laygen.get_inst_pin_coord(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_coord(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_coord(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_coord(inst_right.name, 'VSS', gridname, sort=True)

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=gridname)

def generate_tap(laygen, objectname_pfix, placement_grid, routing_grid_m1m2_thick, devname_tap_boundary, devname_tap_body,
                 m=1, origin=np.array([0,0]), transform='R0'):
    """generate a tap row for body connection"""
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

def generate_diff_mos(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, devname_mos_boundary, devname_mos_body,
                      devname_mos_dmy, m=1, m_dmy=0, origin=np.array([0,0])):
    """generate an analog differential mos structure with dummmies """
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
        imdmyl0=None
    iml0 = laygen.relplace(name="I" + pfix + '0', templatename=devname_mos_body, gridname=pg, refobj=refi, shape=[m, 1])
    imr0 = laygen.relplace(name="I" + pfix + '1', templatename=devname_mos_body, gridname=pg, refobj=iml0, shape=[m, 1], transform='MY')
    refi=imr0
    if not m_dmy==0:
        imdmyr0 = laygen.relplace(name="I" + pfix + 'DMYR0', templatename=devname_mos_dmy, gridname=pg, refobj=refi, shape=[m_dmy, 1], transform='MY')
        refi=imdmyr0
    else:
        imdmyr0=None
    imbr0 = laygen.relplace(name="I" + pfix + 'BR0', templatename=devname_mos_boundary, gridname=pg, refobj=refi, transform='MY')
    mdl=iml0.elements[:, 0]
    mdr=imr0.elements[:, 0]

    #route
    #gate
    rgl0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=mdl[0].pins['G0'], refobj1=mdl[-1].pins['G0'])
    rgr0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=mdr[0].pins['G0'], refobj1=mdr[-1].pins['G0'])
    for _mdl, _mdr in zip(mdl, mdr):
        laygen.via(name=None, xy=[0, 0], refobj=_mdl.pins['G0'], gridname=rg12)
        laygen.via(name=None, xy=[0, 0], refobj=_mdr.pins['G0'], gridname=rg12)
    #drain
    rdl0=laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12, refobj0=mdl[0].pins['D0'], refobj1=mdl[-1].pins['D0'])
    rdr0=laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12, refobj0=mdr[-1].pins['D0'], refobj1=mdr[0].pins['D0'])
    for _mdl, _mdr in zip(mdl, mdr):
        laygen.via(name=None, xy=[0, 1], refobj=_mdl.pins['D0'], gridname=rg12)
        laygen.via(name=None, xy=[0, 1], refobj=_mdr.pins['D0'], gridname=rg12)
    #source
    rs0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=mdl[0].pins['S0'], refobj1=mdr[0].pins['S0'])
    for _mdl, _mdr in zip(mdl, mdr):
        laygen.via(name=None, xy=[0, 0], refobj=_mdl.pins['S0'], gridname=rg12)
        laygen.via(name=None, xy=[0, 0], refobj=_mdr.pins['S0'], gridname=rg12)
    laygen.via(name=None, xy=[0, 0], refobj=mdl[-1].pins['S1'], gridname=rg12)
    laygen.via(name=None, xy=[0, 0], refobj=mdr[-1].pins['S1'], gridname=rg12)
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
    return [imbl0, imdmyl0, iml0, imr0, imdmyr0, imbr0]

def generate_clkdiffpair(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m1m2_thick, routing_grid_m2m3,
                         devname_mos_boundary, devname_mos_body, devname_mos_dmy, devname_tap_boundary, devname_tap_body,
                         m_in=2, m_in_dmy=1, m_clkh=2, m_clkh_dmy=1, m_tap=12, origin=np.array([0, 0])):
    """generate a clocked differential pair"""
    pg = placement_grid
    rg12 = routing_grid_m1m2
    rg12t = routing_grid_m1m2_thick
    rg23 = routing_grid_m2m3
    m_clk=m_clkh*2

    #placement
    [itapbl0, itap0, itapbr0] = generate_tap(laygen, objectname_pfix=objectname_pfix+'NTAP0', placement_grid=pg,
                                             routing_grid_m1m2_thick=rg12t,
                                             devname_tap_boundary=devname_tap_boundary, devname_tap_body=devname_tap_body,
                                             m=m_tap, origin=origin)
    diffpair_origin = laygen.get_inst_xy(itapbl0.name, pg) + laygen.get_template_size(itapbl0.cellname, pg) * np.array([0, 1])
    [ickbl0, ickdmyl0, ick0, ickdmyr0, ickbr0]=generate_mos(laygen, objectname_pfix +'CK0', placement_grid=pg, routing_grid_m1m2=rg12,
                                        devname_mos_boundary=devname_mos_boundary, devname_mos_body=devname_mos_body,
                                        devname_mos_dmy=devname_mos_dmy, m=m_clkh*2, m_dmy=m_clkh_dmy, origin=diffpair_origin)
    in_origin=laygen.get_inst_xy(ickbl0.name, pg)+laygen.get_template_size(ickbl0.cellname, pg)*np.array([0,1])
    [iinbl0, iindmyl0, iinl0, iinr0, iindmyr0, iinbr0] = \
        generate_diff_mos(laygen, objectname_pfix+'IN0', placement_grid=pg, routing_grid_m1m2=rg12,
                          devname_mos_boundary=devname_mos_boundary, devname_mos_body=devname_mos_body,
                          devname_mos_dmy=devname_mos_dmy, m=m_in, m_dmy=m_in_dmy, origin=in_origin)

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
    #dmy route
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, 
                 refobj0=iindmyl0.elements[0, 0].pins['S0'], refobj1=itap0.elements[0, 0].pins['TAP0'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=iindmyl0.elements[0, 0].pins['D0'], refobj1=itap0.elements[1, 0].pins['TAP0'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=iindmyr0.elements[0, 0].pins['S0'], refobj1=itap0.elements[-1, 0].pins['TAP1'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                 refobj0=iindmyr0.elements[0, 0].pins['D0'], refobj1=itap0.elements[-1, 0].pins['TAP0'])
    return [itapbl0, itap0, itapbr0, ickbl0, ick0, ickbr0, iinbl0, iindmyl0, iinl0, iinr0, iindmyr0, iinbr0]

def generate_salatch_regen(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m1m2_thick,
                   routing_grid_m2m3, routing_grid_m3m4,
                   devname_nmos_boundary, devname_nmos_body, devname_nmos_dmy,
                   devname_pmos_boundary, devname_pmos_body, devname_pmos_dmy,
                   devname_ptap_boundary, devname_ptap_body, devname_ntap_boundary, devname_ntap_body,
                   m_rgnp=2, m_rgnp_dmy=1, m_rstp=1, m_tap=12, origin=np.array([0, 0])):
    """generate a regenerative stage of SAlatch"""
    #grids
    pg = placement_grid
    rg12 = routing_grid_m1m2
    rg12t = routing_grid_m1m2_thick
    rg23 = routing_grid_m2m3
    rg34 = routing_grid_m3m4
    pfix = objectname_pfix

    #parameters
    m_rgnn = m_rgnp + 2 * m_rstp - 1
    m_rgnn_dmy = m_rgnp_dmy

    #placement
    #tap
    [itapbln0, itapn0, itapbrn0] = generate_tap(laygen, objectname_pfix=pfix+'NTAP0', 
                                                placement_grid=pg, routing_grid_m1m2_thick=rg12t,
                                                devname_tap_boundary=devname_ptap_boundary, devname_tap_body=devname_ptap_body,
                                                m=m_tap, origin=origin)
    rgnbody_origin = laygen.get_inst_xy(itapbln0.name, pg) + laygen.get_template_size(itapbln0.cellname, pg) * np.array([0, 1])
    #nmos row
    imbln0 = laygen.relplace(name="I" + pfix + 'BLN0', templatename=devname_nmos_boundary, gridname=pg, xy=rgnbody_origin)
    imdmyln0 = laygen.relplace(name="I" + pfix + 'DMYLN0', templatename=devname_nmos_dmy, gridname=pg, refobj=imbln0, shape=[m_rgnn_dmy, 1])
    imln0 = laygen.relplace(name="I" + pfix + 'LN0', templatename=devname_nmos_body, gridname=pg, refobj=imdmyln0, shape=[m_rgnn, 1])
    imln1 = laygen.relplace(name="I" + pfix + 'LN1', templatename=devname_nmos_dmy, gridname=pg, refobj=imln0)
    imrn1 = laygen.relplace(name="I" + pfix + 'RN1', templatename=devname_nmos_dmy, gridname=pg, refobj=imln1, transform='MY')
    imrn0 = laygen.relplace(name="I" + pfix + 'RN0', templatename=devname_nmos_body, gridname=pg, refobj=imrn1, shape=[m_rgnn, 1], transform='MY')
    imdmyrn0 = laygen.relplace(name="I" + pfix + 'DMYRN0', templatename=devname_nmos_dmy, gridname=pg, refobj=imrn0, shape=[m_rgnn_dmy, 1], transform='MY')
    imbrn0 = laygen.relplace(name="I" + pfix + 'BRN0', templatename=devname_nmos_boundary, gridname=pg, refobj=imdmyrn0, transform='MY')
    #pmos row
    imblp0 = laygen.relplace(name="I" + pfix + 'BLP0', templatename=devname_pmos_boundary, gridname=pg, refobj=imbln0, direction='top', transform='MX')
    imdmylp0 = laygen.relplace(name="I" + pfix + 'DMYLP0', templatename=devname_pmos_dmy, gridname=pg, refobj=imblp0, shape=[m_rgnp_dmy, 1], transform='MX')
    imlp0 = laygen.relplace(name="I" + pfix + 'LP0', templatename=devname_pmos_body, gridname=pg, refobj=imdmylp0, shape=[m_rgnp, 1], transform='MX')
    imrstlp0 = laygen.relplace(name="I" + pfix + 'RSTLP0', templatename=devname_pmos_body, gridname=pg, refobj=imlp0, shape=[m_rstp, 1], transform='MX')
    imrstlp1 = laygen.relplace(name="I" + pfix + 'RSTLP1', templatename=devname_pmos_body, gridname=pg, refobj=imrstlp0, shape=[m_rstp, 1], transform='MX')
    imrstrp1 = laygen.relplace(name="I" + pfix + 'RSTRP1', templatename=devname_pmos_body, gridname=pg, refobj=imrstlp1, shape=[m_rstp, 1], transform='R180')
    imrstrp0 = laygen.relplace(name="I" + pfix + 'RSTRP0', templatename=devname_pmos_body, gridname=pg, refobj=imrstrp1, shape=[m_rstp, 1], transform='R180')
    imrp0 = laygen.relplace(name="I" + pfix + 'RP0', templatename=devname_pmos_body, gridname=pg, refobj=imrstrp0, shape=[m_rgnp, 1], transform='R180')
    imdmyrp0 = laygen.relplace(name="I" + pfix + 'DMYRP0', templatename=devname_pmos_dmy, gridname=pg, refobj=imrp0, shape=[m_rgnp_dmy, 1], transform='R180')
    imbrp0 = laygen.relplace(name="I" + pfix + 'BRP0', templatename=devname_pmos_boundary, gridname=pg, refobj=imdmyrp0, transform='R180')
    #tap
    tap_origin = laygen.get_inst_xy(imblp0.name, pg) + laygen.get_template_size(devname_ntap_boundary, pg) * np.array([0, 1])
    [itapbl0, itap0, itapbr0] = generate_tap(laygen, objectname_pfix=pfix+'PTAP0', placement_grid=pg, routing_grid_m1m2_thick=rg12t,
                                             devname_tap_boundary=devname_ntap_boundary, devname_tap_body=devname_ntap_body,
                                             m=m_tap, origin=tap_origin, transform='MX')

    #route
    #tap to pmos
    for _m in np.concatenate((imlp0.elements[:, 0], imrp0.elements[:, 0], 
                              imrstlp0.elements[:, 0], imrstlp1.elements[:, 0],
                              imrstrp0.elements[:, 0], imrstrp1.elements[:, 0])):
        for pn in ['S0', 'S1']:
            laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                         refobj0=_m.pins[pn], refobj1=itap0.pins['TAP0'], direction='y')
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
    rglp0=laygen.route(None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                       refobj0=imlp0.elements[0, 0].pins['G0'], refobj1=imlp0.elements[-1, 0].pins['G0'])
    for _mlp in imlp0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_mlp.pins['G0'], gridname=rg12)
    rgrp0=laygen.route(None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                       refobj0=imrp0.elements[0, 0].pins['G0'], refobj1=imrp0.elements[-1, 0].pins['G0'])
    for _mrp in imrp0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_mrp.pins['G0'], gridname=rg12)
    #gate-pn vertical
    rglv0=laygen.route(name=None, xy0=[-1, 0], xy1=[-1, 0], gridname0=rg23,
                       refobj0=imlp0.elements[-1, 0].pins['G0'], via0=[0, 0], refobj1=imln0.elements[m_rgnp-1, 0].pins['G0'], via1=[0, 0])
    rgrv0=laygen.route(name=None, xy0=[-1, 0], xy1=[-1, 0], gridname0=rg23,
                       refobj0=imrp0.elements[-1, 0].pins['G0'], via0=[0, 0], refobj1=imrn0.elements[m_rgnp-1, 0].pins['G0'], via1=[0, 0])

    #drain-pn vertical
    rdlv=[]
    rdrv=[]
    for _mlp, _mln in zip(imlp0.elements[:, 0], imln0.elements[:, 0]):
        rdlv+=[laygen.route(name=None, xy0=[0, 0], xy1=[0, 1], gridname0=rg23,
                      refobj0=_mlp.pins['D0'], via0=[0, 0], refobj1=_mln.pins['D0'], via1=[0, 0])]
    for _mrp, _mrn in zip(imrp0.elements[:, 0], imrn0.elements[:, 0]):
        rdrv+=[laygen.route(name=None, xy0=[0, 0], xy1=[0, 1], gridname0=rg23,
                      refobj0=_mrp.pins['D0'], via0=[0, 0], refobj1=_mrn.pins['D0'], via1=[0, 0])]
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
    rdlp0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                       refobj0=imlp0.elements[0, 0].pins['D0'], refobj1=imrstlp0.elements[-1, 0].pins['D0'])
    for _m in imlp0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_m.pins['D0'], gridname=rg12)
    for _m in imrstlp0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_m.pins['D0'], gridname=rg12)
    rdrp0=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                       refobj0=imrp0.elements[0, 0].pins['D0'], refobj1=imrstrp0.elements[-1, 0].pins['D0'])
    for _m in imrp0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_m.pins['D0'], gridname=rg12)
    for _m in imrstrp0.elements[:, 0]:
        laygen.via(name=None, xy=[0, 0], refobj=_m.pins['D0'], gridname=rg12)
    #cross-coupled route and via
    xyg0=laygen.get_rect_xy(rglv0.name, rg34, sort=True)[0]
    xyd0=laygen.get_rect_xy(rdlv[0].name, rg34, sort=True)[0]
    xyg1=laygen.get_rect_xy(rgrv0.name, rg34, sort=True)[0]
    xyd1=laygen.get_rect_xy(rdrv[0].name, rg34, sort=True)[0]
    rop=laygen.route(name=None, xy0=[xyd0[0], xyg0[1]], xy1=[xyd1[0], xyg0[1]], gridname0=rg34)
    rom=laygen.route(name=None, xy0=[xyd0[0], xyg0[1]+1], xy1=[xyd1[0], xyg0[1]+1], gridname0=rg34)
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
    #dmy-p
    for i in range(m_rgnp_dmy):
        laygen.route(None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imdmylp0.elements[i, 0].pins['S0'], refobj1=itap0.elements[i, 0].pins['TAP0'], direction='y')
        laygen.route(None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imdmylp0.elements[i, 0].pins['D0'], refobj1=itap0.elements[i, 0].pins['TAP0'], direction='y')
        laygen.route(None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imdmyrp0.elements[i, 0].pins['S0'], refobj1=itap0.elements[m_tap-1-i, 0].pins['TAP0'], direction='y')
        laygen.route(None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imdmyrp0.elements[i, 0].pins['D0'], refobj1=itap0.elements[m_tap-1-i, 0].pins['TAP0'], direction='y')
    #dmy-n
    for i in range(m_rgnn_dmy):
        laygen.route(None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imdmyln0.elements[i, 0].pins['S0'], refobj1=itapn0.elements[i, 0].pins['TAP0'], direction='y')
        laygen.route(None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imdmyln0.elements[i, 0].pins['D0'], refobj1=itapn0.elements[i, 0].pins['TAP0'], direction='y')
        laygen.route(None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imdmyrn0.elements[i, 0].pins['S0'], refobj1=itapn0.elements[m_tap-1-i, 0].pins['TAP0'], direction='y')
        laygen.route(None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12,
                     refobj0=imdmyrn0.elements[i, 0].pins['D0'], refobj1=itapn0.elements[m_tap-1-i, 0].pins['TAP0'], direction='y')
    return [itapbln0, itapn0, itapbrn0, imbln0, imdmyln0, imln0, imln1, imrn1, imrn0, imdmyrn0, imbrn0,
            imblp0, imdmylp0, imlp0, imrstlp0, imrstlp1, imrstrp1, imrstrp0, imrp0, imdmyrp0, imbrp0,
            itapbl0, itap0, itapbr0, rop, rom]

def generate_salatch_simple(laygen, objectname_pfix, placement_grid,
                          routing_grid_m1m2, routing_grid_m1m2_thick, routing_grid_m2m3,
                          routing_grid_m2m3_thick, routing_grid_m3m4, routing_grid_m4m5,
                          devname_ntap_boundary, devname_ntap_body,
                          devname_pmos_boundary, devname_pmos_body, devname_pmos_dmy,
                          devname_nmos_boundary, devname_nmos_body, devname_nmos_dmy,
                          devname_ptap_boundary, devname_ptap_body,
                          m_in=4, m_ofst=2, m_clkh=2, m_rgnp=2, m_rst=1, num_vert_pwr=20, origin=np.array([0, 0])):
    """generate strongarm latch"""
    #derived parameters
    m_rgnn = m_rgnp + m_rst*2 - 1                 #nmos regeneration pair
    m_tot=max(m_in, m_clkh, m_rgnp + m_rst*2) + 1 #total m of half circuit, +2 for dummy
    m_in_dmy = m_tot - m_in                       #dummies for input row
    m_clkh_dmy = m_tot - m_clkh                   #for clock
    m_rgnp_dmy = m_tot - m_rgnp - m_rst*2         #for rgnp
    m_rgnn_dmy = m_rgnp_dmy                       #for rgnn
    m_tap=m_tot*2*2                               #tap width x2 for diff, x2 for nf=2
    print('total row size is: %d'%(m_tot*2))
    l_clkb_m4=4 #clkb output wire length

    #grids
    pg = placement_grid
    rg12 = routing_grid_m1m2
    rg12t = routing_grid_m1m2_thick
    rg23 = routing_grid_m2m3
    rg23t = routing_grid_m2m3_thick
    rg34 = routing_grid_m3m4
    rg45 = routing_grid_m4m5

    #main pair
    mainpair_origin = origin
    [imaintapbl0, imaintap0, imaintapbr0, imainckbl0, imainck0, imainckbr0,
     imaininbl0, imainindmyl0, imaininl0, imaininr0, imainindmyr0, imaininbr0]=\
    generate_clkdiffpair(laygen, objectname_pfix=objectname_pfix+'MAIN0', placement_grid=pg,
                         routing_grid_m1m2=rg12, routing_grid_m1m2_thick=rg12t, routing_grid_m2m3=rg23,
                         devname_mos_boundary=devname_nmos_boundary, devname_mos_body=devname_nmos_body, devname_mos_dmy=devname_nmos_dmy,
                         devname_tap_boundary=devname_ptap_boundary, devname_tap_body=devname_ptap_body,
                         m_in=m_in, m_in_dmy=m_in_dmy, m_clkh=m_clkh, m_clkh_dmy=m_clkh_dmy, m_tap=m_tap, origin=mainpair_origin)
    #regen
    regen_origin = laygen.get_inst_xy(imaininbl0.name, pg) + laygen.get_template_size(imaininbl0.cellname, pg) * np.array([0, 1])

    [irgntapbln0, irgntapn0, irgntapbrn0,
     irgnbln0, irgndmyln0, irgnln0, irgnln1, irgnrn1, irgnrn0, irgndmyrn0, irgnbrn0,
     irgnblp0, irgndmylp0, irgnlp0, irgnrstlp0, irgnrstlp1, irgnrstrp1, irgnrstrp0, irgnrp0, irgndmyrp0, irgnbrp0,
     irgntapbl0, irgntap0, irgntapbr0, rop, rom]=\
    generate_salatch_regen(laygen, objectname_pfix=objectname_pfix+'RGN0', placement_grid=pg,
                           routing_grid_m1m2=rg12, routing_grid_m1m2_thick=rg12t, routing_grid_m2m3=rg23, routing_grid_m3m4=rg34,
                           devname_nmos_boundary=devname_nmos_boundary, devname_nmos_body=devname_nmos_body, devname_nmos_dmy=devname_nmos_dmy,
                           devname_pmos_boundary=devname_pmos_boundary, devname_pmos_body=devname_pmos_body, devname_pmos_dmy=devname_pmos_dmy,
                           devname_ptap_boundary=devname_ptap_boundary, devname_ptap_body=devname_ptap_body,
                           devname_ntap_boundary=devname_ntap_boundary, devname_ntap_body=devname_ntap_body,
                           m_rgnp=m_rgnp, m_rgnp_dmy=m_rgnp_dmy, m_rstp=m_rst, m_tap=m_tap, origin=regen_origin)
    #regen-diff pair connections
    for i in range(m_rst):
        rintm=laygen.route(None, xy0=[0, 0], xy1=[0, 1], gridname0=rg23,
                refobj0=irgnln0.elements[-i-1, 0].pins['S1'], via0=[0, 0], refobj1=irgnrstlp1.elements[m_rst-1-i, 0].pins['S0'], via1=[0, 0])
        rintp=laygen.route(None, xy0=[0, 0], xy1=[0, 1], gridname0=rg23,
                refobj0=irgnrn0.elements[-i-1, 0].pins['S1'], via0=[0, 0], refobj1=irgnrstrp1.elements[m_rst-1-i, 0].pins['S0'], via1=[0, 0])
    for i in range(min(m_in, m_rgnp+m_rst)-1):
        laygen.route(None, xy0=[0, 1], xy1=[0, 0], gridname0=rg23,
                     refobj0=imaininl0.elements[m_in - 1 - i, 0].pins['S0'], via0=[0, 0], refobj1=irgnln0.elements[-i-1, 0].pins['S1'], via1=[0, 0])
        laygen.route(None, xy0=[0, 1], xy1=[0, 0], gridname0=rg23,
                     refobj0=imaininr0.elements[m_in - 1 - i, 0].pins['S0'], via0=[0, 0], refobj1=irgnrn0.elements[-i-1, 0].pins['S1'], via1=[0, 0])
    laygen.create_boundary_pin_from_rect(rintp, gridname=rg23, pinname='INTP', layer=laygen.layers['pin'][3], size=2, direction='top')
    laygen.create_boundary_pin_from_rect(rintm, gridname=rg23, pinname='INTM', layer=laygen.layers['pin'][3], size=2, direction='top')
    laygen.route(None, xy0=[0, 1], xy1=[0, 1], gridname0=rg23,
                 refobj0=irgnrstlp1.elements[0, 0].pins['D0'], refobj1=irgnrstlp1.elements[m_rst-1, 0].pins['D0'])
    laygen.route(None, xy0=[0, 1], xy1=[0, 1], gridname0=rg23,
                 refobj0=irgnrstrp1.elements[0, 0].pins['D0'], refobj1=irgnrstrp1.elements[m_rst-1, 0].pins['D0'])
    
    laygen.via(None, xy=[0, 1], refobj=imaininl0.elements[m_in-1, 0].pins['S0'], gridname=rg23)
    laygen.via(None, xy=[0, 1], refobj=imaininr0.elements[m_in-1, 0].pins['S0'], gridname=rg23)
    for i in range(m_rst):
        laygen.via(None, xy=[0, 1], refobj=irgnrstlp1.elements[i, 0].pins['D0'], gridname=rg12)
        laygen.via(None, xy=[0, 1], refobj=irgnrstrp1.elements[i, 0].pins['D0'], gridname=rg12)
    #clk connection
    rclk=laygen.route(None, xy0=[1, 0], xy1=[1, 0], gridname0=rg23,
                      refobj0=imainck0.elements[m_clkh-1, 0].pins['G0'], refobj1=irgnrstlp1.elements[m_rst-1, 0].pins['G0'], via0=[0, 0], via1=[0, 0])
    laygen.create_boundary_pin_from_rect(rclk, gridname=rg23, pinname='CLK', layer=laygen.layers['pin'][3], size=4, direction='bottom')
    #input connection
    rinp=laygen.route(None, xy0=[0, -4], xy1=[0, 0], gridname0=rg23,
                      refobj0=imaininl0.elements[0, 0].pins['G0'], refobj1=imaininl0.elements[0, 0].pins['G0'], via1=[0, 0])
    rinm=laygen.route(None, xy0=[0, -4], xy1=[0, 0], gridname0=rg23,
                      refobj0=imaininr0.elements[0, 0].pins['G0'], refobj1=imaininr0.elements[0, 0].pins['G0'], via1=[0, 0])
    laygen.pin_from_rect(layer=laygen.layers['pin'][3], rect=rinp, gridname=rg23, name='INP')
    laygen.pin_from_rect(layer=laygen.layers['pin'][3], rect=rinm, gridname=rg23, name='INM')
    laygen.pin_from_rect(layer=laygen.layers['pin'][4], rect=rop, gridname=rg34, name='OUTP')
    laygen.pin_from_rect(layer=laygen.layers['pin'][4], rect=rom, gridname=rg34, name='OUTM')
    #VDD/VSS
    rvss0 = laygen.route(None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12t,
                        refobj0=imaintap0.elements[0, 0].pins['TAP0'], refobj1=imaintap0.elements[-1, 0].pins['TAP1'])
    rvss1 = laygen.route(None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12t,
                        refobj0=irgntapn0.elements[0, 0].pins['TAP0'], refobj1=irgntapn0.elements[-1, 0].pins['TAP1']) 
    rvdd0 = laygen.route(None, xy0=[0, 1], xy1=[0, 1], gridname0=rg12t,
                        refobj0=irgntap0.elements[0, 0].pins['TAP0'], refobj1=irgntap0.elements[-1, 0].pins['TAP1'])
    laygen.pin_from_rect(name='VSS0', layer=laygen.layers['pin'][2], rect=rvss0, gridname=rg12t, netname='VSS:')
    laygen.pin_from_rect(name='VSS1', layer=laygen.layers['pin'][2], rect=rvss1, gridname=rg12t, netname='VSS:')
    laygen.pin_from_rect(name='VDD0', layer=laygen.layers['pin'][2], rect=rvdd0, gridname=rg12t, netname='VDD')

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
    #workinglib = 'adc_sar_generated'
    workinglib = 'laygo_working'
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

    mycell_list = []
    #salatch generation 
    cellname = 'salatch_simple'
    print(cellname+" generating")
    mycell_list.append(cellname)
    m_in=4    #input nmos size, larger than 4, even number
    m_clkh=12  #clk nmos size, even number
    m_rst=2   #reset pmos size, even number
    m_rgnp=4  #regen pmos size, even number

    #divide by 2 (using nf2 mos)
    m_in=int(m_in/2)            
    m_clkh=int(m_clkh/2)            
    m_rst=int(m_rst/2)
    m_rgnp=int(m_rgnp/2) 

    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)

    sa_origin=np.array([0, 0])

    #salatch body
    # 1. generate without spacing
    generate_salatch_simple(laygen, objectname_pfix='SA0',
                          placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick,
                          routing_grid_m2m3=rg_m2m3, routing_grid_m2m3_thick=rg_m2m3_thick, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5,
                          devname_ptap_boundary='ptap_fast_boundary', devname_ptap_body='ptap_fast_center_nf1',
                          devname_nmos_boundary='nmos4_fast_boundary', devname_nmos_body='nmos4_fast_center_nf2',
                          devname_nmos_dmy='nmos4_fast_dmy_nf2',
                          devname_pmos_boundary='pmos4_fast_boundary', devname_pmos_body='pmos4_fast_center_nf2',
                          devname_pmos_dmy='pmos4_fast_dmy_nf2',
                          devname_ntap_boundary='ntap_fast_boundary', devname_ntap_body='ntap_fast_center_nf1',
                          m_in=m_in, m_clkh=m_clkh, m_rgnp=m_rgnp, m_rst=m_rst,
                          num_vert_pwr=4, origin=sa_origin)
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

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

def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin"""
    rvdd0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VSS', gridname, sort=True)

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=gridname)

def generate_space(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4,
                   m_space_4x=0, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0])):
    """generate space row """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    tap_name = 'tap'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'
    space_4x_name = 'space_4x'

    # placement
    itapl = laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                         gridname = pg, xy=origin, template_libname = templib_logic)
    isp4x = []
    isp2x = []
    isp1x = []
    refi=itapl.name
    if not m_space_4x==0:
        isp4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP4X0', templatename=space_4x_name,
                     shape = np.array([m_space_4x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp4x[-1].name
    if not m_space_2x==0:
        isp2x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2X0', templatename=space_2x_name,
                     shape = np.array([m_space_2x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp2x[-1].name
    if not m_space_1x==0:
        isp1x.append(laygen.relplace(name="I" + objectname_pfix + 'SP1X0', templatename=space_1x_name,
                     shape=np.array([m_space_1x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp1x[-1].name
    itapr=laygen.relplace(name = "I" + objectname_pfix + 'TAPR0', templatename = tap_name,
                          gridname = pg, refinstname = refi, template_libname = templib_logic)

    # power pin
    pwr_dim=laygen.get_xy(obj =itapl.template, gridname=rg_m2m3)
    rvdd = []
    rvss = []
    rp1='VDD'
    for i in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin(name = 'VDD'+str(2*i-2), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSS'+str(2*i-2), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2+1, 0]), xy1=np.array([2*i+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin(name = 'VDD'+str(2*i-1), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSS'+str(2*i-1), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
    for j in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2+1, 0]), xy1=np.array([2*j+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2, 0]), xy1=np.array([2*j+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))

def generate_space_tap(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, 
                       m_tap=2, origin=np.array([0, 0])):
    """generate space row only with taps """
    pg = placement_grid
    rg_m1m2 = 'route_M1_M2_cmos'
    rg_m2m3 = 'route_M2_M3_cmos'

    ptap_center_name = 'ptap_fast_center_nf2'
    ptap_boundary_name = 'ptap_fast_boundary'
    ntap_center_name = 'ntap_fast_center_nf2'
    ntap_boundary_name = 'ntap_fast_boundary'

    # placement
    iptapl = laygen.place(name = "I" + objectname_pfix + 'PTAPL0', templatename = ptap_boundary_name,
                          gridname = pg, xy=origin)
    iptap = []
    refi=iptapl.name
    iptap.append(laygen.relplace(name="I" + objectname_pfix + 'PTAP0', templatename = ptap_center_name,
               shape=np.array([m_tap, 1]), gridname=pg, refinstname=refi))
    refi = iptap[-1].name
    iptapr=laygen.relplace(name = "I" + objectname_pfix + 'PTAPR0', templatename = ptap_boundary_name,
                           gridname = pg, refinstname = refi)

    intapl = laygen.relplace(name = "I" + objectname_pfix + 'NTAPL0', templatename = ntap_boundary_name,
                             gridname = pg, refinstname = iptapl.name, direction = 'top', transform = 'MX')
    intap = []
    refi=intapl.name
    intap.append(laygen.relplace(name="I" + objectname_pfix + 'NTPL0', templatename = ntap_center_name,
              shape=np.array([m_tap, 1]), gridname=pg, refinstname=refi, transform = 'MX'))
    refi = intap[-1].name
    intapr=laygen.relplace(name = "I" + objectname_pfix + 'NTAPR0', templatename = ntap_boundary_name,
                           gridname = pg, refinstname = refi, transform = 'MX')
    # power pin
    xy = laygen.get_xy(obj = iptapr.template, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=iptapl.name, refinstname1=iptapr.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=intapl.name, refinstname1=intapr.name)
    xy_s0 = laygen.get_template_pin_xy(iptap[0].cellname, 'TAP0', rg_m1m2)[0, :]
    # power/ground vertical route
    for i in range(m_tap):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=iptap[0].name, refinstindex0=np.array([i, 0]),
                     refinstname1=iptap[0].name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0*np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=intap[0].name, refinstindex0=np.array([i, 0]),
                     refinstname1=intap[0].name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=iptap[0].name, gridname=rg_m1m2,refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=intap[0].name, gridname=rg_m1m2,refinstindex=np.array([i, 0]))
    # power pin
    #pwr_dim=laygen.get_xy(obj =itapl.template, gridname=rg_m2m3)
    pwr_dim=6
    rvdd = []
    rvss = []
    for i in range(0, int(pwr_dim/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=iptapl.name, refinstindex0=np.array([0, 0]),
                     refinstname1=intapl.name, refinstindex1=np.array([0, 0]), via1=[[0, 0]]))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=iptapl.name, refinstindex0=np.array([0, 0]),
                     refinstname1=intapl.name, refinstindex1=np.array([0, 0]), via0=[[0, 0]]))
        laygen.pin(name = 'VDD'+str(2*i-2), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSS'+str(2*i-2), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2+1-pwr_dim, 0]), xy1=np.array([2*i+2+1-pwr_dim, 0]), gridname0=rg_m2m3,
                     refinstname0=iptapr.name, refinstindex0=np.array([0, 0]),
                     refinstname1=intapr.name, refinstindex1=np.array([0, 0]), via1=[[0, 0]]))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2-pwr_dim, 0]), xy1=np.array([2*i+2-pwr_dim, 0]), gridname0=rg_m2m3,
                     refinstname0=iptapr.name, refinstindex0=np.array([0, 0]),
                     refinstname1=intapr.name, refinstindex1=np.array([0, 0]), via0=[[0, 0]]))
        laygen.pin(name = 'VDD'+str(2*i-1), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSS'+str(2*i-1), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')

def generate_space_dcap(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4,
                        m_dcap=0, m_space_4x=0, m_space_2x=0, m_space_1x=0, dcap_name='dcap2_8x', origin=np.array([0, 0])):
    """generate space row """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    tap_name = 'tap'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'
    space_4x_name = 'space_4x'
    #dcap_name = 'dcap2_8x'

    # placement
    itapl = laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                         gridname = pg, xy=origin, template_libname = templib_logic)
    idcap = []
    isp4x = []
    isp2x = []
    isp1x = []
    refi=itapl.name
    if not m_dcap==0:
        idcap.append(laygen.relplace(name="I" + objectname_pfix + 'DCAP0', templatename=dcap_name,
                     shape = np.array([m_dcap, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = idcap[-1].name
    if not m_space_4x==0:
        isp4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP4X0', templatename=space_4x_name,
                     shape = np.array([m_space_4x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp4x[-1].name
    if not m_space_2x==0:
        isp2x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2X0', templatename=space_2x_name,
                     shape = np.array([m_space_2x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp2x[-1].name
    if not m_space_1x==0:
        isp1x.append(laygen.relplace(name="I" + objectname_pfix + 'SP1X0', templatename=space_1x_name,
                     shape=np.array([m_space_1x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp1x[-1].name
    itapr=laygen.relplace(name = "I" + objectname_pfix + 'TAPR0', templatename = tap_name,
                          gridname = pg, refinstname = refi, template_libname = templib_logic)

    # power pin
    pwr_dim=laygen.get_xy(obj =itapl.template, gridname=rg_m2m3)
    rvdd = []
    rvss = []
    rp1='VDD'
    for i in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin(name = 'VDD'+str(2*i-2), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSS'+str(2*i-2), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2+1, 0]), xy1=np.array([2*i+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin(name = 'VDD'+str(2*i-1), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSS'+str(2*i-1), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
    for j in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2+1, 0]), xy1=np.array([2*j+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2, 0]), xy1=np.array([2*j+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))

    yamlfile_output="adc_sar_size.yaml"
    #write to file
    with open(yamlfile_output, 'r') as stream:
        outdict = yaml.load(stream)
    outdict['m_dcap2']=m_dcap
    with open(yamlfile_output, 'w') as stream:
        yaml.dump(outdict, stream)


def generate_space_wbnd(laygen, objectname_pfix, workinglib, space_name, placement_grid, origin=np.array([0, 0])):
    space_origin = origin + laygen.get_xy(obj=laygen.get_template(name = 'boundary_bottomleft'), gridname = pg)
    ispace=laygen.place(name="I" + objectname_pfix + 'SP0', templatename=space_name,
                         gridname=pg, xy=space_origin, template_libname=workinglib)
    xy0=laygen.get_xy(obj=laygen.get_template(name=space_name, libname=workinglib), gridname=pg)
    xsp=xy0[0]
    #ysp=xy0[1]
    m_bnd = int(xsp / laygen.get_xy(obj=laygen.get_template(name = 'boundary_bottom'), gridname=pg)[0])
    [bnd_bottom, bnd_top, bnd_left, bnd_right] \
        = laygenhelper.generate_boundary(laygen, objectname_pfix='BND0', placement_grid=pg,
                            devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
                            shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
                            shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_left=['nmos4_fast_left', 'pmos4_fast_left'],
                            transform_left=['R0', 'MX'],
                            devname_right=['nmos4_fast_right', 'pmos4_fast_right'],
                            transform_right=['R0', 'MX'],
                            origin=origin)
    #pins
    space_template = laygen.templates.get_template(space_name, workinglib)
    space_pins=space_template.pins
    space_origin_phy = ispace.bbox[0]
    vddcnt=0
    vsscnt=0
    for pn, p in space_pins.items():
        if pn.startswith('VDD'):
            laygen.add_pin('VDD' + str(vddcnt), 'VDD', space_origin_phy+p['xy'], p['layer'])
            vddcnt += 1
        if pn.startswith('VSS'):
            laygen.add_pin('VSS' + str(vsscnt), 'VSS', space_origin_phy+p['xy'], p['layer'])
            vsscnt += 1

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

    mycell_list = []
    # generation (2 step)
    cellname='space'
    print(cellname+" generating")
    mycell_list.append(cellname)
    # 1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_space(laygen, objectname_pfix='SP0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                   m_space_4x=0, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    #2. calculate spacing param and regenerate
    x0 = laygen.templates.get_template('sarafe_nsw', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0]  \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_space_4x=int(m_space/4)
    m_space_2x=int((m_space-m_space_4x*4)/2)
    m_space_1x=int(m_space-m_space_4x*4-m_space_2x*2)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_space(laygen, objectname_pfix='SP0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                             m_space_4x=m_space_4x, m_space_2x=m_space_2x, m_space_1x=m_space_1x, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    
    # generation (2 step)
    cellname='space_dcap'
    print(cellname+" generating")
    mycell_list.append(cellname)
    # 1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_space_dcap(laygen, objectname_pfix='SP0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                   m_dcap=0, m_space_4x=0, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    #2. calculate spacing param and regenerate
    x0 = laygen.templates.get_template('sarafe_nsw', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0]  \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_dcap=int(m_space/10)
    m_space_4x=int((m_space-m_dcap*10)/4)
    m_space_2x=int((m_space-m_dcap*10-m_space_4x*4)/2)
    m_space_1x=int(m_space-m_dcap*10-m_space_4x*4-m_space_2x*2)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_space_dcap(laygen, objectname_pfix='SP0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                   m_dcap=m_dcap, m_space_4x=m_space_4x, m_space_2x=m_space_2x, m_space_1x=m_space_1x, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    
    # generation (2 step)
    cellname='space_dcap_nmos'
    print(cellname+" generating")
    mycell_list.append(cellname)
    # 1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_space_dcap(laygen, objectname_pfix='SP0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                   m_dcap=0, m_space_4x=0, m_space_2x=0, m_space_1x=0, dcap_name='dcap3_8x', origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    #2. calculate spacing param and regenerate
    x0 = laygen.templates.get_template('sarafe_nsw', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0]  \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_dcap=int(m_space/10)
    m_space_4x=int((m_space-m_dcap*10)/4)
    m_space_2x=int((m_space-m_dcap*10-m_space_4x*4)/2)
    m_space_1x=int(m_space-m_dcap*10-m_space_4x*4-m_space_2x*2)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_space_dcap(laygen, objectname_pfix='SP0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                   m_dcap=m_dcap, m_space_4x=m_space_4x, m_space_2x=m_space_2x, m_space_1x=m_space_1x, dcap_name='dcap3_8x', origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    
    #space with boundary
    cellname_wbnd='space_wbnd'
    print(cellname_wbnd+" generating")
    mycell_list.append(cellname_wbnd)
    laygen.add_cell(cellname_wbnd)
    laygen.sel_cell(cellname_wbnd)
    generate_space_wbnd(laygen, objectname_pfix='SP0', workinglib=workinglib, space_name=cellname, placement_grid=pg, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    cellname_tap='space_tap'
    print(cellname_tap+" generating")
    mycell_list.append(cellname_tap)
    laygen.add_cell(cellname_tap)
    laygen.sel_cell(cellname_tap)
    #space with taps
    generate_space_tap(laygen, objectname_pfix='SP0', placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, 
                       m_tap=int(m_space/2)+6, origin=np.array([0, 0]))
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

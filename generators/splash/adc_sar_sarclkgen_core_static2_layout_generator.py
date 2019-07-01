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

"""Logic layout
"""
import laygo
import numpy as np
import yaml
import os
#import logging;logging.basicConfig(level=logging.DEBUG)

def create_io_pin(laygen, layer, gridname, pinname_list, rect_list, offset_y=np.array([-1, 1])):
    """create digital io pin"""
    rect_xy_list = [laygen.get_rect_xy(name=r.name, gridname=gridname, sort=True) for r in rect_list]
    #align pins
    ry = rect_xy_list[0][:, 1] + offset_y.T
    for i, xy_rect in enumerate(rect_xy_list):
        xy_rect[:, 1]=ry
        laygen.pin(name=pinname_list[i], layer=layer, xy=xy_rect, gridname=gridname)

def create_power_pin(laygen, layer, gridname, rect_vdd, rect_vss):
    """create power pin"""
    rvdd_pin_xy = laygen.get_rect_xy(rect_vdd.name, gridname)
    rvss_pin_xy = laygen.get_rect_xy(rect_vss.name, gridname)
    laygen.pin(name='VDD', layer=layer, xy=rvdd_pin_xy, gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=rvss_pin_xy, gridname=gridname)

def generate_sarclkgen_core2(laygen, objectname_pfix,
                     placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                     devname_nmos_boundary, devname_nmos_body, devname_nmos_space, devname_pmos_boundary, devname_pmos_body,
                     m=1, origin=np.array([0,0]), create_pin=False):
    #done signal generator
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m=max(1, int(m/2)) #using nf=2 devices

    # placement
    in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_boundary, pg, xy=origin)
    in1 = laygen.relplace("I"+objectname_pfix + 'N1', devname_nmos_body, pg, in0.name, shape=np.array([m, 1]))
    in3=in1
    #in2 = laygen.relplace("I" + objectname_pfix + 'N2', devname_nmos_boundary, pg, in1.name)
    #in3 = laygen.relplace("I" + objectname_pfix + 'N3', devname_nmos_boundary, pg, in2.name)
    #in4 = laygen.relplace("I"+objectname_pfix + 'N4', devname_nmos_body, pg, in3.name, shape=np.array([m, 1]))
    in5 = laygen.relplace("I"+objectname_pfix + 'N5', devname_nmos_boundary, pg, in3.name)
    in6 = laygen.relplace("I"+objectname_pfix + 'N6', devname_nmos_space, pg, in5.name, shape=np.array([m, 1]))

    ip0 = laygen.relplace("I"+objectname_pfix + 'P0', devname_pmos_boundary, pg, in0.name, direction='top', transform='MX')
    ip1 = laygen.relplace("I"+objectname_pfix + 'P1', devname_pmos_body, pg, ip0.name, transform='MX', shape=np.array([m, 1]))
    ip3=ip1
    #ip2 = laygen.relplace("I"+objectname_pfix + 'P2', devname_pmos_boundary, pg, ip1.name, transform='MX')
    #ip3 = laygen.relplace("I"+objectname_pfix + 'P3', devname_pmos_boundary, pg, ip2.name, transform='MX')
    ip4 = laygen.relplace("I"+objectname_pfix + 'P4', devname_pmos_body, pg, ip3.name, transform='MX', shape=np.array([m, 1]))
    ip5 = laygen.relplace("I"+objectname_pfix + 'P5', devname_pmos_boundary, pg, ip4.name, transform='MX')

    # route
    # clkb
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
        #laygen.via(None, np.array([0, 0]), refinstname=in4.name, refpinname='G0', refinstindex=np.array([i, 0]),
        #           gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=in1.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
    rclkb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2, 0]), xy1=np.array([2, 2]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='G0', refinstname1=in1.name, refpinname1='G0',
                       endstyle0="extend", endstyle1="extend")
    laygen.via(None, np.array([2, 0]), refinstname=in1.name, refpinname='G0', gridname=rg_m2m3)
    # b0
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip1.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
    rb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                       refinstname0=ip1.name, refpinname0='G0', refinstname1=ip1.name, refpinname1='G0',
                       endstyle0="extend", endstyle1="extend")
    laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='G0', gridname=rg_m2m3)
    # a0
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip4.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
    ra0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                       refinstname0=ip4.name, refpinname0='G0', refinstname1=ip4.name, refpinname1='G0',
                       endstyle0="extend", endstyle1="extend")
    laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='G0', gridname=rg_m2m3)

    # internal connection between mos
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0',
                 refinstname1=in1.name, refpinname1='D0', refinstindex1=np.array([2*m - 1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=ip1.name, refpinname0='D0',
                 refinstname1=ip4.name, refpinname1='D0', refinstindex1=np.array([m - 1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        #laygen.via(None, np.array([0, 1]), refinstname=in4.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip4.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    # output
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                       refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([2*m - 1, 0]), via0=[[0, 0]],
                       refinstname1=ip4.name, refpinname1='D0', refinstindex1=np.array([m - 1, 0]), via1=[[0, 0]])
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        #laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
        #             refinstname0=in4.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
        #             refinstname1=in4.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip4.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=ip4.name, refinstindex1=np.array([i, 0]))
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        #laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
        #             refinstname0=in4.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
        #             refinstname1=in4.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=ip4.name, refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                     refinstname1=ip4.name, refinstindex1=np.array([i, 0]))
    # power and groud rail
    xy = laygen.get_template_size(in5.cellname, rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip5.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in5.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['A', 'B', 'CLKB', 'O'], rect_list=[ra0, rb0, rclkb0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

def generate_sarclkgen_core_static(laygen, objectname_pfix,
                     placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin,
                     devname_nmos_boundary, devname_nmos_body, devname_nmos_space, devname_pmos_boundary, devname_pmos_body,
                     devname_pmos_space,
                     m=4, m_small=2, origin=np.array([0,0]), create_pin=False):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin

    m=max(1, int(m/2)) #using nf=2 devices
    m_small=max(1, int(m_small/2)) #using nf=2 devices

    # placement
    #in0 = laygen.place("I"+objectname_pfix + 'N0', devname_nmos_boundary, pg, xy=origin)
    #in1 = laygen.relplace("I"+objectname_pfix + 'N1', devname_nmos_body, pg, in0.name, shape=np.array([m_small, 1]))
    #in2 = laygen.relplace("I"+objectname_pfix + 'N2', devname_nmos_boundary, pg, in1.name)
    #in1s = laygen.relplace("I"+objectname_pfix + 'N1S', devname_nmos_space, pg, in2.name, shape=np.array([m-m_small, 1]))
    in1s = laygen.place("I"+objectname_pfix + 'N1S', devname_nmos_space, pg, xy=origin, shape=np.array([m-m_small, 1]))
    in0 = laygen.relplace("I"+objectname_pfix + 'N0', devname_nmos_boundary, pg, in1s.name)
    in1 = laygen.relplace("I"+objectname_pfix + 'N1', devname_nmos_body, pg, in0.name, shape=np.array([m_small, 1]))
    in2 = laygen.relplace("I"+objectname_pfix + 'N2', devname_nmos_boundary, pg, in1.name)
    in3 = laygen.relplace("I"+objectname_pfix + 'N3', devname_nmos_boundary, pg, in2.name)
    in4 = laygen.relplace("I"+objectname_pfix + 'N4', devname_nmos_body, pg, in3.name, shape=np.array([m, 1]))
    in5 = laygen.relplace("I"+objectname_pfix + 'N5', devname_nmos_boundary, pg, in4.name)
    in6 = laygen.relplace("I"+objectname_pfix + 'N6', devname_nmos_boundary, pg, in5.name)
    in7 = laygen.relplace("I"+objectname_pfix + 'N7', devname_nmos_body, pg, in6.name, shape=np.array([m, 1]))
    in8 = laygen.relplace("I"+objectname_pfix + 'N8', devname_nmos_boundary, pg, in7.name)

    ip0_xy = laygen.get_template_size(in1s.cellname, gridname=pg, libname=utemplib)
    ip0_xy[0] = 0
    ip0_xy[1] = 2*ip0_xy[1]
    ip0_xy += origin
    #ip0 = laygen.relplace("I"+objectname_pfix + 'P0', devname_pmos_boundary, pg, in0.name, direction='top', transform='MX')
    ip0 = laygen.place("I"+objectname_pfix + 'P0', devname_pmos_boundary, pg, xy=ip0_xy, transform='MX')
    ip1 = laygen.relplace("I"+objectname_pfix + 'P1', devname_pmos_body, pg, ip0.name, transform='MX', shape=np.array([m, 1]))
    ip2 = laygen.relplace("I"+objectname_pfix + 'P2', devname_pmos_boundary, pg, ip1.name, transform='MX')
    ip3 = laygen.relplace("I"+objectname_pfix + 'P3', devname_pmos_boundary, pg, ip2.name, transform='MX')
    ip4 = laygen.relplace("I"+objectname_pfix + 'P4', devname_pmos_body, pg, ip3.name, transform='MX', shape=np.array([m, 1]))
    ip5 = laygen.relplace("I"+objectname_pfix + 'P5', devname_pmos_boundary, pg, ip4.name, transform='MX')
    ip6 = laygen.relplace("I"+objectname_pfix + 'P6', devname_pmos_boundary, pg, ip5.name, transform='MX')
    #ip7 = laygen.relplace("I"+objectname_pfix + 'P7', devname_pmos_body, pg, ip6.name, transform='MX', shape=np.array([m_small, 1]))
    ip7 = laygen.relplace("I"+objectname_pfix + 'P7', devname_pmos_body, pg, ip6.name, transform='MX', shape=np.array([m, 1]))
    ip8 = laygen.relplace("I"+objectname_pfix + 'P8', devname_pmos_boundary, pg, ip7.name, transform='MX')
    #ip7s = laygen.relplace("I"+objectname_pfix + 'P7S', devname_pmos_space, pg, ip8.name, transform='MX', shape=np.array([m-m_small, 1]))
    # route
    # rst
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    for i in range(min(m,m_small)):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip1.name, refpinname1='G0', refinstindex1=np.array([0, 0]), direction='y')
    if m == 1:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([1, 0]), gridname0=rg_m1m2,
                     refinstname0=ip1.name, refpinname0='G0', refinstindex0=np.array([0, 0]), endstyle0="extend",
                     refinstname1=ip1.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]), endstyle1="extend")
        rrst0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                              refinstname0=ip1.name, refpinname0='G0', via0=[[0, 0]], refinstname1=ip1.name, refpinname1='G0',
                              endstyle0="extend", endstyle1="extend")
    else:
        laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=ip1.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                     refinstname1=ip1.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
        rrst0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                              refinstname0=ip1.name, refpinname0='G0', via0=[[0, 0]], refinstname1=ip1.name, refpinname1='G0',
                              endstyle0="extend", endstyle1="extend")
    # upb
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in4.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip4.name, refpinname1='G0', refinstindex1=np.array([i, 0]),
                     )
        laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-1, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=ip4.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip4.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
    rupb0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-1, 0]), xy1=np.array([-1, 2]), gridname0=rg_m2m3,
                       refinstname0=ip4.name, refpinname0='G0', refinstname1=ip4.name, refpinname1='G0', via0=[[0, 0]],
                       endstyle0="extend", endstyle1="extend")
    #done
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in7.name, refpinname='G0', refinstindex=np.array([i, 0]),
                   gridname=rg_m1m2)
    #for i in range(m_small):
    #    laygen.via(None, np.array([0, 0]), refinstname=ip7.name, refpinname='G0', refinstindex=np.array([i, 0]),
    #               gridname=rg_m1m2)
    #for i in range(min(m,m_small)):
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                     refinstname0=in7.name, refpinname0='G0', refinstindex0=np.array([i, 0]),
                     refinstname1=ip7.name, refpinname1='G0', refinstindex1=np.array([i, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=in7.name, refpinname0='G0', refinstindex0=np.array([0, 0]),
                 refinstname1=in7.name, refpinname1='G0', refinstindex1=np.array([m - 1, 0]))
    rdone0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 2]), gridname0=rg_m2m3,
                       refinstname0=in7.name, refpinname0='G0', via0=[[0, 0]], refinstname1=in7.name, refpinname1='G0',
                       endstyle0="extend", endstyle1="extend")
    # internal connection between mos
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
             refinstname0=in4.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
             refinstname1=in7.name, refpinname1='D0', refinstindex1=np.array([m - 1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=in4.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=in7.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m2m3,
             refinstname0=ip1.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
             refinstname1=ip7.name, refpinname1='S1', refinstindex1=np.array([m - 1, 0]))
             #refinstname1=ip7.name, refpinname1='S1', refinstindex1=np.array([m_small - 1, 0]))
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=ip1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip4.name, refpinname='S1', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #for i in range(m_small):
    for i in range(m):
        laygen.via(None, np.array([0, 0]), refinstname=ip7.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 0]), refinstname=ip7.name, refpinname='S1', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    # output
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=in1.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=in4.name, refpinname1='S1', refinstindex1=np.array([m-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refinstname0=ip4.name, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refinstname1=ip7.name, refpinname1='D0', refinstindex1=np.array([m-1, 0]))
    for i in range(m_small):
        laygen.via(None, np.array([0, 1]), refinstname=in1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    for i in range(m):
        laygen.via(None, np.array([0, 1]), refinstname=ip7.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=in4.name, refpinname='S0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=in4.name, refpinname='S1', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=ip4.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    for i in range(1,m-1):
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                       refinstname0=in4.name, refpinname0='D0', refinstindex0=np.array([i, 0]), via0=[[0, 0]],
                       refinstname1=ip4.name, refpinname1='D0', refinstindex1=np.array([i, 0]), via1=[[0, 0]])
    ro0 = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                       refinstname0=in4.name, refpinname0='D0', refinstindex0=np.array([m - 1, 0]), via0=[[0, 0]],
                       refinstname1=ip4.name, refpinname1='D0', refinstindex1=np.array([m - 1, 0]), via1=[[0, 0]])
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(in1.cellname, 'S0', rg_m1m2)[0, :]
    for i in range(m_small):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=in7.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in7.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s0 * np.array([1, 0]), xy1=xy_s0, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=in7.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s0 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
    xy_s1 = laygen.get_template_pin_xy(in1.cellname, 'S1', rg_m1m2)[0, :]
    for i in range(m_small):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=in1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in1.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
    for i in range(m):
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=in7.name, refinstindex0=np.array([i, 0]),
                     refinstname1=in7.name, refinstindex1=np.array([i, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=xy_s1 * np.array([1, 0]), xy1=xy_s1, gridname0=rg_m1m2,
                     refinstname0=ip1.name, refinstindex0=np.array([i, 0]),
                     refinstname1=ip1.name, refinstindex1=np.array([i, 0]))
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=in7.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
        laygen.via(None, xy_s1 * np.array([1, 0]), refinstname=ip1.name, gridname=rg_m1m2,
                   refinstindex=np.array([i, 0]))
    # power and groud rail
    xy = laygen.get_template_size(in5.cellname, rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip8.name)
    #rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
    #             refinstname0=in0.name, refinstname1=in8.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in1s.name, refinstname1=in8.name)
    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg_m2m3_pin,
                      pinname_list = ['UPB', 'RST', 'DONE', 'PHI0'], rect_list=[rupb0, rrst0, rdone0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, rect_vdd=rvdd, rect_vss=rvss)

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

    mycell_list = []
    #capdrv generation
    cell_name='sarclkgen_core_static2'
    cell_name2='sarclkgen_core2'
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
        m=sizedict['sarclkgen']['m']*4

    print(cell_name+" generating")
    mycell_list.append(cell_name)
    laygen.add_cell(cell_name)
    laygen.sel_cell(cell_name)
    generate_sarclkgen_core_static(laygen, objectname_pfix='CGC0',
                     placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, 
                     routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body='nmos4_fast_center_nf2',
                     devname_nmos_space='nmos4_fast_space_nf2',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body='pmos4_fast_center_nf2', 
                     devname_pmos_space='pmos4_fast_space_nf2', 
                     m=m, origin=np.array([0,0]), create_pin=True)
    laygen.add_template_from_cell()

    cell_name=cell_name2
    print(cell_name+" generating")
    mycell_list.append(cell_name)
    laygen.add_cell(cell_name)
    laygen.sel_cell(cell_name)
    generate_sarclkgen_core2(laygen, objectname_pfix='CGC1',
                     placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, 
                     routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                     devname_nmos_boundary='nmos4_fast_boundary',
                     devname_nmos_body='nmos4_fast_center_nf2',
                     devname_nmos_space='nmos4_fast_space_nf2',
                     devname_pmos_boundary='pmos4_fast_boundary',
                     devname_pmos_body='pmos4_fast_center_nf2', 
                     m=4, origin=np.array([0,0]), create_pin=True)
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

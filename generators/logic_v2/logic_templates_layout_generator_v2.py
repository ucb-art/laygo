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
    Logic layout generator (new version), Using GridLayoutGenerator2
"""
import laygo
import numpy as np
import yaml
import os
#import logging;logging.basicConfig(level=logging.DEBUG)

def create_logic_io_pin(laygen, gridname, pinname_list, rect_list, offset_n=np.array([-1, 1])):
    """generate digital io pin"""
    rect_mn_list = [laygen.get_mn(obj=r, gridname=gridname, sort=True) for r in rect_list]
    # align pins
    rn = rect_mn_list[0][:, 1] + offset_n.T
    for mn_rect, pn, r in zip(rect_mn_list, pinname_list, rect_list):
        mn_rect[:, 1]=rn
        laygen.pin(name=pn, mn0=mn_rect[0, :], mn1=mn_rect[1, :], gridname=gridname)

def create_logic_power_pin(laygen, gridname, rect_vdd, rect_vss, pinname_vdd='VDD', pinname_vss='VSS'):
    """generate power pin"""
    laygen.pin(name=pinname_vdd, ref=rect_vdd, gridname=gridname)
    laygen.pin(name=pinname_vss, ref=rect_vss, gridname=gridname)

def _create_logic_mos(laygen, devname_center, devname_boundary_left, devname_boundary_right, devname_space,
                      place_grid, nf, mn=np.array([0, 0]), ref=None, transform='R0'):
    """logic mosfet generator core function"""
    pg = place_grid
    dnbl = devname_boundary_left    #boundary left mos structure name
    dnc = devname_center            #core mos structure name
    dnbr = devname_boundary_right   #boundary right mos structure name
    dnsp = devname_space            #spacing structure name
    if nf == 1:
        _m = 1
    else:
        _m = int(nf / 2)
    dev_bl0 = laygen.place(gridname=pg, cellname=dnbl, mn=mn, ref=ref, shape=[1, 1], transform=transform)
    dev_core0 = laygen.place(gridname=pg, cellname=dnc, ref=dev_bl0.right, shape=[_m, 1], transform=transform)
    dev_br0 = laygen.place(gridname=pg, cellname=dnbr, ref=dev_core0.right, shape=[1, 1], transform=transform)
    if nf == 1:
        dev_br0 = laygen.place(gridname=pg, cellname=dnsp, ref=dev_br0.right, shape=[1, 1], transform=transform)
    return {'dev': [dev_bl0, dev_core0, dev_br0], 'core': dev_core0}

def create_logic_nmos(laygen, place_grid, nf, mn=np.array([0, 0]), ref=None, transform='R0'):
    """logic n-mosfet generator"""
    dnbl = 'nmos4_fast_boundary'
    if nf == 1:
        dnc = 'nmos4_fast_center_nf1_left'
    else:
        dnc = 'nmos4_fast_center_nf2'
    dnbr = 'nmos4_fast_boundary'
    dnsp = 'nmos4_fast_space'
    return _create_logic_mos(laygen, devname_center=dnc, devname_boundary_left=dnbl, devname_boundary_right=dnbr,
                             devname_space=dnsp, place_grid=place_grid, nf=nf, mn=mn, ref=ref, transform=transform)

def create_logic_pmos(laygen, place_grid, nf, mn=np.array([0, 0]), ref=None, transform='R0'):
    """logic p-mosfet generator"""
    dnbl='pmos4_fast_boundary'
    if nf == 1:
        dnc = 'pmos4_fast_center_nf1_left'
    else:
        dnc = 'pmos4_fast_center_nf2'
    dnbr='pmos4_fast_boundary'
    dnsp = 'nmos4_fast_space'
    return _create_logic_mos(laygen, devname_center=dnc, devname_boundary_left=dnbl, devname_boundary_right=dnbr,
                             devname_space=dnsp, place_grid=place_grid, nf=nf, mn=mn, ref=ref, transform=transform)


def generate_logic_gate(laygen, gate_type, place_grid, route_grid_m1m2, route_grid_m2m3,
                        route_grid_m1m2_pin, route_grid_m2m3_pin,
                        m=1, origin=np.array([0,0]), pin_height=2, create_pin=True):
    rg12 = route_grid_m1m2
    rg23 = route_grid_m2m3
    rg12_pin = route_grid_m1m2_pin
    rg23_pin = route_grid_m2m3_pin

    if gate_type=='inv': #inverter
        #place
        nrow0 = create_logic_nmos(laygen, place_grid, nf=m, mn=origin, transform='R0')
        prow0 = create_logic_pmos(laygen, place_grid, nf=m, ref=nrow0['dev'][0].top, transform='MX')
        nbl0 = nrow0['dev'][0]
        n0 = nrow0['core']
        nbr0 = nrow0['dev'][-1]
        pbl0 = prow0['dev'][0]
        p0 = prow0['core']
        pbr0 = prow0['dev'][-1]

        #route
        #input
        input_conn=n0 #generate the gate structure in nmos side
        laygen.route(gridname0=rg12, ref0=n0.pins['G0'], ref1=p0.pins['G0']) #vertical m1
        laygen.via(gridname=rg12, ref=input_conn.pins['G0'])                 #m1_m2 via
        if m == 1:
            ofstl = 0
            ofstr = 2
        elif m == 2:
            ofstl = -1
            ofstr = 1
        else:
            ofstl = 0
            ofstr = 0
        r0 = laygen.route(gridname0=rg12, mn0=[ofstl, 0], mn1=[ofstr, 0], ref0=input_conn[0, 0].pins['G0'], ref1=input_conn[-1, 0].pins['G0'])
        ri = laygen.route(gridname0=rg23, mn0=[0, 0], mn1=[0, pin_height], ref0=r0, ref1=r0, via0=[0, 0])

        #output
        if m == 1:
            ofstl = -1
            ofstr = 1
        elif m == 2:
            ofstl = -1
            ofstr = 1
        else:
            ofstl = 0
            ofstr = 0
        r1 = laygen.route(gridname0=rg12, mn0=[ofstl, 0], mn1=[ofstr, 0], ref0=n0[0, 0].pins['D0'], ref1=n0[-1, 0].pins['D0'])
        laygen.via(gridname=rg12, ref=n0.pins['D0'], overlay=r1)
        r2 = laygen.route(gridname0=rg12, mn0=[ofstl, 0], mn1=[ofstr, 0], ref0=p0[0, 0].pins['D0'], ref1=p0[-1, 0].pins['D0'])
        laygen.via(gridname=rg12, ref=p0.pins['D0'], overlay=r2)
        ro = laygen.route(gridname0=rg23, ref0=r1.right, ref1=r2.right, via0=[0, 0], via1=[0, 0])

        #parameter passing
        if m == 1:
            power_route_devices = [[n0, ['S0']], [p0, ['S0']]]
        else:
            power_route_devices = [[n0, ['S0', 'S1']], [p0, ['S0', 'S1']]]
        vss_rail_boundary_devices = [nbl0, nbr0]
        vdd_rail_boundary_devices = [pbl0, pbr0]
        io_pin_names=['I', 'O']
        io_pin_rects=[ri, ro]

    if gate_type=='nand': #nand
        #place
        nrow0 = create_logic_nmos(laygen, place_grid, nf=m, mn=origin, transform='R0')
        nrow1 = create_logic_nmos(laygen, place_grid, nf=m, ref=nrow0['dev'][-1].right, transform='R0')
        prow0 = create_logic_pmos(laygen, place_grid, nf=m, ref=nrow0['dev'][0].top, transform='MX')
        prow1 = create_logic_pmos(laygen, place_grid, nf=m, ref=prow0['dev'][-1].right, transform='MX')
        nbl0 = nrow0['dev'][0]
        n0 = nrow0['core']
        n1 = nrow1['core']
        nbr1 = nrow1['dev'][-1]
        pbl0 = prow0['dev'][0]
        p0 = prow0['core']
        p1 = prow0['core']
        pbr1 = prow1['dev'][-1]

        #route
        # a
        laygen.route(gridname0=rg12, ref0=n1.pins['G0'], ref1=p1.pins['G0'])  # vertical m1
        laygen.via(gridname=rg12, ref=p1.pins['G0'])  # m1_m2 via
        if m == 1:
            ofstl = 0
            ofstr = 2
        elif m == 2:
            ofstl = -1
            ofstr = 1
        else:
            ofstl = 0
            ofstr = 0
        r0 = laygen.route(gridname0=rg12, mn0=[ofstl, 0], mn1=[ofstr, 0], ref0=p1[0, 0].pins['G0'],
                          ref1=p1[-1, 0].pins['G0'])
        ra = laygen.route(gridname0=rg23, mn0=[0, 0], mn1=[0, -pin_height], ref0=r0, ref1=r0, via0=[0, 0])
        # b
        laygen.route(gridname0=rg12, ref0=n0.pins['G0'], ref1=p0.pins['G0'])  # vertical m1
        laygen.via(gridname=rg12, ref=n0.pins['G0'])  # m1_m2 via
        if m == 1:
            ofstl = 0
            ofstr = 2
        elif m == 2:
            ofstl = -1
            ofstr = 1
        else:
            ofstl = 0
            ofstr = 0
        r1 = laygen.route(gridname0=rg12, mn0=[ofstl, 0], mn1=[ofstr, 0], ref0=n0[0, 0].pins['G0'],
                          ref1=n0[-1, 0].pins['G0'])
        rb = laygen.route(gridname0=rg23, mn0=[0, 0], mn1=[0, pin_height], ref0=r1, ref1=r1, via0=[0, 0])
        # internal
        if m == 1:
            r2 = laygen.route(gridname0=rg12, mn0=[0, 1], mn1=[0, 1], ref0=n0[0, 0].pins['D0'], ref1=n1[-1, 0].pins['S0'])
        else:
            r2 = laygen.route(gridname0=rg12, mn0=[0, 1], mn1=[0, 1], ref0=n0[0, 0].pins['D0'], ref1=n1[-1, 0].pins['S1'])
        laygen.via(gridname=rg12, ref=n0.pins['D0'], overlay=r2)
        laygen.via(gridname=rg12, ref=n1.pins['S0'], overlay=r2)
        if m > 1:
            laygen.via(gridname=rg12, ref=n1.pins['S1'], overlay=r2)
        # output
        if m == 1:
            ofstl = -1
            ofstr = 1
        elif m == 2:
            ofstl = -1
            ofstr = 1
        else:
            ofstl = 0
            ofstr = 0
        r3 = laygen.route(gridname0=rg12, mn0=[ofstl, 0], mn1=[ofstr, 0], ref0=n1[0, 0].pins['D0'], ref1=n1[-1, 0].pins['D0'])
        laygen.via(gridname=rg12, ref=n1.pins['D0'], overlay=r3)
        r4 = laygen.route(gridname0=rg12, mn0=[ofstl, 0], mn1=[ofstr, 0], ref0=p0[0, 0].pins['D0'], ref1=p1[-1, 0].pins['D0'])
        laygen.via(gridname=rg12, ref=p0.pins['D0'], overlay=r4)
        laygen.via(gridname=rg12, ref=p1.pins['D0'], overlay=r4)
        ro = laygen.route(gridname0=rg23, ref0=r3.right, ref1=r4.right, via0=[0, 0], via1=[0, 0])

        #parameter passing
        if m == 1:
            power_route_devices = [[n0, ['S0']], [p0, ['S0']], [p1, ['S0']]]
        else:
            power_route_devices = [[n0, ['S0', 'S1']], [p0, ['S0', 'S1']], [p1, ['S0', 'S1']]]
        vss_rail_boundary_devices = [nbl0, nbr1]
        vdd_rail_boundary_devices = [pbl0, pbr1]
        io_pin_names = ['A', 'B', 'O']
        io_pin_rects = [ra, rb, ro]

    # power and ground route
    for dev, pins in power_route_devices:
        for pn in pins:
            laygen.route(gridname0=rg12, ref0=dev.pins[pn], ref1=dev.bottom, direction='y', via1=[0, 0])
    rvdd = laygen.route(gridname0=rg12, ref0=vdd_rail_boundary_devices[0].bottom_left, ref1=vdd_rail_boundary_devices[1].bottom_right)
    rvss = laygen.route(gridname0=rg12, ref0=vss_rail_boundary_devices[0].bottom_left, ref1=vss_rail_boundary_devices[1].bottom_right)

    # pin
    if create_pin is True:
        create_logic_io_pin(laygen, gridname=rg23_pin, pinname_list=io_pin_names, rect_list=io_pin_rects)
        create_logic_power_pin(laygen, gridname=rg12, rect_vdd=rvdd, rect_vss=rvss)

if __name__ == '__main__':
    import laygo
    import numpy as np

    # initialize #######################################################################################################
    laygen = laygo.GridLayoutGenerator2(config_file="../../labs/laygo_config.yaml")
    laygen.use_phantom = True  # for abstract generation. False when generating a real layout.
    # load template and grid
    utemplib = laygen.tech + '_microtemplates_dense'  # device template library name
    laygen.load_template(filename='../../labs/' + utemplib + '_templates.yaml', libname=utemplib)
    laygen.load_grid(filename='../../labs/' + utemplib + '_grids.yaml', libname=utemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)

    # grids
    pg = 'placement_basic'  # placement grid
    rg12 = 'route_M1_M2_cmos'
    rg23 = 'route_M2_M3_cmos'
    rg34 = 'route_M3_M4_basic'
    rg12_pin = 'route_M1_M2_basic'
    rg23_pin = 'route_M2_M3_basic'

    # library creation
    laygen.add_library('laygo_working')

    cell_name_dict = {'inv': [1, 2, 4, 8, 16, 32],
                      'nand': [1, 2, 4, 8, 16],
                      }

    # layout generation ################################################################################################
    # for cell_name_prim, m_list in iteritems(cell_name_dict):
    generated_cells = []
    for cell_name_prim, m_list in cell_name_dict.items():
        for m in m_list:
            cell_name = cell_name_prim + '_' + str(m) + 'x'
            print('logic primitive:' + cell_name)
            laygen.add_cell(cell_name)
            generate_logic_gate(laygen, gate_type=cell_name_prim, place_grid=pg, route_grid_m1m2=rg12, route_grid_m2m3=rg23,
                         route_grid_m1m2_pin=rg12_pin, route_grid_m2m3_pin=rg23_pin,
                         m=m, origin=np.array([0, 0]))
            generated_cells += [cell_name]

    # display ##########################################################################################################
    #laygen.display()

    # export ###########################################################################################################
    laygen.export_GDS('../../output.gds', cellname=generated_cells, layermapfile="../../labs/laygo_faketech.layermap")


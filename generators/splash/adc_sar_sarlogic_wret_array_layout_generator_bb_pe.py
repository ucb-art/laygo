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

def generate_sarlogic_xor(laygen, objectname_pfix, placement_grid,  
                 routing_grid_m1m2, routing_grid_m2m3, routing_grid_m1m2_pin, routing_grid_m2m3_pin, m_xor, 
                 origin=np.array([0, 0])):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m1m2_pin = routing_grid_m1m2_pin
    rg_m2m3_pin = routing_grid_m2m3_pin
    m_xor = m_xor

    # placement
    in0 = laygen.relplace(name = "I" + objectname_pfix + 'N0', templatename = "nmos4_fast_boundary", 
                gridname = pg, refobj = None, transform="R0")
    ixorna = laygen.relplace(name = "I" + objectname_pfix + 'XORNA', templatename = "nmos4_fast_center_nf2", 
                gridname = pg, refobj = in0, transform="R0", shape=np.array([int(m_xor/2),1]))
    in1 = laygen.relplace(name = "I" + objectname_pfix + 'N1', templatename = "nmos4_fast_boundary", 
                gridname = pg, refobj = ixorna, transform="R0")
    ixornad = laygen.relplace(name = "I" + objectname_pfix + 'XORNAd', templatename = "nmos4_fast_center_nf2", 
                gridname = pg, refobj = in1, transform="R0", shape=np.array([int(m_xor/2),1]))
    in2 = laygen.relplace(name = "I" + objectname_pfix + 'N2', templatename = "nmos4_fast_boundary", 
                gridname = pg, refobj = ixornad, transform="R0")
    ixornab0 = laygen.relplace(name = "I" + objectname_pfix + 'XORNAb0', templatename = "nmos4_fast_center_nf2", 
                gridname = pg, refobj = in2, transform="R0", shape=np.array([int(m_xor/2),1]))
    in3 = laygen.relplace(name = "I" + objectname_pfix + 'N3', templatename = "nmos4_fast_boundary", 
                gridname = pg, refobj = ixornab0, transform="R0")
    ixornab1 = laygen.relplace(name = "I" + objectname_pfix + 'XORNAb1', templatename = "nmos4_fast_center_nf2", 
                gridname = pg, refobj = in3, transform="R0", shape=np.array([int(m_xor/2),1]))
    in4 = laygen.relplace(name = "I" + objectname_pfix + 'N4', templatename = "nmos4_fast_boundary", 
                gridname = pg, refobj = ixornab1, transform="R0")
    ip0 = laygen.relplace(name = "I" + objectname_pfix + 'P0', templatename = "pmos4_fast_boundary", 
                gridname = pg, refobj = in0, transform="MX", direction="top")
    ixorpa = laygen.relplace(name = "I" + objectname_pfix + 'XORPA', templatename = "pmos4_fast_center_nf2", 
                gridname = pg, refobj = ip0, transform="MX", shape=np.array([int(m_xor/2),1]))
    ip1 = laygen.relplace(name = "I" + objectname_pfix + 'P1', templatename = "pmos4_fast_boundary", 
                gridname = pg, refobj = ixorpa, transform="MX")
    ixorpab1 = laygen.relplace(name = "I" + objectname_pfix + 'XORPAb1', templatename = "pmos4_fast_center_nf2", 
                gridname = pg, refobj = ip1, transform="MX", shape=np.array([int(m_xor/2),1]))
    ip2 = laygen.relplace(name = "I" + objectname_pfix + 'P2', templatename = "pmos4_fast_boundary", 
                gridname = pg, refobj = ixorpab1, transform="MX")
    ixorpab0 = laygen.relplace(name = "I" + objectname_pfix + 'XORPAb0', templatename = "pmos4_fast_center_nf2", 
                gridname = pg, refobj = ip2, transform="MX", shape=np.array([int(m_xor/2),1]))
    ip3 = laygen.relplace(name = "I" + objectname_pfix + 'P3', templatename = "pmos4_fast_boundary", 
                gridname = pg, refobj = ixorpab0, transform="MX")
    ixorpad = laygen.relplace(name = "I" + objectname_pfix + 'XORPAd', templatename = "pmos4_fast_center_nf2", 
                gridname = pg, refobj = ip3, transform="MX", shape=np.array([int(m_xor/2),1]))
    ip4 = laygen.relplace(name = "I" + objectname_pfix + 'P4', templatename = "pmos4_fast_boundary", 
                gridname = pg, refobj = ixorpad, transform="MX")
    # Gate Routing
    ra=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2, refobj0=ixorna.pins['G0'], refobj1=ixorpa.pins['G0'])
    rab=laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2, refobj0=ixorpab0.pins['G0'], refobj1=ixorpab1.pins['G0'], via0=[0, 0], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2, refobj0=ixornab0.pins['G0'], refobj1=ixornab1.pins['G0'], via0=[0, 0], via1=[0, 0])
    rad=laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg_m1m2, refobj0=ixornad.pins['G0'], refobj1=ixorpad.pins['G0'])
    laygen.route(name=None, layer=laygen.layers['metal'][2], xy0=[0, 0], xy1=[0, 1], gridname0=rg_m1m2, 
            refobj0=ixornad.pins['G0'], refobj1=ixornad.pins['G0'], endstyle1="extend", via0=[0, 0])
    laygen.route(name=None, layer=laygen.layers['metal'][2], xy0=[0, 0], xy1=[0, 1], gridname0=rg_m1m2, 
            refobj0=ixorpad.pins['G0'], refobj1=ixorpad.pins['G0'], endstyle1="extend", via0=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m2m3, refobj0=ixornab0.pins['G0'], refobj1=ixorpab0.pins['G0'], via0=[0, 0], via1=[0, 0])

    # drain
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2, refobj0=ixornad.pins['S0'], refobj1=ixornad.pins['S1'], via0=[0, 0], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2, refobj0=ixornab1.pins['S0'], refobj1=ixornab1.pins['S1'], via0=[0, 0], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2, refobj0=ixorna.pins['D0'], refobj1=ixornad.pins['S0'], via0=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2, refobj0=ixornab0.pins['D0'], refobj1=ixornab1.pins['S0'], via0=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2, refobj0=ixorpab1.pins['S0'], refobj1=ixorpab1.pins['S1'], via0=[0, 0], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2, refobj0=ixorpad.pins['S0'], refobj1=ixorpad.pins['S1'], via0=[0, 0], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2, refobj0=ixorpa.pins['D0'], refobj1=ixorpab1.pins['S0'], via0=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m1m2, refobj0=ixorpab0.pins['D0'], refobj1=ixorpad.pins['S0'], via0=[0, 0])

    # output
    laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg_m1m2, refobj0=ixornad.pins['D0'], refobj1=ixornab1.pins['D0'], via0=[0, 0], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg_m1m2, refobj0=ixorpad.pins['D0'], refobj1=ixorpab1.pins['D0'], via0=[0, 0], via1=[0, 0])
    ro=laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg_m2m3, refobj0=ixornab1.pins['D0'], refobj1=ixorpad.pins['D0'], via0=[0, 0], via1=[0, 0])
    
    # power routing
    laygen.route(name=None, xy0=[0, 0], xy1=[0, -1], gridname0=rg_m1m2, refobj0=ixorna.pins['S0'], refobj1=ixorna.pins['S0'], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, -1], gridname0=rg_m1m2, refobj0=ixornab0.pins['S0'], refobj1=ixornab0.pins['S0'], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, -1], gridname0=rg_m1m2, refobj0=ixorpa.pins['S0'], refobj1=ixorpa.pins['S0'], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, -1], gridname0=rg_m1m2, refobj0=ixorpab0.pins['S0'], refobj1=ixorpab0.pins['S0'], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, -1], gridname0=rg_m1m2, refobj0=ixorna.pins['S1'], refobj1=ixorna.pins['S1'], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, -1], gridname0=rg_m1m2, refobj0=ixornab0.pins['S1'], refobj1=ixornab0.pins['S1'], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, -1], gridname0=rg_m1m2, refobj0=ixorpa.pins['S1'], refobj1=ixorpa.pins['S1'], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, -1], gridname0=rg_m1m2, refobj0=ixorpab0.pins['S1'], refobj1=ixorpab0.pins['S1'], via1=[0, 0])

    # power and groud rail
    xy = laygen.get_xy(obj = in2.template, gridname = rg_m1m2) * np.array([1, 0])
    rvdd=laygen.route("R"+objectname_pfix+"VDD0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=ip0.name, refinstname1=ip4.name)
    rvss=laygen.route("R"+objectname_pfix+"VSS0", laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=xy, gridname0=rg_m1m2,
                 refinstname0=in0.name, refinstname1=in4.name)

    # pins
    laygen.pin('VDD', laygen.layers['pin'][2], gridname=rg_m2m3, netname='VDD', refobj=rvdd)
    laygen.pin('VSS', laygen.layers['pin'][2], gridname=rg_m2m3, netname='VDD', refobj=rvss)
    laygen.pin('A', laygen.layers['pin'][1], gridname=rg_m2m3, netname='A', refobj=ra)
    laygen.pin('Ab', laygen.layers['pin'][2], gridname=rg_m2m3, netname='Ab', refobj=rab)
    laygen.pin('Ad', laygen.layers['pin'][2], gridname=rg_m2m3, netname='Ad', refobj=rad)
    laygen.pin('O', laygen.layers['pin'][3], gridname=rg_m2m3, netname='O', refobj=ro)

def generate_sarlogic_pulse_generator(laygen, objectname_pfix, placement_grid, templib_logic, 
                 routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4, m_dl, m_xor, num_inv_dl,
                 origin=np.array([0, 0])):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4
    m = m_dl
    m_xor = m_xor
    num_inv_dl = num_inv_dl

    # placement
    ibuf0 = laygen.relplace(name = "I" + objectname_pfix + 'BUF0', templatename = "inv_" + str(m) + "x", 
                gridname = pg, refobj = None, #xy=np.array([0, laygen.get_template_size(name="inv_" + str(m) + "x", gridname=pg, libname=templib_logic)[1]]), 
                transform="R0", template_libname=templib_logic)
    ibuf1 = laygen.relplace(name = "I" + objectname_pfix + 'BUF1', templatename = "inv_" + str(m) + "x", 
                gridname = pg, refobj = ibuf0, transform="R0", direction="right", template_libname=templib_logic)
    idl = []
    for i in range(num_inv_dl):
        tf='R0'
        if i==0:
            idl.append(laygen.relplace(name = "I" + objectname_pfix + 'DL' + str(i), templatename = "inv_" + str(m) + "x", 
                    gridname = pg, refobj = ibuf1, transform=tf, direction="right", template_libname=templib_logic))
        else:
            idl.append(laygen.relplace(name = "I" + objectname_pfix + 'DL' + str(i), templatename = "inv_" + str(m) + "x", 
                    gridname = pg, refobj = idl[-1], transform=tf, direction="right", template_libname=templib_logic))
    ixor = laygen.relplace(name = "I" + objectname_pfix + 'NAND', templatename = "nand_" + str(m_xor) + "x", 
                gridname = pg, refobj = idl[-1], transform="R0", direction="right", template_libname=templib_logic)
    iout = laygen.relplace(name = "I" + objectname_pfix + 'OUT', templatename = "inv_8x", 
                gridname = pg, refobj = ixor, transform="R0", direction="right", template_libname=templib_logic)

    # inv routing
    laygen.route(name=None, xy0=[0, 1], xy1=[2, 1], gridname0=rg_m2m3, refobj0=ibuf0.pins['O'], refobj1=ibuf0.pins['O'], via0=[0, 0])
    laygen.route(name=None, layer=laygen.layers['metal'][2], xy0=[2, 1], xy1=[2, 0], gridname0=rg_m2m3, refobj0=ibuf0.pins['O'], refobj1=ibuf0.pins['O'], endstyle0="extend", endstyle1="extend")
    laygen.route(name=None, xy0=[2, 0], xy1=[0, 0], gridname0=rg_m2m3, refobj0=ibuf0.pins['O'], refobj1=ibuf1.pins['I'])
    roa=laygen.route(name=None, xy0=[0, 1], xy1=[2, 1], gridname0=rg_m2m3, refobj0=ibuf1.pins['O'], refobj1=ibuf1.pins['O'], via0=[0, 0])
    laygen.route(name=None, layer=laygen.layers['metal'][2], xy0=[2, 1], xy1=[2, 0], gridname0=rg_m2m3, refobj0=ibuf1.pins['O'], refobj1=ibuf1.pins['O'], endstyle0="extend", endstyle1="extend")
    laygen.route(name=None, xy0=[2, 0], xy1=[0, 0], gridname0=rg_m2m3, refobj0=ibuf1.pins['O'], refobj1=idl[0].pins['I'])
    for i in range(num_inv_dl-1):
        laygen.route(name=None, xy0=[0, 1], xy1=[2, 1], gridname0=rg_m2m3, refobj0=idl[i].pins['O'], refobj1=idl[i].pins['O'], via0=[0, 0])
        laygen.route(name=None, layer=laygen.layers['metal'][2], xy0=[2, 1], xy1=[2, 0], gridname0=rg_m2m3, refobj0=idl[i].pins['O'], refobj1=idl[i].pins['O'], endstyle0="extend", endstyle1="extend")
        laygen.route(name=None, xy0=[2, 0], xy1=[0, 0], gridname0=rg_m2m3, refobj0=idl[i].pins['O'], refobj1=idl[i+1].pins['I'])

    # nand routing
    laygen.route(name=None, xy0=[0, 2], xy1=[0, 2], gridname0=rg_m2m3, refobj0=ibuf0.pins['I'], refobj1=ixor.pins['B'], via0=[0, 0], via1=[0, 0])
    ra=laygen.route(name=None, xy0=[0, 0], xy1=[0, 2], gridname0=rg_m2m3, refobj0=ibuf0.pins['I'], refobj1=ibuf0.pins['I'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 2], gridname0=rg_m2m3, refobj0=ixor.pins['B'], refobj1=ixor.pins['B'], via0=[0, 0])
    laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg_m2m3, refobj0=idl[num_inv_dl-1].pins['O'], refobj1=ixor.pins['A'], via0=[0, 0], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m2m3, refobj0=ixor.pins['O'], refobj1=iout.pins['I'], via0=[0, 0])
    
    # pin
    ro_pin_xy = laygen.get_inst_pin_xy(iout.name, 'O', rg_m2m3)
    laygen.pin(name='O', layer=laygen.layers['pin'][3], xy=ro_pin_xy, gridname=rg_m2m3)
    laygen.pin('A', laygen.layers['pin'][3], gridname=rg_m2m3, netname='A', refobj=ra)
    laygen.pin('OA', laygen.layers['pin'][2], gridname=rg_m2m3, netname='OA', refobj=roa)

    # power pin
    rvdd0_pin_xy = laygen.get_inst_pin_xy(ibuf0.name, 'VDD', rg_m1m2)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(ixor.name, 'VDD', rg_m1m2)
    rvss0_pin_xy = laygen.get_inst_pin_xy(ibuf0.name, 'VSS', rg_m1m2)
    rvss1_pin_xy = laygen.get_inst_pin_xy(ixor.name, 'VSS', rg_m1m2)

    laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=rg_m1m2)
    laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=rg_m1m2)

def generate_sarlogic_pulse_generator2(laygen, objectname_pfix, placement_grid, templib_logic, 
                 routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4, m_dl, m_xor, num_inv_dl,
                 origin=np.array([0, 0])):
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4
    m = m_dl
    m_xor = m_xor
    num_inv_dl = num_inv_dl

    # placement
    ibuf0 = laygen.relplace(name = "I" + objectname_pfix + 'BUF0', templatename = "inv_" + str(m) + "x", 
                gridname = pg, refobj = None, #xy=np.array([0, laygen.get_template_size(name="inv_" + str(m) + "x", gridname=pg, libname=templib_logic)[1]]), 
                transform="R0", template_libname=templib_logic)
    ibuf1 = laygen.relplace(name = "I" + objectname_pfix + 'BUF1', templatename = "inv_" + str(m) + "x", 
                gridname = pg, refobj = ibuf0, transform="R0", direction="right", template_libname=templib_logic)
    idl = []
    for i in range(num_inv_dl):
        tf='R0'
        if i==0:
            idl.append(laygen.relplace(name = "I" + objectname_pfix + 'DL' + str(i), templatename = "inv_" + str(m) + "x", 
                    gridname = pg, refobj = ibuf1, transform=tf, direction="right", template_libname=templib_logic))
        else:
            idl.append(laygen.relplace(name = "I" + objectname_pfix + 'DL' + str(i), templatename = "inv_" + str(m) + "x", 
                    gridname = pg, refobj = idl[-1], transform=tf, direction="right", template_libname=templib_logic))
    ixor = laygen.relplace(name = "I" + objectname_pfix + 'XOR', templatename = "sarlogic_xor", 
                gridname = pg, refobj = idl[-1], transform="R0", direction="right", template_libname=workinglib)

    # inv routing
    laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg_m2m3, refobj0=ibuf0.pins['O'], refobj1=ibuf1.pins['I'], via0=[0, 0], via1=[0, 0])
    roa=laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg_m2m3, refobj0=ibuf1.pins['O'], refobj1=idl[0].pins['I'], via0=[0, 0], via1=[0, 0])
    for i in range(num_inv_dl-1):
        laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg_m2m3, refobj0=idl[i].pins['O'], refobj1=idl[i+1].pins['I'], via0=[0, 0], via1=[0, 0])
    # xor routing
    laygen.route(name=None, xy0=[0, 3], xy1=[0, 3], gridname0=rg_m2m3, refobj0=ibuf0.pins['I'], refobj1=ixor.pins['A'], via0=[0, 0], via1=[0, 0])
    ra=laygen.route(name=None, xy0=[0, 0], xy1=[0, 3], gridname0=rg_m2m3, refobj0=ibuf0.pins['I'], refobj1=ibuf0.pins['I'])
    laygen.route(name=None, xy0=[0, 0], xy1=[0, 3], gridname0=rg_m2m3, refobj0=ixor.pins['A'], refobj1=ixor.pins['A'], via0=[0, 0])
    laygen.route(name=None, xy0=[-2, 0], xy1=[0, 0], gridname0=rg_m1m2, refobj0=ixor.pins['A'], refobj1=ixor.pins['A'], via1=[0, 0])
    laygen.route(name=None, xy0=[0, 2], xy1=[0, 0], gridname0=rg_m2m3, refobj0=ibuf1.pins['I'], refobj1=ixor.pins['Ab'], via0=[0, 0])
    laygen.route(name=None, xy0=[0, 1], xy1=[0, 0], gridname0=rg_m2m3, refobj0=idl[num_inv_dl-1].pins['O'], refobj1=ixor.pins['Ad'], via0=[0, 0])
    
    # pin
    ro_pin_xy = laygen.get_inst_pin_xy(ixor.name, 'O', rg_m2m3)
    laygen.pin(name='O', layer=laygen.layers['pin'][3], xy=ro_pin_xy, gridname=rg_m2m3)
    laygen.pin('A', laygen.layers['pin'][3], gridname=rg_m2m3, netname='A', refobj=ra)
    laygen.pin('OA', laygen.layers['pin'][2], gridname=rg_m2m3, netname='OA', refobj=roa)

    # power pin
    rvdd0_pin_xy = laygen.get_inst_pin_xy(ibuf0.name, 'VDD', rg_m1m2)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(ixor.name, 'VDD', rg_m1m2)
    rvss0_pin_xy = laygen.get_inst_pin_xy(ibuf0.name, 'VSS', rg_m1m2)
    rvss1_pin_xy = laygen.get_inst_pin_xy(ixor.name, 'VSS', rg_m1m2)

    laygen.pin(name='VDD', layer=laygen.layers['pin'][2], xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=rg_m1m2)
    laygen.pin(name='VSS', layer=laygen.layers['pin'][2], xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=rg_m1m2)

def generate_sarlogic_wret_v2_array_bb_pe(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m2m3,
                            routing_grid_m3m4, routing_grid_m4m5, num_bits=8, num_bits_row=4, num_inv_bb=4, m=4, m_buf=4,
                            m_tapbb=0, m_spacebb_1x=0, m_spacebb_2x=0,
                            m_space_left_4x=0, m_space_4x=0, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0])):
    """generate cap driver array """
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    num_row=int(num_bits/num_bits_row)
    if num_bits>num_row*num_bits_row:
        num_row+=1

    tap_name='tap'
    slogic_name='sarlogic_wret_v2'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'
    space_4x_name = 'space_4x'

    # placement
    itapl=[]
    islogic=[]
    itapr=[]
    isp4x=[]
    isp2x=[]
    isp1x=[]
    for i in range(num_row):
        if i%2==0: tf='R0'
        else: tf='MX'
        if i==0:
            itapl.append(laygen.place(name="I" + objectname_pfix + 'TAPL0', templatename=tap_name,
                                      gridname=pg, xy=origin, template_libname=templib_logic))
        else:
            itapl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPL'+str(i), templatename = tap_name,
                                         gridname = pg, refinstname = itapl[-1].name, transform=tf,
                                         direction = 'top', template_libname=templib_logic))
        refi = itapl[-1].name
        if not m_space_left_4x==0:
            ispl4x=laygen.relplace(name="I" + objectname_pfix + 'SPL4X'+str(i), templatename=space_4x_name,
                                   shape = np.array([m_space_left_4x, 1]), gridname=pg, transform=tf,
                                   refinstname=refi, template_libname=templib_logic)
            refi = ispl4x.name
        for j in range(num_bits_row):
            if i*num_bits_row+j < num_bits:
                islogic.append(laygen.relplace(name = "I" + objectname_pfix + 'CLG'+str(i*num_bits_row+j), templatename = slogic_name,
                                               gridname = pg, refinstname = refi, shape=np.array([1, 1]),
                                               transform=tf, template_libname=workinglib))
                refi = islogic[-1].name
            else:
                nfill = laygen.get_template_size(name=islogic[0].cellname, gridname=pg, libname=workinglib)[0]
                #ifill=laygen.relplace(name = "I" + objectname_pfix + 'CLGFILL'+str(i*num_bits_row+j), templatename = space_1x_name,
                #                               gridname = pg, refinstname = refi, shape=np.array([nfill, 1]),
                #                               transform=tf, template_libname=templib_logic)
                #refi = ifill.name
                nfill_4x = int(nfill/4)
                nfill_2x = int((nfill-nfill_4x*4)/2)
                nfill_1x = nfill-nfill_4x*4-nfill_2x*2
                if nfill_4x>0:
                    ifill_4x=laygen.relplace(name = "I" + objectname_pfix + 'SLFILL4X'+str(i*num_bits_row+j), templatename = space_4x_name,
                                             gridname = pg, refinstname = refi, shape=np.array([nfill_4x, 1]),
                                             transform=tf, template_libname=templib_logic)
                    refi = ifill_4x.name
                if nfill_2x>0:
                    ifill_2x=laygen.relplace(name = "I" + objectname_pfix + 'SLFILL2X'+str(i*num_bits_row+j), templatename = space_2x_name,
                                             gridname = pg, refinstname = refi, shape=np.array([nfill_2x, 1]),
                                             transform=tf, template_libname=templib_logic)
                    refi = ifill_2x.name
                if nfill_1x>0:
                    ifill_1x=laygen.relplace(name = "I" + objectname_pfix + 'SLFILL1X'+str(i*num_bits_row+j), templatename = space_2x_name,
                                             gridname = pg, refinstname = refi, shape=np.array([nfill_1x, 1]),
                                             transform=tf, template_libname=templib_logic)
                    refi = ifill_1x.name
        if not m_space_4x==0:
            isp4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP4X'+str(i), templatename=space_4x_name,
                         shape = np.array([m_space_4x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp4x[-1].name
        if not m_space_2x==0:
            isp2x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2X'+str(i), templatename=space_2x_name,
                         shape = np.array([m_space_2x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp2x[-1].name
        if not m_space_1x==0:
            isp1x.append(laygen.relplace(name="I" + objectname_pfix + 'SP1X'+str(i), templatename=space_1x_name,
                         shape=np.array([m_space_1x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp1x[-1].name
        itapr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPR'+str(i), templatename = tap_name,
                               gridname = pg, refinstname = refi, transform=tf, template_libname = templib_logic))

    # buffer with body biasing for timing calibration and pre-emphasis pulse generator
    # placement
    pg_name = 'pulse_gen'
    buf_name = 'inv_'+str(m_buf)+'x'
    inv_bb_name = 'inv_'+str(m)+'x'
    nor_name = 'nor_2x'
    pg_size = laygen.get_template_size(name=pg_name, gridname=pg, libname=workinglib)[0]
    sp_size = laygen.get_template_size(name='space_4x', gridname=pg, libname=templib_logic)[0]
    buf_size = laygen.get_template_size(name=buf_name, gridname=pg, libname=templib_logic)[0]
    nor_size = laygen.get_template_size(name=nor_name, gridname=pg, libname=templib_logic)[0]
    m_space_dmy = int(3*(pg_size+sp_size*2)/laygen.get_template_size(name='space_1x', gridname=pg, libname=templib_logic)[0])
    m_space_dmy2 = int(num_bits*(buf_size+nor_size)/laygen.get_template_size(name='space_1x', gridname=pg, libname=templib_logic)[0])
    x2 = laygen.templates.get_template('sarafe_nsw_doubleSA', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(buf_name, libname=logictemplib).xy[1][0] * num_bits \
         - laygen.templates.get_template(nor_name, libname=logictemplib).xy[1][0] * num_bits \
         - laygen.templates.get_template('tap_float', libname=logictemplib).xy[1][0] * 2 \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_spacebuf = int(round(x2 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    tap_space = (laygen.templates.get_template('tap', libname=logictemplib).xy[1][0]) / (laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0])
    #m_tapbuf = int(m_spacebuf / tap_space)
    m_spacebuf_2x = int((m_spacebuf - 0) / 2)
    m_spacebuf_1x = int(m_spacebuf - 0 - m_spacebuf_2x * 2)
    itapbbl=[]
    itapbbr=[]
    ispace_dmy=[]
    ispace_dmy2=[]
    iinv_bb=[]
    ipg_zmid=[]
    ipg_zm=[]
    ipg_zp=[]
    isp_zmid=[]
    isp_zm=[]
    isp_zp=[]
    inor=[]
    ibuf=[]
    ispacebb_1x=[]
    ispacebb_2x=[]
    itapbb=[]
    for i in range(num_bits+3+5+3): # 4 dummy rows for routing space, 6 rows for nor+buf
        if i%2==0: tf='MX'
        else: tf='R0'
        if i==0:
            itapbbl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBBL0', templatename = 'tap_float', direction='top',
                               gridname = pg, refinstname = itapl[-1].name, transform=tf, template_libname = templib_logic))
            itapbbr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBBR0', templatename = 'tap_float', direction='top',
                               gridname = pg, refinstname = itapr[-1].name, transform=tf, template_libname = templib_logic))
            ispace_dmy.append(laygen.relplace(name = "I" + objectname_pfix + 'SPDMY'+str(i), templatename = 'space_1x', direction='right', shape=np.array([m_space_dmy,1]),
                               gridname = pg, refinstname = itapbbl[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_1x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB1x'+str(i), templatename = 'space_1x', direction='right', shape=np.array([m_spacebb_1x,1]),
                               gridname = pg, refinstname = ispace_dmy[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_2x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB2x'+str(i), templatename = 'space_2x', direction='right', shape=np.array([m_spacebb_2x,1]),
                               gridname = pg, refinstname = ispacebb_1x[-1].name, transform=tf, template_libname = templib_logic))
            itapbb.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBB'+str(i), templatename = 'tap_float', direction='right', shape=np.array([m_tapbb,1]),
                               gridname = pg, refinstname = ispacebb_2x[-1].name, transform=tf, template_libname = templib_logic))
        elif i<3:
            itapbbl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBBL'+str(i), templatename = 'tap_float', direction='top',
                               gridname = pg, refinstname = itapbbl[-1].name, transform=tf, template_libname = templib_logic))
            itapbbr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBBR'+str(i), templatename = 'tap_float', direction='top',
                               gridname = pg, refinstname = itapbbr[-1].name, transform=tf, template_libname = templib_logic))
            ispace_dmy.append(laygen.relplace(name = "I" + objectname_pfix + 'SPDMY'+str(i), templatename = 'space_1x', direction='right', shape=np.array([m_space_dmy,1]),
                               gridname = pg, refinstname = itapbbl[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_1x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB1x'+str(i), templatename = 'space_1x', direction='right', shape=np.array([m_spacebb_1x,1]),
                               gridname = pg, refinstname = ispace_dmy[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_2x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB2x'+str(i), templatename = 'space_2x', direction='right', shape=np.array([m_spacebb_2x,1]),
                               gridname = pg, refinstname = ispacebb_1x[-1].name, transform=tf, template_libname = templib_logic))
            itapbb.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBB'+str(i), templatename = 'tap_float', direction='right', shape=np.array([m_tapbb,1]),
                               gridname = pg, refinstname = ispacebb_2x[-1].name, transform=tf, template_libname = templib_logic))
        elif i<num_bits+3:
            itapbbl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBBL'+str(i), templatename = 'tap_float', direction='top',
                               gridname = pg, refinstname = itapbbl[-1].name, transform=tf, template_libname = templib_logic))
            itapbbr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBBR'+str(i), templatename = 'tap_float', direction='top',
                               gridname = pg, refinstname = itapbbr[-1].name, transform=tf, template_libname = templib_logic))
            isp_zmid.append(laygen.relplace(name = "I" + objectname_pfix + 'SPZMID'+str(i), templatename = 'space_4x', direction='right', shape=np.array([2,1]),
                               gridname = pg, refinstname = itapbbl[-1].name, transform=tf, template_libname = templib_logic))
            ipg_zmid.append(laygen.relplace(name = "I" + objectname_pfix + 'PGZMID'+str(i), templatename = pg_name, direction='right',
                               gridname = pg, refinstname = isp_zmid[-1].name, transform=tf, template_libname = workinglib))
            isp_zm.append(laygen.relplace(name = "I" + objectname_pfix + 'SPZM'+str(i), templatename = 'space_4x', direction='right', shape=np.array([2,1]),
                               gridname = pg, refinstname = ipg_zmid[-1].name, transform=tf, template_libname = templib_logic))
            ipg_zm.append(laygen.relplace(name = "I" + objectname_pfix + 'PGZM'+str(i), templatename = pg_name, direction='right',
                               gridname = pg, refinstname = isp_zm[-1].name, transform=tf, template_libname = workinglib))
            isp_zp.append(laygen.relplace(name = "I" + objectname_pfix + 'SPZP'+str(i), templatename = 'space_4x', direction='right', shape=np.array([2,1]),
                               gridname = pg, refinstname = ipg_zm[-1].name, transform=tf, template_libname = templib_logic))
            ipg_zp.append(laygen.relplace(name = "I" + objectname_pfix + 'PGZP'+str(i), templatename = pg_name, direction='right',
                               gridname = pg, refinstname = isp_zp[-1].name, transform=tf, template_libname = workinglib))
            ispacebb_1x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB1x'+str(i), templatename = 'space_1x', direction='right', shape=np.array([m_spacebb_1x,1]),
                               gridname = pg, refinstname = ipg_zp[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_2x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB2x'+str(i), templatename = 'space_2x', direction='right', shape=np.array([m_spacebb_2x,1]),
                               gridname = pg, refinstname = ispacebb_1x[-1].name, transform=tf, template_libname = templib_logic))
            itapbb.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBB'+str(i), templatename = 'tap_float', direction='right', shape=np.array([m_tapbb,1]),
                               gridname = pg, refinstname = ispacebb_2x[-1].name, transform=tf, template_libname = templib_logic))
        elif i<num_bits+3+5-1:
            itapbbl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBBL'+str(i), templatename = 'tap_float', direction='top',
                               gridname = pg, refinstname = itapbbl[-1].name, transform=tf, template_libname = templib_logic))
            itapbbr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBBR'+str(i), templatename = 'tap_float', direction='top',
                               gridname = pg, refinstname = itapbbr[-1].name, transform=tf, template_libname = templib_logic))
            ispace_dmy2.append(laygen.relplace(name = "I" + objectname_pfix + 'SPDMY'+str(i), templatename = 'space_1x', direction='right', shape=np.array([m_space_dmy,1]),
                               gridname = pg, refinstname = itapbbl[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_1x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB1x'+str(i), templatename = 'space_1x', direction='right', shape=np.array([m_spacebb_1x,1]),
                               gridname = pg, refinstname = ispace_dmy2[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_2x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB2x'+str(i), templatename = 'space_2x', direction='right', shape=np.array([m_spacebb_2x,1]),
                               gridname = pg, refinstname = ispacebb_1x[-1].name, transform=tf, template_libname = templib_logic))
            itapbb.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBB'+str(i), templatename = 'tap_float', direction='right', shape=np.array([m_tapbb,1]),
                               gridname = pg, refinstname = ispacebb_2x[-1].name, transform=tf, template_libname = templib_logic))
        elif i<num_bits+3+5:
            itapl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPL'+str(i), templatename = 'tap', direction='top',
                               gridname = pg, refinstname = itapbbl[-1].name, transform=tf, template_libname = templib_logic))
            itapr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPR'+str(i), templatename = 'tap', direction='top',
                               gridname = pg, refinstname = itapbbr[-1].name, transform=tf, template_libname = templib_logic))
            ispace_dmy2.append(laygen.relplace(name = "I" + objectname_pfix + 'SPDMY'+str(i), templatename = 'space_1x', direction='right', shape=np.array([m_space_dmy,1]),
                               gridname = pg, refinstname = itapl[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_1x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB1x'+str(i), templatename = 'space_1x', direction='right', shape=np.array([m_spacebb_1x,1]),
                               gridname = pg, refinstname = ispace_dmy2[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_2x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB2x'+str(i), templatename = 'space_2x', direction='right', shape=np.array([m_spacebb_2x,1]),
                               gridname = pg, refinstname = ispacebb_1x[-1].name, transform=tf, template_libname = templib_logic))
            laygen.relplace(name = "I" + objectname_pfix + 'TAP'+str(i), templatename = 'tap', direction='right', shape=np.array([m_tapbb,1]),
                               gridname = pg, refinstname = ispacebb_2x[-1].name, transform=tf, template_libname = templib_logic)
        elif i<num_bits+3+5+1:
            itapl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPL'+str(i), templatename = 'tap', direction='top',
                               gridname = pg, refinstname = itapl[-1].name, transform=tf, template_libname = templib_logic))
            itapr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPR'+str(i), templatename = 'tap', direction='top',
                               gridname = pg, refinstname = itapr[-1].name, transform=tf, template_libname = templib_logic))
            inor.append(laygen.relplace(name = "I" + objectname_pfix + 'NOR'+str(i), templatename = nor_name, direction='right', 
                               gridname = pg, refinstname = itapl[-1].name, transform=tf, template_libname = templib_logic))
            ibuf.append(laygen.relplace(name = "I" + objectname_pfix + 'BUF'+str(i), templatename = buf_name, direction='right', 
                               gridname = pg, refinstname = inor[-1].name, transform=tf, template_libname = templib_logic))
            for j in range(num_bits-1):
                inor.append(laygen.relplace(name = "I" + objectname_pfix + 'NOR'+str(i)+str(j), templatename = nor_name, direction='right', 
                               gridname = pg, refinstname = ibuf[-1].name, transform=tf, template_libname = templib_logic))
                ibuf.append(laygen.relplace(name = "I" + objectname_pfix + 'BUF'+str(i)+str(j), templatename = buf_name, direction='right', 
                               gridname = pg, refinstname = inor[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_1x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB1x'+str(i), templatename = 'space_1x', direction='right', shape=np.array([m_spacebuf_1x,1]),
                               gridname = pg, refinstname = ibuf[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_2x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB2x'+str(i), templatename = 'space_2x', direction='right', shape=np.array([m_spacebuf_2x,1]),
                               gridname = pg, refinstname = ispacebb_1x[-1].name, transform=tf, template_libname = templib_logic))
        elif i<num_bits+3+5+2:
            itapl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBBL'+str(i), templatename = 'tap', direction='top',
                               gridname = pg, refinstname = itapl[-1].name, transform=tf, template_libname = templib_logic))
            itapr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBBR'+str(i), templatename = 'tap', direction='top',
                               gridname = pg, refinstname = itapr[-1].name, transform=tf, template_libname = templib_logic))
            ispace_null = laygen.relplace(name = "I" + objectname_pfix + 'NULL'+str(i), templatename = 'space_2x', direction='right', 
                               gridname = pg, refinstname = itapl[-1].name, transform=tf, template_libname = templib_logic)
            inor.append(laygen.relplace(name = "I" + objectname_pfix + 'NOR'+str(i), templatename = nor_name, direction='right', 
                               gridname = pg, refinstname = ispace_null.name, transform=tf, template_libname = templib_logic))
            ibuf.append(laygen.relplace(name = "I" + objectname_pfix + 'BUF'+str(i), templatename = buf_name, direction='right', 
                               gridname = pg, refinstname = inor[-1].name, transform=tf, template_libname = templib_logic))
            for j in range(num_bits-1):
                inor.append(laygen.relplace(name = "I" + objectname_pfix + 'NOR'+str(i)+str(j), templatename = nor_name, direction='right', 
                               gridname = pg, refinstname = ibuf[-1].name, transform=tf, template_libname = templib_logic))
                ibuf.append(laygen.relplace(name = "I" + objectname_pfix + 'BUF'+str(i)+str(j), templatename = buf_name, direction='right', 
                               gridname = pg, refinstname = inor[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_1x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB1x'+str(i), templatename = 'space_1x', direction='right', shape=np.array([m_spacebuf_1x,1]),
                               gridname = pg, refinstname = ibuf[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_2x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB2x'+str(i), templatename = 'space_2x', direction='right', shape=np.array([m_spacebuf_2x-1,1]),
                               gridname = pg, refinstname = ispacebb_1x[-1].name, transform=tf, template_libname = templib_logic))
        elif i<num_bits+3+5+3:
            itapl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBBL'+str(i), templatename = 'tap', direction='top',
                               gridname = pg, refinstname = itapl[-1].name, transform=tf, template_libname = templib_logic))
            itapr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPBBR'+str(i), templatename = 'tap', direction='top',
                               gridname = pg, refinstname = itapr[-1].name, transform=tf, template_libname = templib_logic))
            ispace_null = laygen.relplace(name = "I" + objectname_pfix + 'NULL'+str(i), templatename = 'space_4x', direction='right', 
                               gridname = pg, refinstname = itapl[-1].name, transform=tf, template_libname = templib_logic)
            inor.append(laygen.relplace(name = "I" + objectname_pfix + 'NOR'+str(i), templatename = nor_name, direction='right', 
                               gridname = pg, refinstname = ispace_null.name, transform=tf, template_libname = templib_logic))
            ibuf.append(laygen.relplace(name = "I" + objectname_pfix + 'BUF'+str(i), templatename = buf_name, direction='right', 
                               gridname = pg, refinstname = inor[-1].name, transform=tf, template_libname = templib_logic))
            for j in range(num_bits-1):
                inor.append(laygen.relplace(name = "I" + objectname_pfix + 'NOR'+str(i)+str(j), templatename = nor_name, direction='right', 
                               gridname = pg, refinstname = ibuf[-1].name, transform=tf, template_libname = templib_logic))
                ibuf.append(laygen.relplace(name = "I" + objectname_pfix + 'BUF'+str(i)+str(j), templatename = buf_name, direction='right', 
                               gridname = pg, refinstname = inor[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_1x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB1x'+str(i), templatename = 'space_1x', direction='right', shape=np.array([m_spacebuf_1x,1]),
                               gridname = pg, refinstname = ibuf[-1].name, transform=tf, template_libname = templib_logic))
            ispacebb_2x.append(laygen.relplace(name = "I" + objectname_pfix + 'SPBB2x'+str(i), templatename = 'space_2x', direction='right', shape=np.array([m_spacebuf_2x-2,1]),
                               gridname = pg, refinstname = ispacebb_1x[-1].name, transform=tf, template_libname = templib_logic))
    # internal pins
    pdict = laygen.get_inst_pin_xy(None, None, rg_m3m4)
    # rst route
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4,
                 refinstname0=islogic[0].name, refpinname0='RST2', refinstindex0=np.array([0, 0]),
                 refinstname1=islogic[num_bits_row*(num_row-1)].name, refpinname1='RST2', refinstindex1=np.array([0, 0]))
    rrst=[]
    for i in range(num_row):
        rrst.append(laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([1, 0]),
                                 gridname0=rg_m4m5, 
                                 refinstname0=islogic[i*num_bits_row].name, refpinname0='RST',
                                 refinstindex0=np.array([0, 0]),
                                 refinstname1=islogic[min(i*num_bits_row+num_bits_row-1, num_bits-1)].name, refpinname1='RST',
                                 refinstindex1=np.array([0, 0])))
    # saop route
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4,
                 refinstname0=islogic[0].name, refpinname0='SAOP2', refinstindex0=np.array([0, 0]),
                 refinstname1=islogic[num_bits_row*(num_row-1)].name, refpinname1='SAOP2', refinstindex1=np.array([0, 0]))
    rsaop=[]
    for i in range(num_row):
        rsaop.append(
            laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([1, 0]), gridname0=rg_m4m5,
                         refinstname0=islogic[i*num_bits_row].name, refpinname0='SAOP', 
                         refinstindex0=np.array([0, 0]),
                         refinstname1=islogic[min(i*num_bits_row+num_bits_row-1, num_bits-1)].name, refpinname1='SAOP',
                         refinstindex1=np.array([0, 0])))
    # saom route
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4,
                 refinstname0=islogic[0].name, refpinname0='SAOM2', refinstindex0=np.array([0, 0]),
                 refinstname1=islogic[num_bits_row*(num_row-1)].name, refpinname1='SAOM2', refinstindex1=np.array([0, 0]))
    rsaom = []
    for i in range(num_row):
        rsaom.append(
            laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([1, 0]), gridname0=rg_m4m5,
                         refinstname0=islogic[i*num_bits_row].name, refpinname0='SAOM', 
                         refinstindex0=np.array([0, 0]),
                         refinstname1=islogic[min(i*num_bits_row+num_bits_row-1, num_bits-1)].name, refpinname1='SAOM',
                         refinstindex1=np.array([0, 0])))
    # nor+buf route
    for i in range(num_bits*3):
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg_m2m3, 
                 refobj0=inor[i].pins['O'], refobj1=ibuf[i].pins['I'], via0=[0, 0], via1=[0, 0])
    #pins
    xy=laygen.get_rect_xy(rrst[0].name, rg_m4m5, sort=True)
    laygen.boundary_pin_from_rect(rrst[0], rg_m4m5, 'RST', laygen.layers['pin'][4], size=6, direction='left')
    #rv0, rrst0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], xy[0], np.array([xy[0][0]+4, 2]), rg_m4m5)
    #laygen.boundary_pin_from_rect(rrst0, rg_m4m5, 'RST', laygen.layers['pin'][5], size=6, direction='bottom')
    laygen.boundary_pin_from_rect(rsaop[0], rg_m4m5, "SAOP", laygen.layers['pin'][4], size=6, direction='left')
    laygen.boundary_pin_from_rect(rsaom[0], rg_m4m5, "SAOM", laygen.layers['pin'][4], size=6, direction='left')
    y1 = laygen.get_template_size(name=islogic[0].cellname, gridname=rg_m4m5, libname=workinglib)[1]
    y2 = y1*(num_row)
    pdict2 = laygen.get_inst_pin_xy(None, None, rg_m3m4, sort=True)
    pdict_m4m5 = laygen.get_inst_pin_xy(None, None, rg_m4m5, sort=True)
    for i in range(num_row):
        for j in range(num_bits_row):
            if i*num_bits_row+j < num_bits:
                rv0, rsb0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5[islogic[i*num_bits_row+j].name]['SB'][0],
                                            np.array([pdict_m4m5[islogic[i*num_bits_row+j].name]['SB'][0][0]+1+i+6, 0]), rg_m4m5)
                rv0, rreto0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5[islogic[i*num_bits_row+j].name]['RETO'][0],
                                            np.array([pdict_m4m5[islogic[i*num_bits_row+j].name]['RETO'][0][0]+1+i+2, 0]), rg_m4m5)
                laygen.boundary_pin_from_rect(rsb0, rg_m4m5, 'SB<'+str(i*num_bits_row+j)+'>', laygen.layers['pin'][5], size=6, direction='bottom')
                laygen.boundary_pin_from_rect(rreto0, rg_m4m5, 'RETO<'+str(i*num_bits_row+j)+'>', laygen.layers['pin'][5], size=6, direction='bottom')

    # Pg routing: input
    for i in range(num_bits):
        laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                        pdict[islogic[i].name]['ZMID'][0], 
                        np.array([pdict_m4m5[ipg_zmid[i].name]['A'][0][0]-10+i, laygen.get_inst_bbox(ispace_dmy[0].name, rg_m4m5)[0][1]+i+1]),
                        pdict[islogic[i].name]['ZMID'][0][0]+(num_row-int(i/2)-1)+(1+num_row)*0-10, rg_m4m5)
        laygen.route(name=None, xy0=[0, 0], xy1=[-10+i, 0], gridname0=rg_m3m4, refobj0=ipg_zmid[i].pins['A'], refobj1=ipg_zmid[i].pins['A'], via0=[0,0])
        laygen.route(name=None, xy0=[pdict_m4m5[ipg_zmid[i].name]['A'][0][0]-10+i, laygen.get_inst_bbox(ispace_dmy[0].name, rg_m4m5)[0][1]+i+1], 
                        xy1=[-10+i, 0], gridname0=rg_m3m4, refobj0=None, refobj1=ipg_zmid[i].pins['A'], via0=[0,0], via1=[0,0])
        laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                        pdict[islogic[i].name]['ZM'][0], 
                        np.array([pdict_m4m5[ipg_zm[i].name]['A'][0][0]-10+i, laygen.get_inst_bbox(ispace_dmy[0].name, rg_m4m5)[0][1]+i+1+num_bits*1]),
                        pdict[islogic[i].name]['ZM'][0][0]+(num_row-int(i/2)-1)+(1+num_row)*1-10, rg_m4m5)
        laygen.route(name=None, xy0=[0, 0], xy1=[-10+i, 0], gridname0=rg_m3m4, refobj0=ipg_zm[i].pins['A'], refobj1=ipg_zm[i].pins['A'], via0=[0,0])
        laygen.route(name=None, xy0=[pdict_m4m5[ipg_zm[i].name]['A'][0][0]-10+i, laygen.get_inst_bbox(ispace_dmy[0].name, rg_m4m5)[0][1]+i+1+num_bits*1], 
                        xy1=[-10+i, 0], gridname0=rg_m3m4, refobj0=None, refobj1=ipg_zm[i].pins['A'], via0=[0,0], via1=[0,0])
        laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5],
                        pdict[islogic[i].name]['ZP'][0], 
                        np.array([pdict_m4m5[ipg_zp[i].name]['A'][0][0]-10+i, laygen.get_inst_bbox(ispace_dmy[0].name, rg_m4m5)[0][1]+i+1+num_bits*2]),
                        pdict[islogic[i].name]['ZP'][0][0]+(num_row-int(i/2)-1)+(1+num_row)*2-10, rg_m4m5)
        laygen.route(name=None, xy0=[0, 0], xy1=[-10+i, 0], gridname0=rg_m3m4, refobj0=ipg_zp[i].pins['A'], refobj1=ipg_zp[i].pins['A'], via0=[0,0])
        laygen.route(name=None, xy0=[pdict_m4m5[ipg_zp[i].name]['A'][0][0]-10+i, laygen.get_inst_bbox(ispace_dmy[0].name, rg_m4m5)[0][1]+i+1+num_bits*2], 
                        xy1=[-10+i, 0], gridname0=rg_m3m4, refobj0=None, refobj1=ipg_zp[i].pins['A'], via0=[0,0], via1=[0,0])
    # Pg routing: output
    for i in range(num_bits):
        #ZMID-OA
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 3], gridname0=rg_m3m4, refobj0=ipg_zmid[i].pins['OA'], refobj1=ipg_zmid[i].pins['OA'], via1=[0,0])
        laygen.route(name=None, xy0=[0, 3], xy1=[-3+2*i, 3], gridname0=rg_m4m5, refobj0=ipg_zmid[i].pins['OA'], refobj1=ipg_zmid[i].pins['OA'], via1=[0,0])
        laygen.route(name=None, xy0=[pdict_m4m5[ipg_zmid[i].name]['OA'][0][0]-3+2*i, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i], 
                        xy1=[-3+2*i, 3], gridname0=rg_m4m5, refobj0=None, refobj1=ipg_zmid[i].pins['OA'], via0=[0,0])
        laygen.route(name=None, xy0=[pdict_m4m5[ipg_zmid[i].name]['OA'][0][0]-3+2*i, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i], 
                        xy1=[pdict[inor[i].name]['B'][0][0], laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i], 
                        gridname0=rg_m3m4, refobj0=None, refobj1=None, via1=[0,0])
        laygen.route(name=None, xy0=[pdict[inor[i].name]['B'][0][0], laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m3m4)[0][1]+i], 
                        xy1=[0, 0], gridname0=rg_m3m4, refobj0=None, refobj1=inor[i].pins['B'])
        #ZMID-O
        if not i==(num_bits-1):
            laygen.route(name=None, xy0=[0, 0], xy1=[0, -1], gridname0=rg_m3m4, refobj0=ipg_zmid[i+1].pins['O'], refobj1=ipg_zmid[i+1].pins['O'], via1=[0,0])
            laygen.route(name=None, xy0=[0, -1], xy1=[1-2*i, -1], gridname0=rg_m4m5, refobj0=ipg_zmid[i+1].pins['O'], refobj1=ipg_zmid[i+1].pins['O'], via1=[0,0])
            laygen.route(name=None, xy0=[pdict_m4m5[ipg_zmid[i+1].name]['O'][0][0]+1-2*i, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*1], 
                        xy1=[1-2*i, -1], gridname0=rg_m4m5, refobj0=None, refobj1=ipg_zmid[i+1].pins['O'], via0=[0,0])
            laygen.route(name=None, xy0=[pdict_m4m5[ipg_zmid[i+1].name]['O'][0][0]+1-2*i, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*1], 
                        xy1=[pdict[inor[i].name]['A'][0][0], laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*1], 
                        gridname0=rg_m3m4, refobj0=None, refobj1=None, via1=[0,0])
            laygen.route(name=None, xy0=[pdict[inor[i].name]['A'][0][0], laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m3m4)[0][1]+i+num_bits*1], 
                        xy1=[0, 0], gridname0=rg_m3m4, refobj0=None, refobj1=inor[i].pins['A'])
        else:
            laygen.route(name=None, xy0=[0, 0], xy1=[0, -3], gridname0=rg_m2m3, refobj0=inor[i].pins['A'], refobj1=inor[i].pins['A'], via1=[0,0])
        #ZM-OA
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 3], gridname0=rg_m3m4, refobj0=ipg_zm[i].pins['OA'], refobj1=ipg_zm[i].pins['OA'], via1=[0,0])
        laygen.route(name=None, xy0=[0, 3], xy1=[-3+2*i, 3], gridname0=rg_m4m5, refobj0=ipg_zm[i].pins['OA'], refobj1=ipg_zm[i].pins['OA'], via1=[0,0])
        laygen.route(name=None, xy0=[pdict_m4m5[ipg_zm[i].name]['OA'][0][0]-3+2*i, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*2], 
                        xy1=[-3+2*i, 3], gridname0=rg_m4m5, refobj0=None, refobj1=ipg_zm[i].pins['OA'], via0=[0,0])
        laygen.route(name=None, xy0=[pdict_m4m5[ipg_zm[i].name]['OA'][0][0]-3+2*i, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*2], 
                        xy1=[pdict[inor[i+num_bits].name]['B'][0][0], laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*2], 
                        gridname0=rg_m3m4, refobj0=None, refobj1=None, via1=[0,0])
        laygen.route(name=None, xy0=[pdict[inor[i+num_bits].name]['B'][0][0], laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m3m4)[0][1]+i+num_bits*2], 
                        xy1=[0, 0], gridname0=rg_m3m4, refobj0=None, refobj1=inor[i+num_bits].pins['B'])
        #ZM-O
        if not i==(num_bits-1):
            laygen.route(name=None, xy0=[0, 0], xy1=[0, -1], gridname0=rg_m3m4, refobj0=ipg_zm[i+1].pins['O'], refobj1=ipg_zm[i+1].pins['O'], via1=[0,0])
            laygen.route(name=None, xy0=[0, -1], xy1=[1-2*i, -1], gridname0=rg_m4m5, refobj0=ipg_zm[i+1].pins['O'], refobj1=ipg_zm[i+1].pins['O'], via1=[0,0])
            laygen.route(name=None, xy0=[pdict_m4m5[ipg_zm[i+1].name]['O'][0][0]+1-2*i, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*3], 
                        xy1=[1-2*i, -1], gridname0=rg_m4m5, refobj0=None, refobj1=ipg_zm[i+1].pins['O'], via0=[0,0])
            laygen.route(name=None, xy0=[pdict_m4m5[ipg_zm[i+1].name]['O'][0][0]+1-2*i, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*3], 
                        xy1=[pdict[inor[i+num_bits].name]['A'][0][0], laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*3], 
                        gridname0=rg_m3m4, refobj0=None, refobj1=None, via1=[0,0])
            laygen.route(name=None, xy0=[pdict[inor[i+num_bits].name]['A'][0][0], laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m3m4)[0][1]+i+num_bits*3], 
                        xy1=[0, 0], gridname0=rg_m3m4, refobj0=None, refobj1=inor[i+num_bits].pins['A'])
        else:
            laygen.route(name=None, xy0=[0, 0], xy1=[0, -3], gridname0=rg_m2m3, refobj0=inor[i+num_bits].pins['A'], refobj1=inor[i+num_bits].pins['A'], via1=[0,0])
        #ZP-OA
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 3], gridname0=rg_m3m4, refobj0=ipg_zp[i].pins['OA'], refobj1=ipg_zp[i].pins['OA'], via1=[0,0])
        laygen.route(name=None, xy0=[0, 3], xy1=[-3+2*i, 3], gridname0=rg_m4m5, refobj0=ipg_zp[i].pins['OA'], refobj1=ipg_zp[i].pins['OA'], via1=[0,0])
        laygen.route(name=None, xy0=[pdict_m4m5[ipg_zp[i].name]['OA'][0][0]-3+2*i, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*4], 
                        xy1=[-3+2*i, 3], gridname0=rg_m4m5, refobj0=None, refobj1=ipg_zp[i].pins['OA'], via0=[0,0])
        laygen.route(name=None, xy0=[pdict_m4m5[ipg_zp[i].name]['OA'][0][0]-3+2*i, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*4], 
                        xy1=[pdict[inor[i+num_bits*2].name]['B'][0][0]+2, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*4], 
                        gridname0=rg_m4m5, refobj0=None, refobj1=None, via1=[0,0])
        laygen.route(name=None, xy0=[pdict_m4m5[inor[i+num_bits*2].name]['B'][0][0]+2, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*4], 
                        xy1=[2, -4], gridname0=rg_m4m5, refobj0=None, refobj1=inor[i+num_bits*2].pins['B'], via1=[0,0])
        laygen.route(name=None, xy0=[2, -4], xy1=[0, -4], gridname0=rg_m3m4, refobj0=inor[i+num_bits*2].pins['B'], refobj1=inor[i+num_bits*2].pins['B'], via1=[0,0])
        laygen.route(name=None, xy0=[0, 0], xy1=[0, -4], gridname0=rg_m3m4, refobj0=inor[i+num_bits*2].pins['B'], refobj1=inor[i+num_bits*2].pins['B'])
        #ZP-O
        if not i==(num_bits-1):
            laygen.route(name=None, xy0=[0, 0], xy1=[0, -1], gridname0=rg_m3m4, refobj0=ipg_zp[i+1].pins['O'], refobj1=ipg_zp[i+1].pins['O'], via1=[0,0])
            laygen.route(name=None, xy0=[0, -1], xy1=[1-2*i, -1], gridname0=rg_m4m5, refobj0=ipg_zp[i+1].pins['O'], refobj1=ipg_zp[i+1].pins['O'], via1=[0,0])
            laygen.route(name=None, xy0=[pdict_m4m5[ipg_zp[i+1].name]['O'][0][0]+1-2*i, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*5], 
                        xy1=[1-2*i, -1], gridname0=rg_m4m5, refobj0=None, refobj1=ipg_zp[i+1].pins['O'], via0=[0,0])
            laygen.route(name=None, xy0=[pdict_m4m5[ipg_zp[i+1].name]['O'][0][0]+1-2*i, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*5], 
                        xy1=[pdict[inor[i+num_bits*2].name]['A'][0][0]+2, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*5], 
                        gridname0=rg_m4m5, refobj0=None, refobj1=None, via1=[0,0])
            laygen.route(name=None, xy0=[pdict_m4m5[inor[i+num_bits*2].name]['A'][0][0]+2, laygen.get_inst_bbox(ispace_dmy2[0].name, rg_m4m5)[0][1]+i+num_bits*5], 
                        xy1=[2, -4], gridname0=rg_m4m5, refobj0=None, refobj1=inor[i+num_bits*2].pins['A'], via1=[0,0])
            laygen.route(name=None, xy0=[2, -4], xy1=[0, -4], gridname0=rg_m3m4, refobj0=inor[i+num_bits*2].pins['A'], refobj1=inor[i+num_bits*2].pins['A'], via1=[0,0])
            laygen.route(name=None, xy0=[0, 0], xy1=[0, -4], gridname0=rg_m3m4, refobj0=inor[i+num_bits*2].pins['A'], refobj1=inor[i+num_bits*2].pins['A'])
        else:
            laygen.route(name=None, xy0=[0, 0], xy1=[0, -3], gridname0=rg_m2m3, refobj0=inor[i+num_bits*2].pins['A'], refobj1=inor[i+num_bits*2].pins['A'], via1=[0,0])

        # routing: output    
        if i%2==0:
            rv0, rh0, rzmid0 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                pdict_m4m5[ibuf[i+num_bits*0].name]['O'][0],
                np.array([pdict_m4m5[inor[num_bits*2+3].name]['B'][0][0]-int(i/2)-0, pdict_m4m5[ibuf[i+num_bits*2].name]['O'][0][1]+6]), 
                pdict_m4m5[ibuf[i+num_bits*0].name]['O'][0][1]-3+i, rg_m3m4, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
            rv0, rh0, rzm0 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                pdict_m4m5[ibuf[i+num_bits*1].name]['O'][0],
                np.array([pdict_m4m5[inor[num_bits*2+3].name]['A'][0][0]-int(i/2)+7, pdict_m4m5[ibuf[i+num_bits*2].name]['O'][0][1]+6]), 
                pdict_m4m5[ibuf[i+num_bits*1].name]['O'][0][1]-3+i, rg_m3m4, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
            rv0, rh0, rzp0 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                pdict_m4m5[ibuf[i+num_bits*2].name]['O'][0],
                np.array([pdict_m4m5[inor[num_bits*2+3].name]['A'][0][0]-int(i/2)+7+(num_row+1)*1, pdict_m4m5[ibuf[i+num_bits*2].name]['O'][0][1]+6]), 
                pdict_m4m5[ibuf[i+num_bits*2].name]['O'][0][1]-3+i, rg_m3m4, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
            laygen.boundary_pin_from_rect(rzp0, rg_m4m5, 'ZP<'+str(i)+'>', laygen.layers['pin'][5], size=6, direction='top')
            laygen.boundary_pin_from_rect(rzmid0, rg_m4m5, 'ZMID<'+str(i)+'>', laygen.layers['pin'][5], size=6, direction='top')
            laygen.boundary_pin_from_rect(rzm0, rg_m4m5, 'ZM<'+str(i)+'>', laygen.layers['pin'][5], size=6, direction='top')
        else:
            rv0, rh0, rzmid0 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                pdict_m4m5[ibuf[i+num_bits*0].name]['O'][0],
                np.array([pdict_m4m5[inor[num_bits*2+6].name]['B'][0][0]-int(i/2)-0, pdict_m4m5[ibuf[i+num_bits*2].name]['O'][0][1]+6]), 
                pdict_m4m5[ibuf[i+num_bits*0].name]['O'][0][1]-3+i, rg_m3m4, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
            rv0, rh0, rzm0 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                pdict_m4m5[ibuf[i+num_bits*1].name]['O'][0],
                np.array([pdict_m4m5[inor[num_bits*2+6].name]['A'][0][0]-int(i/2)+7, pdict_m4m5[ibuf[i+num_bits*2].name]['O'][0][1]+6]), 
                pdict_m4m5[ibuf[i+num_bits*1].name]['O'][0][1]-3+i, rg_m3m4, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
            rv0, rh0, rzp0 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                pdict_m4m5[ibuf[i+num_bits*2].name]['O'][0],
                np.array([pdict_m4m5[inor[num_bits*2+6].name]['A'][0][0]-int(i/2)+7+(num_row+1)*1, pdict_m4m5[ibuf[i+num_bits*2].name]['O'][0][1]+6]), 
                pdict_m4m5[ibuf[i+num_bits*2].name]['O'][0][1]-3+i, rg_m3m4, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
            laygen.boundary_pin_from_rect(rzp0, rg_m4m5, 'ZP<'+str(i)+'>', laygen.layers['pin'][5], size=6, direction='top')
            laygen.boundary_pin_from_rect(rzmid0, rg_m4m5, 'ZMID<'+str(i)+'>', laygen.layers['pin'][5], size=6, direction='top')
            laygen.boundary_pin_from_rect(rzm0, rg_m4m5, 'ZM<'+str(i)+'>', laygen.layers['pin'][5], size=6, direction='top')

    # power pin
    pwr_dim=laygen.get_template_size(name=itapl[-1].cellname, gridname=rg_m2m3, libname=itapl[-1].libname)
    rvdd = []
    rvss = []
    if num_row%2==0: rp1='VSS'
    else: rp1='VDD'
    for i in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin('VSS'+str(2*i-2), laygen.layers['pin'][3], gridname=rg_m2m3, netname='VSS', refobj=rvss[-1])
        laygen.pin('VDD'+str(2*i-2), laygen.layers['pin'][3], gridname=rg_m2m3, netname='VDD', refobj=rvdd[-1])
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2+1, 0]), xy1=np.array([2*i+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin('VSS'+str(2*i-1), laygen.layers['pin'][3], gridname=rg_m2m3, netname='VSS', refobj=rvss[-1])
        laygen.pin('VDD'+str(2*i-1), laygen.layers['pin'][3], gridname=rg_m2m3, netname='VDD', refobj=rvdd[-1])
    for i in range(num_row+3+1):
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
    for i in range(num_bits+3+5-1):
        for j in range(0, int(pwr_dim[0]/2)):
            rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                         refinstname0=itapbbl[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                         refinstname1=itapbbl[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
            rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                         refinstname0=itapbbl[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                         refinstname1=itapbbl[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))
            rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2+1, 0]), xy1=np.array([2*j+2+1, 0]), gridname0=rg_m2m3,
                         refinstname0=itapbbr[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                         refinstname1=itapbbr[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
            rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2, 0]), xy1=np.array([2*j+2, 0]), gridname0=rg_m2m3,
                         refinstname0=itapbbr[i].name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                         refinstname1=itapbbr[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))

    # body biasing tap 
    rvbb_m2 = []
    rvbb_m3 = []
    tap_space = (laygen.templates.get_template('tap_float', libname=logictemplib).xy[1][0]) / (laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0])
    for i in range(num_bits+3+5-1):
        for j in range(2):
            for k in range(m_tapbb):
                rvbb_m2.append(laygen.route(None, laygen.layers['metal'][2], xy0=np.array([int(tap_space/2), 2+1*j]), xy1=np.array([int(tap_space/2), 2+1*j]), gridname0=rg_m1m2,
                         refinstname0=itapbb[i].name, refpinname0='VSS', refinstindex0=np.array([k, 0]), via0=[[0, 0]],
                         refinstname1=itapbbr[i].name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))
                for l in range(int(tap_space)-2):
                    rvbb_m3.append(laygen.route(None, laygen.layers['metal'][3], 
                         xy0=np.array([int(tap_space/2)+l, 1*j]), xy1=np.array([int(tap_space/2)+l, 2+1*j]), gridname0=rg_m2m3,
                         refinstname0=itapbb[i].name, refpinname0='VSS', refinstindex0=np.array([k, 0]),
                         refinstname1=itapbb[i].name, refpinname1='VSS', refinstindex1=np.array([k, 0]), via1=[[0, 0]]))
    for k in range(m_tapbb):
        for l in range(int(tap_space)-2):
            rvbb_m3_v=laygen.route(None, laygen.layers['metal'][3], 
                         xy0=np.array([int(tap_space/2)+l, 6]), xy1=np.array([int(tap_space/2)+l, 6]), gridname0=rg_m2m3,
                         refinstname0=itapbb[0].name, refpinname0='VSS', refinstindex0=np.array([k, 0]),
                         refinstname1=itapbb[num_bits+3+5-2].name, refpinname1='VSS', refinstindex1=np.array([k, 0]))
            laygen.pin_from_rect('VBB_'+str(k)+'_'+str(l), laygen.layers['pin'][3], rvbb_m3_v, gridname=rg_m2m3, netname='VBB')
    # connecting left tap
    for j in range(1):
        for k in range(3):
            rvbb_m2_h1=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([int(tap_space/2), 2+1*j]), xy1=np.array([int(tap_space/2), 2+1*j]), gridname0=rg_m1m2,
                         refinstname0=itapbb[k].name, refpinname0='VSS', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                         refinstname1=itapbbl[k].name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]])
        for k in range(4):
            rvbb_m2_h1=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([int(tap_space/2), 2+1*j]), xy1=np.array([int(tap_space/2), 2+1*j]), gridname0=rg_m1m2,
                         refinstname0=itapbb[k+num_bits+3].name, refpinname0='VSS', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                         refinstname1=itapbbl[k+num_bits+3].name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]])
        for i in range(1,num_bits+3+5-1):
            rvbb_m3_v_left=laygen.route(None, laygen.layers['metal'][1], xy0=np.array([laygen.get_template_size('tap_float', rg_m1m2, logictemplib)[0], 2+1*j]), 
                        xy1=np.array([laygen.get_template_size('tap_float', rg_m1m2, logictemplib)[0], 2+1*j]), gridname0=rg_m1m2,
                        refinstname0=itapbbl[i].name, refpinname0='VSS', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                        refinstname1=itapbbl[i-1].name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]])
        
    for i in range(num_bits):
        rvbb_m2_left=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([int(tap_space/2), 2]), 
                        xy1=np.array([laygen.get_template_size('tap_float', gridname=rg_m1m2, libname=logictemplib)[0], 2]), gridname0=rg_m1m2,
                        refinstname0=itapbbl[i+3].name, refpinname0='VSS', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                        refinstname1=itapbbl[i+3].name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=None)

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

    num_bits=9
    xorname='sarlogic_xor'
    pgname='pulse_gen'
    cellname_v2='sarlogic_wret_v2_array_bb_pe'
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
        m=sizedict['sarlogic']['m']
        m_dl=sizedict['sarlogic']['m_dl']
        m_xor=sizedict['sarlogic']['m_xor']
        m_buf=sizedict['sarlogic']['m_buf']
        num_inv_bb=sizedict['sarlogic']['num_inv_bb']
        num_inv_dl=sizedict['sarlogic']['num_inv_dl']
        m_space_left_4x=sizedict['sarabe_m_space_left_4x']

    cellname=xorname
    print(cellname+" generating")
    mycell_list = []
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarlogic_xor(laygen, objectname_pfix='PG0',  
                            placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m1m2_pin=rg_m1m2_pin, routing_grid_m2m3_pin=rg_m2m3_pin,
                            m_xor=4, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    cellname=pgname
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarlogic_pulse_generator(laygen, objectname_pfix='PG0', templib_logic=logictemplib, 
                            placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                            m_dl=m_dl, m_xor=m_xor, num_inv_dl=num_inv_dl, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    cellname=cellname_v2
    print(cellname+" generating")
    mycell_list.append(cellname)
    # generation (2 step)
    # 1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarlogic_wret_v2_array_bb_pe(laygen, objectname_pfix='CA0', templib_logic=logictemplib, 
                            placement_grid=pg, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                            routing_grid_m4m5=rg_m4m5, num_bits=num_bits, m_buf=m_buf, num_bits_row=2, 
                            m_space_left_4x=m_space_left_4x, m_space_4x=0, m_space_2x=0,
                            m_tapbb=0, m_spacebb_1x=0, m_spacebb_2x=0, num_inv_bb=2,
                            m_space_1x=0, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    # 2. calculate spacing param and regenerate
    #x0 = laygen.templates.get_template('sarafe_nsw_doubleSA', libname=workinglib).xy[1][0] \
    #     - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
    #     - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    x0 = laygen.templates.get_template('sarafe_nsw_doubleSA', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('sarlogic_wret_v2', libname=workinglib).xy[1][0] * 2\
         - laygen.templates.get_template('tap_float', libname=logictemplib).xy[1][0] * 2 \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    x1 = laygen.templates.get_template('sarafe_nsw_doubleSA', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('pulse_gen', libname=workinglib).xy[1][0] * 3\
         - laygen.templates.get_template('tap_float', libname=logictemplib).xy[1][0] * 2 \
         - laygen.templates.get_template('space_4x', libname=logictemplib).xy[1][0] * 6 \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_space_4x = int(m_space / 4)
    m_space_2x = int((m_space - m_space_4x * 4) / 2)
    m_space_1x = int(m_space - m_space_4x * 4 - m_space_2x * 2)
    # tap and space for body biasing
    buf_name = 'inv_' + str(m_buf) + 'x'
    m_spacebb = int(round(x1 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    tap_space = (laygen.templates.get_template('tap_float', libname=logictemplib).xy[1][0]) / (laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0])
    m_tapbb = int(m_spacebb / tap_space)
    m_spacebb_2x = int((m_spacebb - m_tapbb * tap_space) / 2)
    m_spacebb_1x = int(m_spacebb - m_tapbb * tap_space - m_spacebb_2x * 2)
    #print(m_spacebb, tap_space, m_tapbb, m_spacebb_2x, m_spacebb_1x)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarlogic_wret_v2_array_bb_pe(laygen, objectname_pfix='CA0', templib_logic=logictemplib,
                            placement_grid=pg, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                            routing_grid_m4m5=rg_m4m5, num_bits=num_bits, m_buf=m_buf, num_bits_row=2, 
                            m_space_left_4x=m_space_left_4x, m_space_4x=m_space_4x,
                            m_tapbb=m_tapbb, m_spacebb_1x=m_spacebb_1x, m_spacebb_2x=m_spacebb_2x, num_inv_bb=num_inv_bb,
                            m_space_2x=m_space_2x, m_space_1x=m_space_1x, origin=np.array([0, 0]))
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

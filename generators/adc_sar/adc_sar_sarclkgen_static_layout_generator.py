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
import yaml
import os
#import logging;logging.basicConfig(level=logging.DEBUG)

def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin"""
    rvdd0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VSS', gridname, sort=True)

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=gridname)

def generate_sarclkgen_static(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4,
        m=2, fo=2, m_space_left_4x=0, m_space_4x=0, m_space_2x=0, m_space_1x=0, fast=True, origin=np.array([0, 0]),
                              mux_fast=False):
    """generate a static sar clock generator """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    tap_name = 'tap'
    inv_name = 'inv_' + str(m) + 'x'
    invd_name = 'inv_1x'
    iobuf_name = 'inv_' + str(fo*m) + 'x'
    iobuf2_name = 'inv_' + str(fo*m*2) + 'x'
    nand_name = 'nand_' + str(2*m) + 'x'
    nand2_name = 'nand_' + str(fo*m) + 'x'
    nor_name = 'nor_' + str(m) + 'x'
    sr_name = 'ndsr_2x'
    mux_name = 'mux2to1_' +  str(2*m) + 'x'  # static signal, doesn't need fast?
    core_name = 'sarclkgen_core_static2'
    #core2_name = 'sarclkgen_core2'
    delay_name = 'sarclkdelay_compact_dual'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'
    space_4x_name = 'space_4x'

    # placement
    itapl = laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                         gridname = pg, xy=origin, template_libname = templib_logic)
    refi=itapl.name
    if not m_space_left_4x==0:
        ispl4x=laygen.relplace(name="I" + objectname_pfix + 'SPL4X0', templatename=space_4x_name,
                               shape = np.array([m_space_left_4x, 1]), gridname=pg,
                               refinstname=refi, template_libname=templib_logic)
        refi = ispl4x.name
    iinv7 = laygen.relplace(name="I" + objectname_pfix + 'INV7', templatename=invd_name,
                            gridname=pg, refinstname=refi, template_libname=templib_logic)
    inand0 = laygen.relplace(name="I" + objectname_pfix + 'ND0', templatename=nand_name,
                             gridname=pg, refinstname=iinv7.name, template_libname=templib_logic)
    #icore2 = laygen.relplace(name="I" + objectname_pfix + 'CORE2', templatename=core2_name,
    #                         gridname=pg, refinstname=iinv7.name, template_libname=workinglib)
    #inand0=icore2
    idly0 = laygen.relplace(name="I" + objectname_pfix + 'DLY0', templatename=delay_name,
                            gridname=pg, refinstname=inand0.name, template_libname=workinglib)
    iinv5 = laygen.relplace(name="I" + objectname_pfix + 'INV5', templatename=inv_name,
                            gridname=pg, refinstname=idly0.name, template_libname=templib_logic)
    if mux_fast is False:
        icore0 = laygen.relplace(name="I" + objectname_pfix + 'CORE0', templatename=core_name,
                                gridname=pg, refinstname=iinv5.name, template_libname=workinglib)
    else:
        imuxinv = laygen.relplace(name='I'+objectname_pfix+'MUXINV0', templatename=inv_name,
                                  gridname=pg, refinstname=iinv5.name, template_libname=templib_logic)
        imux0 = laygen.relplace(name="I" + objectname_pfix + 'MUX0', templatename=mux_name,
                                gridname=pg, refinstname=imuxinv.name, template_libname=templib_logic)
        icore0 = laygen.relplace(name="I" + objectname_pfix +'CORE0', templatename=core_name,
                                 gridname=pg, refinstname=imux0.name, template_libname=workinglib)
    iinv8 = laygen.relplace(name="I" + objectname_pfix + 'INV8', templatename=iobuf_name,
                            gridname=pg, refinstname=icore0.name, template_libname=templib_logic)
    iinv8b = laygen.relplace(name="I" + objectname_pfix + 'INV8B', templatename=iobuf2_name,
                            gridname=pg, refinstname=iinv8.name, template_libname=templib_logic)
    iinv8c = laygen.relplace(name="I" + objectname_pfix + 'INV8C', templatename=iobuf2_name,
                            gridname=pg, refinstname=iinv8b.name, template_libname=templib_logic)
    iinv0 = laygen.relplace(name="I" + objectname_pfix + 'INV0', templatename=invd_name,
                            gridname=pg, refinstname=iinv8c.name, template_libname=templib_logic)
    iinv1 = laygen.relplace(name="I" + objectname_pfix + 'INV1', templatename=invd_name,
                            gridname=pg, refinstname=iinv0.name, template_libname=templib_logic)
    iinv2 = laygen.relplace(name="I" + objectname_pfix + 'INV2', templatename=invd_name,
                            gridname=pg, refinstname=iinv1.name, template_libname=templib_logic)

    #refl=iinv8c.name
    #reflcn=iinv8c.cellname
    #refl=iinv8.name
    #reflcn=iinv8.cellname
    refl=iinv2.name
    reflcn=iinv2.cellname
    isp4x = []
    isp2x = []
    isp1x = []
    refi=refl
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

    # internal pins
    pdict = laygen.get_inst_pin_xy(None, None, rg_m3m4)
    pdict23 = laygen.get_inst_pin_xy(None, None, rg_m2m3)

    # internal routes
    #x0 = laygen.get_xy(obj =inand0, gridname=rg_m3m4)[0] + 1
    x0 = laygen.get_xy(obj =iinv7, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_xy(obj =laygen.get_inst(name=refl), gridname=rg_m3m4)[0]\
         +laygen.get_xy(obj=laygen.get_template(name=reflcn, libname=templib_logic), gridname=rg_m3m4)[0] - 1
    y0 = pdict[inand0.name]['A'][0][1] + 0
    # internal routes - and2
    [rv0, rphi0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[icore0.name]['PHI0'][0],
                                       pdict[iinv8.name]['I'][0], y0 - 2 + 1, rg_m3m4)

    # internal routes - clkdelay
    [rv0, rdone0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inand0.name]['O'][0],
                                       pdict[idly0.name]['I'][0], y0 + 0+2, rg_m3m4)  

    # internal routes - phi0 logic
    [rv0, rup0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[idly0.name]['O'][0],
                                       pdict[iinv5.name]['I'][0], y0 + 0, rg_m3m4)  # up
    if fast==True and mux_fast==False:
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[icore0.name]['UPB'][0],
                                       pdict[iinv5.name]['O'][0], y0 + 2-1+1, rg_m3m4)  # upb
    elif fast==False:
        [rv0, rh0] = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], pdict23[icore0.name]['UPB'][0],
                                       pdict23[icore0.name]['VDD'][0], rg_m2m3)  # upb
    else:
        laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[imux0.name]['EN0'][0],
                         pdict[imuxinv.name]['O'][0], y0+2-1, rg_m3m4)
        laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[imux0.name]['EN1'][0],
                         pdict[imuxinv.name]['I'][0], y0, rg_m3m4)
        laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[imux0.name]['I0'][0],
                         pdict[iinv5.name]['O'][0], y0+2-1+1, rg_m3m4)
        laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], pdict23[imux0.name]['I1'][0],
                                       pdict23[imux0.name]['VDD'][0], rg_m2m3)  # upb
        laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[icore0.name]['UPB'][0],
                         pdict[imux0.name]['O'][0], y0+2-1+1, rg_m3m4)

    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[icore0.name]['DONE'][0],
                                       pdict[inand0.name]['O'][0], y0 + 0+4, rg_m3m4) #DONE-pre
    # internal routes - outputbuf
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv8.name]['O'][0],
                                       pdict[iinv8b.name]['I'][0], y0 - 1, rg_m3m4) 
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv8b.name]['O'][0],
                                       pdict[iinv8c.name]['I'][0], y0 + 1, rg_m3m4) 

    # input routes
    rv0, rsaop0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inand0.name]['A'][0],
                                  np.array([x0, y0 + 2+1]), rg_m3m4)
    rv0, rsaom0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inand0.name]['B'][0],
                                   np.array([x0, y0 + 1]), rg_m3m4)
    rv0, rrst0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[icore0.name]['RST'][0],
                                   np.array([x0, y0 - 2+1]), rg_m3m4)
    rv0, rextsel_clk0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv7.name]['I'][0],
                                        np.array([x0, y0 + 5]), rg_m3m4)
    #rv0, rextclk0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv9.name]['I'][0],
    #                                np.array([x0, y0 + 5]), rg_m3m4)

    #sel routes
    rv0, rsel0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv0.name]['O'][0],
                                 pdict[idly0.name]['SEL<0>'][0], rg_m3m4)
    rv0, rsel1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv1.name]['O'][0],
                                 pdict[idly0.name]['SEL<1>'][0], rg_m3m4)
    rv0, rsel2 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv2.name]['O'][0],
                                 pdict[idly0.name]['SEL<2>'][0], rg_m3m4)
    rv0, rsel0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv0.name]['I'][0],
                                 np.array([x1, y0+5]), rg_m3m4)
    rv0, rsel1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv1.name]['I'][0],
                                 np.array([x1, y0+4]), rg_m3m4)
    rv0, rsel2 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv2.name]['I'][0],
                                 np.array([x1, y0+3]), rg_m3m4)
    #rsel0 = laygen.route(None, laygen.layers['metal'][4], xy0=pdict[idly0.name]['SEL<0>'][0], xy1=np.array([x1, pdict[idly0.name]['SEL<0>'][0][1]]), gridname0=rg_m3m4)
    #rsel1 = laygen.route(None, laygen.layers['metal'][4], xy0=pdict[idly0.name]['SEL<1>'][0], xy1=np.array([x1, pdict[idly0.name]['SEL<1>'][0][1]]), gridname0=rg_m3m4)
    #Short/en
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv7.name]['O'][0],
                                       pdict[idly0.name]['ENB'][0], y0 - 7, rg_m3m4)  # upb
    #rv0, rshort0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[idly0.name]['SHORTB'][0],
    #                             np.array([x0, y0+8]), rg_m3m4)
    rv0, rshort0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[idly0.name]['SHORTB'][0],
                                 np.array([pdict[idly0.name]['SHORTB'][0][0]+6, y0-9]), rg_m3m4)

    if mux_fast is True:
        _, rmodesel0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[imuxinv.name]['I'][0],
                                      np.array([pdict[imuxinv.name]['I'][0][0]+6, y0-8]), rg_m3m4)

    #output routes
    #[rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[icore2.name]['CLKB'][0],
    #                                   pdict[iinv8c.name]['O'][0], y0 + 8-13, rg_m3m4)  
    v0, rclkob0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv8c.name]['O'][0],
                                  np.array([x1, y0 + 8-13]), rg_m3m4)
    v0, rclko0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv8b.name]['O'][0],
                                  np.array([x1, y0 + 1]), rg_m3m4)

    # pins
    laygen.boundary_pin_from_rect(rsaop0, rg_m3m4, "SAOP", laygen.layers['pin'][4], size=6, direction='left')
    laygen.boundary_pin_from_rect(rsaom0, rg_m3m4, "SAOM", laygen.layers['pin'][4], size=6, direction='left')
    laygen.boundary_pin_from_rect(rphi0, rg_m3m4, "PHI0", laygen.layers['pin'][4], size=6, direction='left')
    laygen.boundary_pin_from_rect(rrst0, rg_m3m4, "RST", laygen.layers['pin'][4], size=6, direction='left')
    laygen.boundary_pin_from_rect(rup0, rg_m3m4, "UP", laygen.layers['pin'][4], size=4, direction='right')
    laygen.boundary_pin_from_rect(rextsel_clk0, rg_m3m4, "EXTSEL_CLK", laygen.layers['pin'][4], size=6,
                                  direction='left')
    laygen.boundary_pin_from_rect(rshort0, rg_m3m4, "SHORTB", laygen.layers['pin'][4], size=6, direction='left')
    #laygen.boundary_pin_from_rect(rextclk0, rg_m3m4, "EXTCLK", laygen.layers['pin'][4], size=6, direction='left')
    if mux_fast is True:
        laygen.boundary_pin_from_rect(rmodesel0, rg_m3m4, "MODESEL", laygen.layers['pin'][4], size=6, direction='left')
    laygen.boundary_pin_from_rect(rdone0, rg_m3m4, "DONE", laygen.layers['pin'][4], size=4, direction='right')
    laygen.boundary_pin_from_rect(rclkob0, rg_m3m4, "CLKOB", laygen.layers['pin'][4], size=6, direction='right')
    laygen.boundary_pin_from_rect(rclko0, rg_m3m4, "CLKO", laygen.layers['pin'][4], size=6, direction='right')
    laygen.boundary_pin_from_rect(rsel0, rg_m3m4, "SEL<0>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.boundary_pin_from_rect(rsel1, rg_m3m4, "SEL<1>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.boundary_pin_from_rect(rsel2, rg_m3m4, "SEL<2>", laygen.layers['pin'][4], size=6, direction='right')

    # power route (horizontal)
    #create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=itapl, inst_right=itapr)
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=itapl.name, refpinname0='VDD', refinstname1=itapr.name, refpinname1='VDD')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
                 refinstname0=itapl.name, refpinname0='VSS', refinstname1=itapr.name, refpinname1='VSS')

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

    mycell_list = []
    num_bits=9
    m=2
    fo=2
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
        m=sizedict['sarclkgen']['m']
        fo=sizedict['sarclkgen']['fo']
        ndelay=sizedict['sarclkgen']['ndelay']
        fast=sizedict['sarclkgen']['fast']
        mux_fast=sizedict['sarclkgen']['mux_fast']
        m_space_left_4x=sizedict['sarabe_m_space_left_4x']
    #generation (2 step)
    cellname='sarclkgen_static'
    print(cellname+" generating")
    mycell_list.append(cellname)
    #1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkgen_static(laygen, objectname_pfix='CKG0', templib_logic=logictemplib, placement_grid=pg,
                       routing_grid_m3m4=rg_m3m4,
                       m=m, fo=fo, m_space_left_4x=m_space_left_4x, m_space_4x=0, m_space_2x=0, m_space_1x=0, fast=fast,
                       origin=np.array([0, 0]),mux_fast=mux_fast)
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
    generate_sarclkgen_static(laygen, objectname_pfix='CKG0', templib_logic=logictemplib, placement_grid=pg,
                       routing_grid_m3m4=rg_m3m4,
                       m=m, fo=fo, m_space_left_4x=m_space_left_4x, 
                       m_space_4x=m_space_4x, m_space_2x=m_space_2x, m_space_1x=m_space_1x, fast=fast, origin=np.array([0, 0]),
                       mux_fast=mux_fast)
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

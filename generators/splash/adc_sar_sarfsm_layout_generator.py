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
#import logging;logging.basicConfig(level=logging.DEBUG)

def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin"""
    rvdd0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VSS', gridname, sort=True)

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=gridname)

def generate_sarfsm(laygen, objectname_pfix, templib_logic, placement_grid,
                    routing_grid_m3m4, num_bits=8, num_bits_row=4, m=2,
                    m_space_left_4x=0, m_space_4x=0, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0])):
    """generate one-hot coded sar fsm """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4
    num_row = int(num_bits / num_bits_row)
    if num_bits>num_row*num_bits_row:
        num_row+=1

    tap_name='tap'
    tie_name = 'tie_2x'
    dff_name='dff_rsth_'+str(m)+'x'
    inv_name='inv_'+str(m)+'x'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'
    space_4x_name = 'space_4x'

    # placement
    itapl=[]
    itapr=[]
    isp4x=[] #space cells
    isp2x=[]
    isp1x=[]
    ifill4x=[] #fill cells
    ifill2x=[]
    ifill1x=[]
    itapl.append(laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                              gridname = pg, xy=origin, template_libname = templib_logic))
    refi=itapl[-1].name
    if not m_space_left_4x==0:
        ispl4x=laygen.relplace(name="I" + objectname_pfix + 'SPL4X0', templatename=space_4x_name,
                               shape = np.array([m_space_left_4x, 1]), gridname=pg,
                               refinstname=refi, template_libname=templib_logic)
        refi = ispl4x.name
    itie0 = laygen.relplace(name = "I" + objectname_pfix + 'TIE0', templatename = tie_name,
                            gridname = pg, refinstname = refi, template_libname = templib_logic)
    idff0 = laygen.relplace(name = "I" + objectname_pfix + 'TRGGEN0', templatename = dff_name,
                            gridname = pg, refinstname = itie0.name, template_libname = templib_logic)
    iinv0 = laygen.relplace(name = "I" + objectname_pfix + 'INV0', templatename = inv_name,
                            gridname = pg, refinstname = idff0.name, template_libname = templib_logic)
    refi = iinv0.name
    #fill insertion
    fill_tie_x = laygen.get_template_size(tie_name, pg, libname=templib_logic)[0]
    fill_x = (laygen.get_template_size(dff_name, pg, libname = templib_logic)*np.array([num_bits_row - 1, 1]) \
             - laygen.get_template_size(inv_name, pg, libname = templib_logic))[0]
    m_fill_4x=int(fill_x/4)
    fill_x=fill_x-m_fill_4x*4
    m_fill_2x=int(fill_x/2)
    fill_x=fill_x-m_fill_2x*2
    m_fill_1x=fill_x
    if not m_fill_4x==0:
        ifill4x.append(laygen.relplace(name="I" + objectname_pfix + 'F4X0', templatename=space_4x_name,
                     shape = np.array([m_fill_4x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = ifill4x[-1].name
    if not m_fill_2x==0:
        ifill2x.append(laygen.relplace(name="I" + objectname_pfix + 'F2X0', templatename=space_2x_name,
                     shape = np.array([m_fill_2x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = ifill2x[-1].name
    if not m_fill_1x==0:
        ifill1x.append(laygen.relplace(name="I" + objectname_pfix + 'F1X0', templatename=space_1x_name,
                     shape=np.array([m_fill_1x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = ifill1x[-1].name
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
    itapr.append(laygen.relplace(name="I" + objectname_pfix + 'TAPR0', templatename=tap_name,
                                 gridname=pg, refinstname=refi, template_libname=templib_logic))
    idff=[]
    for i in range(num_row):
        if i%2==0: tf='MX'
        else: tf='R0'
        itapl.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPL'+str(i+1), templatename = tap_name,
                                     gridname = pg, refinstname = itapl[-1].name, transform=tf,
                                     direction = 'top', template_libname=templib_logic))
        refi=itapl[-1].name
        if not m_space_left_4x==0:
            ispl4x=laygen.relplace(name="I" + objectname_pfix + 'SPL4X'+str(i+1), templatename=space_4x_name,
                                   shape = np.array([m_space_left_4x, 1]), gridname=pg, transform=tf,
                                   refinstname=refi, template_libname=templib_logic)
            refi = ispl4x.name
        ifilltie=laygen.relplace(name="I" + objectname_pfix + 'FT'+str(i), templatename=space_1x_name,
                     shape=np.array([fill_tie_x, 1]), gridname=pg, transform=tf,
                     refinstname=refi, template_libname=templib_logic)
        refi = ifilltie.name
        for j in range(num_bits_row):
            if i*num_bits_row+j < num_bits:
                idff.append(laygen.relplace(name = "I" + objectname_pfix + 'FSM'+str(i*num_bits_row+j), templatename = dff_name,
                                           gridname = pg, refinstname = refi, shape=np.array([1, 1]),
                                           transform=tf, template_libname=templib_logic))
                refi = idff[-1].name
            else:
                nfill = laygen.get_template_size(name=idff[0].cellname, gridname=pg, libname=templib_logic)[0]
                #ifill=laygen.relplace(name = "I" + objectname_pfix + 'FSMFILL'+str(i*num_bits_row+j), templatename = space_1x_name,
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
            isp4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP4X'+str(i+1), templatename=space_4x_name,
                         shape = np.array([m_space_4x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp4x[-1].name
        if not m_space_2x==0:
            isp2x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2X'+str(i+1), templatename=space_2x_name,
                         shape = np.array([m_space_2x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp2x[-1].name
        if not m_space_1x==0:
            isp1x.append(laygen.relplace(name="I" + objectname_pfix + 'SP1X'+str(i+1), templatename=space_1x_name,
                         shape=np.array([m_space_1x, 1]), transform=tf, gridname=pg,
                         refinstname=refi, template_libname=templib_logic))
            refi = isp1x[-1].name
        itapr.append(laygen.relplace(name = "I" + objectname_pfix + 'TAPR'+str(i+1), templatename = tap_name,
                               gridname = pg, refinstname = refi, transform=tf, template_libname = templib_logic))

    # internal pins
    pdict = laygen.get_inst_pin_xy(None, None, rg_m3m4)

    # internal route references
    x0 = laygen.get_inst_xy(name=itie0.name, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_inst_xy(name=idff[-1].name, gridname=rg_m3m4)[0]\
         +laygen.get_template_size(name=idff[-1].cellname, gridname=rg_m3m4, libname=templib_logic)[0] - 1
    x2 = laygen.get_inst_xy(name=itapr[-1].name, gridname=rg_m4m5)[0] - 2 -2
    y0 = pdict[idff0.name]['I'][0][1] + 2
    y1 = laygen.get_template_size(name=itie0.cellname, gridname=rg_m3m4, libname=templib_logic)[1]
    y2 = y1*(num_row+1)

    # internal routes
    #tie
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[itie0.name]['TIEVSS'][0], pdict[idff0.name]['I'][0], y0+1, rg_m3m4)
    #clock
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4,
                 refinstname0=idff0.name, refpinname0='CLK', refinstname1=idff[(num_row-1)*num_bits_row].name, refpinname1='CLK')
    for i in range(1, num_bits_row):
        if (num_row-1)*num_bits_row + i < num_bits:
            [rv0, rclk0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                               pdict[idff[(num_row-1)*num_bits_row].name]['CLK'][0],
                                               pdict[idff[(num_row-1)*num_bits_row+i].name]['CLK'][0], 2 * y1 - y0 - 4, rg_m3m4)
        else:
            [rv0, rclk0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                               pdict[idff[(num_row-2)*num_bits_row].name]['CLK'][0],
                                               pdict[idff[(num_row-2)*num_bits_row+i].name]['CLK'][0], 2 * y1 - y0 - 4, rg_m3m4)
    #rst
    laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4,
                 refinstname0=idff0.name, refpinname0='RST', refinstname1=idff[(num_row-1)*num_bits_row].name, refpinname1='RST')
    for i in range(1, num_bits_row):
        if (num_row-1)*num_bits_row + i < num_bits:
            [rv0, rrst0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                               pdict[idff[(num_row-1)*num_bits_row].name]['RST'][0],
                                               pdict[idff[(num_row-1)*num_bits_row+i].name]['RST'][0], 2 * y1 - y0 - 2, rg_m3m4)
        else:
            [rv0, rrst0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                               pdict[idff[(num_row-2)*num_bits_row].name]['RST'][0],
                                               pdict[idff[(num_row-2)*num_bits_row+i].name]['RST'][0], 2 * y1 - y0 - 2, rg_m3m4)
    #codepath
    #trig/trigb
    [rv0, rrst_dly0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[idff0.name]['O'][0],
                                       pdict[iinv0.name]['I'][0], y0-1, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv0.name]['O'][0],
                                       pdict[idff[0].name]['I'][0], y1+0-1, rg_m3m4)
    #sb
    for i in range(num_row):
        for j in range(num_bits_row - 1):
            if i*num_bits_row+j < num_bits:
                if i%2==0:
                    y=y1+y1*i+y1-y0-1
                else:
                    y=y1+y1*i+y0+1
                if i*num_bits_row+j+1 < num_bits:
                    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[idff[i*num_bits_row+j].name]['O'][0],
                                                       pdict[idff[i*num_bits_row+j+1].name]['I'][0], y, rg_m3m4)
                    xy=laygen.get_rect_xy(rh0.name, rg_m4m5, sort=True)
                    rsb0=laygen.route(None, laygen.layers['metal'][5], xy0=xy[0]+np.array([i, 0]), xy1=np.array([xy[0][0]+i, y2]),
                                      gridname0=rg_m4m5, via0=[[0, 0]])
                    laygen.boundary_pin_from_rect(rsb0, rg_m4m5, "SB<" + str(num_bits - i * num_bits_row - j - 1) + ">",
                                                         laygen.layers['pin'][5], size=6, direction='top')
    #sb (route to next row)
    for i in range(num_row-1):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[idff[(i+1)*num_bits_row-1].name]['O'][0],
                                           pdict[idff[(i+1)*num_bits_row].name]['I'][0], y1*(i+2)-1, rg_m3m4)
        xy=laygen.get_rect_xy(rh0.name, rg_m4m5, sort=True)
        rsb0=laygen.route(None, laygen.layers['metal'][5], xy0=xy[0]+np.array([i, 0]), xy1=np.array([xy[0][0]+i, y2]),
                          gridname0=rg_m4m5, via0=[[0, 0]])
        laygen.boundary_pin_from_rect(rsb0, rg_m4m5, "SB<" + str(num_bits - (i + 1) * num_bits_row) + ">",
                                             laygen.layers['pin'][5], size=6, direction='top')
    #sb (lsb)
    rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[idff[num_bits-1].name]['O'][0],
                                np.array([pdict[idff[num_bits-1].name]['O'][0][0]-6, y]), rg_m3m4)
    xy=laygen.get_rect_xy(rh0.name, rg_m4m5, sort=True)
    rsb0=laygen.route(None, laygen.layers['metal'][5], xy0=xy[0]+np.array([0, 0]), xy1=np.array([xy[0][0]+0, y2]),
                      gridname0=rg_m4m5, via0=[[0, 0]])
    laygen.boundary_pin_from_rect(rsb0, rg_m4m5, "SB<0>", laygen.layers['pin'][5], size=6, direction='top')
    # pins
    #xy=laygen.get_rect_xy(rrst0.name, rg_m4m5, sort=True)
    #rv0, rrst0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], xy[0],
    #                             np.array([xy[0][0]+6, 2]), rg_m4m5)
    #laygen.boundary_pin_from_rect(rrst0, rg_m4m5, 'RST',
    #                                     laygen.layers['pin'][5], size=6, direction='bottom')
    laygen.boundary_pin_from_rect(rrst0, rg_m4m5, 'RST',
                                         laygen.layers['pin'][4], size=6, direction='left')
    laygen.boundary_pin_from_rect(rclk0, rg_m4m5, 'CLK',
                                         laygen.layers['pin'][4], size=6, direction='right')
    laygen.boundary_pin_from_rect(rrst_dly0, rg_m4m5, 'RST_DLY',
                                         laygen.layers['pin'][4], size=6, direction='right')

    # power pin
    pwr_dim=laygen.get_template_size(name=itapl[-1].cellname, gridname=rg_m2m3, libname=itapl[-1].libname)
    rvdd = []
    rvss = []
    if num_row%2==0: rp1='VDD'
    else: rp1='VSS'
    for i in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i-2), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i-2), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2+1, 0]), xy1=np.array([2*i+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr[0].name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr[-1].name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i-1), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i-1), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
    for i in range(num_row+1):
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
    # generation (2 step)
    cellname='sarfsm'
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
        m=sizedict['sarfsm']['m']
        m_space_left_4x=sizedict['sarabe_m_space_left_4x']
    #yamlfile_system_input="adc_sar_dsn_system_input.yaml"
    #if load_from_file==True:
    #    with open(yamlfile_system_input, 'r') as stream:
    #        sysdict_i = yaml.load(stream)
    #    cellname='sarfsm_'+str(sysdict_i['n_bit'])+'b'
    #    m=sysdict_i['m_sarfsm']
    #    num_bits=sysdict_i['n_bit']

    print(cellname+" generating")
    mycell_list.append(cellname)
    # 1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    #num_bits_row=3
    x0 = laygen.templates.get_template('sarafe_nsw', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('tap', libname=logictemplib).xy[1][0] * 2 \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    dff_name='dff_rsth_'+str(m)+'x'
    x1 = laygen.templates.get_template(dff_name, libname=logictemplib).xy[1][0] 
    num_bits_row=int(np.floor(x0/x1))
    generate_sarfsm(laygen, objectname_pfix='FSM0', templib_logic=logictemplib, placement_grid=pg,
                    routing_grid_m3m4=rg_m3m4, num_bits=num_bits, num_bits_row=num_bits_row, m=m, 
                    m_space_left_4x=m_space_left_4x, m_space_4x=0, m_space_2x=0, m_space_1x=0,
                    origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    # 2. calculate spacing param and regenerate
    x0 = laygen.templates.get_template('sarafe_nsw', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_space_4x = int(m_space / 4)
    m_space_2x = int((m_space - m_space_4x * 4) / 2)
    m_space_1x = int(m_space - m_space_4x * 4 - m_space_2x * 2)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarfsm(laygen, objectname_pfix='FSM0', templib_logic=logictemplib, placement_grid=pg,
                    routing_grid_m3m4=rg_m3m4, num_bits=num_bits, num_bits_row=num_bits_row, m=m, 
                    m_space_left_4x=m_space_left_4x, m_space_4x=m_space_4x, m_space_2x=m_space_2x,
                    m_space_1x=m_space_1x, origin=np.array([0, 0]))
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

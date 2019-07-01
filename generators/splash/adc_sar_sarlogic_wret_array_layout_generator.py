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

def generate_sarlogic_wret_array(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m2m3,
                            routing_grid_m3m4, routing_grid_m4m5, num_bits=8, num_bits_row=4, 
                            m_space_left_4x=0, m_space_4x=0,
                            m_space_2x=0, m_space_1x=0, origin=np.array([0, 0])):
    """generate cap driver array """
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    num_row=int(num_bits/num_bits_row)
    if num_bits>num_row*num_bits_row:
        num_row+=1

    tap_name='tap'
    slogic_name='sarlogic_wret'
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

                rv0, rzp0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5[islogic[i*num_bits_row+j].name]['ZP'][0],
                                            np.array([pdict_m4m5[islogic[i*num_bits_row+j].name]['ZP'][0][0]-2+1+i-11+(1+num_row)*2-3, y2]), rg_m4m5)
                rv0, rzm0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5[islogic[i*num_bits_row+j].name]['ZM'][0],
                                            np.array([pdict_m4m5[islogic[i*num_bits_row+j].name]['ZM'][0][0]-2+1+i-11+(1+num_row)*1-3, y2]), rg_m4m5)
                rv0, rzmid0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5[islogic[i*num_bits_row+j].name]['ZMID'][0],
                                             np.array([pdict_m4m5[islogic[i*num_bits_row+j].name]['ZMID'][0][0]-2+1+i-11+(1+num_row)*0-3, y2]), rg_m4m5)

                rv0, rreto0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5[islogic[i*num_bits_row+j].name]['RETO'][0],
                                            np.array([pdict_m4m5[islogic[i*num_bits_row+j].name]['RETO'][0][0]+1+i+0, 0]), rg_m4m5)
                laygen.boundary_pin_from_rect(rsb0, rg_m4m5, 'SB<'+str(i*num_bits_row+j)+'>', laygen.layers['pin'][5], size=6, direction='bottom')
                laygen.boundary_pin_from_rect(rzp0, rg_m4m5, 'ZP<'+str(i*num_bits_row+j)+'>', laygen.layers['pin'][5], size=6, direction='top')
                laygen.boundary_pin_from_rect(rzmid0, rg_m4m5, 'ZMID<'+str(i*num_bits_row+j)+'>', laygen.layers['pin'][5], size=6, direction='top')
                laygen.boundary_pin_from_rect(rzm0, rg_m4m5, 'ZM<'+str(i*num_bits_row+j)+'>', laygen.layers['pin'][5], size=6, direction='top')
                laygen.boundary_pin_from_rect(rreto0, rg_m4m5, 'RETO<'+str(i*num_bits_row+j)+'>', laygen.layers['pin'][5], size=6, direction='bottom')

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
    for i in range(num_row):
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

def generate_sarlogic_wret_v2_array(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m2m3,
                            routing_grid_m3m4, routing_grid_m4m5, num_bits=8, num_bits_row=4, 
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

                rv0, rzp0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5[islogic[i*num_bits_row+j].name]['ZP'][0],
                                            np.array([pdict_m4m5[islogic[i*num_bits_row+j].name]['ZP'][0][0]-2+1+(num_row-i-1)-11+(1+num_row)*2-3-2-2+10, y2-6]), rg_m4m5)
                rv0, rzm0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5[islogic[i*num_bits_row+j].name]['ZM'][0],
                                            np.array([pdict_m4m5[islogic[i*num_bits_row+j].name]['ZM'][0][0]-2+1+(num_row-i-1)-11+(1+num_row)*1-3-2-2+10, y2-6]), rg_m4m5)
                rv0, rzmid0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5[islogic[i*num_bits_row+j].name]['ZMID'][0],
                                             np.array([pdict_m4m5[islogic[i*num_bits_row+j].name]['ZMID'][0][0]-2+1+(num_row-i-1)-11+(1+num_row)*0-3-2-2+10, y2-6]), rg_m4m5)

                rv0, rreto0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5[islogic[i*num_bits_row+j].name]['RETO'][0],
                                            np.array([pdict_m4m5[islogic[i*num_bits_row+j].name]['RETO'][0][0]+1+i+2, 0]), rg_m4m5)
                laygen.boundary_pin_from_rect(rsb0, rg_m4m5, 'SB<'+str(i*num_bits_row+j)+'>', laygen.layers['pin'][5], size=6, direction='bottom')
                laygen.boundary_pin_from_rect(rzp0, rg_m4m5, 'ZP<'+str(i*num_bits_row+j)+'>', laygen.layers['pin'][5], size=6, direction='top')
                laygen.boundary_pin_from_rect(rzmid0, rg_m4m5, 'ZMID<'+str(i*num_bits_row+j)+'>', laygen.layers['pin'][5], size=6, direction='top')
                laygen.boundary_pin_from_rect(rzm0, rg_m4m5, 'ZM<'+str(i*num_bits_row+j)+'>', laygen.layers['pin'][5], size=6, direction='top')
                laygen.boundary_pin_from_rect(rreto0, rg_m4m5, 'RETO<'+str(i*num_bits_row+j)+'>', laygen.layers['pin'][5], size=6, direction='bottom')

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
    for i in range(num_row):
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

    num_bits=9
    cellname_v2='sarlogic_wret_v2_array'
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
        m_space_left_4x=sizedict['sarabe_m_space_left_4x']

    cellname=cellname_v2
    print(cellname+" generating")
    mycell_list = []
    mycell_list.append(cellname)
    # generation (2 step)
    # 1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarlogic_wret_v2_array(laygen, objectname_pfix='CA0', templib_logic=logictemplib, 
                            placement_grid=pg, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                            routing_grid_m4m5=rg_m4m5, num_bits=num_bits, num_bits_row=2, 
                            m_space_left_4x=m_space_left_4x, m_space_4x=0, m_space_2x=0,
                            m_space_1x=0, origin=np.array([0, 0]))
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
    generate_sarlogic_wret_v2_array(laygen, objectname_pfix='CA0', templib_logic=logictemplib,
                            placement_grid=pg, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                            routing_grid_m4m5=rg_m4m5, num_bits=num_bits, num_bits_row=2, 
                            m_space_left_4x=m_space_left_4x, m_space_4x=m_space_4x,
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

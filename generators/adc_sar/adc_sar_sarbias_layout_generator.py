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
from math import log
import yaml
import os
import laygo.GridLayoutGeneratorHelper as laygenhelper #utility functions
#import logging;logging.basicConfig(level=logging.DEBUG)

def generate_cap(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4,
                 cap_1x_name='space_1x', cap_2x_name='dcap_2x', cap_4x_name='dcap_4x',
                 m_cap_4x=0, m_cap_2x=0, m_cap_1x=0, origin=np.array([0, 0])):
    """generate cap row """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4
    rg_m3m4_thick = rg_m3m4_basic_thick
    tap_name = 'tap'

    # placement
    itapl = laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                         gridname = pg, xy=origin, template_libname = templib_logic)
    isp4x = []
    isp2x = []
    isp1x = []
    refi=itapl.name
    if not m_cap_4x==0:
        isp4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP4X0', templatename=cap_4x_name,
                     shape = np.array([m_cap_4x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp4x[-1].name
    if not m_cap_2x==0:
        isp2x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2X0', templatename=cap_2x_name,
                     shape = np.array([m_cap_2x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp2x[-1].name
    if not m_cap_1x==0:
        isp1x.append(laygen.relplace(name="I" + objectname_pfix + 'SP1X0', templatename=cap_1x_name,
                     shape=np.array([m_cap_1x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp1x[-1].name
    itapr=laygen.relplace(name = "I" + objectname_pfix + 'TAPR0', templatename = tap_name,
                          gridname = pg, refinstname = refi, template_libname = templib_logic)
    # bias pin if needed
    if 'I' in laygen.templates.get_template(cap_4x_name, templib_logic).pins:
        ri=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4_thick,
                        refinstname0=isp4x[0].name, refpinname0='I', refinstindex0=np.array([0, 0]),
                        refinstname1=isp4x[0].name, refpinname1='I', refinstindex1=np.array([m_cap_4x-1, 0]))
        for i in range(m_cap_4x):
            laygen.via(None, np.array([0, 0]), refinstname=isp4x[0].name, refpinname='I', refinstindex=np.array([i, 0]),
                       gridname=rg_m3m4_thick)
        laygen.pin_from_rect('I', laygen.layers['pin'][4], ri, gridname=rg_m3m4_thick)

    # power pin
    pwr_dim=laygen.get_template_size(name=itapl.cellname, gridname=rg_m2m3, libname=itapl.libname)
    rvdd = []
    rvss = []
    rp1='VDD'
    rvdd_m4=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([pwr_dim[0], 0]), gridname0=rg_m3m4_thick,
                         refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                         refinstname1=itapr.name, refpinname1='VDD', refinstindex1=np.array([0, 0]))
    rvss_m4=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([pwr_dim[0], 0]), gridname0=rg_m3m4_thick,
                         refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                         refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0]))
    laygen.pin_from_rect('VDD', laygen.layers['pin'][4], rvdd_m4, gridname=rg_m3m4_thick)
    laygen.pin_from_rect('VSS', laygen.layers['pin'][4], rvss_m4, gridname=rg_m3m4_thick)
    for i in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.via(None, np.array([2*i, 0]), refinstname=itapl.name, refpinname='VDD', refinstindex=np.array([0, 0]),
                   gridname=rg_m3m4_thick)
        laygen.via(None, np.array([2*i+1, 0]), refinstname=itapl.name, refpinname='VSS', refinstindex=np.array([0, 0]),
                   gridname=rg_m3m4_thick)
        #laygen.pin_from_rect('VDD'+str(2*i-2), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        #laygen.pin_from_rect('VSS'+str(2*i-2), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2+1, 0]), xy1=np.array([2*i+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.via(None, np.array([2*i+2+1, 0]), refinstname=itapr.name, refpinname='VDD', refinstindex=np.array([0, 0]),
                   gridname=rg_m3m4_thick)
        laygen.via(None, np.array([2*i+2, 0]), refinstname=itapr.name, refpinname='VSS', refinstindex=np.array([0, 0]),
                   gridname=rg_m3m4_thick)
        #laygen.pin_from_rect('VDD'+str(2*i-1), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        #laygen.pin_from_rect('VSS'+str(2*i-1), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
    for j in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[0,0],
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[0,0]))
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2+1, 0]), xy1=np.array([2*j+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[0,0],
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2, 0]), xy1=np.array([2*j+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[0,0]))

def generate_cap_wbnd(laygen, objectname_pfix, workinglib, cap_name, placement_grid, m=1, shape=np.array([1, 1]), origin=np.array([0, 0])):
    cap_origin = origin + laygen.get_template_size('boundary_bottomleft', pg)
    icap=[]
    for i in range(m):
        if i==0:
            icap.append(laygen.place(name="I" + objectname_pfix + 'SP0', templatename=cap_name,
                              gridname=pg, xy=cap_origin, shape=shape, template_libname=workinglib))
        else:
            if i%2==0:
                icap.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(i), templatename=cap_name,
                            gridname=pg, refinstname=icap[-1].name, shape=shape, template_libname=workinglib, direction='top'))
            else:
                icap.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(i), templatename=cap_name,
                            gridname=pg, refinstname=icap[-1].name, shape=shape, template_libname=workinglib, direction='top', transform='MX'))
    xy0=laygen.get_template_size(name=cap_name, gridname=pg, libname=workinglib)*shape
    xsp=xy0[0]
    #ysp=xy0[1]
    m_bnd = int(xsp / laygen.get_template_size('boundary_bottom', gridname=pg)[0])
    devname_left=[]
    devname_right=[]
    transform_left=[]
    transform_right=[]
    for i in range(m):
        if i%2==0:
            devname_left+=['nmos4_fast_left', 'pmos4_fast_left']
            devname_right+=['nmos4_fast_right', 'pmos4_fast_right']
            transform_left+=['R0', 'MX']
            transform_right+=['R0', 'MX']
        else:
            devname_left+=['pmos4_fast_left', 'nmos4_fast_left']
            devname_right+=['pmos4_fast_right', 'nmos4_fast_right']
            transform_left+=['MX', 'R0']
            transform_right+=['MX', 'R0']
    [bnd_bottom, bnd_top, bnd_left, bnd_right] \
        = laygenhelper.generate_boundary(laygen, objectname_pfix='BND0', placement_grid=pg,
                            devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
                            shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
                            shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_left=devname_left,
                            transform_left=transform_left,
                            devname_right=devname_right,
                            transform_right=transform_right,
                            origin=origin)
    pdict_m3m4_thick=laygen.get_inst_pin_xy(None, None, rg_m3m4_thick)
    for i in range(int((m+1)/2)):
        pxyvdd=pdict_m3m4_thick[icap[i*2].name]['VDD']
        pxyvdd[1] = pxyvdd[0]+(pxyvdd[1]-pxyvdd[0])*shape
        pxyvss=pdict_m3m4_thick[icap[i*2].name]['VSS']
        pxyvss[1] = pxyvss[0]+(pxyvss[1]-pxyvss[0])*shape
        laygen.pin('VDD'+str(i), laygen.layers['pin'][4], pdict_m3m4_thick[icap[i*2].name]['VDD'], gridname=rg_m3m4_thick, netname='VDD')
        laygen.pin('VSS'+str(i), laygen.layers['pin'][4], pdict_m3m4_thick[icap[i*2].name]['VSS'], gridname=rg_m3m4_thick, netname='VSS')
    cap_template = laygen.templates.get_template(cap_name, workinglib)
    cap_pins=cap_template.pins
    if 'I' in cap_pins:
        if m==1:
            laygen.pin('I', laygen.layers['pin'][4], pdict_m3m4_thick[icap[i].name]['I'], gridname=rg_m3m4_thick)
        else:
            for i in range(int(m)):
                laygen.pin('I<'+str(i)+'>', laygen.layers['pin'][4], pdict_m3m4_thick[icap[i].name]['I'], gridname=rg_m3m4_thick)

def generate_rdacarray_core(laygen, objectname_pfix, rdac_libname, cap_1x_libname, rdac_name, cap_1x_name,
                            placement_grid,
                            routing_grid_m3m4, 
                            routing_grid_m4m5, 
                            routing_grid_m4m5_thick, 
                            routing_grid_m4m5_basic_thick, 
                            routing_grid_m5m6_thick, 
                            routing_grid_m5m6_basic_thick, 
                            routing_grid_m6m7_thick, 
                            num_rdac=4, origin=np.array([0, 0])):
    """generate rdac array core """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_thick = routing_grid_m4m5_thick
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_basic_thick = routing_grid_m5m6_basic_thick
    rg_m6m7_thick = routing_grid_m6m7_thick

    left_space=0
    right_space=0
    # placement
    # rdac
    irdac=[]
    irdac.append(laygen.place(name="I" + objectname_pfix + 'RDAC0', templatename=rdac_name,
                         gridname=pg, xy=origin + np.array([left_space, 0]), template_libname=rdac_libname))
    for i in range(1, num_rdac):
        irdac.append(laygen.relplace(name="I" + objectname_pfix + 'RDAC'+str(i), templatename=rdac_name,
                             gridname=pg, refinstname=irdac[-1].name, template_libname=rdac_libname))
    rdac_template = laygen.templates.get_template(rdac_name, rdac_libname)
    rdac_pins=rdac_template.pins
    rdac_xy=irdac[0].xy[0]
    rdac_size = laygen.templates.get_template(rdac_name, libname=rdac_libname).size
    left_space_phy = laygen.get_grid(pg).width*left_space
    right_space_phy = laygen.get_grid(pg).width*right_space
    cap_1x_size = laygen.templates.get_template(cap_1x_name, libname=cap_1x_libname).size #height resolution to make the cell fit to other blocks
    
    #prboundary
    prbnd_x=num_rdac*rdac_size[0]+left_space_phy+right_space_phy
    #prbnd_y=(int(rdac_size[1]/cap_1x_size[1])+6)*cap_1x_size[1]
    prbnd_y=(int(rdac_size[1]/cap_1x_size[1])+1)*cap_1x_size[1]
    laygen.add_rect(None, np.array([origin, origin+np.array([prbnd_x, prbnd_y])]), laygen.layers['prbnd'])

    #VDD/VSS
    #m6
    vddcnt_m6=0
    vsscnt_m6=0
    rvdd_m6=[]
    rvss_m6=[]
    for pn, p in rdac_pins.items():
        if pn.startswith('VDD'):
            pxy=rdac_xy+rdac_pins[pn]['xy']
            r=laygen.add_rect(None, np.array([pxy[0], [pxy[1][0]+rdac_size[0]*(num_rdac-1), pxy[1][1]]]), laygen.layers['metal'][6])
            rvdd_m6.append(r)
            laygen.add_pin('VDD' + str(vddcnt_m6), 'VDD', r.xy, laygen.layers['pin'][6])
            vddcnt_m6+=1
        if pn.startswith('VSS'):
            pxy=rdac_xy+rdac_pins[pn]['xy']
            r=laygen.add_rect(None, np.array([pxy[0], [pxy[1][0]+rdac_size[0]*(num_rdac-1), pxy[1][1]]]), laygen.layers['metal'][6])
            rvss_m6.append(r)
            laygen.add_pin('VSS' + str(vsscnt_m6), 'VSS', r.xy, laygen.layers['pin'][6])
            vsscnt_m6+=1
    #digital in
    for pn, p in rdac_pins.items():
        if pn.startswith('code'):
            phead=pn.split('<')[0]
            ptail='<'+pn.split('<')[1]
            for i in range(num_rdac):
                pxy=rdac_xy+rdac_pins[pn]['xy']+np.array([rdac_size[0]*i, 0])
                pxy[0][1]=0
                r=laygen.add_rect(None, pxy, laygen.layers['metal'][5])
                laygen.add_pin(phead+str(i)+ptail, phead+str(i)+ptail, pxy, rdac_pins[pn]['layer'])
    #analog out
    rdac_size_m5m6_basic_thick=laygen.get_template_size(name=irdac[0].cellname, gridname=rg_m5m6_basic_thick, libname=irdac[0].libname)
    x0=rdac_size_m5m6_basic_thick[0]*num_rdac-1
    y0=rdac_size_m5m6_basic_thick[1]-1
    for i in range(num_rdac):
        #make virtual grids and route on the grids (assuming drc clearance of each block)
        rg_route='route_M4_M5_temp_sig'
        laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m5m6_basic_thick, gridname_output=rg_route,
                                              instname=[irdac[i].name], inst_pin_prefix=['out'], xy_grid_type='xgrid')
        #laygen.get_grid(rg_route).display()
        pdict_route = laygen.get_inst_pin_xy(None, None, rg_route)
        for j in range(5): #5 muxes
            xy0=pdict_route[irdac[i].name]['out<'+str(j)+'>'][1]
            #rv0, rh0 = laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][6], 
            #                           xy0, np.array([xy0[0]+6, y0+i*5+j]), 
            #                           gridname=rg_route)
            rv0=laygen.route(None, layer=laygen.layers['metal'][5], xy0=xy0, xy1=np.array([xy0[0], y0+i*5+j]), gridname0=rg_route, via1=[0,0])
            rv1=laygen.route(None, layer=laygen.layers['metal'][5], xy0=xy0, xy1=np.array([xy0[0], y0+i*5+j+2]), gridname0=rg_route)
            xy1=laygen.get_rect_xy(rv0.name, gridname=rg_m5m6_basic_thick, sort=True)
            r=laygen.route(None, layer=laygen.layers['metal'][6], xy0=xy1[1], xy1=np.array([x0, xy1[1][1]]), gridname0=rg_m5m6_basic_thick)
            laygen.boundary_pin_from_rect(r, rg_m5m6_basic_thick, 'out'+str(i)+'<'+str(j)+'>', laygen.layers['pin'][6], size=6, direction='right')

def generate_sfarray_wopcm_core(laygen, objectname_pfix, sf_libname, cap_1x_libname, sf_name, cap_1x_name,
                     placement_grid,
                     routing_grid_m3m4, 
                     routing_grid_m4m5, 
                     routing_grid_m4m5_thick, 
                     routing_grid_m4m5_basic_thick, 
                     routing_grid_m5m6_thick, 
                     routing_grid_m5m6_basic_thick, 
                     routing_grid_m6m7_thick, 
                     num_bias=3, left_space=12, right_space=12, bot_space=12, origin=np.array([0, 0])):
    """generate sar array core """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_thick = routing_grid_m4m5_thick
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_basic_thick = routing_grid_m5m6_basic_thick
    rg_m6m7_thick = routing_grid_m6m7_thick

    num_route=6
    num_stack=1

    # placement
    # source follower
    sf_xy=origin + np.array([left_space, bot_space])
    isf = laygen.place(name="I" + objectname_pfix + 'SF0', templatename=sf_name,
                      gridname=pg, xy=sf_xy, shape=np.array([num_bias, num_stack]), template_libname=sf_libname)
    sf_template = laygen.templates.get_template(sf_name, sf_libname)
    sf_pins=sf_template.pins
    sf_xy=isf.xy
    left_space_phy = laygen.get_grid(pg).width*left_space
    right_space_phy = laygen.get_grid(pg).width*right_space
    sf_size = laygen.templates.get_template(sf_name, libname=sf_libname).size
    cap_1x_size = laygen.templates.get_template(cap_1x_name, libname=cap_1x_libname).size #height resolution to make the cell fit to other blocks
    
    #prboundary
    prbnd_x=num_bias*sf_size[0]+left_space_phy+right_space_phy
    prbnd_y=(int((sf_size[1]*num_stack+laygen.get_grid(pg).height*bot_space*2)/cap_1x_size[1])+1)*cap_1x_size[1]
    laygen.add_rect(None, np.array([origin, origin+np.array([prbnd_x, prbnd_y])]), laygen.layers['prbnd'])
    pdict_m4m5_thick=laygen.get_inst_pin_xy(None, None, rg_m4m5_thick)
    pdict_m5m6_thick=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    pdict_m6m7_thick=laygen.get_inst_pin_xy(None, None, rg_m6m7_thick)
    
    #internal routes
    #make virtual grids and route on the grids (assuming drc clearance of each block)
    rg_route='route_M4_M5_basic_thick_temp_sig'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m4m5_basic_thick, gridname_output=rg_route,
                                          instname=isf.name,
                                          inst_pin_prefix=['VBIAS', 'in', 'out', 'VDD', 'VSS'], xy_grid_type='ygrid')
    pdict_route = laygen.get_inst_pin_xy(None, None, rg_route)
    #Equalize routing length
    sf_vbias_xy=sf_xy+sf_pins['VBIAS']['xy']
    sf_out_xy=sf_xy+sf_pins['out']['xy']
    sf_in_xy=sf_xy+sf_pins['in']['xy']
    sf_vdd_xy=sf_xy+sf_pins['VDD']['xy']
    sf_vss_xy=sf_xy+sf_pins['VSS']['xy']
    sf_vss_1_xy=sf_xy+sf_pins['VSS_1']['xy']
    x0=min(sf_vbias_xy[0][0], sf_out_xy[0][0], sf_in_xy[0][0])
    x1=max(sf_vbias_xy[1][0], sf_out_xy[1][0], sf_in_xy[1][0]) #, x0+(num_route+1)*5)
    #routes
    rsf_vdd=[]
    rsf_vss=[]
    rsf_vss_1=[]
    rsf_vbias=[]
    rsf_in=[]
    rsf_out=[]
    rsf_vdd_xy=[]
    rsf_vss_xy=[]
    rsf_vss_1_xy=[]
    rsf_vbias_xy=[]
    rsf_in_xy=[]
    rsf_out_xy=[]
    #VDD/VSS xy
    for i in range(num_bias):
        rsf_vdd.append(laygen.add_rect(None, np.array([[x0, sf_vdd_xy[0][1]], [x1, sf_vdd_xy[1][1]]])+i*np.array([[sf_size[0], 0], [sf_size[0], 0]]), laygen.layers['metal'][4]))
        rsf_vdd_xy.append(laygen.get_rect_xy(rsf_vdd[-1].name, gridname=rg_m4m5_basic_thick, sort=True))
    for i in range(num_bias):
        rsf_vss.append(laygen.add_rect(None, np.array([[x0, sf_vss_xy[0][1]], [x1, sf_vss_xy[1][1]]])+i*np.array([[sf_size[0], 0], [sf_size[0], 0]]), laygen.layers['metal'][4]))
        rsf_vss_xy.append(laygen.get_rect_xy(rsf_vss[-1].name, gridname=rg_m4m5_basic_thick, sort=True))
    for i in range(num_bias):
        rsf_vss_1.append(laygen.add_rect(None, np.array([[x0, sf_vss_1_xy[0][1]], [x1, sf_vss_1_xy[1][1]]])+i*np.array([[sf_size[0], 0], [sf_size[0], 0]]), laygen.layers['metal'][4]))
        rsf_vss_1_xy.append(laygen.get_rect_xy(rsf_vss_1[-1].name, gridname=rg_m4m5_basic_thick, sort=True))
    #MIR_N_xy
    for i in range(num_bias):
        rsf_vbias.append(laygen.add_rect(None, np.array([[x0, sf_vbias_xy[0][1]], [x1, sf_vbias_xy[1][1]]])+i*np.array([[sf_size[0], 0], [sf_size[0], 0]]), laygen.layers['metal'][4]))
        rsf_vbias_xy.append(laygen.get_rect_xy(rsf_vbias[-1].name, gridname=rg_route, sort=True))
    #SF_IN_xy
    for i in range(num_bias):
        rsf_in.append(laygen.add_rect(None, np.array([[x0, sf_in_xy[0][1]], [x1, sf_in_xy[1][1]]])+i*np.array([[sf_size[0], 0], [sf_size[0], 0]]), laygen.layers['metal'][4]))
        rsf_in_xy.append(laygen.get_rect_xy(rsf_in[-1].name, gridname=rg_route, sort=True))
    #SF_OUT_xy
    for i in range(num_bias):
        rsf_out.append(laygen.add_rect(None, np.array([[x0, sf_out_xy[0][1]], [x1, sf_out_xy[1][1]]])+i*np.array([[sf_size[0], 0], [sf_size[0], 0]]), laygen.layers['metal'][4]))
        rsf_out_xy.append(laygen.get_rect_xy(rsf_out[-1].name, gridname=rg_route, sort=True))
    #Vertical routes
    rvdd=[]
    rvss=[]
    rbias=[]
    rin=[]
    rout=[]
    xref=[]
    for i in range(num_bias):
        xref.append(rsf_out_xy[i][0][0])
    for i in range(num_bias):
        for j in range(num_route):
            #VDD
            r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=np.array([xref[i]+2*j+1, rsf_vss_xy[i][0][1]+1]), xy1=np.array([xref[i]+2*j+1, rsf_vss_1_xy[i][1][1]-1]), gridname0=rg_m4m5_basic_thick)
            #vxy=0.5*np.array([r.xy[0][0]+r.xy[1][0], sf_vdd_xy[0][1]+sf_vdd_xy[1][1]])
            #laygen.add_inst(None, utemplib, 'via_M4_M5_3', xy=vxy) #hack- should be updated
            laygen.via(None,np.array([xref[i]+2*j+1, rsf_vdd_xy[i][0][1]]), rg_m4m5_basic_thick)
            rvdd.append(r)
            #VSS
            r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=np.array([xref[i]+2*j+2, rsf_vss_xy[i][0][1]+1]), xy1=np.array([xref[i]+2*j+2, rsf_vss_1_xy[i][1][1]-1]), gridname0=rg_m4m5_basic_thick)
            rvss.append(r)
            vxy=0.5*np.array([r.xy[0][0]+r.xy[1][0], sf_vss_xy[0][1]+sf_vss_xy[1][1]])
            laygen.add_inst(None, utemplib, 'via_M4_M5_3', xy=vxy) #hack- should be updated
            vxy=0.5*np.array([r.xy[0][0]+r.xy[1][0], sf_vss_1_xy[0][1]+sf_vss_1_xy[1][1]])
            laygen.add_inst(None, utemplib, 'via_M4_M5_3', xy=vxy) #hack- should be updated
            #for k in range(rsf_vss_xy[i][0][1]+1, rsf_vss_xy[i][1][1], 2):
            #    laygen.via(None,np.array([xref[i]+2*j+2,  k]), rg_m4m5_basic_thick)
            #for k in range(rsf_vss_1_xy[i][0][1]+1, rsf_vss_1_xy[i][1][1], 2):
            #    laygen.via(None,np.array([xref[i]+2*j+2,  k]), rg_m4m5_basic_thick)
            #VBIAS
            laygen.route(None, layer=laygen.layers['metal'][4], xy0=rsf_vbias_xy[i][0], xy1=rsf_vbias_xy[i][0]+np.array([num_route*5+1,0]), gridname0=rg_route)
            rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], rsf_vbias_xy[i][0], rsf_out_xy[i][0]+np.array([num_route*2+j+1,0]), gridname=rg_route)
            rbias.append(rv0)
            #SF_IN
            laygen.route(None, layer=laygen.layers['metal'][4], xy0=rsf_in_xy[i][0], xy1=rsf_in_xy[i][0]+np.array([num_route*5+1,0]), gridname0=rg_route)
            rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], rsf_in_xy[i][0], rsf_vbias_xy[i][0]+np.array([num_route*3+j+1,0]), gridname=rg_route)
            rin.append(rv0)
            #SF_OUT
            laygen.route(None, layer=laygen.layers['metal'][4], xy0=rsf_out_xy[i][0], xy1=rsf_out_xy[i][0]+np.array([num_route*5+1,0]), gridname0=rg_route)
            rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], rsf_out_xy[i][0], rsf_vbias_xy[i][0]+np.array([num_route*4+j+1,0]), gridname=rg_route)
            rout.append(rv0)
    #pin
    for i, r in enumerate(rvdd):
        laygen.add_pin('VDD' + str(i), 'VDD', r.xy, laygen.layers['pin'][5])
    for i, r in enumerate(rvss):
        laygen.add_pin('VSS' + str(i), 'VSS', r.xy, laygen.layers['pin'][5])
    for i, r in enumerate(rbias):
        laygen.add_pin('ADCBIAS' + str(i), 'ADCBIAS<'+str(int(i/num_route))+'>', r.xy, laygen.layers['pin'][5])
    for i, r in enumerate(rin):
        laygen.add_pin('VIN'+str(int(i%num_route))+'<'+str(int(i/num_route))+'>', 'VIN<'+str(int(i/num_route))+'>', r.xy, laygen.layers['pin'][5])
    for i, r in enumerate(rout):
        laygen.add_pin('VOUT'+str(int(i%num_route))+ '<' + str(int(i/num_route)) + '>', 'VOUT<'+str(int(i/num_route))+'>', r.xy, laygen.layers['pin'][5])
    #VDD & VSS
    #m4
    vddcnt_m4=0
    vsscnt_m4=0
    rvdd_m4=[]
    rvss_m4=[]
    for pn, p in sf_pins.items():
        if pn.startswith('VDD'):
            pxy=sf_xy+sf_pins[pn]['xy']
            pxy_vss=sf_xy+sf_pins['VSS']['xy']
            rvdd_m4.append(laygen.add_rect(None, np.array([np.array([pxy_vss[0][0], pxy[0][1]]), np.array([pxy_vss[1][0]+sf_size[0]*(num_bias-1), pxy[1][1]])]), laygen.layers['metal'][4]))
            vddcnt_m4+=1
        if pn.startswith('VSS'):
            pxy=sf_xy+sf_pins[pn]['xy']
            rvss_m4.append(laygen.add_rect(None, np.array([pxy[0], np.array([pxy[1][0]+sf_size[0]*(num_bias-1), pxy[1][1]])]), laygen.layers['metal'][4]))
            vsscnt_m4+=1

def generate_pcmarray_core(laygen, objectname_pfix, pcm_libname, cap_1x_libname, pcm_name, cap_1x_name,
                     placement_grid,
                     routing_grid_m3m4, 
                     routing_grid_m4m5, 
                     routing_grid_m4m5_thick, 
                     routing_grid_m4m5_basic_thick, 
                     routing_grid_m5m6_thick, 
                     routing_grid_m5m6_basic_thick, 
                     routing_grid_m6m7_thick, 
                     num_bias=3, left_space=12, right_space=12, mir_space=12, origin=np.array([0, 0])):
    """generate sar array core """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_thick = routing_grid_m4m5_thick
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_basic_thick = routing_grid_m5m6_basic_thick
    rg_m6m7_thick = routing_grid_m6m7_thick

    # placement
    # pmos mirror and source follower
    ipcm = laygen.place(name="I" + objectname_pfix + 'PCM0', templatename=pcm_name,
                      gridname=pg, xy=origin + np.array([left_space, mir_space]), shape=np.array([num_bias, 1]), template_libname=pcm_libname)
    pcm_template = laygen.templates.get_template(pcm_name, pcm_libname)
    pcm_pins=pcm_template.pins
    pcm_xy=ipcm.xy[0]
    pcm_size = laygen.templates.get_template(pcm_name, libname=pcm_libname).size
    left_space_phy = laygen.get_grid(pg).width*left_space
    right_space_phy = laygen.get_grid(pg).width*right_space
    cap_1x_size = laygen.templates.get_template(cap_1x_name, libname=cap_1x_libname).size #height resolution to make the cell fit to other blocks
    
    #prboundary
    prbnd_x=num_bias*pcm_size[0]+left_space_phy+right_space_phy
    prbnd_y=(int((pcm_size[1]+laygen.get_grid(pg).height*mir_space*2)/cap_1x_size[1])+1)*cap_1x_size[1]
    laygen.add_rect(None, np.array([origin, origin+np.array([prbnd_x, prbnd_y])]), laygen.layers['prbnd'])
    pdict_m4m5_thick=laygen.get_inst_pin_xy(None, None, rg_m4m5_thick)
    pdict_m5m6_thick=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    pdict_m6m7_thick=laygen.get_inst_pin_xy(None, None, rg_m6m7_thick)
    
    #internal routes
    #make virtual grids and route on the grids (assuming drc clearance of each block)
    rg_route='route_M4_M5_basic_thick_temp_sig'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m4m5_basic_thick, gridname_output=rg_route,
                                          instname=ipcm.name,
                                          inst_pin_prefix=['VBIAS', 'in', 'out', 'VDD', 'VSS'], xy_grid_type='ygrid')
    pdict_route = laygen.get_inst_pin_xy(None, None, rg_route)
    #Equalize routing length
    pcm_vbias_xy=pcm_xy+pcm_pins['VBIAS']['xy']
    pcm_out_xy=pcm_xy+pcm_pins['out']['xy']
    pcm_vdd_xy=pcm_xy+pcm_pins['VDD']['xy']
    pcm_vss_xy=pcm_xy+pcm_pins['VSS']['xy']
    x0=min(pcm_vbias_xy[0][0], pcm_out_xy[0][0], pcm_vss_xy[0][0])
    x1=max(pcm_vbias_xy[1][0], pcm_out_xy[1][0], pcm_vss_xy[1][0])
    #routes
    rpcm_vdd=[]
    rpcm_vss=[]
    rpcm_vbias=laygen.add_rect(None, np.array([[x0, pcm_vbias_xy[0][1]], [x1, pcm_vbias_xy[1][1]]]), laygen.layers['metal'][4])
    rpcm_out=[]
    rpcm_vdd_xy=[]
    rpcm_vss_xy=[]
    rpcm_vbias_xy=laygen.get_rect_xy(rpcm_vbias.name, gridname=rg_route, sort=True)
    rpcm_out_xy=[]
    #VDD/VSS xy
    for i in range(num_bias):
        rpcm_vdd.append(laygen.add_rect(None, np.array([[x0, pcm_vdd_xy[0][1]], [x1, pcm_vdd_xy[1][1]]])+i*np.array([[pcm_size[0], 0], [pcm_size[0], 0]]), laygen.layers['metal'][4]))
        rpcm_vdd_xy.append(laygen.get_rect_xy(rpcm_vdd[-1].name, gridname=rg_m4m5_basic_thick, sort=True))
    for i in range(num_bias):
        rpcm_vss.append(laygen.add_rect(None, np.array([[x0, pcm_vss_xy[0][1]], [x1, pcm_vss_xy[1][1]]])+i*np.array([[pcm_size[0], 0], [pcm_size[0], 0]]), laygen.layers['metal'][4]))
        rpcm_vss_xy.append(laygen.get_rect_xy(rpcm_vss[-1].name, gridname=rg_m4m5_basic_thick, sort=True))
    #MIR_P_xy
    for i in range(num_bias):
        rpcm_out.append(laygen.add_rect(None, np.array([[x0, pcm_out_xy[0][1]], [x1, pcm_out_xy[1][1]]])+i*np.array([[pcm_size[0], 0], [pcm_size[0], 0]]), laygen.layers['metal'][4]))
        rpcm_out_xy.append(laygen.get_rect_xy(rpcm_out[-1].name, gridname=rg_route, sort=True))
    #VBIAS
    for pn, p in pcm_pins.items():
        if pn.startswith('VBIAS'):
            pxy=pcm_xy+pcm_pins[pn]['xy']
            rvbias=laygen.add_rect(None, np.array([pxy[0], np.array([pxy[1][0]+pcm_size[0]*(num_bias-1), pxy[1][1]])]), laygen.layers['metal'][4])
    #Vertical routes
    rvdd=[]
    rvss=[]
    rbias=[]
    rin=[]
    rout=[]
    num_route=6
    xref=[]
    for i in range(num_bias):
        xref.append(rpcm_out_xy[i][0][0])
    for i in range(num_bias):
        for j in range(num_route):
            #VDD
            r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=np.array([xref[i]+2*j+1, rpcm_vss_xy[i][0][1]+1]), xy1=np.array([xref[i]+2*j+1, rpcm_vdd_xy[i][1][1]-1]), gridname0=rg_m4m5_basic_thick)
            for k in range(rpcm_vdd_xy[i][0][1]+1, rpcm_vdd_xy[i][1][1], 2):
                laygen.via(None,np.array([xref[i]+2*j+1,  k]), rg_m4m5_basic_thick)
            rvdd.append(r)
            #VSS
            r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=np.array([xref[i]+2*j+2, rpcm_vss_xy[i][0][1]+1]), xy1=np.array([xref[i]+2*j+2, rpcm_vdd_xy[i][1][1]-1]), gridname0=rg_m4m5_basic_thick)
            rvss.append(r)
            for k in range(rpcm_vss_xy[i][0][1]+1, rpcm_vss_xy[i][1][1], 2):
                laygen.via(None,np.array([xref[i]+2*j+2,  k]), rg_m4m5_basic_thick)
            #MIR
            rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], rpcm_out_xy[i][0], rpcm_out_xy[i][0]+np.array([num_route*2+j+1,+1]), gridname=rg_route)
            rout.append(rv0)
            #VBIAS
            rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], rpcm_vbias_xy[0], rpcm_out_xy[i][0]+np.array([num_route*3+j+1,0]), gridname=rg_route)
            rbias.append(rv0)
    #pin
    for i, r in enumerate(rvdd):
        laygen.add_pin('VDD' + str(i), 'VDD', r.xy, laygen.layers['pin'][5])
    for i, r in enumerate(rvss):
        laygen.add_pin('VSS' + str(i), 'VSS', r.xy, laygen.layers['pin'][5])
    for i, r in enumerate(rbias):
        laygen.add_pin('ADCBIAS' + str(i), 'ADCBIAS', r.xy, laygen.layers['pin'][5])
    for i, r in enumerate(rout):
        laygen.add_pin('VOUT'+str(int(i%num_route))+ '<' + str(int(i/num_route)) + '>', 'VOUT<'+str(int(i/num_route))+'>', r.xy, laygen.layers['pin'][5])
    #VDD & VSS
    #m4
    vddcnt_m4=0
    vsscnt_m4=0
    rvdd_m4=[]
    rvss_m4=[]
    for pn, p in pcm_pins.items():
        if pn.startswith('VDD'):
            pxy=pcm_xy+pcm_pins[pn]['xy']
            #laygen.add_pin('VDD' + str(vddcnt_m4), 'VDD', pxy, pcm_pins[pn]['layer'])
            rvdd_m4.append(laygen.add_rect(None, np.array([pxy[0], np.array([pxy[1][0]+pcm_size[0]*(num_bias-1), pxy[1][1]])]), laygen.layers['metal'][4]))
            vddcnt_m4+=1
        if pn.startswith('VSS'):
            pxy=pcm_xy+pcm_pins[pn]['xy']
            #laygen.add_pin('VSS' + str(vsscnt_m4), 'VSS', pxy, pcm_pins[pn]['layer'])
            rvss_m4.append(laygen.add_rect(None, np.array([pxy[0], np.array([pxy[1][0]+pcm_size[0]*(num_bias-1), pxy[1][1]])]), laygen.layers['metal'][4]))
            vsscnt_m4+=1

def generate_sfarray_core(laygen, objectname_pfix, sf_libname, pcm_libname, cap_1x_libname, sf_name, pcm_name, cap_1x_name,
                     placement_grid,
                     routing_grid_m3m4, 
                     routing_grid_m4m5, 
                     routing_grid_m4m5_thick, 
                     routing_grid_m4m5_basic_thick, 
                     routing_grid_m5m6_thick, 
                     routing_grid_m5m6_basic_thick, 
                     routing_grid_m6m7_thick, 
                     num_bias=3, left_space=12, right_space=12, mir_space=12, origin=np.array([0, 0])):
    """generate sar array core """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_thick = routing_grid_m4m5_thick
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_basic_thick = routing_grid_m5m6_basic_thick
    rg_m6m7_thick = routing_grid_m6m7_thick

    # placement
    # pmos mirror and source follower
    ipcm = laygen.place(name="I" + objectname_pfix + 'PCM0', templatename=pcm_name,
                      gridname=pg, xy=origin + np.array([left_space, mir_space]), shape=np.array([num_bias, 1]), template_libname=pcm_libname)
    sf_xy = origin + (laygen.get_template_size(pcm_name, gridname=pg, libname=pcm_libname)*np.array([0,1]) ) + np.array([left_space, 2*mir_space])
    isf = laygen.place(name="I" + objectname_pfix + 'SF0', templatename=sf_name,
                      gridname=pg, xy=sf_xy, shape=np.array([num_bias, 1]), template_libname=sf_libname)
    #isf = laygen.relplace(name="I" + objectname_pfix + 'SF0', templatename=sf_name,
    #                  gridname=pg, refinstname=ipcm.name, direction='top', shape=np.array([num_bias, 1]), template_libname=sf_libname)
    pcm_template = laygen.templates.get_template(pcm_name, pcm_libname)
    pcm_pins=pcm_template.pins
    pcm_xy=ipcm.xy[0]
    sf_template = laygen.templates.get_template(sf_name, sf_libname)
    sf_pins=sf_template.pins
    sf_xy=isf.xy[0]
    pcm_size = laygen.templates.get_template(pcm_name, libname=pcm_libname).size
    left_space_phy = laygen.get_grid(pg).width*left_space
    right_space_phy = laygen.get_grid(pg).width*right_space
    sf_size = laygen.templates.get_template(sf_name, libname=sf_libname).size
    cap_1x_size = laygen.templates.get_template(cap_1x_name, libname=cap_1x_libname).size #height resolution to make the cell fit to other blocks
    
    #prboundary
    prbnd_x=num_bias*max((pcm_size[0], sf_size[0]))+left_space_phy+right_space_phy
    prbnd_y=(int((pcm_size[1]+sf_size[1]+laygen.get_grid(pg).height*mir_space*2)/cap_1x_size[1])+1)*cap_1x_size[1]
    laygen.add_rect(None, np.array([origin, origin+np.array([prbnd_x, prbnd_y])]), laygen.layers['prbnd'])
    pdict_m4m5_thick=laygen.get_inst_pin_xy(None, None, rg_m4m5_thick)
    pdict_m5m6_thick=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    pdict_m6m7_thick=laygen.get_inst_pin_xy(None, None, rg_m6m7_thick)
    
    #internal routes
    #make virtual grids and route on the grids (assuming drc clearance of each block)
    rg_route='route_M4_M5_basic_thick_temp_sig'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m4m5_basic_thick, gridname_output=rg_route,
                                          instname=[ipcm.name, isf.name],
                                          inst_pin_prefix=['VBIAS', 'in', 'out', 'VDD', 'VSS'], xy_grid_type='ygrid')
    pdict_route = laygen.get_inst_pin_xy(None, None, rg_route)
    #Equalize routing length
    pcm_vbias_xy=pcm_xy+pcm_pins['VBIAS']['xy']
    pcm_out_xy=pcm_xy+pcm_pins['out']['xy']
    pcm_vdd_xy=pcm_xy+pcm_pins['VDD']['xy']
    pcm_vss_xy=pcm_xy+pcm_pins['VSS']['xy']
    sf_vbias_xy=sf_xy+sf_pins['VBIAS']['xy']
    sf_out_xy=sf_xy+sf_pins['out']['xy']
    sf_in_xy=sf_xy+sf_pins['in']['xy']
    sf_vdd_xy=sf_xy+sf_pins['VDD']['xy']
    sf_vss_xy=sf_xy+sf_pins['VSS']['xy']
    sf_vss_1_xy=sf_xy+sf_pins['VSS_1']['xy']
    x0=min(pcm_vbias_xy[0][0], pcm_out_xy[0][0], pcm_vss_xy[0][0], sf_vbias_xy[0][0], sf_out_xy[0][0], sf_in_xy[0][0])
    x1=max(pcm_vbias_xy[1][0], pcm_out_xy[1][0], pcm_vss_xy[1][0], sf_vbias_xy[1][0], sf_out_xy[1][0], sf_in_xy[1][0])
    #routes
    rpcm_vdd=[]
    rpcm_vss=[]
    rpcm_vbias=laygen.add_rect(None, np.array([[x0, pcm_vbias_xy[0][1]], [x1, pcm_vbias_xy[1][1]]]), laygen.layers['metal'][4])
    rpcm_out=[]
    rsf_vdd=[]
    rsf_vss=[]
    rsf_vss_1=[]
    rsf_vbias=[]
    rsf_in=[]
    rsf_out=[]
    rpcm_vdd_xy=[]
    rpcm_vss_xy=[]
    rpcm_vbias_xy=laygen.get_rect_xy(rpcm_vbias.name, gridname=rg_route, sort=True)
    rpcm_out_xy=[]
    rsf_vdd_xy=[]
    rsf_vss_xy=[]
    rsf_vss_1_xy=[]
    rsf_vbias_xy=[]
    rsf_in_xy=[]
    rsf_out_xy=[]
    #VDD/VSS xy
    for i in range(num_bias):
        rpcm_vdd.append(laygen.add_rect(None, np.array([[x0, pcm_vdd_xy[0][1]], [x1, pcm_vdd_xy[1][1]]])+i*np.array([[pcm_size[0], 0], [pcm_size[0], 0]]), laygen.layers['metal'][4]))
        rpcm_vdd_xy.append(laygen.get_rect_xy(rpcm_vdd[-1].name, gridname=rg_m4m5_basic_thick, sort=True))
    for i in range(num_bias):
        rpcm_vss.append(laygen.add_rect(None, np.array([[x0, pcm_vss_xy[0][1]], [x1, pcm_vss_xy[1][1]]])+i*np.array([[pcm_size[0], 0], [pcm_size[0], 0]]), laygen.layers['metal'][4]))
        rpcm_vss_xy.append(laygen.get_rect_xy(rpcm_vss[-1].name, gridname=rg_m4m5_basic_thick, sort=True))
    for i in range(num_bias):
        rsf_vdd.append(laygen.add_rect(None, np.array([[x0, sf_vdd_xy[0][1]], [x1, sf_vdd_xy[1][1]]])+i*np.array([[sf_size[0], 0], [sf_size[0], 0]]), laygen.layers['metal'][4]))
        rsf_vdd_xy.append(laygen.get_rect_xy(rsf_vdd[-1].name, gridname=rg_m4m5_basic_thick, sort=True))
    for i in range(num_bias):
        rsf_vss.append(laygen.add_rect(None, np.array([[x0, sf_vss_xy[0][1]], [x1, sf_vss_xy[1][1]]])+i*np.array([[sf_size[0], 0], [sf_size[0], 0]]), laygen.layers['metal'][4]))
        rsf_vss_xy.append(laygen.get_rect_xy(rsf_vss[-1].name, gridname=rg_m4m5_basic_thick, sort=True))
    for i in range(num_bias):
        rsf_vss_1.append(laygen.add_rect(None, np.array([[x0, sf_vss_1_xy[0][1]], [x1, sf_vss_1_xy[1][1]]])+i*np.array([[sf_size[0], 0], [sf_size[0], 0]]), laygen.layers['metal'][4]))
        rsf_vss_1_xy.append(laygen.get_rect_xy(rsf_vss_1[-1].name, gridname=rg_m4m5_basic_thick, sort=True))
    #MIR_P_xy
    for i in range(num_bias):
        rpcm_out.append(laygen.add_rect(None, np.array([[x0, pcm_out_xy[0][1]], [x1, pcm_out_xy[1][1]]])+i*np.array([[pcm_size[0], 0], [pcm_size[0], 0]]), laygen.layers['metal'][4]))
        rpcm_out_xy.append(laygen.get_rect_xy(rpcm_out[-1].name, gridname=rg_route, sort=True))
    #MIR_N_xy
    for i in range(num_bias):
        rsf_vbias.append(laygen.add_rect(None, np.array([[x0, sf_vbias_xy[0][1]], [x1, sf_vbias_xy[1][1]]])+i*np.array([[sf_size[0], 0], [sf_size[0], 0]]), laygen.layers['metal'][4]))
        rsf_vbias_xy.append(laygen.get_rect_xy(rsf_vbias[-1].name, gridname=rg_route, sort=True))
    #SF_IN_xy
    for i in range(num_bias):
        rsf_in.append(laygen.add_rect(None, np.array([[x0, sf_in_xy[0][1]], [x1, sf_in_xy[1][1]]])+i*np.array([[sf_size[0], 0], [sf_size[0], 0]]), laygen.layers['metal'][4]))
        rsf_in_xy.append(laygen.get_rect_xy(rsf_in[-1].name, gridname=rg_route, sort=True))
    #SF_OUT_xy
    for i in range(num_bias):
        rsf_out.append(laygen.add_rect(None, np.array([[x0, sf_out_xy[0][1]], [x1, sf_out_xy[1][1]]])+i*np.array([[sf_size[0], 0], [sf_size[0], 0]]), laygen.layers['metal'][4]))
        rsf_out_xy.append(laygen.get_rect_xy(rsf_out[-1].name, gridname=rg_route, sort=True))
    #VBIAS
    for pn, p in pcm_pins.items():
        if pn.startswith('VBIAS'):
            pxy=pcm_xy+pcm_pins[pn]['xy']
            rvbias=laygen.add_rect(None, np.array([pxy[0], np.array([pxy[1][0]+pcm_size[0]*(num_bias-1), pxy[1][1]])]), laygen.layers['metal'][4])
            #laygen.add_pin('ADCBIAS', 'ADCBIAS', rvbias.xy, laygen.layers['pin'][4])
    #Vertical routes
    rvdd=[]
    rvss=[]
    rbias=[]
    rin=[]
    rout=[]
    num_route=6
    xref=[]
    for i in range(num_bias):
        xref.append(rpcm_out_xy[i][0][0])
    for i in range(num_bias):
        for j in range(num_route):
            #VDD
            r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=np.array([xref[i]+2*j+1, rpcm_vss_xy[i][0][1]+1]), xy1=np.array([xref[i]+2*j+1, rsf_vss_1_xy[i][1][1]-1]), gridname0=rg_m4m5_basic_thick)
            for k in range(rpcm_vdd_xy[i][0][1]+1, rpcm_vdd_xy[i][1][1], 2):
                laygen.via(None,np.array([xref[i]+2*j+1,  k]), rg_m4m5_basic_thick)
            for k in range(rsf_vdd_xy[i][0][1]+1, rsf_vdd_xy[i][1][1], 2):
                laygen.via(None,np.array([xref[i]+2*j+1,  k]), rg_m4m5_basic_thick)
            rvdd.append(r)
            #VSS
            r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=np.array([xref[i]+2*j+2, rpcm_vss_xy[i][0][1]+1]), xy1=np.array([xref[i]+2*j+2, rsf_vss_1_xy[i][1][1]-1]), gridname0=rg_m4m5_basic_thick)
            rvss.append(r)
            for k in range(rpcm_vss_xy[i][0][1]+1, rpcm_vss_xy[i][1][1], 2):
                laygen.via(None,np.array([xref[i]+2*j+2,  k]), rg_m4m5_basic_thick)
            for k in range(rsf_vss_xy[i][0][1]+1, rsf_vss_xy[i][1][1], 2):
                laygen.via(None,np.array([xref[i]+2*j+2,  k]), rg_m4m5_basic_thick)
            for k in range(rsf_vss_1_xy[i][0][1]+1, rsf_vss_1_xy[i][1][1], 2):
                laygen.via(None,np.array([xref[i]+2*j+2,  k]), rg_m4m5_basic_thick)
            #MIR
            rh0, rv0, rh1 = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][5], rpcm_out_xy[i][0], rsf_vbias_xy[i][0], xref[i]+num_route*3+j+1, gridname=rg_route)
            #VBIAS
            rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], rpcm_vbias_xy[0], rpcm_out_xy[i][0]+np.array([num_route*2+j+1,0]), gridname=rg_route)
            rbias.append(rv0)
            #SF_IN
            rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], rsf_in_xy[i][0], rsf_vbias_xy[i][0]+np.array([num_route*2+j+1,0]), gridname=rg_route)
            rin.append(rv0)
            #SF_OUT
            rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], rsf_out_xy[i][0], rsf_vbias_xy[i][0]+np.array([num_route*4+j+1,0]), gridname=rg_route)
            rout.append(rv0)
    #pin
    for i, r in enumerate(rvdd):
        laygen.add_pin('VDD' + str(i), 'VDD', r.xy, laygen.layers['pin'][5])
    for i, r in enumerate(rvss):
        laygen.add_pin('VSS' + str(i), 'VSS', r.xy, laygen.layers['pin'][5])
    for i, r in enumerate(rbias):
        laygen.add_pin('ADCBIAS' + str(i), 'ADCBIAS', r.xy, laygen.layers['pin'][5])
    for i, r in enumerate(rin):
        laygen.add_pin('VIN'+str(int(i%num_route))+'<'+str(int(i/num_route))+'>', 'VIN<'+str(int(i/num_route))+'>', r.xy, laygen.layers['pin'][5])
    for i, r in enumerate(rout):
        laygen.add_pin('VOUT'+str(int(i%num_route))+ '<' + str(int(i/num_route)) + '>', 'VOUT<'+str(int(i/num_route))+'>', r.xy, laygen.layers['pin'][5])
    #VDD & VSS
    #m4
    vddcnt_m4=0
    vsscnt_m4=0
    rvdd_m4=[]
    rvss_m4=[]
    for pn, p in sf_pins.items():
        if pn.startswith('VDD'):
            pxy=sf_xy+sf_pins[pn]['xy']
            pxy_vss=sf_xy+sf_pins['VSS']['xy']
            #laygen.add_pin('VDD' + str(vddcnt_m4), 'VDD', pxy, sf_pins[pn]['layer'])
            #rvdd_m4.append(laygen.add_rect(None, np.array([pxy[0], np.array([pxy[1][0]+sf_size[0]*(num_bias-1), pxy[1][1]])]), laygen.layers['metal'][4]))
            rvdd_m4.append(laygen.add_rect(None, np.array([np.array([pxy_vss[0][0], pxy[0][1]]), np.array([pxy_vss[1][0]+sf_size[0]*(num_bias-1), pxy[1][1]])]), laygen.layers['metal'][4]))
            vddcnt_m4+=1
        if pn.startswith('VSS'):
            pxy=sf_xy+sf_pins[pn]['xy']
            #laygen.add_pin('VSS' + str(vsscnt_m4), 'VSS', pxy, sf_pins[pn]['layer'])
            rvss_m4.append(laygen.add_rect(None, np.array([pxy[0], np.array([pxy[1][0]+sf_size[0]*(num_bias-1), pxy[1][1]])]), laygen.layers['metal'][4]))
            vsscnt_m4+=1
    for pn, p in pcm_pins.items():
        if pn.startswith('VDD'):
            pxy=pcm_xy+pcm_pins[pn]['xy']
            #laygen.add_pin('VDD' + str(vddcnt_m4), 'VDD', pxy, pcm_pins[pn]['layer'])
            rvdd_m4.append(laygen.add_rect(None, np.array([pxy[0], np.array([pxy[1][0]+pcm_size[0]*(num_bias-1), pxy[1][1]])]), laygen.layers['metal'][4]))
            vddcnt_m4+=1
        if pn.startswith('VSS'):
            pxy=pcm_xy+pcm_pins[pn]['xy']
            #laygen.add_pin('VSS' + str(vsscnt_m4), 'VSS', pxy, pcm_pins[pn]['layer'])
            rvss_m4.append(laygen.add_rect(None, np.array([pxy[0], np.array([pxy[1][0]+pcm_size[0]*(num_bias-1), pxy[1][1]])]), laygen.layers['metal'][4]))
            vsscnt_m4+=1

def generate_sfarray(laygen, objectname_pfix, sf_core_libname, biascap_libname, dcap_upper_libname, dcap_lower_libname,
                     sf_core_name, biascap_name, dcap_upper_name, dcap_lower_name,
                     placement_grid,
                     routing_grid_m3m4, 
                     routing_grid_m4m5, 
                     routing_grid_m4m5_thick, 
                     routing_grid_m4m5_basic_thick, 
                     routing_grid_m5m6_thick, 
                     routing_grid_m5m6_basic_thick, 
                     routing_grid_m6m7_thick, 
                     routing_grid_m7m8_thick, 
                     num_bias=3, origin=np.array([0, 0])):
    """generate sar array core """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_thick = routing_grid_m4m5_thick
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_basic_thick = routing_grid_m5m6_basic_thick
    rg_m6m7_thick = routing_grid_m6m7_thick
    rg_m7m8_thick = routing_grid_m7m8_thick

    num_stack=4
    # placement
    #lower dcap
    idcapl = laygen.place(name="I" + objectname_pfix + 'DCAPL0', templatename=dcap_lower_name,
                          gridname=pg, xy=origin, template_libname=dcap_lower_libname)
    # sf core
    isf = laygen.relplace(name="I" + objectname_pfix + 'SF0', templatename=sf_core_name,
                          gridname=pg, refinstname=idcapl.name, direction='top', shape=np.array([1, num_stack]), template_libname=sf_core_libname)
    #bias cap
    ibcap0 = laygen.relplace(name="I" + objectname_pfix + 'BCAP0', templatename=biascap_name,
                          gridname=pg, refinstname=isf.name, direction='top', template_libname=biascap_libname)
    ibcap1 = laygen.relplace(name="I" + objectname_pfix + 'BCAP1', templatename=biascap_name,
                          gridname=pg, refinstname=ibcap0.name, direction='top', template_libname=biascap_libname)
    ibcap2 = laygen.relplace(name="I" + objectname_pfix + 'BCAP2', templatename=biascap_name,
                          gridname=pg, refinstname=ibcap1.name, direction='top', template_libname=biascap_libname)
    #upper dcap
    idcapu = laygen.relplace(name="I" + objectname_pfix + 'DCAPU0', templatename=dcap_upper_name,
                          gridname=pg, refinstname=ibcap2.name, direction='top', template_libname=dcap_upper_libname)

    #internal routes
    #output to bcap
    num_route=6
    pdict = laygen.get_inst_pin_xy(None, None, rg_m4m5_thick)
    for i in range(6):
        for j in range(num_route):
            rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict[ibcap0.name]['I<'+str(i)+'>'][0], pdict[isf.name]['VOUT'+str(j)+'<0>'][0], gridname=rg_m4m5_thick)
            rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict[ibcap1.name]['I<'+str(i)+'>'][0], pdict[isf.name]['VOUT'+str(j)+'<1>'][0], gridname=rg_m4m5_thick)
            rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict[ibcap2.name]['I<'+str(i)+'>'][0], pdict[isf.name]['VOUT'+str(j)+'<2>'][0], gridname=rg_m4m5_thick)

    #VDD/VSS routes
    pn_vdd_sf=[]
    pn_vss_sf=[]
    rvdd=[]
    rvss=[]
    y0=500000
    y1=0
    y0_upper=500000
    y1_lower=0
    for pn in pdict[isf.name]:
        if pn.startswith('VDD'):
            pn_vdd_sf.append(pn)
        if pn.startswith('VSS'):
            pn_vss_sf.append(pn)
    for pn in pdict[ibcap0.name]:
        if pn.startswith('VDD'):
            for pnvddsf in pn_vdd_sf:
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict[ibcap0.name][pn][0], pdict[isf.name][pnvddsf][0], gridname=rg_m4m5_thick)
        if pn.startswith('VSS'):
            for pnvsssf in pn_vss_sf:
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict[ibcap0.name][pn][0], pdict[isf.name][pnvsssf][0], gridname=rg_m4m5_thick)
    for pn in pdict[ibcap1.name]:
        if pn.startswith('VDD'):
            for pnvddsf in pn_vdd_sf:
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict[ibcap1.name][pn][0], pdict[isf.name][pnvddsf][0], gridname=rg_m4m5_thick)
        if pn.startswith('VSS'):
            for pnvsssf in pn_vss_sf:
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict[ibcap1.name][pn][0], pdict[isf.name][pnvsssf][0], gridname=rg_m4m5_thick)
    for pn in pdict[ibcap2.name]:
        if pn.startswith('VDD'):
            for pnvddsf in pn_vdd_sf:
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict[ibcap2.name][pn][0], pdict[isf.name][pnvddsf][0], gridname=rg_m4m5_thick)
        if pn.startswith('VSS'):
            for pnvsssf in pn_vss_sf:
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict[ibcap2.name][pn][0], pdict[isf.name][pnvsssf][0], gridname=rg_m4m5_thick)
    for pn in pdict[idcapu.name]:
        if pn.startswith('VDD'):
            if pdict[idcapu.name][pn][0][1]>y1:
                y1=pdict[idcapu.name][pn][0][1]
            if pdict[idcapu.name][pn][0][1]<y0_upper:
                y0_upper=pdict[idcapu.name][pn][0][1]
            for pnvddsf in pn_vdd_sf:
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict[idcapu.name][pn][0], pdict[isf.name][pnvddsf][0], gridname=rg_m4m5_thick)
        if pn.startswith('VSS'):
            if pdict[idcapu.name][pn][0][1]>y1:
                y1=pdict[idcapu.name][pn][0][1]
            if pdict[idcapu.name][pn][0][1]<y0_upper:
                y0_upper=pdict[idcapu.name][pn][0][1]
            for pnvsssf in pn_vss_sf:
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict[idcapu.name][pn][0], pdict[isf.name][pnvsssf][0], gridname=rg_m4m5_thick)
    for pn in pdict[idcapl.name]:
        if pn.startswith('VDD'):
            if pdict[idcapl.name][pn][0][1]<y0:
                y0=pdict[idcapl.name][pn][0][1]
            if pdict[idcapl.name][pn][0][1]>y1_lower:
                y1_lower=pdict[idcapl.name][pn][0][1]
            for pnvddsf in pn_vdd_sf:
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict[idcapl.name][pn][0], pdict[isf.name][pnvddsf][0], gridname=rg_m4m5_thick)
        if pn.startswith('VSS'):
            if pdict[idcapl.name][pn][0][1]<y0:
                y0=pdict[idcapl.name][pn][0][1]
            if pdict[idcapl.name][pn][0][1]>y1_lower:
                y1_lower=pdict[idcapl.name][pn][0][1]
            for pnvsssf in pn_vss_sf:
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict[idcapl.name][pn][0], pdict[isf.name][pnvsssf][0], gridname=rg_m4m5_thick)
    #short m5 power grid
    for i, pnvddsf in enumerate(pn_vdd_sf):
        r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=np.array([pdict[isf.name][pnvddsf][0][0], y0]), xy1=np.array([pdict[isf.name][pnvddsf][0][0], y1]), gridname0=rg_m4m5_thick)
        rvdd.append(r)
        #laygen.pin_from_rect('VDD'+str(i), laygen.layers['pin'][5], r, gridname=rg_m4m5_thick, netname='VDD')
    for i, pnvsssf in enumerate(pn_vss_sf):
        r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=np.array([pdict[isf.name][pnvsssf][0][0], y0]), xy1=np.array([pdict[isf.name][pnvsssf][0][0], y1]), gridname0=rg_m4m5_thick)
        rvss.append(r)
        #laygen.pin_from_rect('VSS'+str(i), laygen.layers['pin'][5], r, gridname=rg_m4m5_thick, netname='VSS')
    #lower m5/m6 power grid
    rvddl_m5=[]
    rvssl_m5=[]
    for i, pnvddsf in enumerate(pn_vdd_sf):
        r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=np.array([pdict[isf.name][pnvddsf][0][0], y0]), xy1=np.array([pdict[isf.name][pnvddsf][0][0], y1_lower]), gridname0=rg_m4m5_thick)
        rvddl_m5.append(r)
    for i, pnvsssf in enumerate(pn_vss_sf):
        r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=np.array([pdict[isf.name][pnvsssf][0][0], y0]), xy1=np.array([pdict[isf.name][pnvsssf][0][0], y1_lower]), gridname0=rg_m4m5_thick)
        rvssl_m5.append(r)
    rail_m6_dcapl_vdd, rail_m6_dcapl_vss=laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='RDCAPL_M6',
                    layer=laygen.layers['metal'][6], gridname=rg_m5m6_thick, netnames=['VDD', 'VSS'], direction='x', 
                    input_rails_rect=[rvddl_m5, rvssl_m5], generate_pin=False, 
                    overwrite_start_coord=None, overwrite_end_coord=None, overwrite_num_routes=None,
                    offset_start_index=1, offset_end_index=-1)
    #upper m5/m6 power grid
    rvddu_m5=[]
    rvssu_m5=[]
    for i, pnvddsf in enumerate(pn_vdd_sf):
        r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=np.array([pdict[isf.name][pnvddsf][0][0], y0_upper]), xy1=np.array([pdict[isf.name][pnvddsf][0][0], y1]), gridname0=rg_m4m5_thick)
        rvddu_m5.append(r)
    for i, pnvsssf in enumerate(pn_vss_sf):
        r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=np.array([pdict[isf.name][pnvsssf][0][0], y0_upper]), xy1=np.array([pdict[isf.name][pnvsssf][0][0], y1]), gridname0=rg_m4m5_thick)
        rvssu_m5.append(r)
    rail_m6_dcapu_vdd, rail_m6_dcapu_vss=laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='RDCAPU_M6',
                    layer=laygen.layers['metal'][6], gridname=rg_m5m6_thick, netnames=['VDD', 'VSS'], direction='x', 
                    input_rails_rect=[rvddu_m5, rvssu_m5], generate_pin=False, 
                    overwrite_start_coord=None, overwrite_end_coord=None, overwrite_num_routes=None,
                    offset_start_index=40, offset_end_index=-1)
    #m7 grid
    rail_m7=laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='RDCAPU_M7',
                    layer=laygen.layers['metal'][7], gridname=rg_m6m7_thick, netnames=['VDD', 'VSS'], direction='y', 
                    input_rails_rect=[rail_m6_dcapl_vdd+rail_m6_dcapu_vdd, rail_m6_dcapl_vss+rail_m6_dcapu_vss], generate_pin=False, 
                    overwrite_start_coord=None, overwrite_end_coord=None, overwrite_num_routes=None,
                    offset_start_index=0, offset_end_index=0)
    #m8 grid
    rail_m8=laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='RDCAPU_M8',
                    layer=laygen.layers['pin'][8], gridname=rg_m7m8_thick, netnames=['VDD', 'VSS'], direction='x', 
                    input_rails_rect=rail_m7, generate_pin=True, 
                    overwrite_start_coord=None, overwrite_end_coord=None, overwrite_num_routes=None,
                    offset_start_index=0, offset_end_index=-60)
    
    #pins        
    sf_template = laygen.templates.get_template(sf_core_name, sf_core_libname)
    sf_pins=sf_template.pins
    sf_xy=isf.xy
    sf_size = sf_template.size
    for pn in sf_pins:
        if pn.startswith('ADCBIAS'):
            laygen.add_pin(pn, sf_pins[pn]['netname'], sf_xy+sf_pins[pn]['xy'], sf_pins[pn]['layer'])
            rxy=sf_xy+sf_pins[pn]['xy']
            rxy[1][1] += sf_size[1]*(num_stack-1)
            laygen.add_rect(None, rxy, laygen.layers['metal'][5])
    for pn in sf_pins:
        if pn.startswith('VIN'):
            laygen.add_pin(pn, sf_pins[pn]['netname'], sf_xy+sf_pins[pn]['xy'], sf_pins[pn]['layer'])
            rxy=sf_xy+sf_pins[pn]['xy']
            rxy[1][1] += sf_size[1]*(num_stack-1)
            laygen.add_rect(None, rxy, laygen.layers['metal'][5])
    vout_cnt=np.zeros(num_bias)
    for pn in sf_pins:
        if pn.startswith('VOUT'):
            for i in range(num_bias):
                if pn.endswith('<'+str(i)+'>'):
                    laygen.add_pin('VREF'+str(int(vout_cnt[i]))+'<'+str(i)+'>', 'VREF<'+str(i)+'>', sf_xy+sf_pins[pn]['xy'], sf_pins[pn]['layer'])
                    vout_cnt[i]+=1

def generate_rdacarray_cap(laygen, objectname_pfix, dcap_upper_libname, dcap_upper_name, 
                       placement_grid,
                       routing_grid_m3m4, 
                       routing_grid_m4m5, 
                       routing_grid_m4m5_thick, 
                       routing_grid_m4m5_basic_thick, 
                       routing_grid_m5m6_thick, 
                       routing_grid_m5m6_basic_thick, 
                       routing_grid_m6m7_thick, 
                       routing_grid_m7m8_thick, 
                       num_rdac=4, origin=np.array([0, 0])):
    """generate sar array core """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_thick = routing_grid_m4m5_thick
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_basic_thick = routing_grid_m5m6_basic_thick
    rg_m6m7_thick = routing_grid_m6m7_thick
    rg_m7m8_thick = routing_grid_m7m8_thick

    # placement
    # rdac core
    idcapu = laygen.place(name="I" + objectname_pfix + 'DCAPU0', templatename=dcap_upper_name,
                         gridname=pg, xy=origin, template_libname=dcap_upper_libname)
    #VDD/VSS
    rail_m5_dcapu=laygenhelper.generate_power_rails_from_rails_inst(laygen, routename_tag='RDCAPU_M5', 
                    layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y', 
                    input_rails_instname=idcapu.name, input_rails_pin_prefix=['VDD', 'VSS'], generate_pin=False, 
                    overwrite_start_coord=None, overwrite_end_coord=None, overwrite_num_routes=80,
                    offset_start_index=0, offset_end_index=0)
    #m6 rail
    rail_m6_dcapu=laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='RDCAPU_M6',
                    layer=laygen.layers['pin'][6], gridname=rg_m5m6_thick, netnames=['VDD', 'VSS'], direction='x', 
                    input_rails_rect=rail_m5_dcapu, generate_pin=True, 
                    overwrite_start_coord=1, overwrite_end_coord=None, overwrite_num_routes=None,
                    offset_start_index=0, offset_end_index=0)
    '''
    #m7 rail
    rail_m7_dcapu=laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='RDCAPU_M7',
                    layer=laygen.layers['metal'][7], gridname=rg_m6m7_thick, netnames=['VDD', 'VSS'], direction='y', 
                    input_rails_rect=rail_m6_dcapu, generate_pin=False,  
                    overwrite_start_coord=1, overwrite_end_coord=None, overwrite_num_routes=None,
                    offset_start_index=1, offset_end_index=-1)
    #m8 grid
    rail_m8=laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='RDCAPU_M8',
                    layer=laygen.layers['pin'][8], gridname=rg_m7m8_thick, netnames=['VDD', 'VSS'], direction='x', 
                    input_rails_rect=rail_m7_dcapu, generate_pin=True, 
                    overwrite_start_coord=None, overwrite_end_coord=None, overwrite_num_routes=None,
                    offset_start_index=0, offset_end_index=0)
    '''

def generate_rdacarray(laygen, objectname_pfix, rdac_core_libname, dcap_upper_libname,
                       rdac_core_name, dcap_upper_name, 
                       placement_grid,
                       routing_grid_m3m4, 
                       routing_grid_m4m5, 
                       routing_grid_m4m5_thick, 
                       routing_grid_m4m5_basic_thick, 
                       routing_grid_m5m6_thick, 
                       routing_grid_m5m6_basic_thick, 
                       routing_grid_m6m7_thick, 
                       routing_grid_m7m8_thick, 
                       num_rdac=4, origin=np.array([0, 0])):
    """generate sar array core """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_thick = routing_grid_m4m5_thick
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_basic_thick = routing_grid_m5m6_basic_thick
    rg_m6m7_thick = routing_grid_m6m7_thick
    rg_m7m8_thick = routing_grid_m7m8_thick

    # placement
    # rdac core
    irdac = laygen.place(name="I" + objectname_pfix + 'RDAC0', templatename=rdac_core_name,
                         gridname=pg, xy=origin, template_libname=rdac_core_libname)
    #upper dcap
    idcapu = laygen.relplace(name="I" + objectname_pfix + 'DCAPU0', templatename=dcap_upper_name,
                          gridname=pg, refinstname=irdac.name, direction='top', template_libname=dcap_upper_libname)
    #pins
    rdac_template = laygen.templates.get_template(rdac_core_name, rdac_core_libname)
    rdac_pins=rdac_template.pins
    rdac_xy=irdac.xy[0]
    for pn in rdac_pins:
        if pn.startswith('code'):
            laygen.add_pin(pn, pn, rdac_xy+rdac_pins[pn]['xy'], rdac_pins[pn]['layer'])
        if pn.startswith('out'):
            laygen.add_pin(pn, pn, rdac_xy+rdac_pins[pn]['xy'], rdac_pins[pn]['layer'])
    #VDD/VSS
    rail_m7_dcapu=laygenhelper.generate_power_rails_from_rails_inst(laygen, routename_tag='RDCAPU_M7',
                    layer=laygen.layers['metal'][7], gridname=rg_m6m7_thick, netnames=['VDD', 'VSS'], direction='y', 
                    input_rails_instname=idcapu.name, input_rails_pin_prefix=['VDD', 'VSS'], generate_pin=False,  
                    overwrite_start_coord=None, overwrite_end_coord=None, overwrite_num_routes=None,
                    offset_start_index=1, offset_end_index=-1)
    rail_m7_dcapu_extend0=[]
    for r in rail_m7_dcapu[0]:
        xy0=laygen.get_rect_xy(r.name, gridname=rg_m6m7_thick, sort=True)
        xy0[0][1]=1
        r1=laygen.route(None, laygen.layers['metal'][7], xy0=xy0[0], xy1=xy0[1], gridname0=rg_m6m7_thick)
        rail_m7_dcapu_extend0.append(r1)
    rail_m7_dcapu_extend1=[]
    for r in rail_m7_dcapu[1]:
        xy0=laygen.get_rect_xy(r.name, gridname=rg_m6m7_thick, sort=True)
        xy0[0][1]=1
        r1=laygen.route(None, laygen.layers['metal'][7], xy0=xy0[0], xy1=xy0[1], gridname0=rg_m6m7_thick)
        rail_m7_dcapu_extend1.append(r1)
    rail_m7_dcapu=[rail_m7_dcapu_extend0, rail_m7_dcapu_extend1]
    rg_route='route_M6_M7_thick_temp_pwr'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m6m7_thick, gridname_output=rg_route,
                                          instname=[irdac.name, idcapu.name],
                                          inst_pin_prefix=['VDD', 'VSS'], xy_grid_type='ygrid')
    pdict_route = laygen.get_inst_pin_xy(None, None, rg_route)
    rail_m7_rdac=laygenhelper.generate_power_rails_from_rails_inst(laygen, routename_tag='RDAC_M7', 
                    layer=laygen.layers['metal'][7], gridname=rg_route, netnames=['VDD', 'VSS'], direction='y', 
                    input_rails_instname=irdac.name, input_rails_pin_prefix=['VDD', 'VSS'], generate_pin=False, 
                    overwrite_start_coord=None, overwrite_end_coord=None, overwrite_num_routes=None,
                    offset_start_index=1, offset_end_index=-1)
    #m8 grid
    rail_m8=laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='RDCAPU_M8',
                    layer=laygen.layers['pin'][8], gridname=rg_m7m8_thick, netnames=['VDD', 'VSS'], direction='x', 
                    input_rails_rect=rail_m7_dcapu, generate_pin=True, 
                    overwrite_start_coord=None, overwrite_end_coord=None, overwrite_num_routes=None,
                    offset_start_index=0, offset_end_index=-60)


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
    #ret_libname = 'adc_retimer_ec'
    rdac_libname = 'ge_tech_rdac_8b'
    sf_libname = 'sourceFollower_generated'
    pcm_libname = 'pCM_generated'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    #laygen.load_template(filename=ret_libname+'.yaml', libname=ret_libname)
    laygen.load_template(filename=sf_libname+'.yaml', libname=sf_libname)
    laygen.load_template(filename=pcm_libname+'.yaml', libname=pcm_libname)
    laygen.load_template(filename=rdac_libname+'.yaml', libname=rdac_libname)
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
    rg_m3m4_thick = 'route_M3_M4_thick'
    rg_m3m4_basic_thick = 'route_M3_M4_basic_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m4m5_basic_thick = 'route_M4_M5_basic_thick'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m5m6_basic_thick = 'route_M5_M6_basic_thick'
    rg_m6m7_thick = 'route_M6_M7_thick'
    rg_m7m8_thick = 'route_M7_M8_thick'

    mycell_list = []
    num_bits=9
    num_slices=9
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        num_bits=specdict['n_bit']
        num_slices=specdict['n_interleave']

    cellname = 'sarbias_'+str(num_slices)+'slice'
    sf_name = 'sourceFollower'
    pcm_name = 'pCM'
    rdac_name = 'rdac'
    tisar_name = 'tisaradc_body_'+str(num_bits)+'b_array_'+str(num_slices)+'slice_core'
    sar_name = 'sar_wsamp_'+str(num_bits)+'b_array_'+str(num_slices)+'slice'
    #ret_name = 'adc_retimer'
    #sh_name = 'adc_frontend_sampler_array'
    #tisar_dcap_name = 'tisaradc_body_dcap'
    #dcap_name = 'dcap'
    #sf core generation (w/o pmos mirror)
    cellname = 'sarbias_'+str(num_slices)+'slice_sfarray_wopcm_core'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sfarray_wopcm_core(laygen, objectname_pfix='SF0', 
                    sf_libname=sf_libname, cap_1x_libname=logictemplib,
                    sf_name=sf_name, cap_1x_name='space_1x',
                    placement_grid=pg, 
                    routing_grid_m3m4=rg_m3m4, 
                    routing_grid_m4m5=rg_m4m5, 
                    routing_grid_m4m5_basic_thick=rg_m4m5_basic_thick, 
                    routing_grid_m4m5_thick=rg_m4m5_thick, 
                    routing_grid_m5m6_thick=rg_m5m6_thick, 
                    routing_grid_m5m6_basic_thick=rg_m5m6_basic_thick, 
                    routing_grid_m6m7_thick=rg_m6m7_thick, 
                    num_bias=3, left_space=12, right_space=12+36, bot_space=0, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    sf_wopcm_core_name=cellname

    #biascap generation
    #calculate # of cap cells to be inserted
    x0 = laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('tap', libname=logictemplib).xy[1][0] * 2 \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_cap_4x=int(m_space/10) #x6 instead of x4..needs to be fixed
    m_space_2x=int((m_space-m_cap_4x*10)/2)
    m_space_1x=int(m_space-m_cap_4x*10-m_space_2x*2)
    #generate
    cellname = 'sarbias_'+str(num_slices)+'slice_sfarray_biascap_core'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_cap(laygen, objectname_pfix='CAP0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                 cap_1x_name='space_1x', cap_2x_name='space_2x', cap_4x_name='bcap2_8x',
                 m_cap_4x=m_cap_4x, m_cap_2x=m_space_2x, m_cap_1x=m_space_1x, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    cellname_core=cellname
    cellname = 'sarbias_'+str(num_slices)+'slice_sfarray_biascap'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_cap_wbnd(laygen, objectname_pfix='CAP0', workinglib=workinglib, cap_name=cellname_core, placement_grid=pg, m=6, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    biascap_name=cellname

    #dcap generation(lower side)
    #calculate # of cap cells to be inserted
    x0 = laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('tap', libname=logictemplib).xy[1][0] * 2 \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_cap_4x=int(m_space/10) #x10 instead of x4..needs to be fixed
    m_space_2x=int((m_space-m_cap_4x*10)/2)
    m_space_1x=int(m_space-m_cap_4x*10-m_space_2x*2)
    #generate
    cellname = 'sarbias_'+str(num_slices)+'slice_sfarray_dcap_lower_core'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_cap(laygen, objectname_pfix='CAP0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                 cap_1x_name='space_1x', cap_2x_name='space_2x', cap_4x_name='dcap2_8x',
                 m_cap_4x=m_cap_4x, m_cap_2x=m_space_2x, m_cap_1x=m_space_1x, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    cellname_core=cellname
    cellname = 'sarbias_'+str(num_slices)+'slice_sfarray_dcap_lower'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_cap_wbnd(laygen, objectname_pfix='CAP0', workinglib=workinglib, cap_name=cellname_core, placement_grid=pg, m=4, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    dcap_lower_name=cellname

    #dcap generation(upper side)
    #calculate # of cap cells to be inserted
    x0 = laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('tap', libname=logictemplib).xy[1][0] * 2 \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_cap_4x=int(m_space/10) #x10 instead of x4..needs to be fixed
    m_space_2x=int((m_space-m_cap_4x*10)/2)
    m_space_1x=int(m_space-m_cap_4x*10-m_space_2x*2)
    #generate
    cellname = 'sarbias_'+str(num_slices)+'slice_sfarray_dcap_upper_core'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_cap(laygen, objectname_pfix='CAP0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                 cap_1x_name='space_1x', cap_2x_name='space_2x', cap_4x_name='dcap2_8x',
                 m_cap_4x=m_cap_4x, m_cap_2x=m_space_2x, m_cap_1x=m_space_1x, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    cellname_core=cellname
    cellname = 'sarbias_'+str(num_slices)+'slice_sfarray_dcap_upper'
    print(cellname+" generating")
    #figure out dcap stack size
    num_stack=4
    y0 = laygen.templates.get_template('tisaradc_body_space', libname=workinglib).xy[1][1] \
         - laygen.templates.get_template(dcap_lower_name, libname=workinglib).xy[1][1] \
         - laygen.templates.get_template(sf_wopcm_core_name, libname=workinglib).xy[1][1]*num_stack \
         - laygen.templates.get_template(biascap_name, libname=workinglib).xy[1][1]*3
    m_cup = int(round(y0 / laygen.templates.get_template(cellname_core, libname=workinglib).xy[1][1])) - 1
    #m_cup = int(round(y0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][1])) - 1
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_cap_wbnd(laygen, objectname_pfix='CAP0', workinglib=workinglib, cap_name=cellname_core, placement_grid=pg, m=m_cup, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    dcap_upper_name=cellname

    #sf top generation
    cellname = 'sarbias_'+str(num_slices)+'slice_sfarray'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    #sf_wopcm_core_name=cellname
    generate_sfarray(laygen, objectname_pfix='SF0', 
                    sf_core_libname=workinglib, biascap_libname=workinglib, dcap_lower_libname=workinglib, dcap_upper_libname=workinglib,
                    sf_core_name=sf_wopcm_core_name, biascap_name=biascap_name, dcap_lower_name=dcap_lower_name, dcap_upper_name=dcap_upper_name,
                    placement_grid=pg, 
                    routing_grid_m3m4=rg_m3m4, 
                    routing_grid_m4m5=rg_m4m5, 
                    routing_grid_m4m5_basic_thick=rg_m4m5_basic_thick, 
                    routing_grid_m4m5_thick=rg_m4m5_thick, 
                    routing_grid_m5m6_thick=rg_m5m6_thick, 
                    routing_grid_m5m6_basic_thick=rg_m5m6_basic_thick, 
                    routing_grid_m6m7_thick=rg_m6m7_thick, 
                    routing_grid_m7m8_thick=rg_m7m8_thick, 
                    num_bias=3, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    #rdac core generation
    cellname = 'sarbias_'+str(num_slices)+'slice_rdac_core'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_rdacarray_core(laygen, objectname_pfix='RDAC0', rdac_libname=rdac_libname, 
                            cap_1x_libname=logictemplib, rdac_name=rdac_name, cap_1x_name='space_1x',
                            placement_grid=pg,
                            routing_grid_m3m4=rg_m3m4, 
                            routing_grid_m4m5=rg_m4m5, 
                            routing_grid_m4m5_thick=rg_m4m5_thick, 
                            routing_grid_m4m5_basic_thick=rg_m4m5_basic_thick, 
                            routing_grid_m5m6_thick=rg_m5m6_thick, 
                            routing_grid_m5m6_basic_thick=rg_m5m6_basic_thick, 
                            routing_grid_m6m7_thick=rg_m6m7_thick, 
                            num_rdac=4, origin=np.array([0, 0])) #left_space=12, right_space=12, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    rdac_core_name=cellname

    rdac_core_name = 'sarbias_'+str(num_slices)+'slice_rdac_core'
    #rdac dcap generation(upper side)
    #calculate # of cap cells to be inserted
    #x0 = laygen.templates.get_template(rdac_core_name, libname=workinglib).xy[1][0] \
    #     - laygen.templates.get_template('tap', libname=logictemplib).xy[1][0] * 2 \
    #     - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    x0 = laygen.templates.get_template(rdac_core_name, libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    x0 = x0/4 #4 rdac
    x0 = x0 - laygen.templates.get_template('tap', libname=logictemplib).xy[1][0] * 2 
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_cap_4x=int(m_space/10) #x10 instead of x4..needs to be fixed
    m_space_2x=int((m_space-m_cap_4x*10)/2)
    m_space_1x=int(m_space-m_cap_4x*10-m_space_2x*2)
    #generate
    cellname = 'sarbias_'+str(num_slices)+'slice_rdacarray_dcap_upper_core'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_cap(laygen, objectname_pfix='CAP0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                 cap_1x_name='space_1x', cap_2x_name='space_2x', cap_4x_name='dcap2_8x',
                 m_cap_4x=m_cap_4x, m_cap_2x=m_space_2x, m_cap_1x=m_space_1x, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    cellname_core=cellname
    cellname = 'sarbias_'+str(num_slices)+'slice_rdacarray_dcap_upper'
    print(cellname+" generating")
    #figure out dcap stack size
    y0 = laygen.templates.get_template('tisaradc_body_space', libname=workinglib).xy[1][1] \
         - laygen.templates.get_template(rdac_core_name, libname=workinglib).xy[1][1] 
    m_cup = int(round(y0 / laygen.templates.get_template(cellname_core, libname=workinglib).xy[1][1])) - 1
    #m_cup = int(round(y0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][1])) - 1
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_cap_wbnd(laygen, objectname_pfix='CAP0', workinglib=workinglib, cap_name=cellname_core, placement_grid=pg, m=m_cup, shape=np.array([4, 1]), origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    dcap_upper_name=cellname

    rdac_upper_name = 'sarbias_'+str(num_slices)+'slice_rdac_core'
    dcap_upper_name = 'sarbias_'+str(num_slices)+'slice_rdacarray_dcap_upper'
    #rdac cap wrapper generation
    cellname = 'sarbias_'+str(num_slices)+'slice_rdacarray_dcap_upper_wrap'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_rdacarray_cap(laygen, objectname_pfix='RDAC0', 
                    dcap_upper_libname=workinglib, dcap_upper_name=dcap_upper_name,
                    placement_grid=pg, 
                    routing_grid_m3m4=rg_m3m4, 
                    routing_grid_m4m5=rg_m4m5, 
                    routing_grid_m4m5_basic_thick=rg_m4m5_basic_thick, 
                    routing_grid_m4m5_thick=rg_m4m5_thick, 
                    routing_grid_m5m6_thick=rg_m5m6_thick, 
                    routing_grid_m5m6_basic_thick=rg_m5m6_basic_thick, 
                    routing_grid_m6m7_thick=rg_m6m7_thick, 
                    routing_grid_m7m8_thick=rg_m7m8_thick, 
                    num_rdac=4, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    dcap_upper_name=cellname
    rdac_core_name = 'sarbias_'+str(num_slices)+'slice_rdac_core'
    dcap_upper_name = 'sarbias_'+str(num_slices)+'slice_rdacarray_dcap_upper_wrap'

    #rdac top generation
    cellname = 'sarbias_'+str(num_slices)+'slice_rdacarray'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_rdacarray(laygen, objectname_pfix='RDAC0', 
                    rdac_core_libname=workinglib, dcap_upper_libname=workinglib,
                    rdac_core_name=rdac_core_name, dcap_upper_name=dcap_upper_name,
                    placement_grid=pg, 
                    routing_grid_m3m4=rg_m3m4, 
                    routing_grid_m4m5=rg_m4m5, 
                    routing_grid_m4m5_basic_thick=rg_m4m5_basic_thick, 
                    routing_grid_m4m5_thick=rg_m4m5_thick, 
                    routing_grid_m5m6_thick=rg_m5m6_thick, 
                    routing_grid_m5m6_basic_thick=rg_m5m6_basic_thick, 
                    routing_grid_m6m7_thick=rg_m6m7_thick, 
                    routing_grid_m7m8_thick=rg_m7m8_thick, 
                    num_rdac=4, origin=np.array([0, 0]))
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

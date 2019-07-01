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


def generate_sarafe_nsw(laygen, objectname_pfix, workinglib, placement_grid,
                    routing_grid_m2m3_thick, routing_grid_m3m4_thick,
                    routing_grid_m4m5_thick, 
                    routing_grid_m5m6, routing_grid_m5m6_thick, routing_grid_m5m6_basic_thick,
                    routing_grid_m6m7,
                    num_bits=8, num_bits_vertical=6, num_cdrv_output_routes=2, m_sa=8, double_sa=False, vref_sf=False, origin=np.array([0, 0])):
    """generate sar analog frontend """
    pg = placement_grid

    rg_m3m4_thick = routing_grid_m3m4_thick
    rg_m5m6 = routing_grid_m5m6
    rg_m6m7 = routing_grid_m6m7

    tap_name='tap'
    cdrv_name='capdrv_nsw_array'
    #cdac_name='capdac_'+str(num_bits)+'b'
    cdac_name='capdac'
    sf_name='sourceFollower_vref'
    if double_sa == False:
        sa_name='salatch_pmos'
    elif double_sa == True:
        sa_name='doubleSA_pmos'
    # placement
    xy0 = origin + (laygen.get_template_size(cdrv_name, gridname=pg, libname=workinglib)*np.array([1, 0]) )
    icdrvl = laygen.place(name="I" + objectname_pfix + 'CDRVL0', templatename=cdrv_name, gridname=pg,
                          xy=xy0, template_libname = workinglib, transform='MY')
    icdrvr = laygen.place(name="I" + objectname_pfix + 'CDRVR0', templatename=cdrv_name, gridname=pg,
                          xy=xy0, template_libname = workinglib)

    # xy0 = origin + laygen.get_template_size(cdrv_name, gridname=pg, libname=workinglib)*np.array([0, 1]) \
    #          + laygen.get_template_size(sa_name, gridname=pg, libname=workinglib) * np.array([0, 1])
    # isa = laygen.place(name="I" + objectname_pfix + 'SA0', templatename=sa_name, gridname=pg,
    #                    xy=xy0, template_libname = workinglib, transform='MX')
    # if vref_sf == True:
    #     xy0 = origin + laygen.get_template_size(cdrv_name, gridname=pg, libname=workinglib) * np.array([0, 1])
    #     isf = laygen.relplace(name="I" + objectname_pfix + 'SF0', templatename=sf_name, gridname=pg, refinstname=isa.name,
    #                           direction='top', template_libname=workinglib)
    #     xy0 = origin + laygen.get_template_size(cdrv_name, gridname=pg, libname=workinglib) * np.array([0, 1]) \
    #           + laygen.get_template_size(sf_name, gridname=pg, libname=workinglib) * np.array([0, 1]) \
    #           + laygen.get_template_size(sa_name, gridname=pg, libname=workinglib) * np.array([0, 1])

    if vref_sf == True:
        xy0 = origin + laygen.get_template_size(cdrv_name, gridname=pg, libname=workinglib) * np.array([0, 1])
        isf = laygen.place(name="I" + objectname_pfix + 'SF0', templatename=sf_name, gridname=pg,
                           xy=xy0, template_libname=workinglib)
        isa = laygen.relplace(name="I" + objectname_pfix + 'SA0', templatename=sa_name, gridname=pg,
                              refinstname=isf.name, direction='top', transform='MX', template_libname=workinglib)
        xy0 = origin + laygen.get_template_size(cdrv_name, gridname=pg, libname=workinglib) * np.array([0, 1]) \
              + laygen.get_template_size(sf_name, gridname=pg, libname=workinglib) * np.array([0, 1]) \
              + laygen.get_template_size(sa_name, gridname=pg, libname=workinglib) * np.array([0, 1])

    xy0 = origin + xy0 \
                 + laygen.get_template_size(cdac_name, gridname=pg, libname=workinglib)*np.array([1, 0])
    icdacl = laygen.place(name="I" + objectname_pfix + 'CDACL0', templatename=cdac_name, gridname=pg,
                          xy=xy0, template_libname = workinglib, transform='MY')
    icdacr = laygen.place(name="I" + objectname_pfix + 'CDACR0', templatename=cdac_name, gridname=pg,
                          xy=xy0, template_libname = workinglib)

    # pin informations
    pdict_m3m4_thick=laygen.get_inst_pin_xy(None, None, rg_m3m4_thick)

    # internal pins
    icdrvl_vo_xy = []
    icdacl_i_xy = []
    icdacl_i2_xy = []
    icdrvr_vo_xy = []
    icdacr_i_xy = []
    icdacr_i2_xy = []

    icdrvl_vo_c0_xy = laygen.get_inst_pin_xy(icdrvl.name, 'VO_C0', rg_m5m6)
    icdacl_i_c0_xy = laygen.get_inst_pin_xy(icdacl.name, 'I_C0', rg_m5m6)
    icdrvr_vo_c0_xy = laygen.get_inst_pin_xy(icdrvr.name, 'VO_C0', rg_m5m6)
    icdacr_i_c0_xy = laygen.get_inst_pin_xy(icdacr.name, 'I_C0', rg_m5m6)
    for i in range(num_bits):
        icdacl_i_xy.append(laygen.get_inst_pin_xy(icdacl.name, 'I<' + str(i) + '>', rg_m4m5))
        icdacr_i_xy.append(laygen.get_inst_pin_xy(icdacr.name, 'I<' + str(i) + '>', rg_m4m5))
        if i>=num_bits_vertical:
            icdacl_i2_xy.append(laygen.get_inst_pin_xy(icdacl.name, 'I2<' + str(i) + '>', rg_m4m5))
            icdacr_i2_xy.append(laygen.get_inst_pin_xy(icdacr.name, 'I2<' + str(i) + '>', rg_m4m5))

    for j in range(num_cdrv_output_routes):
        for i in range(num_bits):
            icdrvl_vo_xy.append(laygen.get_inst_pin_xy(icdrvl.name, 'VO'+str(j)+'<' + str(i) + '>', rg_m5m6))
            icdrvr_vo_xy.append(laygen.get_inst_pin_xy(icdrvr.name, 'VO'+str(j)+'<' + str(i) + '>', rg_m5m6))

    #route
    #capdrv to capdac
    #y0 = origin[1] + laygen.get_template_size(cdrv_name, gridname=rg_m5m6, libname=workinglib)[1]-2 #refer to capdrv
    # y0 = origin[1] + laygen.get_template_size(cdrv_name, gridname=rg_m4m5, libname=workinglib)[1] \
    #      + laygen.get_template_size(sa_name, gridname=rg_m4m5, libname=workinglib)[1]-4 #refer to sa
    y0 = origin[1] + laygen.get_inst_xy(isa.name, gridname=rg_m4m5)[1]-4 #refer to sa
    if vref_sf == False:
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6], icdrvl_vo_c0_xy[0],
                                           icdacl_i_c0_xy[0], y0 + 1, rg_m5m6, layerv1=laygen.layers['metal'][5], gridname1=rg_m5m6)
        laygen.boundary_pin_from_rect(rv0, rg_m4m5, "VOL_C0", laygen.layers['pin'][5], size=4, direction='bottom', netname='VREF<1>')
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6], icdrvr_vo_c0_xy[0],
                                           icdacr_i_c0_xy[0], y0 + 1, rg_m5m6, layerv1=laygen.layers['metal'][5], gridname1=rg_m5m6)
        laygen.boundary_pin_from_rect(rv0, rg_m4m5, "VOR_C0", laygen.layers['pin'][5], size=4, direction='bottom', netname='VREF<1>')
    else:
        [rh0, rv0] = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                            xy0=laygen.get_inst_pin_xy(isf.name, 'out<1>', rg_m4m5_thick_basic)[0],
                            xy1=laygen.get_inst_pin_xy(icdacl.name, 'I_C0', rg_m4m5_thick_basic)[0],
                            gridname0=rg_m4m5_thick_basic)
        # laygen.boundary_pin_from_rect(rv0, rg_m4m5, "VOL_C0", laygen.layers['pin'][5], size=4, direction='bottom', netname='SF_VREF<1>')
        [rh0, rv0] = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                            xy0=laygen.get_inst_pin_xy(isf.name, 'out<1>', rg_m4m5_thick_basic)[0],
                            xy1=laygen.get_inst_pin_xy(icdacr.name, 'I_C0', rg_m4m5_thick_basic)[0],
                            gridname0=rg_m4m5_thick_basic)
        # laygen.boundary_pin_from_rect(rv0, rg_m4m5, "VOR_C0", laygen.layers['pin'][5], size=4, direction='bottom', netname='SF_VREF<1>')
        x0 = laygen.get_template_size(sa_name, gridname=rg_m3m4, libname=workinglib)[0]
        y_byp = laygen.get_inst_pin_xy(isf.name, 'bypass', rg_m3m4)[0][1]
        rbyp = laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, y_byp]), xy1=np.array([x0, y_byp]), gridname0=rg_m3m4)
        laygen.via(None, xy=np.array([laygen.get_inst_pin_xy(isf.name, 'bypass', rg_m3m4)[0][0], y_byp]), gridname=rg_m3m4)
        # laygen.pin('SF_bypass', layer=laygen.layers['pin'][3], xy=laygen.get_inst_pin_xy(isf.name, 'bypass', rg_m3m4), gridname=rg_m3m4)
        laygen.pin('SF_bypass', layer=laygen.layers['pin'][4], xy=np.array([[0, y_byp], [x0, y_byp]]), gridname=rg_m3m4)
        laygen.pin('SF_VBIAS', layer=laygen.layers['pin'][5],
                   xy=laygen.get_inst_pin_xy(isf.name, 'VBIAS', rg_m4m5_thick), gridname=rg_m4m5_thick)

    for j in range(num_cdrv_output_routes):
        for i in range(num_bits):
            if i in range(num_bits_vertical) and i%2==(num_bits_vertical+1)%2:
                #if not i%2==num_bits_vertical%2:
                [rv0l, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][4], icdrvl_vo_xy[i+j*num_bits][0],
                                               icdacl_i_xy[i][0], y0 - i - 1, rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4)
                [rv0r, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][4], icdrvr_vo_xy[i+j*num_bits][0],
                                               icdacr_i_xy[i][0], y0 - i - 1, rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4)
            else:
                [rv0l, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6], icdrvl_vo_xy[i+j*num_bits][0],
                                               icdacl_i_xy[i][0], y0 - i - 1, rg_m5m6, layerv1=laygen.layers['metal'][5], gridname1=rg_m5m6)
                [rv0r, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][6], icdrvr_vo_xy[i+j*num_bits][0],
                                               icdacr_i_xy[i][0], y0 - i - 1, rg_m5m6, layerv1=laygen.layers['metal'][5], gridname1=rg_m5m6)
            laygen.boundary_pin_from_rect(rv0l, rg_m4m5, "VOL<"+str(i)+">", laygen.layers['pin'][5], size=4, direction='bottom')
            laygen.boundary_pin_from_rect(rv0r, rg_m4m5, "VOR<"+str(i)+">", laygen.layers['pin'][5], size=4, direction='bottom')
            #more routes for horizontal dacs
            if i>=num_bits_vertical:
                [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][4], icdrvl_vo_xy[i+j*num_bits][0],
                                                   icdacl_i_xy[i][0], y0 + 2 + i - num_bits_vertical, rg_m4m5, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
                [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][4], icdrvr_vo_xy[i+j*num_bits][0],
                                                   icdacr_i_xy[i][0], y0 + 2 + i - num_bits_vertical, rg_m4m5, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
                [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][4], icdrvl_vo_xy[i+j*num_bits][0],
                                                   icdacl_i2_xy[i-num_bits_vertical][0], y0 + 2 + i - num_bits_vertical, rg_m4m5, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
                [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][5], laygen.layers['metal'][4], icdrvr_vo_xy[i+j*num_bits][0],
                                                   icdacr_i2_xy[i-num_bits_vertical][0], y0 + 2 + i - num_bits_vertical, rg_m4m5, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)



    #vref
    rvref0=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                        refinstname0=icdrvl.name, refpinname0='VREF<0>', gridname0=rg_m4m5,
                        refinstname1=icdrvr.name, refpinname1='VREF<0>')
    rvref1=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                        refinstname0=icdrvl.name, refpinname0='VREF<1>', gridname0=rg_m4m5,
                        refinstname1=icdrvr.name, refpinname1='VREF<1>')
    rvref2=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                        refinstname0=icdrvl.name, refpinname0='VREF<2>', gridname0=rg_m4m5,
                        refinstname1=icdrvr.name, refpinname1='VREF<2>')
    #input pins
    #y0 = laygen.get_inst_pin_xy(icdrvl.name, 'EN0<0>', rg_m4m5, index=np.array([0, 0]), sort=True)[0][1]
    y0 = 0
    rclkb=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                      refinstname0=isa.name, refpinname0='CLKB', gridname0=rg_m4m5, direction='y')
    routp=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                      refinstname0=isa.name, refpinname0='OUTP', gridname0=rg_m4m5, direction='y')
    routm=laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                      refinstname0=isa.name, refpinname0='OUTM', gridname0=rg_m4m5, direction='y')
    #rosp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
    #                  refinstname0=isa.name, refpinname0='OSP', gridname0=rg_m2m3, direction='y')
    #rosm=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
    #                  refinstname0=isa.name, refpinname0='OSM', gridname0=rg_m2m3, direction='y')
    pdict_m3m4 = laygen.get_inst_pin_xy(None, None, rg_m3m4)
    laygen.get_inst_xy(icdacr.name, rg_m3m4)
    yos=laygen.get_inst_xy(isa.name, rg_m3m4)[1] \
        - laygen.get_template_size(name=isa.cellname, gridname=rg_m3m4, libname=workinglib)[1]
    [rv0, rh0, rosp] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict_m3m4[isa.name]['OSP'][0],
                                       np.array([laygen.get_inst_xy(icdacr.name, rg_m3m4)[0]-2, 0]), yos, rg_m3m4)
    [rv0, rh0, rosm] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict_m3m4[isa.name]['OSM'][0],
                                       np.array([laygen.get_inst_xy(icdacr.name, rg_m3m4)[0]+2, 0]), yos, rg_m3m4)
    renl0 = []
    renl1 = []
    renl2 = []
    renr0 = []
    renr1 = []
    renr2 = []
    for i in range(num_bits):
        renl0.append(laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                     refinstname0=icdrvl.name, refpinname0='EN'+str(i)+'<0>', gridname0=rg_m5m6, direction='y'))
        renl1.append(laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                     refinstname0=icdrvl.name, refpinname0='EN'+str(i)+'<1>', gridname0=rg_m5m6, direction='y'))
        renl2.append(laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                     refinstname0=icdrvl.name, refpinname0='EN'+str(i)+'<2>', gridname0=rg_m5m6, direction='y'))
        renr0.append(laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                     refinstname0=icdrvr.name, refpinname0='EN'+str(i)+'<0>', gridname0=rg_m5m6, direction='y'))
        renr1.append(laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                     refinstname0=icdrvr.name, refpinname0='EN'+str(i)+'<1>', gridname0=rg_m5m6, direction='y'))
        renr2.append(laygen.route(None, laygen.layers['metal'][5], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                     refinstname0=icdrvr.name, refpinname0='EN'+str(i)+'<2>', gridname0=rg_m5m6, direction='y'))
    #inp/inm
    pdict_m3m4 = laygen.get_inst_pin_xy(None, None, rg_m3m4)
    outcnt=0
    for pn in pdict_m3m4[icdacl.name]:
        if pn.startswith('O'): #out pin
            outcnt+=1
    x0 = laygen.get_inst_xy(icdacl.name, rg_m3m4)[0] - 8
    x1 = laygen.get_inst_xy(icdacr.name, rg_m3m4)[0] + 8
    nrin_sa = 4  # number of M6 horizontal route stacks for cdac to sa
    nrin = 2**num_bits_vertical - 2*nrin_sa # number of M6 horizontal route stacks
    if nrin<1: 
        nrin = 2**num_bits_vertical - nrin_sa
    rinp=[]
    rinm=[]
    for i in range(nrin):
        xy0=laygen.get_inst_pin_xy(icdacl.name, "O"+str(outcnt-1-i), rg_m3m4, index=np.array([0, 0]), sort=True)[0]
        r = laygen.route(None, laygen.layers['metal'][4], xy0=xy0, xy1=np.array([x0, xy0[1]]), gridname0=rg_m3m4)
        rinp.append(r)
        '''
        #additional routes for dummy for density rules; may not process portable
        for j in range(3):
            laygen.route(None, laygen.layers['metal'][6], xy0=xy0+np.array([0, 2*j+2]), xy1=np.array([x0, xy0[1]+2*j+2]), gridname0=rg_m5m6)
        '''
        xy0=laygen.get_inst_pin_xy(icdacr.name, "O"+str(outcnt-1-i), rg_m3m4, index=np.array([0, 0]), sort=True)[1]
        r = laygen.route(None, laygen.layers['metal'][4], xy0=xy0, xy1=np.array([x1, xy0[1]]), gridname0=rg_m3m4)
        rinm.append(r)
        '''
        #additional routes for dummy for density rules; may not process portable
        for j in range(3):
            laygen.route(None, laygen.layers['metal'][6], xy0=xy0+np.array([0, 2*j+2]), xy1=np.array([x1, xy0[1]+2*j+2]), gridname0=rg_m5m6)
        '''

    for i in range(nrin_sa):
        xy0=laygen.get_inst_pin_xy(icdacl.name, "O"+str(i), rg_m3m4, index=np.array([0, 0]), sort=True)[0]
        laygen.route(None, laygen.layers['metal'][4], xy0=xy0, xy1=np.array([x0, xy0[1]]), gridname0=rg_m4m5)
        for j in range(4):
            laygen.via(None, [x0-2*j, xy0[1]], rg_m4m5)
        xy0=laygen.get_inst_pin_xy(icdacr.name, "O"+str(i), rg_m3m4, index=np.array([0, 0]), sort=True)[1]
        laygen.route(None, laygen.layers['metal'][4], xy0=xy0, xy1=np.array([x1, xy0[1]]), gridname0=rg_m4m5)
        for j in range(4):
            laygen.via(None, [x1+2*j, xy0[1]], rg_m4m5)
    xy0 = laygen.get_inst_pin_xy(isa.name, "INP", rg_m3m4, index=np.array([0, 0]), sort=True)[0]
    xy1 = laygen.get_inst_pin_xy(icdacl.name, "O"+str(nrin_sa-1), rg_m4m5, index=np.array([0, 0]), sort=True)[0]
    for j in range(4):
        laygen.route(None, laygen.layers['metal'][5], xy0=np.array([x0-2*j, xy0[1]]), xy1=np.array([x0-2*j, xy1[1]]), gridname0=rg_m5m6)
    xy0 = laygen.get_inst_pin_xy(isa.name, "INM", rg_m4m5, index=np.array([0, 0]), sort=True)[0]
    xy1 = laygen.get_inst_pin_xy(icdacr.name, "O"+str(nrin_sa-1), rg_m5m6, index=np.array([0, 0]), sort=True)[0]
    for j in range(4):
        laygen.route(None, laygen.layers['metal'][5], xy0=np.array([x1+2*j, xy0[1]]), xy1=np.array([x1+2*j, xy1[1]]), gridname0=rg_m5m6)
    #inp/inm - sa to capdac
    xy0 = laygen.get_inst_pin_xy(isa.name, "INP", rg_m4m5, index=np.array([0, 0]), sort=True)[0]
    xy1 = laygen.get_inst_pin_xy(isa.name, "INM", rg_m4m5, index=np.array([0, 0]), sort=True)[0]
    rsainp=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x0-8, xy0[1]]), xy1=xy0, gridname0=rg_m4m5)
    rsainm=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x1+8, xy1[1]]), xy1=xy1, gridname0=rg_m4m5)
    for j in range(4):
        laygen.via(None, [x0 - 2 * j, xy0[1]], rg_m4m5)
        laygen.via(None, [x1 + 2 * j, xy1[1]], rg_m4m5)
    x0 = laygen.get_inst_xy(icdacl.name, rg_m3m4)[0] - 1
    x1 = laygen.get_inst_xy(icdacr.name, rg_m3m4)[0] + 1
    xy0 = laygen.get_inst_pin_xy(isa.name, "INP", rg_m3m4, index=np.array([0, 0]), sort=True)[0]
    xy1 = laygen.get_inst_pin_xy(isa.name, "INM", rg_m3m4, index=np.array([0, 0]), sort=True)[0]
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x0, xy0[1]]), xy1=xy0, gridname0=rg_m3m4, via1=[[0, 0]])
    laygen.route(None, laygen.layers['metal'][4], xy0=np.array([x1, xy1[1]]), xy1=xy1, gridname0=rg_m3m4, via1=[[0, 0]])

    #vdd/vss - route
    #cdrv_left_m4
    rvdd_cdrvl_m3=[]
    rvss_cdrvl_m3=[]
    for pn, p in pdict_m3m4_thick[icdrvl.name].items():
        if pn.startswith('VSSR'):
            rvss_cdrvl_m3.append(p)
    input_rails_xy = [rvss_cdrvl_m3]
    rvss_cdrvl_m4 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_CDRVL_M4_', 
                layer=laygen.layers['metal'][4], gridname=rg_m3m4_thick, netnames=['VSS'], direction='x', 
                input_rails_xy=input_rails_xy, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=None, 
                offset_start_index=0, offset_end_index=0)
    rvss_cdrvl_m4=rvss_cdrvl_m4[0]
    #cdrv_right_m4
    x1 = laygen.get_inst_xy(name=icdrvr.name, gridname=rg_m3m4_thick)[0]\
         +laygen.get_template_size(name=icdrvr.cellname, gridname=rg_m3m4_thick, libname=workinglib)[0]
    rvdd_cdrvr_m3=[]
    rvss_cdrvr_m3=[]
    for pn, p in pdict_m3m4_thick[icdrvr.name].items():
        if pn.startswith('VSSR'):
            rvss_cdrvr_m3.append(p)
    input_rails_xy = [rvss_cdrvr_m3]
    rvss_cdrvr_m4 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_CDRVR_M4_', 
                layer=laygen.layers['metal'][4], gridname=rg_m3m4_thick, netnames=['VSS'], direction='x', 
                input_rails_xy=input_rails_xy, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=x1, 
                offset_start_index=0, offset_end_index=0)
    rvss_cdrvr_m4=rvss_cdrvr_m4[0]
    #sa_left_m4_m5
    rvdd_sal_m3=[]
    rvss_sal_m3=[]
    for pn, p in pdict_m3m4_thick[isa.name].items():
        if pn.startswith('VDDL'):
            rvdd_sal_m3.append(p)
        if pn.startswith('VSSL'):
            rvss_sal_m3.append(p)
    input_rails_xy = [rvdd_sal_m3, rvss_sal_m3]
    rvdd_sal_m4, rvss_sal_m4 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_SAL_M4_', 
                layer=laygen.layers['metal'][4], gridname=rg_m3m4_thick, netnames=['VDD', 'VSS'], direction='x', 
                input_rails_xy=input_rails_xy, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=-4)
    #input_rails_rect = [rvdd_sal_m4+rvdd_cdrvl_m4, rvss_sal_m4+rvss_cdrvl_m4]
    input_rails_rect = [rvdd_sal_m4, rvss_sal_m4+rvss_cdrvl_m4]
    rvdd_sal_m5, rvss_sal_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_SAL_M5_', 
                layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=None,
                offset_start_index=1, offset_end_index=-6)
    #sa_right_m4_m5
    x1 = laygen.get_inst_xy(name=isa.name, gridname=rg_m3m4_thick)[0]\
         +laygen.get_template_size(name=isa.cellname, gridname=rg_m3m4_thick, libname=workinglib)[0]
    rvdd_sar_m3=[]
    rvss_sar_m3=[]
    for pn, p in pdict_m3m4_thick[isa.name].items():
        if pn.startswith('VDDR'):
            rvdd_sar_m3.append(p)
        if pn.startswith('VSSR'):
            rvss_sar_m3.append(p)
    input_rails_xy = [rvdd_sar_m3, rvss_sar_m3]
    rvdd_sar_m4, rvss_sar_m4 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_SAR_M4_', 
                layer=laygen.layers['metal'][4], gridname=rg_m3m4_thick, netnames=['VDD', 'VSS'], direction='x', 
                input_rails_xy=input_rails_xy, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=x1,
                offset_start_index=0, offset_end_index=-4)
    #input_rails_rect = [rvdd_sar_m4+rvdd_cdrvr_m4, rvss_sar_m4+rvss_cdrvr_m4]
    input_rails_rect = [rvdd_sar_m4, rvss_sar_m4+rvss_cdrvr_m4]
    rvdd_sar_m5, rvss_sar_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_SAR_M5_', 
                layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=None,
                offset_start_index=7, offset_end_index=0)
    #sa_m6
    num_vref_routes_m6=5
    x1 = laygen.get_inst_xy(name=isa.name, gridname=rg_m5m6_thick)[0]\
         +laygen.get_template_size(name=isa.cellname, gridname=rg_m5m6_thick, libname=workinglib)[0]
    x1_phy = laygen.get_inst_xy(name=isa.name)[0]\
         +laygen.get_template_size(name=isa.cellname, libname=workinglib)[0]
    y1 = laygen.get_inst_xy(name=isa.name, gridname=rg_m5m6_thick)[1]
    input_rails_rect = [rvdd_sal_m5+rvdd_sar_m5, rvss_sal_m5+rvss_sar_m5]
    #sa_m6_bottom_shield
    rvdd_sa_m6, rvss_sa_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_0_', 
                layer=laygen.layers['metal'][6], gridname=rg_m5m6_thick, netnames=['VDD', 'VSS'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=x1,
                overwrite_start_index=2, overwrite_end_index=4)
    #trimming
    for r in rvdd_sa_m6:
        r.xy1[0]=x1_phy
    for r in rvss_sa_m6:
        r.xy1[0]=x1_phy
    #sa_m6_mid and top_shield
    for i in range(3):
        rvss_sa_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_'+str(i+1)+'_', 
                    layer=laygen.layers['metal'][6], gridname=rg_m5m6_thick, netnames=['VSS'], direction='x', 
                    input_rails_rect=[rvss_sal_m5+rvss_sar_m5], 
                    generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=x1,
                    overwrite_start_index=4+(1+num_vref_routes_m6)*(i+1)-1, overwrite_num_routes=0)#overwrite_end_index=4+(1+num_vref_routes_m6)*(i+1))
        #trimming
        for r in rvss_sa_m6[0]:
            r.xy1[0]=x1_phy
    #sa_m6_top_main_route
    vbias_xy = laygen.get_inst_pin_xy(isf.name, 'VBIAS', rg_m5m6_thick)
    rvdd_sa_m6_b, rvss_sa_m6_b = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_B_',
                layer=laygen.layers['metal'][6], gridname=rg_m5m6_thick, netnames=['VDD', 'VSS'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=False, 
                overwrite_start_coord=0, overwrite_end_coord=x1,
                offset_start_index=4+(1+num_vref_routes_m6)*3, overwrite_end_index=vbias_xy[0][1]-1)
    rvdd_sa_m6_t, rvss_sa_m6_t = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_T_',
                layer=laygen.layers['metal'][6], gridname=rg_m5m6_thick, netnames=['VDD', 'VSS'], direction='x',
                input_rails_rect=input_rails_rect, generate_pin=False,
                overwrite_start_coord=0, overwrite_end_coord=x1,
                overwrite_start_index=vbias_xy[1][1]+1, offset_end_index=0)
    #trimming and pinning
    for r in rvdd_sa_m6_b:
        r.xy1[0]=x1_phy
        p=laygen.pin_from_rect(name='VDD_M6_'+r.name, layer=laygen.layers['pin'][6], rect=r, gridname=rg_m5m6_thick, netname='VDD')
        p.xy1[0]=x1_phy
    for r in rvss_sa_m6_b:
        r.xy1[0]=x1_phy
        p=laygen.pin_from_rect(name='VSS_M6_'+r.name, layer=laygen.layers['pin'][6], rect=r, gridname=rg_m5m6_thick, netname='VSS')
        p.xy1[0]=x1_phy
    for r in rvdd_sa_m6_t:
        r.xy1[0]=x1_phy
        p=laygen.pin_from_rect(name='VDD_M6_'+r.name, layer=laygen.layers['pin'][6], rect=r, gridname=rg_m5m6_thick, netname='VDD')
        p.xy1[0]=x1_phy
    for r in rvss_sa_m6_t:
        r.xy1[0]=x1_phy
        p=laygen.pin_from_rect(name='VSS_M6_'+r.name, layer=laygen.layers['pin'][6], rect=r, gridname=rg_m5m6_thick, netname='VSS')
        p.xy1[0]=x1_phy
    #pins
    #laygen.pin(name='VREF<0>', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(rvref0.name, rg_m4m5), gridname=rg_m4m5)
    #laygen.pin(name='VREF<1>', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(rvref1.name, rg_m4m5), gridname=rg_m4m5)
    #laygen.pin(name='VREF<2>', layer=laygen.layers['pin'][4], xy=laygen.get_rect_xy(rvref2.name, rg_m4m5), gridname=rg_m4m5)
    '''
    t = laygen.templates.get_template(icdrvl.cellname, libname=workinglib)
    vref0vl_pin_xy=np.tile(laygen.get_inst_xy(name=icdrvl.name, gridname=rg_m4m5), (2,1))\
                   + np.array([-1, 1]) * laygen.get_template_pin_xy(t.name, 'VREF_M5<0>', rg_m4m5, libname=workinglib)
    vref1vl_pin_xy=np.tile(laygen.get_inst_xy(name=icdrvl.name, gridname=rg_m4m5), (2,1))\
                   + np.array([-1, 1]) * laygen.get_template_pin_xy(t.name, 'VREF_M5<1>', rg_m4m5, libname=workinglib)
    vref2vl_pin_xy=np.tile(laygen.get_inst_xy(name=icdrvl.name, gridname=rg_m4m5), (2,1))\
                   + np.array([-1, 1]) * laygen.get_template_pin_xy(t.name, 'VREF_M5<2>', rg_m4m5, libname=workinglib)
    vref0vr_pin_xy=np.tile(laygen.get_inst_xy(name=icdrvr.name, gridname=rg_m4m5), (2,1))\
                   + np.array([1, 1]) * laygen.get_template_pin_xy(t.name, 'VREF_M5<0>', rg_m4m5, libname=workinglib)
    vref1vr_pin_xy=np.tile(laygen.get_inst_xy(name=icdrvr.name, gridname=rg_m4m5), (2,1))\
                   + np.array([1, 1]) * laygen.get_template_pin_xy(t.name, 'VREF_M5<1>', rg_m4m5, libname=workinglib)
    vref2vr_pin_xy=np.tile(laygen.get_inst_xy(name=icdrvr.name, gridname=rg_m4m5), (2,1))\
                   + np.array([1, 1]) * laygen.get_template_pin_xy(t.name, 'VREF_M5<2>', rg_m4m5, libname=workinglib)
    laygen.pin(name='VREF_M5L<0>', layer=laygen.layers['pin'][5], xy=vref0vl_pin_xy, gridname=rg_m4m5, netname='VREF<0>')
    laygen.pin(name='VREF_M5L<1>', layer=laygen.layers['pin'][5], xy=vref1vl_pin_xy, gridname=rg_m4m5, netname='VREF<1>')
    laygen.pin(name='VREF_M5L<2>', layer=laygen.layers['pin'][5], xy=vref2vl_pin_xy, gridname=rg_m4m5, netname='VREF<2>')
    laygen.pin(name='VREF_M5R<0>', layer=laygen.layers['pin'][5], xy=vref0vr_pin_xy, gridname=rg_m4m5, netname='VREF<0>')
    laygen.pin(name='VREF_M5R<1>', layer=laygen.layers['pin'][5], xy=vref1vr_pin_xy, gridname=rg_m4m5, netname='VREF<1>')
    laygen.pin(name='VREF_M5R<2>', layer=laygen.layers['pin'][5], xy=vref2vr_pin_xy, gridname=rg_m4m5, netname='VREF<2>')
    vref0vl_pin_xy=np.tile(laygen.get_inst_xy(name=icdrvl.name, gridname=rg_m4m5), (2,1))\
                   + np.array([-1, 1]) * laygen.get_template_pin_xy(t.name, 'VREF_M5_2<0>', rg_m4m5, libname=workinglib)
    vref1vl_pin_xy=np.tile(laygen.get_inst_xy(name=icdrvl.name, gridname=rg_m4m5), (2,1))\
                   + np.array([-1, 1]) * laygen.get_template_pin_xy(t.name, 'VREF_M5_2<1>', rg_m4m5, libname=workinglib)
    vref2vl_pin_xy=np.tile(laygen.get_inst_xy(name=icdrvl.name, gridname=rg_m4m5), (2,1))\
                   + np.array([-1, 1]) * laygen.get_template_pin_xy(t.name, 'VREF_M5_2<2>', rg_m4m5, libname=workinglib)
    vref0vr_pin_xy=np.tile(laygen.get_inst_xy(name=icdrvr.name, gridname=rg_m4m5), (2,1))\
                   + np.array([1, 1]) * laygen.get_template_pin_xy(t.name, 'VREF_M5_2<0>', rg_m4m5, libname=workinglib)
    vref1vr_pin_xy=np.tile(laygen.get_inst_xy(name=icdrvr.name, gridname=rg_m4m5), (2,1))\
                   + np.array([1, 1]) * laygen.get_template_pin_xy(t.name, 'VREF_M5_2<1>', rg_m4m5, libname=workinglib)
    vref2vr_pin_xy=np.tile(laygen.get_inst_xy(name=icdrvr.name, gridname=rg_m4m5), (2,1))\
                   + np.array([1, 1]) * laygen.get_template_pin_xy(t.name, 'VREF_M5_2<2>', rg_m4m5, libname=workinglib)
    laygen.pin(name='VREF_M5L_2<0>', layer=laygen.layers['pin'][5], xy=vref0vl_pin_xy, gridname=rg_m4m5, netname='VREF<0>')
    laygen.pin(name='VREF_M5L_2<1>', layer=laygen.layers['pin'][5], xy=vref1vl_pin_xy, gridname=rg_m4m5, netname='VREF<1>')
    laygen.pin(name='VREF_M5L_2<2>', layer=laygen.layers['pin'][5], xy=vref2vl_pin_xy, gridname=rg_m4m5, netname='VREF<2>')
    laygen.pin(name='VREF_M5R_2<0>', layer=laygen.layers['pin'][5], xy=vref0vr_pin_xy, gridname=rg_m4m5, netname='VREF<0>')
    laygen.pin(name='VREF_M5R_2<1>', layer=laygen.layers['pin'][5], xy=vref1vr_pin_xy, gridname=rg_m4m5, netname='VREF<1>')
    laygen.pin(name='VREF_M5R_2<2>', layer=laygen.layers['pin'][5], xy=vref2vr_pin_xy, gridname=rg_m4m5, netname='VREF<2>')
    '''
    #sf_left_m4_m5
    rvdd_sf_m4=[]
    rvss_sf_m4=[]
    pdict_m4m5_thick=laygen.get_inst_pin_xy(None, None, rg_m4m5_thick)
    for pn, p in pdict_m4m5_thick[isf.name].items():
        if pn.startswith('VDD'):
            rvdd_sf_m4.append(p)
        if pn.startswith('VSS'):
            rvss_sf_m4.append(p)
    input_rails_xy = [rvdd_sf_m4, rvss_sf_m4]
    rvdd_sfl_m5, rvss_sfl_m5 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_SFL_M5_',
                layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y',
                input_rails_xy=input_rails_xy, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=None,
                offset_start_index=1, overwrite_end_index=4)
    # input_rails_rect = [rvdd_sal_m4, rvss_sal_m4+rvss_cdrvl_m4]
    # rvdd_sal_m5, rvss_sal_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_SAL_M5_',
    #             layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y',
    #             input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=None,
    #             offset_start_index=1, offset_end_index=-6)

    # VREF
    pdict_vref=laygen.get_inst_pin_xy(None, None, rg_m5m6_basic_thick)
    x1 = laygen.get_inst_xy(name=isa.name, gridname=rg_m5m6_basic_thick)[0]\
         +laygen.get_template_size(name=isa.cellname, gridname=rg_m5m6_basic_thick, libname=workinglib)[0]
    if vref_sf == False:
        for i in range(3):
            laygen.route(None, laygen.layers['metal'][5], gridname0=rg_m5m6_basic_thick,
                         xy0=pdict_vref[icdrvl.name]['VREF_M5<'+str(i)+'>'][0],
                         xy1=pdict_vref[icdrvl.name]['VREF_M5<'+str(i)+'>'][0]+np.array([0, (num_vref_routes_m6+1)*3+4]))
            laygen.route(None, laygen.layers['metal'][5], gridname0=rg_m5m6_basic_thick,
                         xy0=pdict_vref[icdrvr.name]['VREF_M5<'+str(i)+'>'][0],
                         xy1=pdict_vref[icdrvr.name]['VREF_M5<'+str(i)+'>'][0]+np.array([0, (num_vref_routes_m6+1)*3+4]))
            laygen.route(None, laygen.layers['metal'][5], gridname0=rg_m5m6_basic_thick,
                         xy0=pdict_vref[icdrvl.name]['VREF_M5_2<'+str(i)+'>'][0],
                         xy1=pdict_vref[icdrvl.name]['VREF_M5_2<'+str(i)+'>'][0]+np.array([0, (num_vref_routes_m6+1)*3+4]))
            laygen.route(None, laygen.layers['metal'][5], gridname0=rg_m5m6_basic_thick,
                         xy0=pdict_vref[icdrvr.name]['VREF_M5_2<'+str(i)+'>'][0],
                         xy1=pdict_vref[icdrvr.name]['VREF_M5_2<'+str(i)+'>'][0]+np.array([0, (num_vref_routes_m6+1)*3+4]))
            input_rails_xy=[[pdict_vref[icdrvl.name]['VREF_M5<'+str(i)+'>'], pdict_vref[icdrvl.name]['VREF_M5_2<'+str(i)+'>'],
                             pdict_vref[icdrvr.name]['VREF_M5<'+str(i)+'>'], pdict_vref[icdrvr.name]['VREF_M5_2<'+str(i)+'>']]]
            laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_M6_', layer=laygen.layers['pin'][6],
                gridname=rg_m5m6_basic_thick, netnames=['VREF<'+str(i)+'>'], direction='x',
                input_rails_xy=input_rails_xy, generate_pin=True, overwrite_start_coord=0, overwrite_end_coord=x1,
                overwrite_start_index=4+(num_vref_routes_m6+1)*i, overwrite_end_index=4+(num_vref_routes_m6+1)*i+num_vref_routes_m6-1)
    else:
        x_ref = laygen.get_inst_pin_xy(icdrvl.name, 'VREF_M5_2<1>', rg_m4m5_thick_basic)[0][0]
        for i in range(3):
            rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                       xy0=laygen.get_inst_pin_xy(isf.name, 'in<'+str(i)+'>', rg_m4m5)[0],
                                       xy1=np.array([x_ref-1-1*i, 2]),
                                       gridname0=rg_m4m5)
            # rh1, rv1 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
            #                            xy0=laygen.get_inst_pin_xy(isf.name, 'in<'+str(i)+'>', rg_m4m5)[0],
            #                            xy1=np.array([x_center-2+2*i, 2]),
            #                            gridname0=rg_m4m5)
            laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_', layer=laygen.layers['pin'][6],
                                                            gridname=rg_m5m6_basic_thick, netnames=['VREF<' + str(i) + '>'],
                                                            direction='x',
                                                            input_rails_rect=[[rv0]], generate_pin=True,
                                                            overwrite_start_coord=0, overwrite_end_coord=x1,
                                                            overwrite_start_index=4 + (num_vref_routes_m6 + 1) * i,
                                                            overwrite_end_index=4 + (num_vref_routes_m6 + 1) * i + num_vref_routes_m6 - 1)
            laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                            xy0=laygen.get_inst_pin_xy(isf.name, 'out<'+str(i)+'>', rg_m4m5_thick_basic)[0],
                            xy1=laygen.get_inst_pin_xy(icdrvl.name, 'VREF_M5<'+str(i)+'>', rg_m4m5_thick_basic)[0],
                            gridname0=rg_m4m5_thick_basic)
            laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                            xy0=laygen.get_inst_pin_xy(isf.name, 'out<'+str(i)+'>', rg_m4m5_thick_basic)[0],
                            xy1=laygen.get_inst_pin_xy(icdrvl.name, 'VREF_M5_2<'+str(i)+'>', rg_m4m5_thick_basic)[0],
                            gridname0=rg_m4m5_thick_basic)
            laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                            xy0=laygen.get_inst_pin_xy(isf.name, 'out<'+str(i)+'>', rg_m4m5_thick_basic)[0],
                            xy1=laygen.get_inst_pin_xy(icdrvr.name, 'VREF_M5<'+str(i)+'>', rg_m4m5_thick_basic)[0],
                            gridname0=rg_m4m5_thick_basic)
            laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                            xy0=laygen.get_inst_pin_xy(isf.name, 'out<'+str(i)+'>', rg_m4m5_thick_basic)[0],
                            xy1=laygen.get_inst_pin_xy(icdrvr.name, 'VREF_M5_2<'+str(i)+'>', rg_m4m5_thick_basic)[0],
                            gridname0=rg_m4m5_thick_basic)

    laygen.boundary_pin_from_rect(rclkb, rg_m4m5, "CLKB", laygen.layers['pin'][5], size=4, direction='bottom')
    laygen.boundary_pin_from_rect(routp, rg_m4m5, "OUTP", laygen.layers['pin'][5], size=4, direction='bottom')
    laygen.boundary_pin_from_rect(routm, rg_m4m5, "OUTM", laygen.layers['pin'][5], size=4, direction='bottom')
    laygen.boundary_pin_from_rect(rosp, rg_m2m3, "OSP", laygen.layers['pin'][3], size=4, direction='bottom')
    laygen.boundary_pin_from_rect(rosm, rg_m2m3, "OSM", laygen.layers['pin'][3], size=4, direction='bottom')
    for i in range(num_bits):
        laygen.boundary_pin_from_rect(renl0[i], rg_m5m6, "ENL"+str(i)+"<0>", laygen.layers['pin'][5], size=4, direction='bottom')
        laygen.boundary_pin_from_rect(renl1[i], rg_m5m6, "ENL"+str(i)+"<1>", laygen.layers['pin'][5], size=4, direction='bottom')
        laygen.boundary_pin_from_rect(renl2[i], rg_m5m6, "ENL"+str(i)+"<2>", laygen.layers['pin'][5], size=4, direction='bottom')
        laygen.boundary_pin_from_rect(renr0[i], rg_m5m6, "ENR"+str(i)+"<0>", laygen.layers['pin'][5], size=4, direction='bottom')
        laygen.boundary_pin_from_rect(renr1[i], rg_m5m6, "ENR"+str(i)+"<1>", laygen.layers['pin'][5], size=4, direction='bottom')
        laygen.boundary_pin_from_rect(renr2[i], rg_m5m6, "ENR"+str(i)+"<2>", laygen.layers['pin'][5], size=4, direction='bottom')

    laygen.pin_from_rect(name='SAINP', layer=laygen.layers['pin'][4], rect=rsainp, gridname=rg_m4m5, netname='INP')
    laygen.pin_from_rect(name='SAINM', layer=laygen.layers['pin'][4], rect=rsainm, gridname=rg_m4m5, netname='INM')
    for i, r in enumerate(rinp):
        laygen.boundary_pin_from_rect(r, rg_m4m5, "INP"+str(i), laygen.layers['pin'][4], size=8, direction='right', netname="INP")
    for i, r in enumerate(rinm):
        laygen.boundary_pin_from_rect(r, rg_m4m5, "INM"+str(i), laygen.layers['pin'][4], size=8, direction='left', netname="INM")

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
    rg_m2m3_thick = 'route_M2_M3_thick_basic'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m3m4_thick = 'route_M3_M4_basic_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m4m5_thick_basic = 'route_M4_M5_thick_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m5m6_basic_thick = 'route_M5_M6_basic_thick'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m6m7 = 'route_M6_M7_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    mycell_list = []
    num_bits=8
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        num_bits=specdict['n_bit']-1
        vref_sf=specdict['use_vref_sf']
        m_sa=sizedict['salatch']['m']
        doubleSA=sizedict['salatch']['doubleSA']
        num_bits_vertical=sizedict['capdac']['num_bits_vertical']
    #sarafe generation
    cellname='sarafe_nsw_doubleSA'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarafe_nsw(laygen, objectname_pfix='CA0', workinglib=workinglib,
                    placement_grid=pg, routing_grid_m2m3_thick=rg_m2m3_thick, routing_grid_m3m4_thick=rg_m3m4_thick,
                    routing_grid_m4m5_thick=rg_m4m5_thick, routing_grid_m5m6=rg_m5m6, 
                    routing_grid_m5m6_basic_thick=rg_m5m6_basic_thick, routing_grid_m5m6_thick=rg_m5m6_thick,
                    routing_grid_m6m7=rg_m6m7, num_bits=num_bits, num_bits_vertical=num_bits_vertical,
                    num_cdrv_output_routes=1, m_sa=m_sa, double_sa=doubleSA, vref_sf=vref_sf,
                    origin=np.array([0, 0]))
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

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

def generate_TISARADC(laygen, objectname_pfix, sar_libname, rdac_libname, space_1x_libname,
                             sar_name, rdac_name, space_1x_name, placement_grid,
                                routing_grid_m3m4, routing_grid_m4m5, routing_grid_m4m5_basic_thick, routing_grid_m5m6, routing_grid_m5m6_thick,
                                routing_grid_m5m6_basic_thick, routing_grid_m5m6_thick_basic,
                                routing_grid_m6m7_thick, routing_grid_m7m8_thick,
                                num_inv_bb, num_bits=9, num_slices=8, clk_pulse=True, slice_order=[0, 1], trackm=4, origin=np.array([0, 0])):
    """generate sar array """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_basic_thick = routing_grid_m5m6_basic_thick
    rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic
    rg_m6m7_thick = routing_grid_m6m7_thick
    rg_m7m8_thick = routing_grid_m7m8_thick

    # placement
    # sar
    # sar_slice_size = laygen.templates.get_template(sar_slice_name, libname=sar_libname).size
    bnd_size = laygen.get_template('boundary_bottom', libname=utemplib).size
    sar_slice_size = laygen.get_template_size(sar_slice_name, pg, libname=sar_libname)
    rdac_xy = laygen.templates.get_template(rdac_name, libname=rdac_libname).xy
    rdac_off_x = laygen.grids.get_absgrid_x(pg, rdac_xy[1][0])
    num_input_shield_track = 0 # defined in tisar_htree_diff_m7m8, to be parameterized
    if not num_input_shield_track == 0:
        htree_off_y = laygen.get_template_pin_xy(htree_name, 'VSS_0_0', rg_m7m8_thick, libname=workinglib)[0][1]-2
        if num_input_shield_track == 2:
            htree_off_x = laygen.get_template_pin_xy(htree_name, 'VSS_0_0', rg_m7m8_thick, libname=workinglib)[0][0]/2 + \
                          laygen.get_template_pin_xy(htree_name, 'VSS_0_1', rg_m7m8_thick, libname=workinglib)[0][0]/2 - \
                          int(laygen.get_template_size(sar_slice_name, rg_m7m8_thick, libname=workinglib)[0]/2*5)
        elif num_input_shield_track == 1:
            htree_off_x = laygen.get_template_pin_xy(htree_name, 'VSS_0_0', rg_m7m8_thick, libname=workinglib)[0][0] - \
                          int(laygen.get_template_size(sar_slice_name, rg_m7m8_thick, libname=workinglib)[0]/2*5+0.5)
    else:
        htree_off_y = laygen.get_template_pin_xy(htree_name, 'WNO_0_0', rg_m7m8_thick, libname=workinglib)[0][1]-2
        htree_off_x = int(laygen.get_template_pin_xy(htree_name, 'WNO_0_0', rg_m7m8_thick, libname=workinglib)[0][0] / 2 + \
                      laygen.get_template_pin_xy(htree_name, 'WPO_0_0', rg_m7m8_thick, libname=workinglib)[0][0] / 2 - \
                      laygen.get_template_size(sar_slice_name, rg_m7m8_thick, libname=workinglib)[0] / 2 * 5 + 0.5)-1

    # sar_xy = origin + (laygen.get_template_size(rdac_name, gridname=pg, libname=rdac_libname)*np.array([1,0]) )
    sar_xy = origin
    isar = laygen.relplace(name="I" + objectname_pfix + 'SAR0', templatename=sar_name,
                      gridname=pg, xy=sar_xy, template_libname=sar_libname)
    irdac = laygen.relplace(name="I" + objectname_pfix + 'RDAC0', templatename=rdac_name,
                      gridname=pg, transform='R0', xy=[-rdac_off_x, 0],
                      template_libname=rdac_libname)
    if input_htree == True:
        ihtree_in = laygen.relplace(name="I" + objectname_pfix + 'HTREE0', templatename=htree_name,
                          gridname=rg_m7m8_thick, transform='MX', xy=[-htree_off_x, htree_off_y],
                          template_libname=workinglib)

    sar_template = laygen.templates.get_template(sar_name, sar_libname)
    sar_pins=sar_template.pins
    sar_xy=isar.xy

    #prboundary
    # sar_size = laygen.templates.get_template(sar_name, libname=sar_libname).size
    space_size = laygen.templates.get_template('boundary_bottom', libname=utemplib).size
    size_x=isar.xy[0]+isar.size[0]
    size_y=isar.xy[1]+isar.size[1]
    laygen.add_rect(None, np.array([origin, origin+np.array([size_x, size_y])]), laygen.layers['prbnd'])

    # Routing

    pdict_m2m3=laygen.get_inst_pin_xy(None, None, rg_m2m3)
    pdict_m3m4=laygen.get_inst_pin_xy(None, None, rg_m3m4)
    pdict_m4m5=laygen.get_inst_pin_xy(None, None, rg_m4m5)
    pdict_m4m5_basic_thick=laygen.get_inst_pin_xy(None, None, rg_m4m5_basic_thick)
    pdict_m5m6=laygen.get_inst_pin_xy(None, None, rg_m5m6)
    pdict_m5m6_thick=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    pdict_m6m7_thick=laygen.get_inst_pin_xy(None, None, rg_m6m7_thick)
    pdict_m7m8_thick=laygen.get_inst_pin_xy(None, None, rg_m7m8_thick)
    pdict_m5m6_thick_basic=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick_basic)

    # ADC input route
    if input_htree == True:
        rinp_m7=[]
        rinm_m7=[]
        num_input_track = htree_trackm
        if htree_metal_v == 7:
            for i in range(num_slices):
                inp_xy_m5 = pdict_m5m6_thick[isar.name]['INP%d' % i][1]
                inm_xy_m5 = pdict_m5m6_thick[isar.name]['INM%d' % i][1]
                for j in range(num_input_track):
                    inp_xy_m7 = laygen.get_inst_pin_xy(ihtree_in.name, 'WPO_' + str(slice_order.index(i)) + '_' + str(j), rg_m6m7_thick)[1]
                    inm_xy_m7 = laygen.get_inst_pin_xy(ihtree_in.name, 'WNO_' + str(slice_order.index(i)) + '_' + str(j), rg_m6m7_thick)[1]
                    laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                                 xy0=inp_xy_m5, xy1=inp_xy_m7, track_y=inp_xy_m5[1]-3,
                                 gridname0=rg_m5m6_thick, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7_thick)
                    laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                                     xy0=inm_xy_m5, xy1=inm_xy_m7, track_y=inm_xy_m5[1]-2,
                                     gridname0=rg_m5m6_thick, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7_thick)
                # for j in range(num_input_shield_track):
                #     for k in range(2):
                #         laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                #                      xy0=laygen.get_inst_pin_xy(iret.name, 'VSS' + str(2*i+k), rg_m5m6_thick)[1],
                #                      xy1=laygen.get_inst_pin_xy(ihtree_in.name, 'VSS_' + str(i) + '_' + str(j), rg_m6m7_thick)[1],
                #                      track_y=laygen.get_inst_pin_xy(ihtree_in.name, 'VSS_' + str(i) + '_' + str(j), rg_m6m7_thick)[0][1],
                #                      gridname0=rg_m5m6_thick, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7_thick)
            for j in range(num_input_track):
                inp_xy_m7 = laygen.get_inst_pin_xy(ihtree_in.name, 'WPI_' + str(j), rg_m6m7_thick)
                inm_xy_m7 = laygen.get_inst_pin_xy(ihtree_in.name, 'WNI_' + str(num_input_shield_track+num_input_track+j), rg_m6m7_thick)
                laygen.pin('INP_'+str(j), xy=inp_xy_m7, layer=laygen.layers['pin'][7], gridname=rg_m6m7_thick, netname='INP')
                laygen.pin('INM_' + str(j), xy=inm_xy_m7, layer=laygen.layers['pin'][7], gridname=rg_m6m7_thick, netname='INM')

        elif htree_metal_v == 9:
            for i in range(num_slices):
                inp_xy_m5 = pdict_m5m6_thick[isar.name]['INP%d' % i][1]
                inm_xy_m5 = pdict_m5m6_thick[isar.name]['INM%d' % i][1]
                inp_xy_m7 = pdict_m7m8_thick[isar.name]['INP%d' % i][1]
                inm_xy_m7 = pdict_m7m8_thick[isar.name]['INM%d' % i][1]
                m8_ref_y = pdict_m7m8_thick[isar.name]['VDDSAMP_SAMP_M8_0'][1][1]
                for j in range(num_input_track):
                    inp_xy_m9 = laygen.get_inst_pin_xy(ihtree_in.name, 'WPO_' + str(slice_order.index(i)) + '_' + str(j), rg_m8m9_thick)[1]
                    inm_xy_m9 = laygen.get_inst_pin_xy(ihtree_in.name, 'WNO_' + str(slice_order.index(i)) + '_' + str(j), rg_m8m9_thick)[1]
                    rv0, rh0, rv1 = laygen.route_vhv(layerv0=laygen.layers['metal'][7], layerh=laygen.layers['metal'][8],
                                 xy0=inp_xy_m7, xy1=inp_xy_m9, track_y=m8_ref_y-3,
                                 gridname0=rg_m7m8_thick, layerv1=laygen.layers['metal'][9], gridname1=rg_m8m9_thick)
                    rh_m8 = laygen.route(None, laygen.layers['metal'][8], np.array([inp_xy_m7[0]-2, m8_ref_y-3]), np.array([inp_xy_m7[0]+2, m8_ref_y-3]), rg_m7m8_thick)
                    xy = laygen.get_rect_xy(rv0.name, rg_m6m7_thick)[0]
                    laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                                 xy0=inp_xy_m5, xy1=xy, track_y=inp_xy_m5[1]+6,
                                 gridname0=rg_m5m6_thick, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7_thick)

                    rv0, rh0, rv1 = laygen.route_vhv(layerv0=laygen.layers['metal'][7], layerh=laygen.layers['metal'][8],
                                     xy0=inm_xy_m7, xy1=inm_xy_m9, track_y=m8_ref_y-2,
                                     gridname0=rg_m7m8_thick, layerv1=laygen.layers['metal'][9], gridname1=rg_m8m9_thick)
                    rh_m8 = laygen.route(None, laygen.layers['metal'][8], np.array([inm_xy_m7[0]-2, m8_ref_y-2]), np.array([inm_xy_m7[0]+2, m8_ref_y-2]), rg_m7m8_thick)
                    xy = laygen.get_rect_xy(rv0.name, rg_m6m7_thick)[0]
                    laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                                 xy0=inm_xy_m5, xy1=xy, track_y=inm_xy_m5[1]+7,
                                 gridname0=rg_m5m6_thick, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7_thick)
                # for j in range(num_input_shield_track):
                #     for k in range(2):
                #         laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                #                      xy0=laygen.get_inst_pin_xy(iret.name, 'VSS' + str(2*i+k), rg_m5m6_thick)[1],
                #                      xy1=laygen.get_inst_pin_xy(ihtree_in.name, 'VSS_' + str(i) + '_' + str(j), rg_m6m7_thick)[1],
                #                      track_y=laygen.get_inst_pin_xy(ihtree_in.name, 'VSS_' + str(i) + '_' + str(j), rg_m6m7_thick)[0][1],
                #                      gridname0=rg_m5m6_thick, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7_thick)
            for j in range(num_input_track):
                inp_xy_m9 = laygen.get_inst_pin_xy(ihtree_in.name, 'WPI_' + str(j), rg_m8m9_thick)
                inm_xy_m9 = laygen.get_inst_pin_xy(ihtree_in.name, 'WNI_' + str(num_input_shield_track+num_input_track+j), rg_m8m9_thick)
                laygen.pin('INP_'+str(j), xy=inp_xy_m9, layer=laygen.layers['pin'][9], gridname=rg_m8m9_thick, netname='INP')
                laygen.pin('INM_' + str(j), xy=inm_xy_m9, layer=laygen.layers['pin'][9], gridname=rg_m8m9_thick, netname='INM')


    if use_sf == True:
        # SF_bypass route
        bypass_sar = pdict_m4m5[isar.name]['SF_bypass'][0]
        rh0, rbyp = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                        xy0=bypass_sar,
                        xy1=np.array([bypass_sar[0]-2, 0]),
                        # xy1=np.array([laygen.get_inst_pin_xy(irdac.name, 'SEL<'+str(num_hori*num_vert*rdac_num_bits-1)+'>', rg_m4m5)[0][0]+4, 0]),
                        gridname0=rg_m4m5)
        laygen.boundary_pin_from_rect(rbyp, rg_m4m5, 'SF_bypass', layer=laygen.layers['pin'][5], direction='bottom', size=4)

    if vref_sf == True:
        # VREF_SF_bypass route
        bypass_sar = pdict_m4m5[isar.name]['VREF_SF_bypass'][0]
        rh0, rbyp = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                        xy0=bypass_sar,
                        xy1=np.array([bypass_sar[0], 0]),
                        gridname0=rg_m4m5)
        laygen.boundary_pin_from_rect(rbyp, rg_m4m5, 'VREF_SF_bypass', layer=laygen.layers['pin'][5], direction='bottom', size=4)

    # RDAC routing
    if use_sf == True and vref_sf == True:
        for i in range(num_slices):
            laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                            xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(i) + '>', rg_m5m6_thick_basic)[0],
                            xy1=laygen.get_inst_pin_xy(isar.name, 'SF_Voffp' + str(i), rg_m5m6_thick_basic)[0],
                            gridname0=rg_m5m6_thick_basic)
            laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                            xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices+i) + '>', rg_m5m6_thick_basic)[0],
                            xy1=laygen.get_inst_pin_xy(isar.name, 'SF_Voffn' + str(i), rg_m5m6_thick_basic)[0],
                            gridname0=rg_m5m6_thick_basic)
            # laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
            #                 xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices*2+i) + '>', rg_m5m6_thick_basic)[0],
            #                 xy1=np.array([laygen.get_inst_pin_xy(isar.name, 'SF_Voffp' + str(i), rg_m5m6_thick_basic)[0][0]-1,
            #                               laygen.get_inst_pin_xy(isar.name, 'samp_body' + str(i)+'_M6', rg_m5m6_thick_basic)[0][1]]),
            #                 gridname0=rg_m5m6_thick_basic, gridname1=rg_m5m6_thick_basic)
            # laygen.via(None,np.array([laygen.get_inst_pin_xy(isar.name, 'SF_Voffp' + str(i), rg_m5m6_thick)[0][0]-1,
            #                           laygen.get_inst_pin_xy(isar.name, 'samp_body' + str(i)+'_M6', rg_m5m6_thick)[0][1]]), rg_m5m6_thick)
            laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                            xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_vert*num_hori-1) + '>', rg_m5m6_thick)[0],
                            xy1=laygen.get_inst_pin_xy(isar.name, 'VREF_SF_BIAS' + str(i), rg_m5m6_thick)[0],
                            gridname0=rg_m5m6_thick)
            laygen.route(None, laygen.layers['metal'][6],
                         xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices * 2) + '>', rg_m5m6_thick)[0],
                         xy1=laygen.get_inst_pin_xy(isar.name, 'SF_BIAS' + str(i), rg_m5m6_thick)[0],
                         gridname0=rg_m5m6_thick)  # connect all SF_BIAS
    elif use_offset == True:
        for i in range(num_slices):
            laygen.route_hvh(layerh0=laygen.layers['metal'][6], layerv=laygen.layers['metal'][5],
                             xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(i) + '>', rg_m5m6)[0],
                             xy1=laygen.get_inst_pin_xy(isar.name, 'OSP' + str(i), rg_m5m6)[0],
                             track_x=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(i) + '>', rg_m5m6)[1][0] + 2*i + 2,
                             gridname0=rg_m5m6, layerh1=laygen.layers['metal'][6], gridname1=rg_m5m6)
            laygen.route_hvh(layerh0=laygen.layers['metal'][6], layerv=laygen.layers['metal'][5],
                             xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices+i) + '>', rg_m5m6)[0],
                             xy1=laygen.get_inst_pin_xy(isar.name, 'OSM' + str(i), rg_m5m6)[0],
                             track_x=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices+i) + '>', rg_m5m6)[1][0] + 2 * (i + num_slices) + 2,
                             gridname0=rg_m5m6, layerh1=laygen.layers['metal'][6], gridname1=rg_m5m6)

    # CLKCAL routing extend
    x_clkcal_m4 = laygen.get_template_size('tisaradc_body_space', gridname=rg_m2m3_pin, libname=workinglib)[0] + \
                  laygen.get_inst_pin_xy(isar.name, 'CLKCAL0<0>', rg_m2m3_pin)[0][0]
    y_ref_m4 = laygen.get_template_size('tisaradc_body_space', gridname=rg_m2m3_pin, libname=workinglib)[1]
    for i in range(num_slices):
        for j in range(5):
            laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2],
                            xy0=laygen.get_inst_pin_xy(isar.name, 'CLKCAL' + str(i) + '<' + str(j) + '>', rg_m2m3_pin)[0] - np.array([i*5+j, 0]),
                            xy1=np.array([x_clkcal_m4, y_ref_m4 + i*5+j]),
                            gridname0=rg_m2m3_pin, gridname1=rg_m2m3_pin, via0=[0,0])

    # Input pins
    if input_htree == True:
        htree_template = laygen.templates.get_template(htree_name, sar_libname)
        htree_pins = htree_template.pins
        htree_xy=ihtree_in.xy
        for pn, p in htree_pins.items():
            pin_prefix_list = ['INP', 'INM']
            for pn, p in htree_pins.items():
                for pfix in pin_prefix_list:
                    if pn.startswith(pfix):
                        laygen.add_pin(pn, htree_pins[pn]['netname'], htree_xy + htree_pins[pn]['xy'], htree_pins[pn]['layer'])

    # TIADC pins
    sar_template = laygen.templates.get_template(sar_name, sar_libname)
    sar_pins = sar_template.pins
    # for i in range(num_slices):
    #     for j in range(num_bits):
    #         pxy = laygen.get_inst_pin_xy(isar.name, 'ADCOUT%d<%d>'%(i,j), rg_m4m5)
    #         rout = laygen.route(None, laygen.layers['metal'][5], pxy[0], [pxy[0][0], 0], rg_m4m5)
    #         laygen.boundary_pin_from_rect(rout, rg_m4m5, 'ADCO%d<%d>'%(i,j), layer=laygen.layers['pin'][5], direction='bottom', size=4)
    #     pxy = laygen.get_inst_pin_xy(isar.name, 'CLKO0%d' % (i), rg_m4m5)
    #     refxy = laygen.get_inst_pin_xy(isar.name, 'ADCOUT%d<0>'%(i), rg_m4m5)
    #     rv0, rh0, rout = laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
    #         xy0=pxy[0], xy1=[refxy[0][0]-3, 0], track_y=pxy[0][1]+2, gridname0=rg_m4m5)
    #     laygen.boundary_pin_from_rect(rout, rg_m4m5, 'CLKO%d' % (i), layer=laygen.layers['pin'][5], direction='bottom', size=4)
    for pn, p in sar_pins.items():
        pin_prefix_list = ['INP', 'INM', 'VREF', 'ASCLKD', 'EXTSEL_CLK', 'ADCOUT', 'CLKOUT_DES', 'CLKCAL', 'RSTP',
                           'RSTN', 'CLKIP', 'CLKIN', 'VDD', 'VSS', 'MODESEL']
        # if use_sf == False:
        #     pin_prefix_list.remove('SF_bypass')
        if clkgen_mode == False:
            pin_prefix_list.remove('MODESEL')
        if input_htree == True:
            pin_prefix_list.remove('INP')
            pin_prefix_list.remove('INM')
        for pn, p in sar_pins.items():
            for pfix in pin_prefix_list:
                if pn.startswith(pfix):
                    if not pn.startswith('VREF_'):
                        laygen.add_pin(pn, sar_pins[pn]['netname'], sar_xy + sar_pins[pn]['xy'], sar_pins[pn]['layer'])
        # if pn.startswith('ADCOUT'):
        #     pxy = laygen.get_inst_pin_xy(isar.name, pn, rg_m3m4)
        #     rout = laygen.route(None, laygen.layers['metal'][3], pxy[0], [pxy[0][0], 0], rg_m3m4)
        #     laygen.boundary_pin_from_rect(rout, rg_m3m4, pn, layer=laygen.layers['pin'][3],
        #                                   direction='bottom', size=4)
        # if pn.startswith('CLKOUT'):
        #     pxy = laygen.get_inst_pin_xy(isar.name, pn, rg_m4m5)
        #     rout = laygen.route(None, laygen.layers['metal'][5], pxy[0], [pxy[0][0], 0], rg_m4m5)
        #     laygen.boundary_pin_from_rect(rout, rg_m4m5, pn, layer=laygen.layers['pin'][5],
        #                                   direction='bottom', size=4)
        # if pn.startswith('ASCLKD'):
        #     pxy=laygen.get_inst_pin_xy(isar.name, pn, rg_m4m5)
        #     rout = laygen.route(None, laygen.layers['metal'][5], pxy[0], [pxy[0][0], 0], rg_m4m5)
        #     laygen.boundary_pin_from_rect(rout, rg_m4m5, pn, layer=laygen.layers['pin'][5],
        #                               direction='bottom', size=4)
        # if pn.startswith('EXTSEL_'):
        #     pxy=laygen.get_inst_pin_xy(isar.name, pn, rg_m4m5)
        #     rout = laygen.route(None, laygen.layers['metal'][5], pxy[0], [pxy[0][0], 0], rg_m4m5)
        #     laygen.boundary_pin_from_rect(rout, rg_m4m5, pn, layer=laygen.layers['pin'][5],
        #                               direction='bottom', size=4)
        # if pn.startswith('VREF<'):
        #     pxy=laygen.get_inst_pin_xy(isar.name, pn, rg_m5m6_thick)
        #     laygen.pin(pn, layer=sar_pins[pn]['layer'], xy=pxy, gridname=rg_m5m6_thick, netname=pn.split("_")[0])

    # RDAC control pins
    rdac_template = laygen.templates.get_template(rdac_name, rdac_libname)
    rdac_pins = rdac_template.pins
    for pn, p in rdac_pins.items():
        if pn.startswith('SEL<'):
            pxy = laygen.get_inst_pin_xy(irdac.name, pn, rg_m5m6)
            laygen.pin('RDAC_'+pn, layer=rdac_pins[pn]['layer'], xy=pxy, gridname=rg_m5m6)

def generate_TISARADC_wodac(laygen, objectname_pfix, sar_libname, rdac_libname, space_1x_libname,
                             sar_name, rdac_name, space_1x_name, placement_grid,
                                routing_grid_m3m4, routing_grid_m4m5, routing_grid_m4m5_basic_thick, routing_grid_m5m6, routing_grid_m5m6_thick,
                                routing_grid_m5m6_basic_thick, routing_grid_m5m6_thick_basic,
                                routing_grid_m6m7_thick, routing_grid_m7m8_thick,
                                num_inv_bb, num_bits=9, num_slices=8, clk_pulse=True, slice_order=[0, 1], trackm=4, origin=np.array([0, 0])):
    """generate sar array """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_basic_thick = routing_grid_m5m6_basic_thick
    rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic
    rg_m6m7_thick = routing_grid_m6m7_thick
    rg_m7m8_thick = routing_grid_m7m8_thick

    # placement
    # sar
    # sar_slice_size = laygen.templates.get_template(sar_slice_name, libname=sar_libname).size
    bnd_size = laygen.get_template('boundary_bottom', libname=utemplib).size
    sar_slice_size = laygen.get_template_size(sar_slice_name, pg, libname=sar_libname)
    rdac_xy = laygen.templates.get_template(rdac_name, libname=rdac_libname).xy
    rdac_off_x = laygen.grids.get_absgrid_x(pg, rdac_xy[1][0])
    num_input_shield_track = 0 # defined in tisar_htree_diff_m7m8, to be parameterized
    if not num_input_shield_track == 0:
        htree_off_y = laygen.get_template_pin_xy(htree_name, 'VSS_0_0', rg_m7m8_thick, libname=workinglib)[0][1]-2
        if num_input_shield_track == 2:
            htree_off_x = laygen.get_template_pin_xy(htree_name, 'VSS_0_0', rg_m7m8_thick, libname=workinglib)[0][0]/2 + \
                          laygen.get_template_pin_xy(htree_name, 'VSS_0_1', rg_m7m8_thick, libname=workinglib)[0][0]/2 - \
                          int(laygen.get_template_size(sar_slice_name, rg_m7m8_thick, libname=workinglib)[0]/2*5)
        elif num_input_shield_track == 1:
            htree_off_x = laygen.get_template_pin_xy(htree_name, 'VSS_0_0', rg_m7m8_thick, libname=workinglib)[0][0] - \
                          int(laygen.get_template_size(sar_slice_name, rg_m7m8_thick, libname=workinglib)[0]/2*5+0.5)
    else:
        htree_off_y = laygen.get_template_pin_xy(htree_name, 'WNO_0_0', rg_m7m8_thick, libname=workinglib)[0][1]-2
        htree_off_x = int(laygen.get_template_pin_xy(htree_name, 'WNO_0_0', rg_m7m8_thick, libname=workinglib)[0][0] / 2 + \
                      laygen.get_template_pin_xy(htree_name, 'WPO_0_0', rg_m7m8_thick, libname=workinglib)[0][0] / 2 - \
                      laygen.get_template_size(sar_slice_name, rg_m7m8_thick, libname=workinglib)[0] / 2 * 5 + 0.5)-1

    # sar_xy = origin + (laygen.get_template_size(rdac_name, gridname=pg, libname=rdac_libname)*np.array([1,0]) )
    sar_xy = origin
    isar = laygen.relplace(name="I" + objectname_pfix + 'SAR0', templatename=sar_name,
                      gridname=pg, xy=sar_xy, template_libname=sar_libname)
    if input_htree == True:
        ihtree_in = laygen.relplace(name="I" + objectname_pfix + 'HTREE0', templatename=htree_name,
                          gridname=rg_m7m8_thick, transform='MX', xy=[-htree_off_x, htree_off_y],
                          template_libname=workinglib)

    sar_template = laygen.templates.get_template(sar_name, sar_libname)
    sar_pins=sar_template.pins
    sar_xy=isar.xy

    #prboundary
    # sar_size = laygen.templates.get_template(sar_name, libname=sar_libname).size
    space_size = laygen.templates.get_template('boundary_bottom', libname=utemplib).size
    size_x=isar.xy[0]+isar.size[0]
    size_y=isar.xy[1]+isar.size[1]
    laygen.add_rect(None, np.array([origin, origin+np.array([size_x, size_y])]), laygen.layers['prbnd'])

    # Routing

    pdict_m2m3=laygen.get_inst_pin_xy(None, None, rg_m2m3)
    pdict_m3m4=laygen.get_inst_pin_xy(None, None, rg_m3m4)
    pdict_m4m5=laygen.get_inst_pin_xy(None, None, rg_m4m5)
    pdict_m4m5_basic_thick=laygen.get_inst_pin_xy(None, None, rg_m4m5_basic_thick)
    pdict_m5m6=laygen.get_inst_pin_xy(None, None, rg_m5m6)
    pdict_m5m6_thick=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    pdict_m6m7_thick=laygen.get_inst_pin_xy(None, None, rg_m6m7_thick)
    pdict_m7m8_thick=laygen.get_inst_pin_xy(None, None, rg_m7m8_thick)
    pdict_m5m6_thick_basic=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick_basic)

    # ADC input route
    if input_htree == True:
        rinp_m7=[]
        rinm_m7=[]
        num_input_track = htree_trackm
        if htree_metal_v == 7:
            for i in range(num_slices):
                inp_xy_m5 = pdict_m5m6_thick[isar.name]['INP%d' % i][1]
                inm_xy_m5 = pdict_m5m6_thick[isar.name]['INM%d' % i][1]
                for j in range(num_input_track):
                    inp_xy_m7 = laygen.get_inst_pin_xy(ihtree_in.name, 'WPO_' + str(slice_order.index(i)) + '_' + str(j), rg_m6m7_thick)[1]
                    inm_xy_m7 = laygen.get_inst_pin_xy(ihtree_in.name, 'WNO_' + str(slice_order.index(i)) + '_' + str(j), rg_m6m7_thick)[1]
                    laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                                 xy0=inp_xy_m5, xy1=inp_xy_m7, track_y=inp_xy_m5[1]-3,
                                 gridname0=rg_m5m6_thick, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7_thick)
                    laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                                     xy0=inm_xy_m5, xy1=inm_xy_m7, track_y=inm_xy_m5[1]-2,
                                     gridname0=rg_m5m6_thick, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7_thick)
            for j in range(num_input_track):
                inp_xy_m7 = laygen.get_inst_pin_xy(ihtree_in.name, 'WPI_' + str(j), rg_m6m7_thick)
                inm_xy_m7 = laygen.get_inst_pin_xy(ihtree_in.name, 'WNI_' + str(num_input_shield_track+num_input_track+j), rg_m6m7_thick)
                laygen.pin('INP_'+str(j), xy=inp_xy_m7, layer=laygen.layers['pin'][7], gridname=rg_m6m7_thick, netname='INP')
                laygen.pin('INM_' + str(j), xy=inm_xy_m7, layer=laygen.layers['pin'][7], gridname=rg_m6m7_thick, netname='INM')

        elif htree_metal_v == 9:
            for i in range(num_slices):
                inp_xy_m5 = pdict_m5m6_thick[isar.name]['INP%d' % i][1]
                inm_xy_m5 = pdict_m5m6_thick[isar.name]['INM%d' % i][1]
                inp_xy_m7 = pdict_m7m8_thick[isar.name]['INP%d' % i][1]
                inm_xy_m7 = pdict_m7m8_thick[isar.name]['INM%d' % i][1]
                m8_ref_y = pdict_m7m8_thick[isar.name]['VDDSAMP_SAMP_M8_0'][1][1]
                for j in range(num_input_track):
                    inp_xy_m9 = laygen.get_inst_pin_xy(ihtree_in.name, 'WPO_' + str(slice_order.index(i)) + '_' + str(j), rg_m8m9_thick)[1]
                    inm_xy_m9 = laygen.get_inst_pin_xy(ihtree_in.name, 'WNO_' + str(slice_order.index(i)) + '_' + str(j), rg_m8m9_thick)[1]
                    rv0, rh0, rv1 = laygen.route_vhv(layerv0=laygen.layers['metal'][7], layerh=laygen.layers['metal'][8],
                                 xy0=inp_xy_m7, xy1=inp_xy_m9, track_y=m8_ref_y-3,
                                 gridname0=rg_m7m8_thick, layerv1=laygen.layers['metal'][9], gridname1=rg_m8m9_thick)
                    rh_m8 = laygen.route(None, laygen.layers['metal'][8], np.array([inp_xy_m7[0]-2, m8_ref_y-3]), np.array([inp_xy_m7[0]+2, m8_ref_y-3]), rg_m7m8_thick)
                    xy = laygen.get_rect_xy(rv0.name, rg_m6m7_thick)[0]
                    laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                                 xy0=inp_xy_m5, xy1=xy, track_y=inp_xy_m5[1]+6,
                                 gridname0=rg_m5m6_thick, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7_thick)

                    rv0, rh0, rv1 = laygen.route_vhv(layerv0=laygen.layers['metal'][7], layerh=laygen.layers['metal'][8],
                                     xy0=inm_xy_m7, xy1=inm_xy_m9, track_y=m8_ref_y-2,
                                     gridname0=rg_m7m8_thick, layerv1=laygen.layers['metal'][9], gridname1=rg_m8m9_thick)
                    rh_m8 = laygen.route(None, laygen.layers['metal'][8], np.array([inm_xy_m7[0]-2, m8_ref_y-2]), np.array([inm_xy_m7[0]+2, m8_ref_y-2]), rg_m7m8_thick)
                    xy = laygen.get_rect_xy(rv0.name, rg_m6m7_thick)[0]
                    laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                                 xy0=inm_xy_m5, xy1=xy, track_y=inm_xy_m5[1]+7,
                                 gridname0=rg_m5m6_thick, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7_thick)
            for j in range(num_input_track):
                inp_xy_m9 = laygen.get_inst_pin_xy(ihtree_in.name, 'WPI_' + str(j), rg_m8m9_thick)
                inm_xy_m9 = laygen.get_inst_pin_xy(ihtree_in.name, 'WNI_' + str(num_input_shield_track+num_input_track+j), rg_m8m9_thick)
                laygen.pin('INP_'+str(j), xy=inp_xy_m9, layer=laygen.layers['pin'][9], gridname=rg_m8m9_thick, netname='INP')
                laygen.pin('INM_' + str(j), xy=inm_xy_m9, layer=laygen.layers['pin'][9], gridname=rg_m8m9_thick, netname='INM')


    if use_sf == True:
        # SF_bypass route
        bypass_sar = pdict_m4m5[isar.name]['SF_bypass'][0]
        rh0, rbyp = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                        xy0=bypass_sar,
                        xy1=np.array([bypass_sar[0]-2, 0]),
                        gridname0=rg_m4m5)
        laygen.boundary_pin_from_rect(rbyp, rg_m4m5, 'SF_bypass', layer=laygen.layers['pin'][5], direction='bottom', size=4)

    if vref_sf == True:
        # VREF_SF_bypass route
        bypass_sar = pdict_m4m5[isar.name]['VREF_SF_bypass'][0]
        rh0, rbyp = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                        xy0=bypass_sar,
                        xy1=np.array([bypass_sar[0], 0]),
                        gridname0=rg_m4m5)
        laygen.boundary_pin_from_rect(rbyp, rg_m4m5, 'VREF_SF_bypass', layer=laygen.layers['pin'][5], direction='bottom', size=4)

    # RDAC routing
    if use_sf == True and vref_sf == True:
        for i in range(num_slices):
            _pin = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                            xy0=laygen.get_template_pin_xy(rdac_name, 'out<' + str(i) + '>', rg_m5m6_thick_basic,
                                                           libname=rdac_libname)[0]*np.array([0, 1]),
                            xy1=laygen.get_inst_pin_xy(isar.name, 'SF_Voffp' + str(i), rg_m5m6_thick_basic)[0],
                            gridname0=rg_m5m6_thick_basic)[0]  #get horizontal wires
            _pinname = 'RDAC_OUT<%d>' % i
            laygen.boundary_pin_from_rect(_pin, rg_m5m6_thick_basic, name=_pinname, layer=laygen.layers['pin'][6],
                                          size=4, direction='left', netname=_pinname)

            _pin = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                            xy0=laygen.get_template_pin_xy(rdac_name, 'out<' + str(num_slices+i) + '>',
                                                           rg_m5m6_thick_basic, libname=rdac_libname)[0]*np.array([0,1]),
                            xy1=laygen.get_inst_pin_xy(isar.name, 'SF_Voffn' + str(i), rg_m5m6_thick_basic)[0],
                            gridname0=rg_m5m6_thick_basic)[0]
            _pinname = 'RDAC_OUT<%d>' % (num_slices+i)
            laygen.boundary_pin_from_rect(_pin, rg_m5m6_thick_basic, name=_pinname, layer=laygen.layers['pin'][6],
                                          size=4, direction='left', netname=_pinname)

            _pin = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                            xy0=laygen.get_template_pin_xy(rdac_name, 'out<' + str(num_vert*num_hori-1) + '>',
                                                           rg_m5m6_thick, libname=rdac_libname)[0]*np.array([0, 1]),
                            xy1=laygen.get_inst_pin_xy(isar.name, 'VREF_SF_BIAS' + str(i), rg_m5m6_thick)[0],
                            gridname0=rg_m5m6_thick)[0]
            _pinname = 'RDAC_OUT<%d>' % (num_vert*num_hori-1)
            laygen.boundary_pin_from_rect(_pin, rg_m5m6_thick, name=_pinname, layer=laygen.layers['pin'][6],
                                          size=4, direction='left', netname=_pinname)

            _pin = laygen.route(None, laygen.layers['metal'][6],
                         xy0=laygen.get_template_pin_xy(rdac_name, 'out<' + str(num_slices * 2) + '>', rg_m5m6_thick,
                                                        libname=rdac_libname)[0]*np.array([0, 1]),
                         xy1=laygen.get_inst_pin_xy(isar.name, 'SF_BIAS' + str(i), rg_m5m6_thick)[0],
                         gridname0=rg_m5m6_thick)  # connect all SF_BIAS
            _pinname = 'RDAC_OUT<%d>' % (num_slices * 2)
            laygen.boundary_pin_from_rect(_pin, rg_m5m6_thick, name=_pinname, layer=laygen.layers['pin'][6],
                                          size=4, direction='left', netname=_pinname)

    elif use_offset == True:
        for i in range(num_slices):
            _pin = laygen.route_hvh(layerh0=laygen.layers['metal'][6], layerv=laygen.layers['metal'][5],
                             xy0=laygen.get_template_pin_xy(rdac_name, 'out<' + str(i) + '>', rg_m5m6,
                                                        libname=rdac_libname)[0]*np.array([0,1]),
                             xy1=laygen.get_inst_pin_xy(isar.name, 'OSP' + str(i), rg_m5m6)[0],
                             track_x=laygen.get_template_pin_xy(rdac_name, 'out<' + str(i) + '>', rg_m5m6,
                                                                libname=rdac_libname)[1][0] + 2*i + 2,
                             gridname0=rg_m5m6, layerh1=laygen.layers['metal'][6], gridname1=rg_m5m6)[0]
            _pinname = 'RDAC_OUT<%d>' % i
            laygen.boundary_pin_from_rect(_pin, rg_m5m6_thick_basic, name=_pinname, layer=laygen.layers['pin'][6],
                                          size=4, direction='left', netname=_pinname)

            _pin = laygen.route_hvh(layerh0=laygen.layers['metal'][6], layerv=laygen.layers['metal'][5],
                             xy0=laygen.get_template_pin_xy(rdac_name, 'out<' + str(num_slices+i) + '>', rg_m5m6,
                                                            libname=rdac_libname)[0]*np.array([0,1]),
                             xy1=laygen.get_inst_pin_xy(isar.name, 'OSM' + str(i), rg_m5m6)[0],
                             track_x=laygen.get_template_pin_xy(rdac_name, 'out<' + str(num_slices+i) + '>', rg_m5m6,
                                                                libname=rdac_libname)[1][0] + 2 * (i + num_slices) + 2,
                             gridname0=rg_m5m6, layerh1=laygen.layers['metal'][6], gridname1=rg_m5m6)[0]
            _pinname = 'RDAC_OUT<%d>' % (num_slices+i)
            laygen.boundary_pin_from_rect(_pin, rg_m5m6_thick_basic, name=_pinname, layer=laygen.layers['pin'][6],
                                      size=4, direction='left', netname=_pinname)

    # CLKCAL routing extend
    x_clkcal_m4 = laygen.get_template_size('tisaradc_body_space', gridname=rg_m2m3_pin, libname=workinglib)[0] + \
                  laygen.get_inst_pin_xy(isar.name, 'CLKCAL0<0>', rg_m2m3_pin)[0][0]
    y_ref_m4 = laygen.get_template_size('tisaradc_body_space', gridname=rg_m2m3_pin, libname=workinglib)[1]
    for i in range(num_slices):
        for j in range(5):
            laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2],
                            xy0=laygen.get_inst_pin_xy(isar.name, 'CLKCAL' + str(i) + '<' + str(j) + '>', rg_m2m3_pin)[0] - np.array([i*5+j, 0]),
                            xy1=np.array([x_clkcal_m4, y_ref_m4 + i*5+j]),
                            gridname0=rg_m2m3_pin, gridname1=rg_m2m3_pin, via0=[0,0])

    # Input pins
    if input_htree == True:
        htree_template = laygen.templates.get_template(htree_name, sar_libname)
        htree_pins = htree_template.pins
        htree_xy=ihtree_in.xy
        for pn, p in htree_pins.items():
            pin_prefix_list = ['INP', 'INM']
            for pn, p in htree_pins.items():
                for pfix in pin_prefix_list:
                    if pn.startswith(pfix):
                        laygen.add_pin(pn, htree_pins[pn]['netname'], htree_xy + htree_pins[pn]['xy'], htree_pins[pn]['layer'])

    # TIADC pins
    sar_template = laygen.templates.get_template(sar_name, sar_libname)
    sar_pins = sar_template.pins

    for pn, p in sar_pins.items():
        pin_prefix_list = ['INP', 'INM', 'VREF', 'ASCLKD', 'EXTSEL_CLK', 'ADCOUT', 'CLKOUT_DES', 'CLKCAL', 'RSTP',
                           'RSTN', 'CLKIP', 'CLKIN', 'VDD', 'VSS', 'MODESEL']
        if clkgen_mode == False:
            pin_prefix_list.remove('MODESEL')
        if input_htree == True:
            pin_prefix_list.remove('INP')
            pin_prefix_list.remove('INM')
        for pn, p in sar_pins.items():
            for pfix in pin_prefix_list:
                if pn.startswith(pfix):
                    if not pn.startswith('VREF_'):
                        laygen.add_pin(pn, sar_pins[pn]['netname'], sar_xy + sar_pins[pn]['xy'], sar_pins[pn]['layer'])


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
    ret_libname = 'adc_sar_generated'
    clkdist_libname = 'clk_dis_generated'
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
    rg_m3m4_thick = 'route_M3_M4_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m4m5_basic_thick = 'route_M4_M5_basic_thick'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m5m6_basic_thick = 'route_M5_M6_basic_thick'
    rg_m5m6_thick_basic = 'route_M5_M6_thick_basic'
    rg_m5m6_thick2_thick = 'route_M5_M6_thick2_thick'
    rg_m6m7_thick = 'route_M6_M7_thick'
    rg_m6m7_basic_thick = 'route_M6_M7_basic_thick'
    rg_m6m7_thick2_thick = 'route_M6_M7_thick2_thick'
    rg_m7m8_thick = 'route_M7_M8_thick'
    rg_m8m9_thick = 'route_M8_M9_thick'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    mycell_list = []
    num_bits=9
    num_slices=9
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
        num_slices=specdict['n_interleave']
        num_inv_bb=sizedict['sarlogic']['num_inv_bb']
        rdac_num_bits=sizedict['r2rdac']['num_bits']
        num_hori=sizedict['r2rdac_array']['num_hori']
        num_vert=sizedict['r2rdac_array']['num_vert']
        trackm=sizedict['clk_dis_htree']['m_track']
        slice_order=sizedict['slice_order']
        clk_pulse=specdict['clk_pulse_overlap']
        use_sf = specdict['use_sf']
        vref_sf = specdict['use_vref_sf']
        use_offset = specdict['use_offset']
        input_htree = specdict['input_htree']
        if input_htree == True:
            htree_metal_v=sizedict['input_htree']['metal_v']
            htree_metal_h=sizedict['input_htree']['metal_h']
            htree_trackm=sizedict['input_htree']['trackm']
        clkgen_mode = sizedict['sarclkgen']['mux_fast']
        generate_dac = specdict['generate_dac']

    cellname = 'TISARADC'
    sar_name = 'tisaradc_body'
    sar_slice_name = 'sar_wsamp'
    rdac_name = 'r2r_dac_array'
    htree_name = 'tisar_htree_diff'
    #tisar_space_name = 'tisaradc_body_space'
    space_1x_name = 'space_1x'
     

    #sar generation
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)

    if not generate_dac:
        generate_TISARADC_wodac(laygen, objectname_pfix='TISAR0',
                    sar_libname=workinglib, rdac_libname=workinglib, space_1x_libname=logictemplib,
                    sar_name=sar_name, rdac_name=rdac_name, space_1x_name=space_1x_name,
                    placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5, routing_grid_m4m5_basic_thick=rg_m4m5_basic_thick,
                    routing_grid_m5m6=rg_m5m6,
                    routing_grid_m5m6_thick=rg_m5m6_thick, routing_grid_m5m6_basic_thick=rg_m5m6_basic_thick,
                    routing_grid_m5m6_thick_basic=rg_m5m6_thick_basic,
                    routing_grid_m6m7_thick=rg_m6m7_thick, routing_grid_m7m8_thick=rg_m7m8_thick,
                    num_inv_bb=num_inv_bb, num_bits=num_bits, num_slices=num_slices, clk_pulse=clk_pulse, slice_order=slice_order, trackm=trackm, origin=np.array([0, 0]))
    else:
        generate_TISARADC(laygen, objectname_pfix='TISAR0',
                    sar_libname=workinglib, rdac_libname=workinglib, space_1x_libname=logictemplib,
                    sar_name=sar_name, rdac_name=rdac_name, space_1x_name=space_1x_name,
                    placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5, routing_grid_m4m5_basic_thick=rg_m4m5_basic_thick,
                    routing_grid_m5m6=rg_m5m6,
                    routing_grid_m5m6_thick=rg_m5m6_thick, routing_grid_m5m6_basic_thick=rg_m5m6_basic_thick,
                    routing_grid_m5m6_thick_basic=rg_m5m6_thick_basic,
                    routing_grid_m6m7_thick=rg_m6m7_thick, routing_grid_m7m8_thick=rg_m7m8_thick,
                    num_inv_bb=num_inv_bb, num_bits=num_bits, num_slices=num_slices, clk_pulse=clk_pulse, slice_order=slice_order, trackm=trackm, origin=np.array([0, 0]))
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

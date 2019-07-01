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

def generate_tisaradc_body(laygen, objectname_pfix, libname, tisar_core_name, tisar_space_name, tisar_space2_name, 
                           placement_grid,
                           routing_grid_m3m4, routing_grid_m4m5, routing_grid_m4m5_basic_thick, routing_grid_m5m6, routing_grid_m5m6_thick, 
                           routing_grid_m5m6_thick_basic, routing_grid_m6m7_thick, routing_grid_m7m8_thick, 
                           num_bits=9, num_slices=8, origin=np.array([0, 0])):
    """generate sar array """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic
    rg_m6m7_thick = routing_grid_m6m7_thick
    rg_m7m8_thick = routing_grid_m7m8_thick

    # placement
    ispace20 = laygen.place(name="I" + objectname_pfix + 'SP20', templatename=tisar_space2_name,
                      gridname=pg, xy=origin, template_libname=libname)
    space20_template = laygen.templates.get_template(tisar_space2_name, libname)
    space20_pins=space20_template.pins
    space20_xy=ispace20.xy
    space0_origin = laygen.get_template_size(ispace20.cellname, gridname=pg, libname=workinglib)*np.array([1, 0])
    ispace0 = laygen.place(name="I" + objectname_pfix + 'SP0', templatename=tisar_space_name,
                      gridname=pg, xy=space0_origin, template_libname=libname)
    space_template = laygen.templates.get_template(tisar_space_name, libname)
    space_pins=space_template.pins
    space0_xy=ispace0.xy
    sar_origin = space0_origin + laygen.get_template_size(ispace0.cellname, gridname=pg, libname=workinglib)*np.array([1, 0])
    isar = laygen.place(name="I" + objectname_pfix + 'SAR0', templatename=tisar_core_name,
                      gridname=pg, xy=sar_origin, template_libname=libname)
    sar_template = laygen.templates.get_template(tisar_core_name, libname)
    sar_pins=sar_template.pins
    sar_xy=isar.xy
    space1_origin = sar_origin + laygen.get_template_size(isar.cellname, gridname=pg, libname=workinglib)*np.array([1, 0])
    ispace1 = laygen.place(name="I" + objectname_pfix + 'SP1', templatename=tisar_space_name,
                      gridname=pg, xy=space1_origin, template_libname=libname)
    space1_xy=ispace1.xy
    space21_origin = space1_origin + laygen.get_template_size(ispace1.cellname, gridname=pg, libname=workinglib)*np.array([1, 0])
    ispace21 = laygen.place(name="I" + objectname_pfix + 'SP21', templatename=tisar_space2_name,
                      gridname=pg, xy=space21_origin, template_libname=libname)
    space21_xy=ispace21.xy

    #prboundary
    sar_size = laygen.templates.get_template(tisar_core_name, libname=libname).size
    space_size = laygen.templates.get_template(tisar_space_name, libname=libname).size
    space2_size = laygen.templates.get_template(tisar_space2_name, libname=libname).size

    #VDD/VSS/VREF integration 
    rvddclkd=[]
    rvddsamp=[]
    rvddsar=[]
    rvddsar_upper=[]
    rvref0=[]
    rvref1=[]
    rvref2=[]
    rvssclkd=[]
    rvsssamp=[]
    rvsssar=[]
    rvsssar_upper=[]
    vddsampcnt=0
    vddsarcnt=0
    y_vddsar_max=0
    y_vddsamp_min=500000
    y_vddsamp_max=0
    y_vddclkd_min=500000
    y_vref0=sar_pins['VREF0<0>']['xy'][0][1]
    #categorize vdd pins and fiugre out htresholds
    for pn, p in sar_pins.items():
        if pn.startswith('VDDCLKD'):
            pxy=np.array([[0, space0_xy[1]+sar_pins[pn]['xy'][0][1]], 
                          [space_size[0]*4+sar_size[0], space1_xy[1]+sar_pins[pn]['xy'][1][1]]])
            rvddclkd.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
            if pxy[1][1]<y_vddclkd_min:
                y_vddclkd_min=pxy[1][1]
        if pn.startswith('VDDSAMP'):
            pxy=np.array([[0, space0_xy[1]+sar_pins[pn]['xy'][0][1]], 
                          [space_size[0]*4+sar_size[0], space1_xy[1]+sar_pins[pn]['xy'][1][1]]])
            rvddsamp.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
            if pxy[1][1]<y_vddsamp_min:
                y_vddsamp_min=pxy[1][1]
            if pxy[1][1]>y_vddsamp_max:
                y_vddsamp_max=pxy[1][1]
        if pn.startswith('VDDSAR'):
            pxy=np.array([[0, space0_xy[1]+sar_pins[pn]['xy'][0][1]], 
                          [space_size[0]*4+sar_size[0], space1_xy[1]+sar_pins[pn]['xy'][1][1]]])
            if pxy[0][1] > y_vref0:
                rvddsar_upper.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
            else:
                rvddsar.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
            if pxy[1][1]>y_vddsar_max:
                y_vddsar_max=pxy[1][1]
        if pn.startswith('VREF'):
            pxy=np.array([[0, space0_xy[1]+sar_pins[pn]['xy'][0][1]], 
                          [space_size[0]*4+sar_size[0], space1_xy[1]+sar_pins[pn]['xy'][1][1]]])
            if pn.endswith('<0>'):
                rvref0.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
            if pn.endswith('<1>'):
                rvref1.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
            if pn.endswith('<2>'):
                rvref2.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
    y_vss_th=0.5*(y_vddsar_max+y_vddsamp_min) #find out threshold
    y_vss_th2=0.5*(y_vddsamp_max+y_vddclkd_min) #find out threshold
    for pn, p in sar_pins.items():
        if pn.startswith('VSS'):
            pxy=np.array([[0, space0_xy[1]+sar_pins[pn]['xy'][0][1]], 
                          [space_size[0]*4+sar_size[0], space1_xy[1]+sar_pins[pn]['xy'][1][1]]])
            if pxy[0][1] > y_vss_th2:
                rvssclkd.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
            elif pxy[0][1] > y_vss_th:
                rvsssamp.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
            elif pxy[0][1] > y_vref0:
                rvsssar_upper.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
            else:
                rvsssar.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
    #M7 rails
    rg_route='route_M6_M7_thick_temp_pwr'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m6m7_thick, gridname_output=rg_route,
                                          instname=[isar.name],
                                          inst_pin_prefix=['VDD', 'VSS', 'VREF'], xy_grid_type='ygrid')
    '''
    #M7 rails-clkd
    input_rails_rect = [rvddclkd, rvssclkd]
    rvddclkd_m7_pre, rvssclkd_m7_pre= laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_CLKD_M7_', 
                layer=laygen.layers['metal'][7], gridname=rg_route, netnames=['VDDCLKD', 'VSS'], direction='y', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, offset_end_coord=None,
                offset_start_index=2, offset_end_index=-2)
    '''
    #M7 rails-samp
    input_rails_rect = [rvddsamp, rvsssamp]
    rvddsamp_m7_pre, rvsssamp_m7_pre= laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_SAMP_M7_', 
                layer=laygen.layers['metal'][7], gridname=rg_route, netnames=['VDDSAMP', 'VSS'], direction='y', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, offset_end_coord=None,
                offset_start_index=2, offset_end_index=-2)
    #M7 rails-sar_lower
    input_rails_rect = [rvddsar, rvsssar]
    rvddsar_m7, rvsssar_m7= laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_SAR_M7_', 
                layer=laygen.layers['metal'][7], gridname=rg_route, netnames=['VDDSAR', 'VSS'], direction='y', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=2, offset_end_index=-2)
    #M7 rails-sar_upper(+vref)
    input_rails_rect = [rvddsar_upper, rvsssar_upper, rvref0, rvsssar_upper, rvref1, rvsssar_upper, rvref2, rvsssar_upper]
    rvddsar_m7_upper, rvsssar0_m7, rvref0_m7_pre, rvsssar1_m7, rvref1_m7_pre, rvsssar2_m7, rvref2_m7_pre, rvsssar3_m7= laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_SAR_UPPER_M7_', 
                layer=laygen.layers['metal'][7], gridname=rg_route, netnames=['VDDSAR', 'VSS', 'VREF<0>', 'VSS', 'VREF<1>', 'VSS', 'VREF<2>', 'VSS'], direction='y', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=2, offset_end_index=-2)
    rvsssar_m7_upper_pre=rvsssar0_m7+rvsssar1_m7+rvsssar2_m7+rvsssar3_m7
    #extend m7 rails for clkd and samp and vref, rvsssar_m7_upper
    #rvddclkd_m7=[]
    #rvssclkd_m7=[]
    rvddsamp_m7=[]
    rvsssamp_m7=[]
    rvref0_m7=[]
    rvref1_m7=[]
    rvref2_m7=[]
    rvsssar_m7_upper=[]
    '''
    for r in rvddclkd_m7_pre:
        rxy=laygen.get_rect_xy(r.name, gridname=rg_m6m7_thick, sort=True)
        rxy[1][1]+=12
        r2=laygen.route(None, laygen.layers['metal'][7], xy0=rxy[0], xy1=rxy[1], gridname0=rg_m6m7_thick)
        rvddclkd_m7.append(r2)
    for r in rvssclkd_m7_pre:
        rxy=laygen.get_rect_xy(r.name, gridname=rg_m6m7_thick, sort=True)
        rxy[1][1]+=12
        r2=laygen.route(None, laygen.layers['metal'][7], xy0=rxy[0], xy1=rxy[1], gridname0=rg_m6m7_thick)
        rvssclkd_m7.append(r2)
    '''
    for r in rvddsamp_m7_pre:
        rxy=laygen.get_rect_xy(r.name, gridname=rg_m6m7_thick, sort=True)
        #rxy[0][1]-=1
        rxy[1][1]+=24
        r2=laygen.route(None, laygen.layers['metal'][7], xy0=rxy[0], xy1=rxy[1], gridname0=rg_m6m7_thick)
        rvddsamp_m7.append(r2)
    for r in rvsssamp_m7_pre:
        rxy=laygen.get_rect_xy(r.name, gridname=rg_m6m7_thick, sort=True)
        #rxy[0][1]-=1
        rxy[1][1]+=24
        r2=laygen.route(None, laygen.layers['metal'][7], xy0=rxy[0], xy1=rxy[1], gridname0=rg_m6m7_thick)
        rvsssamp_m7.append(r2)
        #extend upper vss routes in the space area down to zero (for vss short)
        if r.xy[0][0]<sar_xy[0]:
            laygen.route(None, laygen.layers['metal'][7], xy0=[rxy[0][0], 0], xy1=rxy[1], gridname0=rg_m6m7_thick)
        if r.xy[0][0]>sar_xy[0]+sar_template.width:
            laygen.route(None, laygen.layers['metal'][7], xy0=[rxy[0][0], 0], xy1=rxy[1], gridname0=rg_m6m7_thick)
    for r in rvref0_m7_pre:
        rxy=laygen.get_rect_xy(r.name, gridname=rg_m6m7_thick, sort=True)
        rxy[0][1]-=24
        #rxy[1][1]+=24
        r2=laygen.route(None, laygen.layers['metal'][7], xy0=rxy[0], xy1=rxy[1], gridname0=rg_m6m7_thick)
        rvref0_m7.append(r2)
    for r in rvref1_m7_pre:
        rxy=laygen.get_rect_xy(r.name, gridname=rg_m6m7_thick, sort=True)
        rxy[0][1]-=24
        #rxy[1][1]+=24
        r2=laygen.route(None, laygen.layers['metal'][7], xy0=rxy[0], xy1=rxy[1], gridname0=rg_m6m7_thick)
        rvref1_m7.append(r2)
    for r in rvref2_m7_pre:
        rxy=laygen.get_rect_xy(r.name, gridname=rg_m6m7_thick, sort=True)
        rxy[0][1]-=24
        #rxy[1][1]+=24
        r2=laygen.route(None, laygen.layers['metal'][7], xy0=rxy[0], xy1=rxy[1], gridname0=rg_m6m7_thick)
        rvref2_m7.append(r2)
    for r in rvsssar_m7_upper_pre:
        rxy=laygen.get_rect_xy(r.name, gridname=rg_m6m7_thick, sort=True)
        rxy[0][1]-=24
        #rxy[1][1]+=24
        r2=laygen.route(None, laygen.layers['metal'][7], xy0=rxy[0], xy1=rxy[1], gridname0=rg_m6m7_thick)
        rvsssar_m7_upper.append(r2)
    #connect VDDSAR/VSS in sar region
    for r in rvddsar_m7_upper:
        rxy=laygen.get_rect_xy(r.name, gridname=rg_m6m7_thick, sort=True)
        rxy[0][1]=1
        r2=laygen.route(None, laygen.layers['metal'][7], xy0=rxy[0], xy1=rxy[1], gridname0=rg_m6m7_thick)
    for r in rvsssar_m7_upper:
        rxy=laygen.get_rect_xy(r.name, gridname=rg_m6m7_thick, sort=True)
        rxy[0][1]=1
        r2=laygen.route(None, laygen.layers['metal'][7], xy0=rxy[0], xy1=rxy[1], gridname0=rg_m6m7_thick)
  
    #connect VSS between sar/samp/clkd in space region
    '''
    for r in rvssclkd_m7:
        if r.xy[1][0] < sar_xy[0]:
            laygen.add_rect(None, np.array([[r.xy[0][0],rvsssar_m7[0].xy[0][1]], r.xy[1]]), laygen.layers['metal'][7])
        if r.xy[0][0] > space1_xy[0]:
            laygen.add_rect(None, np.array([[r.xy[0][0],rvsssar_m7[0].xy[0][1]], r.xy[1]]), laygen.layers['metal'][7])
    '''
    #create VSS pins for connection to core
    for i, r in enumerate(rvsssar_m7):
        pxy=np.array([[r.xy[0][0],0], r.xy[1]])
        laygen.add_rect(None, pxy, laygen.layers['metal'][7])
        laygen.add_pin('VSS_SAR_M7_'+str(i), 'VSS', pxy, laygen.layers['pin'][7])
    '''
    #connect VDDSAMP between samp/clkd in space region
    for r in rvddclkd_m7:
        if r.xy[1][0] < sar_xy[0]:
            laygen.add_rect(None, np.array([[r.xy[0][0],rvddsamp_m7[0].xy[0][1]], r.xy[1]]), laygen.layers['metal'][7])
        if r.xy[0][0] > space1_xy[0]:
            laygen.add_rect(None, np.array([[r.xy[0][0],rvddsamp_m7[0].xy[0][1]], r.xy[1]]), laygen.layers['metal'][7])
    #M8 routes
    #input_rails_rect = [rvddclkd_m7, rvssclkd_m7]
    #rvddclkd_m8, rvssclkd_m8= laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_CLKD_M8_', 
    #            layer=laygen.layers['pin'][8], gridname=rg_m7m8_thick, netnames=['VDDSAMP', 'VSS'], direction='x', 
    #            input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
    #            offset_start_index=1, offset_end_index=0)
    input_rails_rect = [rvssclkd_m7, rvddclkd_m7]
    rvssclkd_m8, rvddclkd_m8= laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_CLKD_M8_', 
                layer=laygen.layers['pin'][8], gridname=rg_m7m8_thick, netnames=['VSS', 'VDDSAMP'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=1, offset_end_index=0)
    '''
    #M8 routes
    input_rails_rect = [rvsssamp_m7, rvddsamp_m7]
    rvsssamp_m8, rvddsamp_m8= laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_SAMP_M8_', 
                layer=laygen.layers['pin'][8], gridname=rg_m7m8_thick, netnames=['VSS', 'VDDSAMP'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=1, offset_end_index=0)
    input_rails_rect = [rvddsar_m7, rvsssar_m7]
    rvddsar_m8, rvsssar_m8= laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_SAR_M8_', 
                layer=laygen.layers['pin'][8], gridname=rg_m7m8_thick, netnames=['VDDSAR', 'VSS'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    input_rails_rect = [rvref0_m7, rvsssar_m7_upper, rvref1_m7, rvsssar_m7_upper, rvref2_m7, rvsssar_m7_upper]
    laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_VREF_M8_', 
                layer=laygen.layers['metal'][8], gridname=rg_m7m8_thick, netnames=['VREF<0>', 'VSS', 'VREF<1>', 'VSS', 'VREF<2>', 'VSS'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=1, offset_end_index=0)

    #osp/osm route
    pdict_os_m4m5 = laygen.get_inst_pin_coord(None, None, rg_m4m5_basic_thick)
    rosp_m5=[]
    rosm_m5=[]
    for i in range(num_slices):
        rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], 
                        pdict_os_m4m5[isar.name]['OSP'+str(i)][0], pdict_os_m4m5[isar.name]['OSP'+str(i)][0]+np.array([-i-2, -10]), gridname=rg_m4m5_basic_thick)
        rosp_m5.append(rv0)
        rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], 
                        pdict_os_m4m5[isar.name]['OSM'+str(i)][0], pdict_os_m4m5[isar.name]['OSM'+str(i)][0]+np.array([-num_slices-i-2, -10]), gridname=rg_m4m5_basic_thick)
        rosm_m5.append(rv0)
    pdict_os_m5m6 = laygen.get_inst_pin_coord(None, None, rg_m5m6_thick)
    x0=pdict_os_m5m6[isar.name]['VREF0<0>'][0][0]-4*num_slices
    y0=pdict_os_m5m6[isar.name]['VREF0<0>'][0][1]-8
    rosp_m6=[]
    rosm_m6=[]
    for i in range(num_slices):
        xy0=laygen.get_rect_xy(rosp_m5[i].name, gridname=rg_m5m6_thick, sort=True)[0]
        rv0, rh0 = laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][6], xy0, np.array([x0, y0-2*i]), gridname=rg_m5m6_thick)
        laygen.create_boundary_pin_form_rect(rh0, rg_m5m6_thick, 'OSP'+str(i), laygen.layers['pin'][6], size=6, direction='left')
        rosp_m6.append(rh0)
        xy0=laygen.get_rect_xy(rosm_m5[i].name, gridname=rg_m5m6_thick, sort=True)[0]
        rv0, rh0 = laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][6], xy0, np.array([x0, y0-2*i-1]), gridname=rg_m5m6_thick)
        laygen.create_boundary_pin_form_rect(rh0, rg_m5m6_thick, 'OSM'+str(i), laygen.layers['pin'][6], size=6, direction='left')
        rosm_m6.append(rh0)
    
            
    #other pins - duplicate
    pin_prefix_list=['INP', 'INM', 'VREF', 'ASCLKD', 'EXTSEL_CLK', 'ADCOUT', 'CLKOUT_DES', 'CLKBOUT_NC', 'CLKCAL', 'RSTP', 'RSTN', 'CLKIP', 'CLKIN']
    for pn, p in sar_pins.items():
        for pfix in pin_prefix_list:
            if pn.startswith(pfix):
                laygen.add_pin(pn, sar_pins[pn]['netname'], sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])

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
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    #laygen.load_template(filename=ret_libname+'.yaml', libname=ret_libname)
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
    rg_m5m6_thick_basic = 'route_M5_M6_thick_basic'
    rg_m5m6_thick2_thick = 'route_M5_M6_thick2_thick'
    rg_m6m7_thick = 'route_M6_M7_thick'
    rg_m6m7_thick2_thick = 'route_M6_M7_thick2_thick'
    rg_m7m8_thick = 'route_M7_M8_thick'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

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

    cellname = 'tisaradc_body'
    tisar_core_name = 'tisaradc_body_core'
    tisar_space_name = 'tisaradc_body_space'
    tisar_space2_name = 'tisaradc_body_space2'

    #sar generation
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_tisaradc_body(laygen, objectname_pfix='TISA0', 
                           libname=workinglib, tisar_core_name=tisar_core_name, tisar_space_name=tisar_space_name, tisar_space2_name=tisar_space2_name,
                           placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5, 
                           routing_grid_m4m5_basic_thick=rg_m4m5_basic_thick, routing_grid_m5m6=rg_m5m6,
                           routing_grid_m5m6_thick=rg_m5m6_thick, routing_grid_m5m6_thick_basic=rg_m5m6_thick_basic, 
                           routing_grid_m6m7_thick=rg_m6m7_thick, routing_grid_m7m8_thick=rg_m7m8_thick, num_bits=num_bits, num_slices=num_slices, origin=np.array([0, 0]))
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

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

def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin from instances located at left/right boundaries"""
    rvdd0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VSS', gridname, sort=True)
    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=gridname)

def generate_samp_body(laygen, objectname_pfix, templib_logic, 
                       placement_grid='placement_basic',
                       routing_grid_m2m3='route_M2_M3_cmos', 
                       routing_grid_m3m4='route_M3_M4_basic', 
                       samp_cellname='nsw_wovdd_4x',
                       samp_m=4,
                       space_cellname_list=['space_wovdd_4x', 'space_wovdd_2x', 'space_wovdd_1x'],
                       tap_cellname='tap_wovdd',
                       space_m_list=[0, 0, 0],
                       tap_m_list=[2, 2],
                       origin=np.array([0, 0])):
    """
    generate a sampler body. 
    """
    #variable/cell namings
    pg = placement_grid
    rg23 = routing_grid_m2m3
    rg34 = routing_grid_m3m4

    itap=[]
    isp_t=[]
    isp=[]
    isamp=[]

    '''
    width = laygen.templates.get_template('sarafe_nsw', libname=workinglib).xy[1][0] \
                - laygen.templates.get_template('nmos4_fast_left').xy[1][0]*2
    height = laygen.templates.get_template('space_wovdd_1x', libname=logictemplib).xy[1][1]
    m_space2 = int(round(width / laygen.templates.get_template('space_wovdd_1x', libname=logictemplib).xy[1][0]))
    #m_space2 = int(m_space2/2) #double space cells
    #m_space2_4x = int(m_space2 / 4)
    #m_space2_2x = int((m_space2 - m_space2_4x * 4) / 2)
    #m_space2_1x = int(m_space2 - m_space2_4x * 4 - m_space2_2x * 2)
    #space2_m_list=[m_space2_4x, m_space2_2x, m_space2_1x]
    print(width)
    # placement
    # top space
    isp_t.append(laygen.relplace(name=None, templatename='space_wovdd_1x', gridname=pg,  
                               direction='right', shape=[m_space2, 1], offset=np.array([0,height]), 
                               template_libname=templib_logic, transform='R0'))
    '''
    # left tap
    itap.append(laygen.relplace(name=None, templatename=tap_cellname, gridname=pg, 
                                direction='right', shape=[tap_m_list[0], 1], template_libname=templib_logic, transform='R0'))
    # left space
    isp.append(laygen.relplace(name=None, templatename=space_cellname_list, gridname=pg, refobj=itap[-1], 
                               direction=['right']*len(space_cellname_list), shape=[[i, 1] for i in space_m_list], 
                               template_libname=templib_logic, transform='R0'))
    # left switch
    isamp.append(laygen.relplace(name=None, templatename=samp_cellname, gridname=pg, refobj=isp[-1][-1], 
                                 direction='right', shape=[samp_m, 1], template_libname=templib_logic, transform='R0'))
    # right switch
    isamp.append(laygen.relplace(name=None, templatename=samp_cellname, gridname=pg, refobj=isamp[-1], 
                                 direction='right', shape=[samp_m, 1], template_libname=templib_logic, transform='MY'))
    # right space
    isp.append(laygen.relplace(name=None, templatename=list(reversed(space_cellname_list)), gridname=pg, refobj=isamp[-1], 
                               direction=['right']*len(space_cellname_list), shape=[[i, 1] for i in list(reversed(space_m_list))], 
                               template_libname=templib_logic, transform='R0'))
    # right tap
    itap.append(laygen.relplace(name=None, templatename=tap_cellname, gridname=pg, refobj=isp[-1][-1], 
                                direction='right', shape=[tap_m_list[0], 1], template_libname=templib_logic, transform='R0'))
    # signal routes
    sides=['left', 'right']
    pins_se=['EN']
    pins_diff=['I', 'O']
    yofsts_se=np.array([-2])
    yofsts_diff=np.array([4, 0])
    # xy reference coordinates
    xl=[laygen.get_inst_pin_xy(name=isamp[0].name, pinname='EN', gridname=rg34, index=[0, 0], sort=True)[0][0],
        laygen.get_inst_pin_xy(name=isamp[0].name, pinname='I', gridname=rg34, index=[samp_m-1, 0], sort=True)[0][0]]
    xr=[laygen.get_inst_pin_xy(name=isamp[1].name, pinname='I', gridname=rg34, index=[samp_m-1, 0], sort=True)[0][0],
        laygen.get_inst_pin_xy(name=isamp[1].name, pinname='EN', gridname=rg34, index=[0, 0], sort=True)[0][0]]
    x=np.array([xl, xr])
    y0=laygen.get_inst_pin_xy(name=isamp[0].name, pinname='I', gridname=rg34, index=[0, 0], sort=True)[0][1]
    y_se=yofsts_se+y0
    y_diff=yofsts_diff+y0
    # actual routes
    routes={p:[] for p in pins_se+pins_diff}
    for p, _y in zip(pins_se, y_se): #horizontal M4 (single)
        routes[p].append(laygen.route(name=None, xy0=[xl[0],_y], xy1=[xr[1],_y], gridname0=rg34)) 
    for s, _x, _isamp in zip(sides, x, isamp):
        for p, _y in zip(pins_diff, y_diff): #horizontal M4 (differential)
            routes[p].append(laygen.route(name=None, xy0=[_x[0],_y], xy1=[_x[1],_y], gridname0=rg34)) 
        for p, _y in zip(pins_diff+pins_se, np.concatenate((y_diff,y_se))):
            for i in range(samp_m): #vertical M3 + via
                laygen.route(name=None, xy0=[0, 0], xy1=[_x[0],_y], refobj0=_isamp.elements[i, 0].pins[p], 
                             gridname0=rg34, direction='y', via1=[0, 0]) 
    # signal pins 
    for p in pins_diff:
        for r, sfix in zip(routes[p], ['P', 'M']):
            laygen.pin_from_rect(name=p+str(sfix), layer=laygen.layers['pin'][4], rect=r, gridname=rg34)
    for p in pins_se:
        for r in routes[p]:
            laygen.pin_from_rect(name=p, layer=laygen.layers['pin'][4], rect=r, gridname=rg34)
    
    # power routes
    num_pwr=int(laygen.get_template_size(name=itap[0].cellname, gridname=rg23, libname=itap[0].libname)[0]/2)*min(tap_m_list)
    rvss=[]
    for _itap, pfix in zip(itap, ['L', 'R']):
        rvss.append([])
        for i in range(0, num_pwr):
            rvss[-1].append(laygen.route(name=None, xy0=[2*i+2, 0], xy1=[2*i+2, 0], gridname0=rg23, 
                            refobj0=_itap.pins['VSS0'], refobj1=_itap.pins['VSS1'], via0=[0, 0], via1=[0, 0]))
    # power pins
    for rv, sfix in zip(rvss, ['L', 'R']):
        for idx, r in enumerate(rv):
            laygen.pin_from_rect(name='VSS'+str(sfix)+str(idx), layer=laygen.layers['pin'][3], rect=r, gridname=rg23, netname='VSS')

def generate_samp_space(laygen, objectname_pfix, templib_logic, 
                       placement_grid='placement_basic',
                       routing_grid_m2m3='route_M2_M3_cmos', 
                       routing_grid_m3m4='route_M3_M4_basic', 
                       samp_cellname='nsw_wovdd_4x',
                       samp_m=4,
                       space_cellname_list=['space_wovdd_4x', 'space_wovdd_2x', 'space_wovdd_1x'],
                       tap_cellname='tap_wovdd',
                       space_m_list=[0, 0, 0],
                       tap_m_list=[2, 2],
                       origin=np.array([0, 0])):
    """
    generate a sampler space. 
    """
    #variable/cell namings
    pg = placement_grid
    rg23 = routing_grid_m2m3
    rg34 = routing_grid_m3m4

    itap=[]
    isp_t=[]
    isp=[]
    isamp=[]

    width = laygen.templates.get_template('sarafe_nsw', libname=workinglib).xy[1][0] \
                - laygen.templates.get_template('nmos4_fast_left').xy[1][0]*2
    height = laygen.templates.get_template('space_wovdd_1x', libname=logictemplib).xy[1][1]
    m_space2 = int(round(width / laygen.templates.get_template('space_wovdd_1x', libname=logictemplib).xy[1][0]))
    print(width)
    # placement
    # top space
    isp_t.append(laygen.relplace(name=None, templatename='space_1x', gridname=pg,  
                               direction='right', shape=[m_space2, 1], 
                               template_libname=templib_logic, transform='R0'))

def generate_samp_buffer(laygen, objectname_pfix, templib_logic, 
                         placement_grid='placement_basic',
                         routing_grid_m2m3='route_M2_M3_cmos', 
                         routing_grid_m3m4='route_M3_M4_basic', 
                         inbuf_cellname_list=['inv_8x', 'inv_24x'],
                         outbuf_cellname_list=['inv_4x', 'inv_24x'],
                         space_cellname_list=['space_4x', 'space_2x', 'space_1x'],
                         tap_cellname='tap',
                         space_m_list=[0, 0, 0],
                         tap_m_list=[2, 2],
                         origin=np.array([0, 0])):
    """
    generate a sampler buffer.
    """
    #variable/cell namings
    pg = placement_grid
    rg23 = routing_grid_m2m3
    rg34 = routing_grid_m3m4
    itap=[]
    isp=[]
    iinbuf=[]
    ioutbuf=[]
    # placement
    # left tap
    itap.append(laygen.relplace(name=None, templatename=tap_cellname, gridname=pg, 
                                direction='right', shape=[tap_m_list[0], 1], template_libname=templib_logic, transform='R0'))
    # left space
    isp.append(laygen.relplace(name=None, templatename=space_cellname_list, gridname=pg, refobj=itap[-1], 
                               direction=['right']*len(space_cellname_list), shape=[[i, 1] for i in space_m_list], 
                               template_libname=templib_logic, transform='R0'))
    # inbuf buffer
    iinbuf=laygen.relplace(name=None, templatename=inbuf_cellname_list, gridname=pg, refobj=isp[-1][-1], 
                           direction='right', template_libname=templib_logic, transform='R0')
    # right switch
    ioutbuf=laygen.relplace(name=None, templatename=outbuf_cellname_list, gridname=pg, refobj=iinbuf[-1], 
                            direction='right', template_libname=templib_logic, transform='R0')
    # right space
    isp.append(laygen.relplace(name=None, templatename=list(reversed(space_cellname_list)), gridname=pg, refobj=ioutbuf[-1], 
                               direction=['right']*len(space_cellname_list), shape=[[i, 1] for i in list(reversed(space_m_list))], 
                               template_libname=templib_logic, transform='R0'))
    # right tap
    itap.append(laygen.relplace(name=None, templatename=tap_cellname, gridname=pg, refobj=isp[-1][-1], 
                                direction='right', shape=[tap_m_list[0], 1], template_libname=templib_logic, transform='R0'))
    
    # signal routes
    #chain
    yofst_chain=2
    for ibf0, ibf1 in zip(iinbuf[:-1], iinbuf[1:]):
        xy0=laygen.get_inst_pin_xy(name=ibf0.name, pinname='O', gridname=rg23, sort=True)[0]
        xy1=laygen.get_inst_pin_xy(name=ibf1.name, pinname='I', gridname=rg23, sort=True)[0]
        laygen.route_vhv(xy0=xy0, xy1=xy1, track_y=xy0[1]+yofst_chain, gridname0=rg23)
    xy0=laygen.get_inst_pin_xy(name=iinbuf[-1].name, pinname='O', gridname=rg23, sort=True)[0]
    xy1=laygen.get_inst_pin_xy(name=ioutbuf[0].name, pinname='I', gridname=rg23, sort=True)[0]
    laygen.route_vhv(xy0=xy0, xy1=xy1, track_y=xy0[1]+yofst_chain, gridname0=rg23)
    for obf0, obf1 in zip(ioutbuf[:-1], ioutbuf[1:]):
        xy0=laygen.get_inst_pin_xy(name=obf0.name, pinname='O', gridname=rg23, sort=True)[0]
        xy1=laygen.get_inst_pin_xy(name=obf1.name, pinname='I', gridname=rg23, sort=True)[0]
        laygen.route_vhv(xy0=xy0, xy1=xy1, track_y=xy0[1]+yofst_chain, gridname0=rg23)
    #input
    yofst_in=4
    xy0=laygen.get_inst_pin_xy(name=iinbuf[0].name, pinname='I', gridname=rg34, sort=True)[0]
    rv0, rin=laygen.route_vh(xy0=xy0, xy1=xy0+np.array([4, yofst_in]), gridname0=rg34)
    #output_sw
    yofst_osw=2
    xy0=laygen.get_inst_pin_xy(name=iinbuf[-1].name, pinname='O', gridname=rg34, sort=True)[0]
    rv0, rout_sw=laygen.route_vh(xy0=xy0, xy1=xy0+np.array([-4, yofst_osw]), gridname0=rg34)
    #output_buf
    yofst_obuf=0
    xy0=laygen.get_inst_pin_xy(name=ioutbuf[-1].name, pinname='O', gridname=rg34, sort=True)[0]
    rv0, rout_buf=laygen.route_vh(xy0=xy0, xy1=xy0+np.array([-4, yofst_obuf]), gridname0=rg34)
    # signal pins 
    for p, r in zip(['IN', 'OUT_SW', 'OUT_BUF'],[rin, rout_sw, rout_buf]):
        laygen.pin_from_rect(name=p, layer=laygen.layers['pin'][4], rect=r, gridname=rg34)

    # power routes
    num_pwr=int(laygen.get_template_size(name=itap[0].cellname, gridname=rg23, libname=itap[0].libname)[0]*min(tap_m_list)/2)
    rvdd=[]
    rvss=[]
    for _itap, pfix in zip(itap, ['L', 'R']):
        rvdd.append([])
        rvss.append([])
        for i in range(0, num_pwr):
            rvdd[-1].append(laygen.route(name=None, xy0=[2*i+1, 0], xy1=[2*i+1, 0], gridname0=rg23, 
                            refobj0=_itap.pins['VSS'], refobj1=_itap.pins['VDD'], via1=[0, 0]))
            rvss[-1].append(laygen.route(name=None, xy0=[2*i+2, 0], xy1=[2*i+2, 0], gridname0=rg23, 
                            refobj0=_itap.pins['VSS'], refobj1=_itap.pins['VDD'], via0=[0, 0]))
    # power pins
    for rv, sfix in zip(rvss, ['L', 'R']):
        for idx, r in enumerate(rv):
            laygen.pin_from_rect(name='VSS'+str(sfix)+str(idx), layer=laygen.layers['pin'][3], rect=r, gridname=rg23, netname='VSS')
    for rv, sfix in zip(rvdd, ['L', 'R']):
        for idx, r in enumerate(rv):
            laygen.pin_from_rect(name='VDD'+str(sfix)+str(idx), layer=laygen.layers['pin'][3], rect=r, gridname=rg23, netname='VDD')

def generate_samp(laygen, objectname_pfix, workinglib, 
                  placement_grid='placement_basic',
                  routing_grid_m4m5='route_M4_M5_basic_thick', 
                  power_grid_m3m4='route_M3_M4_basic_thick',
                  power_grid_m4m5='route_M4_M5_thick',
                  power_grid_m5m6='route_M5_M6_thick',
                  origin=np.array([0, 0])):
    """generate a sampler with clock buffers. used when AnalogMOS is not available
    """
    #variable/cell namings
    pg = placement_grid
    rg45bt = routing_grid_m4m5
    pg34bt = power_grid_m3m4
    pg45t = power_grid_m4m5
    pg56t = power_grid_m5m6

    # placement
    core_origin = origin + laygen.get_template_size('boundary_bottomleft', pg)
    # sampler body
    isamp = laygen.relplace(name=None, templatename='sarsamp_body', gridname=pg, template_libname=workinglib, transform='R0', xy=core_origin)
    # sampler space
    ispace = laygen.relplace(name=None, templatename='sarsamp_space', gridname=pg, refobj=isamp,
                           direction='top', template_libname=workinglib, transform='R0')
    # clock buffer
    ibuf = laygen.relplace(name=None, templatename='sarsamp_buf', gridname=pg, refobj=ispace,
                           direction='top', template_libname=workinglib, transform='R0')
    # boundaries
    m_bnd = int(laygen.get_template_size('sarsamp_body', gridname=pg, libname=workinglib)[0]/laygen.get_template_size('boundary_bottom', gridname=pg)[0])
    devname_bnd_left = ['nmos4_fast_left', 'nmos4_fast_left', 'nmos4_fast_left', 'pmos4_fast_left'] + ['nmos4_fast_left', 'pmos4_fast_left']
    devname_bnd_right = ['nmos4_fast_right', 'nmos4_fast_right', 'nmos4_fast_right', 'pmos4_fast_right'] + ['nmos4_fast_right', 'pmos4_fast_right']
    transform_bnd_left = ['R0', 'MX', 'R0', 'MX'] + ['R0', 'MX']
    transform_bnd_right = ['R0', 'MX', 'R0', 'MX'] + ['R0', 'MX']
    [bnd_bottom, bnd_top, bnd_left, bnd_right] \
        = laygenhelper.generate_boundary(laygen, objectname_pfix='BND0', placement_grid=pg,
                            devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
                            shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
                            shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_left=devname_bnd_left,
                            transform_left=transform_bnd_left,
                            devname_right=devname_bnd_right,
                            transform_right=transform_bnd_right,
                            origin=origin)

    # route
    x_center=int((laygen.get_inst_bbox(name=ibuf.name, gridname=rg45bt, sort=True)[1][0] \
                  -laygen.get_inst_bbox(name=ibuf.name, gridname=rg45bt, sort=True)[0][0])/2\
                  +laygen.get_inst_bbox(name=ibuf.name, gridname=rg45bt, sort=True)[0][0])
    y_top=int(laygen.get_inst_bbox(name=ibuf.name, gridname=rg45bt, sort=True)[1][1])
    #in
    xy0=laygen.get_inst_pin_xy(name=isamp.name, pinname='IP', gridname=rg45bt, sort=True)[0]
    xy1=[x_center-3, y_top]
    rh0, rinp0=laygen.route_hv(xy0=xy0, xy1=xy1, gridname0=rg45bt)
    xy0=laygen.get_inst_pin_xy(name=isamp.name, pinname='IM', gridname=rg45bt, sort=True)[1]
    xy1=[x_center+3, y_top]
    rh0, rinn0=laygen.route_hv(xy0=xy0, xy1=xy1, gridname0=rg45bt)
    #out
    xy0=laygen.get_inst_pin_xy(name=isamp.name, pinname='OP', gridname=rg45bt, sort=True)[0]
    xy1=[x_center-4, 0]
    rh0, routp0=laygen.route_hv(xy0=xy0, xy1=xy1, gridname0=rg45bt)
    xy0=laygen.get_inst_pin_xy(name=isamp.name, pinname='OM', gridname=rg45bt, sort=True)[1]
    xy1=[x_center+4, 0]
    rh0, routn0=laygen.route_hv(xy0=xy0, xy1=xy1, gridname0=rg45bt)
    #en
    xy0=laygen.get_inst_pin_xy(name=ibuf.name, pinname='OUT_SW', gridname=rg45bt, sort=True)[0]
    xy1=laygen.get_inst_pin_xy(name=isamp.name, pinname='EN', gridname=rg45bt, sort=True)[0]
    rh0, rckpg0, rh1 = laygen.route_hvh(xy0=xy0, xy1=xy1, track_x=x_center-1, gridname0=rg45bt)
    rh0, rv0, rh1 = laygen.route_hvh(xy0=xy0, xy1=xy1, track_x=x_center+1, gridname0=rg45bt)
    #ckin
    xy0=laygen.get_inst_pin_xy(name=ibuf.name, pinname='IN', gridname=rg45bt, sort=True)[0]
    xy1=[xy0[0], y_top]
    rh0, rckin0=laygen.route_hv(xy0=xy0, xy1=xy1, gridname0=rg45bt)
    #ckout
    xy0=laygen.get_inst_pin_xy(name=ibuf.name, pinname='OUT_BUF', gridname=rg45bt, sort=True)[0]
    xy1=[x_center, 0]
    rh0, rckout0=laygen.route_hv(xy0=xy0, xy1=xy1, gridname0=rg45bt)

    # signal pins 
    for p, r in zip(['inp', 'inn', 'outp', 'outn', 'ckin', 'ckout', 'ckpg'],[rinp0, rinn0, routp0, routn0, rckin0, rckout0, rckpg0]):
        laygen.pin_from_rect(name=p, layer=laygen.layers['pin'][5], rect=r, gridname=rg45bt)

    #vdd/vss - route
    #samp_m3_xy
    rvss_samp_m3=[[], []]
    for pn, p in laygen.get_inst(isamp.name).pins.items(): 
        if pn.startswith('VSSL'):
            xy=laygen.get_inst_pin_xy(name=isamp.name, pinname=pn, gridname=pg34bt, sort=True)
            rvss_samp_m3[0].append(xy)
        if pn.startswith('VSSR'):
            xy=laygen.get_inst_pin_xy(name=isamp.name, pinname=pn, gridname=pg34bt, sort=True)
            rvss_samp_m3[1].append(xy)
    #samp_m4
    rvss_samp_m4=[None, None]
    input_rails_xy=[rvss_samp_m3[0]]
    rvss_samp_m4[0] = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_SAMPL_M4_', 
                      layer=laygen.layers['metal'][4], gridname=pg34bt, netnames=['samp_body'], direction='x', 
                      input_rails_xy=input_rails_xy, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                      offset_start_index=0, offset_end_index=-1)[0]
    input_rails_xy=[rvss_samp_m3[1]]
    rvss_samp_m4[1] = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_SAMPR_M4_', 
                      layer=laygen.layers['metal'][4], gridname=pg34bt, netnames=['samp_body'], direction='x', 
                      input_rails_xy=input_rails_xy, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None, 
                      offset_start_index=0, offset_end_index=-1)[0]
    #buf_m3_xy
    rvdd_buf_m3=[[], []]
    rvss_buf_m3=[[], []]
    for pn, p in laygen.get_inst(ibuf.name).pins.items(): 
        if pn.startswith('VSSL'):
            xy=laygen.get_inst_pin_xy(name=ibuf.name, pinname=pn, gridname=pg34bt, sort=True)
            rvss_buf_m3[0].append(xy)
        if pn.startswith('VSSR'):
            xy=laygen.get_inst_pin_xy(name=ibuf.name, pinname=pn, gridname=pg34bt, sort=True)
            rvss_buf_m3[1].append(xy)
        if pn.startswith('VDDL'):
            xy=laygen.get_inst_pin_xy(name=ibuf.name, pinname=pn, gridname=pg34bt, sort=True)
            rvdd_buf_m3[0].append(xy)
        if pn.startswith('VDDR'):
            xy=laygen.get_inst_pin_xy(name=ibuf.name, pinname=pn, gridname=pg34bt, sort=True)
            rvdd_buf_m3[1].append(xy)
    #buf_m4
    rvss_buf_m4=[None, None]
    rvdd_buf_m4=[None, None]
    input_rails_xy=[rvdd_buf_m3[0], rvss_buf_m3[0]]
    rvdd_buf_m4[0], rvss_buf_m4[0] = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_BUFL_M4_', 
                                     layer=laygen.layers['metal'][4], gridname=pg34bt, netnames=['VDD', 'VSS'], direction='x', 
                                     input_rails_xy=input_rails_xy, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                                     offset_start_index=1, offset_end_index=0)
    input_rails_xy=[rvdd_buf_m3[1], rvss_buf_m3[1]]
    rvdd_buf_m4[1], rvss_buf_m4[1] = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_BUFR_M4_', 
                                     layer=laygen.layers['metal'][4], gridname=pg34bt, netnames=['VDD', 'VSS'], direction='x', 
                                     input_rails_xy=input_rails_xy, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                                     offset_start_index=1, offset_end_index=0)
    #m4_buf
    rvss_m4=[rvss_buf_m4[0], rvss_buf_m4[1]]
    #rvss_m4=[rvss_samp_m4[0]+rvss_buf_m4[0], rvss_samp_m4[1]+rvss_buf_m4[1]]
    rvdd_m4=rvdd_buf_m4
    #m4_samp
    rvss_samp_m4=[rvss_samp_m4[0], rvss_samp_m4[1]]
    #m5
    rvss_m5=[None, None]
    rvdd_m5=[None, None]
    input_rails_rect = [rvdd_m4[0], rvss_m4[0]]
    rvdd_m5[0], rvss_m5[0] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='L_M5_', 
                layer=laygen.layers['metal'][5], gridname=pg45t, netnames=['VDD', 'VSS'], direction='y',
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    input_rails_rect = [rvdd_m4[1], rvss_m4[1]]
    rvdd_m5[1], rvss_m5[1] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='R_M5_', 
                layer=laygen.layers['metal'][5], gridname=pg45t, netnames=['VDD', 'VSS'], direction='y',
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    for r in rvdd_m5[0]:
        p=laygen.pin_from_rect(name='LVDD_M5_'+r.name, layer=laygen.layers['pin'][5], rect=r, gridname=pg45t, netname='VDD')
    for r in rvdd_m5[1]:
        p=laygen.pin_from_rect(name='RVDD_M5_'+r.name, layer=laygen.layers['pin'][5], rect=r, gridname=pg45t, netname='VDD')
    for r in rvss_m5[0]:
        p=laygen.pin_from_rect(name='LVSS_M5_'+r.name, layer=laygen.layers['pin'][5], rect=r, gridname=pg45t, netname='VSS')
    for r in rvss_m5[1]:
        p=laygen.pin_from_rect(name='RVSS_M5_'+r.name, layer=laygen.layers['pin'][5], rect=r, gridname=pg45t, netname='VSS')

    #m5 samp
    rvss_samp_m5=[None, None]
    input_rails_rect = [rvss_samp_m4[0], rvss_samp_m4[0]]
    rvss_samp_m5[0], rvss_samp_m5[0] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='L_M5_', 
                layer=laygen.layers['metal'][5], gridname=pg45t, netnames=['samp_body', 'samp_body'], direction='y', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    input_rails_rect = [rvss_samp_m4[1], rvss_samp_m4[1]]
    rvss_samp_m5[1], rvss_samp_m5[1] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='L_M5_', 
                layer=laygen.layers['metal'][5], gridname=pg45t, netnames=['samp_body', 'samp_body'], direction='y', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    #m6
    input_rails_rect = [rvdd_m5[0]+rvdd_m5[1], rvss_m5[0]+rvss_m5[1]]
    x1 = laygen.get_inst_bbox(name=ibuf.name, gridname=pg56t)[1][0] + laygen.get_template_size('nmos4_fast_left', gridname=pg56t)[0]
    rvdd_m6, rvss_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_', 
                layer=laygen.layers['metal'][6], gridname=pg56t, netnames=['VDD', 'VSS'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=x1,
                offset_start_index=0, offset_end_index=0)
    #m6_samp
    input_rails_rect = [rvss_samp_m5[0]+rvss_samp_m5[1], rvss_samp_m5[0]+rvss_samp_m5[1]]
    x1 = laygen.get_inst_bbox(name=ibuf.name, gridname=pg56t)[1][0] + laygen.get_template_size('nmos4_fast_left', gridname=pg56t)[0]
    rvss_samp_m6, rvss_samp_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_', 
                layer=laygen.layers['metal'][6], gridname=pg56t, netnames=['samp_body', 'samp_body'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0+1, overwrite_end_coord=x1-1,
                offset_start_index=0, offset_end_index=0)
    #trimming and pinning
    x1_phy = laygen.get_inst_bbox(name=ibuf.name)[1][0] + laygen.get_template_size('nmos4_fast_left')[0]
    for r in rvdd_m6:
        r.xy1[0]=x1_phy
        p=laygen.pin_from_rect(name='VDD_M6_'+r.name, layer=laygen.layers['pin'][6], rect=r, gridname=pg56t, netname='VDD')
        p.xy1[0]=x1_phy
    for r in rvss_m6:
        r.xy1[0]=x1_phy
        p=laygen.pin_from_rect(name='VSS_M6_'+r.name, layer=laygen.layers['pin'][6], rect=r, gridname=pg56t, netname='VSS')
        p.xy1[0]=x1_phy
    for r in rvss_samp_m6:
        r.xy1[0]=x1_phy
        p=laygen.pin_from_rect(name='samp_body_M6_'+r.name, layer=laygen.layers['pin'][6], rect=r, gridname=pg56t, netname='samp_body')
        p.xy1[0]=x1_phy

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
    rg23 = 'route_M2_M3_cmos'
    rg34 = 'route_M3_M4_basic'
    rg34bt = 'route_M3_M4_basic_thick'
    rg45 = 'route_M4_M5_basic'
    rg45bt = 'route_M4_M5_basic_thick'
    rg45td = 'route_M4_M5_thick_dense'
    #rg45bt = 'route_M4_M5_basic'
    rg45t = 'route_M4_M5_thick'
    rg56t = 'route_M5_M6_thick'

    mycell_list = []
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        m_sw=sizedict['sarsamp']['m_sw']
        m_sw_arr=sizedict['sarsamp']['m_sw_arr']
        m_inbuf_list=sizedict['sarsamp']['m_inbuf_list']
        m_outbuf_list=sizedict['sarsamp']['m_outbuf_list']
    samp_cellname='nsw_wovdd_'+str(m_sw)+'x'
    inbuf_cellname_list=['inv_'+str(i)+'x' for i in m_inbuf_list]
    outbuf_cellname_list=['inv_'+str(i)+'x' for i in m_outbuf_list]

    #body cell generation (2 step)
    cellname='sarsamp_body' 
    print(cellname+" generating")
    mycell_list.append(cellname)
    # 1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_samp_body(laygen, objectname_pfix='SW0', templib_logic=logictemplib, 
                       placement_grid=pg,
                       routing_grid_m2m3=rg23,
                       routing_grid_m3m4=rg34,
                       samp_cellname=samp_cellname,
                       samp_m=m_sw_arr,
                       space_cellname_list=['space_wovdd_4x', 'space_wovdd_2x', 'space_wovdd_1x'],
                       tap_cellname='tap_wovdd',
                       space_m_list=[0, 0, 0],
                       tap_m_list=[4, 4],
                       origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    # 2. calculate spacing param and regenerate
    x0 = laygen.templates.get_template('sarafe_nsw', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0]*2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_space = int(m_space/2) #double space cells
    m_space_4x = int(m_space / 4)
    m_space_2x = int((m_space - m_space_4x * 4) / 2)
    m_space_1x = int(m_space - m_space_4x * 4 - m_space_2x * 2)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_samp_body(laygen, objectname_pfix='SW0', templib_logic=logictemplib, 
                       placement_grid=pg,
                       routing_grid_m2m3=rg23,
                       routing_grid_m3m4=rg34,
                       samp_cellname=samp_cellname,
                       samp_m=m_sw_arr,
                       space_cellname_list=['space_wovdd_4x', 'space_wovdd_2x', 'space_wovdd_1x'],
                       tap_cellname='tap_wovdd',
                       space_m_list=[m_space_4x, m_space_2x, m_space_1x],
                       tap_m_list=[4, 4],
                       origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    cellname='sarsamp_space' 
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_samp_space(laygen, objectname_pfix='SPACE', templib_logic=logictemplib, 
                       placement_grid=pg,
                       routing_grid_m2m3=rg23,
                       routing_grid_m3m4=rg34,
                       samp_cellname=samp_cellname,
                       samp_m=m_sw_arr,
                       space_cellname_list=['space_wovdd_4x', 'space_wovdd_2x', 'space_wovdd_1x'],
                       tap_cellname='tap_wovdd',
                       space_m_list=[m_space_4x, m_space_2x, m_space_1x],
                       tap_m_list=[4, 4],
                       origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    #buffer cell generation (2 step)
    cellname='sarsamp_buf' 
    print(cellname+" generating")
    mycell_list.append(cellname)
    # 1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_samp_buffer(laygen, objectname_pfix='BUF0', templib_logic=logictemplib, 
                         placement_grid=pg,
                         routing_grid_m2m3=rg23,
                         routing_grid_m3m4=rg34, 
                         inbuf_cellname_list=inbuf_cellname_list,
                         outbuf_cellname_list=outbuf_cellname_list,
                         space_cellname_list=['space_4x', 'space_2x', 'space_1x'],
                         tap_cellname='tap',
                         space_m_list=[0, 0, 0],
                         tap_m_list=[4, 4],
                         origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    # 2. calculate spacing param and regenerate
    x0 = laygen.templates.get_template('sarafe_nsw', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0]*2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_space = int(m_space/2) #double space cells
    m_space_4x = int(m_space / 4)
    m_space_2x = int((m_space - m_space_4x * 4) / 2)
    m_space_1x = int(m_space - m_space_4x * 4 - m_space_2x * 2)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_samp_buffer(laygen, objectname_pfix='BUF0', templib_logic=logictemplib, 
                         placement_grid=pg,
                         routing_grid_m2m3=rg23,
                         routing_grid_m3m4=rg34, 
                         inbuf_cellname_list=inbuf_cellname_list,
                         outbuf_cellname_list=outbuf_cellname_list,
                         space_cellname_list=['space_4x', 'space_2x', 'space_1x'],
                         tap_cellname='tap',
                         space_m_list=[m_space_4x, m_space_2x, m_space_1x],
                         tap_m_list=[4, 4],
                         origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    #sampler top generation
    cellname='sarsamp_bb' 
    print(cellname+" generating")
    mycell_list.append(cellname)
    # 1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_samp(laygen, objectname_pfix='SAMP0', workinglib=workinglib, placement_grid=pg,
                  routing_grid_m4m5=rg45bt, 
                  power_grid_m3m4=rg34bt, 
                  power_grid_m4m5=rg45t,
                  power_grid_m5m6=rg56t,
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

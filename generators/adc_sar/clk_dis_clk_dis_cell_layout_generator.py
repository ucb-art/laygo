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

def generate_tap(laygen, objectname_pfix, placement_grid, routing_grid_m1m2_thick, devname_tap_boundary, devname_tap_body,
                 m=1, origin=np.array([0,0]), transform='R0'):
    """generate a tap primitive"""
    pg = placement_grid
    rg_m1m2_thick = routing_grid_m1m2_thick

    # placement
    itapbl0 = laygen.place("I" + objectname_pfix + 'BL0', devname_tap_boundary, pg, xy=origin, transform=transform)
    itap0 = laygen.relplace(name = "I" + objectname_pfix + '0', templatename = devname_tap_body, gridname = pg, refinstname = itapbl0.name, shape=np.array([m, 1]), transform=transform)
    itapbr0 = laygen.relplace(name = "I" + objectname_pfix + 'BR0', templatename = devname_tap_boundary, gridname = pg, refinstname = itap0.name, transform=transform)

    #power route
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2_thick,
                  refinstname0=itap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                  refinstname1=itap0.name, refpinname1='TAP1', refinstindex1=np.array([m-1, 0])
                  )
    for i in range(1-1, int(m/2)+0):
        laygen.via(None, np.array([0, 0]), refinstname=itap0.name, refpinname='TAP0', refinstindex=np.array([2*i, 0]),
                   gridname=rg_m1m2_thick)
    return [itapbl0, itap0, itapbr0]


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
        dev_bottom.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDBTM'+str(i+1), templatename = d, gridname = pg, refinstname = dev_bottom[-1].name,
                                          shape=shape_bottom[i+1], transform=transform_bottom[i+1]))
    dev_left=[]
    dev_left.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDLFT0', templatename = devname_left[0], gridname = pg, refinstname = dev_bottom[0].name, direction='top',
                                    shape=shape_left[0], transform=transform_left[0]))
    for i, d in enumerate(devname_left[1:]):
        dev_left.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDLFT'+str(i+1), templatename = d, gridname = pg, refinstname = dev_left[-1].name, direction='top',
                                        shape=shape_left[i+1], transform=transform_left[i+1]))
    dev_right=[]
    dev_right.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDRHT0', templatename = devname_right[0], gridname = pg, refinstname = dev_bottom[-1].name, direction='top',
                                     shape=shape_right[0], transform=transform_right[0]))
    for i, d in enumerate(devname_right[1:]):
        dev_right.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDRHT'+str(i+1), templatename = d, gridname = pg, refinstname = dev_right[-1].name, direction='top',
                                         shape=shape_right[i+1], transform=transform_right[i+1]))
    dev_top=[]
    dev_top.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDTOP0', templatename = devname_top[0], gridname = pg, refinstname = dev_left[-1].name, direction='top',
                                   shape=shape_top[0], transform=transform_top[0]))
    for i, d in enumerate(devname_top[1:]):
        dev_top.append(laygen.relplace(name = "I" + objectname_pfix + 'BNDTOP'+str(i+1), templatename = d, gridname = pg, refinstname = dev_top[-1].name,
                                       shape=shape_top[i+1], transform=transform_top[i+1]))
    #dev_right=[]
    return [dev_bottom, dev_top, dev_left, dev_right]

def generate_clkdis_cell(laygen, objectname_pfix, logictemp_lib, working_lib, grid, origin=np.array([0, 0]), num_bits=5, phy_width=20.16, num_capsw_dmy=10, num_dff_dmy=90, 
        len_cal=30, len_capsw=10, m_clki=2, y1_clki=5, y2_clki=10, m_clko=2, y1_clko=25, y2_clko=10, num_vss_vleft=2, num_vdd_vleft=2, num_vss_vright=3, num_vdd_vright=3,
        num_vss_h=4, num_vdd_h=4, m_tgate=4, m_dff=2, m_inv1=2, m_inv2=4, clock_pulse='False', pmos_body='VDD'):
    """generate cap driver """
    

    pg = grid['pg']
    rg_m1m2 = grid['rg_m1m2']
    rg_m1m2_thick = grid['rg_m1m2_thick']
    rg_m2m3 = grid['rg_m2m3']
    rg_m2m3_mos = grid['rg_m2m3_mos']
    rg_m2m3_thick = grid['rg_m2m3_thick']
    rg_m2m3_thick2 = grid['rg_m2m3_thick2']
    rg_m3m4 = grid['rg_m3m4']
    rg_m3m4_dense = grid['rg_m3m4_dense']
    rg_m3m4_thick2 = grid['rg_m3m4_thick2']
    rg_m4m5 = grid['rg_m4m5']
    rg_m5m6 = grid['rg_m5m6']
    rg_m6m7 = grid['rg_m6m7']

    '''
    phy_width = 20.16   #in um
    num_capsw_dmy = 10    #capsw left dummy number
    num_dff_dmy = 90     #dff left dummy number
    len_cal = 30        #calibration input length
    len_capsw = 10      #cap control output length

    #clock input
    m_clki = 2
    y1_clki = 5
    y2_clki = 10

    #clock output
    m_clko = 2
    y1_clko = 25
    y2_clko = 10

    #virtically vss and vdd metals
    num_vss_vleft = 2
    num_vdd_vleft = 2
    num_vss_vright = 3
    num_vdd_vright = 3
    '''
    m_in=3
    m_out=3
    tgate_template = laygen.templates.get_template('tgate_dn_'+str(m_tgate)+'x', logictemplib)
    tgate_pins = tgate_template.pins
    m_in=0
    m_out=0
    for pn, p in tgate_pins.items():
        if pn.startswith('I_'):
            m_in+=1
        if pn.startswith('O_'):
            m_out += 1

    #Get width for pg grid
    width =laygen.grids.get_absgrid_coord_x(gridname=pg, x=phy_width)
    #Half width, using for clock put output at the center of the cell
    half_width=width/2

    #####Place Boundary

    #Calculate size of boundary cell
    bnd_left_size_x = laygen.get_template_xy(name='nmos4_fast_left', gridname=pg, libname=tech + '_microtemplates_dense')[0]
    bnd_right_size_x = laygen.get_template_xy(name='nmos4_fast_right', gridname=pg, libname=tech + '_microtemplates_dense')[0]
    tap4_size_x = laygen.get_template_xy(name='ptap_fast_space_nf4', gridname=pg, libname=tech + '_microtemplates_dense')[0]

    #Caluclate number of top and bottom cells
    bnd_m = width - bnd_left_size_x - bnd_right_size_x  ##This is all the numbe of the cells, using a lot in code!!
    #print(bnd_m)

    [bnd_bottom, bnd_top, bnd_left, bnd_right]=generate_boundary(laygen, objectname_pfix='BND0',
        placement_grid=pg,
        devname_bottom = ['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
        shape_bottom = [np.array([1, 1]), np.array([bnd_m, 1]), np.array([1, 1])],
        devname_top = ['boundary_topleft', 'boundary_top', 'boundary_topright'],
        shape_top = [np.array([1, 1]), np.array([bnd_m, 1]), np.array([1, 1])],
        devname_left = ['ptap_fast_left', 'nmos4_fast_left', 'pmos4_fast_left',
                        'ntap_fast_left', 'pmos4_fast_left', 'nmos4_fast_left',
                        'ptap_fast_left', ],

        transform_left=['R0', 'R0', 'MX', 'MX', 'R0', 'MX', 'MX', ],

        devname_right=['ptap_fast_right', 'nmos4_fast_right', 'pmos4_fast_right',
                       'ntap_fast_right', 'pmos4_fast_right', 'nmos4_fast_right',
                       'ptap_fast_right',],
        transform_right = ['R0', 'R0', 'MX', 'MX', 'R0', 'MX', 'MX',],
        origin=np.array([0, 0]))

    #####Placing all the rows

    ##Bottom ptap row
    ptap0_0 = laygen.relplace(name='I'+objectname_pfix+'PTAP0_0', templatename='ptap_fast_space_nf4', 
                    gridname=pg, refinstname=bnd_left[0].name, template_libname=tech+'_microtemplates_dense')
    ptap0_1= laygen.relplace(name='I'+objectname_pfix+'PTAP0_1', templatename='ptap_fast_center_nf1', 
                    gridname=pg, refinstname=ptap0_0.name, template_libname=tech+'_microtemplates_dense',
                    shape=np.array([bnd_m-2*tap4_size_x, 1]))
    ptap0_2 = laygen.relplace(name='I'+objectname_pfix+'PTAP0_2', templatename='ptap_fast_space_nf4', 
                    gridname=pg, refinstname=ptap0_1.name, template_libname=tech+'_microtemplates_dense')

    ##CAP switch row
    #Calculate coodinate of sw_dmy0
    bnd_left_1_y=laygen.get_inst_xy(name=bnd_left[1].name, gridname=pg)[1] #y coodinate
    sw_dmy_xy=np.array([bnd_left_size_x, bnd_left_1_y]) #xy coodinate
    #Place sw_dmy0 and capsw0
    num_capsw_dmy_4x = int(num_capsw_dmy/4)
    num_capsw_dmy_1x = num_capsw_dmy - 4 * num_capsw_dmy_4x
    print(num_capsw_dmy_4x, num_capsw_dmy_1x)
    sw_dmy0= laygen.place(name='I'+objectname_pfix+'SWDM0_4x', templatename='space_4x', gridname=pg, xy=sw_dmy_xy,
            template_libname=logictemp_lib, shape=np.array([num_capsw_dmy_4x, 1]))
    sw_dmy1= laygen.relplace(name='I'+objectname_pfix+'SWDM0_1x', templatename='space_1x', gridname=pg,
            refinstname=sw_dmy0.name, template_libname=logictemp_lib, shape=np.array([num_capsw_dmy_1x, 1]))
    capsw0=laygen.relplace(name='I'+objectname_pfix+'SW0', templatename='cap_sw_array', gridname=pg, 
            refinstname=sw_dmy1.name, template_libname='clk_dis_generated')
    #Calculate number of sw_dmy1
    capsw0_size_x = laygen.get_template_xy(name='cap_sw_array', gridname=pg, libname='clk_dis_generated')[0]
    sw_dmy1_m = bnd_m-num_capsw_dmy-capsw0_size_x
    #Place sw_dmy1
    sw_dmy1_m_4x = int(sw_dmy1_m / 4)
    sw_dmy1_m_1x = sw_dmy1_m - 4 * sw_dmy1_m_4x
    sw_dmy0= laygen.relplace(name='I'+objectname_pfix+'SWDM1_4x', templatename='space_4x', gridname=pg,
            refinstname=capsw0.name, template_libname=logictemp_lib, shape=np.array([sw_dmy1_m_4x, 1]))
    sw_dmy1= laygen.relplace(name='I'+objectname_pfix+'SWDM1_1x', templatename='space_1x', gridname=pg,
            refinstname=sw_dmy0.name, template_libname=logictemp_lib, shape=np.array([sw_dmy1_m_1x, 1]))

    ##Mitddle ntap row
    ntap0_0= laygen.relplace(name='I'+objectname_pfix+'NTAP0_0', templatename='ntap_fast_space_nf4', gridname=pg, 
            refinstname=bnd_left[3].name, template_libname=tech+'_microtemplates_dense', shape=np.array([1, 1]), transform='MX')
    ntap0_1= laygen.relplace(name='I'+objectname_pfix+'NTAP0_1', templatename='ntap_fast_center_nf1', gridname=pg, 
            refinstname=ntap0_0.name, template_libname=tech+'_microtemplates_dense', shape=np.array([bnd_m-2*tap4_size_x, 1]), transform='MX')
    ntap0_2= laygen.relplace(name='I'+objectname_pfix+'NTAP0_2', templatename='ntap_fast_space_nf4', gridname=pg, 
            refinstname=ntap0_1.name, template_libname=tech+'_microtemplates_dense', shape=np.array([1, 1]), transform='MX')
    
    ##DFF row
    #Calculate coodinate of dff_dmy0
    bnd_left_5_y = laygen.get_inst_xy(name=bnd_left[5].name, gridname=pg)[1] #y coodinate
    dff_dmy0_xy = np.array([bnd_left_size_x, bnd_left_5_y]) #xy coodinate
    #Place dff_dmy0, tgated0, dff0, inv0, and inv1 
    num_dff_dmy_4x = int(num_dff_dmy / 4)
    num_dff_dmy_1x = num_dff_dmy - 4 * num_dff_dmy_4x
    dff_dmy0_0 = laygen.place(name='I'+objectname_pfix+'DFFDM0_4x', templatename='space_4x', gridname=pg, xy=dff_dmy0_xy,
            template_libname=logictemp_lib, shape=np.array([num_dff_dmy_4x, 1]), transform='MX')
    dff_dmy1= laygen.relplace(name='I'+objectname_pfix+'DFFDM0_1x', templatename='space_1x', gridname=pg,
            refinstname=dff_dmy0_0.name, template_libname=logictemp_lib, shape=np.array([num_dff_dmy_1x, 1]), transform='MX')
    tgated0=laygen.relplace(name='I'+objectname_pfix+'TGD0', templatename='tgate_dn_'+str(m_tgate)+'x', gridname=pg, 
            refinstname=dff_dmy0_0.name, template_libname=logictemp_lib, transform='R180')
    dff0=laygen.relplace(name='I'+objectname_pfix+'DFF0', templatename='dff_strsth_ckb_'+str(m_dff)+'x', gridname=pg, 
            refinstname=tgated0.name, template_libname=tech+'_logic_templates', transform='MX')
    inv0=laygen.relplace(name='I'+objectname_pfix+'INV0', templatename='inv_'+str(m_inv1)+'x', gridname=pg, 
            refinstname=dff0.name, template_libname=tech+'_logic_templates', transform='MX')
    inv1=laygen.relplace(name='I'+objectname_pfix+'INV1', templatename='inv_'+str(m_inv2)+'x', gridname=pg, 
            refinstname=inv0.name, template_libname=tech+'_logic_templates', transform='MX')
    #Calculate number of dff_dmy1
    inv1_x = laygen.get_inst_xy(name=inv1.name, gridname=pg)[0]
    m_inv1_x = laygen.get_template_xy(name='inv_' + str(m_inv2) + 'x', gridname=pg, libname=tech + '_logic_templates')[0]
    bnd_right_5_x = laygen.get_inst_xy(name=bnd_right[5].name, gridname=pg)[0] #y coodinate
    dff_dmy1_m = bnd_right_5_x-(inv1_x+m_inv1_x)
    ##Calculate coodinate of dff_dmy1
    dff_dmy1_x = inv1_x+m_inv1_x
    dff_dmy1_xy = np.array([dff_dmy1_x, bnd_left_5_y])
    dff_dmy1_m_4x = int(dff_dmy1_m / 4)
    dff_dmy1_m_1x = dff_dmy1_m - 4 * dff_dmy1_m_4x
    dff_dmy0= laygen.place(name='I'+objectname_pfix+'DFFDM1_4x', templatename='space_4x', gridname=pg, xy=dff_dmy1_xy,
            template_libname=logictemp_lib, shape=np.array([dff_dmy1_m_4x, 1]), transform='MX')
    dff_dmy1= laygen.relplace(name='I'+objectname_pfix+'DFFDM1_1x', templatename='space_1x', gridname=pg,
            refinstname=dff_dmy0.name, template_libname=logictemp_lib, shape=np.array([dff_dmy1_m_1x, 1]), transform='MX')
    
    ##Top ptap row
    ptap1_0 = laygen.relplace(name='I'+objectname_pfix+'PTAP1_0', templatename='ptap_fast_space_nf4', 
                    gridname=pg, refinstname=bnd_left[6].name, template_libname=tech+'_microtemplates_dense',
                    transform='MX')
    ptap1_1= laygen.relplace(name='I'+objectname_pfix+'PTAP1_1', templatename='ptap_fast_center_nf1', 
                    gridname=pg, refinstname=ptap1_0.name, template_libname=tech+'_microtemplates_dense',
                    shape=np.array([bnd_m-2*tap4_size_x, 1]), transform='MX')
    ptap1_2 = laygen.relplace(name='I'+objectname_pfix+'PTAP1_2', templatename='ptap_fast_space_nf4', 
                    gridname=pg, refinstname=ptap1_1.name, template_libname=tech+'_microtemplates_dense',
                    transform='MX')
    
    #####Route and Pin

    #Connection between DFFs, tage_up and inverts
    #route from dff_O to inv0_I
    dff0_O_xy = laygen.get_inst_pin_xy(dff0.name, 'O', rg_m3m4)[0]
    dff0_O_y = dff0_O_xy[1]
    inv0_I_xy = laygen.get_inst_pin_xy(inv0.name, 'I', rg_m3m4)[0]
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], dff0_O_xy, inv0_I_xy, dff0_O_y-2, rg_m3m4)
    #route from inv0_O to inv1_I
    inv0_O_xy = laygen.get_inst_pin_xy(inv0.name, 'O', rg_m3m4)[0]
    inv1_I_xy = laygen.get_inst_pin_xy(inv1.name, 'I', rg_m3m4)[0]
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], inv0_O_xy, inv1_I_xy, dff0_O_y-1, rg_m3m4)
    #route from inv1_O to tgated_EN
    inv1_O_xy = laygen.get_inst_pin_xy(inv1.name, 'O', rg_m3m4)[0]
    tgated_EN_xy = laygen.get_inst_pin_xy(tgated0.name, 'EN', rg_m3m4)[0]
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], inv1_O_xy, tgated_EN_xy, dff0_O_y-5, rg_m3m4)
    #route from inv0_O to tgated_ENB
    inv0_O_xy = laygen.get_inst_pin_xy(inv0.name, 'O', rg_m3m4)[0]
    tgated_ENB_xy = laygen.get_inst_pin_xy(tgated0.name, 'ENB', rg_m3m4)[0]
    laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], inv0_O_xy, tgated_ENB_xy, dff0_O_y-6, rg_m3m4)
    #route from dff0_CLKB to tgated_IN
    dff0_CLKB_xy = laygen.get_inst_pin_xy(dff0.name, 'CLKB', rg_m3m4)[0]
    tgated_I_xy = laygen.get_inst_pin_xy(tgated0.name, 'I_' + str(m_in - 1), rg_m3m4)[0]
    if clock_pulse == False:
        laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], dff0_CLKB_xy, tgated_I_xy, dff0_O_y-1, rg_m3m4)
        for i in range(m_in):
                clkiv=laygen.via(None, np.array([tgated_I_xy[0]+2*i, dff0_O_y-1]), gridname=rg_m3m4)
    else:
        for i in range(m_in):
            tgated_I_xy = laygen.get_inst_pin_xy(tgated0.name, 'I_' + str(i), rg_m3m4)[0]
            laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][3],
                            xy0=tgated_EN_xy, xy1=tgated_I_xy, gridname0=rg_m3m4,
                         via0=[0,0])

    #I/O and Pin
    #I Pin
    i_xy=laygen.get_inst_pin_xy(dff0.name, 'I', rg_m3m4)
    ipp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0,0]), xy1=np.array([0,1]), gridname0=rg_m3m4,
                      refinstname0=dff0.name, refpinname0='I', refinstindex0=np.array([0, 0]),
                      refinstname1=dff0.name, refpinname1='I', refinstindex1=np.array([0, 0])
                      )
    laygen.boundary_pin_from_rect(ipp, gridname=rg_m3m4, name='I', layer=laygen.layers['pin'][3], size=3,
                                  direction='top')
    #O Pin
    o_xy=laygen.get_inst_pin_xy(dff0.name, 'O', rg_m3m4)
    opp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0,0]), xy1=np.array([0,1]), gridname0=rg_m3m4,
                      refinstname0=inv1.name, refpinname0='O', refinstindex0=np.array([0, 0]),
                      refinstname1=inv1.name, refpinname1='O', refinstindex1=np.array([0, 0])
                      )
    laygen.boundary_pin_from_rect(opp, gridname=rg_m3m4, name='O', layer=laygen.layers['pin'][3], size=3,
                                  direction='top')

    #CAL signal and pin
    for i in range(num_bits):
        capswp0=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0,0]), xy1=np.array([0, len_cal]), gridname0=rg_m3m4,
                      refinstname0=capsw0.name, refpinname0='EN<'+str(i)+'>', refinstindex0=np.array([0, 0]),
                      refinstname1=capsw0.name, refpinname1='EN<'+str(i)+'>', refinstindex1=np.array([0, 0])
                      )
        laygen.boundary_pin_from_rect(capswp0, gridname=rg_m3m4, name='CAL<' + str(i) + '>',
                                      layer=laygen.layers['pin'][3], size=1, direction='top')

    #CAPSW signal and pin
    for i in range(num_bits):
        ctrlp0=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0,0]), xy1=np.array([0,-1*len_capsw]), gridname0=rg_m3m4,
                      refinstname0=capsw0.name, refpinname0='VO<'+str(i)+'>', refinstindex0=np.array([0, 0]),
                      refinstname1=capsw0.name, refpinname1='VO<'+str(i)+'>', refinstindex1=np.array([0, 0])
                      )
        laygen.boundary_pin_from_rect(ctrlp0, gridname=rg_m3m4, name='CAPSW<' + str(i) + '>',
                                      layer=laygen.layers['pin'][3], size=1, direction='bottom')

    if clock_pulse == False: clki_x = laygen.get_inst_pin_xy(tgated0.name, 'I_0', rg_m3m4)[0]
    else: clki_x = dff0_CLKB_xy
    clkp_x = laygen.grids.get_absgrid_coord_x(gridname=rg_m4m5, x=phy_width/2)    
    ##Create muti tracks to clki and create pin
    for i in range(m_clki):
        if clock_pulse==False:
            for j in range(m_in):
                clkiv=laygen.via(None, np.array([clki_x[0]-2*j, clki_x[1]+y1_clki+2*i]), gridname=rg_m3m4)
                laygen.route(None, laygen.layers['metal'][3], xy0=np.array([clki_x[0]-2*j, clki_x[1]]), xy1=np.array([clki_x[0]-2*j, clki_x[1]+y1_clki+2*(m_clki-1)]), gridname0=rg_m3m4)
                if i==0 and j==m_in-1:
                    v_xy=laygen.get_inst_xy(name = clkiv.name, gridname = rg_m4m5)
            clki_d=clkp_x-v_xy[0]
        else:
            clkiv = laygen.via(None, np.array([clki_x[0], clki_x[1] + y1_clki + 2 * i]), gridname=rg_m3m4)
            laygen.route(None, laygen.layers['metal'][3], xy0=np.array([clki_x[0], clki_x[1]]),
                         xy1=np.array([clki_x[0], clki_x[1] + y1_clki + 2 * (m_clki - 1)]), gridname0=rg_m3m4)
            if i == 0:
                v_xy = laygen.get_inst_xy(name=clkiv.name, gridname=rg_m4m5)
            clki_d = clkp_x - v_xy[0]
        for j in range(m_clki):
            [clkh, clkv]=laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], np.array([v_xy[0]-1, v_xy[1]+2*i]), 
                    np.array([v_xy[0]+clki_d+m_clki/2-2*j+1,v_xy[1]+y2_clki]), rg_m4m5)
            if (i==0):
                laygen.boundary_pin_from_rect(clkv, gridname=rg_m4m5, name='CLKI_' + str(j),
                                              layer=laygen.layers['pin'][5], size=2, direction='bottom',
                                              netname='CLKI')

    # prboundary
    y_grid = laygen.get_template('boundary_bottom', libname=utemplib).size[1]
    size_y = (int(laygen.get_rect(clkv.name).xy1[1]/y_grid)+1)*y_grid
    size_x = laygen.get_inst(bnd_right[-1].name).xy[0] + laygen.get_inst(bnd_right[-1].name).size[0]
    print('prb:', size_x, size_y)
    laygen.add_rect(None, np.array([origin, origin + np.array([size_x, size_y])]), laygen.layers['prbnd'])

    #laygen.boundary_pin_from_rect(clkv, gridname=rg_m4m5, pinname='CLKI', layer=laygen.layers['pin'][5], size=1, direction='top')

    clko_x = laygen.get_inst_pin_xy(tgated0.name, 'O_0', rg_m3m4)[0]
    ##Create muti tracks to clko and create pin
    for i in range(m_clko):
        for j in range(m_out):
            clkov=laygen.via(None, np.array([clko_x[0]+2*j, clko_x[1]-y1_clko-2*i]), gridname=rg_m3m4)
            laygen.route(None, laygen.layers['metal'][3], xy0=np.array([clko_x[0]+2*j, clko_x[1]]), xy1=np.array([clko_x[0]+2*j, clko_x[1]-y1_clko-2*(m_clko-1)]), gridname0=rg_m3m4)
            if i==0 and j==0:
                v_xy=laygen.get_inst_xy(name = clkov.name, gridname = rg_m4m5)
        clko_d=clkp_x-v_xy[0]
        for j in range(m_clko):
            [clkh, clkv]=laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], np.array([v_xy[0]-1, v_xy[1]-2*i]), 
                    np.array([v_xy[0]+clko_d-m_clko/2+2*j,v_xy[1]-y2_clko]), rg_m4m5)
            if (i==0):
                laygen.boundary_pin_from_rect(clkv, gridname=rg_m4m5, name='CLKO_' + str(j),
                                              layer=laygen.layers['pin'][5], size=1, direction='bottom',
                                              netname='CLKO')

    #####VSS and VDD
    ##Bottom ptap row
    #Generate horizental metal
    vss0_y = laygen.get_inst_pin_xy(ptap0_1.name, 'TAP0', rg_m1m2_thick)[0][1]
    rvss0 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, vss0_y]), xy1=np.array([width, vss0_y]), gridname0=rg_m1m2_thick)
    vss0_1_y = laygen.get_inst_pin_xy(sw_dmy0.name, 'VSS', rg_m1m2)[0][1]
    rvss0_1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, vss0_1_y]), xy1=np.array([width, vss0_1_y]), gridname0=rg_m1m2)
    #Generate thick viaes
    for i in range(0, bnd_m-2, 2):
        laygen.via(None, np.array([0, 0]), refinstname=ptap0_1.name, refpinname='TAP0', refinstindex=np.array([i-tap4_size_x+1, 0]), gridname=rg_m1m2_thick)
    #Generate left cotacts and metals
    for i in range(0, num_capsw_dmy, 2):
        v_x = laygen.get_inst_pin_xy(ptap0_1.name, 'TAP0', rg_m1m2, index=np.array([i-tap4_size_x+1, 0]))[0][0]
        v_y = laygen.get_inst_pin_xy(sw_dmy0.name, 'VSS', rg_m1m2)[0][1]
        laygen.via(None, np.array([v_x, v_y]), gridname=rg_m1m2)
        # laygen.via(None, np.array([0, 3]), refinstname=ptap0_1.name, refpinname='TAP0', refinstindex=np.array([i-tap4_size_x+1, 0]), gridname=rg_m1m2)
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 3]), gridname0=rg_m1m2,
                        refinstname0=ptap0_1.name, refpinname0='TAP0', refinstindex0=np.array([i-tap4_size_x+1, 0]),
                        refinstname1=ptap0_1.name, refpinname1='TAP0', refinstindex1=np.array([i-tap4_size_x+1, 0]))
    laygen.via(None, np.array([0, 0]), refinstname=ptap0_1.name, refpinname='TAP1', refinstindex=np.array([bnd_m-2*tap4_size_x+2, 0]), gridname=rg_m1m2_thick)
    #Generate right contacts and metals
    for i in range(num_capsw_dmy+capsw0_size_x, bnd_m, 2):
        v_x = laygen.get_inst_pin_xy(ptap0_1.name, 'TAP0', rg_m1m2, index=np.array([i-3, 0]))[0][0]
        v_y = laygen.get_inst_pin_xy(sw_dmy0.name, 'VSS', rg_m1m2)[0][1]
        laygen.via(None, np.array([v_x, v_y]), gridname=rg_m1m2)
        # laygen.via(None, np.array([0, 3]), refinstname=ptap0_1.name, refpinname='TAP0', refinstindex=np.array([i-3, 0]), gridname=rg_m1m2)
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 3]), gridname0=rg_m1m2,
                        refinstname0=ptap0_1.name, refpinname0='TAP0', refinstindex0=np.array([i-tap4_size_x+1, 0]),
                        refinstname1=ptap0_1.name, refpinname1='TAP0', refinstindex1=np.array([i-tap4_size_x+1, 0]))
    #laygen.boundary_pin_from_rect(rvss0, gridname=rg_m1m2_thick, pinname='VSS0', layer=laygen.layers['pin'][2], size=1, direction='left', netname='VSS:')
    #laygen.pin(gridname=rg_m1m2_thick, name='VSS0', layer=laygen.layers['pin'][2], refobj=rvss0, netname='VSS:') 
    #laygen.pin(gridname=rg_m1m2, name='VSS0_1', layer=laygen.layers['pin'][2], refobj=rvss0_1, netname='VSS:') 
    
    ##Middle ntap row
    #Generatre horizental metal
    vdd0_y = laygen.get_inst_pin_xy(dff0.name, 'VDD', rg_m2m3_mos)[0][1]
    rvdd0 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, vdd0_y]), xy1=np.array([width, vdd0_y]), gridname0=rg_m2m3_mos)
    vdd0_1_y = laygen.get_inst_pin_xy(sw_dmy0.name, 'VDD', rg_m1m2)[0][1]
    rvdd0_1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, vdd0_1_y]), xy1=np.array([width, vdd0_1_y]), gridname0=rg_m1m2)
    ####rvdd0_2 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, vdd0_2_y]), xy1=np.array([width, vdd0_2_y]), gridname0=rg_m1m2_thick)
    #Generate vias
    # if pmos_body=='VDD':
    #     for i in range(0, bnd_m-2, 2):
    #        laygen.via(None, np.array([0, 0]), refinstname=ntap0_1.name, refpinname='TAP0', refinstindex=np.array([i-tap4_size_x+1, 0]), gridname=rg_m1m2)
    #laygen.via(None, np.array([0, 0]), refinstname=ntap0_1.name, refpinname='TAP1', refinstindex=np.array([bnd_m-2*tap4_size_x+2, 0]), gridname=rg_m1m2) 
    #Generate left contacts and metals
    for i in range(0, num_dff_dmy, 2):
        if pmos_body=='VDD':
            v_x = laygen.get_inst_pin_xy(ntap0_1.name, 'TAP0', rg_m1m2, index=np.array([i-tap4_size_x+1, 0]))[0][0]
            v_y = laygen.get_inst_pin_xy(sw_dmy0.name, 'VDD', rg_m1m2)[0][1]
            laygen.via(None, np.array([v_x, v_y]), gridname=rg_m1m2)
            # laygen.via(None, np.array([0, 3]), refinstname=ntap0_1.name, refpinname='TAP0', refinstindex=np.array([i-tap4_size_x+1, 0]), gridname=rg_m1m2)
            laygen.via(None, np.array([0, -1]), refinstname=ntap0_1.name, refpinname='TAP0', refinstindex=np.array([i-tap4_size_x+1, 0]), gridname=rg_m1m2)
        else:
            if i < 10:
                laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                             gridname0=rg_m1m2,
                             refinstname0=ntap0_1.name, refpinname0='TAP0',
                             refinstindex0=np.array([i - tap4_size_x + 1, 0]),
                             refinstname1=ptap0_1.name, refpinname1='TAP0',
                             refinstindex1=np.array([i - tap4_size_x + 1, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, -1]), xy1=np.array([0, 3]), gridname0=rg_m1m2,
                        refinstname0=ntap0_1.name, refpinname0='TAP0', refinstindex0=np.array([i-tap4_size_x+1, 0]),
                        refinstname1=ntap0_1.name, refpinname1='TAP0', refinstindex1=np.array([i-tap4_size_x+1, 0]))

    #Generate right contacts and metals
    for i in range(dff_dmy1_x-tap4_size_x-bnd_left_size_x+1, bnd_m-tap4_size_x, 2):
        if pmos_body=='VDD':
            v_x = laygen.get_inst_pin_xy(ntap0_1.name, 'TAP0', rg_m1m2, index=np.array([i, 0]))[0][0]
            v_y = laygen.get_inst_pin_xy(sw_dmy0.name, 'VDD', rg_m1m2)[0][1]
            laygen.via(None, np.array([v_x, v_y]), gridname=rg_m1m2)
            # laygen.via(None, np.array([0, 3]), refinstname=ntap0_1.name, refpinname='TAP0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
            laygen.via(None, np.array([0, -1]), refinstname=ntap0_1.name, refpinname='TAP0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        else:
            if i > bnd_m - tap4_size_x - 10:
                laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 0]),
                             gridname0=rg_m1m2,
                             refinstname0=ntap0_1.name, refpinname0='TAP0',
                             refinstindex0=np.array([i - tap4_size_x + 1, 0]),
                             refinstname1=ptap0_1.name, refpinname1='TAP0',
                             refinstindex1=np.array([i - tap4_size_x + 1, 0]))
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, -1]), xy1=np.array([0, 3]), gridname0=rg_m1m2,
                        refinstname0=ntap0_1.name, refpinname0='TAP0', refinstindex0=np.array([i, 0]),
                        refinstname1=ntap0_1.name, refpinname1='TAP0', refinstindex1=np.array([i, 0]))

    #laygen.boundary_pin_from_rect(rvdd0, gridname=rg_m1m2_thick, pinname='VDD', layer=laygen.layers['pin'][2], size=1, direction='left')
    #laygen.pin(gridname=rg_m1m2_thick, name='VDD0', layer=laygen.layers['pin'][2], refobj=rvdd0, netname='VDD') 
    #laygen.pin(gridname=rg_m1m2, name='VDD0_1', layer=laygen.layers['pin'][2], refobj=rvdd0_1, netname='VDD') 
    
    ##Top ptap row
    #Generatre horizental metal
    vss1_y = laygen.get_inst_pin_xy(ptap1_1.name, 'TAP0', rg_m1m2_thick)[0][1]
    rvss1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, vss1_y]), xy1=np.array([width, vss1_y]), gridname0=rg_m1m2_thick)
    ####rvss0_1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, vss1_1_y-0.5]), xy1=np.array([width, vss1_1_y]), gridname0=rg_m1m2)
    #Generate viaes 
    for i in range(0, bnd_m-2, 2):
        laygen.via(None, np.array([0, 0]), refinstname=ptap1_1.name, refpinname='TAP0', refinstindex=np.array([i-tap4_size_x+1, 0]), gridname=rg_m1m2_thick)
    laygen.via(None, np.array([0, 0]), refinstname=ptap1_1.name, refpinname='TAP1', refinstindex=np.array([bnd_m-2*tap4_size_x+2, 0]), gridname=rg_m1m2_thick) 
    #Generate left contacts and metals
    for i in range(0, num_dff_dmy, 2):
        laygen.via(None, np.array([i+1, 0]), refinstname=dff_dmy0_0.name, refpinname='VSS', refinstindex=np.array([0, 0]), gridname=rg_m1m2)
        # laygen.via(None, np.array([0, 3]), refinstname=ptap1_1.name, refpinname='TAP0', refinstindex=np.array([i-tap4_size_x+1, 0]), gridname=rg_m1m2)
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 3]), gridname0=rg_m1m2,
                        refinstname0=ptap1_1.name, refpinname0='TAP0', refinstindex0=np.array([i-tap4_size_x+1, 0]),
                        refinstname1=ptap1_1.name, refpinname1='TAP0', refinstindex1=np.array([i-tap4_size_x+1, 0]))
    #Generate right contacts and metals
    for i in range(dff_dmy1_x-tap4_size_x-bnd_left_size_x+1, bnd_m-tap4_size_x, 2):
        laygen.via(None, np.array([i+1-(dff_dmy1_x-tap4_size_x-bnd_left_size_x+1), 0]), refinstname=dff_dmy0.name, refpinname='VSS', refinstindex=np.array([0, 0]), gridname=rg_m1m2)
        # laygen.via(None, np.array([0, 3]), refinstname=ptap1_1.name, refpinname='TAP0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.route(None, laygen.layers['metal'][1], xy0=np.array([0, 0]), xy1=np.array([0, 3]), gridname0=rg_m1m2,
                        refinstname0=ptap1_1.name, refpinname0='TAP0', refinstindex0=np.array([i, 0]),
                        refinstname1=ptap1_1.name, refpinname1='TAP0', refinstindex1=np.array([i, 0]))
    #laygen.pin(gridname=rg_m1m2_thick, name='VSS1', layer=laygen.layers['pin'][2], refobj=rvss1, netname='VSS:')
    
    ##ST, RST
    st_xy=laygen.get_inst_pin_xy(dff0.name, 'ST', rg_m3m4)
    stp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0,0]), xy1=np.array([0,1]), gridname0=rg_m3m4,
                      refinstname0=dff0.name, refpinname0='ST', refinstindex0=np.array([0, 0]),
                      refinstname1=dff0.name, refpinname1='ST', refinstindex1=np.array([0, 0])
                      )
    laygen.boundary_pin_from_rect(stp, gridname=rg_m3m4, name='ST', layer=laygen.layers['pin'][3], size=1,
                                  direction='top')
    rst_xy=laygen.get_inst_pin_xy(dff0.name, 'RST', rg_m3m4)
    rstp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0,0]), xy1=np.array([0,1]), gridname0=rg_m3m4,
                      refinstname0=dff0.name, refpinname0='RST', refinstindex0=np.array([0, 0]),
                      refinstname1=dff0.name, refpinname1='RST', refinstindex1=np.array([0, 0])
                      )
    laygen.boundary_pin_from_rect(rstp, gridname=rg_m3m4, name='RST', layer=laygen.layers['pin'][3], size=1,
                                  direction='top')


    #num_vss_vleft = 2
    #num_vdd_vleft = 2

    ##Virtical vss and vdd traces left
    vss0_y = laygen.get_inst_pin_xy(ptap0_1.name, 'TAP0', rg_m2m3_thick2)[0][1]
    vss1_y = laygen.get_inst_pin_xy(ptap1_1.name, 'TAP0', rg_m2m3_thick2)[0][1]
    vdd0_y = laygen.get_inst_pin_xy(dff0.name, 'VDD', rg_m2m3_mos)[0][1]
    for i in range (num_vss_vleft):
        vssx=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, vss0_y]), xy1=np.array([2*i, vss1_y]), gridname0=rg_m2m3_thick2, 
                endstyle0="extend", endstyle1="extend")
        #laygen.pin(gridname=rg_m2m3_thick2, name='VSS0_'+str(i), layer=laygen.layers['pin'][3], refobj=vssx, netname='VSS') 
        laygen.via(None, xy=np.array([2*i,vss0_y]), gridname=rg_m2m3_thick2)
        laygen.via(None, xy=np.array([2*i,vss1_y]), gridname=rg_m2m3_thick2)

    for i in range (num_vdd_vleft):
        vddx=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*num_vss_vleft+2*i, vss0_y]), xy1=np.array([2*num_vss_vleft+2*i, vss1_y]), 
                gridname0=rg_m2m3_thick2, endstyle0="extend", endstyle1="extend")
        #laygen.pin(gridname=rg_m2m3_thick2, name='VDD0_'+str(i), layer=laygen.layers['pin'][3], refobj=vddx, netname='VDD') 
        laygen.via(None, xy=np.array([2*num_vss_vleft+2*i,vdd0_y]), gridname=rg_m2m3_mos)    
        laygen.via(None, xy=np.array([2*num_vss_vleft+2*i,vdd0_1_y]), gridname=rg_m2m3)    

    #num_vss_vright = 3
    #num_vdd_vright = 3
    ##Virtical vss and vdd traces left
    width =laygen.grids.get_absgrid_coord_x(gridname=rg_m2m3_thick2, x=phy_width)
    for i in range (num_vss_vright):
        vssx=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([width-2*i, vss0_y]), xy1=np.array([width-2*i, vss1_y]), 
                gridname0=rg_m2m3_thick2, endstyle0="extend", endstyle1="extend")
        #laygen.pin(gridname=rg_m2m3_thick2, name='VSS1_'+str(i), layer=laygen.layers['pin'][3], refobj=vssx, netname='VSS') 
        laygen.via(None, xy=np.array([width-2*i,vss0_y]), gridname=rg_m2m3_thick2)
        laygen.via(None, xy=np.array([width-2*i,vss1_y]), gridname=rg_m2m3_thick2)

    for i in range (num_vdd_vright):
        vddx=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([width-2*num_vss_vright-2*i, vss0_y]), xy1=np.array([width-2*num_vss_vright-2*i, vss1_y]), 
                gridname0=rg_m2m3_thick2, endstyle0="extend", endstyle1="extend")
        #laygen.pin(gridname=rg_m2m3_thick2, name='VDD1_'+str(i), layer=laygen.layers['pin'][3], refobj=vddx, netname='VDD')
        laygen.via(None, xy=np.array([width-2*num_vss_vright-2*i,vdd0_y]), gridname=rg_m2m3_mos)
        laygen.via(None, xy=np.array([width-2*num_vss_vright-2*i,vdd0_1_y]), gridname=rg_m2m3)

    #num_vss_h = 4
    for i in range(num_vss_h):
        vsslx=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, vss0_y+i+1]), xy1=np.array([(num_vss_vleft+num_vdd_vleft-1)*2, vss0_y+i+1]), gridname0=rg_m3m4_thick2, 
                endstyle0="extend", endstyle1="extend")
        laygen.pin(gridname=rg_m3m4_thick2, name='VSS0_'+str(i), layer=laygen.layers['pin'][4], refobj=vsslx, netname='VSS') 
        vssrx=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([width, vss0_y+i+1]), xy1=np.array([width-2*(num_vss_vright+num_vdd_vright-1), vss0_y+i+1]), gridname0=rg_m3m4_thick2, 
                endstyle0="extend", endstyle1="extend")
        laygen.pin(gridname=rg_m3m4_thick2, name='VSS1_'+str(i), layer=laygen.layers['pin'][4], refobj=vssrx, netname='VSS') 
        for j in range(num_vss_vleft):
            laygen.via(None, xy=np.array([2*j,vss0_y+i+1]), gridname=rg_m3m4_thick2)
        for j in range(num_vss_vright):
            laygen.via(None, xy=np.array([width-2*j,vss0_y+i+1]), gridname=rg_m3m4_thick2)

    #num_vdd_h = 4
    for i in range(num_vdd_h):
        vddlx=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, vss1_y-i-1]), xy1=np.array([(num_vss_vleft+num_vdd_vleft-1)*2, vss1_y-i-1]), gridname0=rg_m3m4_thick2, 
                endstyle0="extend", endstyle1="extend")
        laygen.pin(gridname=rg_m3m4_thick2, name='VDD0_'+str(i), layer=laygen.layers['pin'][4], refobj=vddlx, netname='VDD') 
        vddrx=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([width, vss1_y-i-1]), xy1=np.array([width-2*(num_vss_vright+num_vdd_vright-1), vss1_y-i-1]), gridname0=rg_m3m4_thick2, 
                endstyle0="extend", endstyle1="extend")
        laygen.pin(gridname=rg_m3m4_thick2, name='VDD1_'+str(i), layer=laygen.layers['pin'][4], refobj=vddrx, netname='VDD') 
        for j in range(num_vdd_vleft):
            laygen.via(None, xy=np.array([(num_vss_vleft+j)*2,vss1_y-i-1]), gridname=rg_m3m4_thick2)
        for j in range(num_vdd_vright):
            laygen.via(None, xy=np.array([width-(num_vss_vright+j)*2,vss1_y-i-1]), gridname=rg_m3m4_thick2)


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

    # library load or generation
    workinglib = 'clk_dis_generated'
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
    laygen.load_template(filename='adc_sar_generated.yaml', libname='adc_sar_generated')
    if os.path.exists(workinglib + '.yaml'):  # generated layout file exists
        laygen.load_template(filename=workinglib + '.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    #params
    params = dict(
        num_bits = 5,
        phy_width = 20.16,   #in um
        num_capsw_dmy = 10,    #capsw left dummy number
        num_dff_dmy = 40,     #dff left dummy number
        len_cal = 30,        #calibration input length
        len_capsw = 10,      #cap control output length

        #clock input
        m_clki = 24,
        y1_clki = 7,
        y2_clki = 8,

        #clock output
        m_clko = 2,
        y1_clko = 15,
        y2_clko = 20,

        #virtically vss and vdd metals
        num_vss_vleft = 3,
        num_vdd_vleft = 2,
        num_vss_vright = 3,
        num_vdd_vright = 3,
        num_vss_h =4,
        num_vdd_h=4,

        #size
        m_dff=2, 
        m_inv1=6, 
        m_inv2=8, 
        m_tgate=18, 
    )
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        params['m_dff']=sizedict['clk_dis_cell']['m_dff']
        params['m_inv1']=sizedict['clk_dis_cell']['m_inv1']
        params['m_inv2']=sizedict['clk_dis_cell']['m_inv2']
        params['m_tgate']=sizedict['clk_dis_cell']['m_tgate']
        params['m_clko'] = sizedict['clk_dis_htree']['m_clko']
        params['m_clki']=sizedict['clk_dis_htree']['m_track']
        params['num_bits']=sizedict['clk_dis_cdac']['num_bits']
        params['clock_pulse']=specdict['clk_pulse_overlap']
        params['pmos_body']=specdict['pmos_body']

    load_from_file=True
    if load_from_file==True:
        #load parameters
        params['phy_width']=laygen.get_template_xy(name='sar_wsamp', libname='adc_sar_generated')[0]
    #grid
    grid = dict(
        pg = 'placement_basic', #placement grid
        rg_m1m2 = 'route_M1_M2_cmos',
        rg_m1m2_thick = 'route_M1_M2_basic_thick',
        rg_m2m3 = 'route_M2_M3_cmos',
        rg_m2m3_mos = 'route_M2_M3_mos',
        rg_m2m3_thick = 'route_M2_M3_thick',
        rg_m2m3_thick2 = 'route_M2_M3_thick_basic',
        rg_m3m4 = 'route_M3_M4_basic',
        rg_m3m4_dense = 'route_M3_M4_dense',
        rg_m3m4_thick2 = 'route_M3_M4_basic_thick',
        rg_m4m5 = 'route_M4_M5_basic',
        rg_m5m6 = 'route_M5_M6_basic',
        rg_m6m7 = 'route_M6_M7_basic',
        rg_m1m2_pin = 'route_M1_M2_basic',
        rg_m2m3_pin = 'route_M2_M3_basic',
    )

    #display
    #laygen.display()
    #laygen.templates.display()
    #laygen.save_template(filename=workinglib+'_templates.yaml', libname=workinglib)

    print(workinglib)

    mycell_list=[]

    cellname='clk_dis_cell'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_clkdis_cell(laygen, objectname_pfix='CKD0', logictemp_lib=logictemplib, working_lib=workinglib, grid=grid, 
                        origin=np.array([0, 0]), **params)
    laygen.add_template_from_cell()

    print(mycell_list)

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

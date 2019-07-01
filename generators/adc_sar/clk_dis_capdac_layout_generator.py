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
A simple capacitive DAC generation with programmable bits, dimmensions and Cunit
"""
import laygo
import numpy as np
import os
import yaml
import math

def generate_capdac(laygen, objectname_pfix, placement_grid, routing_grid_m3m4,
                    devname_cap_body='momcap_center', devname_cap_dmy='momcap_dmy', 
                    devname_cap_boundary='momcap_boundary',
                    devname_list_overlay_body=[],
                    devname_list_overlay_dmy=[],
                    devname_list_overlay_boundary_bottom=[],
                    devname_list_overlay_boundary_top=[],
                    devname_list_overlay_boundary_left=[],
                    devname_list_overlay_boundary_right=[],
                    m_unit=1,
                    num_bits_vertical=5,
                    m_vertical=np.array([1,2,4,8,16,32]),
                    num_bits_horizontal=2,
                    m_horizontal=np.array([64, 64]),
                    num_space_left=1,
                    num_space_right=1,
                    num_space_top=1,
                    num_space_bottom=1,
                    origin=np.array([0, 0])):

    """
    Generate a capdac array

    Parameters
    ----------
    laygen : GridLayoutGenerator object
    objectname_pfix : prefix of the object name
    placement_grid : placement grid name
    routing_grid_m3m4 : m3m4 routing grid name (for i/o routings)
    devname_cap_body : unit cap name
    devname_cap_dmy : dummy cap name
    devname_cap_boundary : boundary name
    m_unit : multiplier of unit cap
    num_bits_vertical : number of bits in vertical diretion
    num_bits_horizontal : number of bits in horizontal direction
    num_col_space_right : number of dummy columns in right side
    origin : origin of instance
    """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4
    m=m_unit

    # placement
    #left boundaries
    ibndbl0 = laygen.place(name = "I" + objectname_pfix + "BNDBL0", templatename = devname_cap_boundary,
                           gridname = pg, xy=origin, shape=np.array([num_space_left, num_space_bottom]))
    ibndl0 = laygen.relplace(name = "I" + objectname_pfix + "BNDL0", templatename = devname_cap_boundary,
                             gridname = pg, refinstname=ibndbl0.name, shape=np.array([num_space_left, m*2**num_bits_vertical]), direction='top')
    ibndtl0 = laygen.relplace(name = "I" + objectname_pfix + "BNDTL0", templatename = devname_cap_boundary,
                              gridname = pg, refinstname=ibndl0.name, shape=np.array([num_space_left, num_space_top]), direction='top')
    ibndb=[]
    ibndb.append(laygen.relplace(name="I" + objectname_pfix + 'BNDB0', templatename=devname_cap_boundary,
                                 gridname=pg, refinstname=ibndbl0.name, shape=np.array([1, num_space_bottom])))

    #c0 -single, unit sized cap (will be connected to ground)
    ic0 = laygen.relplace(name = "I" + objectname_pfix + "C0", templatename = devname_cap_dmy,
                          gridname = pg, refinstname=ibndb[0].name, shape=np.array([1, m]), direction='top')
    idmydac=[]  #Added at 03/29/2017
    #vdac
    ivdac=[]
    for i in range(num_bits_vertical):
        if i==0: refin=ic0.name
        #ivdac.append(laygen.relplace(name="I" + objectname_pfix + 'VDAC' + str(i), templatename=devname_cap_body,
        #                             gridname=pg, refinstname=refin, shape=np.array([1, m*2**i]), direction='top')) #radix2
        ivdac.append(laygen.relplace(name="I" + objectname_pfix + 'VDAC' + str(i), templatename=devname_cap_body,
                                     gridname=pg, refinstname=refin, shape=np.array([1, m*m_vertical[i]]), direction='top'))
        refin=ivdac[i].name
        if m_vertical[i]<2**i:
            idmy=laygen.relplace(name="I" + objectname_pfix + 'VDACDMY' + str(i), templatename=devname_cap_dmy,
                                     gridname=pg, refinstname=refin, shape=np.array([1, m*(2**i-m_vertical[i])]), direction='top')
            refin=idmy.name
    ibndt=[]
    ibndt.append(laygen.relplace(name="I" + objectname_pfix + 'BNDT0', templatename=devname_cap_boundary,
                                 gridname=pg, refinstname=refin, shape=np.array([1, num_space_top]), direction='top'))
    #hdac
    ihdac=[]
    for i in range(num_bits_horizontal):
        ibndb.append(laygen.relplace(name="I" + objectname_pfix + 'BNDB' + str(i+1), templatename=devname_cap_boundary,
                                     gridname=pg, refinstname=ibndb[-1].name, shape=np.array([2**i, num_space_bottom])))
        #ihdac.append(laygen.relplace(name="I" + objectname_pfix + 'HDAC' + str(i), templatename=devname_cap_body,
        #                             gridname=pg, refinstname=ibndb[-1].name, shape=np.array([2**i, m*2**num_bits_vertical]), direction='top')) #radix2
        ihdac.append(laygen.relplace(name="I" + objectname_pfix + 'HDAC' + str(i), templatename=devname_cap_body,
                                     gridname=pg, refinstname=ibndb[-1].name, shape=np.array([2**i, m*m_horizontal[i]]), direction='top'))
        refin=ihdac[i].name
        if m_horizontal[i]<2**num_bits_vertical:
            idmy=laygen.relplace(name="I" + objectname_pfix + 'HDACDMY' + str(i), templatename=devname_cap_dmy,
                                     gridname=pg, refinstname=refin, shape=np.array([2**i, m*(m*2**num_bits_vertical-m_horizontal[i])]), direction='top')
            refin=idmy.name
        ibndt.append(laygen.relplace(name="I" + objectname_pfix + 'BNDT' + str(i+1), templatename=devname_cap_boundary,
                                     gridname=pg, refinstname=refin, shape=np.array([2**i, num_space_top]), direction='top'))
    #right boundaries
    ibndbr0 =laygen.relplace(name = "I" + objectname_pfix + "BNDBR0", templatename = devname_cap_boundary,
                             gridname = pg, refinstname=ibndb[-1].name, shape=np.array([num_space_right, num_space_bottom]))
    ibndr0 = laygen.relplace(name = "I" + objectname_pfix + "BNDR0", templatename = devname_cap_boundary,
                             gridname = pg, refinstname=ibndbr0.name, shape=np.array([num_space_right, m*2**num_bits_vertical]), direction='top')
    ibndtr0 = laygen.relplace(name = "I" + objectname_pfix + "BNDTR0", templatename = devname_cap_boundary,
                              gridname = pg, refinstname=ibndr0.name, shape=np.array([num_space_right, num_space_top]), direction='top')
    

    ###Added at 03/29/2017
    #overlaied devices (usually for dummies)
    for dev in devname_list_overlay_boundary_left:
        dev0_list=[ibndl0]
        for dev0 in dev0_list:
            xy0 = laygen.get_inst_xy(name = dev0.name, gridname = pg)
            laygen.place(name = None, templatename = dev, gridname = pg, xy=xy0, shape=dev0.shape)
    for dev in devname_list_overlay_boundary_bottom:
        dev0_list=[ibndbl0] + ibndb + [ibndbr0] 
        for dev0 in dev0_list:
            xy0 = laygen.get_inst_xy(name = dev0.name, gridname = pg)
            laygen.place(name = None, templatename = dev, gridname = pg, xy=xy0, shape=dev0.shape)
    for dev in devname_list_overlay_boundary_right:
        dev0_list=[ibndr0]
        for dev0 in dev0_list:
            xy0 = laygen.get_inst_xy(name = dev0.name, gridname = pg)
            laygen.place(name = None, templatename = dev, gridname = pg, xy=xy0, shape=dev0.shape)
    for dev in devname_list_overlay_boundary_top:
        dev0_list=[ibndtl0] + ibndt + [ibndtr0] 
        for dev0 in dev0_list:
            xy0 = laygen.get_inst_xy(name = dev0.name, gridname = pg)
            laygen.place(name = None, templatename = dev, gridname = pg, xy=xy0, shape=dev0.shape)
    for dev in devname_list_overlay_body:
        dev0_list=ivdac+[ic0]+ihdac 
        for dev0 in dev0_list:
            xy0 = laygen.get_inst_xy(name = dev0.name, gridname = pg)
            laygen.place(name = None, templatename = dev, gridname = pg, xy=xy0, shape=dev0.shape)
    for dev in devname_list_overlay_dmy:
        dev0_list=idmydac
        for dev0 in dev0_list:
            xy0 = laygen.get_inst_xy(name = dev0.name, gridname = pg)
            laygen.place(name = None, templatename = dev, gridname = pg, xy=xy0, shape=dev0.shape)

        ##Added at 03/29/2017


    #reference route coordinate
    y0 = 10
    #c0 route
    #rc0=laygen.route(None, laygen.layers['metal'][3], xy0=c_bot_xy + np.array([0, 0]), xy1=np.array([0, y0]), gridname0=rg_m3m4, direction='y')
    #for j in range(m):
    #    laygen.via(None, c_bot_xy2, refinstname=ic0.name, refinstindex=np.array([0, j]), gridname=rg_m3m4)
    #bottom route
    rbot=[]
    for i, c in enumerate(ivdac):
        c_bot_xy = laygen.get_inst_pin_xy(c.name, 'BOTTOM', rg_m3m4, index=np.array([0, m * m_vertical[i] - 1]))[0]
        c_bot_xy2 = laygen.get_template_pin_xy(c.cellname, 'BOTTOM', rg_m3m4)[0]
        rbot.append(laygen.route(None, laygen.layers['metal'][3], xy0=c_bot_xy + np.array([2*i+2, 0]), xy1=np.array([0, y0]), gridname0=rg_m3m4, direction='y'))
        #for j in range(m*2**i): #radix2
        for j in range(m * m_vertical[i]):
            laygen.via(None, c_bot_xy2 + np.array([2*i+2, 0]), refinstname=c.name, refinstindex=np.array([0, j]), gridname=rg_m3m4)
    for i, c in enumerate(ihdac):
        c_bot_xy = laygen.get_inst_pin_xy(c.name, 'BOTTOM', rg_m3m4, index=np.array([0, m * m_horizontal[i] - 1]))[0]
        c_bot_xy2 = laygen.get_template_pin_xy(c.cellname, 'BOTTOM', rg_m3m4)[0]
        rbot.append(laygen.route(None, laygen.layers['metal'][3], xy0=c_bot_xy + np.array([0, 0]), xy1=np.array([0, y0]), gridname0=rg_m3m4, direction='y'))
        #for j in range(m*2**num_bits_vertical):
        for j in range(m*m_horizontal[i]):
            laygen.via(None, c_bot_xy2 + np.array([0, 0]), refinstname=c.name, refinstindex=np.array([0, j]), gridname=rg_m3m4)
        #parallel connections
        for k in range(2**i):
            c_bot_xy3 = laygen.get_inst_pin_xy(c.name, 'BOTTOM', rg_m3m4, index=np.array([k, m * m_horizontal[i] - 1]))[0]
            laygen.route(None, laygen.layers['metal'][3], xy0=c_bot_xy3 + np.array([0, 0]), xy1=np.array([0, y0+2-2]), gridname0=rg_m3m4, direction='y')
            for j in range(m*m_horizontal[i]):
                laygen.via(None, c_bot_xy2 + np.array([0, 0]), refinstname=c.name, refinstindex=np.array([k, j]), gridname=rg_m3m4)
        #col shorts
        if not i==0:
            laygen.route(None, laygen.layers['metal'][4], xy0=np.array([c_bot_xy[0], y0+2-2]), xy1=np.array([c_bot_xy3[0], y0+2-2]), gridname0=rg_m3m4)
            laygen.via(None, np.array([c_bot_xy[0], y0+2-2]), gridname=rg_m3m4)
            for k in range(2**i):
                c_bot_xy3 = laygen.get_inst_pin_xy(c.name, 'BOTTOM', rg_m3m4, index=np.array([k, m * 2 ** num_bits_vertical - 1]))[0]
                laygen.via(None, np.array([c_bot_xy3[0], y0+2-2]), gridname=rg_m3m4)
 
    #pins 
    #laygen.boundary_pin_from_rect(rc0, rg_m3m4, "I_C0", laygen.layers['pin'][3], size=4, direction='bottom')
    for i, r in enumerate(rbot):
        laygen.boundary_pin_from_rect(r, rg_m3m4, "I<" + str(i) + ">", laygen.layers['pin'][3], size=4,
                                      direction='bottom')
    cnt=0
    for i, c in enumerate(ivdac):
        #for j in range(m * 2 ** i): #radix2
        for j in range(m * m_vertical[i]):
            c_top_xy = laygen.get_inst_pin_xy(c.name, 'TOP', rg_m3m4, index=np.array([0, j]))
            rtop = laygen.route(None, laygen.layers['metal'][4], xy0=c_top_xy[0], xy1=c_top_xy[1], gridname0=rg_m3m4)
            laygen.boundary_pin_from_rect(rtop, rg_m3m4, "O" + str(cnt), laygen.layers['pin'][4], size=4,
                                          direction='left', netname="O")
            cnt+=1

    # prboundary
    y_grid = laygen.get_template('boundary_bottom', libname=utemplib).size[1]
    [size_x, size_y] = laygen.get_inst(ibndtr0.name).xy + laygen.get_inst(ibndtr0.name).size*np.array([num_space_right, num_space_top])
    size_y = int(size_y/y_grid+0.99)*y_grid
    print('prb:', size_x, size_y)
    laygen.add_rect(None, np.array([origin, origin + np.array([size_x, size_y])]), laygen.layers['prbnd'])

if __name__ == '__main__':
    """testbench - generating a capdac array"""
    cell_name='capdac'
    load_from_file=False
    yamlfile_system_input="adc_sar_dsn_system_input.yaml"
    if load_from_file==True:
        with open(yamlfile_system_input, 'r') as stream:
            sysdict_i = yaml.load(stream)
        cell_name='capdac'
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
    workinglib = 'clk_dis_generated'
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
    if os.path.exists(workinglib+'.yaml'): #generated layout file exists
        laygen.load_template(filename=workinglib+'.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    #grid
    pg = 'placement_basic' #placement grid
    rg_m1m2 = 'route_M1_M2_cmos'
    rg_m1m2_thick = 'route_M1_M2_basic_thick'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m3m4 = 'route_M3_M4_dense'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m6m7 = 'route_M3_M4_basic'

    mycell_list = []
    #cap dac generation
    load_from_file = True
    yamlfile_spec = "adc_sar_spec.yaml"
    yamlfile_size = "adc_sar_size.yaml"
    if load_from_file == True:
        # load parameters
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        m_unit=sizedict['clk_dis_cdac']['m']
        num_bits_vertical=sizedict['clk_dis_cdac']['num_bits']
    num_bits_horizontal=0
    num_space_top = 5
    num_space_bottom = 6
    sar_width=laygen.get_template_size('clk_dis_cell', gridname=pg, libname=workinglib)[0]
    mom_width=laygen.get_template_size('momcap_m4_center_1x', gridname=pg, libname=utemplib)[0]
    num_space_left = int((sar_width/2 - mom_width*2)/mom_width)
    num_space_right = 1
    print(cell_name+" generating")
    mycell_list.append(cell_name)
    laygen.add_cell(cell_name)
    laygen.sel_cell(cell_name)

    #routing grid used as placement grid
    generate_capdac(laygen, objectname_pfix='CDAC0', placement_grid=rg_m3m4, routing_grid_m3m4=rg_m3m4,
                    devname_cap_body='momcap_m4_center_1x', devname_cap_dmy='momcap_m4_dmy_1x', 
                    devname_cap_boundary='momcap_boundary_1x',
                    devname_list_overlay_boundary_left=['momcap_dmyblk_1x', 
                                                        'momcap_dmyptn_m1_1x',
                                                        'momcap_dmyptn_m2_1x',
                                                        'momcap_dmyptn_m3_1x',
                                                        #'momcap_dmyptn_m3_2track_1x',
                                                        'momcap_dmyptn_m4_1x',
                                                        'momcap_dmyptn_m5_1x',
                                                        'momcap_dmyptn_m6_1x',
                                                        #'momcap_dmyptn_m7_1x',
                                                        #'momcap_dmyptn_m8_1x',
                                                        #'momcap_dmyptn_m9_1x',
                                                        ],
                    devname_list_overlay_boundary_bottom=[#'momcap_dmyblk_1x', 
                                                        'momcap_dmyptn_m1_1x',
                                                        'momcap_dmyptn_m2_1x',
                                                        #'momcap_dmyptn_m3_1x',
                                                        #'momcap_dmyptn_m4_1x',
                                                        #'momcap_dmyptn_m5_1x',
                                                        'momcap_dmyptn_m6_1x',
                                                        #'momcap_dmyptn_m7_1x',
                                                        #'momcap_dmyptn_m8_1x',
                                                        #'momcap_dmyptn_m9_1x',
                                                        ],
                    devname_list_overlay_boundary_right=['momcap_dmyblk_1x', 
                                                        'momcap_dmyptn_m1_1x',
                                                        'momcap_dmyptn_m2_1x',
                                                        'momcap_dmyptn_m3_1x',
                                                        'momcap_dmyptn_m5_1x',
                                                        'momcap_dmyptn_m6_1x',
                                                        #'momcap_dmyptn_m7_1x',
                                                        #'momcap_dmyptn_m8_1x',
                                                        #'momcap_dmyptn_m9_1x',
                                                        ],
                    devname_list_overlay_boundary_top=[#'momcap_dmyblk_1x', 
                                                        'momcap_dmyptn_m1_1x',
                                                        'momcap_dmyptn_m2_1x',
                                                        'momcap_dmyptn_m3_1x',
                                                        #'momcap_dmyptn_m4_1x',
                                                        #'momcap_dmyptn_m5_1x',
                                                        'momcap_dmyptn_m6_1x',
                                                        #'momcap_dmyptn_m7_1x',
                                                        #'momcap_dmyptn_m8_1x',
                                                        #'momcap_dmyptn_m9_1x',
                                                        ],
                    devname_list_overlay_body=['momcap_dmyblk_1x', 
                                               'momcap_dmyptn_m1_1x',
                                               'momcap_dmyptn_m2_1x',
                                               #'momcap_dmyptn_m3_1x',
                                               'momcap_dmyptn_m6_1x',
                                              # 'momcap_dmyptn_m7_1x',
                                              # 'momcap_dmyptn_m8_1x',
                                              # 'momcap_dmyptn_m9_1x',
                                               ],
                    devname_list_overlay_dmy=['momcap_dmyblk_1x', 
                                              'momcap_dmyptn_m1_1x',
                                              'momcap_dmyptn_m2_1x',
                                              'momcap_dmyptn_m3_1x',
                                              'momcap_dmyptn_m6_1x',
                                              #'momcap_dmyptn_m7_1x',
                                              #'momcap_dmyptn_m8_1x',
                                              #'momcap_dmyptn_m9_1x',
                                              ],
                    m_unit=m_unit,
                    num_bits_vertical=num_bits_vertical,
                    m_vertical=np.array([1,2,4,8,16]),
                    num_bits_horizontal=num_bits_horizontal,
                    m_horizontal=np.array([32]),
                    num_space_left=num_space_left,
                    num_space_right=num_space_right,
                    num_space_top=num_space_top,
                    num_space_bottom=num_space_bottom,
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

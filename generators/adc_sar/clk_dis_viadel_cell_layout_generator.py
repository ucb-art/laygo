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

def generate_clkdis_viadel_cell(laygen, objectname_pfix, logictemp_lib, working_lib, grid, origin=np.array([0, 0]), 
        m_clki=2, m_clko=2, num_bits=5, unit_size=1, num_vss_h=4, num_vdd_h=4):
    """generate cap driver """

    pg = grid['pg']
    rg_m1m2 = grid['rg_m1m2']
    rg_m1m2_thick = grid['rg_m1m2_thick']
    rg_m2m3 = grid['rg_m2m3']
    rg_m2m3_basic = grid['rg_m2m3_basic']
    rg_m2m3_thick = grid['rg_m2m3_thick']
    rg_m2m3_thick2 = grid['rg_m2m3_thick2']
    rg_m3m4 = grid['rg_m3m4']
    rg_m3m4_dense = grid['rg_m3m4_dense']
    rg_m3m4_thick2 = grid['rg_m3m4_thick2']
    rg_m4m5 = grid['rg_m4m5']
    rg_m5m6 = grid['rg_m5m6']
    rg_m6m7 = grid['rg_m6m7']  

    ##Placing capdacs
    capdac = []
    ofst_capdac = np.array([0, laygen.get_template_xy(name='capdac', libname='clk_dis_generated')[1]])
    capdac0_0 = laygen.place(name='I' + objectname_pfix + 'CAPDAC0_0', templatename='capdac', gridname=pg, xy=origin,
                             template_libname='clk_dis_generated', transform='MX', offset=ofst_capdac)
    capdac0_1 = laygen.relplace(name='I' + objectname_pfix + 'CAPDAC0_1', templatename='capdac', gridname=pg,
                                refinstname=capdac0_0.name, template_libname='clk_dis_generated', transform='R180')
    capdac.append(capdac0_0)
    capdac.append(capdac0_1)

    ##Placing delay cell
    viacell = laygen.place(name='I' + objectname_pfix + 'CELL0', templatename='clk_dis_cell', gridname=pg, xy=origin,
                           template_libname='clk_dis_generated', offset=ofst_capdac)
    viacell_height = laygen.get_template_xy(name='clk_dis_cell', libname='clk_dis_generated')[1]
    
    ##Route, clock connection from TGATE to input
    # clki_y =laygen.grids.get_absgrid_coord_y(gridname=rg_m5m6, y=4.13) # y number set by hand, To be fixed
    # for i in range(m_clki):
    #     viadel_I_xy = laygen.get_inst_pin_xy(viacell.name, 'CLKI_' + str(i), rg_m5m6)[0]
    #     clkopx=laygen.route(None, laygen.layers['metal'][5], xy0=viadel_I_xy, xy1=np.array([viadel_I_xy[0],clki_y]), gridname0=rg_m5m6)
    #     laygen.boundary_pin_from_rect(clkopx, gridname=rg_m5m6, name='CLKI_' + str(i),
    #                                   layer=laygen.layers['pin'][5], size=2, direction='top', netname='CLKI')
    for i in range(m_clki):
        viadel_I_xy = laygen.get_inst_pin_xy(viacell.name, 'CLKI_'+str(i), rg_m5m6)[0]
        clkopx = laygen.route(None, laygen.layers['metal'][5], xy0=viadel_I_xy, xy1=viadel_I_xy,
                              gridname0=rg_m5m6)
        laygen.boundary_pin_from_rect(clkopx, gridname=rg_m5m6, name='CLKI_'+str(i), layer=laygen.layers['pin'][5],
                size=2, direction='top', netname='CLKI')

    ##Route, clock connection from TGATE to output
    # clko_y =laygen.grids.get_absgrid_coord_y(gridname=rg_m5m6, y=-20)
    # clko_y = -laygen.get_template_size(name='capdac', gridname=rg_m5m6, libname='clk_dis_generated')[1]
    clko_y = 0
    clko_xy = []
    for i in range(m_clko):
        viadel_O_xy = laygen.get_inst_pin_xy(viacell.name, 'CLKO_' + str(i), rg_m4m5)[0]
        clko_xy.append(viadel_O_xy)
        clkopx=laygen.route(None, laygen.layers['metal'][5], xy0=viadel_O_xy, xy1=np.array([viadel_O_xy[0],clko_y]), gridname0=rg_m4m5)
        laygen.boundary_pin_from_rect(clkopx, gridname=rg_m4m5, name='CLKO_' + str(i),
                                      layer=laygen.layers['pin'][5], size=2, direction='bottom', netname='CLKO')
    for i in range(0,2**(num_bits+unit_size-1)-2,4):
        capdac_O_xy0 = laygen.get_inst_pin_xy(capdac[0].name, 'O' + str(i), rg_m4m5)[0]
        capdac_O_xy1 = laygen.get_inst_pin_xy(capdac[1].name, 'O' + str(i), rg_m4m5)[0]
        laygen.route(None, laygen.layers['metal'][4], xy0=capdac_O_xy0, xy1=capdac_O_xy1, gridname0=rg_m4m5)
        for j in range(m_clko):
            laygen.via(None, xy=np.array([clko_xy[j][0],capdac_O_xy0[1]]), gridname=rg_m4m5)

    ## Route, for inside connection between capdac and viadel
    # for i in range(0,num_bits):
    #     capdac_C_xy0 = laygen.get_inst_pin_xy(capdac[0].name, 'I<' + str(i) + '>', rg_m3m4_dense)[0]
    #     capdac_C_xy1 = laygen.get_inst_pin_xy(capdac[1].name, 'I<' + str(i) + '>', rg_m3m4_dense)[0]
    #     laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], capdac_C_xy0, capdac_C_xy1, -1-2*i, rg_m3m4_dense)
    #     viadel_SW_xy = laygen.get_inst_pin_xy(viacell.name, 'CAPSW<' + str(i) + '>', rg_m3m4)[0]
    #     laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], capdac_C_xy0, viadel_SW_xy, -1-2*i, rg_m3m4_dense, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4)
    ofst_grid_34 = laygen.grids.get_absgrid_coord_y(gridname=rg_m3m4, y=ofst_capdac[1])
    for i in range(0, num_bits):
        capdac_C_xy0 = laygen.get_inst_pin_xy(capdac[0].name, 'I<' + str(i) + '>', rg_m3m4_dense)[0]
        capdac_C_xy1 = laygen.get_inst_pin_xy(capdac[1].name, 'I<' + str(i) + '>', rg_m3m4_dense)[0]
        laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], capdac_C_xy0, capdac_C_xy1,
                         -2 * i + ofst_grid_34, rg_m3m4_dense)
        viadel_SW_xy = laygen.get_inst_pin_xy(viacell.name, 'CAPSW<' + str(i) + '>', rg_m3m4)[0]
        laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], capdac_C_xy0, viadel_SW_xy,
                         -2 * i + ofst_grid_34, rg_m3m4_dense, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4)
        print(-2 * i + ofst_grid_34)

    ##Route, for calibration signals
    #Get the right coodinate on grid m3m4
    for i in range(num_bits):
        viadel_CAL_xy = laygen.get_inst_pin_xy(viacell.name, 'CAL<' + str(i) + '>', rg_m2m3_basic)
        laygen.pin(name='CAL<'+str(i)+'>', layer=laygen.layers['pin'][3], xy=viadel_CAL_xy, gridname=rg_m2m3_basic) 

    
    ##Route, for set/reset signals
    #ST, RST
    viadel_ST_xy = laygen.get_inst_pin_xy(viacell.name, 'ST', rg_m2m3_basic)
    viadel_RST_xy = laygen.get_inst_pin_xy(viacell.name, 'RST', rg_m2m3_basic)
    laygen.pin(name='ST', layer=laygen.layers['pin'][3], xy=viadel_ST_xy, gridname=rg_m2m3_basic) 
    laygen.pin(name='RST', layer=laygen.layers['pin'][3], xy=viadel_RST_xy, gridname=rg_m2m3_basic) 

    ##DATAI and DATAO pin
    viadel_I_xy = laygen.get_inst_pin_xy(viacell.name, 'I', rg_m2m3_basic)
    viadel_O_xy = laygen.get_inst_pin_xy(viacell.name, 'O', rg_m2m3_basic)
    laygen.pin(name='DATAI', layer=laygen.layers['pin'][3], xy=viadel_I_xy, gridname=rg_m2m3_basic) 
    laygen.pin(name='DATAO', layer=laygen.layers['pin'][3], xy=viadel_O_xy, gridname=rg_m2m3_basic) 
    
    ##VDD and VSS pin
    for i in range(num_vss_h):
        vssl_xy = laygen.get_inst_pin_xy(viacell.name, 'VSS0_' + str(i), rg_m3m4_thick2)
        laygen.pin(name='VSS0_'+str(i), layer=laygen.layers['pin'][4], xy=vssl_xy, gridname=rg_m3m4_thick2, netname='VSS')
        vssr_xy = laygen.get_inst_pin_xy(viacell.name, 'VSS1_' + str(i), rg_m3m4_thick2)
        laygen.pin(name='VSS1_'+str(i), layer=laygen.layers['pin'][4], xy=vssr_xy, gridname=rg_m3m4_thick2, netname='VSS')
    for i in range(num_vdd_h):
        vddl_xy = laygen.get_inst_pin_xy(viacell.name, 'VDD0_' + str(i), rg_m3m4_thick2)
        laygen.pin(name='VDD0_'+str(i), layer=laygen.layers['pin'][4], xy=vddl_xy, gridname=rg_m3m4_thick2, netname='VDD')
        vddr_xy = laygen.get_inst_pin_xy(viacell.name, 'VDD1_' + str(i), rg_m3m4_thick2)
        laygen.pin(name='VDD1_'+str(i), layer=laygen.layers['pin'][4], xy=vddr_xy, gridname=rg_m3m4_thick2, netname='VDD')
    
    # # prboundary
    # y_grid = laygen.get_template('boundary_bottom', libname=utemplib).size[1]
    # size_y1 = (int(viacell.size[1]/y_grid+0.99))*y_grid
    # size_y2 = 0-(int(capdac0_0.size[1]/y_grid+0.99)*y_grid)
    # size_x = viacell.size[0]
    # laygen.add_rect(None, np.array([origin + [0, size_y2], origin + np.array([size_x, size_y1])]), laygen.layers['prbnd'])

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
    if os.path.exists(workinglib + '.yaml'):  # generated layout file exists
        laygen.load_template(filename=workinglib + '.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    #params
    params = dict(
        m_clki = 24,
        m_clko = 2,
        num_bits = 5,
        unit_size = 2,
        num_vss_h=4, 
        num_vdd_h=4
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
        params['m_clki']=sizedict['clk_dis_htree']['m_track']
        params['m_clko'] = sizedict['clk_dis_htree']['m_clko']
        params['num_bits'] = sizedict['clk_dis_cdac']['num_bits']
        params['unit_size'] = sizedict['clk_dis_cdac']['m']

    #grid
    grid = dict(
        pg = 'placement_basic', #placement grid
        rg_m1m2 = 'route_M1_M2_cmos',
        rg_m1m2_thick = 'route_M1_M2_basic_thick',
        rg_m2m3 = 'route_M2_M3_cmos',
        rg_m2m3_basic = 'route_M2_M3_basic',
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

    print(workinglib)

    mycell_list=[]

    cellname='clk_dis_viadel_cell'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_clkdis_viadel_cell(laygen, objectname_pfix='CKVIAD', logictemp_lib=logictemplib, working_lib=workinglib, grid=grid, origin=np.array([0, 0]), **params)
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

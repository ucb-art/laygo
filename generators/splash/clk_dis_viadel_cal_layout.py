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
import laygo.GridLayoutGeneratorHelper as laygenhelper #utility functions
#import logging;logging.basicConfig(level=logging.DEBUG)

def generate_sfft_clkdis_viadel(laygen, objectname_pfix, logictemp_lib, working_lib, grid, origin=np.array([0, 0]), way_order=[0, 8, 1, 7, 2, 6, 3, 5, 4],
        m_clki=2, m_clko=2, num_bits=5, num_vss_h=4, num_vdd_h=4):
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
    rg_m4m5_thick = grid['rg_m4m5_thick']
    rg_m5m6 = grid['rg_m5m6']
    rg_m5m6_thick = grid['rg_m5m6_thick']
    rg_m6m7 = grid['rg_m6m7']

    num_ways = len(way_order)
    ##Get the index for each way
    way_index = []
    for i in range(num_ways):
        way_index.append(way_order.index(i))
    print(way_index)
    #Get even and odd index
    #way_index_even = []
    #way_index_odd = []
    #for i in range(int(num_ways/2)):
        #way_index_even.append(way_order.index(2*i))
        #way_index_odd.append(way_order.index(2*i+1))
    x0 = laygen.templates.get_template('clk_dis_viadel_cell', libname=workinglib).xy[1][0]
    ##Placing delay cells
    viacell=[]
    viacell0=laygen.place(name='I'+objectname_pfix+'CELL0', templatename='clk_dis_viadel_cell', gridname=pg, xy=origin, 
            template_libname='clk_dis_generated')
    viacell.append(viacell0)

    for i in range(num_ways-1):
        viacellx=laygen.relplace(name='I'+objectname_pfix+'CELL'+str(i+1), templatename='clk_dis_viadel_cell', gridname=pg, 
                refinstname=viacell[-1].name, template_libname='clk_dis_generated')
        viacell.append(viacellx)
    
    ## Route, connection between different DFFs
    #wire_num = 0
    for i in range(num_ways):
        wire_num = i%2
        #else:
            #wire_num = 2
        #if (i<int(num_ways-1)):
            #if ((i!=0) and (flag !=np.sign(way_index[i+1]-way_index[i]))):
                #wire_num = wire_num + 1
            #flag = np.sign(way_index[i+1]-way_index[i])
            #print(flag)
        #else:
            #wire_num = wire_num + 1 

        #print(wire_num)
        #print(wire_num_odd)
        
        if (i<int(num_ways)-1):
            dff_O_xy = laygen.get_inst_pin_xy(viacell[way_index[i]].name, 'DATAO', rg_m3m4)
            dff_I_xy = laygen.get_inst_pin_xy(viacell[way_index[i+1]].name, 'DATAI', rg_m3m4)
        else:
            dff_O_xy = laygen.get_inst_pin_xy(viacell[way_index[i]].name, 'DATAO', rg_m3m4)
            dff_I_xy = laygen.get_inst_pin_xy(viacell[way_index[0]].name, 'DATAI', rg_m3m4)
        y_cood = dff_I_xy[0][1]
        laygen.pin(name='DATAO<'+str(way_order[way_index[i]])+'>', layer=laygen.layers['pin'][3], xy=dff_O_xy, gridname=rg_m3m4)
        if (i<int(num_ways/2)):
            laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], dff_O_xy[0], dff_I_xy[0], y_cood-7-wire_num, rg_m3m4)
        else:
            laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], dff_O_xy[0], dff_I_xy[0], y_cood-9-wire_num, rg_m3m4)
        '''
        if (i<int(num_ways/2)-1):
            dff_O_xy_even = laygen.get_inst_pin_xy(viacell[way_index_even[i]].name, 'DATAO', rg_m3m4)
            dff_I_xy_even = laygen.get_inst_pin_xy(viacell[way_index_even[i+1]].name, 'DATAI', rg_m3m4)
            dff_O_xy_odd = laygen.get_inst_pin_xy(viacell[way_index_odd[i]].name, 'DATAO', rg_m3m4)
            dff_I_xy_odd = laygen.get_inst_pin_xy(viacell[way_index_odd[i+1]].name, 'DATAI', rg_m3m4)
        else:
            dff_O_xy_even = laygen.get_inst_pin_xy(viacell[way_index_even[i]].name, 'DATAO', rg_m3m4)
            dff_I_xy_even = laygen.get_inst_pin_xy(viacell[way_index_even[0]].name, 'DATAI', rg_m3m4)
            dff_O_xy_odd = laygen.get_inst_pin_xy(viacell[way_index_odd[i]].name, 'DATAO', rg_m3m4)
            dff_I_xy_odd = laygen.get_inst_pin_xy(viacell[way_index_odd[0]].name, 'DATAI', rg_m3m4)
        y_cood = dff_I_xy_even[0][1]
        laygen.pin(name='DATAO<'+str(way_order[way_index_even[i]])+'>', layer=laygen.layers['pin'][3], xy=dff_I_xy_even, gridname=rg_m3m4) 
        laygen.pin(name='DATAO<'+str(way_order[way_index_odd[i]])+'>', layer=laygen.layers['pin'][3], xy=dff_I_xy_odd, gridname=rg_m3m4) 
        laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], dff_O_xy_even[0], dff_I_xy_even[0], y_cood-7-wire_num_even, rg_m3m4)
        laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], dff_O_xy_odd[0], dff_I_xy_odd[0], y_cood-7-wire_num_odd, rg_m3m4)
        '''

    ##Route, clock connection from TGATE to input
    for i in range(num_ways):
        for j in range(m_clki):
            viadel_I_xy = laygen.get_inst_pin_xy(viacell[i].name, 'CLKI_'+str(j), rg_m5m6)
            laygen.pin(name='CLKI'+str(way_order[i])+'_'+str(j), layer=laygen.layers['pin'][5], xy=viadel_I_xy, gridname=rg_m5m6, netname='CLKI<'+str(way_order[i])+'>')
            
    ##Route, clock connection from TGATE to output
    for i in range(num_ways):
        for j in range(m_clko):
            viadel_I_xy = laygen.get_inst_pin_xy(viacell[i].name, 'CLKO_'+str(j), rg_m5m6)
            laygen.pin(name='CLKO'+str(way_order[i])+'_'+str(j), layer=laygen.layers['pin'][5], xy=viadel_I_xy, gridname=rg_m5m6, netname='CLKO<'+str(way_order[i])+'>')
    
    ##Route, for calibration signals
    #Get the right coodinate on grid m3m4
    m2m3_x = laygen.grids.get_absgrid_coord_x(gridname=rg_m2m3_basic, x=x0)
    m3m4_x = laygen.grids.get_absgrid_coord_x(gridname=rg_m3m4, x=x0)
    for i in range(num_ways):
        if i<0:
            for j in range(num_bits):
                viadel_m2m3_xy = laygen.get_inst_pin_xy(viacell[i].name, 'CAL<'+str(j)+'>', rg_m2m3_basic)[1]
                laygen.route(None, laygen.layers['metal'][3], xy0=viadel_m2m3_xy, xy1=np.array([viadel_m2m3_xy[0],viadel_m2m3_xy[1]+5+j+i*num_bits]), gridname0=rg_m2m3_basic)
                laygen.via(None, xy=np.array([viadel_m2m3_xy[0],viadel_m2m3_xy[1]+5+j+i*num_bits]), gridname=rg_m2m3_basic)
                calpx=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0,viadel_m2m3_xy[1]+5+j+i*num_bits]), 
                    xy1=np.array([m2m3_x*num_ways,viadel_m2m3_xy[1]+5+j+i*num_bits]), gridname0=rg_m2m3_basic)
                laygen.boundary_pin_from_rect(calpx, gridname=rg_m2m3_basic, name='CLKCAL'+str(way_order[i])+'<'+str(j)+'>', layer=laygen.layers['pin'][2], 
                    size=2, direction='right')
        else:
            for j in range(num_bits):
                viadel_m2m3_xy = laygen.get_inst_pin_xy(viacell[i].name, 'CAL<'+str(j)+'>', rg_m2m3)[1]
                laygen.route(None, laygen.layers['metal'][3], xy0=viadel_m2m3_xy, xy1=np.array([viadel_m2m3_xy[0],viadel_m2m3_xy[1]-4]), gridname0=rg_m2m3)
                laygen.via(None, xy=np.array([viadel_m2m3_xy[0],viadel_m2m3_xy[1]-4]), gridname=rg_m2m3)

    ##Route, for set/reset signals
    #STP and RSTP -- even
    m2m3_x = laygen.grids.get_absgrid_coord_x(gridname=rg_m2m3_basic, x=x0)
    viadel_ST_xy = laygen.get_inst_pin_xy(viacell[way_index[0]].name, 'ST', rg_m2m3_basic)[1]
    laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], viadel_ST_xy, np.array([0,viadel_ST_xy[1]+12]), rg_m2m3_basic)

    viadel_RST_xy = laygen.get_inst_pin_xy(viacell[way_index[0]].name, 'RST', rg_m2m3)[1]
    laygen.route(None, laygen.layers['metal'][3], xy0=viadel_RST_xy, xy1=np.array([viadel_RST_xy[0],viadel_RST_xy[1]+4]), gridname0=rg_m2m3)
    laygen.via(None, xy=np.array([viadel_RST_xy[0],viadel_RST_xy[1]+4]), gridname=rg_m2m3)

    for i in range(int(num_ways)-1):#way_index
        viadel_RST_xy = laygen.get_inst_pin_xy(viacell[way_index[i+1]].name, 'RST', rg_m2m3_basic)[1]
        laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], viadel_RST_xy, np.array([0,viadel_RST_xy[1]+12]), rg_m2m3_basic)

        viadel_ST_xy = laygen.get_inst_pin_xy(viacell[way_index[i+1]].name, 'ST', rg_m2m3)[1]
        laygen.route(None, laygen.layers['metal'][3], xy0=viadel_ST_xy, xy1=np.array([viadel_ST_xy[0],viadel_ST_xy[1]+4]), gridname0=rg_m2m3)
        laygen.via(None, xy=np.array([viadel_ST_xy[0],viadel_ST_xy[1]+4]), gridname=rg_m2m3)

    stp=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, viadel_RST_xy[1]+12]), xy1=np.array([m2m3_x*num_ways-4, viadel_RST_xy[1]+12]), gridname0=rg_m2m3_basic)
    laygen.boundary_pin_from_rect(stp, gridname=rg_m2m3_basic, name='RSTP', layer=laygen.layers['pin'][2], size=2, direction='left')
    
    '''
    #STN, RSTN -- odd
    viadel_ST_xy = laygen.get_inst_pin_xy(viacell[way_index_odd[0]].name, 'ST', rg_m2m3_basic)[1]
    laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], viadel_ST_xy, np.array([0,viadel_ST_xy[1]+13]), rg_m2m3_basic)

    viadel_RST_xy = laygen.get_inst_pin_xy(viacell[way_index_odd[0]].name, 'RST', rg_m2m3)[1]
    laygen.route(None, laygen.layers['metal'][3], xy0=viadel_RST_xy, xy1=np.array([viadel_RST_xy[0],viadel_RST_xy[1]+4]), gridname0=rg_m2m3)
    laygen.via(None, xy=np.array([viadel_RST_xy[0],viadel_RST_xy[1]+4]), gridname=rg_m2m3)

    for i in range(int(num_ways/2)-1):#way_index
        viadel_RST_xy = laygen.get_inst_pin_xy(viacell[way_index_odd[i+1]].name, 'RST', rg_m2m3_basic)[1]
        laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2], viadel_RST_xy, np.array([0,viadel_RST_xy[1]+13]), rg_m2m3_basic)

        viadel_ST_xy = laygen.get_inst_pin_xy(viacell[way_index_odd[i+1]].name, 'ST', rg_m2m3)[1]
        laygen.route(None, laygen.layers['metal'][3], xy0=viadel_ST_xy, xy1=np.array([viadel_ST_xy[0],viadel_ST_xy[1]+4]), gridname0=rg_m2m3)
        laygen.via(None, xy=np.array([viadel_ST_xy[0],viadel_ST_xy[1]+4]), gridname=rg_m2m3)
      
    stn=laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, viadel_RST_xy[1]+13]), xy1=np.array([m2m3_x*num_ways, viadel_RST_xy[1]+13]), gridname0=rg_m2m3_basic)    
    laygen.boundary_pin_from_rect(stn, gridname=rg_m2m3_basic, pinname='RSTN', layer=laygen.layers['pin'][2], size=2, direction='left')
    '''
    
    ##VDD and VSS pin
    rvssl_m4 = []
    rvssr_m4 = []
    rvddl_m4 = []
    rvddr_m4 = []
    rvdd_m5 = []
    rvss_m5 = []
    for i in range(num_ways):
        for j in range(num_vss_h):
            vssl_xy = laygen.get_inst_pin_xy(viacell[i].name, 'VSS0_' + str(j), rg_m3m4_thick2)
            rvssl_m4.append(laygen.route(None, laygen.layers['metal'][4], xy0=vssl_xy[0], xy1=vssl_xy[1], gridname0=rg_m3m4_thick2))
            vssr_xy = laygen.get_inst_pin_xy(viacell[i].name, 'VSS1_' + str(j), rg_m3m4_thick2)
            rvssr_m4.append(laygen.route(None, laygen.layers['metal'][4], xy0=vssr_xy[0], xy1=vssr_xy[1], gridname0=rg_m3m4_thick2))
            # laygen.pin(name='VSS0_'+str(i)+'_'+str(j), layer=laygen.layers['pin'][4], xy=vssl_xy, gridname=rg_m3m4_thick2, netname='VSS')
            # laygen.pin(name='VSS1_'+str(i)+'_'+str(j), layer=laygen.layers['pin'][4], xy=vssr_xy, gridname=rg_m3m4_thick2, netname='VSS')
        for j in range(num_vdd_h):
            vddl_xy = laygen.get_inst_pin_xy(viacell[i].name, 'VDD0_' + str(j), rg_m3m4_thick2)
            rvddl_m4.append(laygen.route(None, laygen.layers['metal'][4], xy0=vddl_xy[0], xy1=vddl_xy[1], gridname0=rg_m3m4_thick2))
            vddr_xy = laygen.get_inst_pin_xy(viacell[i].name, 'VDD1_' + str(j), rg_m3m4_thick2)
            rvddr_m4.append(laygen.route(None, laygen.layers['metal'][4], xy0=vddr_xy[0], xy1=vddr_xy[1], gridname0=rg_m3m4_thick2))
            # laygen.pin(name='VDD0_'+str(i)+'_'+str(j), layer=laygen.layers['pin'][4], xy=vddl_xy, gridname=rg_m3m4_thick2, netname='VDD')
            # laygen.pin(name='VDD1_'+str(i)+'_'+str(j), layer=laygen.layers['pin'][4], xy=vddr_xy, gridname=rg_m3m4_thick2, netname='VDD')
        rvddl_m5, rvssl_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M5L',
                                                                           layer=laygen.layers['metal'][5],
                                                                           gridname=rg_m4m5_thick,
                                                                           netnames=['VDD', 'VSS'], direction='y',
                                                                           input_rails_rect=[rvddl_m4, rvssl_m4],
                                                                           generate_pin=False,
                                                                           overwrite_start_coord=0,
                                                                           overwrite_end_coord=None,
                                                                           overwrite_num_routes=None,
                                                                           offset_start_index=0,
                                                                           offset_end_index=0)
        rvddr_m5, rvssr_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M5L',
                                                                               layer=laygen.layers['metal'][5],
                                                                               gridname=rg_m4m5_thick,
                                                                               netnames=['VDD', 'VSS'], direction='y',
                                                                               input_rails_rect=[rvddr_m4, rvssr_m4],
                                                                               generate_pin=False,
                                                                               overwrite_start_coord=0,
                                                                               overwrite_end_coord=None,
                                                                               overwrite_num_routes=None,
                                                                               offset_start_index=0,
                                                                               offset_end_index=-2)
        rvddl_m4 = []
        rvssl_m4 = []
        rvddr_m4 = []
        rvssr_m4 = []
        rvdd_m5 += rvddl_m5
        rvdd_m5 += rvddr_m5
        rvss_m5 += rvssl_m5
        rvss_m5 += rvssr_m5
    rvdd_m6, rvss_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M6',
                                                                           layer=laygen.layers['pin'][6],
                                                                           gridname=rg_m5m6_thick,
                                                                           netnames=['VDD', 'VSS'], direction='x',
                                                                           input_rails_rect=[rvdd_m5, rvss_m5],
                                                                           generate_pin=True,
                                                                           overwrite_start_coord=0,
                                                                           overwrite_end_coord=None,
                                                                           overwrite_num_routes=None,
                                                                           offset_start_index=2,
                                                                           offset_end_index=0)



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
        way_order = [0, 32, 1, 31, 2, 30, 3, 29, 4, 28, 5, 27, 6, 26, 7, 25, 8, 24, 9, 23, 10, 22, 11, 21, 12, 20, 13, 19, 14, 18, 15, 17, 16],
        m_clki = 2,
        m_clko = 2,
        num_bits = 5,
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
        params['way_order'] = sizedict['clkcal_order']

    #grid
    grid = dict(
        pg = 'placement_basic', #placement grid
        rg_m1m2 = 'route_M1_M2_cmos',
        rg_m1m2_thick = 'route_M1_M2_thick',
        rg_m2m3 = 'route_M2_M3_cmos',
        rg_m2m3_basic = 'route_M2_M3_basic',
        rg_m2m3_thick = 'route_M2_M3_thick',
        rg_m2m3_thick2 = 'route_M2_M3_thick2',
        rg_m3m4 = 'route_M3_M4_basic',
        rg_m3m4_dense = 'route_M3_M4_dense',
        rg_m3m4_thick2 = 'route_M3_M4_basic_thick',
        rg_m4m5 = 'route_M4_M5_basic',
        rg_m4m5_thick = 'route_M4_M5_thick',
        rg_m5m6 = 'route_M5_M6_basic',
        rg_m5m6_thick = 'route_M5_M6_thick',
        rg_m6m7 = 'route_M6_M7_basic',
        rg_m1m2_pin = 'route_M1_M2_basic',
        rg_m2m3_pin = 'route_M2_M3_basic',
    )

    print(workinglib)

    mycell_list=[]

    cellname='clk_dis_viadel_cal'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sfft_clkdis_viadel(laygen, objectname_pfix='CKVIAD', logictemp_lib=logictemplib, working_lib=workinglib, grid=grid, origin=np.array([0, 0]), **params)
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

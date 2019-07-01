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

"""SER library
"""
import laygo
import numpy as np
#from logic_layout_generator import *
from math import log
import yaml
import os
import laygo.GridLayoutGeneratorHelper as laygenhelper #utility functions
#import logging;logging.basicConfig(level=logging.DEBUG)

def add_to_export_ports(export_ports, pins):
    if type(pins) != list:
        pins = [pins]

    for pin in pins:
        netname = pin.netname
        bbox_float = pin.xy.reshape((1,4))[0]
        for ind in range(len(bbox_float)): # keeping only 3 decimal places
            bbox_float[ind] = float('%.3f' % bbox_float[ind])
        port_entry = dict(layer=int(pin.layer[0][1]), bbox=bbox_float.tolist())
        if netname in export_ports.keys():
            export_ports[netname].append(port_entry)
        else:
            export_ports[netname] = [port_entry]

    return export_ports

def generate_serializer(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m2m3,
                          routing_grid_m4m5, num_ser=8, num_ser_3rd=4, m_ser=1, origin=np.array([0, 0])):
    export_dict = {'boundaries': {'lib_name': 'ge_tech_logic_templates',
                                  'lr_width': 8,
                                  'tb_height': 0.5},
                   'cells': {cell_name: {'cell_name': cell_name,
                                                 'lib_name': workinglib,
                                                 'size': [40, 1]}},
                   'spaces': [{'cell_name': 'space_4x',
                               'lib_name': 'ge_tech_logic_templates',
                               'num_col': 4},
                              {'cell_name': 'space_2x',
                               'lib_name': 'ge_tech_logic_templates',
                               'num_col': 2}],
                   'tech_params': {'col_pitch': 0.09,
                                   'directions': ['x', 'y', 'x', 'y'],
                                   'height': 0.96,
                                   'layers': [2, 3, 4, 5],
                                   'spaces': [0.064, 0.05, 0.05, 0.05],
                                   'widths': [0.032, 0.04, 0.04, 0.04]}}
    export_ports = dict()
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m4m5 = routing_grid_m4m5

    sub_ser = int(num_ser/2)
    ser_name = 'ser_2Nto1_'+str(num_ser)+'to1'
    ser_3rd_name = 'ser_'+str(num_ser_3rd)+'to1'
    ser_overall = int(num_ser * num_ser_3rd)
    # placement
    iser_3rd=[]
    for i in range(num_ser):
        if i==0:
            iser_3rd.append(laygen.place(name = "I" + objectname_pfix + 'SER3rd'+str(i), templatename = ser_3rd_name,
            gridname = pg, xy=origin, transform="R0", shape=np.array([1,1]), template_libname = workinglib))
        else:
            iser_3rd.append(laygen.relplace(name = "I" + objectname_pfix + 'SER3rd'+str(i), templatename = ser_3rd_name,
            gridname = pg, refinstname = iser_3rd[-1].name, transform="R0", shape=np.array([1,1]), template_libname = workinglib, direction = 'top'))
            refi=iser_3rd[-1]
    iser_2stg=laygen.relplace(name = "I" + objectname_pfix + 'SER2stg', templatename = ser_name,
            gridname = pg, refinstname = refi.name, transform="MY", shape=np.array([1,1]), template_libname = workinglib, direction = 'top')

    #Internal Pins
    ser2Nto1_clkb_xy=laygen.get_inst_pin_xy(iser_2stg.name, 'CLKB', rg_m3m4)
    ser2Nto1_clk_xy=laygen.get_inst_pin_xy(iser_2stg.name, 'CLK', rg_m3m4)
    ser2Nto1_rst_xy=[]
    ser2Nto1_rst_xy45=[]
    for i in range(2):
        ser2Nto1_rst_xy.append(laygen.get_inst_pin_xy(iser_2stg.name, 'RST' + str(i), rg_m3m4))
        ser2Nto1_rst_xy45.append(laygen.get_inst_pin_xy(iser_2stg.name, 'RST' + str(i), rg_m4m5))
    ser2Nto1_out_xy=laygen.get_inst_pin_xy(iser_2stg.name, 'out', rg_m3m4)
    ser2Nto1_div_xy=laygen.get_inst_pin_xy(iser_2stg.name, 'divclk', rg_m3m4)
    ser2Nto1_in_xy=[]
    ser3rd_in_xy=[]
    ser3rd_rst_xy=[]
    ser3rd_rst_xy45=[]
    ser3rd_clk_xy=[]
    ser3rd_out_xy=[]
    for i in range(num_ser):
        ser2Nto1_in_xy.append(laygen.get_inst_pin_xy(iser_2stg.name, 'in<' + str(i) + '>', rg_m3m4))
        ser3rd_rst_xy.append(laygen.get_inst_pin_xy(iser_3rd[i].name, 'RST', rg_m3m4))
        ser3rd_rst_xy45.append(laygen.get_inst_pin_xy(iser_3rd[i].name, 'RST', rg_m4m5))
        ser3rd_clk_xy.append(laygen.get_inst_pin_xy(iser_3rd[i].name, 'clk_in', rg_m3m4))
        ser3rd_out_xy.append(laygen.get_inst_pin_xy(iser_3rd[i].name, 'out', rg_m3m4))
        for j in range(num_ser_3rd):
            ser3rd_in_xy.append(laygen.get_inst_pin_xy(iser_3rd[i].name, 'in<' + str(j) + '>', rg_m3m4))
    print(ser3rd_in_xy[10])

    # Route
    for i in range(num_ser):
        [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][3], 
                ser3rd_out_xy[i][0], ser2Nto1_in_xy[i][0], ser3rd_out_xy[i][0][0]+16+i, rg_m3m4)
        via_out = laygen.via(None, ser3rd_out_xy[i][0], gridname=rg_m3m4)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                ser2Nto1_div_xy[0], ser3rd_clk_xy[i][1], ser2Nto1_div_xy[0][1]-10, rg_m3m4)
        via_div = laygen.via(None, ser3rd_clk_xy[i][1], gridname=rg_m3m4)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                ser2Nto1_rst_xy[0][0], ser3rd_rst_xy[i][1]-np.array([5,1]), ser2Nto1_rst_xy[0][0][1]-2, rg_m3m4,
                layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4)
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                ser3rd_rst_xy[i][0], ser3rd_rst_xy[i][1]-np.array([5,1]), ser3rd_rst_xy[i][1][1], rg_m3m4,
                layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4)
    #[rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
    #            ser2Nto1_rst_xy[0][0], ser2Nto1_rst_xy45[0][0]-np.array([4,1]), ser2Nto1_rst_xy[0][1][1], rg_m3m4,
    #            layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                ser2Nto1_rst_xy[1][0], ser2Nto1_rst_xy[1][1]-np.array([3,1]), ser2Nto1_rst_xy[1][1][1], rg_m3m4,
                layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                ser2Nto1_rst_xy[0][0], ser2Nto1_rst_xy[1][1]-np.array([3,1]), ser2Nto1_rst_xy[0][0][1]-2, rg_m3m4,
                layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4)

    #Pin
    #CLK_pin=laygen.pin(name='CLK', layer=laygen.layers['pin'][4], xy=ser2Nto1_clk_xy, gridname=rg_m3m4)
    rCLK=laygen.route(None, laygen.layers['metal'][4], xy0=ser2Nto1_clk_xy[0], xy1=ser2Nto1_clk_xy[1], gridname0=rg_m3m4)
    CLK_pin=laygen.boundary_pin_from_rect(rCLK, rg_m3m4, 'CLK', laygen.layers['pin'][4], size=0, direction='top', netname='CLK')
    export_ports = add_to_export_ports(export_ports, CLK_pin)
    #CLKB_pin=laygen.pin(name='CLKB', layer=laygen.layers['pin'][4], xy=ser2Nto1_clkb_xy, gridname=rg_m3m4)
    rCLKB=laygen.route(None, laygen.layers['metal'][4], xy0=ser2Nto1_clkb_xy[0], xy1=ser2Nto1_clkb_xy[1], gridname0=rg_m3m4)
    CLKB_pin=laygen.boundary_pin_from_rect(rCLKB, rg_m3m4, 'CLKB', laygen.layers['pin'][4], size=0, direction='top', netname='CLKB')
    export_ports = add_to_export_ports(export_ports, CLKB_pin)
    #out_pin=laygen.pin(name='out', layer=laygen.layers['pin'][4], xy=ser2Nto1_out_xy, gridname=rg_m3m4)
    rout=laygen.route(None, laygen.layers['metal'][4], xy0=ser2Nto1_out_xy[0]+np.array([-2,0]), xy1=ser2Nto1_out_xy[1]+np.array([-2,0]), gridname0=rg_m3m4)
    out_pin=laygen.boundary_pin_from_rect(rout, rg_m3m4, 'out', laygen.layers['pin'][4], size=0, direction='top', netname='out')
    export_ports = add_to_export_ports(export_ports, out_pin)
    #RST_pin=laygen.pin(name='RST', layer=laygen.layers['pin'][3], xy=ser2Nto1_rst_xy[1], netname='RST', gridname=rg_m3m4)
    rRST=laygen.route(None, laygen.layers['metal'][3], xy0=ser2Nto1_rst_xy[1][0], xy1=ser2Nto1_rst_xy[1][1], gridname0=rg_m3m4)
    RST_pin=laygen.boundary_pin_from_rect(rRST, rg_m3m4, 'RST', laygen.layers['pin'][3], size=0, direction='left', netname='RST')
    export_ports = add_to_export_ports(export_ports, RST_pin)

    for i in range(num_ser):
        for j in range(ser_overall):
            if j%num_ser==i:
                in_pin=laygen.pin(name='in<'+str(j)+'>', layer=laygen.layers['pin'][4], xy=ser3rd_in_xy[i*num_ser_3rd+int(j/num_ser)], gridname=rg_m3m4)
                export_ports = add_to_export_ports(export_ports, in_pin)

    # power pin
    pwr_dim=laygen.get_xy(obj=laygen.get_template(name='tap', libname=logictemplib), gridname=rg_m2m3)
    rvdd = []
    rvss = []
    print(int(pwr_dim[0]))
    for i in range(-2, int(pwr_dim[0]/2)*2-2):
        subser0_vdd_xy=laygen.get_inst_pin_xy(iser_3rd[0].name, 'VDD' + str(i), rg_m2m3)
        subser0_vss_xy=laygen.get_inst_pin_xy(iser_3rd[0].name, 'VSS' + str(i), rg_m2m3)
        subser1_vdd_xy=laygen.get_inst_pin_xy(iser_2stg.name, 'VDD' + str(i), rg_m2m3)
        subser1_vss_xy=laygen.get_inst_pin_xy(iser_2stg.name, 'VSS' + str(i), rg_m2m3)
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([subser1_vdd_xy[1][0],0]), xy1=subser1_vdd_xy[1], gridname0=rg_m2m3))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([subser1_vss_xy[1][0],0]), xy1=subser1_vss_xy[1], gridname0=rg_m2m3))
        VDD_pin=laygen.pin(name = 'VDD'+str(i), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        export_ports = add_to_export_ports(export_ports, VDD_pin)
        VSS_pin=laygen.pin(name = 'VSS'+str(i), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
        export_ports = add_to_export_ports(export_ports, VSS_pin)

    x1=laygen.get_template_size(ser_name, rg_m3m4_thick, workinglib)[0]
    rvss_m4_xy=[]
    rvdd_m4_xy=[]
    for i in range(num_ser):
        ref_xy=laygen.get_inst_xy(iser_3rd[i].name, rg_m3m4_thick)
        rvss_m4=laygen.route(None, laygen.layers['metal'][4], xy0=ref_xy, xy1=np.array([x1,ref_xy[1]]), gridname0=rg_m3m4_thick)
        rvdd_m4=laygen.route(None, laygen.layers['metal'][4], xy0=ref_xy-[0,1], xy1=np.array([x1,ref_xy[1]-1]), gridname0=rg_m3m4_thick)
        rvss_m4_xy.append(laygen.get_rect_xy(name=rvss_m4.name, gridname=rg_m4m5_thick))
        rvdd_m4_xy.append(laygen.get_rect_xy(name=rvdd_m4.name, gridname=rg_m4m5_thick))
    ser_xy=laygen.get_inst_xy(iser_2stg.name, rg_m3m4_thick)
    print(ser_xy)
    y1=laygen.get_template_size(ser_name, rg_m3m4_thick, workinglib)[1]
    rvss_2stg_m4=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, ser_xy[1]+y1]), xy1=np.array([x1,ser_xy[1]+y1]), gridname0=rg_m3m4_thick)
    rvdd_2stg_m4=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, ser_xy[1]+y1-1]), xy1=np.array([x1,ser_xy[1]-1+y1]), gridname0=rg_m3m4_thick)
    rvss_m4_xy.append(laygen.get_rect_xy(name=rvss_2stg_m4.name, gridname=rg_m4m5_thick))
    rvdd_m4_xy.append(laygen.get_rect_xy(name=rvdd_2stg_m4.name, gridname=rg_m4m5_thick))
    print(rvss_m4_xy)
    input_rails_xy = [rvss_m4_xy, rvdd_m4_xy]
    rvss_m5 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_SER_M5_', 
                layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VSS', 'VDD'], direction='y', 
                input_rails_xy=input_rails_xy, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)

    '''
    input_rails_xy=[]
    rvssr_m3_xy=[]
    rvddr_m3_xy=[]
    rvssl_m3_xy=[]
    rvddl_m3_xy=[]
    for i in range(-2, int(pwr_dim[0]/2)*2-2):
        if i%2==0:
            rvssr_m3_xy.append(laygen.get_rect_xy(name=rvss[i].name, gridname=rg_m3m4_thick))
            rvddr_m3_xy.append(laygen.get_rect_xy(name=rvdd[i].name, gridname=rg_m3m4_thick))
        else:
            rvssl_m3_xy.append(laygen.get_rect_xy(name=rvss[i].name, gridname=rg_m3m4_thick))
            rvddl_m3_xy.append(laygen.get_rect_xy(name=rvdd[i].name, gridname=rg_m3m4_thick))
    input_rails_xy = [rvssl_m3_xy, rvddl_m3_xy]
    rvssl_m4 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_CDRVL_M4_', 
                layer=laygen.layers['metal'][4], gridname=rg_m3m4_thick, netnames=['VSS', 'VDD'], direction='x', 
                input_rails_xy=input_rails_xy, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    input_rails_xy = [rvssr_m3_xy, rvddr_m3_xy]
    rvssr_m4 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_CDRVL_M4_', 
                layer=laygen.layers['metal'][4], gridname=rg_m3m4_thick, netnames=['VSS', 'VDD'], direction='x', 
                input_rails_xy=input_rails_xy, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    '''
    # export_dict will be written to a yaml file for using with StdCellBase
    size_x=laygen.templates.get_template(ser_name, workinglib).xy[1][0]
    size_y=laygen.templates.get_template(ser_name, workinglib).xy[1][1] + num_ser*laygen.templates.get_template(ser_3rd_name, workinglib).xy[1][1]

    export_dict['cells'][cell_name]['ports'] = export_ports
    export_dict['cells'][cell_name]['size_um'] = [float(int(size_x*1e3))/1e3, float(int(size_y*1e3))/1e3]
    #export_dict['cells']['clk_dis_N_units']['num_ways'] = num_ways
    # print('export_dict:')
    # pprint(export_dict)
    # save_path = path.dirname(path.dirname(path.realpath(__file__))) + '/dsn_scripts/'
    save_path = 'ser_generated' 
    #if path.isdir(save_path) == False:
    #    mkdir(save_path)
    with open(save_path + '_int.yaml', 'w') as f:
        yaml.dump(export_dict, f, default_flow_style=False)

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
    workinglib = 'serdes_generated'
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
    rg_m3m4_thick = 'route_M3_M4_basic_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'


    #display
    #laygen.display()
    #laygen.templates.display()
    #laygen.save_template(filename=workinglib+'_templates.yaml', libname=workinglib)

    mycell_list = []
    
    #load from preset
    load_from_file=True
    yamlfile_spec="serdes_spec.yaml"
    yamlfile_size="serdes_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        num_ser=specdict['num_ser']
        num_ser_3rd=specdict['num_ser_3rd']
        m_ser=sizedict['m_ser']
        ser_overall = num_ser * num_ser_3rd
        cell_name='ser_3stage_'+str(ser_overall)+'to1'

    print(cell_name+" generating")
    mycell_list.append(cell_name)
    laygen.add_cell(cell_name)
    laygen.sel_cell(cell_name)
    generate_serializer(laygen, objectname_pfix='SER', templib_logic=logictemplib, 
                          placement_grid=pg, routing_grid_m2m3=rg_m2m3, routing_grid_m4m5=rg_m4m5, num_ser=num_ser,
                          m_ser=m_ser, num_ser_3rd=num_ser_3rd, origin=np.array([0, 0]))
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

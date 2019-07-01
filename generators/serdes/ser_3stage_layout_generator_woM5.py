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
#import logging;logging.basicConfig(level=logging.DEBUG)

def generate_serializer(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m2m3,
                          routing_grid_m4m5, num_ser=8, num_ser_3rd=4, m_ser=1, origin=np.array([0, 0])):
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
    laygen.pin(name='CLK', layer=laygen.layers['pin'][4], xy=ser2Nto1_clk_xy, gridname=rg_m3m4)
    laygen.pin(name='CLKB', layer=laygen.layers['pin'][4], xy=ser2Nto1_clkb_xy, gridname=rg_m3m4)
    laygen.pin(name='out', layer=laygen.layers['pin'][4], xy=ser2Nto1_out_xy, gridname=rg_m3m4)
    laygen.pin(name='RST', layer=laygen.layers['pin'][3], xy=ser2Nto1_rst_xy[1], netname='RST', gridname=rg_m3m4)

    for i in range(num_ser):
        for j in range(ser_overall):
            if j%num_ser==i:
                laygen.pin(name='in<'+str(j)+'>', layer=laygen.layers['pin'][4], xy=ser3rd_in_xy[i*num_ser_3rd+int(j/num_ser)], gridname=rg_m3m4)

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
        laygen.pin(name = 'VDD'+str(i), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSS'+str(i), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')

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
    rg_m4m5 = 'route_M4_M5_basic'
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

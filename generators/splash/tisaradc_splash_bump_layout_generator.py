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

def generate_bump(laygen, objectname_pfix, bump_libname, workinglib, bump_vdd_name, bump_vss_name, bump_sig_name,
                  bump_plug_name, route_v_name, route_h_name,
                  bump_array, ref_xy, bump_pitch, placement_grid, origin=np.array([0, 0])):
    """generate sar array """
    pg = placement_grid

    # bump placement
    pin_size = 20
    bump_size = 72.3
    for i in range(len(bump_array)):
        if not len(bump_array[0]) == len(bump_array[i]):
            print("Number of bumps in each row should be the same")
        else:
            for j in range(len(bump_array[i])):
                if bump_array[i][j].startswith('VDD'):
                    bump_name =  bump_vdd_name
                elif bump_array[i][j].startswith('VSS'):
                    bump_name = bump_vss_name
                else:
                    bump_name = bump_sig_name
                name = "bump_"+bump_array[i][j]+'_'+str(i)+'_'+str(j)
                plug_name = "bump_plug_"+bump_array[i][j]+'_'+str(i)+'_'+str(j)
                xy = ref_xy + [bump_pitch * j, bump_pitch * i]
                laygen.add_inst(name=name, libname=bump_libname, cellname=bump_name, xy=xy)
                laygen.add_inst(name=plug_name, libname=bump_libname, cellname=bump_plug_name, xy=xy)
                laygen.add_pin(bump_array[i][j]+'_'+str(i)+'_'+str(j), bump_array[i][j],
                               xy=[xy+(bump_size-pin_size)/2, xy+(bump_size+pin_size)/2], layer=laygen.layers['pin'][9])
                #route
                if not j == len(bump_array[i])-1:
                    if bump_array[i][j]==bump_array[i][j+1]:
                        laygen.add_inst(None, libname=bump_libname, cellname=route_h_name, xy=xy)
                if not i == len(bump_array)-1:
                    if bump_array[i][j]==bump_array[i+1][j]:
                        laygen.add_inst(None, libname=bump_libname, cellname=route_v_name, xy=xy)


    # bnd_size = laygen.get_template('boundary_bottom', libname=utemplib).size
    # sar_slice_size = laygen.get_template_size(sar_slice_name, pg, libname=sar_libname)
    # clkcal_size = laygen.templates.get_template(clkcal_name, libname=clkdist_libname).size
    # # ret_offset = laygen.get_template_size('boundary_bottomleft', pg, libname=utemplib)[0]
    # ret_offset = 0
    # clkdist_xy = laygen.templates.get_template(clkdist_name, libname=clkdist_libname).xy
    # clkdist_off_y = laygen.grids.get_absgrid_y(pg, clkdist_xy[0][1])
    # # clkdist_xy =laygen.get_template_xy(clkdist_name, pg, libname=clkdist_libname)
    # clkcal_xy = laygen.templates.get_template(clkcal_name, libname=clkdist_libname).xy
    # clkcal_y = laygen.get_template_size(ret_name, pg, libname=ret_libname)[1] + \
    #            laygen.get_template_size(sar_name, pg, libname=sar_libname)[1] + \
    #            laygen.get_template_size(clkdist_name, pg, libname=clkdist_libname)[1] + \
    #            laygen.grids.get_absgrid_y(pg, clkcal_xy[1][1])
    #
    # iret = laygen.place(name="I" + objectname_pfix + 'RET0', templatename=ret_name,
    #                   gridname=pg, xy=origin-[ret_offset,0], template_libname=ret_libname)
    # sar_xy = origin + (laygen.get_template_size(ret_name, gridname=pg, libname=ret_libname)*np.array([0,1]) )
    # isar = laygen.relplace(name="I" + objectname_pfix + 'SAR0', templatename=sar_name,
    #                   gridname=pg, xy=sar_xy, template_libname=sar_libname)
    # isarcal1 = laygen.relplace(name="I" + objectname_pfix + 'SARCAL1', templatename=sar_slice_name,
    #                        gridname=pg, refinstname=isar.name, direction='right', template_libname=sar_libname)
    # isarcal0 = laygen.relplace(name="I" + objectname_pfix + 'SARCAL0', templatename=sar_slice_name,
    #                            gridname=pg, refinstname=isarcal1.name, direction='right', template_libname=sar_libname)
    # iclkdist = laygen.relplace(name="I" + objectname_pfix + 'CLKDIST0', templatename=clkdist_name,
    #                     gridname=pg, refinstname=isar.name, direction='top',
    #                     xy=[0, -clkdist_off_y], template_libname=clkdist_libname)
    # iclkcal = laygen.relplace(name="I" + objectname_pfix + 'CLKCAL0', templatename=clkcal_name,
    #                   gridname=pg, transform='MX',
    #                   xy=[sar_slice_size[0]*2/2, clkcal_y],
    #                   template_libname=clkdist_libname)
    #
    # sar_template = laygen.templates.get_template(sar_name, sar_libname)
    # sar_pins=sar_template.pins
    # sar_xy=isar.xy
    # ret_template = laygen.templates.get_template(ret_name, ret_libname)
    # ret_pins=ret_template.pins
    # ret_xy=iret.xy
    # clkdist_template = laygen.templates.get_template(clkdist_name, clkdist_libname)
    # clkdist_pins=clkdist_template.pins
    # clkdist_xy=iclkdist.xy
    #
    # #prboundary
    # # sar_size = laygen.templates.get_template(sar_name, libname=sar_libname).size
    # # ret_size = laygen.templates.get_template(ret_name, libname=ret_libname).size
    # space_size = laygen.templates.get_template('boundary_bottom', libname=utemplib).size
    # # clkdist_size = laygen.templates.get_template(clkdist_name, libname=clkdist_libname).size+clkdist_offset
    # # clkcal_size = laygen.templates.get_template(clkcal_name, libname=clkdist_libname).size
    # size_x=iclkcal.xy[0]+iclkcal.size[0]
    # size_y=int((iclkcal.xy[1]-laygen.templates.get_template(clkcal_name, libname=clkdist_libname).xy[0][1])/space_size[1]+1)*space_size[1]
    # laygen.add_rect(None, np.array([origin, origin+np.array([size_x, size_y])]), laygen.layers['prbnd'])

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
    # laygen.load_template(filename='adc_retimer.yaml', libname=ret_libname)
    #laygen.load_template(filename=ret_libname+'.yaml', libname=ret_libname)
    laygen.load_template(filename=clkdist_libname+'.yaml', libname=clkdist_libname)
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
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        num_bits=specdict['n_bit']
        num_slices=specdict['n_interleave']

    cellname = 'tisaradc_bumps'
    # bump_libname = 'C28SOI_IO_BUMP_6U1X2T8XLB'
    bump_libname = 'adc_sar_manual'
    bump_vdd_name = 'BUMP_72X72_PAD'
    bump_vss_name = 'BUMP_72X72_PAD'
    bump_sig_name = 'BUMP_72X72_PAD'
    bump_plug_name = 'bumpplug_bottom'
    route_v_name = 'bumproute_v'
    route_h_name = 'bumproute_h'
    # bump_array = [['VDD', 'VDD', 'VREF0', 'VSS', 'VSS', 'CLKP', 'CLKN', 'VSS', 'VSS', 'VDD', 'VDD'],
    #               ['VDD', 'VDD', 'VREF1', 'VSS', 'VSS', 'VDD', 'VDD', 'VSS', 'VSS', 'VDD', 'VDD'],
    #               ['VDD', 'VDD', 'VREF2', 'VSS', 'VSS', 'VDD', 'VDD', 'VSS', 'VSS', 'VDD', 'VDD'],
    #               ['VDD', 'VDD', 'VSS', 'IINP', 'IINN', 'VSS', 'VSS', 'QINP', 'QINN', 'VDD', 'VDD']]
    bump_array = [['VDD', 'VDD', 'VREF2', 'VREF1', 'VREF0', 'VSS', 'VSS', 'VSS', 'VSS', 'VSS', 'VDD', 'VDD', 'VDD', 'VDD'],
                  ['VDD', 'VDD', 'VSS', 'VSS', 'VSS', 'VSS', 'VSS', 'VSS', 'VSS', 'VSS', 'VDD', 'VDD', 'VDD', 'VDD'],
                  ['VDD', 'VDD', 'VSS', 'VSS', 'VSS', 'VSS', 'VSS', 'VSS', 'VSS', 'VSS', 'VDD', 'VDD', 'VDD', 'VDD'],
                  ['VDD', 'VDD', 'IINP', 'IINM', 'VSS', 'VSS', 'CLKP', 'CLKN', 'VSS', 'VSS', 'QINP', 'QINM', 'VDD', 'VDD']]
    ref_xy = np.array([-186.43, -170*1.5])
    bump_pitch = 170

    #layout generation
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_bump(laygen, objectname_pfix='BUMP',
                 bump_libname=bump_libname, workinglib=workinglib, placement_grid=pg,
                 bump_vdd_name=bump_vdd_name, bump_vss_name=bump_vss_name, bump_sig_name=bump_sig_name,
                 bump_plug_name=bump_plug_name, route_v_name=route_v_name, route_h_name=route_h_name,
                 bump_array=bump_array, ref_xy=ref_xy, bump_pitch=bump_pitch, origin=np.array([0, 0]))
    # laygen.add_template_from_cell()

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

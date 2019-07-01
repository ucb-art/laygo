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
from adc_sar_salatch_pmos_layout_generator import *

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
    rg_m1m2 = 'route_M1_M2_cmos'
    rg_m1m2_thick = 'route_M1_M2_basic_thick'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m2m3_thick = 'route_M2_M3_thick_basic'
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
    #salatch generation (wboundary)
    #cellname = 'salatch'
    cellname = 'salatch_pmos_standalone'
    print(cellname+" generating")
    mycell_list.append(cellname)
    m_sa=8
    m_rst_sa=8
    m_rgnn_sa=2
    m_buf_sa=8
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        m_sa=sizedict['salatch_m']
        m_rst_sa=sizedict['salatch_m_rst']
        m_rgnn_sa=sizedict['salatch_m_rgnn']
        m_buf_sa=sizedict['salatch_m_buf']
    m_in=int(m_sa/2)            #4
    m_clkh=max(1, m_in-1)                 #4
    m_rstn=int(m_rst_sa/2)                    #1
    m_buf=int(m_buf_sa/2)
    m_rgnn=int(m_rgnn_sa/2) 
    m_ofst=1

    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)

    sa_origin=np.array([0, 0])

    #salatch body
    # 1. generate without spacing
    generate_salatch_pmos(laygen, objectname_pfix='SA0',
                                placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick,
                                routing_grid_m2m3=rg_m2m3, routing_grid_m2m3_thick=rg_m2m3_thick, 
                                routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5,
                                devname_ptap_boundary='ptap_fast_boundary', devname_ptap_body='ptap_fast_center_nf1',
                                devname_nmos_boundary='nmos4_fast_boundary', devname_nmos_body='nmos4_fast_center_nf2',
                                devname_nmos_dmy='nmos4_fast_dmy_nf2',
                                devname_pmos_boundary='pmos4_fast_boundary', devname_pmos_body='pmos4_fast_center_nf2',
                                devname_pmos_dmy='pmos4_fast_dmy_nf2',
                                devname_ntap_boundary='ntap_fast_boundary', devname_ntap_body='ntap_fast_center_nf1',
                                m_in=m_in, m_ofst=m_ofst, m_clkh=m_clkh, m_rgnn=m_rgnn, m_rstn=m_rstn, m_buf=m_buf,
                                num_vert_pwr=2, origin=sa_origin)
    laygen.add_template_from_cell()
    # 2. calculate spacing param and regenerate
    x0 = 2*laygen.templates.get_template('capdac', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0]
    m_space = int(round(x0 / 2 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_space_4x = int(m_space / 4)
    m_space_2x = int((m_space - m_space_4x * 4) / 2)
    m_space_1x = int(m_space - m_space_4x * 4 - m_space_2x * 2)
    #print("debug", x0, laygen.templates.get_template('capdrv_array_7b', libname=workinglib).xy[1][0] \
    #        , laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
    #        , laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0], m_space, m_space_4x, m_space_2x, m_space_1x)
    
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_salatch_pmos(laygen, objectname_pfix='SA0',
                                placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick,
                                routing_grid_m2m3=rg_m2m3, routing_grid_m2m3_thick=rg_m2m3_thick, 
                                routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5,
                                devname_ptap_boundary='ptap_fast_boundary', devname_ptap_body='ptap_fast_center_nf1',
                                devname_nmos_boundary='nmos4_fast_boundary', devname_nmos_body='nmos4_fast_center_nf2',
                                devname_nmos_dmy='nmos4_fast_dmy_nf2',
                                devname_pmos_boundary='pmos4_fast_boundary', devname_pmos_body='pmos4_fast_center_nf2',
                                devname_pmos_dmy='pmos4_fast_dmy_nf2',
                                devname_ntap_boundary='ntap_fast_boundary', devname_ntap_body='ntap_fast_center_nf1',
                                m_in=m_in, m_ofst=m_ofst, m_clkh=m_clkh, m_rgnn=m_rgnn, m_rstn=m_rstn, m_buf=m_buf,
                                num_vert_pwr=2, origin=sa_origin)
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

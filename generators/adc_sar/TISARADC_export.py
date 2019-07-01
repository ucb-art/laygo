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
import pprint
import numpy as np
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

    mycell_list = []
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"

    cellname = 'TISARADC'
    sar_name = 'tisaradc_body'
    sar_slice_name = 'sar_wsamp'
    rdac_name = 'r2r_dac_array'
    htree_name = 'tisar_htree_diff'
    #tisar_space_name = 'tisaradc_body_space'
    space_1x_name = 'space_1x'
     
    print(cellname+" exporting")
    mycell_list.append('DUMMYCELLNAME')
    laygen.add_cell('DUMMYCELLNAME')
    laygen.sel_cell('DUMMYCELLNAME')

    origin = np.array([0, 0])
    isar = laygen.relplace(name="DUMMY", templatename=cellname, gridname=pg, xy=origin, template_libname=workinglib)

    export_dict = {'boundaries': {'lib_name': 'ge_tech_logic_templates',
                                  'lr_width': 8,
                                  'tb_height': 0.5},
                   'cells': {cellname: {'cell_name': cellname,
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
    #
    sar_template = laygen.templates.get_template(cellname, workinglib)
    pdict = sar_template.pins
    size = sar_template.size
    export_ports = dict()
    for pn, p in pdict.items():
        _pin = laygen.add_pin(pn, pdict[pn]['netname'], origin + pdict[pn]['xy'], pdict[pn]['layer'])
        export_ports = add_to_export_ports(export_ports, _pin)
    export_dict['cells'][cellname]['ports'] = export_ports
    export_dict['cells'][cellname]['size_um'] = [float(int(size[0]*1e3))/1e3, float(int(size[1]*1e3))/1e3]

    save_path = workinglib
    with open(save_path + '_int.yaml', 'w') as f:
        yaml.dump(export_dict, f, default_flow_style=False)

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

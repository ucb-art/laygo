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

"""Lab2: generate layout on abstract grid
   1. Copy this file to working directory
   2. For GDS export, prepare a layermap file
"""
import laygo
#import logging; logging.basicConfig(level=logging.DEBUG)

laygen = laygo.GridLayoutGenerator(config_file="laygo_config.yaml") #change physical grid resolution
workinglib = 'laygo_working'
utemplib = laygen.tech+'_microtemplates_dense'
if laygen.tech=='laygo10n' or laygen.tech=='layge_faketech': #fake technology
    laygen.use_phantom = True

laygen.add_library(workinglib)
laygen.sel_library(workinglib)

#bag import, if bag does not exist, gds import
import imp
try:
    imp.find_module('bag')
    #bag import
    print("import from BAG")
    import bag
    prj = bag.BagProject()
    db=laygen.import_BAG(prj, utemplib, append=False)
except ImportError:
    #gds import
    print("import from GDS")
    db = laygen.import_GDS(laygen.tech+'_microtemplates_dense.gds', layermapfile=laygen.tech+".layermap", append=False)

#construct template
laygen.construct_template_and_grid(db, utemplib, layer_boundary=laygen.layers['prbnd'])

#display and save
#laygen.templates.display()
#laygen.grids.display()
laygen.templates.export_yaml(filename=laygen.tech+'_microtemplates_dense_templates.yaml')
laygen.grids.export_yaml(filename=laygen.tech+'_microtemplates_dense_grids.yaml')

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

"""Logic layout demo
"""
if __name__ == '__main__':
    import laygo
    import numpy as np

    # initialize #######################################################################################################
    import imp
    try:
        imp.find_module('bag')
        lib_path = ''
        laygen = laygo.GridLayoutGenerator(config_file=lib_path+"laygo_config.yaml")
        use_phantom = False
    except ImportError:
        # if bag does not exist, load faketech lib and export phantom to gds
        lib_path = '../../labs/'
        use_phantom = True
    laygen = laygo.GridLayoutGenerator(config_file=lib_path + "laygo_config.yaml")
    laygen.use_phantom = use_phantom

    # template and grid load
    utemplib = laygen.tech + '_microtemplates_dense'  # device template library name
    laygen.load_template(filename=lib_path + utemplib + '_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=lib_path + utemplib + '_grids.yaml', libname=utemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)

    # generate a library and cell to work on
    laygen.add_library('laygo_working')
    laygen.add_cell('nand_demo')

    # placement ########################################################################################################
    # placement parameters
    pg = 'placement_basic'  # placement grid
    nb = 'nmos4_fast_boundary'  # nmos boundary cellname
    nc = 'nmos4_fast_center_nf2'  # nmos body cellname
    pb = 'pmos4_fast_boundary'  # pmos boundary cellname
    pc = 'pmos4_fast_center_nf2'  # pmos body cellname
    nname = [nb, nc, nb, nb, nc, nb]  # nmos device names
    pname = [pb, pc, pb, pb, pc, pb]  # pmos device names
    shape = [[i, 1] for i in [1, 2, 1, 1, 2, 1]]  # device shapes

    nd = []  # nmos
    robj = None
    for _dev, _shape in zip(nname, shape):
        nd += [laygen.relplace(cellname=_dev, gridname=pg, refobj=robj, shape=_shape)]  # default direction is right
        robj = nd[-1].right
    pd = []  # pmos
    robj = nd[0].top
    for _dev, _shape in zip(pname, shape):
        pd += [laygen.relplace(cellname=_dev, gridname=pg, refobj=robj, shape=_shape, transform='MX')]
        robj = pd[-1].right

    # route ############################################################################################################
    # route parameters
    rg12 = 'route_M1_M2_cmos'  # grids
    rg23 = 'route_M2_M3_cmos'

    # a
    for _ng, _pg in zip(nd[1].pins['G0'].elements[:, 0], pd[1].pins['G0'].elements[:, 0]):
        laygen.route(gridname0=rg12, refobj0=_ng, refobj1=_pg, via0=[0, 0])
    ra = laygen.route(gridname0=rg12, refobj0=nd[1].pins['G0'].elements[0, 0], refobj1=nd[1].pins['G0'].elements[-1, 0])
    # b
    for _ng, _pg in zip(nd[4].pins['G0'].elements[:, 0], pd[4].pins['G0'].elements[:, 0]):
        laygen.route(gridname0=rg12, refobj0=_ng, refobj1=_pg, via1=[0, 0])
    rb = laygen.route(gridname0=rg12, refobj0=pd[4].pins['G0'].elements[0, 0], refobj1=pd[4].pins['G0'].elements[-1, 0])
    # internal connections
    laygen.route(xy0=[0, 1], xy1=[0, 1], gridname0=rg12, refobj0=nd[1].pins['D0'].elements[0, 0],
                 refobj1=nd[4].pins['S1'].elements[-1, 0])
    for _p in np.concatenate(
            (nd[1].pins['D0'].elements[:, 0], nd[4].pins['S0'].elements[:, 0], nd[4].pins['S1'].elements[:, 0])):
        v = laygen.via(xy=[0, 1], refobj=_p, gridname=rg12)
    # output
    laygen.route(gridname0=rg12, refobj0=nd[4].pins['D0'].elements[0, 0], refobj1=nd[4].pins['D0'].elements[-1, 0])
    laygen.route(gridname0=rg12, refobj0=pd[1].pins['D0'].elements[0, 0], refobj1=pd[4].pins['D0'].elements[-1, 0])
    for _p in np.concatenate(
            [nd[4].pins['D0'].elements[:, 0], pd[1].pins['D0'].elements[:, 0], pd[4].pins['D0'].elements[:, 0]]):
        v = laygen.via(refobj=_p, gridname=rg12)
    ro = laygen.route(gridname0=rg23, refobj0=nd[4].pins['D0'].elements[-1, 0],
                      refobj1=pd[4].pins['D0'].elements[-1, 0],
                      via0=[0, 0], via1=[0, 0])
    # power and ground route
    for dev in np.concatenate((nd[1].elements[:, 0], pd[1].elements[:, 0], pd[4].elements[:, 0])):
        for pn in ['S0', 'S1']:
            laygen.route(gridname0=rg12, refobj0=dev.pins[pn], refobj1=dev.bottom, direction='y', via1=[0, 0])
    # power and groud rails
    rvdd = laygen.route(gridname0=rg12, refobj0=pd[0].bottom_left, refobj1=pd[5].bottom_right)
    rvss = laygen.route(gridname0=rg12, refobj0=nd[0].bottom_left, refobj1=nd[5].bottom_right)

    # pin ##############################################################################################################
    for pn, pg, pr in zip(['A', 'B', 'O', 'VDD', 'VSS'], [rg12, rg12, rg23, rg12, rg12], [ra, rb, ro, rvdd, rvss]):
        laygen.pin(name=pn, gridname=pg, refobj=pr)

    # display ##########################################################################################################
    laygen.display()

    # export ###########################################################################################################
    # bag export, if bag does not exist, gds export
    mycell_list = ['nand_demo']
    import imp
    try:
        imp.find_module('bag')
        import bag

        prj = bag.BagProject()
        for mycell in mycell_list:
            laygen.sel_cell(mycell)
            laygen.export_BAG(prj, array_delimiter=['[', ']'])
    except ImportError:
        laygen.export_GDS('output.gds', cellname=mycell_list,
                          layermapfile=lib_path+"laygo_faketech.layermap")  # change layermapfile

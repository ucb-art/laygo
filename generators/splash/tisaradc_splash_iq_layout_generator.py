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

def generate_tisaradc_splash(laygen, objectname_pfix, ret_libname, sar_libname, clkdist_libname, space_1x_libname, ret_name, sar_name, clkdist_name, space_1x_name,
                                placement_grid,
                                routing_grid_m3m4, routing_grid_m4m5, routing_grid_m4m5_basic_thick, routing_grid_m5m6, routing_grid_m5m6_thick,
                                routing_grid_m5m6_basic_thick, routing_grid_m5m6_thick_basic,
                                routing_grid_m6m7_thick, routing_grid_m7m8_thick,
                                num_bits=9, num_slices=8, clkdist_offset=14.4, trackm=4, origin=np.array([0, 0])):
    """generate sar array """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_basic_thick = routing_grid_m5m6_basic_thick
    rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic
    rg_m6m7_thick = routing_grid_m6m7_thick
    rg_m7m8_thick = routing_grid_m7m8_thick

    # placement
    laygen.add_inst(name=bump_name, libname=workinglib, cellname=bump_name, xy=origin)
    iadci = laygen.relplace(name="I" + objectname_pfix + 'ADCI', templatename=sar_name,
                      gridname=pg, xy=origin, template_libname=workinglib)
    iadcq = laygen.relplace(name="I" + objectname_pfix + 'ADCQ', templatename=sar_name,
                       gridname=pg, refinstname=iadci.name, direction='right', transform='MY',
                            offset=np.array([laygen.templates.get_template(sar_name, libname=workinglib).xy[0][0]*2,0]), template_libname=workinglib)


    # ADCI pins
    # pin_prefix_list=['VDD', 'VSS', 'VREF', 'RSTP', 'RSTN', 'CLKIP', 'CLKIN']
    # pfix = 'VDD' or 'VSS' or 'VREF' or 'RSTP' or 'RSTN' or 'CLKIP' or 'CLKIN'
    adc_template = laygen.templates.get_template(sar_name, workinglib)
    adc_pins = adc_template.pins
    for pn, p in adc_pins.items():
        # # if pn.startswith('VDD') or pn.startswith('VSS') or pn.startswith('VREF') or pn.startswith('RST') or pn.startswith('CLKI'):
        # #     laygen.add_pin('I_'+pn, adci_pins[pn]['netname'], iadci.xy + adci_pins[pn]['xy'], adci_pins[pn]['layer'])
        # #     laygen.add_pin('Q_'+pn, adci_pins[pn]['netname'], iadcq.xy + adci_pins[pn]['xy'], adci_pins[pn]['layer'])
        # if pn.startswith('RST'):
        #     # rst = laygen.route(None, adc_pins[pn]['layer'], xy0=iadci.xy + adc_pins[pn]['xy'],
        #     #                     xy1=iadcq.xy + adc_pins[pn]['xy'], gridname0=rg_m2m3_pin)
        #     rout = laygen.add_rect(None, xy=[(iadci.xy + adc_pins[pn]['xy'])[0], (iadcq.xy + adc_pins[pn]['xy'])[1]],
        #                           layer=laygen.layers['metal'][2])
        #     laygen.add_pin(pn, adc_pins[pn]['netname'], [(iadci.xy + adc_pins[pn]['xy'])[0], (iadcq.xy + adc_pins[pn]['xy'])[1]],
        #                    adc_pins[pn]['layer'])
        # elif pn.startswith('CLKI') or pn.startswith('VREF'):
        #     rout = laygen.add_rect(None, xy=[(iadci.xy + adc_pins[pn]['xy'])[0], (iadcq.xy + adc_pins[pn]['xy'])[1]],
        #                           layer=laygen.layers['metal'][6])
        #     laygen.add_pin(pn, adc_pins[pn]['netname'],
        #                    [(iadci.xy + adc_pins[pn]['xy'])[0], (iadcq.xy + adc_pins[pn]['xy'])[1]],
        #                    adc_pins[pn]['layer'])
        # elif pn.startswith('VDD') or pn.startswith('VSS'):
        #     laygen.add_pin('I_'+pn, adc_pins[pn]['netname'], iadci.xy + adc_pins[pn]['xy'], adc_pins[pn]['layer'])
        #     laygen.add_pin('Q_'+pn, adc_pins[pn]['netname'], iadcq.xy + adc_pins[pn]['xy'], adc_pins[pn]['layer'])
        # else:
        #     laygen.add_pin('I_'+pn, 'I_'+adc_pins[pn]['netname'], iadci.xy + adc_pins[pn]['xy'], adc_pins[pn]['layer'])
        #     laygen.add_pin('Q_'+pn, 'Q_'+adc_pins[pn]['netname'], iadcq.xy + adc_pins[pn]['xy'], adc_pins[pn]['layer'])

        if pn.startswith('CLKI') or pn.startswith('VREF<'):
            # rout = laygen.add_rect(None, xy=[(iadci.xy + adc_pins[pn]['xy'][0]), (iadcq.xy - [adc_pins[pn]['xy'][0][0], 0] + [0, adc_pins[pn]['xy'][0][1]])],
            #                        layer=laygen.layers['metal'][6])
            # laygen.add_pin(pn, adc_pins[pn]['netname'],
            #                [(iadci.xy + adc_pins[pn]['xy'])[0], (iadcq.xy - [adc_pins[pn]['xy'][0][0], 0] + [0, adc_pins[pn]['xy'][0][1]])],
            #                adc_pins[pn]['layer'])
            rout = laygen.route(None, laygen.layers['metal'][6], xy0=laygen.get_inst_pin_xy(iadci.name, pn, rg_m6m7_thick)[0],
                          xy1=laygen.get_inst_pin_xy(iadcq.name, pn, rg_m6m7_thick)[0], gridname0=rg_m6m7_thick)
            laygen.pin_from_rect(pn, adc_pins[pn]['layer'], rout, rg_m6m7_thick, adc_pins[pn]['netname'])
        elif pn.startswith('VREF_SF_bypass'):
            laygen.add_pin(pn, adc_pins[pn]['netname'], iadci.xy + adc_pins[pn]['xy'], adc_pins[pn]['layer'])
        elif pn.startswith('VDD') or pn.startswith('VSS'):
            laygen.add_pin('I_' + pn, adc_pins[pn]['netname'], iadci.xy + adc_pins[pn]['xy'], adc_pins[pn]['layer'])
            # laygen.add_pin('Q_' + pn, adc_pins[pn]['netname'], iadcq.xy + adc_pins[pn]['xy'], adc_pins[pn]['layer'])
            laygen.add_pin('Q_' + pn, adc_pins[pn]['netname'], iadcq.xy - [[adc_pins[pn]['xy'][0][0], 0], [adc_pins[pn]['xy'][1][0], 0]] + [[0, adc_pins[pn]['xy'][0][1]], [0, adc_pins[pn]['xy'][1][1]]], adc_pins[pn]['layer'])
        else:
            laygen.add_pin('I_' + pn, 'I_' + adc_pins[pn]['netname'], iadci.xy + adc_pins[pn]['xy'], adc_pins[pn]['layer'])
            laygen.add_pin('Q_' + pn, 'Q_' + adc_pins[pn]['netname'], iadcq.xy - [[adc_pins[pn]['xy'][0][0], 0], [adc_pins[pn]['xy'][1][0], 0]] + [[0, adc_pins[pn]['xy'][0][1]], [0, adc_pins[pn]['xy'][1][1]]], adc_pins[pn]['layer'])

    # adcq_template = laygen.templates.get_template(sar_name, workinglib)
    # adcq_pins = adcq_template.pins
    # for pn, p in adcq_pins.items():
    #     for pfix in pin_prefix_list:
    #         if pn.startswith(pfix):
    #             laygen.add_pin(pn, adci_pins[pn]['netname'], iadci.xy + adci_pins[pn]['xy'], adci_pins[pn]['layer'])
    #         else:
    #             laygen.add_pin('Q_' + pn, 'Q_' + adcq_pins[pn]['netname'], iadcq.xy + adcq_pins[pn]['xy'], adcq_pins[pn]['layer'])
        # if pn.startswith('ASCLKD'):
        #     pxy=laygen.get_inst_pin_xy(iadci.name, pn, rg_m4m5)
        #     rout = laygen.route(None, laygen.layers['metal'][5], pxy[0], [pxy[0][0], 0], rg_m4m5)
        #     laygen.boundary_pin_from_rect(rout, rg_m4m5, pn, layer=laygen.layers['pin'][5],
        #                               direction='bottom', size=4)
        # if pn.startswith('EXTSEL_'):
        #     pxy=laygen.get_inst_pin_xy(iadci.name, pn, rg_m4m5)
        #     rout = laygen.route(None, laygen.layers['metal'][5], pxy[0], [pxy[0][0], 0], rg_m4m5)
        #     laygen.boundary_pin_from_rect(rout, rg_m4m5, pn, layer=laygen.layers['pin'][5],
        #                               direction='bottom', size=4)
        # if pn.startswith('VREF'):
        #     pxy=laygen.get_inst_pin_xy(iadci.name, pn, rg_m5m6_thick)
        #     laygen.pin(pn, layer=adci_pins[pn]['layer'], xy=pxy, gridname=rg_m5m6_thick, netname=pn.split("_")[0])
        # if pn.startswith('samp_body'):
        #     pxy=laygen.get_inst_pin_xy(iadci.name, pn, rg_m5m6_thick)
        #     laygen.pin(pn, layer=adci_pins[pn]['layer'], xy=pxy, gridname=rg_m5m6_thick)
        # if pn.startswith('bottom_body'):
        #     pxy=laygen.get_inst_pin_xy(iadci.name, pn, rg_m3m4)
        #     laygen.pin(pn, layer=adci_pins[pn]['layer'], xy=pxy, gridname=rg_m3m4, netname=pn.split("_bottom")[0])

    # # CAL ADC pins
    # sar_template = laygen.templates.get_template(sar_slice_name, sar_libname)
    # sar_pins = sar_template.pins
    # isarcal_name = [isarcal0.name, isarcal1.name]
    # for i in range(len(isarcal_name)):
    #     for j in range(num_bits):
    #         pxy = laygen.get_inst_pin_xy(isarcal_name[i], 'ADCOUT<%d>' % (j), rg_m4m5)
    #         rout = laygen.route(None, laygen.layers['metal'][5], pxy[0], [pxy[0][0], 0], rg_m4m5)
    #         laygen.boundary_pin_from_rect(rout, rg_m4m5, 'ADCO_CAL%d<%d>' % (i, j), layer=laygen.layers['pin'][5],
    #                                       direction='bottom', size=4)
    #     pxy = laygen.get_inst_pin_xy(isarcal_name[i], 'CLKO0', rg_m4m5)
    #     refxy = laygen.get_inst_pin_xy(isarcal_name[i], 'ADCOUT<0>', rg_m4m5)
    #     rv0, rh0, rout = laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
    #                                       xy0=pxy[0], xy1=[refxy[0][0] - 3, 0], track_y=pxy[0][1]+2, gridname=rg_m4m5)
    #     laygen.boundary_pin_from_rect(rout, rg_m4m5, 'CLKO_CAL%d' % (i), layer=laygen.layers['pin'][5],
    #                                   direction='bottom', size=4)
    #     ckd_pin_list = ['CKDSEL1<1>', 'CKDSEL1<0>', 'CKDSEL0<1>', 'CKDSEL0<0>', 'EXTSEL_CLK']
    #     for j in range(len(ckd_pin_list)):
    #         pxy = laygen.get_inst_pin_xy(isarcal_name[i], ckd_pin_list[j], rg_m4m5)
    #         rout = laygen.route(None, laygen.layers['metal'][5], pxy[0], [pxy[0][0], 0], rg_m4m5)
    #         if j < 4:
    #             laygen.boundary_pin_from_rect(rout, rg_m4m5, 'ASCLKD_CAL%d<%d>'%(i, 3-j), layer=laygen.layers['pin'][5],
    #                                       direction='bottom', size=4)
    #         else:
    #             laygen.boundary_pin_from_rect(rout, rg_m4m5, 'EXTSEL_CLK_CAL%d'%(i), layer=laygen.layers['pin'][5],
    #                                       direction='bottom', size=4)
    #     # for pn, p in sar_pins.items():
    #         # if pn.startswith('samp_body'):
    #         #     pxy = laygen.get_inst_pin_xy(isarcal_name[i], pn, rg_m5m6_thick)
    #         #     laygen.pin(pn+str(num_slices+1-i), layer=sar_pins[pn]['layer'], xy=pxy, gridname=rg_m5m6_thick)
    #         # if pn.startswith('bottom_body'):
    #         #     pxy = laygen.get_inst_pin_xy(isarcal_name[i], pn, rg_m3m4)
    #         #     laygen.pin(pn+str(num_slices+1-i), layer=sar_pins[pn]['layer'], xy=pxy, gridname=rg_m3m4, netname='bottom_body%d'%(num_slices+1-i))
    #
    # # CLKDIST pins
    # clkdist_template = laygen.templates.get_template(clkdist_name, clkdist_libname)
    # clkdist_pins = clkdist_template.pins
    # for pn, p in clkdist_pins.items():
    #     if pn.startswith('CLKCAL'):
    #         pxy=laygen.get_inst_pin_xy(iclkdist.name, pn, rg_m2m3_pin)
    #         laygen.pin(pn, layer=clkdist_pins[pn]['layer'], xy=pxy, gridname=rg_m2m3_pin)
    #
    # # Bottom plate body bias pins
    # sar_template = laygen.templates.get_template(sar_name, sar_libname)
    # sar_pins = sar_template.pins
    # y0_m6m7 = laygen.grids.get_absgrid_y(rg_m6m7_thick, size_y)
    # for i in range(num_slices):
    #     for pn, p in sar_pins.items():
    #         if pn.startswith('bottom_body'+str(i)+'_'):
    #             pxy = laygen.get_inst_pin_xy(isar.name, pn, rg_m6m7_thick)
    #             r_m7 = laygen.route(None, laygen.layers['metal'][7], pxy[1], [pxy[1][0], y0_m6m7], rg_m6m7_thick)
    #             laygen.boundary_pin_from_rect(r_m7, rg_m6m7_thick, 'bottom_body'+str(i), laygen.layers['pin'][7], size=6, direction='top')
    # sar_template = laygen.templates.get_template(sar_slice_name, sar_libname)
    # sar_pins = sar_template.pins
    # for i in range(len(isarcal_name)):
    #     for pn, p in sar_pins.items():
    #         if pn.startswith('bottom_body'):
    #             pxy = laygen.get_inst_pin_xy(isarcal_name[i], pn, rg_m6m7_thick)
    #             r_m7 = laygen.route(None, laygen.layers['metal'][7], pxy[1], [pxy[1][0], y0_m6m7], rg_m6m7_thick)
    #             laygen.boundary_pin_from_rect(r_m7, rg_m6m7_thick, 'bottom_body' + str(num_slices+1-i), laygen.layers['pin'][7], size=6,
    #                                       direction='top')
    # # Top plate body bias pins
    # sar_template = laygen.templates.get_template(sar_name, sar_libname)
    # sar_pins = sar_template.pins
    # for i in range(num_slices):
    #     for pn, p in sar_pins.items():
    #         if pn.startswith('samp_body'+str(i)+'_'):
    #             pxy = laygen.get_inst_pin_xy(isar.name, pn, rg_m6m7_thick)
    #             r_m7 = laygen.route(None, laygen.layers['metal'][7], pxy[1]-[1,0], [pxy[1][0]-1, y0_m6m7], rg_m6m7_thick, via0=[0, 0])
    #             laygen.boundary_pin_from_rect(r_m7, rg_m6m7_thick, 'samp_body'+str(i), laygen.layers['pin'][7], size=6, direction='top')
    # sar_template = laygen.templates.get_template(sar_slice_name, sar_libname)
    # sar_pins = sar_template.pins
    # for i in range(len(isarcal_name)):
    #     for pn, p in sar_pins.items():
    #         if pn.startswith('samp_body'):
    #             pxy = laygen.get_inst_pin_xy(isarcal_name[i], pn, rg_m6m7_thick)
    #             r_m7 = laygen.route(None, laygen.layers['metal'][7], pxy[1]-[1,0], [pxy[1][0]-1, y0_m6m7], rg_m6m7_thick, via0=[0, 0])
    #             laygen.boundary_pin_from_rect(r_m7, rg_m6m7_thick, 'samp_body' + str(num_slices + 1 - i),
    #                                           laygen.layers['pin'][7], size=6,
    #                                           direction='top')
    # # VDD/VSS connection for retimer
    # ret_template = laygen.templates.get_template(ret_name, ret_libname)
    # ret_pins = ret_template.pins
    # for pn, p in ret_pins.items():
    #     if pn.startswith('VDD'):
    #         pxy=laygen.get_inst_pin_xy(iret.name, pn, rg_m5m6_thick)
    #         laygen.route(None, laygen.layers['metal'][5], pxy[1], pxy[1]+[0, 10], rg_m5m6_thick)
    #     if pn.startswith('VSS'):
    #         pxy=laygen.get_inst_pin_xy(iret.name, pn, rg_m5m6_thick)
    #         laygen.route(None, laygen.layers['metal'][5], pxy[1], pxy[1]+[0, 10], rg_m5m6_thick)
    #
    # # VDD/VSS rails in M7
    # rvdd_m6_bot=[]
    # rvss_m6_bot=[]
    # rvdd_m6_top=[]
    # rvss_m6_top=[]
    # sar_template = laygen.templates.get_template(sar_name, sar_libname)
    # sar_pins = sar_template.pins
    # x0_m6m7 = laygen.grids.get_absgrid_x(rg_m6m7_thick, size_x)
    # y0_m6m7 = laygen.grids.get_absgrid_y(rg_m6m7_thick, size_y)
    # for pn, p in sar_pins.items():
    #     if pn.startswith('VDDSAR'):
    #         pxy=laygen.get_inst_pin_xy(isar.name, pn, rg_m6m7_thick)
    #         rvdd_m6_bot.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
    #     if pn.startswith('VSSSAR'):
    #         pxy=laygen.get_inst_pin_xy(isar.name, pn, rg_m6m7_thick)
    #         rvss_m6_bot.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
    #     if pn.startswith('VDDSAMP'):
    #         pxy = laygen.get_inst_pin_xy(isar.name, pn, rg_m6m7_thick)
    #         rvdd_m6_top.append(
    #             laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
    #     if pn.startswith('VSSSAMP'):
    #         pxy = laygen.get_inst_pin_xy(isar.name, pn, rg_m6m7_thick)
    #         rvss_m6_top.append(
    #             laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
    # clkdist_template = laygen.templates.get_template(clkdist_name, clkdist_libname)
    # clkdist_pins = clkdist_template.pins
    # for pn, p in clkdist_pins.items():
    #     if pn.startswith('VDD'):
    #         pxy = laygen.get_inst_pin_xy(iclkdist.name, pn, rg_m6m7_thick)
    #         rvdd_m6_top.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
    #     if pn.startswith('VSS'):
    #         pxy = laygen.get_inst_pin_xy(iclkdist.name, pn, rg_m6m7_thick)
    #         rvss_m6_top.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
    # clkcal_template = laygen.templates.get_template(clkcal_name, clkdist_libname)
    # clkcal_pins = clkcal_template.pins
    # for pn, p in clkcal_pins.items():
    #     if pn.startswith('VDD'):
    #         pxy = laygen.get_inst_pin_xy(iclkcal.name, pn, rg_m6m7_thick)
    #         rvdd_m6_top.append(laygen.route(None, laygen.layers['metal'][6], [0, pxy[0][1]], pxy[1], rg_m6m7_thick))
    #     if pn.startswith('VSS'):
    #         pxy = laygen.get_inst_pin_xy(iclkcal.name, pn, rg_m6m7_thick)
    #         rvss_m6_top.append(laygen.route(None, laygen.layers['metal'][6], [0, pxy[0][1]], pxy[1], rg_m6m7_thick))
    #
    # w_size = laygen.get_template_size(sar_slice_name, rg_m6m7_thick, libname=sar_libname)[0]
    # botbody_x = laygen.get_template_pin_xy(sar_slice_name, 'bottom_body_M7_0', rg_m6m7_thick, libname=workinglib)[0][0]
    # # for i in range(2):
    # for i in range(num_slices):
    #     rvdd_m7_0, rvss_m7_0 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M7_0_'+str(i),
    #                                                                        layer=laygen.layers['pin'][7],
    #                                                                        gridname=rg_m6m7_thick,
    #                                                                        netnames=['VDD:', 'VSS:'], direction='y',
    #                                                                        input_rails_rect=[rvdd_m6_bot, rvss_m6_bot],
    #                                                                        generate_pin=True,
    #                                                                        overwrite_start_coord=0,
    #                                                                        overwrite_end_coord=None,
    #                                                                        overwrite_num_routes=None,
    #                                                                        overwrite_start_index=w_size*i,
    #                                                                        overwrite_end_index=w_size*i+botbody_x-2)

    #
    #     rvdd_m7_6, rvss_m7_6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M7_6_'+str(i),
    #                                                                          layer=laygen.layers['pin'][7],
    #                                                                          gridname=rg_m6m7_thick,
    #                                                                          netnames=['VDD:', 'VSS:'], direction='y',
    #                                                                          input_rails_rect=[rvdd_m6_top,
    #                                                                                            rvss_m6_top],
    #                                                                          generate_pin=True,
    #                                                                          overwrite_start_coord=None,
    #                                                                          overwrite_end_coord=y0_m6m7,
    #                                                                          overwrite_num_routes=None,
    #                                                                          overwrite_start_index=w_size * i,
    #                                                                          overwrite_end_index=w_size * i + botbody_x - 2)

    # #
    # # #input pins
    # # #make virtual grids and route on the grids (assuming drc clearance of each block)
    # # rg_m5m6_thick_temp_sig='route_M5_M6_thick_temp_sig'
    # # laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_thick_temp_sig,
    # #                                       instname=isar.name,
    # #                                       inst_pin_prefix=['INP', 'INM'], xy_grid_type='xgrid')
    # # pdict_m5m6_thick_temp_sig = laygen.get_inst_pin_coord(None, None, rg_m5m6_thick_temp_sig)
    # # inp_x_list=[]
    # # inm_x_list=[]
    # # num_input_track=4
    # # in_x0 = pdict_m5m6_thick_temp_sig[isar.name]['INP0'][0][0]
    # # in_x1 = pdict_m5m6_thick_temp_sig[isar.name]['INM0'][0][0]
    # # in_y0 = pdict_m5m6_thick_temp_sig[isar.name]['INP0'][1][1]
    # # in_y1 = in_y0+6
    # # in_y2 = in_y1+2*num_input_track
    # # for i in range(num_slices):
    # #     in_x0 = min(in_x0, pdict_m5m6_thick_temp_sig[isar.name]['INP'+str(i)][0][0])
    # #     in_x1 = max(in_x1, pdict_m5m6_thick_temp_sig[isar.name]['INM'+str(i)][0][0])
    # #     laygen.route(None, laygen.layers['metal'][5],
    # #                  xy0=np.array([pdict_m5m6_thick_temp_sig[isar.name]['INP'+str(i)][0][0], in_y0]),
    # #                  xy1=np.array([pdict_m5m6_thick_temp_sig[isar.name]['INP'+str(i)][0][0], in_y2]),
    # #                  gridname0=rg_m5m6_thick_temp_sig)
    # #     laygen.route(None, laygen.layers['metal'][5],
    # #                  xy0=np.array([pdict_m5m6_thick_temp_sig[isar.name]['INM'+str(i)][0][0], in_y0]),
    # #                  xy1=np.array([pdict_m5m6_thick_temp_sig[isar.name]['INM'+str(i)][0][0], in_y2]),
    # #                  gridname0=rg_m5m6_thick_temp_sig)
    # #     for j in range(num_input_track):
    # #         laygen.via(None,np.array([pdict_m5m6_thick_temp_sig[isar.name]['INP'+str(i)][0][0], in_y1+2*j]), rg_m5m6_thick_temp_sig)
    # #         laygen.via(None,np.array([pdict_m5m6_thick_temp_sig[isar.name]['INM'+str(i)][0][0], in_y1+2*j+1]), rg_m5m6_thick_temp_sig)
    # # #in_x0 -= 2
    # # #in_x1 += 2
    # # rinp=[]
    # # rinm=[]
    # # for i in range(num_input_track):
    # #     rinp.append(laygen.route(None, laygen.layers['metal'][6], xy0=np.array([in_x0, in_y1+2*i]), xy1=np.array([in_x1, in_y1+2*i]), gridname0=rg_m5m6_thick_temp_sig))
    # #     rinm.append(laygen.route(None, laygen.layers['metal'][6], xy0=np.array([in_x0, in_y1+2*i+1]), xy1=np.array([in_x1, in_y1+2*i+1]), gridname0=rg_m5m6_thick_temp_sig))
    # #     laygen.add_pin('INP' + str(i), 'INP', rinp[-1].xy, laygen.layers['pin'][6])
    # #     laygen.add_pin('INM' + str(i), 'INM', rinm[-1].xy, laygen.layers['pin'][6])
    # #

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
        trackm=sizedict['clk_dis_htree']['m_track']

    cellname = 'tisaradc_splash_iq'
    bump_name = 'tisaradc_bumps'
    sar_name = 'tisaradc_splash'
    sar_slice_name = 'sar_wsamp_bb_doubleSA'
    ret_name = 'adc_retimer'
    clkdist_name = 'clk_dis_viadel_htree'
    clkcal_name = 'clk_dis_viadel_cal'
    #tisar_space_name = 'tisaradc_body_space'
    space_1x_name = 'space_1x'
     

    #sar generation
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_tisaradc_splash(laygen, objectname_pfix='TISAR',
                 ret_libname=ret_libname, sar_libname=workinglib, clkdist_libname=clkdist_libname, space_1x_libname=logictemplib,
                 ret_name=ret_name, sar_name=sar_name, clkdist_name=clkdist_name, space_1x_name=space_1x_name,
                 placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5, routing_grid_m4m5_basic_thick=rg_m4m5_basic_thick,
                 routing_grid_m5m6=rg_m5m6,
                 routing_grid_m5m6_thick=rg_m5m6_thick, routing_grid_m5m6_basic_thick=rg_m5m6_basic_thick,
                 routing_grid_m5m6_thick_basic=rg_m5m6_thick_basic, 
                 routing_grid_m6m7_thick=rg_m6m7_thick, routing_grid_m7m8_thick=rg_m7m8_thick,
                 num_bits=num_bits, num_slices=num_slices, clkdist_offset=21.12, trackm=trackm, origin=np.array([0, 0]))
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

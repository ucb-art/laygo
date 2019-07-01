# -*- coding: utf-8 -*-
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

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# noinspection PyUnresolvedReferences,PyCompatibility
from builtins import *

import os
import pkg_resources

from bag.design import Module

yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'tisaradc_body_core.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__tisaradc_body_core(Module):
    """Module for library adc_sar_templates cell tisaradc_body_core.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self,
               sar_lch,
               sar_pw,
               sar_nw,
               sar_sa_m, sar_sa_m_d,
               sar_sa_m_rst, sar_sa_m_rst_d,
               sar_sa_m_rgnn, sar_sa_m_rgnp_d,
               sar_sa_m_buf, doubleSA, sar_sa_m_smallrgnp,
               vref_sf_m_mirror, vref_sf_m_bias, vref_sf_m_off, vref_sf_m_in, vref_sf_m_bias_dum, vref_sf_m_in_dum,
               vref_sf_m_byp, vref_sf_m_byp_bias, vref_sf_bias_current, vref_sf,
               sar_drv_m_list, sar_ckgen_m, sar_ckgen_fo,
               sar_ckgen_ndelay, sar_ckgen_fast, sar_ckgen_muxfast,
               sar_logic_m,
               sar_fsm_m,
               sar_ret_m,
               sar_ret_fo,
               sar_device_intent,
               sar_c_m,
               sar_rdx_array, sar_num_inv_bb,
               samp_lch,
               samp_wp,
               samp_wn,
               samp_fgn,
               samp_fg_inbuf_list,
               samp_fg_outbuf_list,
               samp_nduml,
               samp_ndumr,
               samp_nsep,
               samp_intent,
               num_bits,
               samp_use_laygo, samp_tgate,
               sf_lch, sf_nw, sf_m_mirror, sf_m_bias, sf_m_off, sf_m_in, sf_m_bias_dum, sf_m_in_dum, sf_m_byp,
               sf_m_byp_bias, sf_intent, bias_current, use_sf,
               use_offset, num_slices,
               clk_lch,
               clk_pw,
               clk_nw,
               clk_cdac_bits,
               clk_m_dff,
               clk_m_inv1,
               clk_m_inv2,
               clk_m_tgate,
               clk_n_pd,
               clk_m_capsw,
               clk_unit_cell,
               clk_device_intent,
               clk_pulse,
               ret_lch,
               ret_pw,
               ret_nw,
               ret_m_ibuf,
               ret_m_obuf,
               ret_m_latch,
               ret_m_srbuf,
               ret_m_sr,
               ret_device_intent,
               input_htree,
               ):
        """To be overridden by subclasses to design this module.

        This method should fill in values for all parameters in
        self.parameters.  To design instances of this module, you can
        call their design() method or any other ways you coded.

        To modify schematic structure, call:

        rename_pin()
        delete_instance()
        replace_instance_master()
        reconnect_instance_terminal()
        restore_instance()
        array_instance()
        """
        self.parameters['sar_lch'] = sar_lch
        self.parameters['sar_pw'] = sar_pw
        self.parameters['sar_nw'] = sar_nw
        self.parameters['sar_sa_m'] = sar_sa_m
        self.parameters['sar_sa_m_d'] = sar_sa_m_d
        self.parameters['sar_sa_m_rst'] = sar_sa_m_rst
        self.parameters['sar_sa_m_rst_d'] = sar_sa_m_rst
        self.parameters['sar_sa_m_rgnn'] = sar_sa_m_rgnn
        self.parameters['sar_sa_m_rgnp_d'] = sar_sa_m_rgnp_d
        self.parameters['sar_sa_m_buf'] = sar_sa_m_buf
        self.parameters['doubleSA'] = doubleSA
        self.parameters['sar_sa_m_smallrgnp'] = sar_sa_m_smallrgnp
        self.parameters['vref_sf_m_mirror'] = vref_sf_m_mirror
        self.parameters['vref_sf_m_bias'] = vref_sf_m_bias
        self.parameters['vref_sf_m_in'] = vref_sf_m_in
        self.parameters['vref_sf_m_off'] = vref_sf_m_off
        self.parameters['vref_sf_m_bias_dum'] = vref_sf_m_bias_dum
        self.parameters['vref_sf_m_in_dum'] = vref_sf_m_in_dum
        self.parameters['vref_sf_m_byp'] = vref_sf_m_byp
        self.parameters['vref_sf_m_byp_bias'] = vref_sf_m_byp_bias
        self.parameters['vref_sf_bias_current'] = vref_sf_bias_current
        self.parameters['vref_sf'] = vref_sf
        self.parameters['sar_drv_m_list'] = sar_drv_m_list
        self.parameters['sar_ckgen_m'] = sar_ckgen_m
        self.parameters['sar_ckgen_fo'] = sar_ckgen_fo
        self.parameters['sar_ckgen_ndelay'] = sar_ckgen_ndelay
        self.parameters['sar_ckgen_fast'] = sar_ckgen_fast
        self.parameters['sar_ckgen_muxfast'] = sar_ckgen_muxfast
        self.parameters['sar_logic_m'] = sar_logic_m
        self.parameters['sar_fsm_m'] = sar_fsm_m
        self.parameters['sar_ret_m'] = sar_ret_m
        self.parameters['sar_ret_fo'] = sar_ret_fo
        self.parameters['sar_num_inv_bb'] = sar_num_inv_bb
        self.parameters['sar_device_intent'] = sar_device_intent
        self.parameters['sar_c_m'] = sar_c_m
        self.parameters['sar_rdx_array'] = sar_rdx_array
        self.parameters['samp_lch'] = samp_lch
        self.parameters['samp_wp'] = samp_wp
        self.parameters['samp_wn'] = samp_wn
        self.parameters['samp_fgn'] = samp_fgn
        self.parameters['samp_fg_inbuf_list'] = samp_fg_inbuf_list
        self.parameters['samp_fg_outbuf_list'] = samp_fg_outbuf_list
        self.parameters['samp_nduml'] = samp_nduml
        self.parameters['samp_ndumr'] = samp_ndumr
        self.parameters['samp_nsep'] = samp_nsep
        self.parameters['samp_intent'] = samp_intent
        self.parameters['num_bits'] = num_bits
        self.parameters['samp_tgate'] = samp_tgate
        self.parameters['samp_use_laygo'] = samp_use_laygo  # if true, use laygo for sampler generation
        self.parameters['sf_lch'] = sf_lch
        self.parameters['sf_nw'] = sf_nw
        self.parameters['sf_m_mirror'] = sf_m_mirror
        self.parameters['sf_m_bias'] = sf_m_bias
        self.parameters['sf_m_in'] = sf_m_in
        self.parameters['sf_m_off'] = sf_m_off
        self.parameters['sf_m_bias_dum'] = sf_m_bias_dum
        self.parameters['sf_m_in_dum'] = sf_m_in_dum
        self.parameters['sf_m_byp'] = sf_m_byp
        self.parameters['sf_m_byp_bias'] = sf_m_byp_bias
        self.parameters['sf_intent'] = sf_intent
        self.parameters['bias_current'] = bias_current
        self.parameters['use_sf'] = use_sf  # if true, source follower is used before the sampler
        self.parameters['use_offset'] = use_offset
        self.parameters['num_slices'] = num_slices
        self.parameters['clk_lch'] = clk_lch
        self.parameters['clk_pw'] = clk_pw
        self.parameters['clk_nw'] = clk_nw
        self.parameters['clk_cdac_bits'] = clk_cdac_bits
        self.parameters['clk_m_dff'] = clk_m_dff
        self.parameters['clk_m_inv1'] = clk_m_inv1
        self.parameters['clk_m_inv2'] = clk_m_inv2
        self.parameters['clk_m_tgate'] = clk_m_tgate
        self.parameters['clk_n_pd'] = clk_n_pd
        self.parameters['clk_m_capsw'] = clk_m_capsw
        self.parameters['clk_unit_cell'] = clk_unit_cell
        self.parameters['clk_device_intent'] = clk_device_intent
        self.parameters['ret_lch'] = ret_lch
        self.parameters['ret_pw'] = ret_pw
        self.parameters['ret_nw'] = ret_nw
        self.parameters['ret_m_ibuf'] = ret_m_ibuf
        self.parameters['ret_m_obuf'] = ret_m_obuf
        self.parameters['ret_m_latch'] = ret_m_latch
        self.parameters['ret_device_intent'] = ret_device_intent
        self.parameters['input_htree'] = input_htree

        # sar_wsamp_array generation
        if input_htree == False:
            if use_sf is True:
                term_list = [{
                    ','.join(['INP%d' % (i) for i in range(num_slices)]): 'INP',
                    ','.join(['INM%d' % (i) for i in range(num_slices)]): 'INM',
                    ','.join(['CLK%d' % (i) for i in range(num_slices)]):
                        ','.join(['ICLK%d' % (i) for i in range(num_slices)]),
                    ','.join(['OSP%d' % (i) for i in range(num_slices)]):
                        ','.join(['OSP%d' % (i) for i in range(num_slices)]),
                    ','.join(['OSM%d' % (i) for i in range(num_slices)]):
                        ','.join(['OSM%d' % (i) for i in range(num_slices)]),
                    ','.join(['ASCLKD%d<3:0>' % (i) for i in range(num_slices)]):
                        ','.join(['ASCLKD%d<3:0>' % (i) for i in range(num_slices)]),
                    ','.join(['EXTSEL_CLK%d' % (i) for i in range(num_slices)]):
                        ','.join(['EXTSEL_CLK%d' % (i) for i in range(num_slices)]),
                    ','.join(['MODESEL%d' % (i) for i in range(num_slices)]):
                        ','.join(['MODESEL%d' % (i) for i in range(num_slices)]),
                    ','.join(['ADCOUT%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]):
                        ','.join(['ADCO%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]),
                    ','.join(['CLKO%d' % (i) for i in range(num_slices)]):
                        ','.join(['CLKO%d' % (i) for i in range(num_slices)]),
                    ','.join(['SF_BIAS%d' % (i) for i in range(num_slices)]):
                        ','.join(['SF_BIAS%d' % (i) for i in range(num_slices)]),
                    ','.join(['SF_Voffn%d' % (i) for i in range(num_slices)]):
                        ','.join(['SF_Voffn%d' % (i) for i in range(num_slices)]),
                    ','.join(['SF_Voffp%d' % (i) for i in range(num_slices)]):
                        ','.join(['SF_Voffp%d' % (i) for i in range(num_slices)]),
                    ','.join(['VREF_SF_BIAS%d' % (i) for i in range(num_slices)]):
                        ','.join(['VREF_SF_BIAS%d' % (i) for i in range(num_slices)]),
                }]
            else:
                term_list = [{
                    ','.join(['INP%d' % (i) for i in range(num_slices)]): 'INP',
                    ','.join(['INM%d' % (i) for i in range(num_slices)]): 'INM',
                    ','.join(['CLK%d' % (i) for i in range(num_slices)]):
                        ','.join(['ICLK%d' % (i) for i in range(num_slices)]),
                    ','.join(['OSP%d' % (i) for i in range(num_slices)]):
                        ','.join(['OSP%d' % (i) for i in range(num_slices)]),
                    ','.join(['OSM%d' % (i) for i in range(num_slices)]):
                        ','.join(['OSM%d' % (i) for i in range(num_slices)]),
                    ','.join(['ASCLKD%d<3:0>' % (i) for i in range(num_slices)]):
                        ','.join(['ASCLKD%d<3:0>' % (i) for i in range(num_slices)]),
                    ','.join(['EXTSEL_CLK%d' % (i) for i in range(num_slices)]):
                        ','.join(['EXTSEL_CLK%d' % (i) for i in range(num_slices)]),
                    ','.join(['MODESEL%d' % (i) for i in range(num_slices)]):
                        ','.join(['MODESEL%d' % (i) for i in range(num_slices)]),
                    ','.join(['ADCOUT%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]):
                        ','.join(['ADCO%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]),
                    ','.join(['CLKO%d' % (i) for i in range(num_slices)]):
                        ','.join(['CLKO%d' % (i) for i in range(num_slices)]),
                }]
        else:
            if use_sf is True:
                term_list = [{
                    ','.join(['INP%d' % (i) for i in range(num_slices)]): ','.join(
                        ['INP%d' % (i) for i in range(num_slices)]),
                    ','.join(['INM%d' % (i) for i in range(num_slices)]): ','.join(
                        ['INM%d' % (i) for i in range(num_slices)]),
                    ','.join(['CLK%d' % (i) for i in range(num_slices)]):
                        ','.join(['ICLK%d' % (i) for i in range(num_slices)]),
                    ','.join(['OSP%d' % (i) for i in range(num_slices)]):
                        ','.join(['OSP%d' % (i) for i in range(num_slices)]),
                    ','.join(['OSM%d' % (i) for i in range(num_slices)]):
                        ','.join(['OSM%d' % (i) for i in range(num_slices)]),
                    ','.join(['ASCLKD%d<3:0>' % (i) for i in range(num_slices)]):
                        ','.join(['ASCLKD%d<3:0>' % (i) for i in range(num_slices)]),
                    ','.join(['EXTSEL_CLK%d' % (i) for i in range(num_slices)]):
                        ','.join(['EXTSEL_CLK%d' % (i) for i in range(num_slices)]),
                    ','.join(['MODESEL%d' % (i) for i in range(num_slices)]):
                        ','.join(['MODESEL%d' % (i) for i in range(num_slices)]),
                    ','.join(['ADCOUT%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]):
                        ','.join(['ADCO%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]),
                    ','.join(['CLKO%d' % (i) for i in range(num_slices)]):
                        ','.join(['CLKO%d' % (i) for i in range(num_slices)]),
                    ','.join(['SF_BIAS%d' % (i) for i in range(num_slices)]):
                        ','.join(['SF_BIAS%d' % (i) for i in range(num_slices)]),
                    ','.join(['SF_Voffn%d' % (i) for i in range(num_slices)]):
                        ','.join(['SF_Voffn%d' % (i) for i in range(num_slices)]),
                    ','.join(['SF_Voffp%d' % (i) for i in range(num_slices)]):
                        ','.join(['SF_Voffp%d' % (i) for i in range(num_slices)]),
                    ','.join(['VREF_SF_BIAS%d' % (i) for i in range(num_slices)]):
                        ','.join(['VREF_SF_BIAS%d' % (i) for i in range(num_slices)]),
                }]
            else:
                term_list = [{
                    ','.join(['INP%d' % (i) for i in range(num_slices)]): ','.join(
                        ['INP%d' % (i) for i in range(num_slices)]),
                    ','.join(['INM%d' % (i) for i in range(num_slices)]): ','.join(
                        ['INM%d' % (i) for i in range(num_slices)]),
                    ','.join(['CLK%d' % (i) for i in range(num_slices)]):
                        ','.join(['ICLK%d' % (i) for i in range(num_slices)]),
                    ','.join(['OSP%d' % (i) for i in range(num_slices)]):
                        ','.join(['OSP%d' % (i) for i in range(num_slices)]),
                    ','.join(['OSM%d' % (i) for i in range(num_slices)]):
                        ','.join(['OSM%d' % (i) for i in range(num_slices)]),
                    ','.join(['ASCLKD%d<3:0>' % (i) for i in range(num_slices)]):
                        ','.join(['ASCLKD%d<3:0>' % (i) for i in range(num_slices)]),
                    ','.join(['EXTSEL_CLK%d' % (i) for i in range(num_slices)]):
                        ','.join(['EXTSEL_CLK%d' % (i) for i in range(num_slices)]),
                    ','.join(['MODESEL%d' % (i) for i in range(num_slices)]):
                        ','.join(['MODESEL%d' % (i) for i in range(num_slices)]),
                    ','.join(['ADCOUT%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]):
                        ','.join(['ADCO%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]),
                    ','.join(['CLKO%d' % (i) for i in range(num_slices)]):
                        ','.join(['CLKO%d' % (i) for i in range(num_slices)]),
                }]
        # else:
        #     term_list=[{
        #         ','.join(['INP%d'%(i) for i in range(num_slices)]): 'INP',
        #         ','.join(['INM%d'%(i) for i in range(num_slices)]): 'INM',
        #         ','.join(['CLK%d'%(i) for i in range(num_slices)]): 'DATAO<0:%d>'%(num_slices-1),
        #         ','.join(['OSP%d'%(i) for i in range(num_slices)]):
        #             ','.join(['OSP%d'%(i) for i in range(num_slices)]),
        #         ','.join(['OSM%d'%(i) for i in range(num_slices)]):
        #             ','.join(['OSM%d'%(i) for i in range(num_slices)]),
        #         ','.join(['ASCLKD%d<3:0>'%(i) for i in range(num_slices)]):
        #             ','.join(['ASCLKD%d<3:0>'%(i) for i in range(num_slices)]),
        #         ','.join(['EXTSEL_CLK%d'%(i) for i in range(num_slices)]):
        #             ','.join(['EXTSEL_CLK%d'%(i) for i in range(num_slices)]),
        #         ','.join(['ADCOUT%d<%d:0>'%(i, num_bits-1) for i in range(num_slices)]):
        #             ','.join(['ADCO%d<%d:0>'%(i, num_bits-1) for i in range(num_slices)]),
        #         ','.join(['CLKO%d'%(i) for i in range(num_slices)]):
        #             ','.join(['CLKO%d'%(i) for i in range(num_slices)]),
        #     }]
        name_list = (['ISAR0'])
        self.array_instance('ISAR0', name_list, term_list=term_list)
        self.instances['ISAR0'][0].design(
            sar_lch, sar_pw, sar_nw, sar_sa_m, sar_sa_m_d, sar_sa_m_rst, sar_sa_m_rst_d,
            sar_sa_m_rgnn, sar_sa_m_rgnp_d, sar_sa_m_buf, doubleSA, sar_sa_m_smallrgnp,
            vref_sf_m_mirror, vref_sf_m_bias, vref_sf_m_off, vref_sf_m_in, vref_sf_m_bias_dum, vref_sf_m_in_dum,
            vref_sf_m_byp, vref_sf_m_byp_bias, vref_sf_bias_current, vref_sf,
            sar_drv_m_list, sar_ckgen_m, sar_ckgen_fo, sar_ckgen_ndelay, sar_ckgen_fast, sar_ckgen_muxfast,
            sar_logic_m, sar_fsm_m, sar_ret_m, sar_ret_fo, sar_num_inv_bb,
            sar_device_intent, sar_c_m, sar_rdx_array,
            samp_lch, samp_wp, samp_wn, samp_fgn, samp_fg_inbuf_list, samp_fg_outbuf_list,
            samp_nduml, samp_ndumr, samp_nsep, samp_intent, samp_tgate, num_bits, samp_use_laygo, use_offset,
            sf_lch, sf_nw, sf_m_mirror, sf_m_bias, sf_m_off, sf_m_in, sf_m_bias_dum, sf_m_in_dum, sf_m_byp,
            sf_m_byp_bias, sf_intent, bias_current, use_sf,
            num_slices
        )

        # clock generation
        term_list = [{
            ','.join(['CLKCAL%d<%d:0>' % (i, clk_cdac_bits - 1) for i in range(num_slices)]): ','.join(
                ['CLKCAL%d<%d:0>' % (i, clk_cdac_bits - 1) for i in range(num_slices)]),
            'CLKO<%d:0>' % (num_slices - 1): ','.join(['ICLK%d' % (num_slices - 1 - i) for i in range(num_slices)]),
            'DATAO<%d:0>' % (num_slices - 1): 'DATAO<%d:0>' % (num_slices - 1)
        }]
        name_list = (['ICLKDIS0'])
        self.array_instance('ICLKDIS0', name_list, term_list=term_list)
        self.instances['ICLKDIS0'][0].design(
            lch=clk_lch,
            pw=clk_pw,
            nw=clk_nw,
            m_dff=clk_m_dff,
            m_inv1=clk_m_inv1,
            m_inv2=clk_m_inv2,
            m_tgate=clk_m_tgate,
            n_pd=clk_n_pd,
            m_capsw=clk_m_capsw,
            num_bits=clk_cdac_bits,
            num_ways=num_slices,
            unit_cell=clk_unit_cell,
            clock_pulse=clk_pulse,
            device_intent=clk_device_intent,
        )

        # retimer generation
        # clk_bar phases
        # rules:
        # 1) last stage latches: num_slices-1
        # 2) second last stage latches: int(num_slices/2)-1
        # 3) the first half of first stage latches: int((int(num_slices/2)+1)%num_slices)
        # 4) the second half of first stage latches: 1
        # 5) the output phase = the second last latch phase
        if num_slices > 4:
            ck_phase_2 = num_slices - 1
            ck_phase_1 = int(num_slices / 2) - 1
            ck_phase_0_0 = int((int(num_slices / 2) + 1) % num_slices)
            ck_phase_0_1 = 1
        elif num_slices == 4:
            ck_phase_2 = 0
            ck_phase_1 = 2
            ck_phase_0_0 = 3
            ck_phase_0_1 = 1
        ck_phase_out = ck_phase_1
        ck_phase_buf = sorted(set([ck_phase_2, ck_phase_1, ck_phase_0_0, ck_phase_0_1]))

        term_list = [{
            ','.join(['in_%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]):
                ','.join(['ADCO%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]),
            ','.join(['out_%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]):
                ','.join(['ADCOUT%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]),
            ','.join(['clk%d' % (i) for i in ck_phase_buf]):
                ','.join(['CLKO%d' % (i) for i in ck_phase_buf]),
        }]
        name_list = (['IRET0'])
        self.array_instance('IRET0', name_list, term_list=term_list)
        self.instances['IRET0'][0].design(
            lch=ret_lch,
            pw=ret_pw,
            nw=ret_nw,
            m_ibuf=ret_m_ibuf,
            m_obuf=ret_m_obuf,
            m_latch=ret_m_latch,
            m_srbuf=ret_m_srbuf,
            m_sr=ret_m_sr,
            num_slices=num_slices,
            num_bits=num_bits,
            device_intent=ret_device_intent,
        )
        self.rename_pin('CLKCAL', ','.join(['CLKCAL%d<4:0>' % i for i in range(num_slices)]))
        self.rename_pin('OSP', ','.join(['OSP%d' % (i) for i in range(num_slices)]))
        self.rename_pin('OSM', ','.join(['OSM%d' % (i) for i in range(num_slices)]))
        self.rename_pin('ASCLKD<3:0>', ','.join(['ASCLKD%d<3:0>' % (i) for i in range(num_slices)]))
        self.rename_pin('EXTSEL_CLK', ','.join(['EXTSEL_CLK%d' % (i) for i in range(num_slices)]))
        self.rename_pin('ADCOUT', ','.join(['ADCOUT%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]))
        self.rename_pin('SF_Voffp0', ','.join(['SF_Voffp%d' % (i) for i in range(num_slices)]))
        self.rename_pin('SF_Voffn0', ','.join(['SF_Voffn%d' % (i) for i in range(num_slices)]))
        self.rename_pin('SF_BIAS', ','.join(['SF_BIAS%d' % (i) for i in range(num_slices)]))
        self.rename_pin('VREF_SF_BIAS', ','.join(['VREF_SF_BIAS%d' % (i) for i in range(num_slices)]))
        if sar_ckgen_muxfast == True:
            self.rename_pin('MODESEL', ','.join(['MODESEL%d' % (i) for i in range(num_slices)]))
        else:
            self.remove_pin('MODESEL')

        if use_offset == False:
            self.remove_pin(','.join(['OSP%d' % (i) for i in range(num_slices)]))
            self.remove_pin(','.join(['OSM%d' % (i) for i in range(num_slices)]))
        if vref_sf == False:
            self.remove_pin('VREF_SF_bypass')
            self.remove_pin(','.join(['VREF_SF_BIAS%d' % (i) for i in range(num_slices)]))
        if use_sf == False:
            self.remove_pin('SF_bypass')
            self.remove_pin(','.join(['SF_BIAS%d' % (i) for i in range(num_slices)]))
            self.remove_pin(','.join(['SF_Voffp%d' % (i) for i in range(num_slices)]))
            self.remove_pin(','.join(['SF_Voffn%d' % (i) for i in range(num_slices)]))
        if input_htree == True:
            self.rename_pin('INP', ','.join(['INP%d' % (i) for i in range(num_slices)]))
            self.rename_pin('INM', ','.join(['INM%d' % (i) for i in range(num_slices)]))

            # #rename pins
            # if use_offset == True:
            #     pin_enum=[','.join(['SF_Voffp%d'%(i) for i in range(num_slices)]),
            #               ','.join(['SF_Voffn%d' % (i) for i in range(num_slices)]),
            #               ','.join(['SF_BIAS%d' % (i) for i in range(num_slices)]),
            #               ','.join(['VREF_SF_BIAS%d' % (i) for i in range(num_slices)])
            #               ]
            #     if vref_sf == False:
            #         pin_enum.remove('VREF_SF_bypass')
            #         self.remove_pin('VREF_SF_bypass')
            #         pin_enum.remove(','.join(['VREF_SF_BIAS%d' % (i) for i in range(num_slices)]))
            #         self.remove_pin(','.join(['VREF_SF_BIAS%d' % (i) for i in range(num_slices)]))
            # else:
            #     pin_enum=[','.join(['SF_Voffp%d'%(i) for i in range(num_slices)]),
            #               ','.join(['SF_Voffn%d' % (i) for i in range(num_slices)]),
            #               ','.join(['SF_BIAS%d' % (i) for i in range(num_slices)]),
            #               ','.join(['VREF_SF_BIAS%d' % (i) for i in range(num_slices)])
            #               ]
            #     if vref_sf == False:
            #         pin_enum.remove('VREF_SF_bypass')
            #         self.remove_pin('VREF_SF_bypass')
            #         pin_enum.remove(','.join(['VREF_SF_BIAS%d' % (i) for i in range(num_slices)]))
            #         self.remove_pin(','.join(['VREF_SF_BIAS%d' % (i) for i in range(num_slices)]))
            #     self.remove_pin(','.join(['OSP%d'%(i) for i in range(num_slices)]))
            #     self.remove_pin(','.join(['OSM%d'%(i) for i in range(num_slices)]))
            # for pn in pin_enum:
            #     pn_new=''
            #     for i in range(num_slices):
            #         pn_new=pn_new+pn+str(i)+','
            #     pn_new=pn_new[:-1] #remove the last comma
            #     self.rename_pin(pn+'0', pn_new)

    def get_layout_params(self, **kwargs):
        """Returns a dictionary with layout parameters.

        This method computes the layout parameters used to generate implementation's
        layout.  Subclasses should override this method if you need to run post-extraction
        layout.

        Parameters
        ----------
        kwargs :
            any extra parameters you need to generate the layout parameters dictionary.
            Usually you specify layout-specific parameters here, like metal layers of
            input/output, customizable wire sizes, and so on.

        Returns
        -------
        params : dict[str, any]
            the layout parameters dictionary.
        """
        return {}

    def get_layout_pin_mapping(self):
        """Returns the layout pin mapping dictionary.

        This method returns a dictionary used to rename the layout pins, in case they are different
        than the schematic pins.

        Returns
        -------
        pin_mapping : dict[str, str]
            a dictionary from layout pin names to schematic pin names.
        """
        return {}

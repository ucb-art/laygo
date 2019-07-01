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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'tisaradc_splash_iq.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__tisaradc_splash_iq(Module):
    """Module for library adc_sar_templates cell tisaradc_splash_iq.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, 
            sar_lch, 
            sar_pw, 
            sar_nw, 
            sar_sa_m, 
            sar_sa_m_d, 
            sar_sa_m_rst, 
            sar_sa_m_rst_d, 
            sar_sa_m_rgnn, 
            sar_sa_m_rgnp_d, 
            sar_sa_m_buf,
            doubleSA,
            vref_sf_m_mirror, vref_sf_m_bias, vref_sf_m_off, vref_sf_m_in, vref_sf_m_bias_dum, vref_sf_m_in_dum,
            vref_sf_m_byp, vref_sf_m_byp_bias, vref_sf_bias_current, vref_sf,
            sar_drv_m_list,sar_ckgen_m,sar_ckgen_fo,
            sar_ckgen_ndelay,
            sar_ckgen_fast, sar_ckgen_fastest,
            sar_logic_m,
            sar_fsm_m,
            sar_ret_m,
            sar_ret_fo,
            sar_device_intent,
            sar_c_m,
            sar_rdx_array,
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
            num_inv_bb,
            samp_use_laygo,
               sf_lch, sf_nw, sf_m_mirror, sf_m_bias, sf_m_off, sf_m_in, sf_m_bias_dum, sf_m_in_dum, sf_m_byp,
               sf_m_byp_bias, sf_intent, bias_current, use_sf,
               use_offset,
            num_slices,
            clk_lch,
            clk_pw,
            clk_nw,
            clk_m_dff,
            clk_m_inv1,
            clk_m_inv2,
            clk_m_tgate,
            clk_n_pd,
            clk_m_capsw,
            clk_unit_cell,
            clk_clock_pulse,
            clk_device_intent,
            clkcal_order,
            ret_lch,
            ret_pw,
            ret_nw,
            ret_m_ibuf,
            ret_m_obuf,
            ret_m_latch,
            ret_m_srbuf,
            ret_m_sr,
            ret_device_intent,
               rdac_lch, rdac_pw, rdac_nw, rdac_m, rdac_num_series, rdac_num_bits, rdac_num_dacs, rdac_device_intent
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
        self.parameters['sar_sa_m_rst_d'] = sar_sa_m_rst_d
        self.parameters['sar_sa_m_rgnn'] = sar_sa_m_rgnn
        self.parameters['sar_sa_m_rgnp_d'] = sar_sa_m_rgnp_d
        self.parameters['sar_sa_m_buf'] = sar_sa_m_buf
        self.parameters['doubleSA'] = doubleSA
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
        self.parameters['sar_ckgen_fastest'] = sar_ckgen_fastest
        self.parameters['sar_logic_m'] = sar_logic_m
        self.parameters['sar_fsm_m'] = sar_fsm_m
        self.parameters['sar_ret_m'] = sar_ret_m
        self.parameters['sar_ret_fo'] = sar_ret_fo
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
        self.parameters['num_inv_bb'] = num_inv_bb
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
        self.parameters['clk_m_dff'] = clk_m_dff
        self.parameters['clk_m_inv1'] = clk_m_inv1
        self.parameters['clk_m_inv2'] = clk_m_inv2
        self.parameters['clk_m_tgate'] = clk_m_tgate
        self.parameters['clk_n_pd'] = clk_n_pd
        self.parameters['clk_m_capsw'] = clk_m_capsw
        self.parameters['clk_unit_cell'] = clk_unit_cell
        self.parameters['clk_clock_pulse'] = clk_clock_pulse
        self.parameters['clk_device_intent'] = clk_device_intent
        self.parameters['clkcal_order'] = clkcal_order
        self.parameters['ret_lch'] = ret_lch
        self.parameters['ret_pw'] = ret_pw
        self.parameters['ret_nw'] = ret_nw
        self.parameters['ret_m_ibuf'] = ret_m_ibuf
        self.parameters['ret_m_obuf'] = ret_m_obuf
        self.parameters['ret_m_latch'] = ret_m_latch
        self.parameters['ret_m_srbuf'] = ret_m_srbuf
        self.parameters['ret_m_sr'] = ret_m_sr
        self.parameters['ret_device_intent'] = ret_device_intent
        self.parameters['rdac_lch'] = rdac_lch
        self.parameters['rdac_pw'] = rdac_pw
        self.parameters['rdac_nw'] = rdac_nw
        self.parameters['rdac_m'] = rdac_m
        self.parameters['rdac_num_series'] = rdac_num_series
        self.parameters['rdac_num_bits'] = rdac_num_bits
        self.parameters['rdac_num_dacs'] = rdac_num_dacs
        self.parameters['rdac_device_intent'] = rdac_device_intent

        term_list = [{
            ','.join(['ASCLKD%d<3:0>' % (i) for i in range(num_slices)]):
                ','.join(['I_ASCLKD%d<3:0>' % (i) for i in range(num_slices)]),
            ','.join(['EXTSEL_CLK%d' % (i) for i in range(num_slices)]):
                ','.join(['I_EXTSEL_CLK%d' % (i) for i in range(num_slices)]),
            ','.join(['ADCOUT_RET%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]):
                ','.join(['I_ADCOUT_RET%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]),
            ','.join(['ADCO%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]):
                ','.join(['I_ADCO%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]),
            ','.join(['CLKO%d' % (i) for i in range(num_slices)]):
                ','.join(['I_CLKO%d' % (i) for i in range(num_slices)]),
            ','.join(['samp_body%d' % (i) for i in range(num_slices+2)]):
                ','.join(['I_samp_body%d' % (i) for i in range(num_slices+2)]),
            ','.join(['bottom_body%d' % (i) for i in range(num_slices+2)]):
                ','.join(['I_bottom_body%d' % (i) for i in range(num_slices+2)]),
            'ADCO_CAL0<%d:0>'%(num_bits-1): 'I_ADCO_CAL0<%d:0>'%(num_bits-1),
            'ADCO_CAL1<%d:0>'%(num_bits - 1): 'I_ADCO_CAL1<%d:0>'%(num_bits - 1),
            ','.join(['CLKCAL%d<4:0>' % i for i in range(num_slices)]):
                ','.join(['I_CLKCAL%d<4:0>' % i for i in range(num_slices)]),
            'RDAC_SEL<%d:0>'%(rdac_num_dacs*rdac_num_bits-1): 'I_RDAC_SEL<%d:0>'%(rdac_num_dacs*rdac_num_bits-1),
        }]
        name_list = (['ADCI'])
        self.array_instance('ADCI', name_list, term_list=term_list)
        self.instances['ADCI'][0].design(
            sar_lch,
            sar_pw,
            sar_nw,
            sar_sa_m,
            sar_sa_m_d,
            sar_sa_m_rst,
            sar_sa_m_rst_d,
            sar_sa_m_rgnn,
            sar_sa_m_rgnp_d,
            sar_sa_m_buf,
            doubleSA,
            vref_sf_m_mirror, vref_sf_m_bias, vref_sf_m_off, vref_sf_m_in, vref_sf_m_bias_dum, vref_sf_m_in_dum,
            vref_sf_m_byp, vref_sf_m_byp_bias, vref_sf_bias_current, vref_sf,
            sar_drv_m_list, sar_ckgen_m, sar_ckgen_fo,
            sar_ckgen_ndelay,
            sar_ckgen_fast, sar_ckgen_fastest,
            sar_logic_m,
            sar_fsm_m,
            sar_ret_m,
            sar_ret_fo,
            sar_device_intent,
            sar_c_m,
            sar_rdx_array,
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
            num_inv_bb,
            samp_use_laygo,
            sf_lch, sf_nw, sf_m_mirror, sf_m_bias, sf_m_off, sf_m_in, sf_m_bias_dum, sf_m_in_dum, sf_m_byp,
            sf_m_byp_bias, sf_intent, bias_current, use_sf,
            use_offset,
            num_slices,
            clk_lch,
            clk_pw,
            clk_nw,
            clk_m_dff,
            clk_m_inv1,
            clk_m_inv2,
            clk_m_tgate,
            clk_n_pd,
            clk_m_capsw,
            clk_unit_cell,
            clk_clock_pulse,
            clk_device_intent,
            clkcal_order,
            ret_lch,
            ret_pw,
            ret_nw,
            ret_m_ibuf,
            ret_m_obuf,
            ret_m_latch,
            ret_m_srbuf,
            ret_m_sr,
            ret_device_intent,
            rdac_lch, rdac_pw, rdac_nw, rdac_m, rdac_num_series, rdac_num_bits, rdac_num_dacs, rdac_device_intent,
        )

        term_list = [{
            ','.join(['ASCLKD%d<3:0>' % (i) for i in range(num_slices)]):
                ','.join(['Q_ASCLKD%d<3:0>' % (i) for i in range(num_slices)]),
            ','.join(['EXTSEL_CLK%d' % (i) for i in range(num_slices)]):
                ','.join(['Q_EXTSEL_CLK%d' % (i) for i in range(num_slices)]),
            ','.join(['ADCOUT_RET%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]):
                ','.join(['Q_ADCOUT_RET%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]),
            ','.join(['ADCO%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]):
                ','.join(['Q_ADCO%d<%d:0>' % (i, num_bits - 1) for i in range(num_slices)]),
            ','.join(['CLKO%d' % (i) for i in range(num_slices)]):
                ','.join(['Q_CLKO%d' % (i) for i in range(num_slices)]),
            ','.join(['samp_body%d' % (i) for i in range(num_slices+2)]):
                ','.join(['Q_samp_body%d' % (i) for i in range(num_slices+2)]),
            ','.join(['bottom_body%d' % (i) for i in range(num_slices+2)]):
                ','.join(['Q_bottom_body%d' % (i) for i in range(num_slices+2)]),
            'ADCO_CAL0<%d:0>'%(num_bits - 1): 'Q_ADCO_CAL0<%d:0>'%(num_bits-1),
            'ADCO_CAL1<%d:0>'%(num_bits - 1): 'Q_ADCO_CAL1<%d:0>'%(num_bits - 1),
            ','.join(['CLKCAL%d<4:0>' % i for i in range(num_slices)]):
                ','.join(['Q_CLKCAL%d<4:0>' % i for i in range(num_slices)]),
            'RDAC_SEL<%d:0>' % (rdac_num_dacs * rdac_num_bits - 1): 'Q_RDAC_SEL<%d:0>' % (
            rdac_num_dacs * rdac_num_bits - 1),
        }]
        name_list = (['ADCQ'])
        self.array_instance('ADCQ', name_list, term_list=term_list)
        self.instances['ADCQ'][0].design(
            sar_lch,
            sar_pw,
            sar_nw,
            sar_sa_m,
            sar_sa_m_d,
            sar_sa_m_rst,
            sar_sa_m_rst_d,
            sar_sa_m_rgnn,
            sar_sa_m_rgnp_d,
            sar_sa_m_buf,
            doubleSA,
            vref_sf_m_mirror, vref_sf_m_bias, vref_sf_m_off, vref_sf_m_in, vref_sf_m_bias_dum, vref_sf_m_in_dum,
            vref_sf_m_byp, vref_sf_m_byp_bias, vref_sf_bias_current, vref_sf,
            sar_drv_m_list, sar_ckgen_m, sar_ckgen_fo,
            sar_ckgen_ndelay,
            sar_ckgen_fast, sar_ckgen_fastest,
            sar_logic_m,
            sar_fsm_m,
            sar_ret_m,
            sar_ret_fo,
            sar_device_intent,
            sar_c_m,
            sar_rdx_array,
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
            num_inv_bb,
            samp_use_laygo,
            sf_lch, sf_nw, sf_m_mirror, sf_m_bias, sf_m_off, sf_m_in, sf_m_bias_dum, sf_m_in_dum, sf_m_byp,
            sf_m_byp_bias, sf_intent, bias_current, use_sf,
            use_offset,
            num_slices,
            clk_lch,
            clk_pw,
            clk_nw,
            clk_m_dff,
            clk_m_inv1,
            clk_m_inv2,
            clk_m_tgate,
            clk_n_pd,
            clk_m_capsw,
            clk_unit_cell,
            clk_clock_pulse,
            clk_device_intent,
            clkcal_order,
            ret_lch,
            ret_pw,
            ret_nw,
            ret_m_ibuf,
            ret_m_obuf,
            ret_m_latch,
            ret_m_srbuf,
            ret_m_sr,
            ret_device_intent,
            rdac_lch, rdac_pw, rdac_nw, rdac_m, rdac_num_series, rdac_num_bits, rdac_num_dacs, rdac_device_intent,
        )

        self.rename_pin('I_CLKCAL', ','.join(['I_CLKCAL%d<4:0>'%i for i in range(num_slices)]))
        self.rename_pin('I_OSP', ','.join(['I_OSP%d'%(i) for i in range(num_slices)]))
        self.rename_pin('I_OSM', ','.join(['I_OSM%d'%(i) for i in range(num_slices)]))
        self.rename_pin('I_ASCLKD<3:0>', ','.join(['I_ASCLKD%d<3:0>'%(i) for i in range(num_slices)]))
        self.rename_pin('I_EXTSEL_CLK', ','.join(['I_EXTSEL_CLK%d'%(i) for i in range(num_slices)]))
        self.rename_pin('I_ADCOUT_RET', ','.join(['I_ADCOUT_RET%d<%d:0>'%(i, num_bits-1) for i in range(num_slices)]))
        self.rename_pin('I_ADCO', ','.join(['I_ADCO%d<%d:0>'%(i, num_bits-1) for i in range(num_slices)]))
        self.rename_pin('I_CLKO', ','.join(['I_CLKO%d'%(i) for i in range(num_slices)]))
        self.rename_pin('I_ADCO_CAL0', 'I_ADCO_CAL0<%d:0>'%(num_bits-1))
        self.rename_pin('I_ADCO_CAL1', 'I_ADCO_CAL1<%d:0>'%(num_bits-1))
        self.rename_pin('I_samp_body', ','.join(['I_samp_body%d'%(i) for i in range(num_slices+2)]))
        self.rename_pin('I_bottom_body', ','.join(['I_bottom_body%d'%(i) for i in range(num_slices+2)]))
        self.rename_pin('I_RDAC_SEL', 'I_RDAC_SEL<%d:0>'%(rdac_num_dacs*rdac_num_bits-1))

        self.rename_pin('Q_CLKCAL', ','.join(['Q_CLKCAL%d<4:0>'%i for i in range(num_slices)]))
        self.rename_pin('Q_OSP', ','.join(['Q_OSP%d'%(i) for i in range(num_slices)]))
        self.rename_pin('Q_OSM', ','.join(['Q_OSM%d'%(i) for i in range(num_slices)]))
        self.rename_pin('Q_ASCLKD<3:0>', ','.join(['Q_ASCLKD%d<3:0>'%(i) for i in range(num_slices)]))
        self.rename_pin('Q_EXTSEL_CLK', ','.join(['Q_EXTSEL_CLK%d'%(i) for i in range(num_slices)]))
        self.rename_pin('Q_ADCOUT_RET', ','.join(['Q_ADCOUT_RET%d<%d:0>'%(i, num_bits-1) for i in range(num_slices)]))
        self.rename_pin('Q_ADCO', ','.join(['Q_ADCO%d<%d:0>'%(i, num_bits-1) for i in range(num_slices)]))
        self.rename_pin('Q_CLKO', ','.join(['Q_CLKO%d'%(i) for i in range(num_slices)]))
        self.rename_pin('Q_ADCO_CAL0', 'Q_ADCO_CAL0<%d:0>'%(num_bits-1))
        self.rename_pin('Q_ADCO_CAL1', 'Q_ADCO_CAL1<%d:0>'%(num_bits-1))
        self.rename_pin('Q_samp_body', ','.join(['Q_samp_body%d'%(i) for i in range(num_slices+2)]))
        self.rename_pin('Q_bottom_body', ','.join(['Q_bottom_body%d'%(i) for i in range(num_slices+2)]))
        self.rename_pin('Q_RDAC_SEL', 'Q_RDAC_SEL<%d:0>'%(rdac_num_dacs*rdac_num_bits-1))

        if use_offset == False:
            self.remove_pin(','.join(['I_OSP%d'%(i) for i in range(num_slices)]))
            self.remove_pin(','.join(['I_OSM%d'%(i) for i in range(num_slices)]))
            self.remove_pin(','.join(['Q_OSP%d'%(i) for i in range(num_slices)]))
            self.remove_pin(','.join(['Q_OSM%d'%(i) for i in range(num_slices)]))
        if num_inv_bb == 0:
            self.remove_pin(','.join(['I_bottom_body%d'%(i) for i in range(num_slices+2)]))
            self.remove_pin(','.join(['Q_bottom_body%d'%(i) for i in range(num_slices+2)]))
        if vref_sf == False:
            self.remove_pin('I_VREF_SF_bypass')
            self.remove_pin('Q_VREF_SF_bypass')
        if use_sf == False:
            self.remove_pin('I_SF_bypass')
            self.remove_pin('Q_SF_bypass')
        self.remove_pin(','.join(['I_samp_body%d'%(i) for i in range(num_slices+2)]))
        self.remove_pin(','.join(['Q_samp_body%d'%(i) for i in range(num_slices+2)]))

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

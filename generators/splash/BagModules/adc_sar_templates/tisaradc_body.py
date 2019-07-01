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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'tisaradc_body.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__tisaradc_body(Module):
    """Module for library adc_sar_templates cell tisaradc_body.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, 
            sar_lch, 
            sar_pw, 
            sar_nw, 
            sar_sa_m, 
            sar_sa_m_rst, 
            sar_sa_m_rgnn, 
            sar_sa_m_buf, 
            sar_drv_m_list,sar_ckgen_m,sar_ckgen_fo, 
            sar_ckgen_ndelay, 
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
            samp_use_laygo, 
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
            clk_device_intent,
            ret_lch,
            ret_pw,
            ret_nw,
            ret_m_ibuf,
            ret_m_obuf,
            ret_m_latch,
            ret_device_intent,
            space_msar,
            space_msamp,
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
        self.parameters['sar_sa_m_rst'] = sar_sa_m_rst
        self.parameters['sar_sa_m_rgnn'] = sar_sa_m_rgnn
        self.parameters['sar_sa_m_buf'] = sar_sa_m_buf
        self.parameters['sar_drv_m_list'] = sar_drv_m_list
        self.parameters['sar_ckgen_m'] = sar_ckgen_m
        self.parameters['sar_ckgen_fo'] = sar_ckgen_fo
        self.parameters['sar_ckgen_ndelay'] = sar_ckgen_ndelay
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
        self.parameters['samp_use_laygo'] = samp_use_laygo #if true, use laygo for sampler generation
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
        self.parameters['clk_device_intent'] = clk_device_intent
        self.parameters['ret_lch'] = ret_lch
        self.parameters['ret_pw'] = ret_pw
        self.parameters['ret_nw'] = ret_nw
        self.parameters['ret_m_ibuf'] = ret_m_ibuf
        self.parameters['ret_m_obuf'] = ret_m_obuf
        self.parameters['ret_m_latch'] = ret_m_latch
        self.parameters['ret_device_intent'] = ret_device_intent
        self.parameters['space_msar'] = space_msar
        self.parameters['space_msamp'] = space_msamp

        #sar_wsamp_array generation
        term_list=[{
            ','.join(['OSP%d'%(i) for i in range(num_slices)]):
                ','.join(['OSP%d'%(i) for i in range(num_slices)]),
            ','.join(['OSM%d'%(i) for i in range(num_slices)]):
                ','.join(['OSM%d'%(i) for i in range(num_slices)]),
            ','.join(['ASCLKD%d<3:0>'%(i) for i in range(num_slices)]):
                ','.join(['ASCLKD%d<3:0>'%(i) for i in range(num_slices)]),
            ','.join(['EXTSEL_CLK%d'%(i) for i in range(num_slices)]):
                ','.join(['EXTSEL_CLK%d'%(i) for i in range(num_slices)]),
            ','.join(['CLKCAL%d<4:0>'%i for i in range(num_slices)]):
                ','.join(['CLKCAL%d<4:0>'%i for i in range(num_slices)]),
            ','.join(['ADCOUT%d<%d:0>'%(i, num_bits-1) for i in range(num_slices)]):
                ','.join(['ADCOUT%d<%d:0>'%(i, num_bits-1) for i in range(num_slices)]),
        }]
        name_list=(['ICORE0'])
        self.array_instance('ICORE0', name_list, term_list=term_list)
        self.instances['ICORE0'][0].design(
            sar_lch, 
            sar_pw, 
            sar_nw, 
            sar_sa_m, 
            sar_sa_m_rst, 
            sar_sa_m_rgnn, 
            sar_sa_m_buf, 
            sar_drv_m_list,sar_ckgen_m,sar_ckgen_fo, 
            sar_ckgen_ndelay, 
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
            samp_use_laygo, 
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
            clk_device_intent,
            ret_lch,
            ret_pw,
            ret_nw,
            ret_m_ibuf,
            ret_m_obuf,
            ret_m_latch,
            ret_device_intent,
        )

        self.instances['IDCAP0'].design(sar_lch, sar_pw, sar_nw, space_msamp, space_msar, device_intent=sar_device_intent)
        self.instances['IDCAP1'].design(sar_lch, sar_pw, sar_nw, space_msamp, space_msar, device_intent=sar_device_intent)
    
        self.rename_pin('CLKCAL', ','.join(['CLKCAL%d<4:0>'%i for i in range(num_slices)]))
        self.rename_pin('OSP', ','.join(['OSP%d'%(i) for i in range(num_slices)]))
        self.rename_pin('OSM', ','.join(['OSM%d'%(i) for i in range(num_slices)]))
        self.rename_pin('ASCLKD<3:0>', ','.join(['ASCLKD%d<3:0>'%(i) for i in range(num_slices)]))
        self.rename_pin('EXTSEL_CLK', ','.join(['EXTSEL_CLK%d'%(i) for i in range(num_slices)]))
        self.rename_pin('ADCOUT', ','.join(['ADCOUT%d<%d:0>'%(i, num_bits-1) for i in range(num_slices)]))

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

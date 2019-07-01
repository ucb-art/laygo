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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'salatch_simple.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__salatch_simple(Module):
    """Module for library adc_sar_templates cell salatch_simple.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, m_in, m_clkh, m_rst, m_rgnp, device_intent='fast'):
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
        #parameter registeration
        self.parameters['lch'] = lch
        self.parameters['pw'] = pw
        self.parameters['nw'] = nw
        self.parameters['m_in'] = m_in
        self.parameters['m_rst'] = m_rst
        self.parameters['m_rgnp'] = m_rgnp
        self.parameters['device_intent'] = device_intent
        
        #derived parameters
        m_rgnn = m_rgnp + m_rst*2 - 2                 #nmos regeneration pair
        m_tot=max(m_in, m_clkh, m_rgnp + m_rst*2) + 2 #total m of half circuit, +2 for dummy
        m_in_dmy = m_tot - m_in                       #dummies for input row
        m_clkh_dmy = m_tot - m_clkh                   #for clock
        m_rgnp_dmy = m_tot - m_rgnp - m_rst*2         #for rgnp
        m_rgnn_dmy = m_rgnp_dmy                       #for rgnn
        print('total row size is: %d'%(m_tot*2))
        
        #device sizing
        name_list = ['IINP0', 'IINM0',  'ICKN0', 'IRGNP0', 'IRGNP1', 'IRGNN0', 'IRGNN1', 'IRST0', 'IRST1', 'IRST2', 'IRST3']
        nf_list   = [   m_in,    m_in, m_clkh*2,   m_rgnp,   m_rgnp,   m_rgnn,   m_rgnn,   m_rst,   m_rst,   m_rst,   m_rst]
        for name, nf in zip(name_list, nf_list):
            self.instances[name].design(w=pw, l=lch, nf=nf, intent=device_intent)
        name_list = ['IRGNPDM0',       'IRGNNDM0', 'IRGNNDM1', 'IRGNNDM2',     'IINDM0', 'IINDM1',    'ICKNDM0']
        nf_list   = [m_rgnp_dmy*2,   m_rgnn_dmy*2,          2,          2, m_in_dmy*2-2,        2, m_clkh_dmy*2]
        for name, nf in zip(name_list, nf_list):
            self.instances[name].design(w=pw, l=lch, nf=nf, intent=device_intent)


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

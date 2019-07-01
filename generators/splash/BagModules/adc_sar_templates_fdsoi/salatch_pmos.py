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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'salatch_pmos.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__salatch_pmos(Module):
    """Module for library adc_sar_templates cell salatch_pmos.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, m, m_rst, m_rgnn, m_buf, device_intent='fast'):
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
        self.parameters['lch'] = lch
        self.parameters['pw'] = pw
        self.parameters['nw'] = nw
        self.parameters['m'] = m
        self.parameters['m_rst'] = m_rst
        self.parameters['m_rgnn'] = m_rgnn
        self.parameters['m_buf'] = m_buf
        self.parameters['device_intent'] = device_intent

        m_sa=m
        m_in=int(m_sa/2) #using nf=2 devices
        m_ofst=1
        m_clkh=m_in
        #m_clkh = max(1, m_in-1)
        m_rstn = int(m_rst/2)
        m_buf = int(m_buf/2)
        m_rgnn = int(m_rgnn/2)
        m_rgnp = m_rgnn+2*m_rstn-1
        m_tot=max(m_in, m_clkh, m_rgnn+m_rstn*2+m_buf)+1 #+1 #at least one dummy 
        m_in_dmy = m_tot - m_in - m_ofst
        m_clkh_dmy = m_tot - m_clkh
        m_rgnn_dmy = m_tot - m_rgnn - m_rstn*2 - m_buf
        m_rgnp_dmy = m_rgnn_dmy

        self.instances['IINP0'].design(w=pw, l=lch, nf=m_in*2, intent=device_intent)
        self.instances['IINM0'].design(w=pw, l=lch, nf=m_in*2, intent=device_intent)
        self.instances['ICKP0'].design(w=pw, l=lch, nf=m_clkh*4, intent=device_intent)

        self.instances['IOSP0'].design(w=pw, l=lch, nf=m_ofst*2, intent=device_intent)
        self.instances['IOSM0'].design(w=pw, l=lch, nf=m_ofst*2, intent=device_intent)

        self.instances['IRGNP0'].design(w=pw, l=lch, nf=m_rgnp*2, intent=device_intent)
        self.instances['IRGNP1'].design(w=pw, l=lch, nf=m_rgnp*2, intent=device_intent)
        self.instances['IRGNN0'].design(w=nw, l=lch, nf=m_rgnn*2, intent=device_intent)
        self.instances['IRGNN1'].design(w=nw, l=lch, nf=m_rgnn*2, intent=device_intent)

        self.instances['IRST0'].design(w=nw, l=lch, nf=m_rstn*2, intent=device_intent)
        self.instances['IRST1'].design(w=nw, l=lch, nf=m_rstn*2, intent=device_intent)
        self.instances['IRST2'].design(w=nw, l=lch, nf=m_rstn*2, intent=device_intent)
        self.instances['IRST3'].design(w=nw, l=lch, nf=m_rstn*2, intent=device_intent)

        self.instances['IBUFP0'].design(w=pw, l=lch, nf=m_buf*2, intent=device_intent)
        self.instances['IBUFP1'].design(w=pw, l=lch, nf=m_buf*2, intent=device_intent)
        self.instances['IBUFN0'].design(w=nw, l=lch, nf=m_buf*2, intent=device_intent)
        self.instances['IBUFN1'].design(w=nw, l=lch, nf=m_buf*2, intent=device_intent)

        self.instances['IRGNNDM0'].design(w=nw, l=lch, nf=m_rgnn_dmy*2, intent=device_intent)
        self.instances['IRGNNDM1'].design(w=nw, l=lch, nf=m_rgnn_dmy*2, intent=device_intent)
        self.instances['IRGNPDM0'].design(w=pw, l=lch, nf=m_rgnp_dmy*4-2+2, intent=device_intent)
        self.instances['IRGNPDM1'].design(w=pw, l=lch, nf=2, intent=device_intent)
        self.instances['IRGNPDM2'].design(w=pw, l=lch, nf=2, intent=device_intent)
        self.instances['IOSPB0'].design(w=pw, l=lch, nf=m_in_dmy*2-4, intent=device_intent)
        self.instances['IOSMB0'].design(w=pw, l=lch, nf=m_in_dmy*2-4, intent=device_intent)
        self.instances['IINDM0'].design(w=pw, l=lch, nf=6, intent=device_intent)
        self.instances['IINDM1'].design(w=pw, l=lch, nf=2, intent=device_intent)
        self.instances['ICKPDM0'].design(w=pw, l=lch, nf=m_clkh_dmy*4, intent=device_intent)

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

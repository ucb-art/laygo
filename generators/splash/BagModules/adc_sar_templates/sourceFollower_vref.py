# -*- coding: utf-8 -*-

from typing import Dict

import os
import pkg_resources

from bag.design import Module


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'sourceFollower_vref.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__sourceFollower_vref(Module):
    """Module for library adc_sar_templates cell sourceFollower_vref.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, nw, m_mirror, m_bias, m_off, m_in, m_bias_dum, m_in_dum, m_byp, m_byp_bias, bias_current, device_intent):
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
        self.parameters['nw'] = nw
        self.parameters['m_mirror'] = m_mirror
        self.parameters['m_bias'] = m_bias
        self.parameters['m_in'] = m_in
        self.parameters['m_off'] = m_off
        self.parameters['m_bias_dum'] = m_bias_dum
        self.parameters['m_in_dum'] = m_in_dum
        self.parameters['m_byp'] = m_byp
        self.parameters['m_byp_bias'] = m_byp_bias
        self.parameters['bias_current'] = bias_current
        self.parameters['device_intent'] = device_intent

        self.instances['I0'].design(lch=lch, nw=nw, m_mirror=m_mirror, m_bias=m_bias, m_off=m_off, m_in=m_in,
                                    m_bias_dum=m_bias_dum, m_in_dum=m_in_dum, m_byp=m_byp, m_byp_bias=m_byp_bias, bias_current=bias_current, device_intent=device_intent)
        self.instances['I1'].design(lch=lch, nw=nw, m_mirror=m_mirror, m_bias=m_bias, m_off=m_off, m_in=m_in,
                                    m_bias_dum=m_bias_dum, m_in_dum=m_in_dum, m_byp=m_byp, m_byp_bias=m_byp_bias, bias_current=bias_current, device_intent=device_intent)
        self.instances['I2'].design(lch=lch, nw=nw, m_mirror=m_mirror, m_bias=m_bias, m_off=m_off, m_in=m_in,
                                    m_bias_dum=m_bias_dum, m_in_dum=m_in_dum, m_byp=m_byp, m_byp_bias=m_byp_bias,
                                    bias_current=bias_current, device_intent=device_intent)
        if m_byp==0 and m_byp_bias==0:
            self.remove_pin('bypass')

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

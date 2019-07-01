# -*- coding: utf-8 -*-

from typing import Dict

import os
import pkg_resources

from bag.design import Module


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'r2r_dac_unit.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__r2r_dac_unit(Module):
    """Module for library adc_sar_templates cell r2r_dac_unit.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, m, num_series, device_intent='fast'):
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
        self.parameters['num_series'] = num_series
        self.parameters['device_intent'] = device_intent
        # array generation
        name_list = []
        term_list = []
        for i in range(num_series):
            if i == 0:
                term_list.append({'I': 'I',
                                  'O': 'int%d' % (i),
                                  })
            elif i == num_series-1:
                term_list.append({'I': 'int%d' %(i-1),
                                  'O': 'O',
                                  })
            else:
                term_list.append({'I': 'int%d' %(i-1),
                                  'O': 'int%d' % (i),
                                  })
            name_list.append('ITG%d' % (i))
        self.array_instance('ITG0', name_list, term_list=term_list)
        for i in range(num_series):
            self.instances['ITG0'][i].design(lch=lch, pw=pw, nw=nw, m=m, device_intent=device_intent)

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
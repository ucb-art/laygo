# -*- coding: utf-8 -*-


import bag
from typing import Dict, Set, Any, Optional, List

from bag.layout.template import TemplateDB, TemplateBase
from bag.layout.digital import StdCellTemplate, StdCellBase
from bag.layout.routing import TrackID
from bag.layout import RoutingGrid, TemplateDB
import yaml

impl_lib = 'adc_retimer_ec'


def add_tap(template, xo, blk_master, num_row, port_table):
    ny0 = (num_row + 1) // 2
    inst_list = [template.add_std_instance(blk_master, loc=(xo, 0), ny=ny0, spy=2)]
    ny_list = [ny0]
    if num_row >= 2:
        inst_list.append(template.add_std_instance(blk_master, loc=(xo, 1), ny=num_row - ny0, spy=2))
        ny_list.append(num_row - ny0)

    for inst, ny in zip(inst_list, ny_list):
        for name, warr_list in port_table.items():
            for idx in range(ny):
                port = inst.get_port(name, row=idx)
                warr_list.extend(port.get_pins())

    return xo + blk_master.std_size[0]


def get_masters(template, num_bits, cells_per_tap, adc_width, config_file, parity=0):
    tap_params = dict(cell_name='tap_pwr', config_file=config_file)
    tap_master = template.new_template(params=tap_params, temp_cls=StdCellTemplate)
    lat_name = 'latch_ckb_2x_v%d' % parity
    lat_params = dict(cell_name=lat_name, config_file=config_file)
    lat_master = template.new_template(params=lat_params, temp_cls=StdCellTemplate)

    lat_ncol = lat_master.std_size[0] * num_bits
    tap_ncol = tap_master.std_size[0]
    num_taps = (num_bits // cells_per_tap) + 1
    min_num_col = lat_ncol + tap_ncol * num_taps
    min_space_ncol = tap_master.min_space_width
    if min_num_col > adc_width:
        raise ValueError('Minimum # col = %d > ADC # col = %d' % (min_num_col, adc_width))

    tot_num_col = lat_ncol + num_taps * tap_ncol
    if tot_num_col < adc_width:
        tot_space = adc_width - tot_num_col
        if tot_space % min_space_ncol != 0:
            raise ValueError('space columns = %d not divisible by %d' % (tot_space, min_space_ncol))
        space_units = tot_space // min_space_ncol
        left_space = (space_units // 2) * min_space_ncol
        right_space = tot_space - left_space
    else:
        left_space = right_space = 0

    return lat_master, tap_master, left_space, right_space


class RetimeLatchRow(StdCellBase):
    """A row of retiming latch.

    Parameters
    ----------
    temp_db : TemplateDB
        the template database.
    lib_name : str
        the layout library name.
    params : Dict[str, Any]
        the parameter values.
    used_names : Set[str]
        a set of already used cell names.
    **kwargs :
        dictionary of optional parameters.  See documentation of
        :class:`bag.layout.template.TemplateBase` for details.
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        # type: (TemplateDB, str, Dict[str, Any], Set[str], **Any) -> None
        super(RetimeLatchRow, self).__init__(temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        # type: () -> Dict[str, str]
        """Returns a dictionary containing parameter descriptions.

        Override this method to return a dictionary from parameter names to descriptions.

        Returns
        -------
        param_info : Dict[str, str]
            dictionary from parameter name to description.
        """
        return dict(
            parity='latch standard cell parity type.  Either 0 or 1.',
            num_bits='number of output bits of the ADC.',
            adc_width='ADC width in number of columns.',
            cells_per_tap='Number of latch cells per tap connection.',
            config_file='Standard cell configuration file.',
            clk_width='clock wire width.',
        )

    def draw_layout(self):
        # type: () -> None

        parity = self.params['parity']
        num_bits = self.params['num_bits']
        adc_width = self.params['adc_width']
        config_file = self.params['config_file']
        cells_per_tap = self.params['cells_per_tap']
        clk_width = self.params['clk_width']

        if num_bits % cells_per_tap != 0:
            raise ValueError('num_bits = %d must be multiple of cells_per_tap = %d' % (num_bits, cells_per_tap))

        # use standard cell routing grid
        self.update_routing_grid()

        # get template masters
        lat_master, tap_master, lsp_ncol, rsp_ncol = get_masters(self, num_bits, cells_per_tap, adc_width,
                                                                 config_file, parity=parity)
        num_row = lat_master.std_size[1]
        num_col = lat_master.std_size[0]

        port_table = dict(VDD=[], VSS=[])

        # add left spaces
        xcur = lsp_ncol
        # add left tap
        xcur = add_tap(self, xcur, tap_master, num_row, port_table)

        # add latches and taps
        num_grp = num_bits // cells_per_tap
        clkb_list = []
        bit_idx = 0
        for grp_idx in range(num_grp):
            lat_inst = self.add_std_instance(lat_master, 'XLAT%d' % grp_idx,
                                             loc=(xcur, 0), nx=cells_per_tap, spx=num_col)
            for lat_idx in range(cells_per_tap):
                self.reexport(lat_inst.get_port('I', col=lat_idx), net_name='in<%d>' % bit_idx, show=False)
                self.reexport(lat_inst.get_port('O', col=lat_idx), net_name='out<%d>' % bit_idx, show=False)
                clkb_list.extend(lat_inst.get_port('CLKB', col=lat_idx).get_pins())
                bit_idx += 1
            xcur += cells_per_tap * num_col
            xcur = add_tap(self, xcur, tap_master, num_row, port_table)

        # set template size
        adc_width = adc_width - 2 * self._bound_params['lr_width']
        self.set_std_size((adc_width, num_row))
        # fill spaces
        self.fill_space()

        # connect and export clock.
        clk_layer = clkb_list[0].layer_id + 1
        clk_pitch = self.grid.get_track_pitch(clk_layer, unit_mode=True)
        num_tracks = self.bound_box.height_unit // clk_pitch
        clk_tidx = (num_tracks - 1) / 2
        clk_warr = self.connect_to_tracks(clkb_list, TrackID(clk_layer, clk_tidx, width=clk_width), unit_mode=True)
        self.add_pin('clkb', clk_warr, show=False)

        # export supplies
        self.add_pin('VDD', port_table['VDD'], show=False)
        self.add_pin('VSS', port_table['VSS'], show=False)


class RetimeSpaceRow(StdCellBase):
    """An empty space row.

    Parameters
    ----------
    temp_db : TemplateDB
        the template database.
    lib_name : str
        the layout library name.
    params : Dict[str, Any]
        the parameter values.
    used_names : Set[str]
        a set of already used cell names.
    **kwargs :
        dictionary of optional parameters.  See documentation of
        :class:`bag.layout.template.TemplateBase` for details.
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        # type: (TemplateDB, str, Dict[str, Any], Set[str], **Any) -> None
        super(RetimeSpaceRow, self).__init__(temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        # type: () -> Dict[str, str]
        """Returns a dictionary containing parameter descriptions.

        Override this method to return a dictionary from parameter names to descriptions.

        Returns
        -------
        param_info : Dict[str, str]
            dictionary from parameter name to description.
        """
        return dict(
            num_bits='number of output bits of the ADC.',
            adc_width='ADC width in number of columns.',
            cells_per_tap='Number of latch cells per tap connection.',
            config_file='Standard cell configuration file.',
        )

    def draw_layout(self):
        # type: () -> None

        num_bits = self.params['num_bits']
        adc_width = self.params['adc_width']
        config_file = self.params['config_file']
        cells_per_tap = self.params['cells_per_tap']

        if num_bits % cells_per_tap != 0:
            raise ValueError('num_bits = %d must be multiple of cells_per_tap = %d' % (num_bits, cells_per_tap))

        if num_bits % cells_per_tap != 0:
            raise ValueError('num_bits = %d must be multiple of cells_per_tap = %d' % (num_bits, cells_per_tap))

        # use standard cell routing grid
        self.update_routing_grid()

        # get template masters
        lat_master, tap_master, lsp_ncol, rsp_ncol = get_masters(self, num_bits, cells_per_tap, adc_width,
                                                                 config_file)
        num_row = lat_master.std_size[1]
        num_col = lat_master.std_size[0]

        port_table = dict(VDD=[], VSS=[])

        # add left spaces
        xcur = lsp_ncol
        # add left tap
        xcur = add_tap(self, xcur, tap_master, num_row, port_table)

        # add fill and taps
        num_grp = num_bits // cells_per_tap
        for grp_idx in range(num_grp):
            xcur += cells_per_tap * num_col
            xcur = add_tap(self, xcur, tap_master, num_row, port_table)

        # set template size
        adc_width = adc_width - 2 * self._bound_params['lr_width']
        self.set_std_size((adc_width, num_row))
        # fill spaces
        self.fill_space()

        # export supplies
        self.add_pin('VDD', port_table['VDD'], show=False)
        self.add_pin('VSS', port_table['VSS'], show=False)


class RetimeBufferRow(StdCellBase):
    """A row of clock buffers.

    Parameters
    ----------
    temp_db : TemplateDB
        the template database.
    lib_name : str
        the layout library name.
    params : Dict[str, Any]
        the parameter values.
    used_names : Set[str]
        a set of already used cell names.
    **kwargs :
        dictionary of optional parameters.  See documentation of
        :class:`bag.layout.template.TemplateBase` for details.
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        # type: (TemplateDB, str, Dict[str, Any], Set[str], **Any) -> None
        super(RetimeBufferRow, self).__init__(temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_default_param_values(cls):
        # type: () -> Dict[str, Any]
        return dict(num_buf_dig=0)

    @classmethod
    def get_params_info(cls):
        # type: () -> Dict[str, str]
        """Returns a dictionary containing parameter descriptions.

        Override this method to return a dictionary from parameter names to descriptions.

        Returns
        -------
        param_info : Dict[str, str]
            dictionary from parameter name to description.
        """
        return dict(
            num_buf='number of clock buffers.',
            num_bits='number of output bits of the ADC.',
            adc_width='ADC width in number of columns.',
            cells_per_tap='Number of latch cells per tap connection.',
            config_file='Standard cell configuration file.',
            num_buf_dig='Number of clock buffers to draw for digital block.',
        )

    def draw_layout(self):
        # type: () -> None

        num_buf = self.params['num_buf']
        num_bits = self.params['num_bits']
        adc_width = self.params['adc_width']
        config_file = self.params['config_file']
        cells_per_tap = self.params['cells_per_tap']
        num_buf_dig = self.params['num_buf_dig']

        if num_bits % cells_per_tap != 0:
            raise ValueError('num_bits = %d must be multiple of cells_per_tap = %d' % (num_bits, cells_per_tap))
        if num_buf > num_bits:
            raise ValueError('Must have num_buf = %d < num_bits = %d' % (num_buf, num_bits))
        num_buf_dig_max = (num_bits - num_buf) // 2
        if num_buf_dig_max < num_buf_dig:
            raise ValueError('Must have num_buf_out = %d <= %d' % (num_buf_dig, num_buf_dig_max))

        # use standard cell routing grid
        self.update_routing_grid()

        # get template masters
        lat_master, tap_master, lsp_ncol, rsp_ncol = get_masters(self, num_bits, cells_per_tap, adc_width,
                                                                 config_file)

        buf_params = dict(cell_name='inv_clk_16x', config_file=config_file)
        buf_master = self.new_template(params=buf_params, temp_cls=StdCellTemplate)

        num_col = lat_master.std_size[0]

        port_table = dict(VDD=[], VSS=[])

        # add left spaces
        xcur = lsp_ncol
        # add left tap
        xcur = add_tap(self, xcur, tap_master, 1, port_table)

        # figure out buffer/fill indices
        master_list = [None] * num_bits  # type: List[Optional[StdCellBase]]
        buf_start = (num_bits - num_buf) // 2
        for idx in range(buf_start, buf_start + num_buf + num_buf_dig):
            master_list[idx] = buf_master
        # add fill, buffer, and taps
        in_list = []
        out_list = []
        dig_out_list = []
        cur_buf_idx = 0
        for idx, master in enumerate(master_list):
            if master is not None:
                inst = self.add_std_instance(master, 'X%d' % idx, loc=(xcur, 0))
            else:
                inst = None
            xcur += num_col
            if idx % cells_per_tap == (cells_per_tap - 1):
                xcur = add_tap(self, xcur, tap_master, 1, port_table)
            if inst is not None:
                if cur_buf_idx < num_buf:
                    in_list.extend(inst.get_port('I').get_pins())
                    out_list.extend(inst.get_port('O').get_pins())
                else:
                    out_list.extend(inst.get_port('I').get_pins())
                    dig_out_list.extend(inst.get_port('O').get_pins())
                cur_buf_idx += 1

        # set template size
        adc_width = adc_width - 2 * self._bound_params['lr_width']
        self.set_std_size((adc_width, 1))
        # fill spaces
        self.fill_space()

        if in_list:
            # find input/output track ID
            in_layer = in_list[0].layer_id
            out_layer = out_list[0].layer_id
            if in_layer != out_layer:
                raise ValueError('This template only works if inverter has input and output on same layer.')
            io_layer = in_layer + 1
            tot_space = self.get_num_tracks(io_layer)
            io_width = self.grid.get_max_track_width(io_layer, 2, tot_space, half_end_space=False)
            io_idx_list = self.grid.get_evenly_spaced_tracks(2, tot_space, io_width, half_end_space=False)

            # export input/output
            out_tidx = TrackID(io_layer, io_idx_list[0], width=io_width)
            in_tidx = TrackID(io_layer, io_idx_list[1], width=io_width)
            self.connect_to_tracks(in_list, in_tidx, unit_mode=True)
            out_warr = self.connect_to_tracks(out_list, out_tidx, unit_mode=True)

            self.add_pin('in', in_list[num_buf // 2], show=False)
            self.add_pin('out', out_warr, show=False)
            if dig_out_list:
                dig_out_warr = self.connect_to_tracks(dig_out_list, in_tidx, unit_mode=True)
                self.add_pin('out_dig', dig_out_warr, show=False)

        # export supplies
        self.add_pin('VDD', port_table['VDD'], show=False)
        self.add_pin('VSS', port_table['VSS'], show=False)


class RetimeColumn(StdCellBase):
    """A column.

    Parameters
    ----------
    temp_db : TemplateDB
        the template database.
    lib_name : str
        the layout library name.
    params : Dict[str, Any]
        the parameter values.
    used_names : Set[str]
        a set of already used cell names.
    **kwargs :
        dictionary of optional parameters.  See documentation of
        :class:`bag.layout.template.TemplateBase` for details.
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        # type: (TemplateDB, str, Dict[str, Any], Set[str], **Any) -> None
        super(RetimeColumn, self).__init__(temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_params_info(cls):
        # type: () -> Dict[str, str]
        """Returns a dictionary containing parameter descriptions.

        Override this method to return a dictionary from parameter names to descriptions.

        Returns
        -------
        param_info : Dict[str, str]
            dictionary from parameter name to description.
        """
        return dict(
            num_buf='number of clock buffers.',
            num_buf_dig='number of digital clock buffers.',
            num_bits='number of output bits per ADC.',
            num_adc='number of ADCs',
            adc_width='ADC width in number of columns.',
            cells_per_tap='Number of latch cells per tap connection.',
            config_file='Standard cell configuration file.',
            clk_width='clock wire width.',
            adc_idx='ADC index.',
        )

    def draw_layout(self):
        # type: () -> None

        num_buf = self.params['num_buf']
        num_buf_dig = self.params['num_buf_dig']
        num_bits = self.params['num_bits']
        num_adc = self.params['num_adc']
        adc_width = self.params['adc_width']
        cells_per_tap = self.params['cells_per_tap']
        config_file = self.params['config_file']
        clk_width = self.params['clk_width']
        adc_idx = self.params['adc_idx']

        self.set_draw_boundaries(True)

        self.update_routing_grid()

        lat_params = dict(
            parity=0,
            num_bits=num_bits,
            adc_width=adc_width,
            cells_per_tap=cells_per_tap,
            config_file=config_file,
            clk_width=clk_width,
        )
        lat_master0 = self.new_template(params=lat_params, temp_cls=RetimeLatchRow)
        lat_params['parity'] = 1
        lat_master1 = self.new_template(params=lat_params, temp_cls=RetimeLatchRow)

        space_params = dict(
            num_bits=num_bits,
            adc_width=adc_width,
            cells_per_tap=cells_per_tap,
            config_file=config_file,
        )
        space_master = self.new_template(params=space_params, temp_cls=RetimeSpaceRow)
        buf_params = dict(
            num_buf=num_buf,
            num_buf_dig=num_buf_dig,
            num_bits=num_bits,
            adc_width=adc_width,
            cells_per_tap=cells_per_tap,
            config_file=config_file,
        )
        buf_dig_master = self.new_template(params=buf_params, temp_cls=RetimeBufferRow)
        buf_params['num_buf_dig'] = 0
        buf_master = self.new_template(params=buf_params, temp_cls=RetimeBufferRow)
        buf_params['num_buf'] = 0
        buf_fill_master = self.new_template(params=buf_params, temp_cls=RetimeBufferRow)

        spx = lat_master0.std_size[0]
        spy = lat_master0.std_size[1]

        ck_phase_2 = num_adc - 1
        ck_phase_1 = int(num_adc / 2) - 1
        ck_phase_0_0 = int((int(num_adc / 2) + 1) % num_adc)
        ck_phase_0_1 = 1
        ck_phase_out = ck_phase_1
        ck_phase_buf = sorted(set([ck_phase_2, ck_phase_1, ck_phase_0_0, ck_phase_0_1]))

        # last stage latch
        inst2 = self.add_std_instance(lat_master0, 'X2', nx=1, spx=spx)
        ck_list_inst2 = inst2.get_all_port_pins('clkb')
        self.add_pin('clkb2', ck_list_inst2, show=False)

        self._export_output(inst2, adc_idx, num_bits)
        io_wires = []
        self._collect_io_wires(inst2, 'in', num_bits, io_wires)

        vdd_list = inst2.get_all_port_pins('VDD')
        vss_list = inst2.get_all_port_pins('VSS')

        # second-to-last stage latches
        inst1 = self.add_std_instance(lat_master1, 'X1', loc=(0, spy), nx=1, spx=spx)
        ck_list_inst1 = inst1.get_all_port_pins('clkb')
        self.add_pin('clkb1', ck_list_inst1, show=False)

        self._collect_io_wires(inst1, 'out', num_bits, io_wires)
        io_wires = self.connect_wires(io_wires, unit_mode=True)
        self.add_pin('io21', io_wires, show=False)
        io_wires = []
        self._collect_io_wires(inst1, 'in', num_bits, io_wires)

        vdd_list.extend(inst1.get_all_port_pins('VDD'))
        vss_list.extend(inst1.get_all_port_pins('VSS'))

        # set template size
        cb_nrow = buf_master.std_size[1]
        row_width = adc_width - 2 * self._bound_params['lr_width']
        self.set_std_size((row_width, 4 * spy + cb_nrow))
        # draw boundaries
        self.draw_boundaries()
        blk_w, blk_h = self.bound_box.width_unit, self.bound_box.height_unit

        # first stage latches, clock buffers, fills
        if adc_idx < int(num_adc / 2):
            finst = self.add_std_instance(space_master, loc=(0, 2 * spy))
            inst = self.add_std_instance(lat_master0, loc=(0, 3 * spy))
        else:
            finst = self.add_std_instance(space_master, loc=(0, 3 * spy))
            inst = self.add_std_instance(lat_master0, loc=(0, 2 * spy))
        # connect clk/vdd/vss/output
        ck_list_inst = inst.get_all_port_pins('clkb')
        self.add_pin('clkb<%d>' % adc_idx, ck_list_inst, show=False)
        vdd_list.extend(inst.get_all_port_pins('VDD'))
        vss_list.extend(inst.get_all_port_pins('VSS'))
        vdd_list.extend(finst.get_all_port_pins('VDD'))
        vss_list.extend(finst.get_all_port_pins('VSS'))
        self._collect_io_wires(inst, 'out', num_bits, io_wires)
        # export input
        for bit_idx in range(num_bits):
            in_pin = inst.get_port('in<%d>' % bit_idx).get_pins()[0]
            in_pin = self.connect_wires(in_pin, upper=blk_h, unit_mode=True)
            name = 'in_%d<%d>' % (adc_idx, bit_idx)
            self.add_pin(name, in_pin, show=False)
        # clock buffers/fills
        if adc_idx in ck_phase_buf:
            if adc_idx == ck_phase_out:
                cur_master = buf_dig_master
            else:
                cur_master = buf_master
            cfinst = self.add_std_instance(cur_master, loc=(0, 4 * spy))
            vdd_list.extend(cfinst.get_all_port_pins('VDD'))
            vss_list.extend(cfinst.get_all_port_pins('VSS'))
            in_pin = cfinst.get_port('in').get_pins()[0]
            in_pin = self.connect_wires(in_pin, upper=blk_h, unit_mode=True)
            self.add_pin('clk%d' % adc_idx, in_pin)
            buf_port = cfinst.get_port('out').get_pins()[0]
            self.add_pin('buf%d' %(adc_idx), buf_port, show=False)
            if cfinst.has_port('out_dig'):
                out_dig_warr = cfinst.get_port('out_dig').get_pins()[0]
                self.add_pin('out_dig', out_dig_warr, show=False)
        else:
            cfinst = self.add_std_instance(buf_fill_master, loc=(0, 4 * spy))
            vdd_list.extend(cfinst.get_all_port_pins('VDD'))
            vss_list.extend(cfinst.get_all_port_pins('VSS'))

        io_wires = self.connect_wires(io_wires, unit_mode=True)
        self.add_pin('io10', io_wires, show=False)

        # export supplies
        self.add_pin('VDD', vdd_list, show=False)
        self.add_pin('VSS', vss_list, show=False)

    def _export_output(self, inst, adc_idx, num_bits):
        for bit_idx in range(num_bits):
            out_pin = inst.get_port('out<%d>' % bit_idx, col=0).get_pins()[0]
            out_pin = self.connect_wires(out_pin, lower=0, unit_mode=True)
            name = 'out_%d<%d>' % (adc_idx, bit_idx)
            self.add_pin(name, out_pin, show=True)

    @staticmethod
    def _collect_io_wires(inst, name, num_bits, wire_list):
        for bit_idx in range(num_bits):
            pname = '%s<%d>' % (name, bit_idx)
            wire_list.extend(inst.get_all_port_pins(pname))


class Retimer(TemplateBase):
    """First stage retime latch for a ADC block.

    Parameters
    ----------
    temp_db : TemplateDB
        the template database.
    lib_name : str
        the layout library name.
    params : Dict[str, Any]
        the parameter values.
    used_names : Set[str]
        a set of already used cell names.
    **kwargs :
        dictionary of optional parameters.  See documentation of
        :class:`bag.layout.template.TemplateBase` for details.
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        # type: (TemplateDB, str, Dict[str, Any], Set[str], **Any) -> None
        super(Retimer, self).__init__(temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_default_param_values(cls):
        # type: () -> Dict[str, Any]
        return dict(reserve_tracks=[])

    @classmethod
    def get_params_info(cls):
        # type: () -> Dict[str, str]
        return dict(
            num_buf='number of clock buffers.',
            num_buf_dig='number of digital clock buffers.',
            num_bits='number of output bits per ADC.',
            num_adc='number of ADCs.',
            adc_width='ADC width in number of columns.',
            cells_per_tap='Number of latch cells per tap connection.',
            config_file='Standard cell configuration file.',
            clk_width='clock wire width.',
            adc_order='List of ADC index order.',
            reserve_tracks='tracks to reserve for ADC routing.',
        )

    def draw_layout(self):
        # type: () -> None

        num_buf = self.params['num_buf']
        num_buf_dig = self.params['num_buf_dig']
        num_bits = self.params['num_bits']
        num_adc = self.params['num_adc']
        adc_width = self.params['adc_width']
        cells_per_tap = self.params['cells_per_tap']
        config_file = self.params['config_file']
        clk_width = self.params['clk_width']
        adc_order = self.params['adc_order']
        reserve_tracks = self.params['reserve_tracks']
        buf_ck_width = 5

        col_params = dict(
            num_buf=num_buf,
            num_buf_dig=num_buf_dig,
            num_bits=num_bits,
            num_adc=num_adc,
            adc_width=adc_width,
            cells_per_tap=cells_per_tap,
            config_file=config_file,
            clk_width=clk_width,
            adc_idx=0,
        )

        ck_dict = {}

        # finding clock_bar phases <- added by Jaeduk
        # rules:
        # 1) last stage latches: num_adc-1
        # 2) second last stage latches: int(num_adc/2)-1
        # 3) the first half of first stage latches: int((int(num_adc/2)+1)%num_adc)
        # 4) the second half of first stage latches: 1
        # 5) the output phase = the second last latch phase
        ck_phase_2 = num_adc - 1
        ck_phase_1 = int(num_adc / 2) - 1
        ck_phase_0_0 = int((int(num_adc / 2) + 1) % num_adc)
        ck_phase_0_1 = 1
        ck_phase_out = ck_phase_1
        ck_phase_buf = sorted(set([ck_phase_2, ck_phase_1, ck_phase_0_0, ck_phase_0_1]))
        print('clocking phases:', ck_phase_2, ck_phase_1, ck_phase_0_0, ck_phase_0_1, ck_phase_out, ck_phase_buf)
        ck_dict[ck_phase_2] = []
        ck_dict[ck_phase_1] = []
        ck_dict[ck_phase_0_0] = []
        ck_dict[ck_phase_0_1] = []

        io21_list = []
        io10_list = []
        vdd_list = []
        vss_list = []
        ck1_list = []
        ck5_list = []
        buf_dict = {}
        out_dig_warr = None

        for col_idx, adc_idx in enumerate(adc_order):
            col_params['adc_idx'] = adc_idx
            col_master = self.new_template(params=col_params, temp_cls=RetimeColumn)

            spx = col_master.std_size[0] * col_master.std_col_width_unit
            spy = col_master.std_size[1] * col_master.std_row_height_unit

            col_inst = self.add_instance(col_master, 'C%d' %(adc_idx), loc=(spx * col_idx, 0), unit_mode=True)
            ck_dict[ck_phase_2].extend(col_inst.get_all_port_pins('clkb2'))

            self._export_output(col_inst, adc_idx, num_bits)

            vdd_list.extend(col_inst.get_all_port_pins('VDD'))
            vss_list.extend(col_inst.get_all_port_pins('VSS'))

            ck_dict[ck_phase_1].extend(col_inst.get_all_port_pins('clkb1'))

            io21_list.extend(col_inst.get_all_port_pins('io21'))

            if adc_idx < int(num_adc/2):
                ck_list = ck5_list
            else:
                ck_list = ck1_list
            ck_list.extend(col_inst.get_all_port_pins('clkb<%d>' % adc_idx))

            for bit_idx in range(num_bits):
                in_pin = col_inst.get_port('in_%d<%d>' % (adc_idx, bit_idx)).get_pins()[0]
                name = 'in_%d<%d>' % (adc_idx, bit_idx)
                self.add_pin(name, in_pin, show=True)

            if adc_idx in ck_phase_buf:
                clk_pin = col_inst.get_port('clk%d' % adc_idx).get_pins()[0]
                self.add_pin('clk%d' % adc_idx, clk_pin)
                buf_dict[adc_idx] = col_inst.get_port('buf%d' % (adc_idx)).get_pins()[0]
                if col_inst.has_port('out_dig'):
                    out_dig_warr = col_inst.get_port('out_dig').get_pins()[0]

            io10_list.extend(col_inst.get_all_port_pins('io10'))

        # set template size
        col_top_layer = col_master.top_layer
        if self.grid.dir_tracks[col_top_layer] == 'x':
            size_y = spy / self.grid.get_track_pitch(col_top_layer, unit_mode=True)
        else:
            size_y = spy / self.grid.get_track_pitch(col_top_layer + 1, unit_mode=True)

        self.size = [col_top_layer, adc_width * num_adc, size_y]

        ck_dict[ck_phase_2] = self.connect_wires(ck_dict[ck_phase_2], unit_mode=True)
        ck_dict[ck_phase_1] = self.connect_wires(ck_dict[ck_phase_1], unit_mode=True)
        self.connect_wires(io21_list, unit_mode=True)
        self.connect_wires(io10_list, unit_mode=True)
        ck_dict[ck_phase_0_1] = self.connect_wires(ck1_list)
        ck_dict[ck_phase_0_0] = self.connect_wires(ck5_list)

        for ck_idx in ck_phase_buf:
            buf_out = buf_dict[ck_idx]
            buf_layer = buf_out.layer_id
            ck_wires = ck_dict[ck_idx]
            tr_id = self.grid.coord_to_nearest_track(buf_layer + 1, buf_out.middle_unit, mode=0, unit_mode=True)
            tr_id = TrackID(buf_layer + 1, tr_id, width=buf_ck_width)
            self.connect_to_tracks([buf_out, ] + ck_wires, tr_id, unit_mode=True)

        # export digital output
        tr_id = self.grid.coord_to_nearest_track(out_dig_warr.layer_id + 1, out_dig_warr.middle_unit, mode=0, unit_mode=True)
        tr_id = TrackID(out_dig_warr.layer_id + 1, tr_id, width=buf_ck_width)
        warr = self.connect_to_tracks(out_dig_warr, tr_id, track_lower=0, unit_mode=True)
        self.add_pin('ck_out', warr, show=True)

        sup_layer = vdd_list[0].layer_id + 1
        vdd_list, vss_list = self.do_power_fill(sup_layer, vdd_warrs=vdd_list, vss_warrs=vss_list, unit_mode=True,
                                                space=0, space_le=0, y_margin=220)
        sup_layer += 1

        # reserve routing tracks for ADC
        adc_pitch = col_master.get_num_tracks(sup_layer)
        reserve_tracks = [r / self.grid.get_track_pitch(sup_layer) for r in reserve_tracks]
        for tid in reserve_tracks:
            self.reserve_tracks(sup_layer, tid, num=num_adc, pitch=adc_pitch)

        vdd_list, vss_list = self.do_power_fill(sup_layer, vdd_warrs=vdd_list, vss_warrs=vss_list, unit_mode=True,
                                                fill_width=2, fill_space=1, space=0, space_le=0, y_margin=200)
        sup_layer += 1

        vdd_list, vss_list = self.do_power_fill(sup_layer, vdd_warrs=vdd_list, vss_warrs=vss_list, unit_mode=True,
                                                space=0, space_le=0, y_margin=220)

        self.add_pin('VDD', vdd_list, show=True)
        self.add_pin('VSS', vss_list, show=True)

    def _export_output(self, inst, adc_idx, num_bits):
        for bit_idx in range(num_bits):
            out_pin = inst.get_port('out_%d<%d>' % (adc_idx, bit_idx), col=0).get_pins()[0]
            name = 'out_%d<%d>' % (adc_idx, bit_idx)
            self.add_pin(name, out_pin, show=True)

    @staticmethod
    def _collect_io_wires(inst, name, num_bits, wire_list):
        for bit_idx in range(num_bits):
            pname = '%s<%d>' % (name, bit_idx)
            wire_list.extend(inst.get_all_port_pins(pname))


def latch_adc(prj, temp_db):
    cell_name = 'adc_retimer'
    layout_params = dict(
        num_buf=3,
        num_buf_dig=1,
        num_bits=9,
        num_adc=8,
        adc_width=224,
        cells_per_tap=3,
        config_file='adc_sar_retimer_logic.yaml',
        clk_width=8,
        adc_order=[0, 2, 4, 6, 1, 3, 5, 7],
        reserve_tracks=[31.5, 38.5, 40.5, 55.5, 57.5, 59.5, 91.5, 93.5,
                        127.5, 129.5, 163.5, 165.5, 229.5, 230.5, 231.5, 232.5],
    )
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        layout_params['num_bits']=specdict['n_bit']
        layout_params['num_adc']=specdict['n_interleave']
        layout_params['adc_order']=sizedict['slice_order']
        layout_params['adc_width']=sizedict['adc_width']
        layout_params['reserve_tracks']=sizedict['reserve_tracks']
        if layout_params['num_bits']==10: #this is hack; need to be fixed
            layout_params['cells_per_tap']=5
    template = temp_db.new_template(params=layout_params, temp_cls=Retimer, debug=False)
    temp_db.instantiate_layout(prj, template, cell_name, debug=True)

    template.write_summary_file('%s.yaml' % cell_name, impl_lib, cell_name)


if __name__ == '__main__':

    local_dict = locals()
    if 'bprj' not in local_dict:
        print('creating BAG project')
        bprj = bag.BagProject()
        temp = 70.0
        layers = [3, 4, 5, 6]
        spaces = [0.058, 0.04, 0.04, 0.112]
        widths = [0.032, 0.04, 0.04, 0.080]
        bot_dir = 'y'
        #layers = [3, 4, 5, 6]
        #spaces = [0.052, 0.040, 0.044, 0.096]
        #widths = [0.032, 0.040, 0.040, 0.064]
        #bot_dir = 'y'
        width_override = {
            4: {2: 0.120},
            5: {2: 0.120}
        }

        routing_grid = RoutingGrid(bprj.tech_info, layers, spaces, widths, bot_dir, width_override=width_override)

        tdb = TemplateDB('template_libs.def', routing_grid, impl_lib, use_cybagoa=True)

        latch_adc(bprj, tdb)
    else:
        print('loading BAG project')

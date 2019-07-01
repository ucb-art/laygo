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

"""
The LayoutIO module implements interfaces for layout import and export. It supports BAG and GDS IO.
"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

import yaml
from .LayoutDB import *
from .GDSIO import *
import logging

# TODO: yaml (refer to GridDB.py), skill, matplotlib export
# TODO: path, label support

#aux functions
def _load_layermap(layermapfile):
    """
    Load layermap information from layermapfile (Foundry techfile can be used)

    Parameters
    ----------
    layermapfile : str
        layermap filename
        example can be found in default.layermap or see below
        #technology layer information
        #layername  layerpurpose stream# datatype
        text        drawing 100 0
        prBoundary  drawing 101 0
        metal1      M1      drawing 50  0
        metal1      M1      pin     50  10
        metal2      M2      drawing 51  0
        metal2      M2      pin     51  10

    Returns
    -------
    dict
        constructed layermap information

    """
    layermap = dict()
    f = open(layermapfile, 'r')
    for line in f:
        tokens = line.split()
        if not len(tokens) == 0:
            if not tokens[0].startswith('#'):
                name = tokens[0]
                #if not layermap.has_key(name):
                if name not in layermap:
                    layermap[name] = dict()
                layermap[name][tokens[1]] = [int(tokens[2]), int(tokens[3])]
    return layermap

def _get_layer_from_layermap(layermap, layerid):
    """
    Get corresponding layer name and purpose from layermap

    Parameters
    ----------
    layermap : dict()
        layermap dictionary
    layerid : [int, int]
        layermap id
    Returns
    -------
    [str, str]
        layer name and purpose
    """
    for layer_name, layer in layermap.items():
        for layer_purpose, layer in layer.items():
            if layerid == layer:
                return [layer_name, layer_purpose]
    return None

def _get_bBox(xy):
    """
    Get a bounding box from coordinates

    Parameters
    ----------
    xy : np.2darray
        array of coordinates
    Returns
    -------
    np.2darray
        bounding box array
    """
    a = np.zeros((2, 2))
    a[0, :] = np.min(xy, axis=0)
    a[1, :] = np.max(xy, axis=0)
    return a

#export functions
def export_GDS(db, libname, cellname, filename, layermapfile="default.layermap", physical_unit=1e-9,
               logical_unit=0.001, pin_label_height=0.1, pin_annotate_layer=['text', 'drawing'], text_height=0.1):
    """
    Export specified cell(s) to a GDS file

    Parameters
    ----------
    db : laygo.LayoutDB.LayoutDB
        design database
    libname : str
        name of library to be exported
    cellname : list or str
        name of cells to be exported
    filename : str
        output filename
    layermapfile : str
        layermap filename
    physical_unit : float, optional
        GDS physical unit
    logical_unit : float, optional
        GDS logical unit
    pin_label_height : float, optional
        pin label height
    pin_annotate_layer : [str, str], optional
        pin annotate layer name (used when pinname is different from netname)
    text_height : float, optional
        text height
    """
    layermap = _load_layermap(layermapfile)  # load layermap information

    logging.debug('ExportGDS: Library:' + libname)
    lib_export = Library(5, str.encode(libname), physical_unit, logical_unit)

    if isinstance(cellname, str): cellname = [cellname]  # convert to a list for iteration
    design = db.design
    for sn in cellname:
        s = design[libname][sn]
        logging.debug('ExportGDS: Structure:' + sn)
        s_export = lib_export.add_structure(sn)
        for p in s['rects'].values():  # rect generation
            if p.xy.ndim == 2:
                xy = np.expand_dims(p.xy / logical_unit, axis=0)  # extend dims for iteration
            else:
                xy = p.xy / logical_unit
            for _xy in xy:
                bx1, bx2 = sorted(_xy[:,0].tolist()) #need to be changed..
                by1, by2 = sorted(_xy[:,1].tolist())
                ll = np.array([bx1, by1])  # lower-left
                ur = np.array([bx2, by2])  # upper-right
                _xy=np.vstack([ll,ur])
                c = [[int(_xy[0][0]), int(_xy[0][1])], [int(_xy[0][0]), int(_xy[1][1])],
                     [int(_xy[1][0]), int(_xy[1][1])], [int(_xy[1][0]), int(_xy[0][1])],
                     [int(_xy[0][0]), int(_xy[0][1])]]  # build list
                l = layermap[p.layer[0]][p.layer[1]]
                lib_export.add_boundary(sn, l[0], l[1], c)
                logging.debug('ExportGDS: Rect:' + p.name + ' layer:' + str(l) + ' xy:' + str(c))
        for p in s['pins'].values():  # pin generation
            if p.xy.ndim == 2:
                xy = np.expand_dims(p.xy / logical_unit, axis=0)  # extend dims for iteration
            else:
                xy = p.xy / logical_unit
            for _xy in xy:
                c = [[int(_xy[0][0]), int(_xy[0][1])], [int(_xy[0][0]), int(_xy[1][1])],
                     [int(_xy[1][0]), int(_xy[1][1])], [int(_xy[1][0]), int(_xy[0][1])],
                     [int(_xy[0][0]), int(_xy[0][1])]]  # build list
                l = layermap[p.layer[0]][p.layer[1]]
                lib_export.add_boundary(sn, l[0], l[1], c)
                lib_export.add_text(sn, l[0], l[1], [[int(0.5*(_xy[0][0]+_xy[1][0])), int(0.5*(_xy[0][1]+_xy[1][1]))]],
                                    string=p.netname, textHeight=pin_label_height / logical_unit)
                if not p.name==p.netname: # if netname is different from pinname, create an annotate text
                    l_ann = layermap[pin_annotate_layer[0]][pin_annotate_layer[1]]
                    lib_export.add_text(sn, l_ann[0], l_ann[1],
                                        [[int(0.5*(_xy[0][0]+_xy[1][0])), int(0.5*(_xy[0][1]+_xy[1][1]))]],
                                        string=p.name, textHeight=pin_label_height / logical_unit)
                logging.debug('ExportGDS: Pin:' + p.name + ' net:' + p.netname + ' layer:' + str(l) + ' xy:' + str(c))
        for t in s['texts'].values():  # text generation
            if t.xy.ndim == 1:
                xy = np.expand_dims(t.xy / logical_unit, axis=0)  # extend dims for iteration
            else:
                xy = t.xy / logical_unit
            for _xy in xy:
                l = layermap[t.layer[0]][t.layer[1]]
                _xy = [int(_xy0) for _xy0 in _xy]
                lib_export.add_text(sn, l[0], l[1], [_xy], string=t.text, textHeight=int(text_height / logical_unit))
                logging.debug('ExportGDS: Text:' + t.name + ' text:' + t.text + ' layer:' + str(l) + ' xy:' + str(_xy))
        for inst in s['instances'].values():  # instance generation
            if inst.xy.ndim == 1:
                xy = np.expand_dims(inst.xy / logical_unit, axis=0)  # extend dims for iteration
            else:
                xy = inst.xy / logical_unit
            xyl = xy.tolist()
            for i, _xy in enumerate(xyl):
                if np.array_equal(inst.shape, np.array([1, 1])):
                    xy = [[int(xy0) for xy0 in _xy]]
                    lib_export.add_instance(sn, inst.cellname, xy, inst.transform)
                    logging.debug('ExportGDS: Instance:' + inst.name + ' cellname:' + inst.cellname + ' xy:' + str(xy))
                else:  # mosaic
                    xy_mosaic = [[int(_xy[0]), int(_xy[1])],
                                 [int(_xy[0] + inst.shape[0] * (inst.spacing[0] / logical_unit)), int(_xy[1])],
                                 [int(_xy[0]), int(_xy[1] + inst.shape[1] * (inst.spacing[1] / logical_unit))]]
                    lib_export.add_instance_array(sn, inst.cellname, inst.shape[0], inst.shape[1], xy_mosaic,
                                                  inst.transform)
                    logging.debug('ExportGDS: Instance:' + inst.name + ' cellname:' + inst.cellname + ' xy:' + str(_xy)
                                  + ' shape:' + str(inst.shape.tolist()) + ' spacing:' + str(inst.spacing.tolist()))
        with open(filename, 'wb') as stream:
            lib_export.export(stream)

def export_BAG(db, libname, cellname, prj, array_delimiter=['[', ']'], via_tech='cdsDefTechLib'):
    """
    Export specified cell(s) to BagProject

    Parameters
    ----------
    db : laygo.LayoutDB.LayoutDB
        Layout db object
    libname : str
        name of library to be exported
    cellname : list or str
        name of cells to be exported
    prj : BagProject
        bag object to export
    array_delimiter : list or str
        array delimiter for multiple placements
    via_tech : str
        via technology entry for BagProject. Not being used currently because instances are used for via connections
    """
    #TODO: create library if not exist (using the BAG function below)
    #create_or_erase_library(lib_name tech_lib lib_path erase "tttg")
    dsn = db.design
    if isinstance(cellname, str): cellname = [cellname]  # convert to a list for iteration
    for sn in cellname:
        s = dsn[libname][sn]
        logging.debug('ExportBAG: Structure:' + sn)
        inst_list = [];
        rect_list = [];
        via_list = [];
        pin_list = []
        for r in s['rects'].values():  # rect generation
            if r.xy.ndim == 2:
                xy = np.expand_dims(r.xy, axis=0)  # extend dims for iteration
            else:
                xy = r.xy
            for _xy in xy:
                if not (_xy[0]==_xy[1]).all(): #xy0 and xy1 should not be the same
                    rect_list.append({'layer': r.layer, 'bbox': _xy.tolist()})
                    logging.debug('ExportBAG: Rect:' + r.name + ' layer:' + str(r.layer) + ' xy:' + str(_xy.tolist()))
        for p in s['pins'].values():  # pin generation
            if p.xy.ndim == 2:
                xy = np.expand_dims(p.xy, axis=0)  # extend dims for iteration
            else:
                xy = p.xy
            for _xy in xy:
                bx1, bx2 = sorted(_xy[:,0].tolist()) #need to be changed..
                by1, by2 = sorted(_xy[:,1].tolist())
                ll = np.array([bx1, by1])  # lower-left
                ur = np.array([bx2, by2])  # upper-right
                bnd=np.vstack([ll,ur])

                pin_list.append({'pin_name': p.netname, 'layer': p.layer, 'label': p.netname, 'net_name': p.netname,
                                 'bbox': bnd.tolist()})
                logging.debug('ExportBAG: Pin:' + p.name + ' net:' + p.netname + ' layer:' + str(p.layer) +
                              ' xy:' + str(bnd.tolist()))
        for inst in s['instances'].values():  # instance generation
            if np.all(inst.shape>np.array([0, 0])):
                if inst.xy.ndim == 1:
                    xy = np.expand_dims(inst.xy, axis=0)  # extend dims for iteration
                else:
                    xy = inst.xy
                xyl = xy.tolist()
                for i, _xy in enumerate(xyl):
                    if len(xyl) == 1:
                        name = inst.name
                    else:  # multiple placements
                        if isinstance(array_delimiter, list):
                            name = inst.name + array_delimiter[0] + str(i) + array_delimiter[1]
                        else:
                            name = inst.name + array_delimiter + str(i)  # array delimiter is string
                    if inst.shape[0]<1 or inst.shape[1]<1: #unsupported array
                        print("[WARNING] Instance "+inst.name+" ("+ inst.cellname+") has an unsupported shape:" + str(inst.shape))
                    x = inst.spacing[1]
                    inst_list.append({'loc': _xy, 'name': inst.name, 'lib': inst.libname,
                                      'sp_cols': eval(repr(inst.spacing[0])), 'sp_rows': eval(repr(inst.spacing[1])),
                                      'cell': inst.cellname, 'num_cols': int(inst.shape[0]), 'num_rows': int(inst.shape[1]),
                                      'orient': inst.transform, 'view': 'layout'})

        logging.debug('ExportBAG: rect_list:' + str(rect_list))
        logging.debug('ExportBAG: inst_list:' + str(inst_list))
        prj.instantiate_layout(libname, 'layout', via_tech, [[sn, inst_list, rect_list, via_list, pin_list]])

def export_yaml(db, libname, cellname, filename):
    """
        (Not implemented) Export specified cell(s) to a yaml file
        All information shown in db.display() will be saved

        Parameters
        ----------
        db : laygo.LayoutDB.LayoutDB
            design database
        libname : str
            name of library to be exported
        cellname : list or str
            name of cells to be exported
        filename : str
            output filename
    """
    pass

#import functions
def import_GDS(filename=None, layermapfile="default.layermap", instance_libname=None, res=0.005):
    """
    Import layout information from a gds file

    Parameters
    ----------
    filename : gds filename
    layermapfile : layermap filename (can be found in technology library)
    instance_libname : reference library name (libname of instances)
    res : float
        physical resolution of objects

    Returns
    -------
    laygo.layoutDB.layoutDB
        imported layout information
    """
    layermap = _load_layermap(layermapfile)  # load layermap information
    res_exp = int(log10(1 / res) + 1) #rounding resolution

    with open(filename, 'rb') as stream:
        raw_db=readout(stream)
        raw_db=raw_db.popitem()
        libname=raw_db[0]
        lib=raw_db[1] #read gds file

        db = LayoutDB(res=res)
        db.add_library(libname)
        db.sel_library(libname)
        if instance_libname == None:  # if structure reference libname is not set, use library name
            instance_libname = libname

        #construct db
        for structname, struct in lib.items():
            db.add_cell(structname)
            db.sel_cell(structname)
            for rname, rect in struct['rects'].items():
                r = db.add_rect(name=None, xy=rect['xy'],
                                layer=_get_layer_from_layermap(layermap, rect['layer']))
                logging.debug('ImportGDS: Rect:' + r.name + ' layer:' + str(r.layer) +
                              ' xy:' + str(np.round(r.xy, res_exp).tolist()))

            for tname, text in struct['texts'].items():
                t = db.add_text(name=None, text=text['text'],
                                xy=text['xy'],
                                layer=_get_layer_from_layermap(layermap, text['layer']))
                logging.debug('ImportGDS: Text:' + t.name + ' text:' + t.text + ' layer:' + str(t.layer) +
                              ' xy:' + str(np.round(t.xy, res_exp).tolist()))
            for iname, inst in struct['instances'].items():
                if 'shape' in inst: #mosaic
                    inst = db.add_inst(name=None, libname=instance_libname, cellname=inst['cellname'],
                                       shape=inst['shape'], spacing=inst['spacing'], xy=inst['xy'],
                                       transform=inst['transform'])
                else:
                    inst = db.add_inst(name=None, libname=instance_libname, cellname=inst['cellname'],
                                       xy=inst['xy'], transform=inst['transform'])
                logging.debug('ImportGDS: Instance:' + inst.name + ' cellname:' + inst.cellname +
                              ' xy:' + str(np.round(inst.xy, res_exp).tolist()) +
                              ' shape:' + str(np.round(inst.shape, res_exp).tolist()) +
                              ' spacing:' + str(np.round(inst.spacing, res_exp).tolist()))
    return db


def import_BAG(prj, libname, cellname=None, yamlfile="import_BAG_scratch.yaml", res=0.005):
    """
    Import layout information from BagProject object

    Parameters
    ----------
    prj : BagProject
        BAG object
    cellname : str
        cell name to be imported (None if importing entire cells in the library)
    yamlfile : str
        scratch yaml file (parse_cad_layout skill function wrote layout information on the yamlfile)
    res : float
        physical resolution

    Returns
    -------
    laygo.layoutDB.layoutDB
        imported layout information
    """
    if cellname==None: #importing all cells
        prj.impl_db._eval_skill("get_cell_list(\"" + libname + "\" \"" + yamlfile + "\")")
        with open(yamlfile, 'r') as stream:
            ydict = yaml.load(stream)
            celllist=ydict[libname]
    else:
        if isinstance(cellname, list): celllist=cellname
        else: celllist=[cellname]

    db = LayoutDB(res=res)
 
    db.add_library(libname)
    db.sel_library(libname)
    for cn in celllist:
        prj.impl_db._eval_skill("parse_cad_layout(\"" + libname + "\" \"" + cn + "\" \"" + yamlfile + "\")")
        with open(yamlfile, 'r') as stream:
            ydict = yaml.load(stream)
 
        db.add_cell(ydict['cell_name'])
        db.sel_cell(ydict['cell_name'])
 
        for _r_key, _r in ydict['rects'].items():
            r = db.add_rect(name=None, xy=np.array(_r['bBox']), layer=_r['layer'].split())
            logging.debug('ImportGDS: Rect:' + r.name + ' layer:' + str(r.layer) + ' xy:' + str(r.xy.tolist()))
        for _t_key, _t in ydict['labels'].items():
            t = db.add_text(name=None, text=_t['label'], xy=np.array(_t['xy']), layer=_t['layer'].split())
            logging.debug('ImportGDS: Text:' + t.name + ' text:' + t.text + ' layer:' + str(t.layer) +
                          ' xy:' + str(t.xy.tolist()))
        for _i_key, _i in ydict['instances'].items():
            if not 'rows' in _i: _i['rows']=1
            if not 'cols' in _i: _i['cols']=1
            if not 'sp_rows' in _i: _i['sp_rows']=0
            if not 'sp_cols' in _i: _i['sp_cols']=0
            if not 'transform' in _i: _i['transform']='R0'
            inst = db.add_inst(name=None, libname=_i['lib_name'], cellname=_i['cell_name'], xy=np.array(_i['xy']),
                               shape=np.array([_i['cols'], _i['rows']]), spacing=np.array([_i['sp_cols'], _i['sp_rows']]),
                               transform=_i['transform'])
            logging.debug('ImportGDS: Instance:' + inst.name + ' cellname:' + inst.cellname +
                          ' xy:' + str(inst.xy.tolist()) + ' shape:' + str(inst.shape.tolist())
                          + ' spacing:' + str(inst.spacing.tolist()))
    return db

def import_yaml(filename):
    """
        (Not implemented) Import layout information from a yaml file

        Parameters
        ----------
        filename : yaml filename

        Returns
        -------
        layoutDB : imported layout information
    """
    pass


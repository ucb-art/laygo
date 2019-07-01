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

"""GDSII IO Helper functions. Implemented by Eric Jan"""
__author__ = "Eric Jan"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

import struct
from math import *

#code mapping dictionary
_MAP = {
    'HEADER': b'\x00\x02',
    'BGNLIB': b'\x01\x02',
    'LIBNAME': b'\x02\x06',
    'ENDLIB': b'\x04\x00',
    'UNITS': b'\x03\x05',
    'BGNSTR': b'\x05\x02',
    'STRNAME': b'\x06\x06',
    'ENDSTR': b'\x07\x00',

# TYPES OF ELEMENTS
    'BOUNDARY': b'\x08\x00',
    'SREF': b'\x0a\x00',
    'AREF': b'\x0b\x00',
    'TEXT': b'\x0c\x00',

# ELEMENT PARAMETERS
    'SNAME': b'\x12\x06',
    'STRANS': b'\x1a\x01',
    'MAG': b'\x1b\x05',
    'ANGLE': b'\x1c\x05',
    'LAYER': b'\r\x02',
    'TEXTTYPE': b'\x16\x02',
    'DATATYPE': b'\x0e\x02',
    'COLROW': b'\x13\x02',
    'XY': b'\x10\x03',
    'STRING': b'\x19\x06',
    'ENDEL': b'\x11\x00',
    'PRESENTATION': b'\x17\x01',
}

#code remapping dictionary
_REMAP = {}
for (key, value) in _MAP.items():
    globals()[key] = value
    value = struct.unpack('>H', value)[0]
    _REMAP[value] = key
del key, value

# pack functions
# 	length of the packed data + 4(4 hex digits)		+	 the tag from _MAP(4 hex digits)	+	actual packed data
def pack_data(tag, data):
    """data packing function"""
    if _MAP[tag][1]==1: #bits
        return _pack_bits(_MAP[tag], data)
    elif _MAP[tag][1]==2: #short
        return _pack_short(_MAP[tag], data)
    elif _MAP[tag][1]==3: #int
        return _pack_int(_MAP[tag], data)
    elif _MAP[tag][1]==5: #double
        return _pack_double(_MAP[tag], data)
    elif _MAP[tag][1]==6: #text
        return _pack_text(_MAP[tag], data)

def _pack_double(tag, data):
    """pack to double"""
    if type(data) == list:
        s = struct.pack('>{0}Q'.format(len(data)), *[_real_to_int(d) for d in data])
    else:
        s = struct.pack('>{0}Q'.format(1), _real_to_int(data))
    return struct.pack('>{0}H'.format(1), len(s) + 4) + tag + s

def _pack_short(tag, data):
    """pack to short"""
    if type(data) == list:
        s = struct.pack('>{0}h'.format(len(data)), *data)
    else:
        s = struct.pack('>{0}h'.format(1), data)
    return struct.pack('>{0}H'.format(1), len(s) + 4) + tag + s

def _pack_int(tag, data):
    """pack to int"""
    if type(data) == list:
        s = struct.pack('>{0}l'.format(len(data)), *data)
    else:
        s = struct.pack('>{0}l'.format(1), data)
    return struct.pack('>{0}H'.format(1), len(s) + 4) + tag + s

def _pack_bits(tag, data):
    """pack to bits"""
    if type(data) == list:
        s = struct.pack('>{0}H'.format(len(data)), *data)
    else:
        s = struct.pack('>{0}H'.format(1), data)
    # s = struct.pack('>H', data)
    return struct.pack('>{0}H'.format(1), len(s) + 4) + tag + s

def _pack_text(tag, data):
    """pack to text"""
    if type(data) != bytes:
        data = str.encode(data)
    if len(data) % 2 == 1:
        data += b'\0'
    return struct.pack('>{0}H'.format(1), len(data) + 4) + tag + data

def pack_bgn(tag):
    """pack for begin statement"""
    return struct.pack('>{0}H'.format(1), 28) + _MAP[tag] + struct.pack('>{0}H'.format(12), *[0 for x in range(12)])

def pack_no_data(tag):
    """pack for no data entry"""
    return struct.pack('>{0}H'.format(1), 4) + _MAP[tag]

def pack_optional(tag, data, stream):
    """optional packing function"""
    if data == None:
        return
    return stream.write(pack_data(tag, data))

#gds import function
def readout(stream):
    """gds import function to construct a dictionary"""
    rdict=dict()
    rlist=[]
    header = True
    while header:
        header = stream.read(4)
        if not header or len(header) != 4:
            header = False
        else:
            data_size, tag = struct.unpack('>HH', header)
            data_size -= 4  # substract header size
            data = stream.read(data_size)
            if data_size>=0:
                key = _REMAP[tag]
                tag_type = tag & 0xff
                val = None
                if tag_type == 1: #bits
                    val = struct.unpack('>H', data)[0]
                elif tag_type == 2:  # short
                    val = list(struct.unpack('>%dh' % (len(data) // 2), data))
                elif tag_type == 3:  # int
                    val = list(struct.unpack('>%dl' % (len(data) // 4), data))
                elif tag_type == 5:  # double
                    data = struct.unpack('>%dQ' % (len(data) // 8), data)
                    val = list(_int_to_real(n) for n in data)
                elif tag_type == 6:  # text
                    if data.endswith(b'\x00'):
                        val = data.decode("utf-8")[:-1]
                    else:
                        val = data.decode("utf-8")
                rlist.append([key, val])
                if key == 'LIBNAME': #library description starts
                    libname = val
                    rdict[libname]=dict()
                if key == 'UNITS':
                    logical_unit = val[0]
                    physical_unit = val[1]
                if key == 'STRNAME': #structure description starts
                    cellname = val
                    rdict[libname][cellname] = {'rects':dict(), 'texts':dict(), 'instances':dict()}
                    rect_cnt = 0 #reset rect naming counter
                    text_cnt = 0  # reset text naming counter
                    inst_cnt = 0  # reset instance naming counter
                    mirror_trig = 0 # mirroring tigger
                if key == 'BOUNDARY': #rect
                    rectname = str(rect_cnt)
                    rdict_handle = {'layer':[]}
                    rdict[libname][cellname]['rects'][rectname]=rdict_handle
                    rect_cnt += 1
                if key == 'TEXT': #text
                    labelname = str(text_cnt)
                    rdict_handle = {'layer':[]}
                    rdict[libname][cellname]['texts'][labelname]=rdict_handle
                    text_cnt += 1
                if key == 'SREF' or key == 'AREF': #instame
                    inst_name = str(inst_cnt)
                    rdict_handle = {'libname':libname, 'transform':'R0'}
                    rdict[libname][cellname]['instances'][inst_name]=rdict_handle
                    inst_cnt += 1
                if key == 'LAYER':
                    rdict_handle['layer'].append(val[0])
                if key == 'DATATYPE':
                    rdict_handle['layer'].append(val[0])
                if key == 'TEXTTYPE':
                    rdict_handle['layer'].append(val[0])
                if key == 'XY': #xy cooridinate
                    if len(val)==2: #single cooridinate
                        rdict_handle['xy'] = [v * logical_unit for v in val]
                    else:
                        rdict_handle['xy'] = [[val[2*i] * logical_unit, val[2*i+1] * logical_unit]
                                              for i in range(int(len(val)/2))]
                if key == 'COLROW': #col and row
                    rdict_handle['shape']=val
                if key == 'SNAME':
                    rdict_handle['cellname']=val
                if key == 'STRING':
                    rdict_handle['text']=val
                if key == 'STRANS':
                    if val==32768:
                        mirror_trig=1
                if key == 'ANGLE':
                    if mirror_trig==0: #no mirring
                        if val[0]==90:
                            rdict_handle['transform']='R90'
                        if val[0]==180:
                            rdict_handle['transform']='R180'
                        if val[0]==270:
                            rdict_handle['transform']='R270'
                    else: #mirroring
                        if val[0]==0:
                            rdict_handle['transform']='MX'
                        if val[0]==180:
                            rdict_handle['transform']='MY'
    #postprocess
    for cn in rdict[libname]:
        # rect - leave lowerLeft and upperRight corners only
        for rn in rdict[libname][cn]['rects']:
            xy = rdict[libname][cn]['rects'][rn]['xy']
            rdict[libname][cn]['rects'][rn]['xy']=[xy[0], xy[2]]
            #del rdict[libname][cn]['rects'][rn]['xy'][-1]
        # inst - figure out spacing
        for iname in rdict[libname][cn]['instances']:
            if 'shape' in rdict[libname][cn]['instances'][iname]: #mosaic
                xy=rdict[libname][cn]['instances'][iname]['xy']
                xspace = (xy[1][0] - xy[0][0])/rdict[libname][cn]['instances'][iname]['shape'][0]
                yspace = (xy[2][1] - xy[0][1])/rdict[libname][cn]['instances'][iname]['shape'][1]
                rdict[libname][cn]['instances'][iname]['xy'] = xy[0]
                rdict[libname][cn]['instances'][iname]['spacing'] = [xspace, yspace]
    return rdict

def _int_to_real(num):
    """
    FORMAT
        1 sign bit
        7 bit exponent (offset = -64)
        56 bit mantissa (formed as 0.XXXXX)

    VALUE = SIGN * MANTISSA * 16 ^ (EXP)

    """
    if 0x8000000000000000 & num:
        sign=-1
    else:
        sign=1
    mantissa = num & 0x00ffffffffffffff
    exponent = (num >> 56) & 0x7f
    return ldexp(sign * mantissa, 4 * (exponent - 64) - 56)

def _real_to_int(d):
    """
    FORMAT
        1 sign bit
        7 bit exponent (offset = -64)
        56 bit mantissa (formed as 0.XXXXX)

    VALUE = SIGN * MANTISSA * 16 ^ (EXP)

    """
    if d == 0:
        return 0
    elif d < 0:
        sign = 0x8000000000000000
    else:
        sign = 0

    exponent = log(d, 16)
    if exponent < 0:
        exponent = ceil(exponent)
    else:  # exponent > 0
        exponent = floor(exponent) + 1
    d = d / (16 ** exponent)

    mantissa = _getMantissa(d)

    return sign | (int(exponent) + 64) << 56 | mantissa #updated for Python2 compatibility

def _getMantissa(d):
    mantissa = ""
    for _ in range(56):
        d = d * 2
        mantissa += str((int)(d))
        d = d - (int)(d)
    retVal = eval("0b" + mantissa)
    return retVal
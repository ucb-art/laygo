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
The GDSIO module implements classes and functions to export/import full-custom layout in GDSII format.
Implemented by Eric Jan

Example
-------
Refer to the bottom part of GDSIO.py for example.
"""

__author__ = "Eric Jan"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

#TODO: Implement import functions (similar to load in python-gdsii)

from .GDSIOHelper import *
import pprint

class Library:

    def __init__(self, version, name, physicalUnit, logicalUnit):
        """
        Initialize Library object

        Parameters
        ----------
        version : int
            GDSII file version. 5 is used for v5
        name : str
            library name
        physicalUnit : float
            physical resolution
        logicalUnit : float
            logical resolution
        """
        self.version = version
        self.name = name
        self.units = [logicalUnit, physicalUnit]
        self.structures = dict()
        assert physicalUnit > 0 and logicalUnit > 0

    def export(self, stream):
        """
        Export to stream

        Parameters
        ----------
        stream : stream
            file stream to be written
        """
        stream.write(pack_data("HEADER", self.version))
        stream.write(pack_bgn("BGNLIB"))
        stream.write(pack_data("LIBNAME", self.name))
        stream.write(pack_data("UNITS", self.units))
        for strname, struct in self.structures.items():
            struct.export(stream)
        stream.write(pack_no_data("ENDLIB"))

    def add_structure(self, name):
        """
        Add a structure object to library

        Parameters
        ----------
        name : str
            name of structure

        Returns
        -------
        laygo.GDSIO.Structure
            created structure object
        """
        s=Structure(name)
        self.structures[name]=s
        return s

    def add_boundary(self, strname, layer, dataType, points):
        """
        Add a boundary object to specified structure

        Parameters
        ----------
        strname : str
            structure name to insert the boundary object
        layer : int
            layer name of the boundary object
        dataType : int
            layer purpose of the boundary object
        points : 2xn integer array list
            point array of the boundary object
            ex) [[x0, y0], [x1, x1], ..., [xn-1, yn-1], [x0, y0]]

        Returns
        -------
        laygo.GDSIO.Boundary
            created boundary object
        """
        return self.structures[strname].add_boundary(layer, dataType, points)

    def add_instance(self, strname, cellname, xy, transform='R0'):
        """
        Add an instance object to specified structure

        Parameters
        ----------
        strname : str
            structure name to insert the instance
        cellname : str
            instance cellname
        xy : [int, int]
            instance cooridnate
        transform : str
            transform parameter

        Returns
        -------
        laygo.GDSIO.Instance
            created instance object
        """
        return self.structures[strname].add_instance(cellname, xy, transform)

    def add_instance_array(self, strname, cellname, n_col, n_row, xy, transform='R0'):
        """
        Add an instance array to specified structure

        Parameters
        ----------
        strname : str
            structure name to insert the instance
        cellname : str
            instance cellname
        n_col : int
            number of columns
        n_row : int
            number of rows
        xy : [int, int]
            instance coordinate
        transform : str
            transform parameter

        Returns
        -------
        laygo.GDSIO.InstanceArray
            instance array object
        """
        return self.structures[strname].add_instance_array(cellname, n_col, n_row, xy, transform)

    def add_text(self, strname, layer, textType, xy, string, textHeight=100):
        """
        Add a text object to specified structure

        Parameters
        ----------
        strname : str
            structure name to insert the text object
        layer : int
            layer name of the text object
        textType : int
            layer purpose of the text object
        xy : [int, int]
            text coordinate
        string : str
            text string
        textHeight : int
            text height

        Returns
        -------
        laygo.GDSIO.Text
            text object
        """
        return self.structures[strname].add_text(layer, textType, xy, string, textHeight)


class Structure(list):

    def __init__(self, name):
        """
        initialize Structure object

        Parameters
        ----------
        name : str
            structure name
        """
        list.__init__(self)
        self.name = name
        self.elements = []

    def export(self, stream):
        """
        Export to stream

        Parameters
        ----------
        stream : stream
            file stream to be written
        """
        stream.write(pack_bgn("BGNSTR"))
        stream.write(pack_data("STRNAME", self.name))
        for element in self.elements:
            element.export(stream)
        stream.write(pack_no_data("ENDSTR"))

    def add_boundary(self, layer, dataType, points):
        """
        Add a boundary object to structure

        Parameters
        ----------
        layer : int
            layer name
        dataType : int
            layer purpose
        points : list
            layer coordinates

        Examples
        --------
        add_boundary('test', 50, 0, [[1000, 1000], [1000, 0], [0, 0], [0, 1000], [1000, 1000]])

        Returns
        -------
        laygo.GDSIO.Boundary
            generated boundary object
        """
        elem = Boundary(layer, dataType, points)
        self.elements.append(elem)
        return elem

    def add_instance(self, cellname, xy, transform='R0'):
        """
        Add an instance object to structure

        Parameters
        ----------
        cellname : str
            cell name
        xy : [int, int]
            xy coordinate
        transform : str
            transform parameter

        Returns
        -------
        laygo.GDSIO.Instance
            generated instance object
        """
        elem = Instance(cellname, xy, transform)
        self.elements.append(elem)
        return elem

    def add_instance_array(self, cellname, n_col, n_row, xy, transform='R0'):
        """
        Add an instance array object to structure

        Parameters
        ----------
        cellname : str
            cell name
        n_col : int
            number of columns
        n_row : int
            number of rows
        xy : [int, int]
            xy coordinate
        transform : str
            transform parameter

        Examples
        --------
        new_lib.add_instance_array('test2', 'test', 2, 3, [[3000, 3000], [3000 + 2 * 2000, 3000], [3000, 3000 + 3 * 3000]])

        Returns
        -------
        laygo.GDSIO.InstanceArray
            generated instance array object
        """
        elem = InstanceArray(cellname, n_col, n_row, xy, transform)
        self.elements.append(elem)
        return elem

    def add_text(self, layer, textType, xy, string, textHeight=100):
        """
        Add a text object to structure

        Parameters
        ----------
        layer : int
            layer name
        textType : int
            layer purpose
        xy : list
            xy coordinate
        string : str
            text string
        textHeight : int
            text height

        Returns
        -------
        laygo.GDSIO.Text
            generated text object
        """
        elem = Text(layer, textType, xy, string, textHeight)
        self.elements.append(elem)
        return elem

class Element:
    """Base class for GDSIO objects"""
    possible_transform_parameters = {'R0': (None, None),
                                     'R90': (0, 90),
                                     'R180': (0, 180),
                                     'R270': (0, 270),
                                     'MX': (32768, 0),
                                     'MY': (32768, 180)
                                    }
    """dict: transform parameter dictionary"""

    def set_transform_parameters(self, transform):
        """
        initialize transform parameters

        Parameters
        ----------
        transform : str
            transform parameter,
            'R0' : default, no transform,
            'R90' : rotate by 90-degree,
            'R180' : rotate by 180-degree,
            'R270' : rotate by 270-degree,
            'MX' : mirror across X axis,
            'MY' : mirror across Y axis
        """
        if transform not in self.possible_transform_parameters:
            raise Exception("enter a viable transform parameter\npossible_transform_parameters = ['R0', 'R90', 'R180', 'R270', 'MX', 'MY']")
        self.strans, self.angle = self.possible_transform_parameters[transform]


class Boundary (Element):
    """Boundary object for GDSIO"""

    def __init__(self, layer, dataType, points):
        """
        initialize Boundary object

        Parameters
        ----------
        layer : int
            Layer id
        dataType : int
            Layer purpose
        points : list
            xy coordinates for Boundary object
        """
        if len(points) < 2:
         	raise Exception("not enough points")
        if len(points) >= 2 and points[0] != points[len(points) - 1]:
            raise Exception("start and end points different")
        temp_xy = []
        for point in points:
            if len(point) != 2:
                raise Exception("error for point input: " + str(point))
            temp_xy += point
        self.layer = layer
        self.dataType = dataType
        self.xy = list(temp_xy)

    def export(self, stream):
        """
        Export to stream

        Parameters
        ----------
        stream : stream
            File stream to be written
        """
        stream.write(pack_no_data("BOUNDARY"))
        stream.write(pack_data("LAYER", self.layer))
        stream.write(pack_data("DATATYPE", self.dataType))
        stream.write(pack_data("XY", self.xy))
        stream.write(pack_no_data("ENDEL"))



class Instance (Element):
    """Instance object for GDSIO"""

    def __init__(self, sname, xy, transform='R0'):
        """
        initialize Instance object

        Parameters
        ----------
        sname : str
            Instance name
        xy : array
            xy coordinate of Instance Object
        transform : str
            transform parameter,
            'R0' : default, no transform,
            'R90' : rotate by 90-degree,
            'R180' : rotate by 180-degree,
            'R270' : rotate by 270-degree,
            'MX' : mirror across X axis,
            'MY' : mirror across Y axis
        """
        Element.__init__(self)
        self.sname = sname
        l = len(xy)
        if l > 1:
            raise Exception("too many points provided\ninstance should only be located at one point")
        elif l < 1:
            raise Exception("no point provided\ninstance should be located at a point")
        self.xy = list(xy[0])
        Element.set_transform_parameters(self, transform)

    def export(self, stream):
        """
        Export to stream

        Parameters
        ----------
        stream : stream
            File stream to be written
        """
        stream.write(pack_no_data("SREF"))
        stream.write(pack_data("SNAME", self.sname))
        pack_optional("STRANS", self.strans, stream)
        pack_optional("ANGLE", self.angle, stream)
        stream.write(pack_data("XY", self.xy))
        stream.write(pack_no_data("ENDEL"))


class InstanceArray (Element):
    """InstanceArray object for GDSIO"""

    def __init__(self, sname, n_col, n_row, xy, transform='R0'):
        """
        Initialize Instance Array object

        Parameters
        ----------
        sname : str
            InstanceArray name
        n_col: int
            Number of columns
        n_row : int
            Number of rows
        xy : array
            xy coordinates for InstanceArray Object,
            should be organized as: [(x0, y0), (x0+n_col*sp_col, y_0), (x_0, y0+n_row*sp_row)]
        transform : str
            Transform parameter,
            'R0' : default, no transform,
            'R90' : rotate by 90-degree,
            'R180' : rotate by 180-degree,
            'R270' : rotate by 270-degree,
            'MX' : mirror across X axis,
            'MY' : mirror across Y axis
        """
        l = len(xy)
        if l != 3:
            s = "\nxy: [(x0, y0), (x0+n_col*sp_col, y_0), (x_0, y0+n_row*sp_row)]"
            if l > 3:
                s = "too many points provided" + s
            else:
                s = "not enough points provided" + s
            raise Exception(s)
        self.sname = sname
        self.colrow = [n_col, n_row]
        temp_xy = []
        for point in xy:
            if len(point) != 2:
                raise Exception("error for point input: " + str(point))
            temp_xy += point
        self.xy = list(temp_xy)
        # self.xy = [num for pt in xy for num in pt]
        Element.set_transform_parameters(self, transform)

    def export(self, stream):
        """
        Export to stream

        Parameters
        ----------
        stream : stream
            File stream to be written
        """
        stream.write(pack_no_data("AREF"))
        stream.write(pack_data("SNAME", self.sname))
        pack_optional("STRANS", self.strans, stream)
        pack_optional("ANGLE", self.angle, stream)
        stream.write(pack_data("COLROW", self.colrow))
        stream.write(pack_data("XY", self.xy))
        stream.write(pack_no_data("ENDEL"))


class Text (Element):
    """Text object for GDSIO"""

    def __init__(self, layer, textType, xy, string, textHeight=100):
        """
        Initialize Text object

        Parameters
        ----------
        layer : int
            Layer id
        textType : int
            I'm not really sure what this is
        xy : array
            xy coordinates for Text Object
        string : str
            Text object display string
        """
        l = len(xy)
        if l > 1:
            raise Exception("too many points provided\ninstance should only be located at one point")
        elif l < 1:
            raise Exception("no point provided\ninstance should be located at a point")
        self.layer = layer
        self.textType = textType
        self.xy = xy[0]
        self.string = string
        self.strans = 0
        self.mag = textHeight

    def export(self, stream):
        """
        Export to stream

        Parameters
        ----------
        stream : stream
            File stream to be written
        """
        stream.write(pack_no_data("TEXT"))
        stream.write(pack_data("LAYER", self.layer))
        stream.write(pack_data("TEXTTYPE", self.textType))
        stream.write(pack_data("STRANS", self.strans))
        #stream.write(pack_data("ANGLE", self.angle))
        stream.write(pack_data("MAG", self.mag))
        stream.write(pack_data("XY", self.xy))
        stream.write(pack_data("STRING", self.string))
        stream.write(pack_no_data("ENDEL"))

# test
if __name__ == '__main__':
    # Create a new library
    new_lib = Library(5, b'MYLIB', 1e-9, 0.001)

    # Add a new structure to the new library
    struc = new_lib.add_structure('test')
    # Add a boundary object
    new_lib.add_boundary('test', 50, 0, [[100000, 100000], [100000, 0], [0, 0], [0, 100000], [100000, 100000]])

    # Add a new structure to the new library
    struc2 = new_lib.add_structure('test2')
    # Add an instance
    new_lib.add_instance('test2','test', [[0, 0]])
    # Add an array instance
    new_lib.add_instance_array('test2', 'test', 2, 3,
                               [[300000, 300000], [300000 + 2 * 200000, 300000], [300000, 300000 + 3 * 300000]])
    # Test rotating
    # original Instance
    new_lib.add_instance('test2', 'test', [[0, -200000]])
    # rotate by 90
    new_lib.add_instance('test2', 'test', [[200000, -200000]], "R90") #ANGLE 90, STRANS 0
    # rotate by 180
    new_lib.add_instance('test2', 'test', [[400000, -200000]], "R180") #180, 0
    # rotate by 270
    new_lib.add_instance('test2', 'test', [[600000, -200000]], "R270") #270, 0
    # mirror across x-axis
    new_lib.add_instance('test2', 'test', [[800000, -500000]], "MX") #0, 32768
    # mirror across y-axis
    new_lib.add_instance('test2', 'test', [[1000000, -500000]], "MY") #180, 32768
    # Add a text object
    new_lib.add_text('test2', 45, 0, [[0, 0]], 'mytext')

    # Export to a GDS file
    with open('testGDS.gds', 'wb') as stream:
        new_lib.export(stream)

    # Import a GDS file
    with open('testGDS.gds', 'rb') as stream:
        pprint.pprint(readout(stream))


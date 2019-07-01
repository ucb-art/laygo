
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
"""ADC library
"""
import laygo
import numpy as np
import os
import yaml
#import logging;logging.basicConfig(level=logging.DEBUG)

def generate_clkdis_hcell(laygen, objectname_pfix, logictemp_lib, working_lib, grid, origin=np.array([0, 0]), ratio=2, trackm=4, 
        metal_v1=5, metal_h=4, metal_v2=5, pitch_h=100, len_v1=10, len_h=None, len_v2=10, offset=0, in_pin=0, out_pin=0, out_label=''):
    """generate htree cell """

    if len_h == None:
        len_h = pitch_h*(ratio-1)
    else:
        if len_h < pitch_h*(ratio-1):
            print("horizental length is too small, please redefine it!")
            return
    

    if (metal_v1-metal_h == -1):
        rg1 = grid['rg_m'+str(metal_v1)+'m'+str(metal_h)]
    elif(metal_h-metal_v1 == -1):
        rg1 = grid['rg_m'+str(metal_h)+'m'+str(metal_v1)]
    else:
        print('Some error with metal assignment!')
        return
    #print(rg1)

    if (metal_h-metal_v2 == -1):
        rg2 = grid['rg_m'+str(metal_h)+'m'+str(metal_v2)]
    elif(metal_v2-metal_h == -1):
        rg2 = grid['rg_m'+str(metal_v2)+'m'+str(metal_h)]
    else:
        print('Some error with metal assignment!')
        return
    
    len_v1 = laygen.grids.get_absgrid_coord_y(gridname=rg1, y=len_v1)
    len_h = laygen.grids.get_absgrid_coord_x(gridname=rg1, x=len_h)
    len_v2 = laygen.grids.get_absgrid_coord_y(gridname=rg2, y=len_v2)
    #print(rg2)

    ## vertical tracks 1 and vias
    for i in range(trackm):
        vp1x=laygen.route(None, laygen.layers['metal'][metal_v1], xy0=np.array([origin[0]+2*i, origin[1]]), xy1=np.array([origin[0]+2*i, origin[1]-len_v1-2*trackm+2]), gridname0=rg1)
        if in_pin==1:
            laygen.boundary_pin_from_rect(vp1x, gridname=rg1, name='WI_' + str(i),
                                          layer=laygen.layers['pin'][metal_v1], size=2, direction='top',
                                          netname='W')
        for j in range(trackm):
            laygen.via(None, xy=np.array([origin[0]+2*i,origin[1]-len_v1-2*j]), gridname=rg1)
    
    ## horizental tracks  
    for i in range(trackm):
        laygen.route(None, laygen.layers['metal'][metal_h], xy0=np.array([origin[0]-len_h/2+offset, origin[1]-len_v1-2*i]), xy1=np.array([origin[0]+len_h/2+2*trackm-2+offset, origin[1]-len_v1-2*i]), gridname0=rg1)

    ## vertical tracks 2
    out_xy = []
    for k in range(ratio):
        for i in range(trackm):
            vp2x=laygen.route(None, laygen.layers['metal'][metal_v2], xy0=np.array([origin[0]+2*i-(ratio-1)/2*len_h+k*len_h+offset, origin[1]-len_v1]), 
                xy1=np.array([origin[0]+2*i-(ratio-1)/2*len_h+k*len_h+offset, origin[1]-len_v1-2*trackm+2-len_v2]), gridname0=rg2)
            if out_pin==1:    
                laygen.boundary_pin_from_rect(vp2x, gridname=rg1,
                                              name='WO' + str(out_label) + '_' + str(k) + '_' + str(i),
                                              layer=laygen.layers['pin'][metal_v1], size=2, direction='bottom',
                                              netname='W')
                #print('WO'+str(out_label)+'_'+str(k)+'_'+str(i))
            for j in range(trackm):
                laygen.via(None, xy=np.array([origin[0]+2*i-(ratio-1)/2*len_h+k*len_h+offset,origin[1]-len_v1-2*j]), gridname=rg1)
        out_xy.append(np.array([origin[0]-(ratio-1)/2*len_h+k*len_h+offset, origin[1]-len_v1-2*trackm+2-len_v2]))

    #print(out_xy)
    return out_xy

def generate_clkdis_htree(laygen, objectname_pfix, logictemp_lib, working_lib, grid, origin=np.array([0, 0]), level=2, trackm=2, ratio=[2, 2], metal_v1=[5, 5],
        metal_h=[4, 4], metal_v2=[5, 5], metal=[5, 5], pitch_h=[20.16*2, 20.16], len_v1=[1, 1], len_h=[None, None], len_v2=[1, 1], offset=[0, 0]):
    #grid, level, ratio, metal_v1, metal_h, metal_v2, pitch_h, len_v1, len_v2, offset):
    """generate htree"""

    if ( len(params['metal_v1'])!=params['level'] or len(params['metal_h'])!=params['level'] or len(params['metal_v2'])!=params['level'] or 
            len(params['pitch_h'])!=params['level'] or len(params['len_v1'])!=params['level'] or len(params['len_h'])!=params['level']or 
            len(params['len_v2'])!=params['level'] ):
        print("\nThere's some error with your array size. Please check it!\n")
        return

    cell_params=[]
    for i in range(params['level']):
        params0 = dict( 
            #track number
            trackm = params['trackm'],
            #divide ratio
            ratio = params['ratio'][i],
            #metal layer
            metal_v1 = params['metal_v1'][i],
            metal_h = params['metal_h'][i], 
            metal_v2 = params['metal_v2'][i], 
            #pitch between output
            pitch_h = params['pitch_h'][i], 
            #length
            len_v1 = params['len_v1'][i], 
            len_h = params['len_h'][i],
            len_v2 = params['len_v2'][i],
            #offset
            offset = params['offset'][i],
            #in_pin
            in_pin = 0,
            #out_pin
            out_pin = 0,
            #out_label
            out_label='',
        )
        ## Changing in/out pins
        if i==0:
            if i== params['level']-1:
                params0['in_pin'] = 1
                params0['out_pin'] = 1
            else:
                params0['in_pin'] = 1
                params0['out_pin'] = 0
        elif i== params['level']-1:
            params0['in_pin'] = 0
            params0['out_pin'] = 1
        else: 
            params0['in_pin'] = 0
            params0['out_pin'] = 0
        cell_params.append(params0)

    for k in range(params['level']):
        #Calculat how many leaves at level k
        if k == 0:
            level_ratio = 1
            old_orig_xy = [np.array([0, 0]),]
        else:
            level_ratio = level_ratio*params['ratio'][k-1]
            old_orig_xy = orig_xy

        orig_xy = []
        for i in range(level_ratio):
            if k==params['level']-1:
                cell_params[k]['out_label']=str(i)

            orig_xy0 = generate_clkdis_hcell(laygen, objectname_pfix='HCELL_'+str(k)+'_'+str(i), logictemp_lib=logictemplib, working_lib=workinglib, grid=grid, 
                    origin=old_orig_xy[i], **cell_params[k])
            #print(orig_xy0)
            for orig in orig_xy0:
                orig_xy.append(orig)
    

if __name__ == '__main__':
    laygen = laygo.GridLayoutGenerator(config_file="laygo_config.yaml")

    import imp
    try:
        imp.find_module('bag')
        laygen.use_phantom = False
    except ImportError:
        laygen.use_phantom = True


    tech=laygen.tech
    utemplib = tech+'_microtemplates_dense'
    logictemplib = tech+'_logic_templates'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)

    # library load or generation
    workinglib = 'clk_dis_generated'
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
    if os.path.exists(workinglib + '.yaml'):  # generated layout file exists
        laygen.load_template(filename=workinglib + '.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    #grid
    grid = dict(
        pg = 'placement_basic', #placement grid
        rg_m1m2 = 'route_M1_M2_cmos',
        rg_m1m2_thick = 'route_M1_M2_basic_thick',
        rg_m2m3 = 'route_M2_M3_cmos',
        rg_m2m3_thick = 'route_M2_M3_thick',
        rg_m2m3_thick2 = 'route_M2_M3_thick2',
        rg_m3m4 = 'route_M3_M4_basic',
        rg_m3m4_dense = 'route_M3_M4_dense',
        rg_m4m5 = 'route_M4_M5_basic',
        rg_m5m6 = 'route_M5_M6_basic',
        rg_m6m7 = 'route_M6_M7_basic',
        rg_m1m2_pin = 'route_M1_M2_basic',
        rg_m2m3_pin = 'route_M2_M3_basic',
    )
    #parameters
    pitch_x=laygen.get_template_xy(name='clk_dis_viadel_cell', libname=workinglib)[0]
    params = dict(
        #stage
        level = 2,
        #track number
        trackm = 12,
        #divide ratio
        ratio = [2, 2],
        #metal layer
        metal_v1 = [5, 5],
        metal_h = [4, 4], 
        metal_v2 = [5, 5], 
        #pitch between output
        #pitch_h = [100, 50],    #um
        pitch_h = [pitch_x*2, pitch_x],    #um
        #length
        len_v1 = [1, 0.5],        #um 
        len_h = [None, None],   #um
        len_v2 = [0.5, 1],        #um
        #offset
        offset = [0, 0],        #um
    )
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        #load parameters
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        lvl=int(np.log2(specdict['n_interleave']/2))
        ratio=2
        if lvl==0:
            lvl=1
            ratio=1
        params = dict(
            #stage
            level = lvl,
            #track number
            trackm = 24,
            #divide ratio
            ratio = [ratio]*lvl,
            #metal layer
            metal_v1 = [5]*lvl,
            metal_h = [4]*lvl, 
            metal_v2 = [5]*lvl,
            #pitch between output
            #pitch_h = [100, 50],    #um
            pitch_h = [pitch_x*int(2**(lvl-i-1)) for i in range(lvl)],
            #length
            len_v1 = [1]*lvl,        #um 
            len_h = [None]*lvl,   #um
            len_v2 = [1]*lvl,        #um
            #offset
            offset = [0]*lvl,        #um
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
        params['trackm']=sizedict['clk_dis_htree']['m_track']

    print(workinglib)

    mycell_list=[]

    cellname='clk_dis_htree'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_clkdis_htree(laygen, objectname_pfix='HTREE', logictemp_lib=logictemplib, working_lib=workinglib, grid=grid, **params)
    laygen.add_template_from_cell()

    print(mycell_list)

    laygen.save_template(filename=workinglib+'.yaml', libname=workinglib)
    #bag export, if bag does not exist, gds export
    import imp
    try:
        imp.find_module('bag')
        import bag
        prj = bag.BagProject()
        for mycell in mycell_list:
            laygen.sel_cell(mycell)
            laygen.export_BAG(prj, array_delimiter=['[', ']'])
    except ImportError:
        laygen.export_GDS('output.gds', cellname=mycell_list, layermapfile=tech+".layermap")  # change layermapfile

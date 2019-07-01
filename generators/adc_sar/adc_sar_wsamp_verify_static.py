# -*- coding: utf-8 -*-

import pprint

import bag
#from laygo import *
import laygo
import numpy as np
import yaml
from math import log10, sin, pi
import matplotlib.pyplot as plt

#parameters
lib_name = 'adc_sar_templates'
cell_name = 'sar_wsamp_9b'
impl_lib = 'adc_sar_generated'
tb_lib = 'adc_sar_testbenches'
tb_cell = 'sar_wsamp_9b_tb_tran_static'
load_from_file = True
verify_lvs = False
extracted = False
verify_tran = False
verify_tran_analyze = True
yamlfile_system_input = "adc_sar_spec.yaml"
#yamlfile_system_output="adc_sar_dsn_system_output.yaml"
#csvfile_tf_raw = "adc_sar_tf_raw.csv"
#csvfile_tf_th = "adc_sar_tf_th.csv"
#csvfile_cal = "adc_sar_calcode.csv"
#csvfile_tf_raw = "adc_vtc_pe_slow_1.2V_1mV_sch.csv"
#csvfile_tf_raw = "adc_vtc_pe_faston_1mV_sch.csv"
#csvfile_tf_raw = "adc_vtc_wope_slow_2xsampcapdrv_1mV_sch.csv"
csvfile_tf_raw = "adc_vtc_wope_slow_1mV_sch.csv"
#csvfile_tf_raw = "adc_vtc_titest_1mV_sch.csv"
#csvfile_tf_raw = "adc_vtc_pe_2xcap_1mV_ext.csv"
csvfile_tf_th = "adc_sar_tf_th.csv"
csvfile_cal = "adc_sar_calcode.csv"

#spec
if load_from_file==True:
    with open(yamlfile_system_input, 'r') as stream:
        sysdict = yaml.load(stream)
    cell_name = 'sar_wsamp_'+str(sysdict['n_bit'])+'b'
    tb_cell = 'sar_wsamp_'+str(sysdict['n_bit'])+'b_tb_tran_static'
    n_bit=sysdict['n_bit']
    n_bit_cal=sysdict['n_bit_cal']       
    delay=sysdict['n_interleave']/sysdict['fsamp']
    per=sysdict['n_interleave']/sysdict['fsamp']
    skew_rst=0
    vdd=sysdict['vdd']
    v_in=sysdict['v_in']             
    vicm=sysdict['v_in']/2
    vidm=sysdict['v_in']
    vref0=0
    vref1=sysdict['v_in']/2
    vref2=sysdict['v_in']
else:
    n_bit=9
    n_bit_cal=8
    delay=1e-9
    per=1e-9
    skew_rst=0
    vdd=0.8
    v_in=0.3
    vicm=0.15
    vidm=0.3
    vref0=0
    vref1=sysdict['v_in']/2
    vref2=sysdict['v_in']

#print('creating BAG project')
#prj = bag.BagProject()

#lvs
if verify_lvs==True:
    # run lvs
    print('running lvs')
    lvs_passed, lvs_log = prj.run_lvs(impl_lib, cell_name)
    if not lvs_passed:
        raise Exception('oops lvs died.  See LVS log file %s' % lvs_log)
    print('lvs passed')

# transfer curve test
if verify_tran==True:
    # transient test
    print('creating testbench %s__%s' % (impl_lib, tb_cell))
    tb = prj.create_testbench(tb_lib, tb_cell, impl_lib, cell_name, impl_lib)
    tb.set_parameter('pdelay', delay)
    tb.set_parameter('pper', per)
    tb.set_parameter('pskew_rst', skew_rst)
    tb.set_parameter('pvdd', vdd)
    tb.set_parameter('pvicm', vicm)
    tb.set_parameter('pvref0', vref0)
    tb.set_parameter('pvref1', vref1)
    tb.set_parameter('pvref2', vref2)
    #tb.set_parameter('pvidm', vidm)
    #tb.set_sweep_parameter('pvidm', values=[-1*vidm+i*vidm/10 for i in range(21)])
    #tb.set_sweep_parameter('pvidm', values=[-1*vidm+i*vidm/10 for i in range(3)])
    tb.set_sweep_parameter('pvidm', values=[-1*vidm+i*vidm/(2**(n_bit+1)) for i in range(2**(n_bit+1+1))])
 
    tb.set_simulation_environments(['tt'])

    if extracted:
        #tb.set_simulation_view(impl_lib, cell_name, 'calibre')
        #capdac only
        tb.set_simulation_view(impl_lib, 'sar_'+str(n_bit)+'b_IAFE0_ICAPM0', 'calibre')

    tb.update_testbench()

    print('running simulation')
    tb.run_simulation()

    print('loading results')
    results = bag.data.load_sim_results(tb.save_dir)
    vin=results['pvidm']
    adcout=results['adccode']
    X=np.vstack((vin,adcout)).transpose()
    np.savetxt(csvfile_tf_raw, X, fmt=['%f', '%d'], delimiter=', ')

if verify_tran_analyze==True:
    #load vin/dout curve
    csv = np.genfromtxt(csvfile_tf_raw, delimiter=",")
    #vin = csv[1:,0]
    #adcout = csv[1:,1]
    vin = csv[:,0]
    adcout = csv[:,1]
    plt.figure()
    plt.plot(vin, adcout)
    plt.show(block=False)
    plt.grid()
    plt.title('ADC raw transfer function')
    plt.xlabel('vin')
    plt.ylabel('adcout')
    #extract code map
    #code_th=adcout[0]
    code_th=0
    code_list = []
    vth_list = []
    #extract code map
    for i, v in enumerate(vin):
        if adcout[i]>code_th:
            code_list.append(int(code_th))
            vth_list.append(0.5*(vin[i-1]+vin[i]))
            code_th=adcout[i]
    #save and plot
    X=np.vstack((vth_list, code_list)).transpose()
    np.savetxt(csvfile_tf_th, X, fmt=['%f', '%d'], delimiter=', ')
    plt.figure()
    plt.plot(vth_list, code_list)
    plt.show(block=False)
    plt.grid()
    plt.title('ADC raw transfer function (threshold)')
    plt.xlabel('vin')
    plt.ylabel('code_th') 
    
    #estimate input range calibration due to gain error
    delta_avg=(vth_list[-1]-vth_list[0])/2**(n_bit-1)
    v_in0=v_in
    v_in=0.5*(-vth_list[0]+vth_list[-1])-delta_avg
    print("your adjusted input swing is:", v_in)
    
    #make a calibration map
    v_bit_cal=2*v_in/2**n_bit_cal
    calmap_in_th=[]
    calmap_out=[]
    for i, c in enumerate(code_list):
        calout=2**n_bit_cal-1
        v_th = vth_list[i]
        trig=0
        for c2 in range(2**n_bit_cal):
            v_th_cal = -v_in+v_bit_cal*(c2+1)
            if v_th < v_th_cal and trig==0:
                calout = c2
                #if abs(v_th-v_th_cal) < abs(v_th-v_th_cal+v_bit_cal):
                #    calout = c2
                #else:
                #    calout = c2 - 1 # pick one is closer than the other
                trig=1
        while len(calmap_in_th)-1 < c:
            calmap_in_th.append(len(calmap_in_th))
            calmap_out.append(calout)
    X1=np.array(calmap_in_th)
    X2=np.array(calmap_out)
    calmap=np.vstack((X1,X2)).transpose()
    np.savetxt(csvfile_cal, calmap, fmt='%d', delimiter=', ')
    plt.figure()
    plt.plot(calmap[:,0], calmap[:,1])
    plt.show(block=False)
    plt.grid()
    plt.title('ADC calibration map function')
    plt.xlabel('calmap_in_th')
    plt.ylabel('calmap_out') 
    
    #evaluate low freq ENOB
    sin_freq=1/(2**(n_bit_cal+2+2))*3
    sin_time_bin=np.arange(2**(n_bit_cal+2+2))
    #input signal
    vsin=0.99*v_in*np.sin(2*pi*sin_freq*sin_time_bin)
    sin_fft=np.fft.fft(vsin)
    sin_fft_dB=20*np.log10(np.absolute(sin_fft))
    sin_fft_dBc=sin_fft_dB-max(sin_fft_dB)
    freq_array = np.fft.fftfreq(sin_time_bin.shape[-1])
    #ideal n_bit_cal adc
    sinq_ideal=[]
    for v in vsin:
        sinq_val=0
        for c in range(2**n_bit_cal):
            v_comp = -v_in+v_bit_cal*c
            if v >= v_comp:
                sinq_val=c
        sinq_ideal.append(sinq_val)
    sinq_ideal_fft=np.fft.fft(sinq_ideal-np.average(sinq_ideal))
    sinq_ideal_fft_abs=np.absolute(sinq_ideal_fft)
    sinq_ideal_fft_dB=20*np.log10(np.absolute(sinq_ideal_fft))
    sinq_ideal_fft_dBc=sinq_ideal_fft_dB-max(sinq_ideal_fft_dB)
    #sndr&enob
    sinq_ideal_fft_argmax=np.argmax(sinq_ideal_fft_abs)
    sinq_ideal_fft_sigpwr=2*sinq_ideal_fft_abs[sinq_ideal_fft_argmax]**2 #negative freq)
    sinq_ideal_fft_totpwr=np.sum(np.square(sinq_ideal_fft_abs))
    sinq_ideal_SNDR=20*np.log10(sinq_ideal_fft_sigpwr/(sinq_ideal_fft_totpwr-sinq_ideal_fft_sigpwr))/2 #/2 from sine
    sinq_ideal_ENOB=(sinq_ideal_SNDR-1.76)/6.02
    print('ideal SNDR', sinq_ideal_SNDR)
    print('ideal ENOB', sinq_ideal_ENOB)

    #simulated adc
    sinq=[]
    sinq_vth=[]
    sinq_code_raw=[]
    sinq_code=[]
    for v in vsin:
        sinq_vth_val=min(vth_list)
        sinq_code_raw_val=0
        for i, vth in enumerate(vth_list):
            if v >= vth:
                sinq_vth_val=vth
                sinq_code_raw_val=code_list[i]
        sinq_vth.append(sinq_vth_val)
        sinq_code_raw.append(sinq_code_raw_val)
        #convert to calibrated code
        sinq_code_val=0
        for i, c in enumerate(calmap_in_th):
            if sinq_code_raw_val > c:
                sinq_code_val=calmap_out[i]
        sinq_code.append(sinq_code_val)
        #print(v,sinq_vth_val,sinq_code_raw_val,sinq_code_val)
    sinq_fft=np.fft.fft(sinq_code-np.average(sinq_code))
    sinq_fft_abs=np.absolute(sinq_fft)
    sinq_fft_dB=20*np.log10(np.absolute(sinq_fft))
    sinq_fft_dBc=sinq_fft_dB-max(sinq_fft_dB)
    #sndr&enob
    sinq_fft_argmax=np.argmax(sinq_fft_abs)
    sinq_fft_sigpwr=2*sinq_fft_abs[sinq_fft_argmax]**2 #negative freq)
    sinq_fft_totpwr=np.sum(np.square(sinq_fft_abs))
    sinq_SNDR=20*np.log10(sinq_fft_sigpwr/(sinq_fft_totpwr-sinq_fft_sigpwr))/2 #/2 from sine
    sinq_ENOB=(sinq_SNDR-1.76)/6.02
    print('SNDR', sinq_SNDR)
    print('ENOB', sinq_ENOB)

    fft_n=np.size(freq_array)/2
    #fft_n=np.size(freq_array)
    plt.figure()
    #plt.plot(sin_time_bin, vsin)
    plt.plot(sin_time_bin, sinq_ideal, label='ideal 8bit')
    #plt.plot(sin_time_bin, sinq_vth)
    plt.plot(sin_time_bin, sinq_code, label='design')
    #plt.plot(sin_time_bin, sinq_code_raw)
    #plt.plot(freq_array[:fft_n], sin_fft_dBc[:fft_n])
    plt.show(block=False)
    plt.legend()
    plt.grid()
    strtitle='Time domain, SNDR:'+str(sinq_SNDR)+', ENOB:'+str(sinq_ENOB)
    plt.title(strtitle)
    plt.xlabel('time')
    plt.ylabel('code') 
    plt.figure()
    plt.plot(freq_array[:fft_n], sinq_ideal_fft_dBc[:fft_n], label='ideal 8bit')
    plt.plot(freq_array[:fft_n], sinq_fft_dBc[:fft_n], label='design')
    plt.show(block=False)
    plt.legend()
    plt.grid()
    strtitle='Frequency domain, SNDR:'+str(sinq_SNDR)+', ENOB:'+str(sinq_ENOB)
    plt.title(strtitle)
    plt.xlabel('f/fs')
    plt.ylabel('dB') 
    #plt.ylim([-90, 0])


##write to file
#with open(yamlfile_system_output, 'r') as stream:
#    outdict = yaml.load(stream)
#outdict['v_in_static']=v_in
#with open(yamlfile_system_output, 'w') as stream:
#    yaml.dump(outdict, stream)

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

""" bug fix script
"""
import numpy as np
from math import log
import yaml
import os, sys
from os import walk
import re

resdir='./results'
if not os.path.exists(resdir):
    os.makedirs(resdir)

flist = []
filename_self =  os.path.basename(sys.argv[0])
for (dirpath, dirnames, filenames) in walk('.'):
    for fn in filenames:
        if (fn.endswith('.py')) and (not fn=='__init__.py') and (not fn==filename_self):
            flist.append(fn)
    break
print('BagModule scripts')
print(flist) 

for fn in flist: #[flist[1]]:
    print(fn+" processing")
    f = open(fn, 'r') #readout file
    fibuf = f.readlines()
    f.close()
    fobuf = []
    insert_trig = 0 #trigger for putting stings
    for line in fibuf:
        fobuf.append(line)
        tkn=re.split(" +|, +|\):", line.strip()) #split line into tokens
        if len(tkn)>=2 and tkn[1] == 'design(self': #design function
            print(line, tkn)
            insertbuf=[]
            for t in tkn[2:]:
                insert_trig=1
                pname=t.split('=')[0] #remove default argument setter
                if not pname=='':
                    words='        self.parameters[\''+pname+'\'] = '+pname+'\n'
                    print(words)
                    insertbuf.append(words)
        if insert_trig==1 and len(tkn)>=1 and tkn[0] == '\"\"\"': #code insertion point
            for words in insertbuf:
                fobuf.append(words)
            insert_trig=0
    f = open('./results/'+fn, 'w')
    f.writelines(fobuf)
    f.close()
'''
    f = open(libfile_full, 'w')
    lop=dcorner[cn]['operating_conditions']
    lcap=dcorner[cn]['cap']
    lrise_prop=dcorner[cn]['rise_prop']
    lfall_prop=dcorner[cn]['fall_prop']
    lrise_tran=dcorner[cn]['rise_tran']
    lfall_tran=dcorner[cn]['fall_tran']

    #header
    f_header = open(libfile_header, 'r')
                pn_head, pn_tail = pn.split('[')
'''

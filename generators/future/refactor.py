# refactor
import re, os

def convert_pos_to_named(filename_i, filename_o, func_name):
    """
        Convert positional arguments to named arguments for further refactoring under following assumptions.
        1. Refactoring functions defined in GridLayoutGenerator.py
        2. GridLayoutGenerator is instantiated as laygen
    """
    # GridLayoutGenerator parameters
    laygen_path="../../GridLayoutGenerator.py"
    laygen_instance="laygen"

    # read function definition
    trig=0 #trigger for multiline definitions
    with open(laygen_path, 'r') as f:
        lines_s = f.readlines()
        # read function definition
        for l in lines_s:
            if 'def '+func_name+'(' in l:  # end of function call
                l_token_arg = [] #tokens for arguments
                trig = 1  #trig to readout arguments over multiple lines
                depth = 0 # depth variable to figure out argument definitions
                print("function " + func_name + " definition detected. code snapshot: " + l[:-1])
            if trig == 1:
                s_buf=''
                for c in l:
                    if c==' ' and s_buf=='': #ignore spaces between commas and indents
                        pass
                    else:
                        if c==')' or c==']': #exit bracket decrease depth
                            if depth == 1: #end of definition
                                if s_buf=='': #some functions have something like , ):
                                    pass
                                else:
                                    l_token_arg.append(s_buf)
                                    s_buf = ''
                                trig = 0
                            depth -= 1
                        if c==',' and depth == 1: #if the comma is argument splitter,
                            l_token_arg.append(s_buf)
                            s_buf=''
                        else:
                            if depth >= 1:
                                s_buf += c
                        if c=='(' or c=='[': #go inside bracket. increase depth
                            depth += 1
                if trig == 0:
                    l_token_arg=l_token_arg[1:] #exclude self
                    for i, item in enumerate(l_token_arg):
                        if '=' in item: #has a default value
                            l_token_arg[i] = re.split("=", item)[0]
                    if trig == 0:
                        print("function "+func_name+" definition loaded. arguments: "+str(l_token_arg))

    # read source code
    with open(filename_i, 'r') as f:
        lines_i = f.readlines()
    print("file " + filename_i + " loaded")

    # refactor
    trig = 0  # trigger for multiline call
    depth = 0 # depth variable to find out arguments
    lines_o = [] # output buffer
    for i, l in enumerate(lines_i):
        if laygen_instance + '.' + func_name in l:
            trig = 1
            l_header = l.split(laygen_instance + '.' + func_name)[0]
            depth = -1*(l_header.count('(') + l_header.count('[')) + (l_header.count(')') + l_header.count(']')) #if brackets are before the function call, need to decrease initial depth value
            print("function " + func_name + " call detected in file: "+ filename_i + ", in line:"+ str(i) +" code snapshot: " + l[:-1])
        if trig == 1:
            l_vanilla = l #copy original one
            l_refac = '' #refactored line
            s_buf = ''   #string buffer to store arguments
            arg_index = 0 #argument index to map positional arguments
            trig_refac_arg_readout = 0  # trigger to readout arguments
            for c in l:
                #mystr="    rect_xy_list = [laygen.get_rect_xy(name=r.name, gridname=gridname, sort=True) for r in rect_list]"
                #mystr="    laygen.pin(name='VREF_M5_2<2>', layer=laygen.layers['pin'][5], xy=laygen.get_rect_xy(rvref2v2.name, gridname=rg_m4m5), gridname=rg_m4m5, netname='VREF<2>')"
                #mystr="    diffpair_origin = laygen.get_inst_xy(itapbl0.name, pg) + laygen.get_template_xy(itapbl0.cellname, pg) * np.array([0, 1])"
                #mystr="    org=origin+laygen.get_inst_xy('I'+objectname_pfix+'INV1', pg)+ laygen.get_template_xy(i1.cellname, pg) * np.array([1, 0])"
                #if l_vanilla.startswith(mystr):
                #    print(c, depth, trig_refac_arg_readout, trig_refac_arg, s_buf)
                trig_copy = 1  # trigger to copy c to l_refac without modifications
                trig_refac_arg = 0 # trigger to refactor arguments after readout
                if c == ' ' and s_buf == '':  # ignore spaces between commas and indents
                    pass
                else:
                    if c == ')' or c == ']':  # exit bracket decrease depth
                        if depth == 1:  # end of function call
                            if s_buf == '':  # some functions have something like , ):
                                pass
                            else:
                                if trig_refac_arg_readout == 1:
                                    trig_refac_arg = 1
                            trig = 0 #end of function call
                            trig_refac_arg_readout = 0  # reset readout trigger
                        depth -= 1
                    if c == ',' and depth == 1 and trig_refac_arg_readout==1:  # if the comma is argument splitter,
                        trig_refac_arg = 1
                    elif c == '\n' and depth == 1: # newline
                        if s_buf == '': #no captured argument, the start of function call or captured well - just copy and paste
                            pass
                        else: # maybe the end of function call - do refactoring
                            if trig_refac_arg_readout == 1:
                                trig_refac_arg = 1
                    else:
                        if (depth >= 1) and (trig_refac_arg_readout == 1):
                            s_buf += c
                            trig_copy = 0
                    if c == '(' or c == '[':  # go inside bracket. increase depth
                        depth += 1
                        if (depth == 1) and (l_refac[(-1*len(func_name)):]==func_name):
                            trig_refac_arg_readout = 1 #found the right spot. Start readout
                if trig_refac_arg == 1: #s_buf filled, do refactoring
                    if '=' in s_buf: #named argument, just copy and paste
                        l_refac += s_buf
                    else: #positional argument!
                        l_refac += l_token_arg[arg_index] + ' = ' + s_buf
                        arg_index += 1 #move to next argument
                    s_buf = '' #flush s_buf
                if trig_copy == 1:
                    l_refac += c
                #if c=='\n':
                #    print('newline', depth, trig_copy)
            print("   before refactoring: "+l_vanilla[:-1]) #remove newline for neat plotting
            print("    after refactoring: "+l_refac[:-1])
            #print(len(l),len(l_refac))
            lines_o.append(l_refac) #
        else: #normal codes, just copy and paste
            lines_o.append(l)

    # write source code
    with open(filename_o, 'w') as f:
        for l in lines_o:
            f.write(l)

def convert_pin_from_rect_to_pin(filename_i, filename_o):
    """
        Convert obsolete pin_from_rect function call to pin.
        Assumes the original function calls are refactored to have positional arguments only.
        ex)
        laygen.pin_from_rect(name='A', layer=laygen.layers['pin'][2], rect=ra, gridname=rg12)
        will be converted to
        laygen.pin(name='A', gridname=rg12, refobj=ra)
        parameter mapping)
        name -> name
        layer -> layer or discard(?)
        rect -> refobj
        gridname -> gridname
        netname -> netname

    """
    # GridLayoutGenerator parameters
    laygen_instance = "laygen"
    func_name = "pin_from_rect"
    func_name_new = "pin"
    param_map = {
        'name':'name',
        'layer':'layer',
        'rect':'refobj',
        'gridname':'gridname',
        'netname':'netname'
        }

    # read source code
    with open(filename_i, 'r') as f:
        lines_i = f.readlines()
    print("file " + filename_i + " loaded")

    # refactor
    trig = 0  # trigger for multiline call
    depth = 0  # depth variable to find out arguments
    lines_o = []  # output buffer
    for i, l in enumerate(lines_i):
        if laygen_instance + '.' + func_name in l:
            trig = 1
            l_header = l.split(laygen_instance + '.' + func_name)[0]
            depth = -1 * (l_header.count('(') + l_header.count(
                '['))  # if brackets are before the function call, need to decrease initial depth value
            print("function " + func_name + " call detected in file: " + filename_i + ", in line:" + str(
                i) + " code snapshot: " + l[:-1])
        if trig == 1:
            l_vanilla = l # copy original one
            l = l.replace(laygen_instance + '.' + func_name, laygen_instance + '.' + func_name_new)
            l_refac = ''  # refactored line
            s_buf = ''  # string buffer to store arguments
            for c in l:
                trig_copy = 1  # trigger to copy c to l_refac without modifications
                trig_refac_arg = 0  # trigger to refactor arguements after readout
                if c == ' ' and s_buf == '':  # ignore spaces between commas and indents
                    pass
                else:
                    if c == ')' or c == ']':  # exit bracket decrease depth
                        if depth == 1:  # end of function call
                            if s_buf == '':  # some functions have something like , ):
                                pass
                            else:
                                trig_refac_arg = 1
                            trig = 0  # end of function call
                        depth -= 1
                    if c == ',' and depth == 1:  # if the comma is argument splitter,
                        trig_refac_arg = 1
                    elif c == '\n' and depth == 1:  # newline
                        if s_buf == '':  # no captured argument, the start of function call or captured well - just copy and paste
                            pass
                        else:  # maybe the end of function call - do refactoring
                            trig_refac_arg = 1
                    else:
                        if depth >= 1:
                            s_buf += c
                            trig_copy = 0
                    if c == '(' or c == '[':  # go inside bracket. increase depth
                        depth += 1
                if trig_refac_arg == 1:  # s_buf filled, do refactoring
                    if '=' in s_buf:  # named argument, just copy and paste
                        token_s_buf=s_buf.split('=')
                        key=token_s_buf[0].strip()
                        token_s_buf[0] = token_s_buf[0].replace(key, param_map[key])
                        token_s_buf[0] += '='
                        l_refac += "".join(token_s_buf)
                    else:  # positional argument, ERROR!
                        raise Exception("This refactoring function assumes function calls named arguments only. Exiting (do revert)")
                    s_buf = ''  # flush s_buf
                if trig_copy == 1:
                    l_refac += c
                    # if c=='\n':
                    #    print('newline', depth, trig_copy)
            print("   before refactoring: " + l_vanilla[:-1])  # remove newline for neat plotting
            print("    after refactoring: " + l_refac[:-1])
            # print(len(l),len(l_refac))
            lines_o.append(l_refac)  #
        else:  # normal codes, just copy and paste
            lines_o.append(l)

    # write source code
    with open(filename_o, 'w') as f:
        for l in lines_o:
            f.write(l)

def convert_get_obj_xy_to_get_xy(filename_i, filename_o, func_name):
    """
        Convert positional arguments to named arguments for further refactoring under following assumptions.
        1. Refactoring functions defined in GridLayoutGenerator.py
        2. GridLayoutGenerator is instantiated as laygen
    """
    # GridLayoutGenerator parameters
    laygen_path="../../GridLayoutGenerator.py"
    laygen_instance="laygen"
    func_name_new="get_xy"

    # read source code
    with open(filename_i, 'r') as f:
        lines_i = f.readlines()
    print("file " + filename_i + " loaded")

    # refactor
    trig = 0  # trigger for multiline call
    depth = 0 # depth variable to find out arguments
    lines_o = [] # output buffer
    for i, l in enumerate(lines_i):
        if laygen_instance + '.' + func_name in l:
            trig = 1
            l_header = l.split(laygen_instance + '.' + func_name)[0]
            depth = -1*(l_header.count('(') + l_header.count('[')) + (l_header.count(')') + l_header.count(']')) #if brackets are before the function call, need to decrease initial depth value
            print("function " + func_name + " call detected in file: "+ filename_i + ", in line:"+ str(i) +" code snapshot: " + l[:-1])
        if trig == 1:
            l_vanilla = l #copy original one
            l = l.replace(laygen_instance + '.' + func_name, laygen_instance + '.' + func_name_new)
            l_refac = '' #refactored line
            s_buf = ''   #string buffer to store arguments
            trig_refac_arg_readout = 0  # trigger to readout arguments
            for c in l:
                #mystr="    rect_xy_list = [laygen.get_rect_xy(name=r.name, gridname=gridname, sort=True) for r in rect_list]"
                #mystr="    laygen.pin(name='VREF_M5_2<2>', layer=laygen.layers['pin'][5], xy=laygen.get_rect_xy(rvref2v2.name, gridname=rg_m4m5), gridname=rg_m4m5, netname='VREF<2>')"
                #mystr="    diffpair_origin = laygen.get_inst_xy(itapbl0.name, pg) + laygen.get_template_xy(itapbl0.cellname, pg) * np.array([0, 1])"
                #mystr="    org=origin+laygen.get_inst_xy('I'+objectname_pfix+'INV1', pg)+ laygen.get_template_xy(i1.cellname, pg) * np.array([1, 0])"
                #if l_vanilla.startswith(mystr):
                #    print(c, depth, trig_refac_arg_readout, trig_refac_arg, s_buf)
                trig_copy = 1  # trigger to copy c to l_refac without modifications
                trig_refac_arg = 0 # trigger to refactor arguments after readout
                if c == ' ' and s_buf == '':  # ignore spaces between commas and indents
                    pass
                else:
                    if c == ')' or c == ']':  # exit bracket decrease depth
                        if depth == 1:  # end of function call
                            if s_buf == '':  # some functions have something like , ):
                                pass
                            else:
                                if trig_refac_arg_readout == 1:
                                    trig_refac_arg = 1
                            trig = 0 #end of function call
                            trig_refac_arg_readout = 0  # reset readout trigger
                        depth -= 1
                    if c == ',' and depth == 1 and trig_refac_arg_readout==1:  # if the comma is argument splitter,
                        trig_refac_arg = 1
                    elif c == '\n' and depth == 1: # newline
                        if s_buf == '': #no captured argument, the start of function call or captured well - just copy and paste
                            pass
                        else: # maybe the end of function call - do refactoring
                            if trig_refac_arg_readout == 1:
                                trig_refac_arg = 1
                    else:
                        if (depth >= 1) and (trig_refac_arg_readout == 1):
                            s_buf += c
                            trig_copy = 0
                    if c == '(' or c == '[':  # go inside bracket. increase depth
                        depth += 1
                        if (depth == 1) and (l_refac[(-1*len(func_name_new)):]==func_name_new):
                            trig_refac_arg_readout = 1 #found the right spot. Start readout
                if trig_refac_arg == 1: #s_buf filled, do refactoring
                    if '=' in s_buf: #named argument
                        token_s_buf = s_buf.split('=')
                        print(token_s_buf)
                        if token_s_buf[0].strip()=='name':
                            if '.name' in token_s_buf[1]:
                                token_s_buf[1] = token_s_buf[1].replace('.name', '')
                                token_s_buf[0] = 'obj ='
                                l_refac += "".join(token_s_buf)
                            elif '.cellname' in token_s_buf[1]:
                                token_s_buf[1] = token_s_buf[1].replace('.cellname', '.template')
                                token_s_buf[0] = 'obj ='
                                l_refac += "".join(token_s_buf)
                            else:
                                if func_name == 'get_inst_xy':
                                    l_refac += 'obj ='+laygen_instance+'.get_inst('+s_buf+')'
                                elif func_name == 'get_template_xy':
                                    l_refac += 'obj=' + laygen_instance + '.get_template(' + s_buf + '%%PLACEHOLDER_FOR_LIBNAME%%)'
                                elif func_name == 'get_rect_xy':
                                    l_refac += 'obj ='+laygen_instance+'.get_rect('+s_buf+')'
                                else:
                                    raise Exception("check this")
                        elif token_s_buf[0].strip()=='libname':
                            if func_name == 'get_template_xy':
                                l_refac = l_refac.replace('%%PLACEHOLDER_FOR_LIBNAME%%', ', '+s_buf)
                        else:
                            l_refac += s_buf
                    else: #positional argument, ERROR!
                        raise Exception(
                            "This refactoring function assumes function calls named arguments only. Exiting (do revert)")
                    s_buf = '' #flush s_buf
                if trig_copy == 1:
                    l_refac += c
                #if c=='\n':
                #    print('newline', depth, trig_copy)
            if func_name == 'get_template_xy':
                l_refac = l_refac.replace('%%PLACEHOLDER_FOR_LIBNAME%%','')
                l_refac = l_refac.replace(', )', ')')
            print("   before refactoring: "+l_vanilla[:-1]) #remove newline for neat plotting
            print("    after refactoring: "+l_refac[:-1])
            #print(len(l),len(l_refac))

            lines_o.append(l_refac) #
        else: #normal codes, just copy and paste
            lines_o.append(l)

    # write source code
    with open(filename_o, 'w') as f:
        for l in lines_o:
            f.write(l)

if __name__ == '__main__':
    files_include_special = [
        'nand_demo.py',
        'sarsamp_golden_example.py',
        'lab1_a_baselayoutgenerator_export.py',
        'lab1_b_baselayoutgenerator_import.py',
        'lab1_c_cds_ff_mpt_generate_primitives.py',
        'lab1_c_faketech_generate_primitives.py',
        'lab2_a_gridlayoutgenerator_constructtemplate.py',
        'lab2_b_gridlayoutgenerator_layoutexercise.py',
        'lab2_c_gridlayoutgenerator_logictemplate.py',
        'lab2_d_gridlayoutgenerator_layoutexercise_2.py',

    ] #files to be refactored but not with _layout_generator suffix

    '''
    #positional to named - single run example
    #filename_i = "../logic/logic_templates_layout_generator.py"
    #filename_o = "../logic/logic_templates_layout_generator_refactored.py"
    filename_i = "../serdes/serdes_layout_generator.py"
    filename_o = "../serdes/serdes_layout_generator_refactored.py"
    # func_name = "pin_from_rect"
    func_name = "relplace"
    convert_pos_to_named(filename_i=filename_i, filename_o=filename_o, func_name=func_name)
    '''

    '''
    #positional to named - massive run over multiple directories, functions
    dir_list = ["./", "../adc_sar/", "../golden/", "../logic/", "../serdes/", "../../labs/"]
    func_list=["get_template_xy", "get_inst_xy", "get_rect_xy", "get_pin_xy"]
    for dir in dir_list:
        file_list=os.listdir(dir)
        for file in file_list:
            if file.endswith('_layout_generator.py') or any((file == fn) for fn in files_include_special):
                filename=dir+file
                for func in func_list:
                    convert_pos_to_named(filename_i=filename, filename_o=filename, func_name=func)
    '''

    '''
    #pin_from_rect to pin - single run example
    filename_i = "../serdes/ser_layout_generator.py"
    filename_o = "../serdes/ser_layout_generator_refactored.py"
    convert_pin_from_rect_to_pin(filename_i=filename_i, filename_o=filename_o)
    '''

    '''
    #pin_from_rect to pin - massive run over multiple directories, functions
    dir_list=["./", "../adc_sar/", "../golden/", "../logic/", "../serdes/", "../../labs/"]
    for dir in dir_list:
        file_list=os.listdir(dir)
        for file in file_list:
            if file.endswith('_layout_generator.py') or any((file == fn) for fn in files_include_special):
                filename=dir+file
                convert_pin_from_rect_to_pin(filename_i=filename, filename_o=filename)
    '''

    #get_(obj)_xy to get_obj - massive run over multiple directories, functions
    dir_list=["./", "../adc_sar/", "../golden/", "../logic/", "../serdes/", "../../labs/"]
    #func_list = ["get_template_xy", "get_inst_xy", "get_rect_xy", "get_pin_xy"]
    #func_list = ["get_inst_xy", "get_rect_xy", "get_pin_xy"]
    func_list = ["get_template_xy"]
    for dir in dir_list:
        file_list=os.listdir(dir)
        for file in file_list:
            if file.endswith('_layout_generator.py') or any((file == fn) for fn in files_include_special):
                filename=dir+file
                for func in func_list:
                    convert_get_obj_xy_to_get_xy(filename_i=filename, filename_o=filename, func_name=func)

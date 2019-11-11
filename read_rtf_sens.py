import pandas as pd
import re
import os
rtf_list = []
regex = re.compile(r'^\\pard\\cf3(.*)Zone: (\d);(.*)please wait ...\\par')
regex_z2 = re.compile(r'^\\pard\\cf3(.*); \(including reverse elements at remote buses\) please wait ...\\par')
regex_end = re.compile(r'^End of (.*)\\par')
# \pard\cf3 JBC2_30112  57577 DIST "Z1" (7SD52_V4.3_5A); Contact Logic Code: 21PG1_M1\par
regex_element_info = re.compile(r'^\\pard\\cf3 (.*)  (\S*) (\S*) "(\S*)" \((.*)\); Contact Logic Code: (.*)\\par')
regex_element_info_z2 = re.compile(r'^(\S*) ELEMENT: (.): (.*)  (\S*) (\S*) "(\S*)" (\S*) "(.*)" \((.*)\); Contact Logic Code: "(.*)"\\par')
'FWD ELEMENT: 1: JBC2_30112  57577 DIST "Z1B" Zone "1" (7SD52_V4.3_5A); Contact Logic Code: "21PGB_M1"\\par\n'
'FWD ELEMENT: 1: JBC2_30112  57577 DIST "Z1B" Zone "1" (7SD52_V4.3_5A); Contact Logic Code: "21PGB_M1"\\par'
# \pard\cf2\b  10 TPH      Tie   : 30112-301123                       0.00   1.41   79.22     0.97    68.64   0.00  85.00 FAIL > 999 No Sce I\par
regex_fwd_rev = re.compile(r'(.{4}) (.{6}) (.{5}) (.{4})\\par$')
'\\pard                                                                                                          REV1  67.25 110.0 PASS\\par\n'
'   2 TPH      XFMR  : 301105-301102-1 ( )              Fault on L_115KV_JBC1_JCPRT_CKT1 to   1.06   79.25 FWD1  26.61  50.0 PASS\\par\n'
regex_fault_details = re.compile(r'^(?:\\pard\\cf1\\b0 |\\pard\\cf2\\b |\\pard\\cf2\\b |)(.{3}) (.{8}) (.{40}) (.{6}) (.{6}) (.{7}) (.{8}) (.{8}) (.{6}) (.{6}) (.{4}) (.{5}) (.{8})\\par')
regex_fault_details_z2 = re.compile(r'(?:\\pard\\cf1\\b0 |\\pard\\cf2\\b |\\pard\\cf2\\b |)(.{4}) (.{8}) (.{40}) (.{35}) (.{6}) (.{7}) (.{4}) (.{6}) (.{5}) (.{4})\\par')
regex_fault_details_z2_sens = re.compile(r'(?:\\pard\\cf1\\b0 |\\pard\\cf2\\b |\\pard\\cf2\\b |)(.{3}) (.{8}) (.{40}) (.{35}) (.{7}) (.{6}) (.{7}) (.{6}) (.{5}) (.{5}) (.{4}) (.{5})\\par')
'--- -------- ---------------------------------------- ------------------------------------ ------ ------ ------- ------ --------- ------- ------ ----- ---- -----\\par\n'
regex_fault_details_z2_tranform = re.compile(r'(?:\\pard\\cf1\\b0 |\\pard\\cf2\\b |\\pard\\cf2\\b |)(.{3}) (.{8}) (.{40}) (.{36}) (.{6}) (.{6}) (.{7}) (.{6}) (.{9}) (.{7}) (.{6}) (.{5}) (.{4}) (.{5})\\par')
regex_circuit_details = re.compile(r'^{(\\cf4|\\cf2\\b|\\cf1\\b) (.{0,20}) (.{35}) (.{5}) (.{7}) (.{6}) (.{5}) (.{6}) (.{6}) (.*)\\par}')




# class Demo1:
#     def __init__(self, master):
#         self.master = master
#         self.frame = tk.Frame(self.master, height=50)
#         self.button1 = tk.Button(self.frame, text = 'New Window', width = 25 , command = self.new_window)
#         self.button1.pack()
#         self.frame.pack()
#     def new_window(self):
#         self.newWindow = tk.Toplevel(self.master)
#         self.app = Demo2(self.newWindow)

# class Demo2:
#     def __init__(self, master):
#         self.master = master
#         self.frame = tk.Frame(self.master)
#         self.quitButton = tk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
#         self.quitButton.pack()
#         self.frame.pack()
#     def close_windows(self):
#         self.master.destroy()

# def main(): 
#     root = tk.Tk()
#     app = Demo1(root)
#     root.mainloop()

# main()

def fault_parse(start, fault_list, rtf_list):
    temp = []
    for line in rtf_list[start:]:
        
        if (not regex_end.match(line)):
             temp.append(line)
        else:
            fault_list.append(temp)
            break

def fault_to_panda_z2(fault):
    elements = []
    elements_list = []
    elements_list_sens = []
    elements_list_transform = []
    test = []
    fault_details = False
    fwd_rev = False
    continue_line = False
    mode = 0
    transform = False

    for i in fault:

        if mode == 0:
           
            if re.match(r'^Performing reach test on lines connected at all remote buses ...', i):
                mode = 1
                elements = []

            if re.match(r'^\\pard\\cf3 (.*)  (\S*) (\S*) "(.*)" Zone "(.*)" \((.*)\); Contact Logic Code: "(.*)"', i):
                mode = 2
                one_element = None


        if mode == 2:
            reg1 = re.findall(r'^\\pard\\cf3 (.*)  (\S*) (\S*) "(.*)" Zone "(?:.*)" \((.*)\); Contact Logic Code: "(.*)"', i)
            reg2 = regex_fault_details_z2_sens.findall(i)
            if re.match(r'\\pard\\cf1 Zone (\d) - Testing reach through', i):
                transform = True
           
            
            

            # if fwd_rev:
            #     if count > 1:
            #         if re.match(r'\\par$', i):
            #             fwd_rev_element = regex_fwd_rev.findall(i)
            #             elements_list.append(*fwd_rev_element)
            #             count -= 1

            if reg1:
                one_element = [*reg1]
            
            if fault_details:
         
                i = re.sub(r'\\cf2\\b |\\cf1\\b0 |\\cf2 |\\cf1 |\\cf3 ', '', i)
           
                reg2 = regex_fault_details_z2_tranform.findall(i) if transform else regex_fault_details_z2_sens.findall(i)
            
              
            
                if continue_line:
                    i = re.sub(r'\n', '', last_line) + i
                    continue_line = False
                
                
                if not re.match(r'.*\\par$', i):
                    last_line = i
                    continue_line = True
                    continue
                if reg2:
                     
                    elements_list_sens.append([*one_element[0], *reg2[0]]) if not transform else elements_list_transform.append([*one_element[0], *reg2[0]]) 
                    
            

                    # if elements.__len__() > 1:
                    #     fwd_rev = True
                    #     count = elements.__len__() - 1

            if re.match(r'^--- -------- ---', i):
                fault_details = True
            if  re.match(r'^(?:\\pard\\cf1\\b0 |\\pard\\cf2\\b |\\pard\\cf2\\b |\\pard\\cf1|\\pard|)-------------------------------------------------------------------------------------------------', i):
                if fault_details:
                    mode = 0
                    elements = []
                fault_details = False
                transform = False
        

        if mode == 1:
            

            reg1 = regex_element_info_z2.findall(i)
            reg2 = regex_fault_details_z2.findall(i)
            reg_rev = regex_fwd_rev.findall(i)

            if continue_line:
                    i = re.sub(r'\n', '', last_line) + i
                    continue_line = False
                    reg1 = regex_element_info_z2.findall(i)
                    reg2 = regex_fault_details_z2.findall(i)
                    reg_rev = regex_fwd_rev.findall(i)
                
            if not re.match(r'.*\\par$', i):
                    last_line = i
                    continue_line = True
                    continue
            
            

            # if fwd_rev:
            #     if count > 1:
            #         if re.match(r'\\par$', i):
            #             fwd_rev_element = regex_fwd_rev.findall(i)
            #             elements_list.append(*fwd_rev_element)
            #             count -= 1

            if reg1:
                elements.append(*reg1)
            
            if fault_details:
                '  21 DLG      None                                     Fault on L_115KV_JBC1_JCPRT_CKT1 to   1.06   79.25 FWD1  70.27  50.0 FAIL\\par\n'
                '\\cf2\\b   21 DLG      None                                     Fault on L_115KV_JBC1_JCPRT_CKT1 to\\cf1    1.06   79.25\\cf2  FWD1  70.27  50.0 FAIL\\par\n'
                i = re.sub(r'\\cf2\\b |\\cf1\\b0 |\\cf2 |\\cf1 |\\cf3 ', '', i)
                reg1 = regex_element_info_z2.findall(i)
                reg2 = regex_fault_details_z2.findall(i)
                reg_rev = regex_fwd_rev.findall(i)
            
                if continue_line:
                    i = re.sub(r'\n', '', last_line) + i
                    continue_line = False
                    reg1 = regex_element_info_z2.findall(i)
                    reg2 = regex_fault_details_z2.findall(i)
                    reg_rev = regex_fwd_rev.findall(i)
                
                if not re.match(r'.*\\par$', i):
                    last_line = i
                    continue_line = True
                    continue
                if reg2:
                    if reg2[0][6] =='FWD1':   
                        count = elements.__len__()
                        elements_length = elements.__len__()
                        elements_list.append([*elements[0] ,*reg2[0]])
                        last = reg2
                    else:
                        count -= 1
                        elements_list.append([*elements[elements_length - count],*last[0][:-4], *reg_rev[0]])
                elif reg_rev:
                    if reg_rev[0][0] != 'ed  ': 
                        count -= 1
                        elements_list.append([*elements[elements_length - count],*last[0][:-4], *reg_rev[0]])

                    # if elements.__len__() > 1:
                    #     fwd_rev = True
                    #     count = elements.__len__() - 1

            if re.match(r'---- -------- ----', i):
                fault_details = True
            '\\pard -------------------------------------------------------------------------------------------------------------------------------\\par\n'    
            if  re.match(r'^(?:\\pard\\cf1\\b0|\\pard\\cf2\\b |\\pard\\cf2\\b |\\pard\\cf1 |\\pard |)-------------------------------------------------------------------------------------------------', i):
                if fault_details:
                    mode = 0
                    elements = []
                fault_details = False
                transform = False
            
    if elements_list.__len__() % 2 != 0 or elements_list.__len__() % 3 != 0:
        print
    return [elements_list, elements_list_sens, elements_list_transform]

    
 


def fault_to_panda_z1(fault):
    element_info = False
    fault_details = False
    temp = []
    element_list = []
    circuit_details = []
    for i in fault:

        if element_info:
            match_reg = regex_element_info.findall(i)

            element_info = False

        if re.match(r'^(\\pard\\cf1|\\pard\\cf1\\b0) ------------------------------------------------------------------------------------------------------------------------------.*', i):
            element_info = True
        if re.match(r'^{\\f0\\fs16\\cf4\\qc\\ul', i) :
            #  if element_list.__len__() == 0:
            #      pass
            #  continue
            pass

        if fault_details:
              match_fault = regex_fault_details.findall(i)
              if match_fault:
                #   if match_reg[0].__len__() != 6 or match_fault[0].__len__() != 13 :
                #       print
                    try:
                        list_element = match_reg[0]
                    except IndexError:
                        list_element = 6 * ['error']
                    try:
                        list_fault = match_fault[0]
                    except IndexError:
                        list_fault = 13 * ['error']
                   
                    element_list.append([*list_element, *list_fault ])
              if re.match(r'^(\\pard\\cf1|\\pard\\cf1\\b0) ------------------------------------------------------------------------------------------------------------------------------.*', i):
                    fault_details = False
                    element_info = False
        if re.match(r'^--- --------', i):
             fault_details = True
    return element_list






def parse_file(rtf):

        
        element_pd_list = []
        fault_list_z1 = []
        fault_list_z2 = []
        iter_rtf =  iter(rtf)
        count = 0
        result_faults = []
        result_faults_z2 = []
        for index, i in enumerate(rtf):
            match_zone = regex.findall(i)
            match_z2 = regex_z2.findall(i)
            if match_zone:
                if match_zone[0][1] == '1':
                    fault_parse(index, fault_list_z1, rtf)
                else:
                    fault_parse(index, fault_list_z2, rtf)

        for i in fault_list_z1:
            result_faults = result_faults + fault_to_panda_z1(i)
        #     print
        #     for i in result_faults:
        #         if i.__len__() != 21:
        #             print
      
        for i in fault_list_z2:
            result_faults_z2 = result_faults_z2 + fault_to_panda_z2(i) 
            
            # for i in result_faults:
            #     if i.__len__() != 21:
            #         print
      
                    
            
        
        print('finished')
        result_faults_2 = []
        result_faults_3 = []
        for i in result_faults_z2[1::3]:
            result_faults.extend(i)
        for i in result_faults_z2[0::3]:
            result_faults_2.extend(i)
        for i in result_faults_z2[2::3]:
            result_faults_3.extend(i)

        return {'1': result_faults, '2': result_faults_2 , '3': result_faults_3 }


def parse_sensitivity_files(dirct_path):
    element_pd = pd.DataFrame()
    element_pd_fwd = pd.DataFrame()
    element_pd_transform = pd.DataFrame()

    for filename in os.listdir(dirct_path):
        if filename.startswith("NG_Sens") : 
   
            with open( dirct_path +'\\'+ filename, 'r') as f:
                rtf_list = []
                print(filename)
                for i in f:
                        if i != '\n':
                            rtf_list.append(i)
            temp = parse_file(rtf_list)
            print

          
        
            element_pd = element_pd.append( temp['1'] )
            element_pd_fwd = element_pd_fwd.append( temp['2'] )
            element_pd_transform = element_pd_transform.append( temp['3'] )
        
    print('done')

    element_pd_fwd.columns = ('FWD/REV', 'ELEMENT Order', 'Substation', 'Relay Tag', 'Eelment Type', 'Element Name', 'zones', 'Zone', 'Relay Type', 'CLC','Outage Number', 'Fault Type', 'Contingency', 'Fault Location', 'Line Impedance', 'Line Angle', 'Element Direction',
     'Actual Reach %', 'Reach Margin %', 'PASS/FAIL')
    element_pd_fwd = element_pd_fwd[element_pd_fwd['PASS/FAIL'] == 'FAIL']
    element_pd_fwd = element_pd_fwd[['Substation',  'Relay Tag',  'Relay Type', 'Eelment Type', 'Element Name',  'Zone', 'CLC', 'FWD/REV', 'ELEMENT Order', 'Outage Number', 'Contingency', 'Fault Location', 'Line Impedance', 'Line Angle', 'Element Direction',
     'Actual Reach %', 'Reach Margin %', 'PASS/FAIL']]
    element_pd_fwd.sort_values(['Substation',  'Relay Tag',  'Relay Type', 'Eelment Type', 'Element Name',  'Zone', 'CLC', 'FWD/REV', 'ELEMENT Order', 'Outage Number'], inplace=True)
   
    element_pd.columns = ('Substation', 'Relay Tag', 'Eelment Type', 'Element Name',  'Relay Type', 'CLC','Outage Number', 'Fault Type', 'Contingency', 'Delay',  'Line Impedance', 'Line Angle', 'Setting Reach',
     'Reach %', 'Actual Reach %', 'Desired Reach %', 'PASS/FAIL', 'Operation Time', 'SIR')
    element_pd = element_pd[element_pd['PASS/FAIL'] == 'FAIL']
    element_pd = element_pd[['Substation', 'Relay Tag', 'Relay Type', 'Eelment Type', 'Element Name', 'CLC','Outage Number', 'Fault Type', 'Contingency', 'Delay',  'Line Impedance', 'Line Angle', 'Setting Reach',
      'Reach %', 'Actual Reach %', 'Desired Reach %', 'PASS/FAIL', 'Operation Time', 'SIR']]
    element_pd.sort_values(['Substation',  'Relay Tag',  'Relay Type', 'Eelment Type', 'Element Name', 'CLC', 'Outage Number'], inplace=True)
   
 


    

    # element_pd.columns =['Outage Number', 'Contingency', 'Fault Type', 'Fault Location' , 'Line Under Study', 'LZOP Fault Clearing Time', 'Substation', 'LZOP Name', 'LZOP Type', 'Primary/Backup', 'LZOP Time'
    # , 'Breaker Time', 'Total Time', 'CTI', 'Operation', 'Relay Tag', 'Element Type' , 'Element', 'Relay Type', 'Contact Logic Code', 'Element Operation Time']
    # element_pd = element_pd[element_pd['Operation'] != 'NORMAL OPERATION']
    # test = element_pd['LZOP Time']
    # element_pd = element_pd[(element_pd['Element Operation Time'].astype(float) >= element_pd['LZOP Time'].astype(float).multiply(0.9) ) & ( element_pd['Element Operation Time'].astype(float) <= element_pd['LZOP Time'].astype(float).multiply(1.1)) ]
    # element_pd.set_index(['Line Under Study',  'Substation', 'LZOP Name',  'Contingency', 'Element', 'Fault Type' ], inplace=True)
    # element_pd = element_pd.sort_index()
    # print('generating excel ')
    writer = pd.ExcelWriter('pandas_multiple.xlsx', engine='xlsxwriter')
    element_pd.to_excel(writer,  sheet_name='a')
    element_pd_fwd.to_excel(writer,  sheet_name='b')
    element_pd_transform.to_excel(writer,  sheet_name='c')
    writer.save()

    # print()





             
        
         




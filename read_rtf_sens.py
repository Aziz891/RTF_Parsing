import pandas as pd
import re
import tkinter as tk
from tkinter import filedialog
import os
rtf_list = []
regex = re.compile(r'^\\pard\\cf3(.*);  please wait ...\\par')
regex_z2 = re.compile(r'^\\pard\\cf3(.*); \(including reverse elements at remote buses\) please wait ...\\par')
regex_end = re.compile(r'^End of (.*)\\par')
# \pard\cf3 JBC2_30112  57577 DIST "Z1" (7SD52_V4.3_5A); Contact Logic Code: 21PG1_M1\par
regex_element_info = re.compile(r'^\\pard\\cf3 (\S*)  (\S*) (\S*) "(\S*)" \((.*)\); Contact Logic Code: (.*)\\par')
# \pard\cf2\b  10 TPH      Tie   : 30112-301123                       0.00   1.41   79.22     0.97    68.64   0.00  85.00 FAIL > 999 No Sce I\par

regex_fault_details = re.compile(r'^(?:\\pard\\cf1\\b0 |\\pard\\cf2\\b |\\pard\\cf2\\b |)(.{3}) (.{8}) (.{40}) (.{6}) (.{6}) (.{7}) (.{8}) (.{8}) (.{6}) (.{6}) (.{4}) (.{5}) (.{8})\\par')
regex_circuit_details = re.compile(r'^{(\\cf4|\\cf2\\b|\\cf1\\b) (.{0,20}) (.{35}) (.{5}) (.{7}) (.{6}) (.{5}) (.{6}) (.{6}) (.*)\\par}')
directory = 'C:\\Users\\aziza\\Downloads\\AAB'



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
    return [0]


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
                fault_parse(index, fault_list_z1, rtf)
            if match_z2:
                fault_parse(index, fault_list_z2, rtf)

        # for i in fault_list_z1:
        #     result_faults = result_faults + fault_to_panda_z1(i)
        #     print
            # for i in result_faults:
            #     if i.__len__() != 21:
            #         print
      
        for i in fault_list_z2:
            result_faults_z2 = result_faults_z2 + fault_to_panda_z2(i) 
            
            # for i in result_faults:
            #     if i.__len__() != 21:
            #         print
      
                    
            
        
        print('finished')
        return result_faults


def parse_sensitivity_files(dirct_path):
    element_pd = pd.DataFrame()
    count = 1
    for filename in os.listdir(directory):
        if filename.endswith(".rtf") : 
   
            with open( dirct_path +'\\'+ filename, 'r') as f:
                rtf_list = []
                print(filename)
                for i in f:
                        if i != '\n':
                            rtf_list.append(i)
            temp = parse_file(rtf_list)
            if temp.__len__() > 0:

                element_pd = element_pd.append( temp )
            count += 1
    print('done')


    # element_pd.columns =['Outage Number', 'Contingency', 'Fault Type', 'Fault Location' , 'Line Under Study', 'LZOP Fault Clearing Time', 'Substation', 'LZOP Name', 'LZOP Type', 'Primary/Backup', 'LZOP Time'
    # , 'Breaker Time', 'Total Time', 'CTI', 'Operation', 'Relay Tag', 'Element Type' , 'Element', 'Relay Type', 'Contact Logic Code', 'Element Operation Time']
    # element_pd = element_pd[element_pd['Operation'] != 'NORMAL OPERATION']
    # test = element_pd['LZOP Time']
    # element_pd = element_pd[(element_pd['Element Operation Time'].astype(float) >= element_pd['LZOP Time'].astype(float).multiply(0.9) ) & ( element_pd['Element Operation Time'].astype(float) <= element_pd['LZOP Time'].astype(float).multiply(1.1)) ]
    # element_pd.set_index(['Line Under Study',  'Substation', 'LZOP Name',  'Contingency', 'Element', 'Fault Type' ], inplace=True)
    # element_pd = element_pd.sort_index()
    # print('generating excel ')

    element_pd.to_excel('output.xlsx', engine='xlsxwriter')

    print()

parse_sensitivity_files(directory)






    
   
             
        
         




import pandas as pd
import re
from tkinter import *
rtf_list = []
regex = re.compile(r'^\S* No packages have been outaged;')
regex_end = re.compile(r'^.*Fault cleared at')

element_pd = pd.DataFrame()

root = Tk()

mybutton = Button(root, text = 'Exit')
mybutton.pack()
root.mainloop()



def fault_parse(start):
    temp = []
    for line in rtf_list[start:]:
        
        if (not regex_end.match(line)):
             temp.append(line)
        else:
            fault_list.append(temp)
            break

def fault_to_panda(fault):
    fault_info = False
    fault_details = False
    temp = []
    element_list = []
    circuit_details = []
    for i in fault:

        if fault_info:
            match_reg = re.findall(r'{(\\cf4|\\cf2\\b|\\cf1\\b) (.{5}) (.{40}) (.{10}) (.{50}) (.{9}) (.{26})\\par', i)
            for index, j in enumerate(match_reg[0]):
                
                # if index in [0, 3]:
                #     test = re.findall(r'(\d*)\s(.*)', j)
                #     temp.extend(*test)
                if index in [4]:
                    test = re.split(r'on', j)
                    temp.extend(test)
                elif index ==0:
                    continue
                else:
                    temp.append(j)





            print
            fault_info = False
            


        if re.match(r'^----- ', i):
             fault_info = True


        if fault_details:
            #   element_list = []

              

              if re.match(r'^{\\cf5\\b Element: ', i):
                  element_details = re.findall(r'{\\cf5\\b Element: (\d*) (\w*) "(\w*)" "(\w*)"; \((.*)\)\s*; Contact Logic Code: (\w*)\s*; Op. Time:  (.*)\\par}', i)
                  element_list.append([*temp[:-1], *circuit_details[0][1:], *element_details[0]])
                  print

              elif re.match(r'^{\\cf6\\b   Sup. : ', i):
                  print
              elif re.match(r'{\\cf4  \\par}', i):
                  print

              elif re.match(r'{\\cf4 ----------------', i):
                  fault_details = False

              if re.match(r'^{(\\cf4|\\cf2\\b|\\cf1\\b)', i):
                  circuit_details = re.findall(r'^{(\\cf4|\\cf2\\b|\\cf1\\b) (.{0,20}) (.{35}) (.{5}) (.{7}) (.{6}) (.{5}) (.{6}) (.{6}) (.*)\\par}', i)
                  print            






        if re.match(r'^{\\cf4 -------------------- -', i):
             fault_details = True
    return element_list





with open('NG_Coord_Review_380KV_(MHYL_WEST_49200)_(334_334)_(334_334)_CKT1.rtf', 'r') as f:
    for i in f:
        if i != '\n':
            rtf_list.append(i)
    
fault_list = []
iter_rtf =  iter(rtf_list)

for index, i in enumerate(rtf_list):
     if regex.match(i):

         fault_parse(index)

for i in fault_list:
    result_faults = fault_to_panda(i)
    element_pd = element_pd.append(result_faults, )

element_pd.columns =['column' + str(i) for i in range(22)]
element_pd.set_index(['column4', 'column0', 'column1', 'column2', 'column3', 'column5', 'column6', 'column7'  ], inplace=True)
element_pd = element_pd[element_pd['column14'] != 'NORMAL OPERATION']
element_pd.to_excel('output.xlsx')

print()







    
   
             
        
         




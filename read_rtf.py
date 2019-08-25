import pandas as pd
import re
rtf_list = []
regex = re.compile(r'^\S* No packages have been outaged;')
regex_end = re.compile(r'^.*Fault cleared at')

element_pd = pd.DataFrame()

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
    for i in fault:

        if fault_info:
            match_reg = re.split(r'\s{2,50}', i)
            for index, j in enumerate(match_reg[1:]):
                
                if index in [0, 3]:
                    test = re.findall(r'(\d*)\s(.*)', j)
                    temp.extend(*test)
                elif index in [2]:
                    test = re.split(r'on', j)
                    temp.extend(test)
                else:
                    temp.append(j)




            print
            fault_info = False
            


        if re.match(r'^----- ', i):
             fault_info = True


        if fault_details:

              circuit_details = []  

              if re.match(r'^{\\cf5\\b Element: ', i):
                  elemend_details = re.findall(r'{\\cf5\\b Element: (\d*) (\w*) "(\w*)" "(\w*)"; \((.*)\)\s*; Contact Logic Code: (\w*)\s*; Op. Time:  (.*)\\par}', i)
                  print    

              elif re.match(r'^{\\cf6\\b   Sup. : ', i):
                  print
              elif re.match(r'{\\cf4  \\par}', i):
                  print

              elif re.match(r'{\\cf4 ----------------', i):
                  fault_details = False

              if re.match(r'^{\\cf4', i):
                  circuit_details = re.findall(r'^{\\cf4 (.{0,20}) (.{35}) (.{5}) (.{7}) (.{6}) (.{5}) (.{6})  ', i)
                  print            






        if re.match(r'^{\\cf4 -------------------- -', i):
             fault_details = True
    




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
    fault_to_panda(i)


    
   
             
        
         




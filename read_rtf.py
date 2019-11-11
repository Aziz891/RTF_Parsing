import pandas as pd
import re
import os


rtf_list = []
regex = re.compile(r'^\S* No packages have been outaged;')
regex_end = re.compile(r'^{\\f0\\fs16\\cf4  \\par')
regex_fault_info = re.compile(
    r'{(\\cf4|\\cf1\\b|\\cf2\\b|\\cf3\\b) (.{5}) (.{40}) (.{10}) (.{50}) (.{9}) (.{26})\\par')
regex_element_details = re.compile(
    r'{\\cf5\\b Element: (\d*) (.*) "(.*)".*;(.*); Contact Logic Code:(.*); Op. Time:(.*)\\par}')
    # '{\cf5\b Element: 55537 TIMER "T4" "1"; (7SA522)      ; Contact Logic Code: 21PG4T_M2   ; Op. Time:  2.017\par}'
regex_circuit_details = re.compile(
    r'^{(\\cf4|\\cf2\\b|\\cf1\\b) (.{0,20}) (.{35}) (.{5}) (.{7}) (.{6}) (.{5}) (.{6}) (.{6}) (.*)\\par}')



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


def fault_to_panda(fault):
    fault_info = False
    fault_details = False
    temp = []
    element_list = []
    circuit_details = []
    for i in fault:

        if fault_info:
            match_reg = regex_fault_info.findall(i)
            for index, j in enumerate(match_reg[0]):

                # if index in [0, 3]:
                #     test = re.findall(r'(\d*)\s(.*)', j)
                #     temp.extend(*test)
                if index in [4]:
                    test = re.split(r'on', j)
                    temp.extend(test)
                elif index == 0:
                    continue
                else:
                    temp.append(j)

            fault_info = False

        if re.match(r'^----- ---------------------------------------- ', i):
            fault_info = True
        if re.match(r'^{\\f0\\fs16\\cf4\\qc\\ul', i):
            #  if element_list.__len__() == 0:
            #      pass
            #  continue
            pass

        if fault_details:
            #   element_list = []

            if re.match(r'^{\\cf5\\b Element: ', i):
                element_details = regex_element_details.findall(i)
                element_list.append(
                    [*temp[:-1], *circuit_details[0][1:], *element_details[0]])

            #   elif re.match(r'^{\\cf6\\b   Sup. : ', i):
            #       print
            #   elif re.match(r'{\\cf4  \\par}', i):
            #       print

            elif re.match(r'{\\cf4 ----------------', i):
                fault_details = False

            if re.match(r'^{(\\cf4|\\cf2\\b|\\cf1\\b)', i):
                circuit_details = regex_circuit_details.findall(i)

        if re.match(r'^{\\cf4 -------------------- -', i):
            fault_details = True
    return element_list


def parse_file(rtf):

    element_pd_list = []
    fault_list = []
    iter_rtf = iter(rtf)
    count = 0
    result_faults = []
    for index, i in enumerate(rtf):
        if regex.match(i):

            fault_parse(index, fault_list, rtf)

    for i in fault_list:
        result_faults = result_faults + fault_to_panda(i)
        print
        # for i in result_faults:
        #     if i.__len__() != 21:
        #         print

    print('finished')
    return result_faults


def parse_coordination_files(dirct_path):
   count = 0 
   element_pd = pd.DataFrame()
   for filename in os.listdir(dirct_path):
        if filename.startswith("NG_Coord"):
            count += 1
            with open(dirct_path + '/' + filename, 'r') as f:
                rtf_list = []
                print(filename)
                for i in f:
                    if i != '\n':
                        rtf_list.append(i)
            element_pd = element_pd.append(parse_file(rtf_list))
            # if count > 1:
            #     break
            print('done')


   element_pd.columns = ['Outage Number', 'Contingency', 'Fault Type', 'Fault Location' , 'Line Under Study', 'LZOP Fault Clearing Time', 'Substation', 'LZOP Name', 'LZOP Type', 'Primary/Backup', 'LZOP Time'
                         , 'Breaker Time', 'Total Time', 'CTI', 'Operation', 'Relay Tag', 'Element Type' , 'Element', 'Relay Type', 'Contact Logic Code', 'Element Operation Time']


   element_pd_filtered = element_pd[(element_pd['Operation'] == 'MISCOORDINATION')  ]
   element_pd_filtered = element_pd_filtered[(element_pd_filtered['Element Operation Time'].astype(float) >= element_pd_filtered['LZOP Time'].astype(float).multiply(0.9) ) & (element_pd_filtered['Element Operation Time'].astype(float) <= element_pd_filtered['LZOP Time'].astype(float).multiply(1.1)) ]
   length = element_pd_filtered.shape[0]
   count = 0
   element_pd_temp = pd.DataFrame()
   element_pd_temp_2 = element_pd[(element_pd['Outage Number'].isin(element_pd_filtered['Outage Number'])) & (element_pd['Contingency'].isin(element_pd_filtered['Contingency'])) & (element_pd['Line Under Study'].isin(element_pd_filtered['Line Under Study'])) & (element_pd['Fault Type'].isin(element_pd_filtered['Fault Type'])) & (element_pd['Primary/Backup'] == 'PRIMARY') ]
     
   for index, row in element_pd_filtered.iterrows():
    
        test = element_pd_temp_2[(element_pd_temp_2['Outage Number'] == row[0]) & (element_pd_temp_2['Contingency'] == row[1]) & (element_pd_temp_2['Line Under Study'] == row[4]) & (element_pd_temp_2['Fault Type'] == row[2]) ]
     
        test['Primary/Backup'] =  test['Primary/Backup'] +'-'+ test['Substation'] 
        test['Substation'] = row.at['Substation']
        test['Element'] = row.at['Element']
        test['LZOP Name'] = row.at['LZOP Name']
        element_pd_temp = element_pd_temp.append(test)

        count+= 1
        if count % 100 ==0:
            print((count/length)*100)
        print
        
   print('generating excel ')

   element_pd_filtered = element_pd_filtered[(element_pd_filtered['Element Operation Time'].astype(float) >= element_pd_filtered['LZOP Time'].astype(float).multiply(0.9) ) & (element_pd_filtered['Element Operation Time'].astype(float) <= element_pd_filtered['LZOP Time'].astype(float).multiply(1.1)) ]
   element_pd_filtered.set_index(['Line Under Study',  'Substation', 'LZOP Name',  'Element', 'Fault Type', 'Contingency','Fault Location' ], inplace=True)
   element_pd_filtered = element_pd_filtered.sort_index()
   element_pd_filtered.to_excel('output.xlsx', engine='xlsxwriter')

   print()



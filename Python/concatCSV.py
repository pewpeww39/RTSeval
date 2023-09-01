import pandas as pd 
import re

# fileLoc = str('~\\skywaterTemp\\RTS_B0_1uA')
fileLoc = '~\\skywaterTemp\\feather\\rtsData_Row'
# rtsEval = pd.DataFrame(pd.read_csv(fileLoc+str('One.csv')))
rtsEval= pd.DataFrame(data=[], index=[], columns=[]) 

for i in range(1,6):
    # data = pd.DataFrame(pd.read_csv(fileLoc + str(i) + '.csv'))
    rowRX = re.sub(r'[0-9]+$',
                    lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the row number
                    str(i))  
    data = pd.DataFrame(pd.read_feather(fileLoc + str(rowRX) + '.feather'))
    # dataL = []
    # dataL = {"Vs": data.Vs,
    #           "Vgs": data.Vgs
    #             }
    # print(dataL)
    # data.to_feather('~\\skywaterTemp\\feather\\RTS_B0_10uA' + str(i)+ '.feather')
    rtsEval = pd.concat([rtsEval, data], axis = 0, ignore_index=True)
    # print(rtsEval)
    data = data.reset_index(drop = True, inplace=True)
    print(i)

rtsEval.to_feather('~\\skywaterTemp\\feather\\RTS_B0_10nA.feather')
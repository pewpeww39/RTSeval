import pandas as pd
import re
def inport(file):
    df = pd.DataFrame(pd.read_feather(file))
    return df

# rtsData = inport(fileLoc+ '10uA.feather')
rtsData = pd.DataFrame(data=[], index=[],
                        columns=['Vs', 'Vgs','Ids','Sample_Rate',
                                'Ticks', 'Column','Row','W_L',
                                'Type','DieX', 'DieY']) 
saveLoc = "C:\\Users\\jacob\\OneDrive\\Documents\\Skywater\\RTS_Data\\bank1\\"
for i in range(1,97):
    rowRX = re.sub(r'[0-9]+$',
                    lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the row number
                    str(i))  
    fileLoc = "C:\\Users\\jacob\\Downloads\\rtsData_Row" + str(i) + ".feather"
    data1 = inport(fileLoc, 0 ,0, ['Vs', 'Vgs', 'Ids','Sample_Rate',
                                   'Ticks', 'Column','Row','W_L',
                                     'Type','DieX', 'DieY'])
    # data1.to_feather(saveLoc + 'file' + str(i) + '.feather')
    print(i)
    rtsData = pd.concat([rtsData, data1], axis = 0, ignore_index=True)
    print(i)

rtsData.to_csv(saveLoc + '10uA.csv')

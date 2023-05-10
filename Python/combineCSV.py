import pandas as pd

def inport(file, idex, head, col):
    df = pd.DataFrame(pd.read_csv(file, index_col=[idex] , header=head), 
                            columns = col)
    return df

rtsData = pd.DataFrame(data=[], index=[],
                        columns=['Vs', 'Vgs','Ids','Sample_Rate',
                                'Ticks', 'Column','Row','W_L',
                                'Type','DieX', 'DieY']) 
saveLoc = "C:\\Users\\jacob\\OneDrive\\Documents\\Skywater\\RTS_Data\\bank1\\"
for i in range(1,4):
    fileLoc = "C:\\Users\\jacob\\Downloads\\rtsData_Loop" + str(i) + ".csv"
    data1 = inport(fileLoc, 0 ,0, ['Vs', 'Vgs', 'Ids','Sample_Rate',
                                   'Ticks', 'Column','Row','W_L',
                                     'Type','DieX', 'DieY'])
    data1.to_feather(saveLoc + 'file' + str(i) + '.feather')
    print(i)
    rtsData = pd.concat([rtsData, data1], axis = 0, ignore_index=True)
    print(i)


rtsData.to_feather(saveLoc + '10uA.feather')
# print(rtsData.to_string())
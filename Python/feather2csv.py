import pandas as pd

def inport(file):
    df = pd.DataFrame(pd.read_feather(file))
    return df

fileLoc = "C:\\Users\\jacob\\OneDrive\\Documents\\Skywater\\RTS_Data\\bank1\\"

rtsData = inport(fileLoc+ '10uA.feather')
print(1)
# rtsData = pd.DataFrame(data=[], index=[],
#                         columns=['Vs', 'Vgs','Ids','Sample_Rate',
#                                 'Ticks', 'Column','Row','W_L',
#                                 'Type','DieX', 'DieY']) 

rtsData.to_csv(fileLoc + '10uA.csv')

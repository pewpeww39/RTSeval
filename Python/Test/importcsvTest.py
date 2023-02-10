import pandas as pd

specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv', index_col=[0] , header=0), 
                            columns = ['W', 'L', 'Type'])
spec=[]
print(specData.iloc[1])
for v in range(5):
    spec = list(specData.iloc[v+1])
    print(str(spec))

# C:\Users\jacob\miniconda3\envs\testequ\RTSeval\Files\DOE_RTS_Array_Cells.xlsx
# C:\Users\jacob\miniconda3\envs\testequ\RTSeval\Files\RTS_Array_Cells.csv
import pandas as pd

def inport(file, idex, head, col):
    df = pd.DataFrame(pd.read_csv(file, index_col=[idex] , header=head), 
                            columns = col)
    return df


# specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
#                      index_col=[0] , header=0), columns = ['W', 'L', 'Type'])

specData = inport("~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv", 0, 0, ['W','L'])
spec=[]
print(specData)
for v in range(5):
    spec = list(specData.iloc[v])
    if v == 4:
        print(v)
    print(str(spec))

# C:\Users\jacob\miniconda3\envs\testequ\RTSeval\Files\DOE_RTS_Array_Cells.xlsx
# C:\Users\jacob\miniconda3\envs\testequ\RTSeval\Files\RTS_Array_Cells.csv
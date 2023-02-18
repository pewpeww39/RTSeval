import numpy as np
import math
import time
import pandas as pd
from datetime import datetime
from os import system, name
import serial
import matplotlib.pyplot as plt
import re

aData = pd.DataFrame(data=[], index=[], columns=['index', 'rowS']) 
bData = pd.DataFrame(data=[], index=[], columns=[])
vOut1 = []
vOut1 = [1,2,3,4]
vOut2 = [1,1,1,1,1,1,1]
aData['index'] = vOut1
aData['rowS'] = vOut1
print(aData)
aData = aData.reindex_like(vOut2)
bData = [1,1,1,1,1,1,1,1,1,1]

aData = aData.drop('rowS', axis=1)
aData = aData.reset_index()
print(aData)
aData['rowS'] = [1,1,1,1,1,1,1]
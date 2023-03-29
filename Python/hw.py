import numpy as np
import matplotlib.pyplot as plt

dtList = [0,1,2,3,6,-4,-8,0,0]
k=[-1,0,1,2,3,4,5,6,7]
# dtList1 = [6,2,1,1,1,1,2,2]
# k1=[1,3,5,7,9,11,13,15]
markerline, stemlines, basline = plt.stem(k, dtList, linefmt = 'teal', markerfmt='o')
# markerline1, stemlines1, basline1 = plt.stem(k1, dtList1, linefmt = 'teal', markerfmt='o')
# markerline1.set_markerfacecolor('none')
plt.show()
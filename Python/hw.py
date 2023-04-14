import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import poisson

def stemPlt():
    dtList = [0,1,2,3,6,-4,-8,0,0]
    k=[-1,0,1,2,3,4,5,6,7]
    # dtList1 = [6,2,1,1,1,1,2,2]
    # k1=[1,3,5,7,9,11,13,15]
    markerline, stemlines, basline = plt.stem(k, dtList, linefmt = 'teal', markerfmt='o')
    # markerline1, stemlines1, basline1 = plt.stem(k1, dtList1, linefmt = 'teal', markerfmt='o')
    # markerline1.set_markerfacecolor('none')
    plt.show()

def boxWalk(p,L,N):
    X = np.zeros((N,1))
    for n in range(2, N):
        if X[n-1]==0:
            X[n] = 1
        elif X[n-1] == L:
            X[n] = L-1
        else:
            if np.random.rand() < p:
                X[n] = X[n-1] - 1
            else:
                X[n] = X[n-1] + 1
    # print(X)
    return X

def hw2():
    p = 0.5;                            # probability of moving left
    L = 25;                             # box length
    N = 500;                            # run time
    M = 3000;                           # number of sample paths 
    X1 = pd.DataFrame(data=[], index=[], columns=[]) 
    for m in range(1, M):
        X = pd.DataFrame(boxWalk(p, L, N))
        X1 = pd.concat([X1, X], axis=1)

    meanpath = np.mean(X1, axis=1)
    stdpath = np.std(X1, axis=1)
    meanplus = meanpath + stdpath
    meanminus = meanpath - stdpath

    timeax = np.linspace(1, N, N)

    plt.plot(timeax, X1.iloc[:, :4])
    plt.xlabel('Time, N')
    plt.ylabel('Statistics of X[N]')
    plt.axis([1, N, 0, L])
    plt.legend(['sample path 1', 'sample path 2', 'sample path 3','sample path 4'])
    plt.savefig('D:\\OneDrive - University of Tennessee\\College\\UTC\\Master\\Fall 2022\\Stoichastic Processes\\hw\\hw2\\p2.png')
    fig1 = plt.show(block=False)
    # plt.pause(3)
    plt.close(fig1)

    plt.plot(timeax, meanpath)
    plt.plot(timeax, meanplus)
    plt.plot(timeax, meanminus)
    plt.legend(['mean', 'upper bound', 'lower bound'])
    plt.savefig('D:\\OneDrive - University of Tennessee\\College\\UTC\\Master\\Fall 2022\\Stoichastic Processes\\hw\\hw2\\p3.png')
    fig2 = plt.show(block=False)
    # plt.pause(3)
    plt.close(fig2)


    power = np.linspace(0,3,4, dtype=int)
    # times = 35 * 2**power
    times = [1, 100, 300, 450]
    for i in range(1,5,1):
        t = times[i-1]
        plt.subplot(2,2,i)
        plt.hist(X1.iloc[:,[t]], bins=list(range(0, L)))
        plt.ylabel('Histogram at time ' + str(t))
    # plt.axis([-1, L+1, 0, 20])
    plt.savefig('D:\\OneDrive - University of Tennessee\\College\\UTC\\Master\\Fall 2022\\Stoichastic Processes\\hw\\hw2\\p4.png')
    fig3 = plt.show(block=False)
    plt.pause(3)
    plt.close(fig3)

def possionProcess(n):
    lambdaa = 0.1
    t = 10
    p = (lambdaa * t) / n
    N = pd.DataFrame(data=[], index=[0], columns=[])
    b = pd.DataFrame(data=[], index=[], columns=[])

    for i in range(10000):
        b = np.sum((np.random.rand(1,n) < p))
        N[i] = b 
    return N
N = pd.DataFrame(data=[], index=[], columns=[])
j=0
for i in range(2,14,2):
    N = pd.concat([N,possionProcess(i)], ignore_index=True)
for j in range(0,6,1):
    plt.subplot(2,3,j+1)
    plt.hist(N.iloc[j])
    plt.semilogy()
    i = list(range(2,14,2))
    plt.ylabel('Histogram with  ' + str(i[j]) + ' subintervals')
plt.savefig('D:\\OneDrive - University of Tennessee\\College\\UTC\\Master\\Fall 2022\\Stoichastic Processes\\hw\\hw3\\p1.png')
plt.show()
for i in range(2,14,2):
    possionDistribution = poisson.rvs(1, size = i)
    print(possionDistribution)
    plt.subplot(2,3,j+1)
    j=j+1
    print(j)
    plt.hist(possionDistribution, density=True)
    plt.semilogy()
    plt.title("alpha = 1")
    # i = list(range(2,14,2))
    plt.ylabel('Histogram with  ' + str(i) + ' subintervals')
plt.savefig('D:\\OneDrive - University of Tennessee\\College\\UTC\\Master\\Fall 2022\\Stoichastic Processes\\hw\\hw3\\p1.1.png')
plt.show()




        
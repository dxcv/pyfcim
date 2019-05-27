#%%
from WindPy import *
import numpy as np

#%%
w.start()

#%%
error, df = w.edb("M0039354", "2010-02-01", "2019-03-03","Fill=Previous",usedf=True)


n = df.CLOSE.values.__len__()

F = np.zeros((n,n))
F[0,0:3] = np.array([1,-2,1])
F[1,0:4] = np.array([-2,5,-4,1])
for i in range(2,n-2):
    F[i, (i-2):(i+3)] = np.array([1,-4,6,-4,1])
F[n-2,(n-4):n] = np.array([1, -4, 5, -2])
F[n-1,(n-3):n] = np.array([1,-2,1])

I = np.eye(n)

matX = (np.mat(1600*F+I).I)*df.CLOSE.values.reshape((-1,1))

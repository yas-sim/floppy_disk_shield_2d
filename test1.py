import numpy as np

a = np.array([i for i in range(0, 20)])
b = np.array([i for i in range(100, 120)])

c = np.concatenate([a, b])
c = c.reshape((2,-1))
c = c.transpose((1,0))
print(c)

a = [i for i in range(0,20)]
b = [i for i in range(100,120)]
buf = []
for x,y in zip(a,b):
    buf += [x,y]
print(buf)

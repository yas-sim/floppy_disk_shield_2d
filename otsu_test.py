track_data = 'track2e-4m-a.txt'

file = [ line.rstrip('\n') for line in open(track_data, 'r').readlines() ]
str=''
for f in file:
    str+=f

length = [ ord(c)-ord(' ') for c in str ]

histo = [ 0 for i in range(40) ]

for l in length:
    if l>=len(histo):
        l = len(histo) - 1
    histo[l]+=1

for i,v in enumerate(histo):
    print(i, v)






import math
import numpy as np

class Otsu:
    def __init__(self):
        self.threshold_values = {}
        self.histo = []

    def generate_histogram(self, data):
        self.histo = np.zeros(256)
        for i in range(len(data)):
                self.histo[data[i]] += 1
        return self.histo

    def countData(self):
        cnt = 0
        for i in range(0, len(self.histo)):
            if self.histo[i]>0:
                cnt += self.histo[i]
        return cnt

    def wieght(self, s, e):
        w = 0
        for i in range(s, e):
            w += self.histo[i]
        return w

    def mean(self, s, e):
        m = 0
        w = self.wieght(s, e)
        for i in range(s, e):
            m += self.histo[i] * i
        if w==0:
            return 0
        return m/float(w)

    def variance(self, s, e):
        v = 0
        m = self.mean(s, e)
        w = self.wieght(s, e)
        for i in range(s, e):
            v += ((i - m) **2) * self.histo[i]
        if w==0:
            return 0
        return v/w
                
    def threshold(self):
        self.threshold_values = {}      # Clear threshold value dict
        cnt = self.countData()
        for i in range(1, len(self.histo)):
            vb = self.variance(0, i)
            wb = self.wieght(0, i) / float(cnt)
            mb = self.mean(0, i)
            
            vf = self.variance(i, len(self.histo))
            wf = self.wieght(i, len(self.histo)) / float(cnt)
            mf = self.mean(i, len(self.histo))
            
            V2w = wb * (vb) + wf * (vf)
            V2b = wb * wf * (mb - mf)**2
            
            if not math.isnan(V2w):
                self.threshold_values[i] = V2w

    def mask_histogram(self, s, e):
        for i in range(s, e+1):
            self.histo[i] = 0

    def get_optimal_threshold(self):
        min_V2w = min(self.threshold_values.values())
        optimal_threshold = [k for k,v in self.threshold_values.items() if v == min_V2w]
        return optimal_threshold[0]

otsu = Otsu()
otsu.generate_histogram(length)

otsu.threshold()
th1 = otsu.get_optimal_threshold()
print(th1)

otsu.mask_histogram(0, th1)
otsu.threshold()
th2 = otsu.get_optimal_threshold()
print(th2)

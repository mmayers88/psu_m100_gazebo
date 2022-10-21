import numpy as np
import matplotlib.pyplot as plt
from itertools import product
import GPy as gpy
from scipy.spatial.distance import cdist

# np.random.seed(10000)   # seed for generating test data (didn't do for training data)

plt.close('all')
Nx = 61
Ny = 60
xx = np.linspace(0.,1.,Nx)
yy = np.linspace(0.,1.,Ny)
xy = np.array(list(product(xx, yy)))

# set up superlevel set
nComponents = 3     # number of desired connected components
centSep = 0.7       # require centers to be at least this distance apart
cents = [np.random.rand(2)]
while len(cents) < nComponents:
    newCent = np.random.rand(2)
    dist = cdist(newCent[None, :], np.array(cents))[0,:]
    if min(dist) > centSep:
        cents.append(newCent)

# peakVar and ptsPerPeak control the size of the superlevel set
peaks = []
peakVar = 0.003      # make very small to get circles
ptsPerPeak = 10     # controls size of each component more directly
for cent in cents:
    peakCov = np.random.rand(2, 2)
    peakCov = np.sqrt(peakVar)*(peakCov + peakCov.T)
    np.fill_diagonal(peakCov, np.amax(peakCov) + 0.01*np.random.rand())
    peaks.append(cent + np.random.multivariate_normal([0, 0], peakCov, ptsPerPeak))
peaks = np.array(peaks).reshape(nComponents*ptsPerPeak, 2)


# set up sublevel set
valleys = np.random.rand(100, 2)            # points below level set threshold
vpDists = cdist(valleys, peaks)
badLocs = np.argwhere(vpDists < 0.3)[:,0]
goodLocs = np.setdiff1d(np.arange(len(valleys) - 1), badLocs)
valleys = valleys[goodLocs]

# measurements at peaks and valleys
tau = 0.5   # level set threshold
beta = 0.5   # sampled values range from tau +/- beta
varn = 0.01
samps = np.vstack([peaks, valleys])
meas = np.zeros(samps.shape[0])
meas[:len(peaks)] = tau + beta + np.sqrt(varn)*np.random.randn(len(peaks))
meas[len(peaks):] = tau - beta + np.sqrt(varn)*np.random.randn(len(valleys))

# regress two-dimensional GP field
k = gpy.kern.RBF(input_dim=2, variance=1, lengthscale=0.1)
gpr = gpy.models.gp_regression.GPRegression(samps, meas[:,None], kernel=k)
y, _ = gpr.predict(xy)
Y = y.reshape(Nx, Ny)
plt.figure()
# plt.imshow(Y)
plt.contourf(xx, yy, Y.T)
plt.scatter(samps[:,0], samps[:,1], c=meas)
print(xx)
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.colorbar()


Ythresh = Y >= tau
plt.figure()
Ythresh = Ythresh.T
plt.imshow(np.flip(np.flip(Ythresh,1)))
plt.colorbar()
plt.show()

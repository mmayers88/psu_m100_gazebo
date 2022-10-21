import numpy as np
import matplotlib.pyplot as plt
from itertools import product
import GPy as gpy

np.random.seed(10000)   # seed for generating test data (didn't do for training data)

plt.close('all')
Nx = 21
Ny = 20
xx = np.linspace(0.,1.,Nx)
yy = np.linspace(0.,1.,Ny)
xy = np.array(list(product(xx, yy)))

lenScales = [0.3, 0.6, 0.9]     # test three lengthscales
MC = 100    # number of fields per lengthscale

# two-dimensional kernel to define field - same for all boundary lengthscales
k2 = gpy.kern.RBF(input_dim=2, variance=1, lengthscale=0.1)
mu2 = np.zeros((Nx*Ny))
C2 = k2.K(xy)

allBoundaries = np.zeros((Nx,len(lenScales),MC))
allFields = np.zeros((Nx,Ny,len(lenScales),MC))
for ll, ls in enumerate(lenScales):
    # one-dimensional kernel to define boundary
    k1 = gpy.kern.RBF(input_dim=1, variance=1, lengthscale=0.3)
    mu1 = np.zeros(Nx)
    C1 = k1.K(xx[:,None])
    for mc in range(MC):
        bb = np.random.multivariate_normal(mu1, C1)
        if np.amin(bb) < 0:
            bb += np.abs(np.amin(bb))
        if np.amax(bb) > 1:
            bb /= np.amax(bb)

        # sample locations to generate GP
        Ns = 500
        sig = 0.001   # measurement noise
        xInds = np.random.choice(Nx, Ns)
        yInds = np.random.choice(Ny, Ns)
        samps = np.vstack((xx[xInds], yy[yInds])).T
        meas = np.zeros(Ns)

        # measurement based on distance from boundary
        for ii in range(Ns):
            loc = samps[ii,:]
            dist = np.min(np.linalg.norm(np.tile(loc, (len(bb),1)) - np.vstack((xx, bb)).T, axis=1))
            if loc[1] > bb[xInds[ii]]:
                meas[ii] = sig*np.random.randn() - dist
            else:
                meas[ii] = sig*np.random.randn() + dist

        # regress two-dimensional GP field
        gpr = gpy.models.gp_regression.GPRegression(samps, meas[:,None], kernel=k2)
        y, _ = gpr.predict(xy)
        Y = y.reshape(Nx, Ny)
        
        allBoundaries[:,ll,mc] = bb
        allFields[:,:,ll,mc] = Y

#np.savez('gpTrainData.npz', xx=xx, yy=yy, allBoundaries=allBoundaries, allFields=allFields, lenScales=lenScales)
np.savez('gpTestData.npz', xx=xx, yy=yy, allBoundaries=allBoundaries, allFields=allFields, lenScales=lenScales)

## generation figures
#levels = [-0.7, -0.5, -0.3, 0, 0.3, 0.5, 0.7]
#CS = plt.contour(xx, yy, Y.T, levels, alpha=1.0)
#plt.contourf(xx, yy, Y.T, levels, alpha=0.2)
#CS.collections[3].set_color('black')
#plt.plot(xx, bb)
##plt.scatter(samps[:,0], samps[:,1], c=meas)
#plt.show()

#Ts = 1
#Tt = 1000
#h = 0
#stopErr = 0.07
#xInit = np.array([min(xx), min(yy)])
#totalCost, trueErr, samps, meas = truvar(Y, xx, yy, k2, h, sig, stopErr, xInit, Ts, Tt, Tmax=100)
#sampArray = np.array(samps)
#measArray = np.array(meas)

#levels = [-0.7, -0.5, -0.3, 0, 0.3, 0.5, 0.7]
#plt.figure()
#CS = plt.contour(xx, yy, Y.T, levels, alpha=1.0)
#plt.contourf(xx, yy, Y.T, levels, alpha=0.2)
#CS.collections[3].set_color('black')
#plt.plot(xx, bb)
#plt.plot(sampArray[:,0], sampArray[:,1], '--', c='gray')
#plt.scatter(sampArray[:,0], sampArray[:,1], c=measArray)
#plt.show()

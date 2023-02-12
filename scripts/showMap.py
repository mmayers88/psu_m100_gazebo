import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

Nx = 1000
Ny = 1000
xx = np.linspace(0.,1.,Nx)
yy = np.linspace(0.,1.,Ny)

Y = pd.read_csv("array.csv",header=None)
colnames=['TIME', 'GPS_X', 'GPS_Y', 'a_x', 'a_y', 'b_x', 'b_y'] 
df = pd.read_csv("data_text_firstRun.csv", names=colnames, header=None)

print(df)

df[['a_x', 'a_y', 'b_x', 'b_y']] = df[['a_x', 'a_y', 'b_x', 'b_y']].astype(int)/1000
df[['a_y', 'b_y']] = np.abs(df[['a_y','b_y']])
print(df)



plt.contourf(xx, yy, Y)

plt.scatter(df[['a_x']],df[['a_y']],c ="red",
            linewidths = 1,
            marker ="^",
            edgecolor ="black")
plt.scatter(df[['b_x']],df[['b_y']],c ="green",
            linewidths = 1,
            marker ="v",
            edgecolor ="black")

plt.xlim(0, 1)
plt.ylim(0, 1)
plt.colorbar()
plt.show()
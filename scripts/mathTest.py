import numpy as np
import math

def rotate(xy, degrees=0, origin=(0, 0)):
    '''angle = np.deg2rad(degrees)
    R = np.array([[np.cos(angle), -np.sin(angle)],
                  [np.sin(angle),  np.cos(angle)]])
    o = np.atleast_2d(origin)
    p = np.atleast_2d(p)
    return np.squeeze((R @ (p.T-o.T) + o.T).T)'''
    """Rotate a point around a given point.
    
    I call this the "high performance" version since we're caching some
    values that are needed >1 time. It's less readable than the previous
    function but it's faster.
    """
    radians = np.deg2rad(degrees)
    x, y = xy
    offset_x, offset_y = origin
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = math.cos(radians)
    sin_rad = math.sin(radians)
    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y
    return (qx,qy)

    

def rot_cell_points(origin, dir, buff = 10):
    arr = np.array(
        [(origin[0], origin[1]),(origin[0], origin[1]+buff),(origin[0]+buff, origin[1]+buff),(origin[0]+buff, origin[1])]
    )
    print("Original Arr:")
    print(arr)
    if dir == 0:
        return arr
    if dir == 1:
        arr[0] = rotate(arr[0], 90, arr[0])
        arr[1] = rotate(arr[1], 90, arr[0])
        arr[2] = rotate(arr[2], 90, arr[0])
        arr[3] = rotate(arr[3], 90, arr[0])
    if dir == 2:
        arr[0] = rotate(arr[0], 180, arr[0])
        arr[1] = rotate(arr[1], 180, arr[0])
        arr[2] = rotate(arr[2], 180, arr[0])
        arr[3] = rotate(arr[3], 180, arr[0])
    if dir == 3:
        arr[0] = rotate(arr[0], 270, arr[0])
        arr[1] = rotate(arr[1], 270, arr[0])
        arr[2] = rotate(arr[2], 270, arr[0])
        arr[3] = rotate(arr[3], 270, arr[0])
    print("arr")
    print(arr.astype(int))
    return arr.astype(int)


def main():
    x = rot_cell_points((16,0),1)
    print(x[0][1])

if __name__ == "__main__":
    main()



import numpy as np
from PIL import Image
A = np.genfromtxt('array.csv', delimiter=',')
A *= (255.0/A.max())
#A = np.flip(A,0)
#A = np.flip(A,1)
#im = Image.fromarray(np.flip(A,1))
im = Image.fromarray(A)
#im = im.rotate(180)
im.convert('L').save('array.png')
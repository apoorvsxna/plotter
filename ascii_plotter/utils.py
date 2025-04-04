import math as _math

def _sign(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1

def _transpose(mat):
    return [[x[i] for x in mat] for i in range(len(mat[0]))]

def _y_reverse(mat):
    return [list(reversed(row)) for row in mat]

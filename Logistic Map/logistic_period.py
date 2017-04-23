import time


def getPeriod(a, maxP, trans, tol):
    x = 0.12345
    for n in range(trans):
        x = a * x * (1 - x)
    orbit = []
    for n in range(maxP):
        x = a * x * (1 - x)
        for i, val in enumerate(orbit):
            if abs(x - val) < tol:
                return len(orbit) - i
        orbit.append(x)
    return -1


def bsearch(array, obj):
    l = 0
    r = len(array) - 1
    if l > r:
        return -1, -1
    while l < r - 1:
        m = (l + r) // 2
        if array[m][0] < obj:
            l = m
        else:
            r = m
    if l == r:
        return l, l + 1
    else:
        return l, r


def insert(array, obj, idx):
    l = len(array)
    if l == 0:
        array.append((obj, idx))
    elif l == 1:
        if array[0][0] < obj:
            array.insert(1, (obj, idx))
        else:
            array.insert(0, (obj, idx))
    else:
        if obj < array[0][0]:
            array.insert(0, (obj, idx))
        elif obj > array[-1][0]:
            array.append((obj, idx))
        else:
            _, z = bsearch(array, obj)
            array.insert(z, (obj, idx))


def getPeriodFast(a, maxP, trans, tol):
    x = 0.12345
    for n in range(trans):
        x = a * x * (1 - x)

    orbit = []
    x = a * x * (1 - x)
    orbit.append((x, 0))
    x = a * x * (1 - x)
    if abs(orbit[0][0] - x) < tol:
        return 1
    insert(orbit, x, 1)

    for n in range(2, maxP):
        x = a * x * (1 - x)
        y, z = bsearch(orbit, x) # indexes of closest
        if y >= 0 and abs(orbit[y][0] - x) < tol:
            return len(orbit) - orbit[y][1]
        if z >= 0 and abs(orbit[z][0] - x) < tol:
            return len(orbit) - orbit[z][1]
        '''
        for i, val in enumerate(orbit):
            if abs(x - val) < tol:
                return len(orbit) - i
        '''
        insert(orbit, x, n)
    return -1


if __name__ == '__main__':
    a = 4
    maxP = 10000
    trans = 1000
    tol = 0.0000000001
    s = time.time()
    p = getPeriod(a, maxP, trans, tol)
    e = time.time()
    print('1: %i in %.5f ms' % (p, ((e - s) * 1000)))
    s = time.time()
    p = getPeriodFast(a, maxP, trans, tol)
    e = time.time()
    print('2: %i in %.5f ms' % (p, ((e - s) * 1000)))

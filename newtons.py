


def newtons(f, fprime, guess, max_iter, threshold):
    if abs(f(guess)) < threshold:
        return guess, 0
    for i in range(max_iter):
        if fprime(guess) == 0:
            return guess, -2
        guess = guess - f(guess) / fprime(guess)
        if abs(f(guess)) < threshold:
            return guess, i
    return guess, -1



'''
class NewtonScreen(pyg.screen.GraphScreen):
    def __init__(self, x, y, width, height, valset, zoom_valobj, bg=(255, 255, 255), visible=True):
        super().__init__(x, y, width, height, valset, zoom_valobj, bg=(255, 255, 255), visible=True)
'''




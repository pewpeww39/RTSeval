<<<<<<< HEAD
import numpy as np

def frange(start: float, end: float, step: float):
    """
    Generate a list of floating numbers within a specified range.

    :param start: range start
    :param end: range end
    :param step: range step
    :return:
    """
    numbers = np.linspace(start, end,(end-start)*int(1/step)+1).tolist()
    return [round(num, 2) for num in numbers]

# sweepL = frange(0, 1.2, 0.24)
swpL = np.linspace(0, 1.2)
print(swpL)
=======
import numpy as np

def frange(start: float, end: float, step: float):
    """
    Generate a list of floating numbers within a specified range.

    :param start: range start
    :param end: range end
    :param step: range step
    :return:
    """
    numbers = np.linspace(start, end,(end-start)*int(1/step)+1).tolist()
    return [round(num, 2) for num in numbers]

# sweepL = frange(0, 1.2, 0.24)
swpL = np.linspace(0, 1.2)
print(swpL)
>>>>>>> 954aaee1d78f9b3e5ca8bd37ca83d9463dc5642f
print(pow(10, -5))

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
print(pow(10, -3))
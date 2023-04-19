import numpy as np
import matplotlib.pyplot as plt

# Generate some example data
t = np.linspace(0, 10, 1000)
y = np.concatenate((np.zeros(500), np.ones(500)), axis=None)
y += np.random.normal(scale=0.1, size=len(t))

# Find the indices of the steps in the data
step_indices = np.where(np.abs(np.diff(y)) > 0.5)[0]

# Plot the data with the steps marked
plt.plot(t, y, 'b', label='Data')
plt.plot(t[step_indices], y[step_indices], 'ro', label='Steps')
plt.legend()
plt.show()

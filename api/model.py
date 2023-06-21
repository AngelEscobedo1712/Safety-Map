import numpy as np
import pandas as pd

from pathlib import Path
# from colorama import Fore, Style

from registry import save_model

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import numpy as np

# Create feature and target arrays
X = np.array([[1], [2], [3], [4], [5], [6], [7]], dtype=float)
y = np.array([2, 3, 4, 5, 6, 7, 8], dtype=float)

# Normalize data (this is important for neural networks)
X /= np.amax(X)
y /= np.amax(y)

# Create a Sequential model
model = Sequential()

# Add a Dense layer with 1 unit and input_shape of 1, and use the sigmoid activation function
model.add(Dense(1, input_shape=(1,), activation='sigmoid'))

# Compile the model
model.compile(optimizer=Adam(), loss='mean_squared_error')

# Fit the model
model.fit(X, y, epochs=200)

# Save the model
save_model(model)

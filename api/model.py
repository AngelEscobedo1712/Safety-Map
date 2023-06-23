import numpy as np
import pandas as pd

from pathlib import Path
# from colorama import Fore, Style

from registry import save_model

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import numpy as np


import matplotlib.pyplot as plt
from typing import Tuple

pd.set_option('display.max_columns', 500)

#TensorFlow
from tensorflow.keras import models
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras import optimizers, metrics
from tensorflow.keras.regularizers import L1L2
from tensorflow.keras.callbacks import EarlyStopping

url = "https://storage.googleapis.com/safetymap/preprocessed_data3.csv"

def get_data(url):
  df = pd.read_csv(url)
  df.drop(columns = "colonia_id", inplace = True)
  pre_data = df.set_index(["year_month_hecho","alcaldia_colonia"]).unstack("alcaldia_colonia")

  return df,pre_data

############
INPUT_LENGTH = 1 * 12 # records every 1 month x 12 months per year = 12 months
TRAIN_TEST_RATIO = 0.70 #70% of the data is going to be for training
############

def train_test_split(fold:pd.DataFrame,
                     train_test_ratio: float,
                     input_length: int) -> Tuple[pd.DataFrame]:
    """From a fold dataframe, take a train dataframe and test dataframe based on
    the split ratio.
    - df_train should contain all the timesteps until round(train_test_ratio * len(fold))
    - df_test should contain all the timesteps needed to create all (X_test, y_test) tuples

    Args:
        fold (pd.DataFrame): A fold of timesteps
        train_test_ratio (float): The ratio between train and test 0-1
        input_length (int): How long each X_i will be

    Returns:
        Tuple[pd.DataFrame]: A tuple of two dataframes (fold_train, fold_test)
    """
    fold_train = fold[0:round(len(fold)*train_test_ratio)]
    fold_test = fold[(round(len(fold)*train_test_ratio - input_length)):]
    return fold_train,fold_test

##########################
SEQUENCE_STRIDE = 1
OUTPUT_LENGTH = 12
TARGET = ['burglary', 'danger_of_well-being',
       'domestic_violence', 'fraud', 'homicide', 'property_damage',
       'robbery_with_violence', 'robbery_without_violence', 'sexual_crime',
       'threats']
##########################

def get_X_y_strides(fold: pd.DataFrame, input_length: int, output_length: int,
    sequence_stride: int) -> Tuple[np.array]:
    """slides through a `fold` Time Series (2D array) to create sequences of equal
        * `input_length` for X,
        * `output_length` for y,
    using a temporal gap `sequence_stride` between each sequence

    Args:
        fold (pd.DataFrame): One single fold dataframe
        input_length (int): Length of each X_i
        output_length (int): Length of each y_i
        sequence_stride (int): How many timesteps to take before taking the next X_i

    Returns:
        Tuple[np.array]: A tuple of numpy arrays (X, y)
    """
    for i in range(0, len(fold), sequence_stride):
        # Exits the loop as soon as the last fold index would exceed the last index
        if (i + input_length + output_length) >= len(fold):
            break
        X_i_transformed = fold.iloc[i:i + input_length, :]
        y_i_transformed = fold.iloc[i + input_length:i + input_length + output_length, :][TARGET]

        fold_train_list = X_i_transformed.stack("alcaldia_colonia").groupby(["alcaldia_colonia", "year_month_hecho"])\
                            .apply(lambda x: x.values.tolist()[0])\
                            .groupby("alcaldia_colonia").apply(lambda x: x.values.tolist())\
                            .tolist()

        fold_test_list = y_i_transformed.stack("alcaldia_colonia").groupby(["alcaldia_colonia", "year_month_hecho"])\
                            .apply(lambda x: x.values.tolist()[0])\
                            .groupby("alcaldia_colonia").apply(lambda x: x.values.tolist())\
                            .tolist()

    return (np.array(fold_train_list), np.array(fold_test_list))



def init_model(X_train, y_train):
    model = Sequential()

    # –– Model
    model.add(layers.Masking(mask_value=-1, input_shape=(12,10)))
    model.add(layers.LSTM(units=40, activation='tanh', return_sequences =True))
    model.add(layers.Dense(50, activation='relu'))
    model.add(layers.Dropout(rate=0.2))  # The rate is the percentage of neurons that are "killed"
    model.add(layers.Dense(10, activation='relu'))

    # –– Compilation
    model.compile(loss='mse',
                  optimizer='adam',
                 metrics = ["mae"])

    return model


def make_the_dataframe(predictions):
# Date Series for the prediction dataframe
    start_date = '2023-01-01'
    num_periods = 12
    date_range = pd.date_range(start=start_date, periods=num_periods, freq='MS')
    date_series = pd.Series(range(num_periods), index=date_range)

    # Empty list to save the list of dataframes
    p1 = []
    nom_delitos = df.columns[2:]
    nom_colonias = df.alcaldia_colonia.unique()

    for period in range(predictions.shape[1]):
        p1.append(pd.DataFrame(predictions[:, period, :], columns =nom_delitos, index = nom_colonias).assign(periodo= date_series.index[period].date()))

    new_prediction = pd.concat(p1)
    prediction_dataframe = new_prediction.set_index("periodo",append=True).round(0).astype(int)

    return prediction_dataframe


#Get Fold_train  and Fold_test

(df, pre_data) = get_data(url)

(fold_train, fold_test) = train_test_split(pre_data, TRAIN_TEST_RATIO, INPUT_LENGTH)

# Running the Train function for X and y
X_train, y_train = get_X_y_strides(fold_train, INPUT_LENGTH, OUTPUT_LENGTH, SEQUENCE_STRIDE)

# Running the Test functeion for X and y
X_test, y_test = get_X_y_strides(fold_test, INPUT_LENGTH, OUTPUT_LENGTH, SEQUENCE_STRIDE)

#initiate model
model = init_model(X_train, y_train)

# Early Stopping with patience 10
es = EarlyStopping(patience=10)

# Fiting Model
model.fit(X_train, y_train,
          epochs=200,
          batch_size=32,
          verbose=1,
          callbacks = [es],
          validation_split=0.2)

print("Yaaay! Your Model Seems to Work!")

# Let us get the predictions!
predictions = model.predict(X_test)

prediction_dataframe = make_the_dataframe(predictions)

print("We are Ready!, try with these predictions")

# Save the model
save_model(model)















# Create feature and target arrays
#X = np.array([[1], [2], [3], [4], [5], [6], [7]], dtype=float)
#y = np.array([2, 3, 4, 5, 6, 7, 8], dtype=float)

# Normalize data (this is important for neural networks)
#X /= np.amax(X)
#y /= np.amax(y)

# Create a Sequential model
#model = Sequential()

# Add a Dense layer with 1 unit and input_shape of 1, and use the sigmoid activation function
#model.add(Dense(1, input_shape=(1,), activation='sigmoid'))

# Compile the model
#model.compile(optimizer=Adam(), loss='mean_squared_error')

# Fit the model
#model.fit(X, y, epochs=200)

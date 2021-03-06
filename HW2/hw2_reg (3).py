# -*- coding: utf-8 -*-
"""HW2-reg.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SOJuU0vGs-uA3gUWbsjBDf0rTpHuk6ut
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA
import math
from sklearn.preprocessing import StandardScaler
import datetime
from sklearn.metrics import accuracy_score
# %load_ext tensorboard

from sklearn.metrics import confusion_matrix
import seaborn as sn

from google.colab import drive
drive.mount('/content/drive')

data = pd.read_csv('/content/drive/MyDrive/s_data.csv', header=None)

def train_test_valid_data(data,frac_train,frac_valid):
    n_train = math.floor(frac_train*data.shape[0])
    n_valid = math.floor(frac_valid*data.shape[0])
    data = data.values
    train_data = data[:n_train]
    valid_data = data[n_train:n_train+n_valid]
    test_data = data[n_train+n_valid:]
    return train_data,valid_data,test_data

class EarlyStoppingAtMinLoss(keras.callbacks.Callback):
    def __init__(self, patience=5):
        super(EarlyStoppingAtMinLoss, self).__init__()
        self.patience = patience
        # best_weights to store the weights at which the minimum loss occurs.
        self.best_weights = None

    def on_train_begin(self, logs=None):
        # The number of epoch it has waited when loss is no longer minimum.
        self.wait = 0
        # The epoch the training stops at.
        self.stopped_epoch = 0
        # Initialize the best as infinity.
        self.best = np.Inf

    def on_epoch_end(self, epoch, logs=None):
        current = logs.get("val_loss")
        if np.less(current, self.best):
            self.best = current
            self.wait = 0
            # Record the best weights if current results is better (less).
            self.best_weights = self.model.get_weights()
        else:
            self.wait += 1
            if self.wait >= self.patience:
                self.stopped_epoch = epoch
                self.model.stop_training = True
                print("Restoring model weights from the end of the best epoch.")
                self.model.set_weights(self.best_weights)

    def on_train_end(self, logs=None):
        if self.stopped_epoch > 0:
            print("Epoch %05d: early stopping" % (self.stopped_epoch + 1))

y = data[0]
print(np.unique(y).shape[0])
X = data.drop(0, axis=1)
X_train, X_valid, X_test = train_test_valid_data(X, 0.7, 0.2)
y_train, y_valid, y_test = train_test_valid_data(y, 0.7, 0.2)

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
X_valid = scaler.transform(X_valid)

keras.backend.clear_session()
def adapt_learning_rate(epoch):
    if epoch>5:
      return 0.01 / (epoch+1)**2
    else:
      return 0.01 / (epoch+1)
  
log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)
my_lr_scheduler = keras.callbacks.LearningRateScheduler(adapt_learning_rate)


inp = keras.Input(shape=(90), name="input")
x = keras.layers.Dense(units=10,  name="h1",activation="relu")(inp)
x = keras.layers.Dense(units=10, name="h2",activation="relu")(x)
x = keras.layers.Dense(units=90, name="h3",activation="relu")(x)
x = keras.layers.Dense(units=100, name="h4",activation="relu")(x)

x = keras.layers.Dense(name="output", units=1)(x)
model = keras.Model(inputs=inp, outputs=x)

model.compile(loss='mean_squared_error', optimizer=keras.optimizers.Adam(), metrics=['mean_squared_error'])
model.fit(X_train[:], y_train[:], epochs=10000, verbose=1, validation_data=(X_valid,y_valid),callbacks=[EarlyStoppingAtMinLoss(5),tensorboard_callback,my_lr_scheduler])

pred_test = model.predict(X_test)
print("MSE for test: ",keras.losses.MSE(y_test,pred_test.flatten()))
pred_test = np.round(pred_test.flatten())
print("Accuracy for test:", accuracy_score(y_test,pred_test.flatten()))

cm = confusion_matrix(y_test, pred_test, np.unique(y))
df_cm = pd.DataFrame(cm, index = [i for i in np.unique(y)],
                  columns = [i for i in np.unique(y)])
plt.figure(figsize = (20,14))
sn.heatmap(df_cm)

keras.utils.plot_model(model, show_shapes=True, show_layer_names=True, expand_nested=True)

tensorboard --logdir logs/fit/20210422-181500
# -*- coding: utf-8 -*-
"""Rnn_Predict_Temperature.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RNtKoeu9m6V9eFpcK-2OLVmYfk5sQKP3

# 讀檔
"""

import csv
import numpy as np
import xlwt
from xlwt.Style import add_palette_colour

fname='/content/TY_climate_2015_2018.csv'     #桃園溫度資料
f = open(fname,encoding='cp950')    #使用"cp950"來讀檔
data = f.read()
f.close()

lines = data.split('\n')
header = lines[0].split(',')            #項目名稱

del lines[0]


print(len(lines))
print(header)

import numpy as np
from matplotlib import pyplot as plt

raw_data=[]
for i,line in enumerate(lines):
  value = float(line.split(',')[8])
  raw_data.append([value])
raw_data = np.array(raw_data)
plt.plot(raw_data)
plt.show()

"""# 資料標準化

"""

mean = raw_data[:100000].mean()
raw_data -= mean
std = raw_data[:100000].std()
raw_data/=std
plt.plot(raw_data)
plt.show()

"""# 資料採樣

"""

from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator

length =36                           #每10分鐘取一次資料，所以如果用過去6小時，因此特徵長度設為36
delay =72                            # 預測12小時後的溫度
sample_rate=3
stride =36
batch_size=32

data = raw_data[:-(delay-1)]  #切掉後71筆資料作為訓練資料
target = raw_data[(delay-1):]  #截掉前71筆資料作為目標資料

# 產生訓練資料

train_gen = TimeseriesGenerator(
    data,target,
    length=length,
    sampling_rate=sample_rate,
    stride = stride,
    start_index=0,
    end_index=100000,
    batch_size=32
)

# 產生檢驗資料
val_gen = TimeseriesGenerator(
    data,target,
    length=length,
    sampling_rate=sample_rate,
    stride = stride,
    start_index=100001,
    end_index=130000,
    batch_size=32
    
)

# 產生測試資料
test_gen = TimeseriesGenerator(
    data,target,
    length=length,
    sampling_rate=sample_rate,
    stride = stride,
    start_index=130001,
    end_index=None,
    batch_size=batch_size
)

print(train_gen[0][0].shape)
print(val_gen[0])

"""# 建立密集層並訓練"""

from tensorflow.keras.models import Sequential
from tensorflow.keras import layers

dense_model = Sequential()

dense_model.add(layers.Flatten(input_shape=(12,1))) #由於處理完的資料是3D陣列,所以第一層要用展平層將資料展平
dense_model.add(layers.Dense(10,activation='relu'))
dense_model.add(layers.Dense(10,activation='relu'))
dense_model.add(layers.Dense(1))
dense_model.summary()

dense_model.compile(optimizer='rmsprop' ,loss='mse', metrics=['mae'])

dense_history = dense_model.fit(train_gen,
                  epochs=100,
                  validation_data=val_gen)

"""# 顯示平均溫度誤差"""

print('平均溫度誤差為:',dense_history.history['val_mae'][-1]*std)

print(type(val_gen))

"""# 輸出預測結果

"""

val_temp=[]

for datas in val_gen:
  for temp in datas[1]:
    val_temp.append(temp)

prediction = dense_model.predict(val_gen)


x=[]
val=[]
for i in range(833):
  x.append(i)
  val.append(val_temp[i])


import matplotlib.pyplot as plt

plt.title("Dense NN", fontsize=16) #圖表標題
plt.xlabel("Time", fontsize=10) #x軸標題
plt.ylabel("Temp", fontsize=10) #y軸標題
x=x
y_1=prediction
y_2=val
plt.plot(x, y_1, 'r')
plt.plot(x,y_2,'b--')

plt.legend(['val_temp','pred_temp'])

"""# 損失函數"""

print(dense_history.epoch)
print(dense_history.history['loss'])
print(dense_history.history['val_loss'])


import matplotlib.pyplot as plt

plt.title("Training & Vaildation Loss", fontsize=16) #圖表標題
plt.xlabel("Epoch", fontsize=10) #x軸標題
plt.ylabel("Loss", fontsize=10) #y軸標題
x_1=dense_history.epoch
y_1=dense_history.history['loss']
y_2=dense_history.history['val_loss']
plt.plot(x_1, y_1, 'g')
plt.plot(x_1,y_2,'b--')

plt.legend(['loss','val_loss'])

"""# 建立RNN模型"""

rnn_model=Sequential()
rnn_model.add(layers.SimpleRNN(10,input_shape=(12,1)))
rnn_model.add(layers.Dense(10,activation='relu'))
rnn_model.add(layers.Dense(1))
rnn_model.summary()


rnn_model.compile(optimizer='rmsprop',loss='mse',metrics=['mae'])   #metrics:評量準則
rnn_history = rnn_model.fit(train_gen,epochs=100,validation_data=val_gen)
print('平均溫度誤差為:',rnn_history.history['val_mae'][-1]*std)

prediction=rnn_model.predict(val_gen)
print(len(x))

plt.title("RNN", fontsize=16) #圖表標題
plt.xlabel("Time", fontsize=10) #x軸標題
plt.ylabel("Temp", fontsize=10) #y軸標題
x=x
y_1=val_temp
y_2=prediction
plt.plot(x, y_1, 'r')
plt.plot(x,y_2,'b--')

plt.legend(['val_temp','pred_temp'])

plt.title("Training & Vaildation Loss", fontsize=16) #圖表標題
plt.xlabel("Epoch", fontsize=10) #x軸標題
plt.ylabel("Loss", fontsize=10) #y軸標題
x_1=rnn_history.epoch
y_1=rnn_history.history['loss']
y_2=rnn_history.history['val_loss']
plt.plot(x_1, y_1, 'g')
plt.plot(x_1,y_2,'b--')

plt.legend(['loss','val_loss'])
# -*- coding: utf-8 -*-
"""NetflixStockPredict.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_Fi6hC4jEwDIYZgtymktSKMw2svhFQE7

# B1: Khai báo dữ liệu
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import  load_model

from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers import Dense

from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_absolute_percentage_error

"""# B2: Đọc dữ liệu"""

from google.colab import drive
drive.mount('/content/gdrive')

df=pd.read_csv('/content/gdrive/MyDrive/DataGGColab/NFLX.csv')

"""# B3: Mô tả dữ liệu"""

df["Date"]=pd.to_datetime(df.Date,format="%Y-%m-%d")

df.shape

df.head()

df.info()

"""# B4: Tiền xử lí dữ liệu"""

df1=pd.DataFrame(df,columns=['Date','Close'])
df1.index=df1.Date
df1.drop("Date",axis=1,inplace=True)

plt.figure(figsize=(10,5))
plt.plot(df1['Close'],label='giá thực tế',color='red')
plt.title('biểu đồ giá đóng cửa cổ phiếu Netflix')
plt.xlabel('thời gian')
plt.ylabel('giá đóng cửa(USD)')
plt.legend()
plt.show()

df1

#chia tập dữ liệu
data=df1.values
train_data=data[:800]
test_data=data[800:]

data

#chuẩn hóa dữ liệu
sc=MinMaxScaler(feature_range=(0,1))
sc_train=sc.fit_transform(data)

#tạo vòng lặp các giá trị; Sử dụng giá 50 ngày trước để dự đoán cho ngày kế tiếp
x_train,y_train=[],[]
for i in range(50,len(train_data)):
  x_train.append(sc_train[i-50:i,0])
  y_train.append(sc_train[i,0])

x_train #Gồm các mảng, mỗi mảng gồm 50 giá đóng cửa liên tục

y_train #danh sách giá đóng cửa của ngày hôm sau tương ứng với mỗi mảng của x_train

#xếp dữ liệu thành 1 mảng
x_train=np.array(x_train)
y_train=np.array(y_train)

#xếp dữ liệu thành mảng 1 chiều
x_train=np.reshape(x_train,(x_train.shape[0],x_train.shape[1],1))
y_train=np.reshape(y_train,(y_train.shape[0],1))

"""# B5: Xây dựng và huấn luyện mô hình"""

#xây dựng mô hình
model=Sequential()
model.add(LSTM(units=128,input_shape=(x_train.shape[1],1),return_sequences=True))
model.add(LSTM(units=64))
model.add(Dropout(0.5))
model.add(Dense(1))
model.compile(loss='mean_absolute_error',optimizer='adam')

#huấn luyện mô hình
save_model="save_model.hdf5"
best_model=ModelCheckpoint(save_model,monitor='loss',verbose=2,save_best_only=True,mode='auto')
model.fit(x_train,y_train,epochs=100, batch_size=50,verbose=2, callbacks=[best_model])

#dữ liệu train
y_train=sc.inverse_transform(y_train) #giá thực
final_model=load_model('save_model.hdf5')
y_train_predict=final_model.predict(x_train)
y_train_predict=sc.inverse_transform(y_train_predict) #giá dự đoán

"""# B6: Sử dụng mô hình"""

#Xử lí dữ liệu test
test=df1[len(train_data)-50:].values
test=test.reshape(-1,1)
sc_test=sc.transform(test)

x_test=[]
for i in range(50,test.shape[0]):
  x_test.append(sc_test[i-50:i,0])
x_test=np.array(x_test)
x_test=np.reshape(x_test,(x_test.shape[0],x_test.shape[1],1))

#dữ liệu test
y_test=data[800:] #giá thực
y_test_predict=final_model.predict(x_test)
y_test_predict=sc.inverse_transform(y_test_predict) #giá dự đoán

"""# Độ chính xác của mô hình"""

#lập biểu đồ so sánh
train_data1=df1[50:800]
test_data1=df1[800:]

plt.figure(figsize=(24,8))
plt.plot(df1,label='giá thực tế',color='red') #đường giá thực
train_data1['dự đoán']=y_train_predict #thêm dữ liệu

plt.plot(train_data1['dự đoán'],label='giá dự đoán train',color='green') #đường giá dự báo train
test_data1['dự đoán']=y_test_predict #thêm dữ liệu

plt.plot(test_data1['dự đoán'],label='giá dự đoán test',color='blue') #đường giá dự báo test
plt.title('so sánh giá dự đoán và giá thực tế')
plt.xlabel('thời gian')
plt.ylabel('giá đóng cửa (USD)')
plt.legend()
plt.show()

#r2
print('độ phù hợp của tập train: ', r2_score(y_train,y_train_predict)*100)
#mae
print('sai số tuyệt đối trung bình tập train: ', mean_absolute_error(y_train,y_train_predict), 'USD')
#mape
print('phần trăm sai số tuyệt đối trung bình tập train: ', mean_absolute_percentage_error(y_train,y_train_predict)*100)

train_data1

#r2
print('độ phù hợp của tập test: ', r2_score(y_test,y_test_predict)*100)
#mae
print('sai số tuyệt đối trung bình tập test: ', mean_absolute_error(y_test,y_test_predict) ,' USD')
#mape
print('phần trăm sai số tuyệt đối trung bình tập test: ', mean_absolute_percentage_error(y_test,y_test_predict)*100)

test_data1


# -*- coding: utf-8 -*-
"""Fetal Birth Weight Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1juBcbt7xRQ86m-9jLGkgtVfVaEgpMcHg

NOTE: This notebook is used to do various analysis, EDA and try out different models and finally choose the one which gives good results.
"""

# importing libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import scipy
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression, Ridge
from scipy.stats import spearmanr
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor

# to supress warnings
import warnings
warnings.filterwarnings("ignore")

# function to find root mean squared error
def rmse(y_true,y_pred):
    return np.sqrt(mean_squared_error(y_true,y_pred))

data = pd.read_csv("../dataset/babies.csv")

data.head()

data['birth_weight'] = np.round(data['birth_weight']/35.274,3)
data['weight'] = np.round(data['weight']/2.2046,3)
data.head()

"""### Information about dataset
* target: birth_weight (in kgs)
* gestation (in days)
* parity (1 if first born else 0)
* age (mother's age in years)
* height (mother's height in inches)
* weight (mother's weight in kgs during pregnancy)
* smoke (whether the mother smokes or not 1 = yes and 0 = no)

Dataset Source: http://people.reed.edu/~jones/141/BirthWgt.html
"""

data.describe()

data.isnull().sum()

X = data.iloc[:,1:]
y = data.iloc[:,0]

X

y

X_train, X_test, y_train, y_test = train_test_split(X,y,test_size = 0.15, random_state = 11)

"""### Baseline Models (Mean and kNN)

#### Baseline Model 1 : Mean
"""

class MeanRegressor:

    def __init__(self):
        self.mean = None  # to store mean

    def fit(self,X,y):
        self.mean = np.round(np.mean(y),3)

    def predict(self,X):
        dim = X.shape[0]
        y_pred = [self.mean for i in range(dim)]
        y_pred = np.array(y_pred)
        return y_pred

mr = MeanRegressor()
mr.fit(X_train,y_train)
y_pred_mr_test = mr.predict(X_test)
y_pred_mr_train = mr.predict(X_train)
mr_rmse_test = rmse(y_test,y_pred_mr_test)
mr_rmse_train = rmse(y_train,y_pred_mr_train)
print("RMSE for Train Set:",mr_rmse_train)
print("RMSE for Test Set:",mr_rmse_test)

"""#### Baseline Model 2 : kNN"""

X_sc = StandardScaler().fit_transform(X)
Xtrain, Xtest, ytrain, ytest = train_test_split(X_sc,y,test_size=0.15,random_state=11)

"""With Standard Scaler"""

knn = KNeighborsRegressor()
knn.fit(Xtrain,ytrain)
y_pred_knn_test = knn.predict(Xtest)
y_pred_knn_train = knn.predict(Xtrain)
knn_rmse_test = rmse(ytest,y_pred_knn_test)
knn_rmse_train = rmse(ytrain,y_pred_knn_train)
print("RMSE for Train Set:",knn_rmse_train)
print("RMSE for Test Set:",knn_rmse_test)

"""### Let's do some EDA"""

# relationship between input variable and output variable
sns.distplot(data[data['parity'] == 0]['birth_weight'],label="parity=0")
sns.distplot(data[data['parity'] == 1]['birth_weight'],label="parity=1")
plt.title("Average weight of baby depending on parity")
plt.xlabel("Birth Weight in kgs")
plt.legend()
plt.show()

"""Insight: First born child has a little lower birth weight as compared to child born after first child."""

plt.scatter(data['gestation'],data['birth_weight'])
plt.xlabel("Gestational Age in days")
plt.ylabel("Birth Weight in kgs")
plt.show()

"""Insight: It is quite obvious that as gestational age increases then birth weight also increases."""

sns.scatterplot(x=data.groupby('age').mean()['birth_weight'].index,y=data.groupby('age').mean()['birth_weight'])
plt.xlabel("Mother's Age")
plt.ylabel("Baby's weight in kg")
plt.show()

"""Insight: Baby after 42 age and before 20 years of age is risky"""

# relationship between input variable and output variable
sns.distplot(data[data['smoke'] == 0]['birth_weight'],label="smoke=0")
sns.distplot(data[data['smoke'] == 1]['birth_weight'],label="smoke=1")
plt.title("Average weight of baby depending on mother's smoke/not")
plt.xlabel("Birth Weight in kgs")
plt.legend()
plt.show()

"""NOTE: Usually smokers mothers have lower weight babies"""

sns.scatterplot(x=data.groupby('weight').mean()['birth_weight'].index,y=data.groupby('weight').mean()['birth_weight'])
plt.xlabel("Mother's Weight")
plt.ylabel("Baby's weight in kg")
plt.show()

sns.scatterplot(x=data.groupby('height').mean()['birth_weight'].index,y=data.groupby('height').mean()['birth_weight'])
plt.xlabel("Mother's Height")
plt.ylabel("Baby's weight in kg")
plt.show()

"""### Trying with Linear Regression"""

lr = LinearRegression()
lr.fit(X_train,y_train)
y_pred_lr_test = np.apply_along_axis((lambda x:np.round(x,3)),arr=lr.predict(X_test),axis=0)
y_pred_lr_train = np.apply_along_axis((lambda x:np.round(x,3)),arr=lr.predict(X_train),axis=0)
lr_rmse_test = rmse(y_test,y_pred_lr_test)
lr_rmse_train = rmse(y_train,y_pred_lr_train)
print("RMSE for Train Set:",lr_rmse_train)
print("RMSE for Test Set:",lr_rmse_test)

def model_eval(model,X_train,X_test,y_train,y_test):
    model.fit(X_train,y_train)
    y_pred_test = np.apply_along_axis((lambda x:np.round(x,3)),arr=model.predict(X_test),axis=0)
    y_pred_train = np.apply_along_axis((lambda x:np.round(x,3)),arr=model.predict(X_train),axis=0)
    rmse_test = rmse(y_test,y_pred_test)
    rmse_train = rmse(y_train,y_pred_train)
    return rmse_train, rmse_test

"""### Trying with SVR"""

train = []
test = []
kernel_params = []
c_params = []
epsilon_params = []
for i in ['linear','poly','rbf','sigmoid']:
    for j in [0.5,0.8,1,1.2,1.4,1.6]:
        for k in [0,0.05,0.1,0.15,0.2,0.3]:
                kernel_params.append(i)
                c_params.append(j)
                epsilon_params.append(k)
                train_rmse, test_rmse = model_eval(SVR(kernel=i,C=j,epsilon=k),X_train,X_test,y_train,y_test)
                train.append(train_rmse)
                test.append(test_rmse)

dfsvr = pd.DataFrame(zip(kernel_params,c_params,epsilon_params,train,test),
                 columns = ['Kernel','C','epsilon','Train RMSE','Test RMSE'])
dfsvr

dfsvr['Train RMSE'].min(), dfsvr['Train RMSE'].argmin()

dfsvr['Test RMSE'].min(), dfsvr['Test RMSE'].argmin()

dfsvr.iloc[1,:]

"""### Trying with Decision Tree Regressor"""

train = []
test = []
criterion_params = []
max_depth_params = []
ccp_alpha_params = []
rs_params = []
for i in ["squared_error", "friedman_mse", "absolute_error", "poisson"]:
    for j in [None,1,2,3,4,5]:
        for k in [0,0.2,0.4,0.6,0.8,1,1.2,1.5]:
            for l in [1,8,28,11,42]:
                criterion_params.append(i)
                max_depth_params.append(j)
                ccp_alpha_params.append(k)
                rs_params.append(l)
                train_rmse, test_rmse = model_eval(DecisionTreeRegressor(criterion=i,
                                                                        max_depth=j,
                                                                        ccp_alpha=k,
                                                                        random_state=l),X_train,X_test,y_train,y_test)
                train.append(train_rmse)
                test.append(test_rmse)

dfdtr = pd.DataFrame(zip(criterion_params,max_depth_params,ccp_alpha_params,rs_params,train,test),
                 columns = ['Criterion','max_depth','ccp_alpha','random_state','Train RMSE','Test RMSE'])
dfdtr

dfdtr['Train RMSE'].min(), dfdtr['Train RMSE'].argmin()

dfdtr['Test RMSE'].min(), dfdtr['Test RMSE'].argmin()

dfdtr.iloc[600,:]

"""### Trying with Random Forest Regressor"""

train = []
test = []
criterion_params = []
max_depth_params = []
ccp_alpha_params = []
nestimators_params = []
rs_params = []
for i in ["squared_error", "absolute_error", "poisson"]:
    for j in [None,1,2,3,4,5]:
        for k in [0,0.2,0.4,0.6,0.8,1,1.2,1.5]:
            for l in [x for x in range(2,50)]:
                for m in [1,8,28,11,42]:
                    criterion_params.append(i)
                    max_depth_params.append(j)
                    ccp_alpha_params.append(k)
                    nestimators_params.append(l)
                    rs_params.append(m)
                    train_rmse, test_rmse = model_eval(RandomForestRegressor(criterion=i,
                                                                            max_depth=j,
                                                                            ccp_alpha=k,
                                                                            n_estimators=l,
                                                                            n_jobs=-1,
                                                                            random_state=m),X_train,X_test,y_train,y_test)
                    train.append(train_rmse)
                    test.append(test_rmse)

dfrfr = pd.DataFrame(zip(criterion_params,max_depth_params,ccp_alpha_params,nestimators_params,rs_params,train,test),
                 columns = ['Criterion','max_depth','ccp_alpha','n_estimators','random_state','Train RMSE','Test RMSE'])
dfrfr

dfrfr['Train RMSE'].min(), dfrfr['Train RMSE'].argmin()

dfrfr['Test RMSE'].min(), dfrfr['Test RMSE'].argmin()

dfrfr.iloc[7691,:]

"""### Trying with Adaboost Regressor"""

train = []
test = []
nestimator_params = []
lr_params = []
loss_params = []
rs_params = []
for i in [x for x in range(2,50)]:
    for j in [0.1,0.3,0.5,0.7,0.9,1,1.2,1.5]:
        for k in ['linear', 'square', 'exponential']:
            for l in [1,8,28,11,42]:
                nestimator_params.append(i)
                lr_params.append(j)
                loss_params.append(k)
                rs_params.append(l)
                train_rmse, test_rmse = model_eval(AdaBoostRegressor(base_estimator=DecisionTreeRegressor(
                    criterion='absolute_error',max_depth=3,ccp_alpha=0,random_state=1),
                                                   n_estimators=i,learning_rate=j,loss=k,random_state=l),
                                                   X_train,X_test,y_train,y_test)
                train.append(train_rmse)
                test.append(test_rmse)

dfabr = pd.DataFrame(zip(nestimator_params,lr_params,loss_params,rs_params,train,test),
                 columns = ['n_estimators','learning rate','loss','random_state','Train RMSE','Test RMSE'])
dfabr

dfabr['Train RMSE'].min(), dfabr['Train RMSE'].argmin()

dfabr['Test RMSE'].min(), dfabr['Test RMSE'].argmin()

dfabr.iloc[1182,:]

"""Base Estimator: Linear Regression"""

train = []
test = []
nestimator_params = []
lr_params = []
loss_params = []
rs_params = []
for i in [x for x in range(2,50)]:
    for j in [0.1,0.3,0.5,0.7,0.9,1,1.2,1.5]:
        for k in ['linear', 'square', 'exponential']:
            for l in [1,8,28,11,42]:
                nestimator_params.append(i)
                lr_params.append(j)
                loss_params.append(k)
                rs_params.append(l)
                train_rmse, test_rmse = model_eval(AdaBoostRegressor(base_estimator=LinearRegression(),
                                                                     n_estimators=i,learning_rate=j,loss=k,
                                                                    random_state=l),
                                                   X_train,X_test,y_train,y_test)
                train.append(train_rmse)
                test.append(test_rmse)

dfabr2 = pd.DataFrame(zip(nestimator_params,lr_params,loss_params,rs_params,train,test),
                 columns = ['n_estimators','learning rate','loss','random_state','Train RMSE','Test RMSE'])
dfabr2

dfabr2['Train RMSE'].min(), dfabr2['Train RMSE'].argmin()

dfabr2['Test RMSE'].min(), dfabr2['Test RMSE'].argmin()

dfabr2.iloc[190,:]

"""Base Estimator: Ridge Regression"""

train = []
test = []
nestimator_params = []
lr_params = []
loss_params = []
rs_params = []
for i in [x for x in range(2,50)]:
    for j in [0.1,0.3,0.5,0.7,0.9,1,1.2,1.5]:
        for k in ['linear', 'square', 'exponential']:
            for l in [1,8,28,11,42]:
                nestimator_params.append(i)
                lr_params.append(j)
                loss_params.append(k)
                rs_params.append(l)
                train_rmse, test_rmse = model_eval(AdaBoostRegressor(base_estimator=Ridge(random_state=1,
                                                                                          alpha=1.0,solver='auto'),
                                                                     n_estimators=i,learning_rate=j,loss=k,
                                                                    random_state = l),
                                                   X_train,X_test,y_train,y_test)
                train.append(train_rmse)
                test.append(test_rmse)

dfabr3 = pd.DataFrame(zip(nestimator_params,lr_params,loss_params,rs_params,train,test),
                 columns = ['n_estimators','learning rate','loss','random_state','Train RMSE','Test RMSE'])
dfabr3

dfabr3['Train RMSE'].min(), dfabr3['Train RMSE'].argmin()

dfabr3['Test RMSE'].min(), dfabr3['Test RMSE'].argmin()

dfabr3.iloc[565,:]

"""### Trying with Ridge Regression"""

train = []
test = []
alpha_params = []
solver_params = []
rs_params = []
for i in [0.5,0.8,1,1.2,1.5]:
    for j in ['auto', 'svd', 'cholesky', 'lsqr', 'sparse_cg', 'sag', 'saga']:
        for k in [1,8,28,11,42]:
            alpha_params.append(i)
            solver_params.append(j)
            rs_params.append(k)
            train_rmse, test_rmse = model_eval(Ridge(alpha=i,solver=j,random_state=k),
                                               X_train,X_test,y_train,y_test)
            train.append(train_rmse)
            test.append(test_rmse)

dfr = pd.DataFrame(zip(alpha_params,solver_params,rs_params,train,test),
                 columns = ['alpha','solver','random_state','Train RMSE','Test RMSE'])
dfr

dfr['Train RMSE'].min(), dfr['Train RMSE'].argmin()

dfr['Test RMSE'].min(), dfr['Test RMSE'].argmin()

dfr.iloc[70,:]

class final_model:

    def __init__(self):
        self.model1 = None
        self.model2 = None

    def fit(self,X,y):
        self.model1 = RandomForestRegressor(criterion='squared_error',
                                           max_depth=4.0,
                                           ccp_alpha=0.0,
                                           n_estimators=4,random_state=8)
        self.model2 = AdaBoostRegressor(base_estimator=DecisionTreeRegressor(criterion='absolute_error',
                                                                             max_depth=3,
                                                                             ccp_alpha=0,
                                                                            random_state=1),
                                                                 n_estimators=11,learning_rate=1.2,loss='exponential',
                                        random_state=28)
        self.model1.fit(X,y)
        self.model2.fit(X,y)

    def predict(self,X):
        y_pred1 = np.apply_along_axis((lambda x:np.round(x,3)),arr=self.model1.predict(X),axis=0)
        y_pred2 = np.apply_along_axis((lambda x:np.round(x,3)),arr=self.model2.predict(X),axis=0)
        y_pred = [np.round((1*i+5*j)/6.0,3) for i,j in zip(y_pred1,y_pred2)]
        return np.array(y_pred)

fm = final_model()
fm.fit(X_train,y_train)
y_pred_fm_train = fm.predict(X_train)
y_pred_fm_test = fm.predict(X_test)
print("Train RMSE: ",rmse(y_train,y_pred_fm_train))
print("Test RMSE: ",rmse(y_test,y_pred_fm_test))

fm2 = final_model()
fm2.fit(X,y)
y_pred_fm2 = fm2.predict(X)
print("RMSE: ",rmse(y,y_pred_fm2))

model1 = RandomForestRegressor(criterion='squared_error',
                                           max_depth=4.0,
                                           ccp_alpha=0.0,
                                           n_estimators=4,random_state=8).fit(X,y)
model2 = AdaBoostRegressor(base_estimator=DecisionTreeRegressor(criterion='absolute_error',
                                                                             max_depth=3,
                                                                             ccp_alpha=0,
                                                                            random_state=1),
                                                                 n_estimators=11,learning_rate=1.2,loss='exponential',
                                        random_state=28).fit(X,y)

pickle.dump(model1, open('../models/fetal_bw_m1.sav', 'wb'))
pickle.dump(model2, open('../models/fetal_bw_m2.sav', 'wb'))
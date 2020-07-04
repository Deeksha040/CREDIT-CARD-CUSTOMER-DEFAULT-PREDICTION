# -*- coding: utf-8 -*-
"""CREDIT CARD CUSTOMER DEFAULTER PREDICTIONS (NB2).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XMc8_2WU4InWPIOnnoRTqeUZNUHFu_J6
"""

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import glob
import os
import scipy.stats as ss
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from __future__ import print_function
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.metrics.cluster import homogeneity_score
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OrdinalEncoder
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
import matplotlib.cm as cm
# %matplotlib inline

# Read data 
os.chdir('/content/drive/My Drive/Colab Notebooks')
datapath = os.getcwd()+'/Data/'
file = datapath + 'CreditCardData.csv'
df = pd.read_csv('CreditCardData.csv')

# Rename column 'PAY_0' as 'PAY_1'
df.rename(columns = {'PAY_0' : 'PAY_1'}, inplace = True)

# Print dataframe and column datatypes
pd.options.display.max_columns = None
print(df.head(5))
#print(df.dtypes)

# Create lists of continuous and categorical column names
continuous_cols = ['LIMIT_BAL', 'AGE', 'BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3',
                   'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6', 'PAY_AMT1',
                   'PAY_AMT2', 'PAY_AMT3', 'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6']
categorical_cols = ['SEX', 'EDUCATION', 'MARRIAGE', 'PAY_1', 'PAY_2', 'PAY_3',
                    'PAY_4', 'PAY_5', 'PAY_6', 'default.payment.next.month']

# Assign 'object' datatype to categorical columns                    
df[categorical_cols] = df[categorical_cols].astype('category')

# Print unique values for categorical columns
unique_values = {col:list(df[col].unique()) for col in categorical_cols}
for key, value in unique_values.items():
  print(key,value)

# Adjust categorical column values for misrepresented entries
df.loc[~df['EDUCATION'].isin([1, 2, 3, 4]), 'EDUCATION'] = 5
df.loc[~df['MARRIAGE'].isin([1, 2]), 'MARRIAGE'] = 3
df.loc[~df['PAY_1'].isin([-1, 1, 2, 3, 4, 5, 6, 7, 8, 9]), 'PAY_1'] = 0
df.loc[~df['PAY_2'].isin([-1, 1, 2, 3, 4, 5, 6, 7, 8, 9]), 'PAY_2'] = 0
df.loc[~df['PAY_3'].isin([-1, 1, 2, 3, 4, 5, 6, 7, 8, 9]), 'PAY_3'] = 0
df.loc[~df['PAY_4'].isin([-1, 1, 2, 3, 4, 5, 6, 7, 8, 9]), 'PAY_4'] = 0
df.loc[~df['PAY_5'].isin([-1, 1, 2, 3, 4, 5, 6, 7, 8, 9]), 'PAY_5'] = 0
df.loc[~df['PAY_6'].isin([-1, 1, 2, 3, 4, 5, 6, 7, 8, 9]), 'PAY_6'] = 0
categorical_cols = categorical_cols[:-1]

# Calculate correlation between continuous & continuous variables
# using Spearman's correlation coefficient 
corr = pd.DataFrame(columns = continuous_cols + categorical_cols, 
                    index =  continuous_cols + categorical_cols)
corr[continuous_cols] = df[continuous_cols].corr(method ='spearman')
print(corr)

# Function to calculate correlation between continuous & categorical variables
# using Correlation Ratio

def correlation_ratio(categories, measurements):
    fcat, _ = pd.factorize(categories)
    cat_num = np.max(fcat)+1
    y_avg_array = np.zeros(cat_num)
    n_array = np.zeros(cat_num)
    for i in range(0,cat_num):
        cat_measures = measurements[np.argwhere(fcat == i).flatten()]
        n_array[i] = len(cat_measures)
        y_avg_array[i] = np.average(cat_measures)
    y_total_avg = np.sum(np.multiply(y_avg_array,n_array))/np.sum(n_array)
    numerator = np.sum(np.multiply(n_array,np.power(np.subtract(y_avg_array,y_total_avg),2)))
    denominator = np.sum(np.power(np.subtract(measurements,y_total_avg),2))
    if numerator == 0:
        eta = 0.0
    else:
        eta = np.sqrt(numerator/denominator)
    return eta

# Calculate correlation between continuous &  categorical variables using
# Correlation Ratio

for con_col_name in continuous_cols:
  for cat_col_name in categorical_cols:
    val = correlation_ratio(df[con_col_name].values,
                            df[cat_col_name].astype('float64').values)
    corr.loc[con_col_name, cat_col_name] = val
    corr.loc[cat_col_name, con_col_name] = val  
print(corr)

# Function to calculate correlation between categorical & categorical variables
# using Cramer's V

def cramers_phi(x, y):
    confusion_matrix = pd.crosstab(x,y)
    chi2 = ss.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2/n
    r,k = confusion_matrix.shape
    phi2corr = max(0, phi2-((k-1)*(r-1))/(n-1))
    rcorr = r-((r-1)**2)/(n-1)
    kcorr = k-((k-1)**2)/(n-1)
    return np.sqrt(phi2corr/min((kcorr-1),(rcorr-1)))

# Calculate correlation between categorical & categorical variables
# using Cramer's V
for col in [categorical_cols, categorical_cols]:
  for i in range(0,len(col)):
    for j in range(i,len(col)):
      if i == j:                 
        corr.loc[col[i],col[j]] = 1.0            
      else:                 
        val = cramers_phi(df[col[i]].astype('float64').values,
                          df[col[j]].astype('float64').values) 
        corr.loc[col[i], col[j]] = val
        corr.loc[col[j], col[i]] = val
print(corr)

# Plot the correlation matrix
corr.fillna(value=np.nan, inplace=True)
sns.heatmap(corr)

## Hierarchichal clustering of the correlation matrix
# Generate the linkage matrix
Z = linkage(corr, 'ward')

# Calculate full dendrogram 
plt.figure(figsize=(12, 12))
plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('Variables')
plt.ylabel('distance')
dendrogram(Z, labels=list(corr.columns))
plt.axhline(y=2, color='r', linestyle='--')
plt.show()

# Install Java
! apt-get install default-jre
! java -version
# Install h2o library for GLRM
! pip install h2o

import h2o # For GLRM
from h2o.estimators.glrm import H2OGeneralizedLowRankEstimator
h2o.init()
h2o.remove_all() # Clean slate - just in case the cluster was already running

# Write updated dataframe into a single CSV file
df.to_csv('Data/CreditCardDataUpdated.csv', columns = df.columns)

# Import data as h2o dataframe
dfh2o = h2o.import_file(path = os.path.realpath("Data/CreditCardDataUpdated.csv"))
dfh2o.types

# Reset categorical column data types in h2o dataframe
dfh2o[categorical_cols] = dfh2o[categorical_cols].asfactor()
dfh2o["default.payment.next.month"]=dfh2o["default.payment.next.month"].asfactor()
dfh2o.types

#Created 5 different dataframes which has the features corresponding to the particular cluster.
#Then each time while running GLRM model given each dataframe as the  training frame.
#This is not needed we can give directly the features corresponding to the particular cluster in the trainning frame..
dfh2o_c1=dfh2o[["BILL_AMT1","BILL_AMT2","BILL_AMT3","BILL_AMT4","BILL_AMT5","BILL_AMT6"]]
dfh2o_c2=dfh2o[["AGE","LIMIT_BAL"]]
dfh2o_c3=dfh2o[["PAY_AMT1","PAY_AMT2","PAY_AMT3","PAY_AMT4","PAY_AMT5","PAY_AMT6"]]
dfh2o_c4=dfh2o[["PAY_1","PAY_2","PAY_3","PAY_4","PAY_5","PAY_6"]]
dfh2o_c5=dfh2o[["SEX","EDUCATION","MARRIAGE"]]
#dfh2o_list = [dfh2o_c1,dfh2o_c2,dfh2o_c3,dfh2o_c4,dfh2o_c5]
#print(dfh2o_list)

# Basic GLRM using absolute loss for continuous and categorical loss for
# categorical columns with no regularization and with stadardized columns

#model genearted for the first cluster :bill_amt1 to bill_amt6
model_c1 = H2OGeneralizedLowRankEstimator(k = 1,
                                       loss = "Absolute", multi_loss = "Categorical",
                                       transform = "Standardize",
                                       regularization_x = "None",
                                       regularization_y = "None",
                                       max_iterations = 1000,
                                       min_step_size = 1e-6)
model_c1.train(training_frame=dfh2o_c1)
model_c1.show()

# Print importance of each component of GLRM model
model_c1._model_json["output"]["importance"]

# Split the feature matrix into product of two matrices X and Y
# The matrix X has the same number of rows as the original feature matrix
# but a reduced number of columns representing the original features
# GLRM matrix factors X and Y

#X_matrix and Y_matrix for cluster1...
X_matrix_c1 = h2o.get_frame(model_c1._model_json["output"]["representation_name"])
print(X_matrix_c1)
Y_matrix_c1 = model_c1._model_json["output"]["archetypes"]
print(Y_matrix_c1)

#model genearted for  cluster2 :age and limit balance
model_c2 = H2OGeneralizedLowRankEstimator(k = 1,
                                       loss = "Absolute", multi_loss = "Categorical",
                                       transform = "Standardize",
                                       regularization_x = "None",
                                       regularization_y = "None",
                                       max_iterations = 1000,
                                       min_step_size = 1e-6)
model_c2.train(training_frame=dfh2o_c2)
model_c2.show()

# Print importance of each component of GLRM model
model_c2._model_json["output"]["importance"]

#X_matrix and Y_matrix for cluster2...
X_matrix_c2 = h2o.get_frame(model_c2._model_json["output"]["representation_name"])
print(X_matrix_c2)
Y_matrix_c2 = model_c2._model_json["output"]["archetypes"]
print(Y_matrix_c2)

#model genearted for  cluster3 :pay_amt1 to pay_amt6
model_c3 = H2OGeneralizedLowRankEstimator(k = 1,
                                       loss = "Absolute", multi_loss = "Categorical",
                                       transform = "Standardize",
                                       regularization_x = "None",
                                       regularization_y = "None",
                                       max_iterations = 1000,
                                       min_step_size = 1e-6)
model_c3.train(training_frame=dfh2o_c3)
model_c3.show()

# Print importance of each component of GLRM model
model_c3._model_json["output"]["importance"]

#X_matrix and Y_matrix for cluster3...
X_matrix_c3 = h2o.get_frame(model_c3._model_json["output"]["representation_name"])
print(X_matrix_c3)
Y_matrix_c3 = model_c3._model_json["output"]["archetypes"]
print(Y_matrix_c3)

#Model generated for cluster4: pay1 to pay6
model_c4 = H2OGeneralizedLowRankEstimator(k = 1,
                                       loss = "Absolute", multi_loss = "Categorical",
                                       transform = "Standardize",
                                       regularization_x = "None",
                                       regularization_y = "None",
                                       max_iterations = 1000,
                                       min_step_size = 1e-6)
model_c4.train(training_frame=dfh2o_c4)
model_c4.show()

# Print importance of each component of GLRM model
model_c4._model_json["output"]["importance"]

#X_matrix and Y_matrix for cluster4...
X_matrix_c4 = h2o.get_frame(model_c4._model_json["output"]["representation_name"])
print(X_matrix_c4)
Y_matrix_c4 = model_c4._model_json["output"]["archetypes"]
print(Y_matrix_c4)

#Model generated for cluster5: Gender,Education and marriage
model_c5 = H2OGeneralizedLowRankEstimator(k = 1,
                                       loss = "Absolute", multi_loss = "Categorical",
                                       transform = "Standardize",
                                       regularization_x = "None",
                                       regularization_y = "None",
                                       max_iterations = 1000,
                                       min_step_size = 1e-6)
model_c5.train(training_frame=dfh2o_c5)
model_c5.show()

# Print importance of each component of GLRM model
model_c5._model_json["output"]["importance"]

#X_matrix and Y_matrix for cluster5...
X_matrix_c5 = h2o.get_frame(model_c5._model_json["output"]["representation_name"])
print(X_matrix_c5)
Y_matrix_c5 = model_c5._model_json["output"]["archetypes"]
print(Y_matrix_c5)

# Data for training and testing
#first converted the  X_matrix from each cluster to array
#Then concatenated all the 5 arrays in columnwise

a1 = np.array(h2o.as_list(X_matrix_c1))
a2 = np.array(h2o.as_list(X_matrix_c2))
a3 = np.array(h2o.as_list(X_matrix_c3))
a4 = np.array(h2o.as_list(X_matrix_c4))
a5 = np.array(h2o.as_list(X_matrix_c5))

X=np.concatenate((a1,a2,a3,a4,a5),axis=1)
print(X.shape)

y = df['default.payment.next.month'].to_numpy()
print(y.shape)

# Stratified train & test split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify = y, test_size = 0.25)

print(X_train.shape)

# import model and matrics
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score, RepeatedStratifiedKFold, StratifiedKFold
from sklearn.metrics import accuracy_score, confusion_matrix,roc_curve, roc_auc_score, precision_score, recall_score, precision_recall_curve
from sklearn.metrics import f1_score

from sklearn.linear_model import LogisticRegression 
classifier_LR = LogisticRegression(random_state = 0) 
classifier_LR.fit(X_train,y_train)

y_pred_LR= classifier_LR.predict(X_test)

from sklearn.metrics import confusion_matrix 
cm_LR= confusion_matrix(y_test, y_pred_LR) 
print ("Confusion Matrix : \n", cm_LR)

from sklearn.metrics import accuracy_score 
print ("Accuracy : ", accuracy_score(y_test, y_pred_LR))

group_names = ['True Neg','False Pos','False Neg','True Pos']
group_counts = ["{0:0.0f}".format(value) for value in
                cm_LR.flatten()]
group_percentages = ["{0:.2%}".format(value) for value in
                     cm_LR.flatten()/np.sum(cm_LR)]
labels = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in
          zip(group_names,group_counts,group_percentages)]
labels = np.asarray(labels).reshape(2,2)
sns.heatmap(cm_LR, annot=labels, fmt='', cmap='Blues')
plt.title("COnfusion matrix for Logestic Regression")

from sklearn.metrics import precision_score
precision = precision_score(y_test, y_pred_LR)
print('Precision: %.3f' % precision)

from sklearn.metrics import recall_score
recall = recall_score(y_test, y_pred_LR)
print('Recall: %.3f' % recall)

from sklearn.metrics import f1_score
score = f1_score(y_test, y_pred_LR)
print('F-Measure: %.3f' % score)

##SVM

from sklearn.svm import SVC
classifier_SVM=SVC(kernel='rbf',random_state=0,probability=True)
classifier_SVM.fit(X_train,y_train)

y_pred_SVM=classifier_SVM.predict(X_test)

from sklearn.metrics import confusion_matrix 
cm_SVM= confusion_matrix(y_test, y_pred_SVM) 
print ("Confusion Matrix : \n", cm_SVM)

from sklearn.metrics import accuracy_score 
print ("Accuracy : ", accuracy_score(y_test, y_pred_SVM))

from sklearn.metrics import precision_score
precision = precision_score(y_test, y_pred_SVM, average='binary')
print('Precision: %.3f' % precision)

from sklearn.metrics import recall_score
recall = recall_score(y_test, y_pred_SVM, average='binary')
print('Recall: %.3f' % recall)

from sklearn.metrics import f1_score
score = f1_score(y_test, y_pred_SVM, average='binary')
print('F-Measure: %.3f' % score)

##ROC curve
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import auc

# Get predicted probabilities
y_pred_prob_LR = classifier_LR.predict_proba(X_test)[:,1]
y_pred_prob_SVM = classifier_SVM.predict_proba(X_test)[:,1]

fpr_LR, tpr_LR, thresholds_LR = roc_curve(y_test,y_pred_prob_LR)
fpr_SVM, tpr_SVM, thresholds_SVM = roc_curve(y_test,y_pred_prob_SVM)
roc_auc_LR = auc(fpr_LR, tpr_LR)
roc_auc_SVM= auc(fpr_SVM, tpr_SVM)
print("Area under the ROC curve for Logistic regression is  : %f" % roc_auc_LR)
print("Area under the ROC curve for SVM is  : %f" % roc_auc_SVM)

import pylab as pl
pl.clf()
pl.plot(fpr_LR, tpr_LR, label='ROC curve (area = %0.2f)' % roc_auc_LR)
#pl.plot([0, 1], [0, 1], 'k--')
pl.xlim([0.0, 1.0])
pl.ylim([0.0, 1.0])
pl.xlabel('False Positive Rate')
pl.ylabel('True Positive Rate')
pl.title('Receiverrating characteristic example')
pl.legend(loc="lower right")
pl.show()

#precision recall curve
precision, recall, _ = precision_recall_curve(y_test,y_pred_prob_LR)
# plot the model precision-recall curve
plt.plot(recall, precision, marker='.', label='Logistic')
# axis labels
plt.xlabel('Recall')
plt.ylabel('Precision')
# show the legend
plt.legend()
# show the plot
plt.show()

auc_score = auc(recall, precision)

from sklearn.metrics import precision_recall_curve
precision, recall, thresholds = precision_recall_curve(y_test, y_pred_prob_LR)
plt.plot(recall, precision, marker='.', label='Logistic')
# axis labels
plt.xlabel('Recall')
plt.ylabel('Precision')
# show the legend
plt.legend()
# show the plot
plt.show()

from sklearn.metrics import average_precision_score, auc, roc_curve, precision_recall_curve
average_precision = average_precision_score(y_test, y_pred_prob_LR)

#print('Average precision-recall score RF: {}'.format(average_precision))

from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt

precision, recall, _ = precision_recall_curve(y_test, y_pred_prob_LR)
precision_1, recall_1, _ = precision_recall_curve(y_test, y_pred_prob_SVM)
plt.step(recall, precision, color='b', alpha=0.2,
         where='post')
plt.fill_between(recall, precision, step='post', alpha=0.2,
                 color='b')

plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title("Precision-Recall curve  {}".format(average_precision))

###APPLYING OVERSAMPLING

print("Before OverSampling, counts of label '1': {}".format(sum(y_train == 1))) 
print("Before OverSampling, counts of label '0': {} \n".format(sum(y_train == 0))) 
  
# import SMOTE module from imblearn library 
# pip install imblearn (if you don't have imblearn in your system) 
from imblearn.over_sampling import SMOTE 
sm = SMOTE(random_state = 2) 
X_train_res, y_train_res = sm.fit_sample(X_train, y_train.ravel()) 
  
print('After OverSampling, the shape of train_X: {}'.format(X_train_res.shape)) 
print('After OverSampling, the shape of train_y: {} \n'.format(y_train_res.shape)) 
  
print("After OverSampling, counts of label '1': {}".format(sum(y_train_res == 1))) 
print("After OverSampling, counts of label '0': {}".format(sum(y_train_res == 0)))

from sklearn.linear_model import LogisticRegression 
classifier_LR_OS = LogisticRegression(random_state = 0) 
classifier_LR_OS.fit(X_train_res,y_train_res)

y_pred_LR_OS= classifier_LR_OS.predict(X_test)

from sklearn.metrics import confusion_matrix 
cm_LR_OS= confusion_matrix(y_test, y_pred_LR_OS) 
print ("Confusion Matrix : \n", cm_LR_OS)

group_names = ['True Neg','False Pos','False Neg','True Pos']
group_counts = ["{0:0.0f}".format(value) for value in
                cm_LR_OS.flatten()]
group_percentages = ["{0:.2%}".format(value) for value in
                     cm_LR_OS.flatten()/np.sum(cm_LR_OS)]
labels = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in
          zip(group_names,group_counts,group_percentages)]
labels = np.asarray(labels).reshape(2,2)
sns.heatmap(cm_LR_OS, annot=labels, fmt='', cmap='Blues')
plt.title("Confusion matrix for Logistic Regression")

from sklearn.metrics import accuracy_score 
print ("Accuracy : ", accuracy_score(y_test, y_pred_LR_OS))

from sklearn.metrics import precision_score
precision_LR = precision_score(y_test, y_pred_LR_OS, average='binary')
print('Precision: %.3f' % precision_LR)

from sklearn.metrics import recall_score
recall_LR= recall_score(y_test, y_pred_LR_OS, average='binary')
print('Recall: %.3f' % recall_LR)

from sklearn.metrics import f1_score
score_LR = f1_score(y_test, y_pred_LR_OS, average='binary')
print('F-Measure: %.3f' % score_LR)

specificity_LR = cm_LR_OS[0,0]/(cm_LR_OS[0,0]+cm_LR_OS[0,1])
print('Specificity : ', specificity_LR)

from sklearn.svm import SVC
classifier_SVM_OS=SVC(kernel='rbf',random_state=0,probability=True)
classifier_SVM_OS.fit(X_train_res,y_train_res)

y_pred_SVM_OS= classifier_SVM_OS.predict(X_test)

from sklearn.metrics import confusion_matrix 
cm_SVM_OS= confusion_matrix(y_test, y_pred_SVM_OS) 
print ("Confusion Matrix : \n", cm_SVM_OS)

group_names = ['True Neg','False Pos','False Neg','True Pos']
group_counts = ["{0:0.0f}".format(value) for value in
                cm_SVM_OS.flatten()]
group_percentages = ["{0:.2%}".format(value) for value in
                     cm_SVM_OS.flatten()/np.sum(cm_SVM_OS)]
labels = [f"{v1}\n{v2}\n{v3}" for v1, v2, v3 in
          zip(group_names,group_counts,group_percentages)]
labels = np.asarray(labels).reshape(2,2)
sns.heatmap(cm_SVM_OS, annot=labels, fmt='', cmap='Blues')
plt.title("Confusion matrix for SVM")

from sklearn.metrics import accuracy_score 
print ("Accuracy : ", accuracy_score(y_test, y_pred_SVM_OS))

from sklearn.metrics import precision_score
precision_SVM= precision_score(y_test, y_pred_SVM_OS, average='binary')
print('Precision: %.3f' % precision_SVM)

from sklearn.metrics import recall_score
recall_SVM = recall_score(y_test, y_pred_SVM_OS, average='binary')
print('Recall: %.3f' % recall_SVM)

from sklearn.metrics import f1_score
score_SVM= f1_score(y_test, y_pred_SVM_OS, average='binary')
print('F-Measure: %.3f' % score_SVM)

specificity_SVM = cm_SVM_OS[0,0]/(cm_SVM_OS[0,0]+cm_SVM_OS[0,1])
print('Specificity : ', specificity_SVM)

##ROC

# Get predicted probabilities
y_pred_prob_LR_OS = classifier_LR_OS.predict_proba(X_test)[:,1]
y_pred_prob_SVM_OS= classifier_SVM_OS.predict_proba(X_test)[:,1]

fpr_LR_OS, tpr_LR_OS, thresholds_LR_OS= roc_curve(y_test,y_pred_prob_LR_OS)
fpr_SVM_OS, tpr_SVM_OS, thresholds_SVM_OS = roc_curve(y_test,y_pred_prob_SVM_OS)
roc_auc_LR_OS = auc(fpr_LR_OS, tpr_LR_OS)
roc_auc_SVM_OS= auc(fpr_SVM_OS, tpr_SVM_OS)
print("Area under the ROC curve for Logistic regression is  : %f" % roc_auc_LR_OS)
print("Area under the ROC curve for SVM is  : %f" % roc_auc_SVM_OS)

import pylab as pl
pl.clf()
pl.plot(fpr_LR_OS, tpr_LR_OS, label='ROC curve for LR (area = %0.2f)' % roc_auc_LR_OS)
pl.plot(fpr_SVM_OS, tpr_SVM_OS, label='ROC curve for SVM (area = %0.2f)' % roc_auc_SVM_OS)
pl.plot([0, 1], [0, 1], 'k--',label='tpr=fpr')
pl.xlim([0.0, 1.0])
pl.ylim([0.0, 1.0])
pl.xlabel('False Positive Rate')
pl.ylabel('True Positive Rate')
pl.title('Receiver Operating Characteristic curve')
pl.legend()
pl.show()

from sklearn.metrics import average_precision_score, auc, roc_curve, precision_recall_curve
average_precision = average_precision_score(y_test, y_pred_prob_LR_OS)

#print('Average precision-recall score RF: {}'.format(average_precision))

from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt

precision_LR, recall_LR, _ = precision_recall_curve(y_test, y_pred_prob_LR_OS)

plt.step(recall_LR, precision_LR, color='b', alpha=0.2,
         where='post')
plt.fill_between(recall_LR, precision_LR, step='post', alpha=0.2,
                 color='b')

plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title("Precision-Recall curve  {}".format(average_precision))

###UNDERSAMPLING

print("Before Undersampling, counts of label '1': {}".format(sum(y_train == 1))) 
print("Before Undersampling, counts of label '0': {} \n".format(sum(y_train == 0))) 
  
# apply near miss 
from imblearn.under_sampling import NearMiss 
nr = NearMiss() 
  
X_train_miss, y_train_miss = nr.fit_sample(X_train, y_train.ravel()) 
  
print('After Undersampling, the shape of train_X: {}'.format(X_train_miss.shape)) 
print('After Undersampling, the shape of train_y: {} \n'.format(y_train_miss.shape)) 
  
print("After Undersampling, counts of label '1': {}".format(sum(y_train_miss == 1))) 
print("After Undersampling, counts of label '0': {}".format(sum(y_train_miss == 0)))

from sklearn.linear_model import LogisticRegression 
classifier_LR_US = LogisticRegression(random_state = 0) 
classifier_LR_US.fit(X_train_miss,y_train_miss)

y_pred_LR_US= classifier_LR_US.predict(X_test)

from sklearn.metrics import confusion_matrix 
cm_LR_US= confusion_matrix(y_test, y_pred_LR_US) 
print ("Confusion Matrix : \n", cm_LR_US)

from sklearn.metrics import accuracy_score 
print ("Accuracy : ", accuracy_score(y_test, y_pred_LR_US))

from sklearn.metrics import precision_score
precision = precision_score(y_test, y_pred_LR_US, average='binary')
print('Precision: %.3f' % precision)

from sklearn.metrics import recall_score
recall = recall_score(y_test, y_pred_LR_US, average='binary')
print('Recall: %.3f' % recall)

from sklearn.metrics import f1_score
score = f1_score(y_test, y_pred_LR_US, average='binary')
print('F-Measure: %.3f' % score)

from sklearn.svm import SVC
classifier_SVM_US=SVC(kernel='rbf',random_state=0)
classifier_SVM_US.fit(X_train_miss,y_train_miss)

y_pred_SVM_US= classifier_SVM_US.predict(X_test)

from sklearn.metrics import confusion_matrix 
cm_SVM_US= confusion_matrix(y_test, y_pred_SVM_US) 
print ("Confusion Matrix : \n", cm_SVM_US)

from sklearn.metrics import accuracy_score 
print ("Accuracy : ", accuracy_score(y_test, y_pred_SVM_US))

from sklearn.metrics import precision_score
precision = precision_score(y_test, y_pred_SVM_US, average='binary')
print('Precision: %.3f' % precision)

from sklearn.metrics import recall_score
recall = recall_score(y_test, y_pred_SVM_US, average='binary')
print('Recall: %.3f' % recall)

from sklearn.metrics import f1_score
score = f1_score(y_test, y_pred_SVM_US, average='binary')
print('F-Measure: %.3f' % score)


specificity1 = cm_SVM_US[0,0]/(cm_SVM_US[0,0]+cm_SVM_US[0,1])
print('Specificity : ', specificity1)

# Get predicted probabilities
y_pred_prob_LR_US= classifier_LR_US.predict_proba(X_test)[:,1]
#y_pred_prob_SVM = classifier_SVM.predict_proba(X_test)[:,1]

fpr_LR_US, tpr_LR_US, thresholds_LR_US = roc_curve(y_test,y_pred_prob_LR_US)
fpr_SVM, tpr_SVM, thresholds_SVM = roc_curve(y_test,y_pred_prob_SVM)
roc_auc_LR_US= auc(fpr_LR_US, tpr_LR_US)
roc_auc_SVM= auc(fpr_SVM, tpr_SVM)
print("Area under the ROC curve for Logistic regression is  : %f" % roc_auc_LR_US)
print("Area under the ROC curve for SVM is  : %f" % roc_auc_SVM)

plt.figure(figsize=(3,3))
print(pd.Series(df['default.payment.next.month']).value_counts())
pd.Series(df['default.payment.next.month']).value_counts().plot(kind ='pie', autopct='%1.2f%%')


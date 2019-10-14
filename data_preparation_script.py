# Imports

import numpy as np
import pandas as pd
from IPython.display import display

import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from tqdm import tqdm_notebook as tqdm
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression


from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.svm import SVC 
from sklearn.model_selection import cross_val_score
from sklearn.metrics import make_scorer, f1_score
# Load Data

def load_data() -> pd.Series:
    csv_train = pd.read_csv('superhero-or-supervillain/train.csv').assign(train = 1) 
    csv_test = pd.read_csv('superhero-or-supervillain/test.csv').assign(train = 0) 
    csv = pd.concat([csv_train,csv_test], sort=True)
    return csv

# Analyze Data

def nans_ctr(csv) -> pd.Series:
    return csv.isna().sum()

def unique_ctr(csv) -> pd.Series():
    unique = pd.Series()
    for col in list(csv):
        if(csv.columns.contains(col)):
            unique.at[col] = len(csv[col].unique())
    return unique

def val_types(csv) -> pd.Series():
    val_type = pd.Series()
    for col in list(csv):
        if not csv.columns.contains(col):
            continue
        if csv[col].dtype == np.float64:
            val_type.at[col] = np.float64
        elif csv[col].dtype == np.int64:
            val_type.at[col] = np.int64
        elif csv[col].dtype == np.int32:
            val_type.at[col] = np.int32
        elif csv[col].dtype == np.uint8:
            val_type.at[col] = np.uint8
        elif csv[col].dtype == object:
            val_type.at[col] = object
        elif csv[col].dtype == bool:
            val_type.at[col] = bool
        else:
            print(f"No common value type found in val_types() - {csv[col].dtype}")
    return val_type

def min_max_val(csv) -> pd.Series():
    min_val = pd.Series()
    max_val = pd.Series()
    val_type = val_types(csv)
    for col in list(csv):
        if val_type[col] != object:
            min_val.at[col] = csv[col].min()
            max_val.at[col] = csv[col].max()
        else:    
            min_val.at[col] = None
            max_val.at[col] = None
    return min_val, max_val        
            
def get_stats(csv):
    nans = nans_ctr(csv)
    unique = unique_ctr(csv)
    val_type = val_types(csv)
    min_val, max_val = min_max_val(csv)
    result = pd.DataFrame({ 'nans': nans, 'unique': unique, 'val_type': val_type, 'min_val': min_val, 'max_val': max_val}) 
    return result
    
def bool_to_integer(csv) -> pd.DataFrame():
    for col in csv.columns:
        if csv[col].dtype == bool:
            csv[col] = csv[col].astype(int)
    return csv
    
def standarize_numerical_values(csv):
    for col in csv.columns:
        if col == 'train':
            continue
        if csv[col].dtype == np.float64:
            data = csv[col]
            std = data.std()
            data = data[(data < data.quantile(0.99)) & (data > data.quantile(0.01))]
            mean = data.mean()
            csv[col] = (csv[col] - mean)/std
#             _ = plt.hist(csv[col], bins='auto', alpha = 0.5)
#             plt.yscale('log')
#             plt.title(f"Distr in {col} column")
#             plt.show()
    return csv

def check_rows(csv):
    for row in range(len(csv)):
        print(row, csv.iloc[row].isna().sum())
    return csv

def distribution_in_columns(csv):
    for col in list(csv):
        print(csv[col].value_counts())
    return csv
        
def plot_dist_y(csv):
    plt.pie([len(csv[csv['Alignment'] == 'good']), len(csv[csv['Alignment'] == 'bad']), 
             len(csv[csv['Alignment'] == 'neutral'])], labels = ['good', 'bad', 'neutral'])
    plt.show()
    return csv
    
def factorize(csv) -> pd.DataFrame():
    for col in csv.select_dtypes(include=['object']).columns:
        if col == "Alignment":
            continue
        dummy = pd.get_dummies(csv[col])
        dummy.columns = [col+ " "+x for x in dummy.columns]
        dummy = dummy.drop([dummy.columns[-1]], axis=1)
        csv = csv.drop(col, axis=1)
        csv = pd.concat([csv, dummy], axis=1)
    return csv
    
def rfc_fun(x_tr, y_tr):
    rfc = RandomForestClassifier(max_features = 'auto', random_state=0)
    param_grid = { 
        'n_estimators': [15,50, 100],
        'max_depth' : [1,2,3,5,10,20],
        'criterion' :['gini', 'entropy'],
        'class_weight':[None,'balanced']
    }
    CV_rfc = GridSearchCV(estimator=rfc, param_grid=param_grid, cv= 5).fit(x, y)
    #confusion matrix
    y_pred = CV_rfc.predict(x_tr)
    cm = confusion_matrix(y_tr,  y_pred)
    return CV_rfc
  
def LogisticRegr_fun(x_tr, y_tr):
    grid={"C":np.logspace(-3,3,7), "penalty":["l1","l2"]}# l1 lasso l2 ridge
    logreg=LogisticRegression()
    logreg_cv=GridSearchCV(logreg,grid,cv=10)
    logreg_cv.fit(x_tr,y_tr)
     #confusion matrix
    logreg2=LogisticRegression(C=18,penalty="l2")
    logreg2.fit(x_train,y_train)
    
    y_pred = logreg2.predict(x_tr)
    cm = confusion_matrix(y_tr,  y_pred)
   
    return logreg2

def SVC_fun(x, y):
    svm = SVC()
    parameters = {'kernel':('linear', 'rbf'), 'C':(1,0.25,0.5,0.75),'gamma': (1,2,3,5,10,'auto'),'decision_function_shape':('ovo','ovr'),'shrinking':(True,False)}
    my_scorer = make_scorer(f1_score, greater_is_better=True, average='micro')
    svc = GridSearchCV(svm, parameters,scoring=my_scorer)
    svc.fit(x,y, sample_weight=None)
    #confusion matrix
    y_pred = svc.predict(x_tr)
    cm = confusion_matrix(y_tr,  y_pred)
   
    return svc 
    
    def test_loop_GSC(x,y):
        for rndm_st in [0,35,42,60]: #recall the classifier functions inside here
            x_tr, x_valid, y_tr, y_valid = train_test_split(x_train, y_train, test_size=0.3,random_state=rndm_st)
            vec1=rfc_fun(x_tr, y_tr,rndm_st)
            vec2=LogisticRegr_fun(x_tr, y_tr, rndm_st)
            vec3=SVC_fun(x_tr, y_tr,rndm_st)
    return vec1, vec2, vec3   

if __name__ == "__main__":
    csv = load_data()
    # Just ID not need it
    csv = csv.drop(columns=['Id'])
    csv = standarize_numerical_values(csv)
    csv = bool_to_integer(csv)
    
    csv = factorize(csv)
    stats = get_stats(csv)
    # with pd.option_context('display.max_rows', 500, 'display.max_columns', 500, 'display.width', 1000):
        # print(stats)
        
    Y = csv["Alignment"]
    csv = csv.drop("Alignment",axis=1)
    X = csv

    is_train = csv["train"] == 1
    y_train, uniques = pd.factorize(Y[is_train])

    x_train = X[is_train].values
    x_train = pd.DataFrame(x_train).fillna(0)
    
    x_test = X[is_train == False].values

    x_tr, x_valid, y_tr, y_valid = train_test_split(x_train, y_train, test_size=0.25,random_state=0)

    
    # clf = RandomForestClassifier(n_estimators=100, max_depth=44,random_state=0)
    # clf.fit(x_tr, y_tr)
    # print("RandomForestClassifier:")
    # print("Train",clf.score(x_tr, y_tr))
    # print("Valid",clf.score(x_valid, y_valid))
    
    clf = DecisionTreeClassifier(random_state=0)
    clf.fit(x_tr, y_tr)
    print("DecisionTreeClassifier:")
    print("Train",clf.score(x_tr, y_tr))
    print("Valid",clf.score(x_valid, y_valid))
    
    clf = KNeighborsClassifier(n_neighbors=3)
    clf.fit(x_tr, y_tr)
    print("KNeighborsClassifier:")
    print("Train",clf.score(x_tr, y_tr))
    print("Valid",clf.score(x_valid, y_valid))
    
    from sklearn.linear_model import LogisticRegression
    clf = LogisticRegression(random_state=0, solver='sag',multi_class='multinomial')
    clf.fit(x_train, y_train)
    print("Final Training LogisticRegression")
    print("Train + Valid",clf.score(x_train, y_train))
    x_test = pd.DataFrame(x_test).fillna(0)
    y_predict = clf.predict(x_test)
    
    y_predict = pd.DataFrame(y_predict)
    y_predict[y_predict == 0] = "bad"
    y_predict[y_predict == 1] = "good"
    y_predict[y_predict == 2] = "neutral"
    y_predict.columns = ["Prediction"]
    y_predict.to_csv('result.csv',index_label ="Id")
    

    rfc = rfc_fun(x_tr, y_tr)
    pred = rfc.predict(x_valid)
    print("Accuracy for Random Forest on CV data: ", accuracy_score(y_valid,pred))
    
    
    
    v1,v2,v3=test_loop_GSC(x_tr,y_tr)   
    for v in [v1,v2,v3]:
        vec_acc=[]
        pred = rfc.predict(x_valid)
        print("Accuracy comparison: ", accuracy_score(y_valid,pred))
        
